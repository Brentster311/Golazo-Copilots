# Role Artifact: Retrospective — SHUB-001

## Work Item
SHUB-001: Supportability Hub Documentation Index

## Trigger Condition
**User explicitly requested retrospective** after observing that the User Story was not updated to reflect implementation completion (Status remained "IN PROGRESS", Acceptance Criteria remained unchecked).

## Evidence

### What happened
1. Developer role completed implementation of the documentation index
2. Developer role verified all acceptance criteria were met (81 documents, proper format, summaries)
3. Developer role created `docs/roles/SHUB-001-developer.md` artifact
4. **Developer role failed to update** `docs/workitems/SHUB-001-user-story.md`:
   - Status should have changed: `IN PROGRESS` ? `IMPLEMENTED`
   - Acceptance criteria should have been checked: `[ ]` ? `[x]`

### Root cause
The spine (`.github/copilot-instructions.md`) states:
> "All docs are updated (User Story, Design Review, role notes)"

However, this is **too vague**. It doesn't explicitly require:
1. Updating User Story **Status** field
2. Checking off **Acceptance Criteria** as they are verified

The Developer role file (`.github/roles/developer.md`) also lacks this explicit instruction.

## Workflow Breakdown Identified

| Gap | Location | Impact |
|-----|----------|--------|
| No explicit rule to update User Story status | Spine DoD section | Status field left stale |
| No explicit rule to check acceptance criteria | Spine DoD section | AC items left unchecked |
| Developer role lacks "update User Story" responsibility | Developer role file | Easy to forget this step |

## Proposed Changes

### Change 1: Update Spine DoD Section

**File**: `.github/copilot-instructions.md`

**Current text (lines 81-89)**:
```markdown
### Definition of Done (DoD) — before considering work complete

Work is not "done" until:
- All automated tests pass (locally and/or CI)
- New or changed behavior is covered by tests
- The system builds and runs/deploys using repo-standard commands
- All docs are updated (User Story, Design Review, role notes)
- A refactor pass is completed with **no behavior change**
```

**Proposed text**:
```markdown
### Definition of Done (DoD) — before considering work complete

Work is not "done" until:
- All automated tests pass (locally and/or CI)
- New or changed behavior is covered by tests
- The system builds and runs/deploys using repo-standard commands
- All docs are updated (User Story, Design Review, role notes)
- **User Story status updated to IMPLEMENTED and all verified Acceptance Criteria checked `[x]`**
- A refactor pass is completed with **no behavior change**
```

### Change 2: Add to Absolute Enforcement Rules

**File**: `.github/copilot-instructions.md`

**Add new rule 5** after rule 4 (Retrospective):
```markdown
5) **Keep docs consistent with implementation**
- When implementation is complete, the **Developer** role MUST update the User Story:
  - Change Status from `IN PROGRESS` to `IMPLEMENTED`
  - Check off `[x]` each Acceptance Criterion that has been verified
- Stale documentation is a **process violation**.
```

### Change 3: Update Developer Role File

**File**: `.github/roles/developer.md`

**Add to Responsibilities section**:
```markdown
- **Update User Story after implementation**:
  - Change Status to `IMPLEMENTED`
  - Check off all verified Acceptance Criteria `[x]`
```

## Success Criteria for This Retrospective

- [x] Spine updated with explicit User Story update requirement in DoD (line 94)
- [x] Spine updated with new absolute enforcement rule #5 (line 34)
- [x] Developer role file updated with explicit responsibility (line 21)
- [ ] Future work items will have User Story automatically updated after implementation

## Handoff

? **Retrospective complete.** All proposed changes have been applied to instruction files.
