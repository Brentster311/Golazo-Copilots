# GCP-0059 Design Document — Required Orchestrator-Instructions Bootstrap

## Summary
Golazo currently depends on workspace bootstrap to deploy `.github/copilot-instructions.md` (the orchestrator instructions). This design makes orchestrator-instructions deployment an explicit prerequisite and adds an `orchestrator-only` bootstrap mode so users can satisfy the prerequisite with minimal workspace changes.

## Problem Statement
- Current optional-bootstrap behavior allows workflow tools to run with missing orchestrator instructions.
- Runtime fallback messaging can consume unnecessary tokens over time.
- Missing deterministic preflight causes inconsistent user experience and support burden.

## Business Case
### Why now
- The flaw is newly identified and affects all new users who install without bootstrapping.

### Impact
- Ensures deterministic workflow behavior from first workflow call.
- Reduces token overhead by removing repeated fallback guidance paths.

### KPIs
- % of workflow calls blocked due to missing orchestrator instructions (expected to trend down).
- % of bootstrap runs using `orchestrator-only` mode.
- No increase in failures/regressions for already-bootstrapped sessions.

## Stakeholders
- Primary: Golazo MCP users (install-only and bootstrapped).
- Secondary: Golazo maintainers and role authors.
- Operational: Support/engineering triage for onboarding issues.

## Requirements
### Functional
1. Detect whether deployed orchestrator instructions file exists at workspace root (`.github/copilot-instructions.md`).
2. Extend `golazo_bootstrap` with mode selection:
   - `mode="orchestrator-only"` → manage only `.github/copilot-instructions.md`
   - default/full mode → existing behavior (roles/capabilities/workitems scaffolding)
3. Keep `force` overwrite semantics in both modes.
4. Enforce preflight gate in workflow tools: if orchestrator instructions are missing, fail with actionable remediation command.
5. Keep existing bootstrap behavior backward compatible for callers not specifying mode.

### Non-functional
1. Minimal added latency from orchestrator-instructions preflight check.
2. Deterministic workspace resolution (no dependence on process cwd).
3. High test coverage for `orchestrator-only`, full mode, and missing-instructions gate paths.

## Proposed Approach
### High-level
1. Add `mode` parameter to `golazo_bootstrap` (enum: `orchestrator-only`, `full`; default `full` for compatibility).
2. Refactor bootstrap implementation to perform mode-scoped file actions and preserve existing output reporting.
3. Add shared orchestrator-instructions preflight check utility for workflow tools.
4. In workflow dispatch/tool handlers, enforce gate:
    - if missing instructions, return clear failure plus command example:
       `golazo_bootstrap(workspace_path="<path>", mode="orchestrator-only")`
   - mention `force=true` when replacement is needed.
5. Add regression tests for bootstrap modes, force behavior, and gate enforcement.

### Scope of code touch
- `src/golazo_copilot/tools/golazo_bootstrap.py`
- `src/golazo_copilot/server.py` (tool schema + preflight gate + messaging)
- `tests/test_server_formatters.py`
- `tests/test_gcp_bootstrap.py`
- `tests/test_server.py` and/or integration tests covering missing-instructions blocks

## Alternatives Considered
1. **Force bootstrap before any work item actions**
   - Selected with scope control via `orchestrator-only` mode.
2. **Do nothing; rely on docs**
   - Rejected: known defect remains and onboarding reliability stays poor.
3. **Auto-write `.github/copilot-instructions.md` implicitly on first tool call**
   - Rejected: surprising side effect and unapproved filesystem mutation.

## Risks
1. Breaking users relying on optional-bootstrap behavior.
2. Over-blocking tools if preflight applies too broadly (including non-workflow utilities).
3. Incorrect mode handling causing unexpected file writes.

## Mitigations
1. Restrict required-instructions gate to workflow tools only; keep bootstrap/status-version checks accessible.
2. Provide precise remediation command in every block response.
3. Add explicit tests for mode boundaries and `force` overwrite semantics.

## Open Questions
1. Should `golazo_status` with empty work item (version check) bypass instructions preflight?
2. Should `golazo_bootstrap(mode="orchestrator-only")` also validate/create `.github` folder only, with no other side effects?
3. Do we need a temporary compatibility window before making bootstrap required?

## Dependencies
- Existing package resource: `bootstrap-instructions.md`.
- Existing bootstrap tool and server dispatch contracts.

## Migration / Rollout / Rollback
### Migration
- No data migration required.

### Rollout
- Ship as patch release with regression tests.

### Rollback
- Revert hard preflight gate and return to optional bootstrap semantics.

## Observability Plan
- Log blocked workflow invocations due to missing orchestrator instructions.
- Track `orchestrator-only` bootstrap usage and force-overwrite rate.
- Track bootstrap failures by mode.

## Test Strategy Summary
1. Unit tests: `golazo_bootstrap(mode="orchestrator-only")` creates/updates only orchestrator instructions.
2. Unit tests: `force=false` preserves existing instructions; `force=true` overwrites them.
3. Integration tests: workflow tools are blocked when orchestrator instructions are missing and return remediation command.
4. Integration tests: once orchestrator instructions exist, workflow tools proceed normally.
5. Regression: full bootstrap mode remains backward compatible.
