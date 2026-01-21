# GCP-003: Design Document

## Summary
Update Golazo workflow documentation to enforce TDD (test-first) development and assign git branch/commit operations to the Builder role.

## Problem Statement
Two process violations were identified in RETRO-001:
1. **TDD Violation**: Developer wrote production code before test code
2. **Git Gap**: No role owned git operations; human was asked to commit manually

These gaps reduce workflow consistency and discipline.

## Business Case

### Why Now
- Process violation just occurred in GCP-002
- Fixing now prevents repetition in future work items
- Small change with high impact on quality

### Impact
- **Positive**: Consistent TDD practice across all work items
- **Positive**: Git operations automated within workflow
- **Measurable**: Future work items will have tests committed before code

## Proposed Changes

### 1. Update Developer Role (`developer.md`)

**Add to Responsibilities:**
```markdown
- **Write test code FIRST** based on Test Cases document
- Verify tests fail initially (red phase of TDD)
- Then implement production code to make tests pass (green phase)
```

**Add to Forbidden actions:**
```markdown
- May NOT write or modify production code before test code exists for new functionality
- May NOT skip the red-green-refactor cycle
```

### 2. Update Builder Role (`builder.md`)

**Add to Responsibilities:**
```markdown
- **Before Developer role**: Create feature branch `<workitem-id>` if it doesn't exist
- **After Documentor role**: Stage all changes, commit with message `<workitem-id>: <title>`, push to origin
```

**Add new section:**
```markdown
## Git Operations

### Branch Creation (before Developer)
git checkout -b <workitem-id>

### Commit (after Documentor)
git add .
git commit -m "<workitem-id>: <User Story title>"
git push -u origin <workitem-id>
```

### 3. Update Spine (`copilot-instructions.md`)

**Update DoD Checklist:**
```markdown
- DoD Checklist:
  - [ ] Feature branch `<workitem-id>` created
  - [ ] Test code written before production code
  - [ ] Automated tests pass
  ...
  - [ ] Changes committed to git by Builder
```

**Update State transition rules:**
```markdown
- Before **Developer**: Builder ensures feature branch exists
- After **Documentor**: Builder commits and pushes all changes
```

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Git hooks | Automated enforcement | Complex setup | Rejected |
| Pre-commit checks | Catches violations | Requires tooling | Future work |
| Manual enforcement | Simple | Error-prone | Current (with docs) |

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Git commands fail | Builder prints clear error; human can intervene |
| Branch already exists | Use `git checkout -b` with error handling |
| TDD still violated | Clear documentation; Copilot will self-correct |

## Test Strategy
- No automated tests (documentation-only changes)
- Verification: Read updated files and confirm changes present
