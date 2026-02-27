# -*- coding: utf-8 -*-
"""Golazo Copilot MCP Server - Entry point for GitHub Copilot integration."""

import asyncio
import sys
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from . import __version__
from .tools.golazo_create_workitem import golazo_create_workitem
from .tools.golazo_transition import golazo_transition
from .tools.golazo_status import golazo_status
from .tools.golazo_bootstrap import golazo_bootstrap
from .tools.golazo_consent import golazo_consent
from .tools.golazo_capabilities import golazo_capabilities
from .tools.golazo_role_context import golazo_role_context

# Create server instance with version in name
server = Server(f"golazo-copilot v{__version__}")

# Status icons (using ASCII to avoid encoding issues)
ICON_OK = "[OK]"
ICON_FAIL = "[FAIL]"
ICON_WARN = "[WARN]"
ICON_PENDING = "[...]"
ICON_CHECK = "[x]"
ICON_EMPTY = "[ ]"

_REQUIRED_TOOL_NAMES: set[str] = set()
_STARTUP_TOOL_WARNINGS: list[str] = []


def resolve_work_items_dir(workspace_path: str | None) -> Path:
    """
    Resolve workspace_path to an absolute work_items_dir Path.
    
    Args:
        workspace_path: Workspace root path (required, must not be None or empty)
        
    Returns:
        Absolute Path to the WorkItems directory
        
    Raises:
        ValueError: If workspace_path is None or empty
    """
    if not workspace_path:
        raise ValueError("workspace_path is required — MCP servers cannot rely on cwd")
    return (Path(workspace_path) / "WorkItems").resolve()


# ---------------------------------------------------------------------------
# Pure formatting functions (no MCP or I/O dependencies)
# ---------------------------------------------------------------------------

def format_create_workitem_result(result: dict) -> str:
    """Format golazo_create_workitem result dict into display text."""
    if result["success"]:
        return f"""{ICON_OK} Work item '{result['work_item_id']}' created!

**Current Role:** {result['current_role']}

---
{result['role_instructions']}
"""
    return f"{ICON_FAIL} Failed to create work item: {result['error']}"


def format_transition_result(result: dict) -> str:
    """Format golazo_transition result dict into display text."""
    if result["success"]:
        warning = f"\n{ICON_WARN} {result['warning']}" if result.get("warning") else ""
        # GCP-0053: Closure mode indicator on transition
        closure_label = f" {ICON_WARN} **CLOSURE MODE**" if result.get("closure_pending") else ""
        return f"""{ICON_OK} Transitioned to '{result['current_role']}'!{warning}

**Current Phase:** {result['current_phase']}{closure_label}

---
{result['role_instructions']}
"""
    return f"{ICON_FAIL} Transition failed: {result['error']}"


