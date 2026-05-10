# TIM-0004 — Retrospective Notes

## What Went Well

- **Clear scope from the start**: The User Story was well-formed and unambiguous. Section order, WHY/HOW/WHAT framing, and tone requirements were all explicit. No mid-workflow clarifications needed.
- **Source material readily available**: All six `.docx` files were already in the workspace and extractable immediately. The workflow moved without dependency blockers.
- **QA caught an ordering inconsistency early**: The Design Doc proposed a different section order than the User Story. QA flagged it before implementation, so the developer used the correct order without rework.
- **Document-artifact profile fits cleanly**: The complete workflow profile worked well for a document work item. Most roles completed quickly because the scope was bounded and testable.

## What Didn't Go Well

- **Docx extraction redundancy**: The context showed that two files had been extracted in a prior terminal session (to paths that no longer existed by the time this session ran). Re-extraction was needed. A small friction; resolved quickly.
- **Design Doc section order conflicted with User Story**: The PM role ordered sections differently than the User Story specified. Could be avoided if PM explicitly cross-checks section order against the User Story before finalizing the design doc.

## Action Items

1. **PM Role**: When the deliverable is a structured document with an explicit section order in the User Story, the PM should explicitly list and confirm the section order in the design doc rather than re-deriving it.
2. **Developer Role**: Note in the decision template that for document artifacts, the "tests pass" pre-condition should be interpreted as "acceptance criteria verified manually against the source documents."

## Metrics

- 0 mid-workflow scope changes
- 0 returns to prior roles
- 8/8 test cases passed
- 15 files committed in one clean commit

## Capability Registry

`golazo_capabilities` was consulted during the architect role. Impact analysis confirmed zero capabilities affected. No missed opportunities.

## Lessons Learned

For document-artifact work items, the workflow is efficient and appropriate. The test cases format (TC-01 through TC-08) proved useful as a shared audit trail across developer, builder, and closure roles.
