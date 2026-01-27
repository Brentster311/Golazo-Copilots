# GCP-011: Artifact-First Entrance Criteria in Roles

**Status**: IMPLEMENTED

## User Story

- **Title**: Add entrance criteria validation to each role file
- **As a**: Developer using Golazo workflow
- **I want**: Each role to validate its required input artifacts exist before proceeding
- **So that**: Missing artifacts are caught early and work is sent back to the correct prior role

## Out of Scope

- Changing the spine document (changes go in role files only)
- Adding new roles
- Changing artifact paths or naming

## Assumptions

- **Assumption (explicit)**: Each role already has implicit entrance criteria; this makes them explicit
- **Assumption (explicit)**: Roles should fail-fast and redirect to prior role, not create missing artifacts themselves

## Acceptance Criteria (bulleted, testable)

- [ ] Each role file has explicit "Entry conditions" section
- [ ] Project Owner Assistant: None (first role)
- [ ] Program Manager requires: User Story
- [ ] Reviewer requires: User Story, Design Doc
- [ ] Architect requires: User Story, Design Doc
- [ ] Tester requires: User Story, Design Doc, Review Comments
- [ ] Developer requires: Full DoR (all 4 artifacts)
- [ ] Refactor Expert requires: Passing tests
- [ ] Builder requires: Tests exist
- [ ] Documentor requires: Build passes
- [ ] Retrospective: Work item complete or blocked
- [ ] VERSION updated to 1.1.4
- [ ] CHANGELOG updated with GCP-011 entry

## Rollout / Rollback Notes

- **Rollout**: Update all 10 role files in single commit
- **Rollback**: Revert commit
