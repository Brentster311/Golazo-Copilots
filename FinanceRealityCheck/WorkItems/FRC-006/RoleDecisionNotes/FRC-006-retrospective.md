# FRC-006 Retrospective Notes

## What went well
- UI shell scope remained tightly aligned to FRC-005 contracts.
- Deterministic frontend tests covered health, summary, and unavailable-API states.
- Build/test verification remained fast and reproducible locally.

## What did not go well
- Role transitions occasionally checked required artifacts before file-index refresh, causing immediate retry friction.
- One terminal command used an unnecessary nested Set-Location step, producing non-blocking noise.

## Action items
1. Add a short post-artifact status check before each transition to avoid premature transition attempts.
2. Normalize terminal working-directory steps in scripted commands for cleaner logs.
3. Keep frontend test count and contract assertions explicit in developer/builder notes.

## Metrics
- Transition retry count per work item (target: 0).
- Frontend contract test pass rate (target: 100%).
- Local build completion success rate (target: 100%).
