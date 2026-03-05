# GCP-0026: Update Default Role Files with Required Outputs Format

**Status**: IMPLEMENTED

## User Story

- **Title**: Update Default Role Files with Required Outputs Format
- **As a**: Golazo Copilot user
- **I want**: Default role files to have properly formatted `## Required Outputs` sections with `file:` and `dir:` prefixes
- **So that**: The output validation feature from GCP-0025 works out of the box without requiring custom role files

## Out of Scope

- Adding new validation types beyond `file:` and `dir:`
- Changing role responsibilities or other sections
- Modifying the output_validator.py logic

## Assumptions

- **Assumption (explicit)**: All roles have identifiable required outputs that can be validated
- **Assumption (explicit)**: The `{id}` placeholder syntax is understood and will be used consistently

## Acceptance Criteria

1. [x] All 9 default role files have a `## Required Outputs` section with typed entries
2. [x] Each output uses the correct prefix: `file:` for files, `dir:` for directories
3. [x] The `{id}` placeholder is used for work item ID substitution
4. [x] Existing tests continue to pass (165 tests)
5. [x] Role notes requirement is included where applicable

## Non-Functional Requirements

- No breaking changes to existing role file structure
- Maintain backward compatibility with existing role files

## Telemetry / Metrics Expected

- None

## Rollout / Rollback Notes

- Safe to deploy - additive change only
- Existing role files without typed outputs will continue to work (empty validation)
