# GCP-003: Enforce TDD and Builder Git Operations

**Status**: IMPLEMENTED

## User Story

- **Title**: Enforce TDD Order and Builder Git Operations in Golazo Workflow
- **As a**: Developer using the Golazo workflow
- **I want**: The process to enforce test-first development and automate git operations
- **So that**: Tests are always written before production code, and git branching/committing is handled consistently by the Builder role

## Out of Scope
- CI/CD pipeline setup
- PR automation
- Git hooks implementation
- Changes to artifact structure

## Assumptions
- **Assumption (explicit)**: Git is available in the environment
- **Assumption (explicit)**: Branch naming convention is `<workitem-id>` (e.g., `GCP-003`)
- **Assumption (explicit)**: Commit message format is `<workitem-id>: <User Story title>`

## Acceptance Criteria (bulleted, testable)
- [x] Developer role file requires test code before production code
- [x] Developer role file forbids writing production code before tests
- [x] Builder role file includes branch creation responsibility
- [x] Builder role file includes commit/push responsibility  
- [x] Spine DoD checklist includes "Feature branch created"
- [x] Spine DoD checklist includes "Test code written before production code"
- [x] Spine state machine documents Builder's git responsibilities

## Non-functional Requirements
- Changes must be backward compatible with existing work items
- Documentation must be clear and unambiguous

## Telemetry / Metrics Expected
- None (process documentation only)

## Rollout / Rollback Notes
- Rollout: Merge to main; new work items follow updated process
- Rollback: Revert commit; previous process resumes
