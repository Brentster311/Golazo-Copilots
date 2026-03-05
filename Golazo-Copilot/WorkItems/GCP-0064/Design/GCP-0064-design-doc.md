# Design Doc — GCP-0064

## Summary
Refactor `golazo_status.py` into smaller, cohesive units while preserving existing behavior and public contract. The goal is maintainability and lower complexity, not feature change.

## Problem statement
`golazo_status.py` currently carries multiple responsibilities (state loading, output validation checks, stale-file checks, registry hints, progress computation, formatting support wiring), increasing cognitive load and change risk.

## Business case (why now, impact, KPIs)
### Why now
A prior work item retrospective identified modularity risk and recommended decomposition as follow-up work.

### Impact
- Faster and safer future changes to status logic.
- Improved readability and reviewability.
- Better separation for targeted testing.

### KPIs
- Existing status test suite passes unchanged.
- Reduced file-level complexity in `golazo_status.py` (line count/function density).
- No user-visible regressions in status payload/format behavior.

## Stakeholders
- Golazo maintainers
- Orchestrator/agent users who rely on `golazo_status`
- Test/quality owners

## Functional requirements
1. Preserve `golazo_status` external behavior and response shape.
2. Decompose logic into focused helpers/modules with clear boundaries.
3. Keep compatibility with existing workflows/profiles/closure handling.
4. Keep stale-file/version and output validation behavior intact.

## Non-functional requirements
- Low-risk incremental refactor.
- No performance regression beyond acceptable noise.
- Maintain deterministic behavior.

## Proposed approach (high level)
1. Identify responsibility seams in `golazo_status.py`.
2. Extract helpers (e.g., version/staleness checks, registry hinting, role progress, output/missing-notes checks).
3. Keep orchestration in `golazo_status` thin and readable.
4. Run existing status/bootstrap tests after each extraction step.

## Alternatives considered
1. Leave as-is — rejected (ongoing maintainability risk).
2. Full rewrite — rejected (higher regression risk).
3. Extract helper module(s) incrementally — selected.

## Risks, mitigations, open questions
### Risks
- Behavioral drift during refactor.
- Subtle formatting changes in status outputs.

### Mitigations
- Preserve existing tests and add targeted tests only where needed.
- Refactor in small steps and run tests frequently.

### Open questions
- Whether additional internal module boundaries should be formalized beyond this pass.

## Dependencies
- `golazo-copilot/src/golazo_copilot/tools/golazo_status.py`
- Existing tests under `golazo-copilot/tests`

## Migration / rollout / rollback plan
### Rollout
- Implement incremental extraction and validate with targeted/broader tests.

### Rollback
- Revert refactor commits if compatibility issues emerge.

## Observability plan
- Validate status behavior via existing tests and sample status calls.
- Compare key fields before/after where needed.

## Test strategy summary
- Run status-focused tests first.
- Run adjacent bootstrap/transition tests after refactor.
- Add targeted unit tests only for extracted helper seams if gaps are identified.
