#!/usr/bin/env python3
"""Load customer (AR) opening balances into Business Central through the standard journals API.

Sub-commands (all dry-run unless `load --execute --confirm <ENV>`):

  normalize <xlsx> --out <csv>      Turn the "Dynamics Opening Balance" workbook into a flat CSV.
  plan <csv> [--posting-date D]     Validate the CSV and write the journal-line plan to runs/.
  probe <csv> --batch OB-AR         Check BC: customers exist/unblocked, batch exists, nothing posted yet.
  load <csv> --batch OB-AR --posting-date D [--execute --confirm QA-AGI]
                                    Create lines in chunks and post each chunk. Idempotent: lines whose
                                    Document No. already appears in G/L entries are skipped.

Environment (same keys as the logistics backend / .env.qa):
  AzureAd__TenantId AzureAd__ClientId AzureAd__ClientSecret [AzureAd__Instance]
  Bc__TenantId Bc__Environment Bc__CompanyId [Bc__BaseUrl]

Design notes (see reports/BC opening balance posting plan.md):
  * Standard `journalLines` accepts accountType=Customer + accountNumber but forces Document Type blank
    and offers no Due Date / Currency; good enough for one net balance per customer.
  * Document No. = OB-AR-<customer number suffix> is the idempotency key. The journal batch must have
    NO "No. Series" and NO "Posting No. Series", otherwise codeunit 13 overwrites the document number.
  * "Post with Job Queue" must be OFF on General Ledger Setup, otherwise the post action returns 204
    without posting.
  * Balancing comes from the batch's Bal. Account (OB-CLEARING); no per-line balancing account.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

ACCOUNT_RE = re.compile(r"^AIL-D-(\d+)$")
DOC_PREFIX = "OB-AR-"
DESC_MAX = 100
DOC_MAX = 20


# ----------------------------------------------------------------------------- data model
@dataclass
class Balance:
    row: int
    account_no: str
    mid: str
    description: str
    debit: float
    credit: float

    @property
    def net(self) -> float:
        return round(self.debit - self.credit, 2)


@dataclass
class Line:
    account_no: str
    amount: float
    document_no: str
    external_document_no: str
    description: str
    source_row: int

    def payload(self, posting_date: str) -> dict:
        return {
            "accountType": "Customer",
            "accountNumber": self.account_no,
            "postingDate": posting_date,
            "documentNumber": self.document_no,
            "externalDocumentNumber": self.external_document_no,
            "amount": self.amount,
            "description": self.description,
        }


# ----------------------------------------------------------------------------- normalize
def normalize(xlsx: Path, out: Path) -> None:
    import openpyxl  # only needed for this sub-command

    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    idx = {name: i for i, name in enumerate(header) if name}
    need = ["Account No.", "MID", "Description", "Debit Amount", "Credit Amount"]
    missing = [c for c in need if c not in idx]
    if missing:
        sys.exit(f"workbook is missing columns: {missing}")

    def num(v) -> float:
        if v in (None, ""):
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        sys.exit(f"non-numeric amount {v!r}")

    def mid(v) -> str:
        if v in (None, ""):
            return ""
        s = str(v).strip()
        return s[:-2] if s.endswith(".0") else s

    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["row", "account_no", "mid", "description", "debit", "credit", "net"])
        for r_no, r in enumerate(rows, start=2):
            if not any(c is not None for c in r):
                continue
            acc = str(r[idx["Account No."]] or "").strip()
            d, c = num(r[idx["Debit Amount"]]), num(r[idx["Credit Amount"]])
            w.writerow([r_no, acc, mid(r[idx["MID"]]), str(r[idx["Description"]] or "").strip(), d, c, round(d - c, 2)])
            n += 1
    print(f"normalized {n} rows -> {out}")


def read_csv(path: Path) -> list[Balance]:
    with path.open(newline="") as f:
        return [
            Balance(int(r["row"]), r["account_no"].strip(), r["mid"].strip(), r["description"].strip(),
                    float(r["debit"] or 0), float(r["credit"] or 0))
            for r in csv.DictReader(f)
        ]


# ----------------------------------------------------------------------------- validate + plan
def validate(balances: list[Balance], dedupe_identical: bool) -> tuple[list[Line], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    by_acc: dict[str, list[Balance]] = {}
    for b in balances:
        by_acc.setdefault(b.account_no, []).append(b)

    lines: list[Line] = []
    for acc, items in by_acc.items():
        m = ACCOUNT_RE.match(acc)
        if not m:
            errors.append(f"row {items[0].row}: account {acc!r} does not match AIL-D-<n>")
            continue
        nonzero = [b for b in items if b.net != 0]
        if not nonzero:
            continue  # zero balance: nothing to post
        if len(nonzero) > 1:
            amounts = {b.net for b in nonzero}
            if dedupe_identical and len(amounts) == 1:
                warnings.append(f"{acc}: {len(nonzero)} identical rows ({nonzero[0].net}) merged into one (rows {[b.row for b in nonzero]})")
                nonzero = nonzero[:1]
            else:
                errors.append(f"{acc}: {len(nonzero)} rows with amounts {sorted(amounts)} (rows {[b.row for b in nonzero]}); resolve in the source file")
                continue
        b = nonzero[0]
        if not b.mid:
            warnings.append(f"{acc} (row {b.row}): no MID; externalDocumentNumber left blank")
        if not b.description:
            warnings.append(f"{acc} (row {b.row}): empty description")
        doc = f"{DOC_PREFIX}{m.group(1)}"
        if len(doc) > DOC_MAX:
            errors.append(f"{acc}: document number {doc} longer than {DOC_MAX}")
        lines.append(Line(acc, b.net, doc, b.mid[:35], b.description[:DESC_MAX], b.row))

    mids: dict[str, list[str]] = {}
    for b in balances:
        if b.mid:
            mids.setdefault(b.mid, []).append(b.account_no)
    for mid_, accs in mids.items():
        if len(set(accs)) > 1:
            warnings.append(f"MID {mid_} appears on several customers {sorted(set(accs))}")
    return lines, errors, warnings


def summarize(lines: list[Line]) -> dict:
    deb = [l for l in lines if l.amount > 0]
    cre = [l for l in lines if l.amount < 0]
    return {
        "lines": len(lines),
        "debit_lines": len(deb), "debit_total": round(sum(l.amount for l in deb), 2),
        "credit_lines": len(cre), "credit_total": round(sum(l.amount for l in cre), 2),
        "net_total": round(sum(l.amount for l in lines), 2),
    }


def run_dir() -> Path:
    d = Path("runs") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d.mkdir(parents=True, exist_ok=True)
    return d


def cmd_plan(args) -> list[Line]:
    balances = read_csv(Path(args.csv))
    lines, errors, warnings = validate(balances, args.dedupe_identical)
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    s = summarize(lines)
    print(json.dumps(s, indent=2))
    d = run_dir()
    with (d / "plan.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["account_no", "amount", "document_no", "external_document_no", "description", "source_row"])
        for l in lines:
            w.writerow([l.account_no, l.amount, l.document_no, l.external_document_no, l.description, l.source_row])
    (d / "plan.json").write_text(json.dumps({"posting_date": args.posting_date, "summary": s,
                                              "errors": errors, "warnings": warnings,
                                              "lines": [asdict(l) for l in lines]}, indent=2))
    print(f"plan written to {d}/ ({len(errors)} error(s), {len(warnings)} warning(s))")
    if errors:
        sys.exit(2)
    return lines


# ----------------------------------------------------------------------------- BC client
class Bc:
    def __init__(self) -> None:
        env = os.environ
        missing = [k for k in ("AzureAd__TenantId", "AzureAd__ClientId", "AzureAd__ClientSecret",
                               "Bc__TenantId", "Bc__Environment", "Bc__CompanyId") if not env.get(k)]
        if missing:
            sys.exit(f"missing environment variables: {missing}")
        self.instance = env.get("AzureAd__Instance", "https://login.microsoftonline.com/").rstrip("/")
        self.base = env.get("Bc__BaseUrl", "https://api.businesscentral.dynamics.com").rstrip("/")
        self.scope = env.get("Bc__Scope", "https://api.businesscentral.dynamics.com/.default")
        self.env = env["Bc__Environment"]
        self.company = env["Bc__CompanyId"]
        self.std = f"{self.base}/v2.0/{env['Bc__TenantId']}/{self.env}/api/v2.0/companies({self.company})"
        self._token: str | None = None
        self._token_exp = 0.0
        self.log: list[dict] = []

    def token(self) -> str:
        if self._token and time.time() < self._token_exp - 60:
            return self._token
        data = urllib.parse.urlencode({
            "client_id": os.environ["AzureAd__ClientId"],
            "client_secret": os.environ["AzureAd__ClientSecret"],
            "scope": self.scope, "grant_type": "client_credentials"}).encode()
        req = urllib.request.Request(f"{self.instance}/{os.environ['AzureAd__TenantId']}/oauth2/v2.0/token", data=data)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = json.load(r)
        except urllib.error.HTTPError as e:
            sys.exit(f"token request failed: {e.code} {e.read()[:300].decode(errors='replace')}")
        except urllib.error.URLError as e:
            sys.exit(f"network error reaching {self.instance}: {e.reason}")
        self._token = body["access_token"]
        self._token_exp = time.time() + int(body.get("expires_in", 3599))
        return self._token

    def call(self, method: str, url: str, body: dict | None = None, headers: dict | None = None):
        h = {"Authorization": f"Bearer {self.token()}", "Accept": "application/json", "Accept-Language": "en-US"}
        if body is not None:
            h["Content-Type"] = "application/json"
        h.update(headers or {})
        req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                     method=method, headers=h)
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
                status = r.status
        except urllib.error.HTTPError as e:
            raw = e.read()
            status = e.code
        except urllib.error.URLError as e:
            sys.exit(f"network error calling {urllib.parse.urlsplit(url).netloc}: {e.reason} "
                     "(is api.businesscentral.dynamics.com reachable from this machine?)")
        self.log.append({"t": datetime.now(timezone.utc).isoformat(), "method": method, "url": url,
                         "status": status, "ms": int((time.time() - t0) * 1000)})
        if status >= 400:
            raise RuntimeError(f"{method} {url} -> {status}: {raw[:800].decode(errors='replace')}")
        return json.loads(raw) if raw else None

    def get_all(self, url: str) -> list[dict]:
        out: list[dict] = []
        while url:
            page = self.call("GET", url)
            out.extend(page.get("value", []))
            url = page.get("@odata.nextLink")
        return out


def probe(bc: Bc, lines: list[Line], batch_code: str) -> dict:
    print(f"probing {bc.env} company {bc.company} ...")
    customers = bc.get_all(f"{bc.std}/customers?$select=id,number,displayName,blocked,currencyCode&$top=5000")
    by_no = {c["number"]: c for c in customers}
    print(f"  customers in BC: {len(customers)}")
    problems: list[str] = []
    for l in lines:
        c = by_no.get(l.account_no)
        if not c:
            problems.append(f"{l.account_no}: not found in BC")
        elif c.get("blocked") not in (None, "", "_x0020_", " "):
            problems.append(f"{l.account_no}: blocked={c['blocked']!r}")
        elif c.get("currencyCode"):
            problems.append(f"{l.account_no}: customer currency {c['currencyCode']} (sheet has LCY only)")
    journals = bc.get_all(f"{bc.std}/journals?$filter=code eq '{batch_code}'")
    if not journals:
        problems.append(f"journal batch {batch_code} not found (create it on the GENERAL template with Bal. Account = OB-CLEARING, no No. Series)")
        journal = None
    else:
        journal = journals[0]
        if not journal.get("balancingAccountId") or journal["balancingAccountId"] == "00000000-0000-0000-0000-000000000000":
            problems.append(f"journal batch {batch_code} has no balancing account")
        leftover = bc.get_all(f"{bc.std}/journals({journal['id']})/journalLines?$select=id,documentNumber&$top=5000")
        if leftover:
            problems.append(f"journal batch {batch_code} still holds {len(leftover)} unposted line(s)")
    posted = bc.get_all(f"{bc.std}/generalLedgerEntries?$filter=startswith(documentNumber,'{DOC_PREFIX}')&$select=documentNumber,postingDate&$top=20000")
    posted_docs = {e["documentNumber"] for e in posted}
    already = [l.document_no for l in lines if l.document_no in posted_docs]
    print(f"  already posted document numbers with prefix {DOC_PREFIX}: {len(posted_docs)} (of which {len(already)} in this plan)")
    for p in problems:
        print("PROBE", p)
    return {"journal": journal, "problems": problems, "already_posted": already}


def cmd_probe(args) -> None:
    lines = cmd_plan(args)
    bc = Bc()
    res = probe(bc, lines, args.batch)
    if res["problems"]:
        sys.exit(3)
    print("probe OK")


def cmd_load(args) -> None:
    if not args.posting_date:
        sys.exit("--posting-date is required for load")
    lines = cmd_plan(args)
    bc = Bc()
    res = probe(bc, lines, args.batch)
    if res["problems"]:
        sys.exit("refusing to load: probe reported problems")
    todo = [l for l in lines if l.document_no not in set(res["already_posted"])]
    print(f"{len(todo)} line(s) to post, {len(lines) - len(todo)} already posted (skipped)")
    if not (args.execute and args.confirm == bc.env):
        print(f"DRY RUN. Re-run with --execute --confirm {bc.env} to post into {bc.env}.")
        return
    journal_id = res["journal"]["id"]
    d = run_dir()
    ledger = (d / "ledger.jsonl").open("a")
    chunks = [todo[i:i + args.chunk] for i in range(0, len(todo), args.chunk)]
    for n, chunk in enumerate(chunks, start=1):
        print(f"chunk {n}/{len(chunks)}: inserting {len(chunk)} line(s)")
        for l in chunk:
            bc.call("POST", f"{bc.std}/journals({journal_id})/journalLines", l.payload(args.posting_date))
            ledger.write(json.dumps({"event": "inserted", "chunk": n, **asdict(l)}) + "\n")
        print(f"chunk {n}: posting")
        bc.call("POST", f"{bc.std}/journals({journal_id})/Microsoft.NAV.post")
        ledger.write(json.dumps({"event": "posted", "chunk": n, "lines": len(chunk)}) + "\n")
        ledger.flush()
        # verify: every document number of the chunk must now be in G/L entries
        docs = {l.document_no for l in chunk}
        entries = bc.get_all(f"{bc.std}/generalLedgerEntries?$filter=startswith(documentNumber,'{DOC_PREFIX}') and postingDate eq {args.posting_date}&$select=documentNumber&$top=20000")
        seen = {e["documentNumber"] for e in entries}
        missing = sorted(docs - seen)
        if missing:
            ledger.write(json.dumps({"event": "verify_failed", "chunk": n, "missing": missing}) + "\n")
            (d / "http.json").write_text(json.dumps(bc.log, indent=2))
            sys.exit(f"chunk {n}: {len(missing)} document(s) not found in G/L entries after post (is 'Post with Job Queue' on?): {missing[:5]}")
        print(f"chunk {n}: verified {len(docs)} document(s) in G/L entries")
    (d / "http.json").write_text(json.dumps(bc.log, indent=2))
    print(f"done. run artifacts in {d}/")


# ----------------------------------------------------------------------------- cli
def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("normalize"); n.add_argument("xlsx"); n.add_argument("--out", required=True)

    def common(sp):
        sp.add_argument("csv")
        sp.add_argument("--posting-date", help="yyyy-mm-dd cutover date")
        sp.add_argument("--dedupe-identical", action="store_true",
                        help="merge rows that repeat the same customer with the identical amount")

    pl = sub.add_parser("plan"); common(pl)
    pr = sub.add_parser("probe"); common(pr); pr.add_argument("--batch", default="OB-AR")
    ld = sub.add_parser("load"); common(ld); ld.add_argument("--batch", default="OB-AR")
    ld.add_argument("--chunk", type=int, default=200)
    ld.add_argument("--execute", action="store_true")
    ld.add_argument("--confirm", help="environment name typed back, e.g. QA-AGI")

    a = p.parse_args()
    if a.cmd == "normalize":
        normalize(Path(a.xlsx), Path(a.out))
    elif a.cmd == "plan":
        cmd_plan(a)
    elif a.cmd == "probe":
        cmd_probe(a)
    elif a.cmd == "load":
        cmd_load(a)


if __name__ == "__main__":
    main()
