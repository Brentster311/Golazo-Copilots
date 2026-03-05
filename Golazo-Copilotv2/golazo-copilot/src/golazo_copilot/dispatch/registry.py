"""MCP tool registration definitions."""

from mcp.types import Tool

REQUIRED_TOOL_NAMES: set[str] = set()
WORKFLOW_TOOLS_REQUIRING_INSTRUCTIONS: set[str] = {
    "golazo_create_workitem",
    "golazo_transition",
    "golazo_status",
    "golazo_consent",
    "golazo_role_context",
    "golazo_git_propose",
    "golazo_transition_workitem",
}


def get_tool_definitions() -> list[Tool]:
    """Build tool definitions advertised by this MCP server."""
    return [
        Tool(
            name="golazo_create_workitem",
            description="Create a new Golazo Copilot work item with persistent state tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Unique identifier for the work item. Format: 1-4 letters, dash, 3+ digits (e.g., GCP-0001, AB-001, TEST-1234)"
                    },
                    "profile": {
                        "type": "string",
                        "enum": ["complete", "express", "spike"],
                        "default": "complete",
                        "description": "Workflow profile determining which gates are enforced"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (required)"
                    }
                },
                "required": ["work_item_id", "workspace_path"]
            }
        ),
        Tool(
            name="golazo_transition",
            description="Transition to a new role in the Golazo Copilot workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item identifier"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["project-owner-assistant", "program-manager", "domain-expert", "quality-assurance",
                                 "architect", "developer", "refactor-expert", "builder", "documenter", "retrospective"],
                        "description": "Target role to transition to"
                    },
                    "force": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force transition even if gates not met (requires prior consent)"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (required)"
                    }
                },
                "required": ["work_item_id", "role", "workspace_path"]
            }
        ),
        Tool(
            name="golazo_status",
            description="Get comprehensive workflow status for a work item. Returns current role, phase, required outputs, next steps, deviations, and the Golazo Copilot version number. Use this to check the installed Golazo version.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item identifier. If omitted or empty, only the version is returned."
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (required)"
                    }
                },
                "required": ["workspace_path"]
            }
        ),
        Tool(
            name="golazo_bootstrap",
            description="Bootstrap Golazo Copilot in a workspace - creates copilot instructions and directories",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["full", "orchestrator-only"],
                        "default": "full",
                        "description": "Bootstrap mode: full scaffolding or orchestrator-instructions only"
                    },
                    "force": {
                        "type": "boolean",
                        "default": False,
                        "description": "Overwrite existing files if they exist"
                    },
                    "include_roles": {
                        "type": "boolean",
                        "default": True,
                        "description": "Also copy default role files to .github/agents/golazo-copilot/roles/"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path (required)"
                    }
                },
                "required": ["workspace_path"]
            }
        ),
        Tool(
            name="golazo_consent",
            description="Record Project Owner consent for bypassing workflow gates. The rationale MUST be provided by the Project Owner (human), not generated by the assistant. Required before using force=True.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item identifier"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["skip_outputs", "skip_role", "revert_progress", "custom"],
                        "description": "Type of deviation being consented to"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Justification for the deviation (min 10 characters)"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (required)"
                    }
                },
                "required": ["work_item_id", "action", "reason", "workspace_path"]
            }
        ),
        Tool(
            name="golazo_capabilities",
            description="Query the project capability registry for impact analysis. Reads capabilities.yaml to show features, dependencies, and which capabilities are affected by file changes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "show", "impact", "validate"],
                        "description": "Action to perform: list (summary), show (full card), impact (affected by files), validate (check key_files exist)"
                    },
                    "capability": {
                        "type": "string",
                        "description": "Capability name (required for action='show')"
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File paths to check impact for (required for action='impact')"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing capabilities.yaml (required)"
                    }
                },
                "required": ["action", "workspace_path"]
            }
        ),
        Tool(
            name="golazo_role_context",
            description="Assemble a self-contained context bundle for a specific role in a work item. Returns role instructions, current state, input artifacts (file contents), and previous role notes — everything a subagent needs to perform the role.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item identifier (e.g. GCP-0049)"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role name to bundle context for. If omitted, uses current_role from state.json."
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (required)"
                    }
                },
                "required": ["work_item_id", "workspace_path"]
            }
        ),
        Tool(
            name="golazo_git_propose",
            description="Record proposal-only git action intent in a work item's append-only audit history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item identifier"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["add", "commit", "push", "branch"],
                        "description": "Git intent action to propose"
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File paths for action='add'"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message for action='commit'"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name for action='push' or action='branch'"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (required)"
                    }
                },
                "required": ["work_item_id", "action", "workspace_path"]
            }
        ),
        Tool(
            name="golazo_transition_workitem",
            description="Mark a retrospective-complete work item as completed and set the next sequential work item in global project state.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Completed work item identifier (must currently be at role 'retrospective')"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (required)"
                    }
                },
                "required": ["work_item_id", "workspace_path"]
            }
        ),
    ]
