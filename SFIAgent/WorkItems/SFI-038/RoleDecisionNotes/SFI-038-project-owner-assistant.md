# SFI-038 — Project Owner Assistant Decision Notes

## Decisions
- **Single story**: The request is one vertical slice — add a computed column to existing tables from a static CSV. No decomposition needed.
- **Score formula**: `KPIScore × count` per KPI row. Services and programs aggregate the sum.
- **Lookup key**: Match by KPI name string (CSV `KPI` column → `kpi_stats[id]['name']`). The CSV also has `KPIID` (GUID) which can be used as a secondary key.
- **Default score**: KPIs not in the CSV get score 0, so the column won't break for new/unknown KPIs.

## Assumptions (explicit)
- kpi.csv is bundled in the package directory, not user-configurable.
- The `KPI` name strings in the CSV match the `KpiName` from the S360 API exactly (already confirmed by user's example: "[SFI-AR1.2.7] Vulnerability Management" appears in both).
- Interface type: existing Tkinter GUI (established context).
- Target platform: Windows (established context).
- Data persistence: CSV file on disk, loaded in-memory (no DB).
