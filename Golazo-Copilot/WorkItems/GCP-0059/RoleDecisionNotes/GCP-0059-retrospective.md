# GCP-0059 — Retrospective

## What went well
- Requirement pivots were absorbed quickly and reflected across User Story, design doc, and role decision notes without scope creep.
- Implementation and validation quality were strong: relevant targeted tests passed, broader suite passed, and build completed successfully.
- Final path contract was implemented consistently as `.github/agents/golazo-copilot/orchestrator.md` and `.github/agents/golazo-copilot/roles/...`.
- Inline-only rule for Retrospective was added to workspace instruction files and bootstrap template, reducing recurrence risk.

## What didn't go well
- Requirement wording changed multiple times, creating churn and rework in upstream artifacts.
- Workflow execution was briefly blocked because `.github/copilot-instructions.md` was missing at repo root after moving to agent-scoped instruction location.
- Subagent behavior during Retrospective created confusion because policy intent and effective runtime behavior were out of sync.

## Action items
- Add an automated bootstrap invariant check that ensures `.github/copilot-instructions.md` exists even when agent-specific instructions are used.
- Add/extend tests for role execution policy to enforce: Retrospective always inline, no `runSubagent` allowed in that role.
- Add a single canonical path-constants section for bootstrap outputs and reference it from docs/tests to reduce path drift.
- Add a lightweight requirement-freeze checkpoint at end of Program Manager phase to reduce late path/name churn.

## Metrics
- Rework indicator: count of requirement path/name revisions per work item (target: <=1 after Program Manager sign-off).
- Workflow reliability: % of runs with no instruction-file gate failures (target: 100%).
- Policy compliance: % of Retrospective executions run inline (target: 100%).
- Documentation consistency: count of mismatched path references across User Story/design/tests (target: 0 at builder sign-off).
