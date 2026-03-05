# GCP-0060 — Program Manager Decision Notes

## Decisions
1. Implement proposal-gated intent capture as MCP tool `golazo_git_propose` only; no direct git execution in scope.
2. Persist proposal history on active work item under append-only `git_actions`.
3. Enforce deterministic, action-specific validation:
   - `commit` requires `message`
   - `push` and `branch` require `branch`
4. Ensure backward compatibility by defaulting missing `git_actions` to an empty list.
5. Require explicit, actionable not-found/create guidance when work item does not exist.
6. Treat observability and operational response as first-class deliverables (error categorization and on-call signal quality).

## Assumptions Applied
- MCP tool interaction is the execution surface (no separate CLI/GUI/web requirement).
- Work-item `state.json` persistence is the system of record for audit trail storage.
- Cross-platform file behavior is required, with Windows-first validation in current environment.
- Proposal records include timestamped metadata sufficient for review and post-incident traceability.

## Scope Guardrails Applied
- Included: proposal creation, deterministic validation, state persistence, and observability/test planning.
- Excluded: direct git action execution, external approval engines/UIs, remote provider policy enforcement.
- Scope expansion deferred to future work items if richer lifecycle/status states are needed.

## Rationale
- Auditability improves most quickly by recording intent in existing work-item state rather than introducing external systems.
- Deterministic validation reduces ambiguity and enables reliable automation/tests.
- Append-only history preserves forensic integrity and simplifies reviewer trust.

## Risks & Mitigations
- Risk: proposal bypass (downstream actions with no prior intent record).
  - Mitigation: monitor prior-proposal ratio KPI and surface compliance drift.
- Risk: persistence failures under filesystem contention/errors.
  - Mitigation: explicit failure signals, categorized telemetry, and rollback-by-disable strategy.
- Risk: compatibility regressions on legacy work items missing `git_actions`.
  - Mitigation: defaults-based initialization and regression testing of round-trips.

## Operational Notes
- On-call should prioritize spikes in `workitem_not_found` and persistence write failures.
- Rollback approach is non-destructive: disable tool registration and preserve existing `git_actions` history.
- Failure modes and error categories are designed to be actionable during incident triage.

## Handoff Notes
- Architect: validate data contract boundaries, append-only semantics, and failure-handling design.
- Developer: implement tool handler, schema defaulting, deterministic errors, and tests per acceptance criteria.
- QA: verify all AC scenarios including legacy-state initialization and not-found guidance.
