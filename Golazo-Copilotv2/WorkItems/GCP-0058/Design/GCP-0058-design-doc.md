# GCP-0058 Design Document — Auto-Create Root `capabilities.yaml` on First `golazo_create_workitem`

## Summary
This change ensures `golazo_create_workitem` creates a root `capabilities.yaml` when it is missing during the first successful work item creation in a workspace. If the file already exists, behavior remains unchanged (no overwrite/mutation). The outcome is deterministic capability-registry availability for capability-aware tools without requiring a separate bootstrap step.

## Problem Statement
- New or unprepared workspaces may not include a root `capabilities.yaml`.
- Capability-aware tools expect a deterministic registry file and currently rely on manual/bootstrap preconditions.
- Missing registry setup introduces friction and increases first-run failure or confusion risk.

## Business Case
### Why now
- The issue directly affects first-run usability for new workspaces and increases support/debug overhead.

### Impact
- Improves day-0 reliability by guaranteeing baseline registry file presence at first create-workitem success.
- Reduces onboarding friction and removes a manual prerequisite for common workflows.

### KPIs
- Count of `golazo_create_workitem` calls that auto-create root `capabilities.yaml`.
- Count of `golazo_create_workitem` calls where root `capabilities.yaml` already existed.
- Count/rate of failures attributable to capability-registry initialization path.
- No regression in `golazo_create_workitem` success rate/latency.

## Stakeholders
- Primary: Golazo Copilot users creating first work items in a workspace.
- Secondary: Golazo maintainers, QA, and support teams.
- Downstream: capability-aware tool consumers that require registry presence.

## Requirements
### Functional Requirements
1. During `golazo_create_workitem`, detect whether root `capabilities.yaml` exists at workspace root.
2. If missing, create root `capabilities.yaml` in the same operation path as successful work item creation.
3. If present, do not overwrite or mutate file content.
4. Preserve normal successful response semantics regardless of whether file creation was needed.
5. Add automated tests for:
   - Missing-file branch (file is created).
   - Existing-file branch (file remains unchanged).
   - Overall create-workitem success in both branches.

### Non-Functional Requirements
1. Negligible runtime overhead for existence check and conditional create.
2. Deterministic behavior across supported platforms (Windows/Mac/Linux).
3. Backward compatibility for workspaces with pre-existing `capabilities.yaml`.
4. Race-safe behavior for normal single-invocation workflow usage.

## Proposed Approach
### High-Level Plan
1. Add create-if-missing guard in `golazo_create_workitem` flow after workspace path resolution and before/within final success path where filesystem scaffolding is performed.
2. Use an idempotent file initialization branch:
   - `if not exists(root/capabilities.yaml): create from default template`
   - `else: no-op`
3. Keep existing create-workitem output contract unchanged.
4. Add tests to validate missing/present paths and idempotency of existing file.
5. Include telemetry hooks/counters in existing logging/metrics path where available.

### Data and File Contract
- Target file: workspace-root `capabilities.yaml`.
- Creation trigger: first successful `golazo_create_workitem` in a workspace lacking the file.
- Existing file policy: immutable by this change (no mutation/no overwrite).

## Alternatives Considered
1. **Require manual bootstrap before create-workitem**
   - Rejected: keeps avoidable onboarding friction and fails the user-story objective.
2. **Auto-create in a different tool or global preflight path**
   - Rejected: expands scope beyond `golazo_create_workitem` and increases side-effect surface.
3. **Always rewrite/regenerate `capabilities.yaml`**
   - Rejected: violates explicit out-of-scope and backward-compatibility requirements.

## Risks, Mitigations, Open Questions
### Risks
1. Edge-case race condition if multiple create calls execute concurrently in same workspace.
2. Default template drift could create inconsistent initial registries across versions.
3. Misplaced initialization order could affect error handling/reporting consistency.

### Mitigations
1. Use atomic write/create-if-missing semantics where practical; preserve idempotent fallback.
2. Centralize default template source and verify expected baseline shape in tests.
3. Keep initialization in a single clear step in create-workitem flow with explicit tests for both branches.

### Open Questions
1. Should telemetry be surfaced only in internal logs, or also in user-facing diagnostics (if any)?
2. Do we need a dedicated integration test for simulated near-concurrent calls, or is single-invocation guarantee sufficient for this story?

## Dependencies
- Existing `golazo_create_workitem` tool implementation and workspace path resolution.
- Existing default `capabilities.yaml` template source (or bootstrap-equivalent template provider).
- Test harness for workspace-scoped file setup/assertions.

## Migration / Rollout / Rollback Plan
### Migration
- No data migration required.
- Existing workspaces with `capabilities.yaml` are unaffected.

### Rollout
- Release behind normal patch/minor process with targeted regression tests.
- Validate behavior in fresh workspace and existing-workspace scenarios.

### Rollback
- Remove create-if-missing branch from `golazo_create_workitem` and restore prior behavior.
- Keep tests updated to match reverted contract if rollback is required.

## Observability Plan
- Emit/track metric or structured log for branch outcome:
  - `capabilities_registry_autocreated=true|false`
- Track initialization failures and classify them separately from general create-workitem failures.
- Monitor create-workitem latency to confirm negligible overhead.

## Test Strategy Summary
1. Unit/integration test: missing root `capabilities.yaml` → created during successful `golazo_create_workitem`.
2. Unit/integration test: existing root `capabilities.yaml` → content unchanged after call.
3. Regression test: create-workitem success/response semantics unchanged across both branches.
4. Negative-path test: initialization failure surfaces clear failure classification without corrupting existing files.
