# FRC-004 Retrospective

## What went well
- Sequential role flow from FRC-003 to FRC-004 remained consistent.
- Red/green testing pattern prevented contract regressions.
- Build and packaging remained healthy during feature expansion.

## What did not go well
- Untracked root-level capability file can introduce noise during staging.
- Role instructions occasionally mention broad staging (`git add .`) that can include unrelated files.

## Action items
- Keep explicit staged-file lists scoped to work item plus intended code/docs.
- Add a pre-commit status check step in builder notes template.
- Keep capability contract updates synchronized with each feature increment.

## Metrics
- Unexpected staged-file count per work item (target: 0).
- Number of transition retries due missing artifacts (target: 0).
- Regression failures across prior stories (target: 0).
