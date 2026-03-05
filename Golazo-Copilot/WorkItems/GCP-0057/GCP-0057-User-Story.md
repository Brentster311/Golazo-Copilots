**Status**: IMPLEMENTED

**User Story**
**User Story**
- Title: Require orchestrator-instructions bootstrap with an `orchestrator-only` option
- As a: GitHub Copilot user with Golazo MCP installed
- I want: a required bootstrap step that can deploy only the orchestrator instructions file (`.github/copilot-instructions.md`)
- So that: workflow guidance is deterministic from first use without repeatedly injecting fallback text
- Out of scope:
  - Rewriting role semantics or required-output rules
  - Auto-bootstrapping on unrelated tool calls
  - Changing role semantics or required-output rules
  - Adding new MCP tools
- Assumptions:
  - Assumption (explicit): bootstrap policy can be changed from optional to required for workflow tool usage
  - Assumption (explicit): `golazo_bootstrap` can be extended with a mode selector without breaking compatibility
- Acceptance Criteria (bulleted, testable):
  - `golazo_bootstrap` supports `mode="orchestrator-only"` and creates/updates only `.github/copilot-instructions.md`.
  - `golazo_bootstrap` keeps `force` behavior: with `force=true`, orchestrator instructions are overwritten; with `force=false`, existing instructions are preserved.
  - Workflow tools fail fast when orchestrator instructions are missing and return a clear remediation command using `golazo_bootstrap(..., mode="orchestrator-only")`.
  - Existing `mode="full"` (or default bootstrap behavior) remains backward compatible.
  - Regression tests cover both “orchestrator instructions present” and “orchestrator instructions absent” scenarios.
  - Documentation states bootstrap is required before workflow operations and explains `orchestrator-only` vs full bootstrap.
- Non-functional requirements:
  - Minimal latency impact for preflight orchestrator-instructions checks.
  - Backward compatibility with existing work items.
- Telemetry / metrics expected:
  - Count of blocked workflow calls due to missing orchestrator instructions.
  - Count of `orchestrator-only` bootstrap executions.
  - Count of forced orchestrator-instructions overwrites (`force=true`).
- Rollout / rollback notes:
  - Rollout as a patch/minor version update.
  - Rollback by restoring optional-bootstrap behavior and removing hard preflight gate.

## Closure

### Summary of delivery
- Implemented `golazo_bootstrap(mode="orchestrator-only")` for minimal instructions deployment.
- Added required preflight in server workflow dispatch when orchestrator instructions are missing.
- Preserved default/full bootstrap behavior for backward compatibility.
- Updated README and added regression tests for mode, gating, and diagnostics bypass behavior.

### Acceptance Criteria Validation
- AC1 (`orchestrator-only` mode deploys only instructions): **PASS**
- AC2 (`force` overwrite semantics): **PASS**
- AC3 (workflow tools fail fast with remediation when missing instructions): **PASS**
- AC4 (full/default mode remains compatible): **PASS**
- AC5 (present/absent paths covered by regression tests): **PASS**
- AC6 (documentation updated for required bootstrap + mode options): **PASS**

### Pending / Follow-up Work Items
- Candidate follow-up: split `server.py` into smaller modules to reduce maintenance risk (identified during refactor audit).

### Final status confirmation
- Work item `GCP-0057` is implemented and validated with targeted automated tests.

