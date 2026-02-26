**Status**: IMPLEMENTED

**User Story**
- Title: Reorder Score and Cost columns and add Score/Min ratio in SFIReporter grid
- As a: SFIReporter analyst using the desktop UI
- I want: the `Score` column displayed before `Cost`, plus a new `Score/Min` column that shows Score divided by Cost
- So that: I can compare impact efficiency directly in the table without manual calculation
- Out of scope:
  - Changes to data retrieval, caching, or persistence pipeline
  - Changes to filtering, sorting behavior beyond adding/reordering columns
  - Changes to non-SFIReporter applications or unrelated UI panels
- Assumptions:
  - **Assumption (explicit):** `Score/Min` is computed from the same displayed Score and Cost values for each row at render time.
  - **Assumption (explicit):** Division by zero is represented as `∞` exactly, not a numeric sentinel.
  - **Assumption (explicit):** Existing cross-platform Python/Tkinter patterns remain unchanged while validated on Windows.
- Acceptance Criteria (bulleted, testable):
  - In the SFIReporter table view, `Score` appears immediately before `Cost` in the visible column order.
  - A new column labeled `Score/Min` is present and populated for each displayed row.
  - For rows where `Cost > 0`, `Score/Min` equals `Score / Cost` using the row’s current values.
  - For rows where `Cost == 0`, `Score/Min` displays `∞`.
  - Existing cache/data pipeline behavior is unchanged (no new persistence path, schema, or data source required).
- Non-functional requirements:
  - Keep implementation minimal and localized to SFIReporter UI/table rendering logic.
  - Preserve existing application performance characteristics for table rendering.
  - Maintain current cross-platform Python code style and compatibility.
- Telemetry / metrics expected:
  - No new telemetry required for this UI-only column enhancement.
  - Existing diagnostic/logging behavior remains unchanged.
- Rollout / rollback notes:
  - Rollout via normal SFIReporter release process.
  - Rollback by reverting table column order and removing `Score/Min` presentation logic.

## Closure

- Summary of what was delivered:
  - Reordered table columns so `Score` appears before `Cost` in Services, Program Summary, and Action Items.
  - Added `Score/Min` column in all three tables.
  - Added ratio formatting logic with explicit `∞` rendering for zero-cost rows.
  - Added and passed targeted tests validating column order and ratio behavior.
- Acceptance criteria status:
  - `Score` before `Cost` in visible column order: **PASS**
  - `Score/Min` column exists and is populated: **PASS**
  - `Score/Min = Score / Cost` when `Cost > 0`: **PASS**
  - `Score/Min = ∞` when `Cost == 0`: **PASS**
  - No cache/data pipeline changes: **PASS**
- Future work items:
  - Improve capability registry mapping for UI table files so impact analysis includes this surface.
- Final status confirmation: **IMPLEMENTED**
