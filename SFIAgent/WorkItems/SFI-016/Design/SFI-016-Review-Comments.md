# SFI-016 — Review Comments

## Design Review Summary
**Verdict**: Approved with minor observations.

## Clarity & Completeness
- ✅ Design doc clearly separates the four components (singleton, tracking, UI, tests).
- ✅ Return type change is well-documented with exact dict shape.
- ✅ Alternatives table is thorough.

## Feasibility & Sequencing
- ✅ All four components are interdependent — shipping together is correct.
- ✅ Implementation is already done — this review is retrospective.

## Risk Coverage
- ✅ Stale credentials mitigated by Azure SDK internal refresh.
- ✅ Thread safety handled by existing `status_lock`.
- ⚠️ **Observation**: If the singleton `S360Client` enters a bad state (e.g., underlying HTTP session corrupted), there's no way to force a new instance without restarting the app. **Recommendation**: Consider a future work item for a "Reset Connection" option. Not blocking for SFI-016.

## Edge Cases Identified
1. **All KPIs fail**: Retry button should appear; rows list is empty but UI should still display the warning.
2. **Retry succeeds for some, fails for others**: Button should remain with updated failure list.
3. **User clicks retry while retry is already in progress**: Button should be disabled during retry.
4. **Zero KPIs in action items summary**: `get_detailed_action_items` should return `([], [])` — no crash.

## Naming Review
- ✅ `_client_instance` — clear singleton naming convention.
- ✅ `failed_kpis` — descriptive, matches the domain.
- ✅ `_on_retry_failed` / `_on_retry_complete` — consistent with existing `_on_refresh_complete` pattern.

## Folder Structure
- ✅ No new files in `src/` — changes are contained to existing modules.
- ✅ Test files updated in-place — no structural changes.

---

## Architect Notes

### Bugs Found During Review
1. **`failed_kpis` never initialized** — The variable was referenced in `fetch_kpi_grid()` (inner function) and in the return statements, but never declared as a local list in `get_detailed_action_items()`. This would cause a `NameError` at runtime when any KPI fails. **Fixed**: Added `failed_kpis: list[dict] = []` initialization.
2. **Early return type mismatch** — `return []` on empty input should be `return [], []` to match the `tuple[list[dict], list[dict]]` return type. **Fixed**.
3. **Stale docstring** — Return type annotation said `-> list[dict]` and docstring said "List of detailed action item rows". Updated to `-> tuple[list[dict], list[dict]]` with corrected docstring.

### Architectural Assessment
- ✅ **Singleton pattern**: Appropriate for desktop app. GIL protects the `_client_instance is None` check — no threading race.
- ✅ **Data contract**: `(rows, failed_kpis)` tuple is a clean contract. The failed_kpis dict shape `{kpi_id, kpi_name, error}` provides sufficient info for UI display and retry.
- ✅ **Thread safety**: `failed_kpis` list mutations happen under `status_lock` — correct.
- ✅ **Failure isolation**: Individual KPI failures don't abort the entire fetch. Each worker catches its own exceptions.
- ✅ **No new dependencies**: Uses only stdlib `threading.Lock` and existing `ThreadPoolExecutor`.
- ⚠️ **Coupling note**: `_on_retry_failed` in `tk_app.py` directly calls `get_detailed_action_items` — this is acceptable coupling for a desktop app but would be a concern in a larger architecture.
