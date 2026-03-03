# GCP-0059 Architect Role Decision Notes

## Role Outcome
Architect review completed for bootstrap output-path contract change.

## Decisions Made
1. **Authoritative output contract confirmed**
   - Spine file: `.github/agents/golazo-copilot/orchestrator.md`
   - Copied roles: `.github/agents/golazo-copilot/roles/...`

2. **Stale reference policy**
   - Any reference to `golazo-copilot.md` is invalid for this story and must be corrected to `orchestrator.md`.
   - Any reference to `.github/roles/...` as the bootstrap copy destination is invalid for this story and must be corrected to `.github/agents/golazo-copilot/roles/...`.

3. **Scope guard**
   - This role constrains changes to bootstrap output path/name and associated contract surfaces only.
   - No production behavior expansion, no role-semantics updates, and no unrelated code changes are approved in this scope.

## Capability Impact Summary
- Directly affected: `tool-bootstrap`, `mcp-server`
- Transitively affected: `tool-golazo-update`
- Full analysis recorded in `WorkItems/GCP-0059/Design/GCP-0059-Capability-Impact.md`

## Assumptions (Documented)
1. Root `capabilities.yaml` remains authoritative for this work item’s impact analysis.
2. Existing bootstrap MCP interface (`workspace_path`, `force`, `include_roles`) remains unchanged.
3. Cross-platform path handling remains required, with Windows-active validation context.

## Security/Resilience Assessment
- No new entry points introduced.
- Primary failure modes remain filesystem write/copy and path resolution errors.
- Deterministic error taxonomy and no-partial-write behavior remain mandatory non-functional constraints.

## Handoff Constraints for Developer
1. Centralize and reuse canonical path constants.
2. Update tests/docs/tool text in lockstep to prevent contract drift.
3. Add/maintain negative assertions for legacy path non-creation when new path is valid.

## Escalation Check
No new user story required. Change remains within approved bootstrap output-path scope.