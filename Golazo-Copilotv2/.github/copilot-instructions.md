<!-- Last Updated in Golazo Copilot Version: 2.102.0 -->
# Golazo Copilot v2

This workspace uses Golazo Copilot MCP server for workflow management.

## FORBIDDEN ACTIONS (NEVER DO THESE)

1. **NEVER edit `state.json` directly** - All state changes MUST go through `gcp_*` MCP tools. Editing state.json is a workflow violation that corrupts the work item.

2. **NEVER bypass gates** - If `gcp_transition` fails, FIX THE ISSUE (create the required outputs). Do not work around it.

3. **NEVER skip to Developer role** - You must complete all prior roles first.

4. **NEVER write production code without completing prior roles** - If you're not in developer role yet, you are in the wrong phase.

---

## IMMEDIATE ACTION: Trigger Phrase Recognition (DO NOT SKIP)

When the user's message contains **ANY** of these triggers, **IMMEDIATELY** call `gcp_create_workitem` — do **NOT** ask for confirmation, do **NOT** treat it as a conversational request:

| Trigger | Action |
|---------|--------|
| **"new workitem"** or **"new work item"** | Call `gcp_create_workitem(work_item_id="<id>", profile="complete")` |
| **A work-item ID** matching pattern `[A-Za-z]{1,4}-\d{3,}` (e.g., `GCP-0045`, `CVT-002`) | Use the provided ID in `gcp_create_workitem` |
| **"complete mode"** | Call `gcp_create_workitem` with `profile="complete"` |

**Rules:**
1. If the user provides a work-item ID, use it **exactly**.
2. If no ID is provided, ask the user for the work-item ID.
3. If the work-item ID **already exists** (i.e., `WorkItems/<id>/` folder exists), call `gcp_status` instead of `gcp_create_workitem`.
4. These are **workflow commands**, not conversational requests. Act on the **FIRST** response.
5. After creating the work item, proceed immediately to the project-owner-assistant role.

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
3. domain-expert
4. quality-assurance
5. architect
6. developer
7. refactor-expert
8. documenter
9. builder
10. retrospective

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

---

## Capability Registry (optional)

If a `capabilities.yaml` exists in the project root, use `gcp_capabilities` for impact analysis:
- `gcp_capabilities(action="list")` — summary of all capabilities
- `gcp_capabilities(action="impact", files=["path/to/file.py"])` — check which capabilities are affected by a change
