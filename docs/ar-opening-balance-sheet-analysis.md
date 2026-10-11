# AR opening balance sheet — analysis (2026-10-11)

Source: Google Drive file **Dynamics Opening Balance (1).xlsx** (owner bushra.tabassum@anwargroup.com,
modified 2026-10-07, file id `1Yvov7Mps-r0j_B5y5gKFGkVbE5ej7Znf`). One sheet, `Sheet1`.
The extract itself is not stored in this repository (customer balances); point the loader at a
local copy.

## What the sheet is

An **Edit-in-Excel style export of the Gen. Journal Line table (81)**: 242 columns, every BC field
name present. Only five columns carry data:

| Column | Populated rows | Content |
|---|---|---|
| Account No. | 861 / 861 | Customer codes `AIL-D-44` … `AIL-D-20846`, all matching `AIL-D-<n>` |
| MID | 850 / 861 | Numeric legacy id (19 stored as floats, 831 as text) |
| Description | 861 / 861 | Customer name |
| Debit Amount | 298 | Customer owes AGI (receivable) |
| Credit Amount | 471 | AGI owes customer (advance / overpayment) |

Everything that BC needs to post is **blank**: Journal Template/Batch, Line No., Account Type,
Posting Date, Document Type, Document No., Bal. Account Type/No., Currency, Due Date, Document Date,
posting groups, dimensions. The sheet is a balance list, not a postable journal.

## Totals

| Measure | Value (BDT, assumed LCY) |
|---|---|
| Total debit (receivable) | 478,124,724.73 across 298 customers |
| Total credit (customer advances) | 423,639,456.92 across 471 customers |
| Net receivable | 54,485,267.81 |
| Rows with zero balance | 92 (nothing to post) |
| Rows with both debit and credit | 0 |
| Negative or non-numeric amounts | 0 |
| Amounts with more than 2 decimals | 0 |
| Median non-zero balance | 24,495.00 |
| Customers with balance of 10,000,000 or more (absolute) | 21 (net 31,307,881.70) |

The split (more credit rows than debit rows) is unusual for a receivables ledger and must be
confirmed with Finance: either many dealers prepay (advance deposits), or the sign convention of the
extract is inverted. Posting with the wrong sign is the single largest risk in this file.

## Data-quality findings (must be resolved before posting)

1. **Duplicate customer rows (3 codes).** BC will accept two lines for one customer, so these would
   double-post:
   - `AIL-D-50` — rows 142 and 178, identical debit 737,915.00, same MID 20057. Almost certainly a duplicate; keep one.
   - `AIL-D-1838` — rows 75 and 371 (name differs by a "-Pabna" suffix), identical credit 3,556,250.00, same MID 149692. Likely a duplicate; confirm.
   - `AIL-D-3438` — rows 176 and 177, both zero, no MID. Harmless; drop.
2. **Same MID on different customer codes (3 cases):** MID 23467 (`AIL-D-8492` / `AIL-D-8427`, 1,100 each),
   MID 17792 (`AIL-D-1730` / `AIL-D-12466`, both zero), MID 19985 (`AIL-D-8435` / `AIL-D-1862`, −541,190 each).
   Decide which BC customer is the live one; the second code may be a legacy duplicate master record.
3. **Missing MID (11 rows):** rows 176, 177, 262, 326, 342, 357, 366, 375, 645, 647, 862. Not blocking
   (MID is only used as External Document No. for traceability) but Finance should fill them.
4. **Test data:** row 375 `AIL-D-12506` has a keyboard-mash name, zero balance, no MID. Drop and check
   the customer card in BC.
5. **No currency or FX information.** All amounts are assumed LCY (BDT). Any foreign-currency
   customers (the largest debit balances are foreign contractors) must be posted in document
   currency with the historical rate, which this sheet cannot express.
6. **No aging detail.** One balance per customer means Aged Accounts Receivable will show every
   balance as one open item dated at the posting date. If Finance needs aging, the extract must be
   re-cut per open invoice (document no., document date, due date); see the report, Phase 3 CSV
   templates.

## How it maps to the posting plan

Per `reports/BC opening balance posting plan.md` section 4.9, customer open items are posted through
a General Journal with Account Type = Customer, one line per open item, balanced to the
`OB-CLEARING` G/L account, posting date = cutover date, VAT posting groups blank.

With the data as supplied (one net balance per customer, no document dates) the **standard
`journals`/`journalLines` API is sufficient** for a first QA-AGI load: it accepts Account Type
Customer and `accountNumber`, posts with Document Type blank and Due Date = Posting Date. The
custom AL page from Phase 1 only becomes necessary when aging detail or FX is added.

Derived journal line per customer (zero rows skipped, duplicates resolved first):

| Field | Value |
|---|---|
| accountType | `Customer` |
| accountNumber | `AIL-D-<n>` |
| amount | debit − credit (positive = receivable, negative = advance) |
| documentNumber | `OB-AR-<n>` (idempotency key; batch No. Series and Posting No. Series must be blank) |
| externalDocumentNumber | MID |
| description | customer name, truncated to 100 chars |
| postingDate | cutover date (Finance to confirm) |
| balancing | batch `OB-AR` with `balancingAccountId` = OB-CLEARING G/L account |

Dry-run result on the file as supplied (`plan --dedupe-identical`, merging the two identical
duplicate rows): **767 lines**, 297 debit lines totalling 477,386,809.73, 470 credit lines totalling
−420,083,206.92, **net 57,303,602.81**. The strict plan (no dedupe) stops with two errors until the
duplicates are fixed in the source.

After posting, the clearing account carries the negative of that net until the G/L trial balance
(with the AR control account excluded) is loaded against it; the invariant "OB-CLEARING = 0.00"
closes the cutover.

## Loader

`scripts/post_opening_ar.py` turns the normalized CSV into journal lines and, only with
`--execute --confirm QA-AGI`, creates and posts them. The default is a dry run that validates the
file, resolves every customer against BC, and writes the plan to `runs/`.

```bash
# 1. normalize the workbook (writes <out>.csv with row, account_no, mid, description, debit, credit, net)
python3 scripts/post_opening_ar.py normalize "/path/to/Dynamics Opening Balance (1).xlsx" --out /path/to/ar.csv

# 2. validate + plan (no BC call)
python3 scripts/post_opening_ar.py plan /path/to/ar.csv --posting-date 2026-06-30

# 3. probe BC: every customer exists, batch OB-AR exists, nothing already posted (needs .env.qa)
set -a; source .env.qa; set +a
python3 scripts/post_opening_ar.py probe /path/to/ar.csv --batch OB-AR

# 4. load (creates lines in chunks and posts each chunk; refuses on any validation error)
python3 scripts/post_opening_ar.py load /path/to/ar.csv --batch OB-AR --posting-date 2026-06-30 --execute --confirm QA-AGI
```
