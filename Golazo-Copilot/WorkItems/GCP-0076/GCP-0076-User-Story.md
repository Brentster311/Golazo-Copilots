# GCP-0076 User Story

**Status**: IMPLEMENTED

**User Story**
- Title: Unify and populate the capability registry
- As a: Golazo workflow contributor
- I want: every capability-registry producer and consumer to use one canonical workspace path with meaningful project entries
- So that: status, impact analysis, validation, and release review report the same current capability model
- Out of scope: Automatically inferring capabilities from arbitrary source code; combining independent nested-project registries; changing capability dependency semantics.
- Assumptions:
  - **Assumption (explicit):** The interface remains the existing MCP tools and generated YAML file, not a new UI.
  - **Assumption (explicit):** The target is cross-platform Python and path behavior must remain portable.
  - **Assumption (explicit):** `WorkItems/capabilities.yaml` is canonical, as established by GCP-0065.
  - **Assumption (explicit):** AgentLoop retains its independent `AgentLoop/WorkItems/capabilities.yaml`; test fixtures remain where tests require isolated workspaces.
- Acceptance Criteria (bulleted, testable):
  - Bootstrap, work-item creation, status, and capability operations consistently create or read `WorkItems/capabilities.yaml`, with root `capabilities.yaml` supported only as migration input.
  - When canonical and legacy root files coexist, canonical data wins and obsolete same-project legacy data is not reported as active.
  - The top-level canonical registry describes current Golazo workflow, capability-registry, bootstrap, and release-policy surfaces with valid key files and useful contracts.
  - Obsolete same-project registry files are removed while independent nested-project and required test-fixture registries remain intact.
  - Automated tests fail if path consumers diverge, canonical capability entries become invalid, or duplicate active registries are reintroduced.
- Non-functional requirements: Preserve existing MCP contracts; avoid data loss during migration; use structured YAML; keep all paths workspace-relative.
- Telemetry / metrics expected: Deterministic tests plus registry `list`, `impact`, and `validate` results; no external telemetry.
- Rollout / rollback notes: Ship as a patch release. Rollback restores prior path behavior and registry files; no runtime state migration beyond deterministic legacy-file movement.

## Closure

Delivered one canonical capability registry per workspace boundary, shared canonical/legacy resolution across all registry-aware tools, five meaningful Golazo capability cards, and scoped duplicate cleanup.

### Acceptance Criteria

- PASS: Bootstrap, work-item creation, status, and capability operations consistently resolve `WorkItems/capabilities.yaml`; legacy root data remains migration input.
- PASS: Canonical data wins on coexistence, mutating callers preserve legacy-only data, and status remains read-only.
- PASS: Five current Golazo capability cards have descriptions, contracts, dependencies, valid key files, and representative impact coverage.
- PASS: Obsolete top-level/package registries are removed while AgentLoop and canonical test-workspace registries remain.
- PASS: Focused and legacy regression tests protect path agreement, migration, population, impact, validation, and layout.

### Future Work

Consider a separate reliability work item for instrumentation-resistant timing assertions and Windows fixture cleanup retries. It is not required for this acceptance decision.

Final status: **IMPLEMENTED**.
