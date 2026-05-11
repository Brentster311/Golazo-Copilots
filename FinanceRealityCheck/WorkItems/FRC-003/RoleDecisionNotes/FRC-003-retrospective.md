# FRC-003 Retrospective

## What went well
- Role artifacts were produced quickly with clear scope boundaries.
- TDD red/green cycle was explicit and prevented API drift.
- Build and tests remained stable after feature additions.

## What did not go well
- Builder instructions recommend `git add .`, which can capture unrelated untracked files.
- Capability impact output can be ambiguous if run before code file list is finalized.

## Action items
- Keep staged file lists explicit by work item path plus known code files.
- Run capability impact once during architect and once during developer for changed files.
- Continue creating retrospective plan artifacts to standardize closure quality.

## Metrics
- Gate-blocker count per work item (target: 0).
- Time from developer start to green build (target: under 30 minutes for incremental slices).
- Regression failure count in existing tests (target: 0).
