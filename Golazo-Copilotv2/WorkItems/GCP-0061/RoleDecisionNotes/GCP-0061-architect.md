# GCP-0061 — Architect Decision Notes

## Role Execution Summary
- Verified architect entry conditions:
  - User story present: `WorkItems/GCP-0061/GCP-0061-User-Story.md`
  - Design doc present: `WorkItems/GCP-0061/Design/GCP-0061-design-doc.md`
  - QA review comments present: `WorkItems/GCP-0061/Design/GCP-0061-Review-Comments.md`
- Reviewed design for boundaries, contracts, security/privacy, scalability/resilience, dependency risk, and rollback safety.
- Executed required capability impact analysis and documented findings in `WorkItems/GCP-0061/Design/GCP-0061-Capability-Impact.md`.
- Added architect findings to `WorkItems/GCP-0061/Design/GCP-0061-Review-Comments.md` under `Architect Notes`.

## Key Architectural Decisions
1. **Boundary-first decomposition**
   - Approve split into dispatch, handlers, and formatter utilities with `server.py` reduced to orchestration only.

2. **Strict parity constraints**
   - Keep MCP tool names, required-parameter semantics, and success/error envelopes unchanged.
   - Enforce deterministic error-category/message-intent behavior for invalid and missing parameters.

3. **Failure isolation and rollback**
   - Use reversible extraction slices (`formatters -> handlers -> registration -> orchestration`) to contain blast radius and simplify rollback.

4. **Dependency posture**
   - Prefer zero new runtime dependencies in this refactor; if any are added, require explicit security/vulnerability review.

## Capability/Dependency Impact Outcome
- Directly affected capabilities: `mcp-server`, `output-validation`.
- Transitively affected capabilities: `tool-transition`, `tool-status`, `tool-role-context`, `tool-golazo-update`.
- Compatibility posture: non-breaking and acceptable if parity gates are treated as merge-blocking.

## Assumptions Made (No Questions Asked)
- Design-referenced target module paths (`dispatch/*`, `handlers/*`, `formatters/*`) are intended extraction destinations even where files do not yet exist.
- Existing regression suites are sufficient to enforce behavior parity without introducing new user-facing contract changes.
- Existing MCP trust boundary is retained; this refactor does not create a new external entry point.

## Default-Behavior Checks Surfaced to Project Owner
- Should default formatter error verbosity remain minimal, or may richer internal context be included?
- Is exact registration ordering part of compatibility expectations, or only tool-name/parameter parity?
- Should any newly introduced file/path helper defaults be explicitly pinned (UTF-8 encoding, deterministic newlines) to avoid platform drift?

## Escalation and Scope Check
- No mandatory architectural escalation triggered.
- No scope/behavior change proposed in this architect pass.
- No additional user story created.

## Final Disposition
- **Architect decision**: Approved with constraints documented in review comments and capability impact output.
