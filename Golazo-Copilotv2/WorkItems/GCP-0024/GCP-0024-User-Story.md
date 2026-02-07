# GCP-0024: Evidence Requirements Enhancement & Role Order Update

## User Story

**As a** development team using Golazo Copilot,  
**I want** stricter evidence requirements for DoD items and a more logical role ordering,  
**So that** all roles produce meaningful artifacts and the workflow matches natural development flow.

## Background

The previous implementation allowed "N/A: reason" as valid evidence for `refactorComplete`, which provided an escape hatch that could be abused. Additionally, the role order had Builder before Documentor, which didn't match the natural flow where documentation should be updated before final build verification.

## Acceptance Criteria

1. **N/A Evidence Removed**
   - [ ] `NA_ALLOWED_ITEMS` constant removed
   - [ ] `validate_na_evidence()` function removed
   - [ ] All DoD items require concrete evidence

2. **refactorComplete Requires File**
   - [ ] Added to `FILE_EVIDENCE_ITEMS`
   - [ ] Requires Refactoring Plan file: `WorkItems/<id>/Design/<id>-Refactoring-Plan.md`
   - [ ] Evidence hint updated

3. **retroComplete DoD Item Added**
   - [ ] Added to `VALID_DOD_ITEMS`
   - [ ] Added to `WorkItemState.dod` defaults
   - [ ] Requires Retro Plan file: `WorkItems/<id>/Design/<id>-Retro-Plan.md`
   - [ ] Evidence hint added

4. **Role Order Updated**
   - [ ] New order: Developer → Refactor Expert → Documentor → Builder → Retrospective
   - [ ] `TRANSITIONS` dict updated
   - [ ] `PHASE_MAP` updated (Builder now in completion phase)
   - [ ] `ROLE_ORDER` list updated

5. **Tests Updated**
   - [ ] N/A evidence tests converted to rejection tests
   - [ ] `retroComplete` evidence test added
   - [ ] All 133 tests pass

6. **Documentation Updated**
   - [ ] README.md evidence table updated
   - [ ] bootstrap-instructions.md artifact table includes Refactoring Plan and Retro Plan
   - [ ] copilot-instructions.md role sequence updated
   - [ ] Version bumped to 2.16.0

## Technical Notes

### Files Modified
- `src/golazo_copilot/core/evidence.py` - Remove N/A, add FILE_EVIDENCE_ITEMS entries
- `src/golazo_copilot/core/transitions.py` - Role order changes
- `src/golazo_copilot/core/checklists.py` - Add retroComplete
- `src/golazo_copilot/core/types.py` - Add retroComplete to defaults
- `tests/test_evidence.py` - Update edge case tests
- `README.md`, `bootstrap-instructions.md`, `copilot-instructions.md` - Docs

### New DoD Item Mapping (8 total)

| Item | Role | Evidence Type |
|------|------|---------------|
| branchCreated | Developer | Git branch |
| testsWrittenFirst | Developer | File paths |
| testsPass | Developer | Command output |
| refactorComplete | Refactor Expert | File path |
| docsUpdated | Documentor | File paths |
| buildPasses | Builder | Command output |
| committed | Builder | Git SHA |
| retroComplete | Retrospective | File path |

## Status

✅ **IMPLEMENTED** - All code changes complete, tests passing, docs updated.