def format_status_result(result: dict) -> str:
    """Format golazo_status result dict into display text."""
    if result.get("active", False):
        # GCP-0032: Format version warning if present
        version_warning = ""
        if result.get("version_warning"):
            version_warning = f"\n{ICON_WARN} {result['version_warning']}"

        # GCP-0033: Format role progress
        progress_section = ""
        role_progress = result.get("role_progress", {})
        if role_progress:
            completed = role_progress.get("roles_completed", 0)
            total = role_progress.get("roles_total", 9)
            progress_section = f"\n- Role Progress: {completed}/{total} complete"

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

        # GCP-0042: Format registry hint
        registry_section = ""
        if result.get("registry_hint"):
            registry_section = f"\n- {result['registry_hint']}"

        tooling_warning_section = ""
        tooling_warnings = result.get("tooling_warnings", [])
        if tooling_warnings:
            tooling_warning_section = "\n- Tooling self-check warnings: " + " | ".join(tooling_warnings)

        next_steps = "\n".join(f"- {step}" for step in result["next_steps"])

        # GCP-0053: Closure mode indicator
        closure_label = ""
        if result.get("closure_pending"):
            closure_label = f" {ICON_WARN} **CLOSURE MODE**"

        # Format deviations
        deviations_section = ""
        if result.get("deviations"):
            deviations_lines = []
            for d in result["deviations"]:
                consumed = " (consumed)" if d["consumed"] else ""
                deviations_lines.append(f"- {d['id']}: {d['action']} - \"{d['reason']}\"{consumed}")
            deviations_section = "\n\n**Deviations:**\n" + "\n".join(deviations_lines)

        return f"""**Golazo Status** (v{result['version']}){version_warning}
- Work Item: {result['work_item_id']}
- Current Role: **{result['current_role']}**{closure_label}
    - Phase: {result['current_phase']}{progress_section}{outputs_section}{registry_section}{tooling_warning_section}{deviations_section}

**Next Steps:**
{next_steps}

---
{result['role_instructions']}
"""
    version_info = f" (v{result.get('version', 'unknown')})" if 'version' in result else ""
    tooling_warnings = result.get("tooling_warnings", [])
    tooling_suffix = ""
    if tooling_warnings:
        tooling_suffix = "\n" + "\n".join(f"{ICON_WARN} Tooling self-check: {w}" for w in tooling_warnings)
    return f"{ICON_WARN}{version_info} {result.get('message', 'No active work item')}{tooling_suffix}"


def format_bootstrap_result(result: dict) -> str:
    """Format golazo_bootstrap result dict into display text."""
    if result["success"]:
        created = "\n".join(f"  {ICON_CHECK} {f}" for f in result["files_created"]) or "  (none)"
        skipped = "\n".join(f"  {ICON_EMPTY} {f}" for f in result["files_skipped"]) or "  (none)"
        return f"""{ICON_OK} Golazo Copilot bootstrapped!

**Files Created:**
{created}

**Files Skipped (already exist):**
{skipped}

{result['message']}
"""
    error_msg = result['error']
    if "No workspace markers found" in error_msg:
        error_msg += (
            "\n\n**Next step:** Confirm with the user that the workspace_path is correct. "
            "If it is, create a `WorkItems` folder at that path (e.g. `mkdir <workspace_path>/WorkItems`) "
            "and then re-run `golazo_bootstrap`."
        )
    return f"{ICON_FAIL} Bootstrap failed: {error_msg}"


def format_consent_result(result: dict) -> str:
    """Format golazo_consent result dict into display text."""
    if result["success"]:
        return f"""{ICON_OK} Consent recorded!

**Deviation ID:** {result['deviation_id']}
**Action:** {result['action']}

{result['message']}
"""
    return f"{ICON_FAIL} Consent failed: {result['error']}"


def format_capabilities_result(result: dict, action: str, files: list | None = None) -> str:
    """Format golazo_capabilities result dict into display text."""
    if not result["success"]:
        return f"{ICON_FAIL} {result['error']}"
    if result.get("message"):
        return result["message"]
    if action == "list":
        caps = result["capabilities"]
        if not caps:
            return "**Capability Registry** (empty)"
        lines = [f"**Capability Registry** ({len(caps)} capabilities)"]
        for c in caps:
            lines.append(f"- **{c['name']}**: {c['description']}")
        return "\n".join(lines)
    if action == "show":
        cap = result["capability"]
        key_files = ", ".join(cap["key_files"]) or "(none)"
        contracts = "\n  ".join(f"- {c}" for c in cap["contracts"]) or "  (none)"
        depends = ", ".join(cap["depends_on"]) or "(none)"
        depended = ", ".join(cap["depended_on_by"]) or "(none)"
        return f"""**Capability: {cap['name']}**
- **Description**: {cap['description']}
- **Key Files**: {key_files}
- **Contracts**:
  {contracts}
- **Depends On**: {depends}
- **Depended On By**: {depended}"""
    if action == "impact":
        direct = result["directly_affected"]
        transitive = result["transitively_affected"]
        total = len(direct) + len(transitive)
        lines = [f"**Impact Analysis** ({len(files or [])} files -> {total} capabilities affected)"]
        if direct:
            lines.append("\n**Directly Affected:**")
            for c in direct:
                lines.append(f"- **{c['name']}**: {c['description']}")
        if transitive:
            lines.append("\n**Transitively Affected (dependents):**")
            for c in transitive:
                lines.append(f"- **{c['name']}**: {c['description']}")
        if not direct and not transitive:
            lines.append("\nNo capabilities affected by the given files.")
        return "\n".join(lines)
    if action == "validate":
        lines = ["**Registry Validation**"]
        for r in result["results"]:
            if r["valid"]:
                lines.append(f"{ICON_OK} **{r['name']}**: all key_files exist")
            else:
                missing = ", ".join(r["missing_files"])
                lines.append(f"{ICON_FAIL} **{r['name']}**: missing {missing}")
        return "\n".join(lines)
    return str(result)


