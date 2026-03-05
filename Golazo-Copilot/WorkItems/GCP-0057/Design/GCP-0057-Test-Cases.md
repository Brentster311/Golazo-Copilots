# GCP-0057 Test Cases

## Mapping to Acceptance Criteria
- AC1: `orchestrator-only` mode deploys only orchestrator instructions.
- AC2: `force` semantics for overwrite/preserve.
- AC3: Workflow tools blocked when instructions missing with actionable remediation.
- AC4: Full/default bootstrap behavior remains compatible.
- AC5: Presence/absence paths covered by regression tests.

## Functional Tests

### TC-01 Orchestrator-only creates instructions file
- Precondition: `.github/copilot-instructions.md` absent.
- Action: `golazo_bootstrap(mode="orchestrator-only", force=false)`.
- Expected: `.github/copilot-instructions.md` created; roles and capabilities files unchanged.
- Failure message: "Expected orchestrator instructions file to be created in orchestrator-only mode."

### TC-02 Orchestrator-only preserves existing file by default
- Precondition: `.github/copilot-instructions.md` exists with sentinel text.
- Action: `golazo_bootstrap(mode="orchestrator-only", force=false)`.
- Expected: file content unchanged; result reports file as skipped.
- Failure message: "Expected existing instructions to be preserved when force=false."

### TC-03 Orchestrator-only overwrites with force
- Precondition: `.github/copilot-instructions.md` exists with stale content.
- Action: `golazo_bootstrap(mode="orchestrator-only", force=true)`.
- Expected: content replaced with packaged instructions; result reports file as created/updated.
- Failure message: "Expected instructions overwrite when force=true."

### TC-04 Full mode compatibility
- Precondition: clean workspace.
- Action: `golazo_bootstrap(mode="full")` and `golazo_bootstrap()`.
- Expected: existing full bootstrap outputs still created as before.
- Failure message: "Expected full bootstrap outputs to remain backward compatible."

### TC-05 Missing instructions blocks workflow tool
- Precondition: no `.github/copilot-instructions.md`.
- Action: call `golazo_create_workitem` (or another gated workflow tool).
- Expected: deterministic failure with remediation command using `mode="orchestrator-only"`.
- Failure message: "Expected missing-instructions preflight gate with actionable remediation."

### TC-06 Instructions present allows workflow tool
- Precondition: `.github/copilot-instructions.md` exists.
- Action: call previously blocked workflow tool.
- Expected: tool executes normal behavior.
- Failure message: "Expected workflow tool to run after instructions are present."

### TC-07 Version query remains accessible
- Precondition: missing instructions.
- Action: `golazo_status(work_item_id="")`.
- Expected: returns version, not blocked by preflight gate.
- Failure message: "Expected version-only status path to bypass workflow preflight."

### TC-08 Invalid mode rejected with clear error
- Precondition: none.
- Action: `golazo_bootstrap(mode="unknown")`.
- Expected: validation error naming supported modes.
- Failure message: "Expected invalid-mode error listing orchestrator-only/full."

## Regression Scope
- `test_gcp_bootstrap.py`
- `test_server_formatters.py` (if messages changed)
- `test_server.py` or equivalent dispatch tests for gated behavior

