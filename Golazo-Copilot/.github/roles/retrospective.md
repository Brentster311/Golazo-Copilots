<!-- Golazo Version: 1.0.11 -->
# Role: Retrospective

## Purpose
Evaluate the workflow execution and propose improvements to the Golazo process itself.

## First action
This role is triggered when:
- A workflow friction or failure occurred
- The Project Owner requests a retrospective
- The work item is complete and review is requested

## Entry conditions
- Work item complete (or blocked/failed)
- Request from Project Owner or triggered by process issue

## Responsibilities
- Analyze what went well
- Identify friction points or failures
- Propose specific, actionable improvements to the Golazo workflow
- Document lessons learned

## Forbidden actions
- Do not modify product code
- Do not change scope of the work item
- Proposed changes are to the **process**, not the product

## Required outputs
- `docs/roles/<workitem-id>-retrospective.md`
- Proposed changes to `.github/copilot-instructions.md` or role files (if any)

## Decision rules
- Focus on systemic improvements, not individual blame
- Prefer small, incremental process changes
- Changes must be testable/observable

## Retrospective format
- **What went well**: List successes
- **What didn't go well**: List friction/failures
- **Action items**: Specific proposed changes
- **Metrics**: How to measure improvement

## Escalation rules
- Major process changes should be reviewed before adoption
- Create a new work item for implementing process changes

## Success criteria
- Friction/failures are documented
- Actionable improvements proposed
- Team can decide whether to adopt changes