def format_role_context_result(result: dict) -> str:
    """Format golazo_role_context result dict into display text."""
    if result["status"] != "ok":
        return f"{ICON_FAIL} {result['error']}"
    meta = []
    meta.append(f"Role: {result.get('role', 'unknown')}")
    meta.append(f"Artifacts: {result.get('artifact_count', 0)}")
    meta.append(f"Size: {result.get('total_size', 0)} bytes")
    if result.get("truncated"):
        meta.append(f"{ICON_WARN} Some artifacts were truncated")
    header = " | ".join(meta)
    return f"""{ICON_OK} Role context bundled ({header})

{result['bundle']}"""


def format_update_result(result: dict) -> str:
    """Format golazo_update result dict into display text."""
    if result.get("status") == "error":
        msg = f"{ICON_FAIL} {result['error']}"
        if result.get("stderr"):
            msg += f"\n\n```\n{result['stderr']}\n```"
        return msg

    action = result.get("action")

    if action == "check":
        lines = [
            f"{ICON_OK} **Golazo Copilot Version Check**",
            f"",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| Current version | {result['current_version']} |",
            f"| Latest stable | {result.get('latest_stable', 'N/A')} |",
        ]
        if result.get("latest_prerelease"):
            lines.append(f"| Latest pre-release | {result['latest_prerelease']} |")
        if result["update_available"]:
            lines.append(f"\n{ICON_WARN} **Update available!** Use `golazo_update(action=\"install\", version=\"<version>\")` to install.")
        else:
            lines.append(f"\n{ICON_OK} Already up to date.")
        return "\n".join(lines)

    if action == "install":
        lines = [
            f"{ICON_OK} **Installed golazo-copilot {result['installed_version']}**",
            f"",
            f"{ICON_WARN} {result['restart_message']}",
            f"",
            f"**Post-restart bootstrap options:**",
        ]
        for opt in result.get("bootstrap_options", []):
            lines.append(f"- {opt}")
        return "\n".join(lines)

    # Fallback
    return str(result)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return _get_tool_definitions()


def _get_tool_definitions() -> list[Tool]:
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
                    "force": {
                        "type": "boolean",
                        "default": False,
                        "description": "Overwrite existing files if they exist"
                    },
                    "include_roles": {
                        "type": "boolean",
                        "default": True,
                        "description": "Also copy default role files to .github/roles/"
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
    ]


async def _runtime_tool_self_check() -> list[str]:
    """Validate tool registration consistency at startup.

    Checks:
    - Required tools are advertised in list_tools.
    - Every advertised tool has a dispatcher branch (not Unknown tool).
    """
    warnings: list[str] = []
    tool_names = {tool.name for tool in _get_tool_definitions()}

    missing_required = sorted(_REQUIRED_TOOL_NAMES - tool_names)
    if missing_required:
        warnings.append(
            "Missing required tool registration: " + ", ".join(missing_required)
        )

    missing_dispatch: list[str] = []
    for tool_name in sorted(tool_names):
        try:
            result = await _dispatch_tool(tool_name, {})
        except Exception:
            # Expected for many tools due to required params; this still proves
            # a dispatcher branch exists for the tool.
            continue

        first_text = result[0].text if result and hasattr(result[0], "text") else ""
        if isinstance(first_text, str) and first_text.startswith("Unknown tool:"):
            missing_dispatch.append(tool_name)

    if missing_dispatch:
        warnings.append(
            "Advertised tool(s) missing dispatch branch: " + ", ".join(missing_dispatch)
        )

    return warnings


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        return await _dispatch_tool(name, arguments)
    except ValueError as exc:
        return [TextContent(type="text", text=f"{ICON_FAIL} {exc}")]


