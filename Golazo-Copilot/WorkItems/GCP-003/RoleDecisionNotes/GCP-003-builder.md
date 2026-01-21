# GCP-003: Builder Decision Document

## Work Item
GCP-003 — Enforce TDD and Builder Git Operations

## Git Operations

### Branch Status
? Branch `GCP-003` created at start of work item

### Build Verification
? No build required (documentation-only changes)

### File Verification
| File | Status |
|------|--------|
| `.github/roles/developer.md` | ? Updated with TDD requirements |
| `.github/roles/builder.md` | ? Updated with git operations |
| `.github/copilot-instructions.md` | ? Updated DoD and state machine |

### Test Case Verification

| Test Case | Result |
|-----------|--------|
| TC-001: Developer TDD requirement | ? "Write test code FIRST" present |
| TC-002: Developer TDD forbidden | ? "May NOT write production code before test code" present |
| TC-003: Builder branch creation | ? "git checkout -b <workitem-id>" present |
| TC-004: Builder commit operations | ? "git add", "git commit", "git push" present |
| TC-005: DoD branch checkbox | ? "Feature branch `<workitem-id>` created" present |
| TC-006: DoD TDD checkbox | ? "Test code written before production code" present |
| TC-007: State machine git rules | ? "Before Developer" and "After Documentor" rules present |

## Commit Operations (after Documentor)
Pending Documentor completion.
