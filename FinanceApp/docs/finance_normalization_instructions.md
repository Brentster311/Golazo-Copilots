# Finance Normalization Instructions

## Decisions Locked On 2026-06-14
- Database target: SQLite.
- Work timing: Proceed immediately with available data.
- Categorization mode: Conservative.
- Amazon enrichment: Deferred until Amazon order export CSV is provided.

## Current Data Scope
- Included now:
  - Finances/FirstTech/ExportedTransactions.csv
  - Finances/fidelity/Credit Card - 1860_01-01-2026_06-11-2026.csv
  - PDF statements in Finances/chase
  - PDF statements in Finances/paypal
- Present but not ingested yet:
  - PDF statements in Finances/amazon

## Current Pipeline Entry Point
- Script: scripts/build_finance_sqlite.py
- Run command from repo root:

```powershell
python scripts/build_finance_sqlite.py
```

## Outputs Produced
- SQLite DB: analysis/finance.db
- Summary report: analysis/summary_report.md

## Current Source Coverage Snapshot
- Chase / Credit Card 6773: 2 transactions
- Fidelity / Credit Card 1860: 278 transactions
- FirstTech / Checking: 171 transactions
- PayPal / PayPal Account: 102 transactions

## Normalization Goals
- Convert source transactions into a single schema in SQLite.
- Preserve raw fields and source provenance.
- Add normalized merchant names and conservative normalized categories.
- Flag probable transfer/payment rows so spend analysis can exclude them.
- Detect repeated/recurring transaction candidates.

## PDF Parsing Notes
- Chase parser reads purchase rows that appear as mm/dd + merchant + amount lines in statement text.
- PayPal parser reads account activity blocks and captures transaction date, description, ID, Ref ID, and USD amount.
- PayPal rows labeled General Credit Card Deposit are flagged as Transfers to reduce spend inflation.

## Conservative Categorization Policy
- Use source/provider category only when clearly available.
- Use strict keyword-based mapping for high-confidence merchants.
- If uncertain, keep category as Unclassified/Uncategorized.
- Avoid aggressive inference until manual review or more data is provided.

## Amazon Plan (When Export Is Available)
- Add an amazon_orders table from Amazon order export CSV.
- Match card transactions containing Amazon descriptors to orders using:
  - amount equality or near-equality,
  - date window proximity,
  - optional text clues.
- Store match confidence and leave unmatched rows unresolved.

## Recommended Next Steps
- Provide Amazon order export CSV to enable Amazon transaction lookups.
- Optionally provide CSV exports for Chase/PayPal to avoid PDF parsing.
- Review Unclassified rows and add targeted merchant rules over time.
