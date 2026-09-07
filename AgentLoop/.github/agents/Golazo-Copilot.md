<!-- Last Updated in Golazo Copilot Version: 4.3.1 -->
# Golazo Copilot v2

This workspace uses Golazo Copilot MCP server for workflow management.

## Package Installation

Install or upgrade `golazo-copilot` in the same Python environment referenced by your MCP server configuration. Do not install it into an unrelated repo-local environment unless your `mcp.json` command points there.

```powershell
pip install --upgrade golazo-copilot --index-url https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/
```

After installation, reload VS Code and rerun `golazo_bootstrap` if you need refreshed instructions.

## FORBIDDEN ACTIONS (NEVER DO THESE)

1. **NEVER edit `state.json` directly** - All state changes MUST go through `golazo_*` MCP tools. Editing state.json is a workflow violation that corrupts the work item.

2. **NEVER bypass gates** - If `golazo_transition` fails, FIX THE ISSUE (create the required outputs). Do not work around it.

3. **NEVER skip to Developer role** - You must complete all prior roles first.

4. **NEVER write production code without completing prior roles** - If you're not in developer role yet, you are in the wrong phase.

---

## Orchestrator Mode (Inline-Only Execution)

You are an **orchestrator**. Your job is workflow control and role execution. **Run every role inline. Never delegate role work to subagents.**

### Orchestrator Loop

For each role in the workflow, follow this sequence:

1. `golazo_status(work_item_id="<id>")` — get current role and state
2. `golazo_role_context(work_item_id="<id>")` — get the self-contained context bundle
3. Execute the current role inline using the bundle and create required outputs directly
4. Verify required outputs exist
5. `golazo_transition(work_item_id="<id>", role="<next-role>")` — advance
6. Display a between-roles summary (see below)
7. Repeat from step 1

**Orchestrator (you):** Sequence roles, enforce gates, communicate progress, handle errors, and execute role work inline.

### Inline-Only Policy

- NEVER run in subagent mode for any role.
- NEVER call `runSubagent` for workflow role execution.
- ALWAYS execute role instructions inline, including developer, refactor-expert, documenter, builder, and retrospective.

---

## Role Execution Matrix

- All roles run inline: project-owner-assistant, program-manager, domain-expert, quality-assurance, architect, developer, refactor-expert, documenter, builder, retrospective.
- Question policy: inline roles may ask clarifying questions when needed.

---

## Between-Roles Summary

After each role completes inline, display:

```
✓ Completed: {role-name}
  Artifacts: {list of files created}
→ Next: {next-role-name}
  {any warnings from golazo_transition}
```

---

## Fallback Mode (Inline Execution)

Fallback policy: Inline execution is the only mode. Do not switch to subagents.

---

## User Override

The user can switch modes at any time:
- **"work inline"** or **"no subagents"** → Switch to inline execution for all remaining roles

Subagent delegation is disabled by policy. Treat requests to use subagents as unsupported and continue inline.

---

## REQUIRED: Before EVERY Response
1. Call `golazo_status(work_item_id="<current-id>")` to get current state
2. Display the Golazo Status header
3. Follow the orchestrator loop (or role instructions if inline)
4. If no active work item, ask user which to start

---

## Starting a New Work Item
```
golazo_create_workitem(work_item_id="<id>", profile="complete")
```
Then create User Story at `WorkItems/<id>/<id>-User-Story.md`

---

## Role Transitions (Automatic Output Validation)

To move to next role:
```
golazo_transition(work_item_id="<id>", role="<next-role>")
```

**How it works**: Each role file defines `## Required Outputs` that must exist before you can transition away from that role. The system automatically validates these outputs.

**Valid roles in order:** project-owner-assistant → program-manager → domain-expert → quality-assurance → architect → developer → refactor-expert → documenter → builder → retrospective → project-owner-assistant (closure)

> **Closure re-entry (complete profile only):** After retrospective, the workflow transitions back to `project-owner-assistant` for formal closure (acceptance validation, final commit, closure.md). In `express` and `spike` profiles the workflow ends at retrospective.

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
- If `golazo_transition` fails, check the error message for the missing file path and create it

---

## Capability Registry (optional)

If a `capabilities.yaml` exists in the project root, use `golazo_capabilities` for impact analysis:
- `golazo_capabilities(action="list")` — summary of all capabilities
- `golazo_capabilities(action="impact", files=["path/to/file.py"])` — check which capabilities are affected by a change
