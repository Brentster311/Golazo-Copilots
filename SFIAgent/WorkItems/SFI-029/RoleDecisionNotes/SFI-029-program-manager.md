# SFI-029 — Program Manager Decision Notes

## Design Choices
- N-level grouping driven by org tree structure, not hardcoded 2-level model
- `OrgAncestry` NamedTuple to be replaced with variable-length ancestry path (list of manager names)
- Aggregation functions updated to support N-level rollup
- Three-phase approach: data layer → UI layer → tests

## Sequencing
- Data layer first (get_org_mapping, get_service_owners) — independently testable
- UI changes after data layer validated
- Tests updated alongside each phase
