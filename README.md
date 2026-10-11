# business_central — Business Central scripts (Anwar Group / AGI)

Scripts, research and plans for working with the Microsoft Dynamics 365 Business Central
Online tenant that the [logistics-distribution](https://github.com/Asim971/logistics-distribution)
platform integrates with. First workstream: **posting opening balances** (G/L, customers,
vendors, bank, inventory) into the `QA-AGI` environment and later production.

| Path | Purpose |
|---|---|
| `reports/BC opening balance posting plan.md` | Research report + recommended approach, phased implementation plan and decision log |
| `research_notes/BC opening balance posting plan/` | Source notes behind the report (logistics repo analysis, BC methodology, BC APIs, AL references, cutover controls) |
| `scripts/bc-smoke.sh` | Read-only S2S smoke test: Entra token → `companies` → AL extension `pings` |
| `scripts/set-github-secrets.sh` | Loads an env file into GitHub Actions secrets (repo or environment scoped) |
| `.github/workflows/bc-smoke.yml` | Manual workflow that runs the smoke test with the `qa` environment secrets |
| `.env.example` | Configuration keys (no secret values) shared with the logistics backend |

## Architecture rule (inherited from logistics-distribution ADR-0001)

BC owns commercial, inventory and financial truth. The only writer to BC is a backend
authenticated with a service-to-service (S2S) Entra app registration. Scripts in this repo
must follow the same pattern: client-credentials token for scope
`https://api.businesscentral.dynamics.com/.default`, URL base
`https://api.businesscentral.dynamics.com/v2.0/{tenantId}/{environment}/api/...`,
per-call `companies({companyId})` routing, idempotent writes keyed by a deterministic
Document No. / External Document No., and no SUPER permission for the integration identity.

## Configuration and secrets

Key names use the ASP.NET Core `Section__Key` convention so one set of values serves the
logistics backend (Railway), GitHub Actions and local runs. Copy `.env.example` to `.env.qa`
and fill in values. `.env.qa` and every `.env.*` file except `.env.example` are gitignored —
**never commit real values**.

Store the values as GitHub Actions **environment secrets** (environment `qa`):

```bash
gh auth login                                   # account with admin on Asim971/business_central
DRY_RUN=1 scripts/set-github-secrets.sh .env.qa --env qa   # shows key names only
scripts/set-github-secrets.sh .env.qa --env qa             # creates env "qa" if needed, sets 20 secrets
```

Then run the `bc-smoke` workflow from the Actions tab to prove the connection.

Locally (the Railway `${{Postgres.*}}` connection string is not valid bash; export only what
the script needs or comment that line out):

```bash
set -a; source .env.qa; set +a
scripts/bc-smoke.sh
```

## Status

- [x] Research and plan (see report)
- [x] Secrets handling and smoke test scaffolding
- [ ] Phase 1: opening-balance CSV templates + validator
- [ ] Phase 2: AL API page over Gen. Journal Line (`anwarGroup/logistics`, ids 70100-70199)
- [ ] Phase 3: loader with idempotency ledger, dry run, reconciliation reports
