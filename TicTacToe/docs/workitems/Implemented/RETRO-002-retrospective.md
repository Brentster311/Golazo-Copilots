# Retrospective: RETRO-002 - File Naming Not Reviewed

**Status: ? IMPLEMENTED**

## Trigger
The main game file was named `PythonApplication2.py` - a generic Visual Studio default name that provides no indication of what the application does. No Golazo role flagged this as an issue despite multiple opportunities.

## What Happened

### Timeline
1. WIP-001 started with existing empty file `PythonApplication2.py`
2. All roles accepted this filename without question
3. Developer implemented code in the existing file
4. Refactor Expert focused on code structure, not file naming
5. User identified the issue after WIP-002 completion

### Root Cause
1. **Pre-existing file accepted blindly**: The workspace had a starter file with a poor name
2. **Ambiguous instruction**: "Improve structure and naming" in Refactor Expert role was interpreted as code naming only
3. **No explicit file naming checkpoint**: No role explicitly requires reviewing file/module names

### Roles That Should Have Caught This

| Role | Responsibility | Gap |
|------|----------------|-----|
| Program Manager | Design Review | Should specify file naming in "Proposed Approach" |
| Reviewer | Clarity and completeness | Should flag unclear naming |
| Architect | Architectural alignment | Should review module/file naming conventions |
| Refactor Expert | Improve naming | Ambiguous - should explicitly include file names |

## Impact

- File name `PythonApplication2.py` provides no context about the application
- Imports in test file use unclear module name
- Reduces code discoverability and maintainability

## Resolution

1. Created WIP-005 to rename file to `tictactoe.py`
2. Updated Golazo instructions to clarify naming scope

## Process Improvement Proposal

### Change 1: Clarify Refactor Expert Responsibilities

Update Refactor Expert section to explicitly include file naming:

```markdown
### 7) Refactor Expert — Simplification pass

After tests are green:
- Remove duplication
- Improve structure and naming (including file/module names)
- Reuse existing patterns
- Do not change observable behavior
```

### Change 2: Add File Naming to Program Manager Design Review

Add to the Design Review template:

```markdown
- File/module naming conventions
```

### Change 3: Add Reviewer Checklist Item

Add to Reviewer responsibilities:

```markdown
- Naming clarity (files, classes, methods, variables)
```

## Lessons Learned

1. Pre-existing files should be scrutinized, not blindly accepted
2. "Naming" should explicitly encompass all naming: files, classes, methods, variables
3. Generic IDE-generated names are a code smell that should be flagged
