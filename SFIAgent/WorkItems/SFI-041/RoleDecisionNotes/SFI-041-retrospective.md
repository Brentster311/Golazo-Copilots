# SFI-041 Retrospective Notes

## What went well
- Role-gated workflow produced complete delivery artifacts with clear traceability from story to design, QA, implementation, refactor, builder, and documentation outputs.
- Test-first implementation was applied and validated with strong targeted evidence:
  - `test_sfi_041_action_owner.py` added in Red phase.
  - Builder verification run passed `144` tests in `3.34s` across impacted suites.
- Build confidence was high: both distributions were successfully built in builder role:
  - `sfi_reporter-0.2.0` (sdist + wheel)
  - `s360_client-0.1.0` (sdist + wheel)
- Capability impact analysis was used multiple times (architect, refactor, builder), keeping blast-radius discussion explicit and consistent.

## What did not go well
- Capability registry validation surfaced pre-existing baseline drift (missing files in `reporter-tk-app`, `reporter-llm`, and `reporter-tests` capability cards), which reduced trust in `validate` as a release-readiness signal for this item.
- Environment/tooling friction appeared in refactor role due to initial interpreter mismatch before re-running with the workspace interpreter.
- Large legacy modules (`dialogs.py`, `data.py`) remain above modularity thresholds, making safe refactor opportunities harder to realize inside feature-scoped work items.
- Process evidence is strong but fragmented across role notes; assembling summary metrics required manual cross-document synthesis.

## Capability registry observations
- Observed usage in this work item:
  - `impact` analysis was used for changed files and consistently identified `reporter-data` as directly impacted with transitive impacts to `reporter-tk-app`, `reporter-eta-logic`, `reporter-query-builder`, `reporter-build`, and `reporter-tests`.
  - `validate` was used in builder role and correctly identified baseline registry/file drift not introduced by SFI-041.
- Missed opportunity:
  - Capability `validate` was not run earlier (pre-developer). Running it earlier would have surfaced baseline issues sooner and reduced surprise during builder handoff.

## Metrics
- Workflow completion metrics (SFI-041):
  - Roles completed before retrospective: `9/10`.
  - Required outputs for retrospective before this note: `0/1`; after this note: `1/1`.
  - Role decision notes present (including retrospective): `10`.
  - Design artifacts present: `4` (`design-doc`, `review-comments`, `test-cases`, `capability-impact`).
- Quality/build metrics:
  - Targeted regression result: `144 passed` in `3.34s`.
  - Package build success count: `2/2` projects built successfully.
  - New feature test module count: `1` (`test_sfi_041_action_owner.py`).
- Capability-registry usage metrics:
  - Distinct roles that referenced capability analysis: `3` (architect, refactor, builder).
  - Builder impact result cardinality: `6` affected capabilities.
  - Baseline capability validation misses observed: `5` key files across `3` capabilities (documented as out-of-scope baseline drift).

## Action items (process improvements)
1. Add a **Program Manager gate checklist item**: run `golazo_capabilities(action="validate")` at planning time and document baseline drift status before implementation starts.
2. Add a **Builder handoff template block** requiring two explicit capability metrics: affected capability count from `impact` and baseline drift count from `validate`.
3. Add an **Environment readiness step** in developer/refactor role templates: confirm workspace interpreter path before first test run.
4. Add a **Retrospective metrics rollup section** to each role note template (tests run, pass count, build outputs, capability commands used) to eliminate manual synthesis.
5. Open a separate process work item to reconcile `capabilities.yaml` with existing file layout for `reporter-tk-app`, `reporter-llm`, and `reporter-tests`.

## Success criteria for the above actions
- By next 3 work items, `100%` include early capability `validate` evidence in PM notes.
- Builder notes include both capability metrics (`impact` count + drift count) in `100%` of work items.
- Interpreter mismatch incidents in role notes drop from current observed `1` event in SFI-041 to `0` in next 5 work items.
- Retrospective compilation time target: reduce manual synthesis effort by at least `50%` (measured by number of source notes manually scanned).

## Assumptions documented
- Metrics are derived from committed role notes/build evidence for SFI-041 and represent workflow/process signals, not product KPI outcomes.
- Baseline capability-registry misses existed prior to this work item and were not introduced by SFI-041 implementation.