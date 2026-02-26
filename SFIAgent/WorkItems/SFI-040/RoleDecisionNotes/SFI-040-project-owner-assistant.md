# SFI-040 Project Owner Assistant Decision Notes

## Scope Decision
- Kept scope to one user-observable outcome: improve table readability and efficiency comparison by reordering columns and adding `Score/Min`.
- Avoided decomposition because all requested changes form a single vertical UI slice in one table view.

## Confirmed Inputs from User Request
- Interface type: Desktop GUI (Tkinter) in `SFIReporter`.
- Target platform: Windows environment, while preserving existing cross-platform Python style.
- Data persistence: Unchanged; reuse existing cache/data pipeline.
- Scope expectation: Minimal and testable; no unrelated changes.

## Assumptions (explicit)
- `Score/Min` uses row-level displayed `Score` and `Cost` values.
- `Cost == 0` displays `∞` in the new column.
- No additional settings/feature flags are required for rollout.

## Acceptance Criteria Rationale
- Criteria are limited to five testable checks covering:
  1) Column order,
  2) New column visibility,
  3) Formula behavior for non-zero cost,
  4) Infinity behavior for zero cost,
  5) No persistence/data-pipeline changes.

## Risks / Dependencies
- Low risk: UI table configuration and value formatting only.
- Dependency: Existing Score and Cost values must already be available in the current data model feeding the table.
