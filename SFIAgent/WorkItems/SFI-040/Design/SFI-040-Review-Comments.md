# SFI-040 Review Comments (QA)

## Design Critique
- Scope is clear and minimal: UI-only change in table rendering.
- Sequencing is feasible: column declaration updates, then row tuple updates, then tests.
- Risk surface is low and localized to `app.py` table branches.

## Risks / Edge Cases
1. Inconsistent ratio formatting across service/program/action/grouped branches.
2. Incorrect tuple ordering causing values to land under wrong headings after reorder.
3. Division by zero behavior missing in one branch.

## QA Recommendations
- Use one helper for `Score/Min` formatting reused in every insert path.
- Add tests that assert both column order and values by index.
- Explicitly test zero-cost rendering as `∞`.

## Capability Check
- Ran capability impact for changed paths; no mapped capabilities were reported by registry.
- Recommendation: proceed, but keep tests as regression protection for UI contract.

## QA Verdict
- Approved for implementation with test-first approach.

## Architect Notes

- Architectural alignment: Change is confined to presentation layer (`sfi_reporter.app`) and does not alter service/data boundaries.
- Contract compatibility: Existing `service_stats`, `program_stats`, and `kpi_stats` dictionaries already provide `score` and `cost`; no contract expansion required.
- Failure handling: Division-by-zero branch is explicitly defined (`∞`), avoiding runtime errors.
- Security/privacy: No new data paths, no added telemetry, and no expanded data exposure.
- Rollback safety: Single-file UI revert (`app.py`) with no schema/data migrations.
- Default behavior callout: ratio formatting should be explicitly fixed precision for non-zero values to avoid inconsistent string conversion defaults.

Architect decision: Approved, no new user story required.
