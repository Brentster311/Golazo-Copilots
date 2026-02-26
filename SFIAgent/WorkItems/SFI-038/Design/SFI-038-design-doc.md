# SFI-038 Design Document — KPI Score Column

## Summary
Add a "Score" column to the Services, Program Summary, and Action Items tables. Score is computed as `KPIScore × count` per KPI using a bundled `kpi.csv` lookup table.

## Problem Statement
Users currently see raw item counts per KPI/service/program but have no visibility into the weighted security-debt impact. Users must mentally multiply KPI scores by counts to prioritize remediation.

## Business Case
- **Why now**: The kpi.csv file is already created and added to the project.
- **Impact**: Immediate visibility into security-debt priorities without external tools.
- **KPIs**: No new telemetry — the Score column is the deliverable itself.

## Stakeholders
- SFI Reporter end users (security engineers, managers)

## Functional Requirements
1. Load `kpi.csv` from the package directory at startup; build `{kpi_name: score}` lookup.
2. During `do_refresh`, compute per-KPI score = `KPIScore × count` and store in `kpi_stats`.
3. Aggregate per-service score = Σ(per-KPI scores for items in that service) into `service_stats`.
4. Aggregate per-program score = Σ(per-KPI scores for items in that program) into `program_stats`.
5. Add "Score" column to all three Treeview tables, formatted as comma-separated integers.

## Non-functional Requirements
- CSV load < 50ms
- No new pip dependencies (stdlib `csv` module)
- CSV is read-only at runtime

## Proposed Approach
1. New module `kpi_lookup.py` with `load_kpi_scores() -> dict[str, int]` that reads kpi.csv.
2. In `services.py:do_refresh()`, after building `kpi_stats`, enrich each entry with `score = kpi_score_lookup[name] * count`.
3. Aggregate scores into `service_stats` and `program_stats` the same way `count`/`sla`/`cost` are aggregated.
4. In `app.py`, add `"score"` column to each Treeview and include the value in every `insert()` call.

## Alternatives Considered
- **Hardcoded dict**: Rejected — CSV is easier to update without code changes.
- **API-based scores**: Out of scope — kpi.csv is the designated source.

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| KPI name mismatch between CSV and API | Fallback to score 0; log warning |
| CSV missing/corrupt | Graceful fallback: empty lookup, all scores 0 |

## Dependencies
- `kpi.csv` must be present in `sfi_reporter/` directory

## Rollback Plan
Revert the commit — the Score column is purely additive.

## Test Strategy
- Unit tests for CSV loading, score computation, aggregation, missing-KPI fallback
- Existing tests must continue passing
