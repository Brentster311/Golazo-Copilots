# User Story: GCP-0023

**Status**: SUPERSEDED by GCP-0025 (output validation replaced evidence-based marking) and GCP-0027 (mark tools removed)

## Title
DoR/DoD Evidence-Based Validation

## Description
As a **Project Owner**, I want the `gcp_mark_dor` and `gcp_mark_dod` tools to require verifiable evidence when marking items complete, so that claims are validated rather than blindly accepted.

## Current Behavior
- `gcp_mark_dor(item="userStory")` accepts a boolean claim with no proof
- `gcp_mark_dod(item="testsPass")` can be marked without verification
- No validation that the claimed artifact actually exists

## Desired Behavior
- Each mark call must provide an `evidence` parameter pointing to verifiable proof
- The system validates the evidence exists before accepting the mark
- If evidence is missing or invalid, the mark is rejected with an actionable error

## Evidence Types by Item

### DoR Items
| Item | Required Evidence |
|------|-------------------|
| `userStory` | File path to `<workitem-id>-User-Story.md` |
| `designDoc` | File path to `<workitem-id>-Design-Doc.md` |
| `reviewComments` | File path to `<workitem-id>-Review-Comments.md` |
| `testCases` | File path to `<workitem-id>-Test-Cases.md` |

### DoD Items
| Item | Required Evidence |
|------|-------------------|
| `branchCreated` | Git branch name (verify branch exists) |
| `testsWrittenFirst` | File path(s) to test files |
| `testsPass` | Test command + exit code 0, or CI link |
| `buildPasses` | Build command + exit code 0, or CI link |
| `docsUpdated` | File path(s) to updated docs |
| `refactorComplete` | File path to refactor notes, or "N/A" with justification |
| `committed` | Git commit SHA |

## Acceptance Criteria
1. `gcp_mark_dor` rejects calls without `evidence` parameter
2. `gcp_mark_dod` rejects calls without `evidence` parameter
3. For file-based evidence, system verifies file exists at specified path
4. For git-based evidence (branch, commit), system verifies via git commands
5. For command-based evidence (tests, build), system accepts command output or CI link
6. Error messages clearly state what evidence is missing and expected format
7. Existing tests updated to provide evidence
8. State.json stores evidence alongside the boolean for audit trail

## Out of Scope
- Validating file *contents* (just existence)
- Re-running tests/builds (accept reported results)
- Integration with external CI systems (accept links as evidence)

## Technical Notes
- Evidence stored in state.json: `dor: { userStory: { complete: true, evidence: "path/to/file.md" } }`
- Backward compatibility: existing work items without evidence continue to function
- New marks require evidence
