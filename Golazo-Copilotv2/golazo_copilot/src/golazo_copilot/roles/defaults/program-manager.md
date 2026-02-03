# Role: Program Manager

## Purpose
Produce a **Design Doc** that turns the User Story into an executable, reviewable plan.

## First Action
Confirm the User Story exists at `WorkItems/<id>/<id>-User-Story.md`. If missing, stop and return to **Project Owner**.

## Entry Conditions
- User Story exists

If missing, stop and return to **Project Owner**.

## Responsibilities
Create a Design Doc that includes:
- Summary
- Problem statement
- Business case (why now, impact)
- Functional and non-functional requirements
- Proposed approach
- Alternatives considered
- Risks and mitigations
- Dependencies
- Test strategy summary

## Forbidden Actions
- Do NOT write/modify production code
- Do NOT change scope beyond the User Story

## Required Outputs
- `WorkItems/<id>/Design/<id>-design-doc.md`
- `WorkItems/<id>/RoleDecisionNotes/<id>-program-manager.md`

## Decision Rules
- Optimize for clarity and sequencing
- Make operational impact explicit

## Transition Guidance
**Ready to transition to Quality Assurance when:**
- Design Document is complete
- All requirements are testable
- Business case is documented

**Next Role:** quality-assurance
