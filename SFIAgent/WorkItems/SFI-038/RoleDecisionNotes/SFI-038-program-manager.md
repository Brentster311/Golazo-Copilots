# SFI-038 — Program Manager Decision Notes

## Decisions
- New module `kpi_lookup.py` rather than inlining CSV logic in services.py — keeps concerns separated.
- Lookup keyed by KPI name (string match) since that's what's displayed and available in both CSV and API data.
- Score aggregation follows the same pattern as existing `count`/`sla`/`cost` accumulation in `do_refresh`.
- Comma-formatted integers for display (e.g., "1,488" not "1488.00").
