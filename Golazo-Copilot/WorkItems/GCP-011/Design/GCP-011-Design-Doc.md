# GCP-011: Design Document

## Summary
Update all 10 role files to include explicit entrance criteria checks. Each role validates required artifacts exist before proceeding, and redirects to prior role if missing.

## Problem Statement
Currently, entrance criteria are implied but not explicitly checked in role files. This leads to:
- Roles proceeding without required inputs
- Confusion about which role should produce missing artifacts
- Work being done in wrong order

## Business Case

### Why Now
- Observed during GCP-008/009/010 that roles sometimes start without proper inputs
- Explicit checks will catch issues earlier
- Low implementation cost (documentation only)

### Impact
- **Positive**: Fail-fast when artifacts missing
- **Positive**: Clear redirect path to prior role
- **Positive**: Self-documenting role dependencies

## Functional Requirements

### Role Entrance Criteria Matrix

| Role | Required Artifacts | If Missing, Redirect To |
|------|-------------------|------------------------|
| Project Owner Assistant | None | N/A (first role) |
| Program Manager | User Story | Project Owner Assistant |
| Reviewer | User Story, Design Doc | Program Manager |
| Architect | User Story, Design Doc | Program Manager |
| Tester | User Story, Design Doc, Review Comments | Reviewer/Architect |
| Developer | Full DoR (4 artifacts) | Tester |
| Refactor Expert | Tests passing | Developer |
| Builder | Tests exist | Tester |
| Documentor | Build passes | Builder |
| Retrospective | Work item complete/blocked | N/A |

### Required Changes Per Role File

Each role file must have:
1. "Entry conditions" section listing required artifacts
2. "First action" updated to verify entry conditions
3. Clear redirect instruction if conditions not met

## Proposed Implementation

### Template for Entry Conditions Section

```markdown
## Entry conditions
- [List required artifacts]

If missing, stop and return to **[Prior Role]**.
```

### Example: Program Manager

```markdown
## Entry conditions
- User Story exists at `WorkItems/<workitem-id>/<workitem-id>-User-Story.md`

## First action
Confirm the User Story exists. If missing, stop and return to **Project Owner Assistant**.
```

## Test Strategy
1. Verify each role file has "Entry conditions" section
2. Verify each role specifies correct required artifacts
3. Verify redirect instructions are present and correct
