# GCP-0079 Project Owner Assistant Notes

## Product Decision

The Project Owner selected an explicit offer before first-work-item creation. Accepting starts the first Complete-profile work item directly in Planner; declining or omitting the choice starts POA exactly as today.

## Boundaries

- The MCP tool validates eligibility; orchestration instructions present the choice.
- "Brand-new project" means no existing work-item `state.json` files.
- Planner remains unavailable to Express and Spike.
- Existing callers require no changes.

## Capability Impact

Initial impact analysis identified workflow-adjacent capability cards, but exact registry updates will be determined from the final changed-file set. No capability behavior is intentionally removed.