<!-- Golazo Copilot Version: 2.100.8 -->
# Golazo Copilot v2

This workspace uses Golazo Copilot MCP server for workflow management.

## FORBIDDEN ACTIONS (NEVER DO THESE)

1. **NEVER edit `state.json` directly** - All state changes MUST go through `gcp_*` MCP tools. Editing state.json is a workflow violation that corrupts the work item.

2. **NEVER bypass gates** - If `gcp_transition` fails, FIX THE ISSUE (create the required outputs). Do not work around it.

3. **NEVER skip to Developer role** - You must complete all prior roles first.

4. **NEVER write production code without completing prior roles** - If you're not in developer role yet, you are in the wrong phase.

---

## REQUIRED: Before EVERY Response
1. Call `gcp_status(work_item_id="<current-id>")` to get current state
2. Display the Golazo Status header
3. Follow the role instructions returned
4. If no active work item, ask user which to start

---

## Starting a New Work Item
```
gcp_create_workitem(work_item_id="<id>", profile="complete")
```
Then create User Story at `WorkItems/<id>/<id>-User-Story.md`

---

## Role Transitions (Automatic Output Validation)

To move to next role:
```
gcp_transition(work_item_id="<id>", role="program-manager")
```

**How it works**: Each role file defines `## Required Outputs` that must exist before you can transition away from that role. The system automatically validates these outputs - no manual marking needed!

**Example**: The `project-owner-assistant` role requires:
- `file: WorkItems/{id}/{id}-User-Story.md`
- `file: WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md`

If these files don't exist, transition will fail with a clear error message listing what's missing.

**Valid roles in order:**
1. project-owner-assistant
2. program-manager
3. quality-assurance
4. architect
5. developer
6. refactor-expert
7. documentor
8. builder
9. retrospective

---

## File Naming Convention (ENFORCE)

| Artifact | Path |
|----------|------|
| User Story | `WorkItems/<id>/<id>-User-Story.md` |
| Design Doc | `WorkItems/<id>/Design/<id>-design-doc.md` |
| Review Comments | `WorkItems/<id>/Design/<id>-Review-Comments.md` |
| Test Cases | `WorkItems/<id>/Design/<id>-Test-Cases.md` |
| Refactoring Plan | `WorkItems/<id>/Design/<id>-Refactoring-Plan.md` |
| Retro Plan | `WorkItems/<id>/Design/<id>-Retro-Plan.md` |
| Role Notes | `WorkItems/<id>/RoleDecisionNotes/<id>-<role>.md` |

---

## Gate Enforcement
- **Output Validation Gate**: Cannot transition until all Required Outputs for the current role exist
- If `gcp_transition` fails, check the error message for the missing file path and create it
