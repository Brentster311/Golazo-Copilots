# SFI-038 — Architect Decision Notes

## Decisions
- Single new module `kpi_lookup.py` with `load_kpi_scores()` function.
- Dual-key lookup: by KPI name (primary) and KPIID (fallback).
- Score field added to `kpi_stats`, `service_stats`, and `program_stats` dicts — same pattern as existing count/sla/cost/invalid_eta.
- `pathlib.Path(__file__).parent / "kpi.csv"` for reliable path resolution.
- `encoding="utf-8-sig"` to handle potential BOM.
- No architectural concerns — this is a pure data-enrichment addition.
