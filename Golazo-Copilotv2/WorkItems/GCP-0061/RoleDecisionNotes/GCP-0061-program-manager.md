# GCP-0061 — Program Manager Decision Notes

## Decisions
1. Deliver a behavior-preserving internal refactor only: modularize MCP dispatch/registration internals without changing tool contracts.
2. Enforce module boundary clarity around three concerns: routing/dispatch, handlers, and response formatting/error normalization.
3. Keep `server.py` as a thin orchestration/bootstrap entry point after extraction.
4. Sequence work incrementally (utility extraction first, then handlers, then registration wiring) to reduce blast radius and improve reviewability.
5. Treat deterministic error behavior and rollback readiness as explicit operational gates, not implicit outcomes.
6. Require concise developer-facing notes describing extension points for adding tools post-refactor.

## Assumptions Applied
- GCP-0061 is a direct follow-up to GCP-0060 maintainability closure guidance.
- Existing MCP tool names, required parameter semantics, and success/error response shapes are immutable compatibility constraints.
- Refactor scope remains within `golazo-copilot/src/golazo_copilot` and is validated primarily by existing tests.
- No workflow gate/order/state-schema semantic changes are permitted in this item.

## Scope Guardrails Applied
- Included: internal decomposition of dispatch/registration logic, boundary documentation, parity-focused testing.
- Excluded: new MCP tools, changed tool I/O contracts, new workflow features/policies, unrelated architectural rewrites.
- Constraint: any detected contract drift is treated as a release blocker.

## Rationale
- Concentrated responsibilities in `server.py` currently raise maintenance cost and defect probability.
- Modular boundaries improve change isolation, review quality, and onboarding speed.
- Incremental extraction minimizes risk while preserving straightforward rollback options.

## Risks & Mitigations
- Risk: subtle behavior drift in validation/error messaging during extraction.
  - Mitigation: parity tests for failure paths and deterministic message intent.
- Risk: registration mismatch causing runtime tool lookup failures.
  - Mitigation: explicit assertions for registered names/required params and integration checks.
- Risk: added indirection introduces latency regression.
  - Mitigation: smoke timing checks and staged rollout with regression monitoring.
- Risk: refactor churn spreads beyond server plumbing.
  - Mitigation: strict scope control and slice-by-slice review gates.

## Operational Notes
- On-call priorities: tool-not-found incidents, abnormal invalid-parameter spikes, dispatch failure-rate changes.
- Rollback trigger: any contract regression or elevated dispatch failure profile.
- Rollback method: revert to prior `server.py` wiring/slice-level commits while preserving external behavior guarantees.

## Handoff Notes
- Architect: validate boundary design, failure-mode handling, and staged sequencing feasibility.
- Developer: execute extraction in incremental slices with parity-first tests and no contract changes.
- QA: verify unchanged external behavior across success and failure paths; confirm no expectation drift in regression suites.
- Documenter: produce concise maintainer notes for registration/handler extension points.
