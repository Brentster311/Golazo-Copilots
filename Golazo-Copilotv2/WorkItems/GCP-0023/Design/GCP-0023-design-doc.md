# Design Doc: GCP-0023 - DoR/DoD Evidence-Based Validation

## Summary
Enhance `gcp_mark_dor` and `gcp_mark_dod` tools to require verifiable evidence when marking items complete, replacing blind boolean claims with validated proof.

## Problem Statement
Currently, DoR/DoD items can be marked complete with a simple boolean claim:
```python
gcp_mark_dor(work_item_id="GCP-0001", item="userStory")  # No proof required
```

This allows:
- Claiming "testsPass" without running tests
- Claiming "userStory" without the file existing
- No audit trail of what was actually verified

## Business Case

### Why Now
- Workflow integrity is foundational to Golazo's value proposition
- Users are already bypassing gates with unverified claims
- Evidence collection enables future automation (CI integration, audits)

### Impact
- Higher confidence that gates are meaningful
- Audit trail for retrospectives and compliance
- Foundation for automated validation

### KPIs
- 100% of new marks include evidence
- Evidence validation catches >90% of invalid claims
- No increase in time-to-complete for legitimate workflows

## Stakeholders
- **Developers** using Golazo workflow
- **Project Owners** reviewing work items
- **Golazo maintainers** (backward compatibility)

## Functional Requirements

### FR1: Evidence Parameter Required
- `gcp_mark_dor` and `gcp_mark_dod` require an `evidence` parameter
- Calls without evidence return an error with expected format

### FR2: Evidence Validation by Type

| Item | Evidence Type | Validation |
|------|---------------|------------|
| `userStory` | File path | File exists |
| `designDoc` | File path | File exists |
| `reviewComments` | File path | File exists |
| `testCases` | File path | File exists |
| `branchCreated` | Branch name | `git branch --list <name>` returns match |
| `testsWrittenFirst` | File path(s) | Files exist |
| `testsPass` | Command output or CI link | Accept as-is (string) |
| `buildPasses` | Command output or CI link | Accept as-is (string) |
| `docsUpdated` | File path(s) | Files exist |
| `refactorComplete` | File path or "N/A: <reason>" | File exists OR starts with "N/A:" |
| `committed` | Git SHA | `git rev-parse <sha>` succeeds |

### FR3: Evidence Storage
- State.json stores evidence alongside completion status
- Schema change: `dor: { userStory: { complete: true, evidence: "path", validated_at: "ISO8601" } }`

### FR4: Clear Error Messages
- Error includes: what's missing, expected format, example
- Example: `"Missing evidence for 'userStory'. Expected: file path to User Story markdown (e.g., 'WorkItems/GCP-0001/GCP-0001-User-Story.md')"`

## Non-Functional Requirements

### NFR1: Backward Compatibility
- Existing state.json files with boolean DoR/DoD continue to work
- Only NEW marks require evidence
- Migration: no forced update of existing work items

### NFR2: Performance
- File existence checks: <10ms per file
- Git operations: <100ms per operation
- No network calls (all local validation)

### NFR3: Error Recovery
- Invalid evidence doesn't corrupt state
- Validation failures are recoverable (fix and retry)

## Proposed Approach

### Phase 1: Schema Update (state.py)
1. Update `WorkItemState` model to support evidence structure
2. Add backward-compatible parsing of old boolean format
3. Add `evidence` field to DoR/DoD item schema

### Phase 2: Validation Functions (new file: evidence.py)
1. Create `validate_file_evidence(path: str, work_items_dir: Path) -> bool`
2. Create `validate_git_branch(branch: str) -> bool`
3. Create `validate_git_commit(sha: str) -> bool`
4. Create `validate_evidence(item: str, evidence: str, work_items_dir: Path) -> tuple[bool, str]`

### Phase 3: Update Mark Tools (gcp_mark_dor.py, gcp_mark_dod.py)
1. Add `evidence` parameter (required)
2. Call validation before updating state
3. Store evidence in state.json
4. Return clear error on validation failure

### Phase 4: Update Tests
1. Update all existing tests to provide evidence
2. Add tests for validation logic
3. Add tests for backward compatibility

## Alternatives Considered

### Alt 1: Optional Evidence (Rejected)
- Keeps evidence optional, warns if missing
- **Rejected**: Defeats the purpose; warnings are ignored

### Alt 2: Automatic Evidence Detection (Rejected)
- Tool automatically finds evidence based on conventions
- **Rejected**: Magic behavior is error-prone; explicit is better

### Alt 3: External Validation Service (Rejected)
- CI/CD integration for evidence validation
- **Rejected**: Out of scope; adds complexity and network dependency

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing workflows | Medium | High | Backward compat for old state.json |
| Git not installed/available | Low | Medium | Graceful error with instructions |
| Evidence path wrong format | Medium | Low | Clear error messages with examples |
| Test update burden | High | Medium | Provide evidence helper in tests |

## Open Questions
1. Should we support relative vs absolute paths? **Recommendation:** Relative to workspace root
2. Should evidence be required for `complete=False` (unmarking)? **Recommendation:** No

## Dependencies
- Python `subprocess` for git commands
- Existing `pathlib` for file operations
- No new external dependencies

## Migration / Rollout Plan

### Rollout
1. v2.15.0: Ship with evidence required for new marks
2. Existing work items continue to function
3. Documentation updated with evidence examples

### Rollback
- If issues arise, revert to evidence-optional mode
- State.json format is forward-compatible (old code ignores evidence field)

## Observability Plan
- Log validation attempts and results
- Track: evidence type, validation result, time taken
- No PII in logs (file paths only, not contents)

## Test Strategy Summary
- Unit tests for each validation function
- Integration tests for mark tools with valid/invalid evidence
- Backward compatibility tests with old state.json format
- Error message content tests
