# SFI-040 Design Doc

## Summary
Reorder existing table columns so `Score` appears before `Cost`, and add a derived `Score/Min` column in SFIReporter table views.

## Problem Statement
Users can see score and cost but cannot quickly evaluate impact efficiency without mentally computing a ratio. Current column order also places cost before score, which is less aligned with user preference.

## Business Case
- Improves decision speed for prioritization.
- Reduces manual calculations in operational triage.
- Low-risk UI-only enhancement with no API changes.

## Stakeholders
- SFIReporter end users (ICs and managers)
- Maintainers of `sfi_reporter.app`

## Functional Requirements
1. In Services, Program Summary, and Action Items tables, display `Score` before `Cost`.
2. Add a new column `Score/Min` after `Cost`.
3. For each row, compute `Score/Min = score / cost`.
4. If `cost == 0`, display `∞`.

## Non-Functional Requirements
- No changes to data fetching, cache schema, or persistence behavior.
- Preserve existing sorting defaults unless explicit behavior is needed for new column.
- Keep implementation localized to UI rendering logic in `app.py`.

## Proposed Approach (High Level)
1. Update table column declarations in `_build_ui` for `services_tree`, `program_tree`, and `action_tree`.
2. Add heading and width for `score_per_min` column.
3. Add a local helper formatter in `app.py` to render score-per-minute safely (`∞` for zero-cost, otherwise fixed precision).
4. Update each row insert tuple in `_update_tables` and related grouped-owner rendering to include reordered score/cost and new ratio.
5. Add/adjust tests to assert column order and ratio rendering behavior.

## Alternatives Considered
- Compute in data layer (`services.py`): rejected to avoid persistence/data-contract changes for a presentation-only value.
- Display ratio as integer-only: rejected due to loss of useful precision.

## Risks / Mitigations / Open Questions
- Risk: inconsistent formatting across table branches. Mitigation: centralize formatting helper and reuse everywhere.
- Risk: division edge cases. Mitigation: explicit zero-cost handling with `∞`.
- Open question: preferred decimal precision; defaulting to two decimals for readability.

## Dependencies
- Existing `score` and `cost` values already present in stats dictionaries.

## Migration / Rollout / Rollback
- Rollout: standard release, no migration.
- Rollback: revert `app.py` column definitions and ratio formatter usage.

## Observability Plan
- No new telemetry required; existing logs unchanged.

## Test Strategy Summary
- Unit tests for ratio formatter behavior (non-zero and zero-cost).
- UI table tests to verify column order and inserted value positions.
- Regression run of existing table update tests.
