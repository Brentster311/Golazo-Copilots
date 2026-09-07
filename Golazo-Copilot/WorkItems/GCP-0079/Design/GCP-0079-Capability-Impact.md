# GCP-0079 Capability Impact

## Directly Affected

- **capability-registry-management:** Shared creation/bootstrap files are registered key files. Planner eligibility must be checked before `_ensure_capabilities_registry` so failed creation does not migrate or create a registry.
- **bootstrap-skill-installation:** Bootstrap instruction content changes, but skill-install behavior and contracts are unchanged.
- **project-finalization:** Shared server and README surfaces change, but finalization behavior and closure gates are unchanged.
- **release-policy-guidance:** README and later release metadata will describe the additive creation contract; ownership order is unchanged.

## Transitively Affected

No downstream capability dependencies were reported by the registry.

## Contract Implications

- Add optional `initial_role` to `golazo_create_workitem` with enum values `project-owner-assistant` and `planner`.
- Preserve `project-owner-assistant` as the default.
- Add deterministic validation for Planner profile and first-item eligibility.
- Preserve the state schema; only initial field values differ when explicitly requested.

## Registry Recommendation

Update the workflow-orchestration capability contract and key files if the final registry card does not already cover work-item creation and orchestrator startup behavior. Other cards need no contract changes.
