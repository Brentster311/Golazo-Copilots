# -*- coding: utf-8 -*-
"""Golazo Copilot MCP Server - Entry point for GitHub Copilot integration."""

import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from . import __version__
from .tools.gcp_create_workitem import gcp_create_workitem
from .tools.gcp_transition import gcp_transition
from .tools.gcp_status import gcp_status
from .tools.gcp_bootstrap import gcp_bootstrap
from .tools.gcp_consent import gcp_consent

# Create server instance with version in name
server = Server(f"golazo-copilot v{__version__}")

# Status icons (using ASCII to avoid encoding issues)
ICON_OK = "[OK]"
ICON_FAIL = "[FAIL]"
ICON_WARN = "[WARN]"
ICON_PENDING = "[...]"
ICON_CHECK = "[x]"
ICON_EMPTY = "[ ]"


def resolve_work_items_dir(workspace_path: str | None) -> Path:
    """
    Resolve workspace_path to an absolute work_items_dir Path.
    
    Args:
        workspace_path: Optional workspace root path (string or None)
        
    Returns:
        Absolute Path to the WorkItems directory
    """
    if workspace_path:
        base = Path(workspace_path)
    else:
        base = Path.cwd()
    return (base / "WorkItems").resolve()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="gcp_create_workitem",
            description="Create a new Golazo Copilot work item with persistent state tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Unique identifier for the work item (alphanumeric, hyphens, underscores)"
                    },
                    "profile": {
                        "type": "string",
                        "enum": ["complete", "express", "spike"],
                        "default": "complete",
                        "description": "Workflow profile determining which gates are enforced"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (auto-detected if not provided)"
                    }
                },
                "required": ["work_item_id"]
            }
        ),
        Tool(
            name="gcp_transition",
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
                        "enum": ["project-owner-assistant", "program-manager", "quality-assurance",
                                 "architect", "developer", "refactor-expert", "builder", "documentor", "retrospective"],
                        "description": "Target role to transition to"
                    },
                    "force": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force transition even if gates not met (requires prior consent)"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (auto-detected if not provided)"
                    }
                },
                "required": ["work_item_id", "role"]
            }
        ),
        Tool(
            name="gcp_status",
            description="Get comprehensive workflow status for a work item. Returns current role, phase, required outputs, next steps, deviations, and the Golazo Copilot version number. Use this to check the installed Golazo version.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item identifier"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path containing the WorkItems folder (auto-detected if not provided)"
                    }
                },
                "required": ["work_item_id"]
            }
        ),
        Tool(
            name="gcp_bootstrap",
            description="Bootstrap Golazo Copilot in a workspace - creates copilot instructions and directories",
            inputSchema={
                "type": "object",
                "properties": {
                    "force": {
                        "type": "boolean",
                        "default": False,
                        "description": "Overwrite existing files if they exist"
                    },
                    "include_roles": {
                        "type": "boolean",
                        "default": False,
                        "description": "Also copy default role files to .github/roles/"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Workspace root path (auto-detected if not provided)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="gcp_consent",
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
                        "description": "Workspace root path containing the WorkItems folder (auto-detected if not provided)"
                    }
                },
                "required": ["work_item_id", "action", "reason"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "gcp_create_workitem":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await gcp_create_workitem(
            work_item_id=arguments["work_item_id"],
            profile=arguments.get("profile", "complete"),
            work_items_dir=work_items_dir
        )
        
        if result["success"]:
            content = f"""{ICON_OK} Work item '{result['work_item_id']}' created!

**Current Role:** {result['current_role']}

---
{result['role_instructions']}
"""
        else:
            content = f"{ICON_FAIL} Failed to create work item: {result['error']}"
        
        return [TextContent(type="text", text=content)]
    
    elif name == "gcp_transition":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await gcp_transition(
            work_item_id=arguments["work_item_id"],
            role=arguments["role"],
            force=arguments.get("force", False),
            work_items_dir=work_items_dir
        )
        
        if result["success"]:
            warning = f"\n{ICON_WARN} {result['warning']}" if result.get("warning") else ""
            content = f"""{ICON_OK} Transitioned to '{result['current_role']}'!{warning}

**Current Phase:** {result['current_phase']}

---
{result['role_instructions']}
"""
        else:
            content = f"{ICON_FAIL} Transition failed: {result['error']}"
        
        return [TextContent(type="text", text=content)]
    
    elif name == "gcp_status":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await gcp_status(
            work_item_id=arguments["work_item_id"],
            work_items_dir=work_items_dir
        )
        
        if result.get("active", False):
            # GCP-0027: Format required outputs section
            outputs_section = ""
            req_outputs = result.get("required_outputs", {})
            output_list = req_outputs.get("outputs", [])
            if output_list:
                out_valid = sum(1 for o in output_list if o["valid"])
                out_total = len(output_list)
                out_status = f"{ICON_OK} Complete" if req_outputs.get("complete") else f"{ICON_PENDING} {out_valid}/{out_total}"
                out_lines = []
                for o in output_list:
                    icon = ICON_CHECK if o["valid"] else ICON_EMPTY
                    out_lines.append(f"  {icon} {o['path']}")
                outputs_section = f"\n- Required Outputs: {out_status}\n" + "\n".join(out_lines)
            
            next_steps = "\n".join(f"- {step}" for step in result["next_steps"])
            
            # Format deviations
            deviations_section = ""
            if result.get("deviations"):
                deviations_lines = []
                for d in result["deviations"]:
                    consumed = " (consumed)" if d["consumed"] else ""
                    deviations_lines.append(f"- {d['id']}: {d['action']} - \"{d['reason']}\"{consumed}")
                deviations_section = "\n\n**Deviations:**\n" + "\n".join(deviations_lines)
            
            content = f"""**Golazo Status** (v{result['version']})
- Work Item: {result['work_item_id']}
- Current Role: **{result['current_role']}**
- Phase: {result['current_phase']}{outputs_section}{deviations_section}

**Next Steps:**
{next_steps}

---
{result['role_instructions']}
"""
        else:
            version_info = f" (v{result.get('version', 'unknown')})" if 'version' in result else ""
            content = f"{ICON_WARN}{version_info} {result.get('message', 'No active work item')}"
        
        return [TextContent(type="text", text=content)]
    
    elif name == "gcp_bootstrap":
        result = await gcp_bootstrap(
            workspace_path=arguments.get("workspace_path"),
            force=arguments.get("force", False),
            include_roles=arguments.get("include_roles", False)
        )
        
        if result["success"]:
            created = "\n".join(f"  {ICON_CHECK} {f}" for f in result["files_created"]) or "  (none)"
            skipped = "\n".join(f"  {ICON_EMPTY} {f}" for f in result["files_skipped"]) or "  (none)"
            content = f"""{ICON_OK} Golazo Copilot bootstrapped!

**Files Created:**
{created}

**Files Skipped (already exist):**
{skipped}

{result['message']}
"""
        else:
            content = f"{ICON_FAIL} Bootstrap failed: {result['error']}"
        
        return [TextContent(type="text", text=content)]
    
    elif name == "gcp_consent":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await gcp_consent(
            work_item_id=arguments["work_item_id"],
            action=arguments["action"],
            reason=arguments["reason"],
            work_items_dir=work_items_dir
        )
        
        if result["success"]:
            content = f"""{ICON_OK} Consent recorded!

**Deviation ID:** {result['deviation_id']}
**Action:** {result['action']}

{result['message']}
"""
        else:
            content = f"{ICON_FAIL} Consent failed: {result['error']}"
        
        return [TextContent(type="text", text=content)]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run():
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()

