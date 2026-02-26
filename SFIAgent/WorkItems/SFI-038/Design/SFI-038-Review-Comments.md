# SFI-038 — Review Comments

## Design Review
- **Clarity**: Good. Score = KPIScore × count is unambiguous.
- **Feasibility**: Straightforward — follows existing column-addition pattern.
- **Edge cases identified**:
  1. KPI name in CSV doesn't match API name (e.g., extra whitespace, quote differences) — need normalization.
  2. CSV file missing at runtime → should not crash, fallback to empty lookup.
  3. `KPIScore` column has value 0 for some KPIs — those should still display 0, not be hidden.
  4. Manager tree view aggregates by owner groups — score must roll up correctly.

## Recommendations
- Use both `KPI` name and `KPIID` as lookup keys for resilience.
- Strip/normalize KPI names when building the lookup (handle quoted CSV entries).

## Architect Notes
- **Contract**: `load_kpi_scores(path?) -> dict[str, int]` — keyed by KPI name, value is integer score. Second return or attribute for KPIID lookup.
- **File location**: Use `pathlib.Path(__file__).parent / "kpi.csv"` for reliable package-relative path.
- **Encoding**: Explicit `encoding="utf-8-sig"` to handle BOM if present.
- **Error boundary**: CSV load failure returns empty dict; no crash propagation.
- **No new dependencies**: stdlib `csv` only.
- **Score field**: Add `'score': 0` to existing stat dict initializers in services.py alongside count/sla/cost.
- **Architectural alignment**: Follows existing pattern of enriching stat dicts in `do_refresh` then reading them in `_update_tables`.
