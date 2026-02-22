# GCP-0046 — Project Owner Assistant Decision Notes

## Work Item
GCP-0046: Add Domain Expert Role to the Definition Phase

## Decisions Made

### Scope
- Single role addition (`domain-expert`) inserted between program-manager and quality-assurance
- The role evaluates domain expertise needs and writes guidance to the shared Review Comments artifact
- No new artifact type; domain experts contribute to the existing `{id}-Review-Comments.md`

### Key Design Choices
1. **Role name:** `domain-expert` — follows the kebab-case convention of all other roles
2. **Position:** After program-manager, before quality-assurance — the PM analyzes the problem first, then domain experts provide specialized input before QA reviews everything
3. **Phase:** Definition — domain expertise informs the design, not the implementation
4. **Artifact strategy:** Domain experts write to Review Comments because they provide *input to the design review*, not a separate deliverable. This keeps the artifact model simple and ensures QA/Architect see domain guidance in context.
5. **Required output:** Only the role decision notes (`{id}-domain-expert.md`) — the Review Comments file is a shared artifact, not owned solely by this role

### What Was Not Assumed (would require user input if unclear)
- The user's request was explicit about placement (after PM, before reviewer/QA)
- The user's request was explicit about the trigger categories and consultation rules
- The user's request was explicit that domain experts write to Review Comments

### Risks
- Existing work items in progress will have state.json referencing the old role sequence — backward compatibility is maintained because backward transitions are always allowed and the transition logic uses index comparison
- Test count will increase; all existing transition tests must be updated for the new index positions