async def _dispatch_tool(name: str, arguments: dict) -> list[TextContent]:
    """Internal dispatcher — separated so ValueError bubbles to call_tool."""
    if name == "golazo_create_workitem":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_create_workitem(
            work_item_id=arguments["work_item_id"],
            profile=arguments.get("profile", "complete"),
            work_items_dir=work_items_dir
        )
        return [TextContent(type="text", text=format_create_workitem_result(result))]

    elif name == "golazo_transition":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_transition(
            work_item_id=arguments["work_item_id"],
            role=arguments["role"],
            force=arguments.get("force", False),
            work_items_dir=work_items_dir
        )
        return [TextContent(type="text", text=format_transition_result(result))]

    elif name == "golazo_status":
        work_item_id = arguments.get("work_item_id", "").strip()
        if not work_item_id:
            from golazo_copilot import __version__ as ver
            warning_lines = ""
            if _STARTUP_TOOL_WARNINGS:
                warning_lines = "\n" + "\n".join(f"{ICON_WARN} Tooling self-check: {w}" for w in _STARTUP_TOOL_WARNINGS)
            return [TextContent(type="text", text=f"**Golazo Copilot** (v{ver}){warning_lines}")]
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_status(
            work_item_id=work_item_id,
            work_items_dir=work_items_dir
        )
        if _STARTUP_TOOL_WARNINGS:
            result["tooling_warnings"] = list(_STARTUP_TOOL_WARNINGS)
        return [TextContent(type="text", text=format_status_result(result))]

    elif name == "golazo_bootstrap":
        ws = arguments.get("workspace_path")
        if not ws:
            return [TextContent(type="text", text=f"{ICON_FAIL} workspace_path is required")]
        result = await golazo_bootstrap(
            workspace_path=ws,
            force=arguments.get("force", False),
            include_roles=arguments.get("include_roles", True)
        )
        return [TextContent(type="text", text=format_bootstrap_result(result))]

    elif name == "golazo_consent":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_consent(
            work_item_id=arguments["work_item_id"],
            action=arguments["action"],
            reason=arguments["reason"],
            work_items_dir=work_items_dir
        )
        return [TextContent(type="text", text=format_consent_result(result))]

    elif name == "golazo_capabilities":
        ws_cap = arguments.get("workspace_path")
        if not ws_cap:
            return [TextContent(type="text", text=f"{ICON_FAIL} workspace_path is required")]
        workspace_path = Path(ws_cap)
        result = await golazo_capabilities(
            action=arguments["action"],
            capability=arguments.get("capability"),
            files=arguments.get("files"),
            workspace_path=workspace_path,
        )
        return [TextContent(type="text", text=format_capabilities_result(
            result, arguments["action"], arguments.get("files")
        ))]

    elif name == "golazo_role_context":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        ws = arguments.get("workspace_path")
        project_root = Path(ws) if ws else None
        result = await golazo_role_context(
            work_item_id=arguments["work_item_id"],
            role=arguments.get("role"),
            work_items_dir=work_items_dir,
            project_root=project_root,
        )
        return [TextContent(type="text", text=format_role_context_result(result))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    global _STARTUP_TOOL_WARNINGS
    startup_warnings = await _runtime_tool_self_check()
    _STARTUP_TOOL_WARNINGS = list(startup_warnings)
    for warning in startup_warnings:
        print(f"{ICON_WARN} Startup self-check: {warning}", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run():
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()

