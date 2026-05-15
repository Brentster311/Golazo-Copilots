# FRC-002 Retrospective

## What went well
- Scope stayed narrow and additive over FRC-001 baseline.
- TDD sequence was clean: red failures for missing methods, then green with deterministic alert behavior.
- Capability registry was updated with newly introduced contracts.

## What didn't go well
- Branch context drift risk remained present in the larger monorepo.
- planner.py size increased further, reinforcing modularity debt.

## Action items
1. Add a pre-commit workflow reminder to verify active branch equals current work-item id.
2. Create follow-on refactor work item to split planner.py into smaller modules.
3. Add a standard deterministic-order checklist item for all alert/query features in QA template.

## Metrics
- Branch drift incidents per work item (target: 0).
- Average planner.py line growth per work item before modular refactor (target: flatten to <= +50 lines).
- Alert determinism regressions detected in CI (target: 0).
