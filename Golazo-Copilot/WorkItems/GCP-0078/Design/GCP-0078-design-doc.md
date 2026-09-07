# GCP-0078 Design

## Summary

Revise `golazo-copilot/README.md` to match the current public MCP and workflow contracts. Add a focused source-text test module that anchors claims to the registered tools and profile definitions where practical.

## Documentation Changes

- Consolidate the duplicate persistence feature descriptions.
- Include Planner in the Complete profile while distinguishing profile membership from the Project Owner Assistant initial role.
- Remove the unsupported role-note bypass recipe; retain the valid consented output-gate bypass.
- Add `golazo_role_context` to discovery and reference sections.
- Require installation into the interpreter configured for MCP rather than a global environment.
- State that Git proposals are audit records, Git execution remains agent-driven, and no automatic work-item deletion or creation follows finalization.

## Validation

Add focused tests for the corrected README contract, run that module first, then run the complete test suite with coverage. Inspect the final diff for unrelated runtime or version changes.

## Risk

Low runtime risk because no product behavior changes. The primary risk is replacing one misleading simplification with another; tests should compare stable README claims with source constants and registry definitions where feasible.
