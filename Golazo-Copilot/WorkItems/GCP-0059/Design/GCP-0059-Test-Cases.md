# GCP-0059 Test Cases

## Scope
Validate bootstrap output-path contract changes for centralized agent artifacts under `.github/agents/golazo-copilot`, including:
- Spine file creation/update at `.github/agents/golazo-copilot/orchestrator.md`
- Role copy destination at `.github/agents/golazo-copilot/roles/...`
- Legacy-path non-write behavior
- Option compatibility and docs/help text correctness

## Assumptions
- Bootstrap execution entrypoint remains MCP tool-based.
- Workspace root is the `workspace_path` provided to bootstrap.
- The path contract literals in the user story are authoritative if conflicting wording appears elsewhere.

## Acceptance Criteria Mapping
- **AC1**: Running bootstrap creates/updates spine at `.github/agents/golazo-copilot/orchestrator.md`.
  - Covered by: TC-01, TC-02
- **AC2**: Bootstrap no longer writes spine to legacy locations when new path is available.
  - Covered by: TC-03, TC-04
- **AC3**: With role copy enabled, roles are written under `.github/agents/golazo-copilot/roles/...`.
  - Covered by: TC-05, TC-06
- **AC4**: Existing bootstrap options still work; role copy toggle on/off works without errors.
  - Covered by: TC-07, TC-08
- **AC5**: Documentation/help text reflects new spine filename and roles folder structure.
  - Covered by: TC-09

## Functional Tests

### TC-01 New spine path is created on bootstrap
- Precondition: Fresh workspace with no `.github/agents/golazo-copilot/orchestrator.md`.
- Action: Run bootstrap with default settings.
- Expected outcome:
  - `.github/agents/golazo-copilot/orchestrator.md` exists after run.
  - Parent directories are created as needed.
- Expected failure message:
  - "Expected bootstrap to create spine file at .github/agents/golazo-copilot/orchestrator.md."

### TC-02 New spine path is updated idempotently on rerun
- Precondition: `orchestrator.md` exists from prior successful run.
- Action: Run bootstrap again with same options.
- Expected outcome:
  - Run succeeds.
  - `orchestrator.md` remains valid (no partial/corrupt write).
  - Behavior is deterministic across repeated runs.
- Expected failure message:
  - "Expected idempotent bootstrap rerun to preserve valid orchestrator.md without partial write artifacts."

### TC-03 Legacy spine path is not written when new path is available
- Precondition: Workspace where new path is writable.
- Action: Run bootstrap.
- Expected outcome:
  - No spine file is created/updated at legacy location(s).
  - Only new contract path is used for spine output.
- Expected failure message:
  - "Expected bootstrap to avoid legacy spine output locations when .github/agents/golazo-copilot/orchestrator.md is available."

### TC-04 Existing legacy spine artifact is not modified by new bootstrap run
- Precondition: Legacy spine file already exists with sentinel content; new path is writable.
- Action: Run bootstrap.
- Expected outcome:
  - Legacy file content remains unchanged.
  - New spine file is created/updated at contract path.
- Expected failure message:
  - "Expected bootstrap to leave legacy spine artifacts untouched while writing orchestrator.md at the new contract path."

### TC-05 Roles are copied to contract folder when include_roles=true
- Precondition: Bootstrap source roles available; no existing destination roles folder.
- Action: Run bootstrap with role copying enabled.
- Expected outcome:
  - `.github/agents/golazo-copilot/roles` is created.
  - Copied role files exist under that folder.
- Expected failure message:
  - "Expected copied role files under .github/agents/golazo-copilot/roles when include_roles is enabled."

### TC-06 Roles are not copied outside contract folder when include_roles=true
- Precondition: Workspace contains potential legacy/generic roles destinations.
- Action: Run bootstrap with role copying enabled.
- Expected outcome:
  - No copied roles are emitted to non-contract destinations (for example `.github/roles` or generic `.github/agents/<variable>/...`).
  - Contract folder contains copied roles.
- Expected failure message:
  - "Expected role copy output only under .github/agents/golazo-copilot/roles and no writes to legacy/generic role paths."

