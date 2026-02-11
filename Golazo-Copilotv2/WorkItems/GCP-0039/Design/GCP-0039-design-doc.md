# Design Doc — GCP-0039: Role Instructions — Reference Capability Registry

## Summary
Add a conditional "Capability Registry" section to 5 role files (QA, Architect, Developer, Refactor Expert, Retrospective) instructing the assistant to call `gcp_capabilities(action="impact")` when relevant.

## Problem Statement
The `gcp_capabilities` tool exists but no role instructions mention it. The assistant won't proactively use it unless told to.

## Proposed Approach
Add a new section to each role file's Responsibilities, conditional on `capabilities.yaml` existing:

### Insertion Pattern (same for all 5 roles)
Insert between the last Responsibilities bullet and `## Forbidden actions`:

```markdown
### Capability Registry (if capabilities.yaml exists)
- If a `capabilities.yaml` exists in the project root, run `gcp_capabilities(action="impact", files=[...])` on [context-specific files]
- [Role-specific instruction]
```

### Per-Role Instructions

| Role | Files to Check | Action |
|------|---------------|--------|
| QA | Files referenced in design doc | Flag affected capabilities not covered by test cases |
| Architect | Files in design doc | Verify contract compatibility across affected capabilities |
| Developer | Files being changed | Check no downstream capabilities are broken before committing |
| Refactor Expert | Refactored files | Verify no transitive dependents are affected |
| Retrospective | N/A (presence check) | Check if capabilities.yaml was consulted during the work item |

## Files Changed
5 source role files in `roles/defaults/`:
- `quality-assurance.md`
- `architect.md`
- `developer.md`
- `refactor-expert.md`
- `retrospective.md`

Plus their deployed copies in `.github/roles/` (via bootstrap).

## Test Strategy
- Verify each source role file contains the new section
- Verify conditional phrasing ("If `capabilities.yaml` exists")
- Existing role-loading tests continue to pass

## Risks
- **Low**: Adding text to role files has no code risk. Bootstrap propagates changes.
