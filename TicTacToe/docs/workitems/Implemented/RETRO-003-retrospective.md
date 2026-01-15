# Retrospective: RETRO-003 - Folder Structure Not Reviewed

**Status: ? IMPLEMENTED**

## Trigger
The project folder structure uses generic Visual Studio default names (`PythonApplication2\PythonApplication2\`) that provide no context about the application. No Golazo role flagged this as an issue.

## What Happened

### Current Structure (Problematic)
```
PythonApplication2\                    ? Generic project folder
??? PythonApplication2\                ? Nested folder with same generic name
?   ??? PythonApplication2.py          ? Generic file (WIP-005 addresses)
?   ??? test_tictactoe.py              ? Well-named
?   ??? docs\                          ? Was incorrectly placed (RETRO-001)
??? PythonApplication2.pyproj          ? VS project file
??? PythonApplication2.sln             ? VS solution file
```

### Ideal Structure
```
tictactoe\                             ? Descriptive project folder
??? tictactoe\                         ? Package folder (or just files at root)
?   ??? tictactoe.py                   ? Descriptive filename
?   ??? test_tictactoe.py              ? Test file
??? tictactoe.pyproj                   ? VS project file
??? tictactoe.sln                      ? VS solution file
```

### Root Cause
1. **Visual Studio defaults accepted**: Project created with VS template, names not changed
2. **No folder structure review**: Reviewer role didn't include folder/directory naming
3. **Scope creep concern**: Renaming folders is more invasive than renaming files

## Impact

- Folder names provide no context about the application
- Confusing nested structure with duplicate names
- Harder to navigate and understand project organization

## Resolution

1. Updated Golazo instructions to include folder structure review in Reviewer role
2. Created WIP-006 to address folder renaming (separate from WIP-005 file rename)

## Process Improvement Proposal

### Change: Add Folder Structure to Reviewer Responsibilities

Update Reviewer section to include folder/directory structure review:

```markdown
### 3) Reviewer — Design critique

Review the design for:
- Clarity and completeness
- Feasibility and sequencing
- Risk coverage
- Operability and on-call impact
- Edge cases and failure modes
- Cost / performance tradeoffs
- Naming clarity (files, classes, methods, variables)
- Folder/directory structure and organization
```

## Lessons Learned

1. IDE-generated project structures should be evaluated, not blindly accepted
2. Folder naming is as important as file naming for code organization
3. Reviewer should consider the full project structure, not just the design document

## Related Work Items

- RETRO-001: Artifact path locations
- RETRO-002: File naming not reviewed
- WIP-005: Rename game file to tictactoe.py
- WIP-006: Rename project folders (to be created)