### TC-07 Role copy toggle OFF preserves no-copy behavior
- Precondition: Clean workspace, `include_roles=false`.
- Action: Run bootstrap.
- Expected outcome:
  - Bootstrap succeeds without role copy errors.
  - `.github/agents/golazo-copilot/roles` is not newly populated by this run.
- Expected failure message:
  - "Expected include_roles=false to skip copied role output while bootstrap still succeeds."

### TC-08 Existing bootstrap options remain backward compatible
- Precondition: Baseline scenarios for `mode=full`, `mode=orchestrator-only`, and `force` behavior.
- Action: Execute bootstrap with supported option combinations.
- Expected outcome:
  - Command/tool succeeds according to existing option semantics.
  - Path contract remains the new `.github/agents/golazo-copilot` structure.
- Expected failure message:
  - "Expected existing bootstrap options to remain compatible while honoring new orchestrator/roles output paths."

### TC-09 Docs/help text reflect exact path and filename contract
- Precondition: Latest docs/help text loaded from workspace.
- Action: Validate references in README/help output and instructions.
- Expected outcome:
  - References include `.github/agents/golazo-copilot/orchestrator.md` and `.github/agents/golazo-copilot/roles/...`.
  - No contradictory stale references to legacy paths or wrong filename.
- Expected failure message:
  - "Expected documentation/help text to match the new bootstrap output contract: orchestrator.md and /roles under .github/agents/golazo-copilot."

## Negative / Error Handling Tests

### TC-10 Permission denied on spine write returns actionable error
- Precondition: Destination directory exists but spine write is denied.
- Action: Run bootstrap requiring spine write.
- Expected outcome:
  - Bootstrap fails with actionable write error context.
  - No partial `orchestrator.md` is left behind.
- Expected failure message:
  - "Expected actionable spine write failure (permission denied) with no partial orchestrator.md artifact."

### TC-11 Invalid workspace path returns path-resolution error classification
- Precondition: `workspace_path` is invalid/unresolvable.
- Action: Run bootstrap.
- Expected outcome:
  - Failure is classified as path-resolution error (not generic unknown failure).
  - No filesystem side effects occur.
- Expected failure message:
  - "Expected bootstrap to classify invalid workspace_path as a path-resolution error with zero output artifacts."

### TC-12 Role copy failure is explicit and isolated
- Precondition: Spine destination writable, roles destination copy operation fails (simulated I/O failure).
- Action: Run bootstrap with `include_roles=true`.
- Expected outcome:
  - Error clearly indicates copy failure.
  - Failure telemetry/message is distinguishable from path-resolution/write failures.
  - No corrupt/partial role artifacts remain.
- Expected failure message:
  - "Expected explicit role copy failure classification and cleanup of partial copied role artifacts."

## Reliability / Non-Functional Tests

### TC-13 Cross-platform-safe path handling
- Precondition: Test environment runs path assertions via path-join utilities (not separator literals).
- Action: Execute bootstrap path assertions in CI/local on supported OS runners.
- Expected outcome:
  - Assertions pass independent of separator style/casing rules.
- Expected failure message:
  - "Expected bootstrap output path assertions to be cross-platform safe and independent of separator differences."

### TC-14 Repeated runs remain deterministic
- Precondition: Same workspace and options; run bootstrap N times.
- Action: Compare resulting artifact set and key file contents across runs.
- Expected outcome:
  - Artifact locations and key content are stable and deterministic.
- Expected failure message:
  - "Expected repeated bootstrap runs to produce deterministic artifact paths and stable content for unchanged inputs."

### TC-15 Observability emits required path and error categories
- Precondition: Logging/telemetry hooks enabled in test harness.
- Action: Run success and failure scenarios.
- Expected outcome:
  - Success logs include resolved spine path.
  - Role-copy-enabled runs include resolved roles folder.
  - Failures clearly differentiate path-resolution vs write vs copy categories.
- Expected failure message:
  - "Expected telemetry to emit resolved output paths and distinct error categories (path-resolution, write, copy)."

## Suggested Test Targets
- `golazo-copilot/tests/test_gcp_bootstrap.py`
- `golazo-copilot/tests/test_output_integration.py`
- `golazo-copilot/tests/test_gcp_status.py` (only if status/help text contracts are validated there)
