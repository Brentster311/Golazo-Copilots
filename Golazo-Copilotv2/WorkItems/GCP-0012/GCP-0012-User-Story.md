# GCP-0012: Allow Backward Role Transitions

**Status**: BACKLOG

## User Story

- **Title**: Allow Backward Role Transitions in Workflow
- **As a**: developer using Golazo Copilot
- **I want to**: transition backward to previous roles in the workflow
- **So that**: I can rework earlier artifacts when issues are discovered in later roles without being blocked

## Out of scope
- Changing forward transition rules (no role skipping remains enforced)
- Automatic rollback of artifacts
- Warnings about going backward (future enhancement)
- Tracking reason for backward transitions

## Assumptions
- **Assumption (explicit)**: Backward transitions preserve all progress (DoR/DoD items remain marked). This is acceptable because the user may be going back to refine, not redo.
- **Assumption (explicit)**: Any role can transition to any earlier role in the sequence. Rationale: If you can go forward sequentially, you should be able to return to any prior step.
- **Assumption (explicit)**: The role sequence order is: project-owner-assistant ? program-manager ? quality-assurance ? architect ? developer ? refactor-expert ? builder ? documentor ? retrospective

## Acceptance Criteria

1. **AC1: Backward transitions are allowed**
   - Given I am in role `retrospective`
   - When I call `gcp_transition(role="developer")`
   - Then the transition succeeds
   - And current_role becomes `developer`
   - And all DoR/DoD progress is preserved

2. **AC2: Forward transitions still cannot skip roles**
   - Given I am in role `program-manager`
   - When I call `gcp_transition(role="architect")` (skipping quality-assurance)
   - Then the transition fails
   - And error message indicates invalid transition

3. **AC3: Backward transition to any prior role**
   - Given I am in role `builder`
   - When I transition to `program-manager` (skipping 5 roles backward)
   - Then the transition succeeds
   - And I can re-enter the workflow from that point

4. **AC4: Role history tracks backward transitions**
   - Given I transition backward from `developer` to `architect`
   - When I check `role_history` in state
   - Then a new entry shows entering `architect` with timestamp
   - And the previous `developer` entry shows exit timestamp

## Non-functional requirements
- Backward transitions complete in <100ms
- State file remains valid after backward transition
- All existing tests continue to pass

## Telemetry / metrics expected
- Count of backward transitions per work item
- Most common backward transition patterns (e.g., developer?architect)

## Rollout / rollback notes
- **Breaking change**: No - extends existing behavior
- **Rollback**: Revert to previous version if backward transitions cause state corruption
- **Migration**: None - existing state files compatible
