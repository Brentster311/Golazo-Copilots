# GCP-0065 Retrospective

## What Went Well
- Role handoffs were clear and artifacts were consistently produced across design, implementation, and delivery roles.
- Architectural intent stayed stable end-to-end: canonical capability registry path (`WorkItems/capabilities.yaml`) plus deterministic legacy migration behavior.
- Developer role used capability impact analysis (`golazo_capabilities(action="impact")`) to identify direct and transitive blast radius (`tool-capabilities`, `mcp-server`), which helped keep implementation focused.
- Builder role executed capability registry validation (`golazo_capabilities(action="validate")`) and confirmed all declared `key_files` existed across 16 capabilities.
- Test-first behavior in the developer role was effective for the changed scope (`tests/test_gcp_capabilities.py`: 21 passing), reducing regression risk for the targeted capability-path logic.

## What Did Not Go Well
- Baseline repository state was not green during downstream roles (`pytest`: 519 passed, 1 failed), with failure in `tests/test_golazo_update.py::TestCheckAction::test_tc06b_check_http_401_fallback_pip_index_success` unrelated to GCP-0065 scope.
- Current role gate language expects green baseline before refactor/documenter/builder actions, but practical execution required exceptions to proceed with no-op refactor and doc/build completion. This created policy friction and inconsistent decision handling.
- Refactor role found a fixable lint issue (`ruff I001`) but correctly did not auto-apply changes due baseline red state, leaving minor technical debt in place.
- Builder command hygiene was imperfect (`Push-Location golazo-copilot` warning from already-correct cwd), adding avoidable noise to verification logs.
- Capability registry consultation was useful but not uniformly required at each phase; missed opportunity to standardize when and how impact analysis must be recorded.

## Capability Registry Usage Assessment
- Was it consulted: Yes.
- Where used:
  - Developer: `golazo_capabilities(action="impact")` for changed files.
  - Builder: `golazo_capabilities(action="validate")` before finalization.
- Value gained:
  - Improved confidence in change scope by explicitly linking file edits to affected capabilities.
  - Confirmed registry integrity (`key_files`) at build stage, reducing risk of latent metadata drift.
- Gap observed:
  - No explicit workflow gate requiring documented capability impact evidence before code merge/final closure.

## Action Items (Measurable)
1. Add a formal "Baseline State" classification gate before Refactor/Documenter/Builder.
- Definition:
  - `green`: all tests pass.
  - `yellow`: baseline has known unrelated failures with explicit evidence and issue link.
  - `red`: new or unknown failures introduced by current work item.
- Measure:
  - 100% of work items record one classification and evidence in role notes before refactor.

2. Add "Unrelated Failure Exception" template to role instructions.
- Definition:
  - Required fields: failing test id, first failing commit (if known), why unrelated, allowed role actions, prohibited actions.
- Measure:
  - 0 ad-hoc exception narratives; 100% of non-green baseline executions use the template.

3. Enforce capability-impact evidence at least once before leaving Developer role.
- Definition:
  - Required command output snippet for `golazo_capabilities(action="impact", files=[...])` in developer notes.
- Measure:
  - >=95% of work items with source edits include explicit direct/transitive capability listing.

4. Enforce capability-registry validation in Builder role for complete profile.
- Definition:
  - `golazo_capabilities(action="validate")` output must be captured in builder notes.
- Measure:
  - 100% of complete-profile work items contain validation evidence and pass/fail result.

5. Add command preflight check for builder scripts (cwd and path assumptions).
- Definition:
  - Preflight step verifies current directory and skips redundant `Push-Location`.
- Measure:
  - Reduce non-actionable path warnings in builder logs by >=90% over next 10 work items.

6. Introduce baseline-failure trend metric in retrospective.
- Definition:
  - Track count of work items executed on non-green baseline and whether closure was blocked.
- Measure:
  - Weekly report includes: non-green rate, unrelated-failure rate, and time-to-closure delta; target <=20% non-green executions over next release cycle.

## Metrics To Track Next Cycle
- Baseline classification coverage: target 100%.
- Exception-template usage on yellow baseline: target 100%.
- Developer capability-impact evidence coverage: target >=95%.
- Builder capability validation evidence coverage: target 100%.
- Builder log warning reduction (cwd/path): target >=90% reduction.
- Non-green baseline execution rate: target <=20%.
