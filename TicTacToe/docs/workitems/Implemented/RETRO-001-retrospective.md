# Retrospective: RETRO-001 - Misplaced Role Documents

**Status: ? IMPLEMENTED**

## Trigger
During WIP-001 and WIP-002 implementation, the Developer, Refactor Expert, and Builder role documents were created in the wrong location (`PythonApplication2\docs\roles\`) instead of the correct location (`docs\roles\`).

## What Happened

### Timeline
1. WIP-001 Developer role created files inside project directory
2. Pattern continued for Refactor and Builder roles
3. WIP-002 repeated the same mistake
4. User noticed missing files when reviewing `docs\roles\` directory

### Root Cause
When executing terminal commands, the working directory was inside `PythonApplication2\PythonApplication2\`. When creating role documents, I used relative paths that resolved to the project directory rather than the solution root.

The Golazo instructions specify:
> `docs/roles/<workitem-id>-developer.md`

But I created:
> `PythonApplication2/docs/roles/<workitem-id>-developer.md`

## Impact

- 6 role documents were in wrong location
- Inconsistent artifact structure
- Harder to find documents when reviewing work items

## Resolution

- Moved all 6 files to correct `docs\roles\` location
- Deleted misplaced files from `PythonApplication2\docs\roles\`

## Process Improvement Proposal

### Proposed Change to Golazo Instructions

Add the following clarification to the **Required artifacts and locations** section:

```markdown
### Important: Artifact Path Context

All artifact paths are **relative to the solution/repository root**, NOT the current working directory or project directory.

When creating role documents, ALWAYS use paths starting from the solution root:
- ? Correct: `docs/roles/<workitem-id>-developer.md`
- ? Wrong: `<ProjectName>/docs/roles/<workitem-id>-developer.md`

Before creating any artifact file, verify:
1. The path starts from the solution root
2. The path matches the convention in this document
3. Other artifacts for the same work item are in the same parent directory
```

### Checklist Addition

Add to the **DoD Checklist**:

```markdown
- [ ] All artifacts are in correct locations (relative to solution root)
```

## Lessons Learned

1. Terminal working directory context can cause path confusion
2. Role documents created later in workflow (Developer, Refactor, Builder) are more prone to this error because terminal context may have changed
3. A quick file listing before creating artifacts would catch this

## Verification

All role documents now in correct locations:

| Work Item | Role | Correct Location |
|-----------|------|------------------|
| WIP-001 | Developer | `docs\roles\WIP-001-developer.md` ? |
| WIP-001 | Refactor | `docs\roles\WIP-001-refactor.md` ? |
| WIP-001 | Builder | `docs\roles\WIP-001-builder.md` ? |
| WIP-002 | Developer | `docs\roles\WIP-002-developer.md` ? |
| WIP-002 | Refactor | `docs\roles\WIP-002-refactor.md` ? |
| WIP-002 | Builder | `docs\roles\WIP-002-builder.md` ? |

## Implementation Status

**Changes applied to `.github\copilot-instructions.md`:**

1. ? Added "Important: Artifact Path Context (RETRO-001)" section under "Required artifacts and locations"
2. ? Added `[ ] All artifacts in correct locations (solution root)` to DoD Checklist in status header
