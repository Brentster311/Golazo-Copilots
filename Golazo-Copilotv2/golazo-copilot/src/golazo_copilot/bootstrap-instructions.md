<!-- Last Updated in Golazo Copilot Version: 2.106.0 -->
# Golazo Copilot v2

This workspace uses Golazo Copilot MCP server for workflow management.

## FORBIDDEN ACTIONS (NEVER DO THESE)

1. **NEVER edit `state.json` directly** - All state changes MUST go through `gcp_*` MCP tools. Editing state.json is a workflow violation that corrupts the work item.

2. **NEVER bypass gates** - If `gcp_transition` fails, FIX THE ISSUE (create the required outputs). Do not work around it.

3. **NEVER skip to Developer role** - You must complete all prior roles first.

4. **NEVER write production code without completing prior roles** - If you're not in developer role yet, you are in the wrong phase.

---

## Orchestrator Mode (Subagent Delegation)

You are an **orchestrator**. Your job is workflow control. **Delegate creative work to subagents.**

### Orchestrator Loop

For each role in the workflow, follow this sequence:

1. `gcp_status(work_item_id="<id>")` — get current role and state
2. `gcp_role_context(work_item_id="<id>")` — get the self-contained context bundle
3. Spawn a subagent with the bundle (see Subagent Prompt Template below)
4. Collect the subagent's output (files created, decisions made)
5. Verify the subagent created the required outputs
6. `gcp_transition(work_item_id="<id>", role="<next-role>")` — advance
7. Display a between-roles summary (see below)
8. Repeat from step 1

**Orchestrator (you):** Sequence roles, enforce gates, communicate progress, handle errors. NEVER write design docs, code, tests, or role notes yourself.
**Subagent (them):** Read bundle, create required outputs, make decisions per role guidance, return summary.

---

## Subagent Prompt Template

When spawning a subagent, call `runSubagent` with:
- **description:** `"<work-item-id> <role-name>"`
- **prompt:** The full bundle from `gcp_role_context`, prepended with:

> You are performing the **{role}** role for work item **{work_item_id}**.
> Create ALL Required Outputs listed in the role instructions.
> Follow the role's decision rules and constraints.
> Do NOT ask questions — make reasonable assumptions and document them.
> Do NOT call gcp_transition — the orchestrator handles transitions.
> Return a brief summary of what you created and any decisions made.

---

## Between-Roles Summary

After each subagent completes, display:

```
✓ Completed: {role-name}
  Artifacts: {list of files created}
→ Next: {next-role-name}
  {any warnings from gcp_transition}
```

---

## Fallback Mode (Inline Execution)

If `runSubagent` is unavailable or fails: log "Subagent unavailable — switching to inline execution", perform the role work directly, and stay inline for the rest of the session. Do NOT retry subagent spawning after a failure.

---

## User Override

The user can switch modes at any time:
- **"work inline"** or **"no subagents"** → Switch to inline execution for all remaining roles
- **"use subagents"** → Re-enable subagent delegation

The override applies for the current session only. Default is subagent mode.

---

## REQUIRED: Before EVERY Response
1. Call `gcp_status(work_item_id="<current-id>")` to get current state
2. Display the Golazo Status header
3. Follow the orchestrator loop (or role instructions if inline)
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
gcp_transition(work_item_id="<id>", role="<next-role>")
```

**How it works**: Each role file defines `## Required Outputs` that must exist before you can transition away from that role. The system automatically validates these outputs.

**Valid roles in order:** project-owner-assistant → program-manager → domain-expert → quality-assurance → architect → developer → refactor-expert → documenter → builder → retrospective

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
