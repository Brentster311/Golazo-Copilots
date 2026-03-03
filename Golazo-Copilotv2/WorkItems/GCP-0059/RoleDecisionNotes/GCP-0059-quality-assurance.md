# GCP-0059 — Quality Assurance Notes

## Review Outcome
- QA review completed against user story and design doc for the bootstrap path contract update.
- Required QA outputs are complete: review comments, AC-mapped test cases, and decision notes.
- Design is conditionally approved for implementation with one mandatory wording correction (spine filename contradiction).

## Key QA Decisions
1. Enforced critical path contract as authoritative:
   - Spine: `.github/agents/golazo-copilot/orchestrator.md`
   - Roles: `.github/agents/golazo-copilot/roles/...`
2. Flagged design inconsistency where one section references `golazo-copilot.md`; QA treats this as non-authoritative and requires correction to `orchestrator.md`.
3. Required explicit negative/error validation with deterministic, human-readable expected failure messages per test case.
4. Required branch coverage for role-copy toggle (`include_roles=true|false`) and legacy-path non-write behavior.
5. Required telemetry validation for resolved output paths and error-category distinctions (path-resolution/write/copy).

## Assumptions Made
- MCP bootstrap interface and option contract remain unchanged except for output path/filename behavior in scope.
- Legacy files may exist from previous runs and should not be rewritten by the new contract path behavior.
- Cross-platform compatibility is required; tests should avoid OS-specific separator assumptions.

## Risks Raised
- Conflicting filename text in design can cause implementation drift if not corrected before/with coding.
- Legacy-path regressions may reappear if constants are duplicated instead of centralized.
- Weak error classification can reduce operability and root-cause triage quality.

## Handoff to Architect / Developer
- Centralize path constants/helpers for `.github/agents/golazo-copilot`, `orchestrator.md`, and `roles`.
- Implement tests from `GCP-0059-Test-Cases.md` with strict AC traceability and explicit failure messages.
- Update docs/help text in the same change set to prevent stale contract references.
- Preserve existing bootstrap option semantics while enforcing new output locations.
