"""Routing/dispatch for MCP server tools."""

from mcp.types import TextContent

from ..formatters.results import ICON_FAIL
from ..handlers.tools import handle_registered_tool
from .paths import has_orchestrator_instructions
from .registry import WORKFLOW_TOOLS_REQUIRING_INSTRUCTIONS, get_tool_definitions


async def dispatch_tool(name: str, arguments: dict, startup_tool_warnings: list[str] | None = None) -> list[TextContent]:
    """Internal dispatcher with workflow preflight and routed handlers."""
    preflight_failure = _workflow_preflight_failure(name, arguments)
    if preflight_failure:
        return [TextContent(type="text", text=preflight_failure)]

    handled = await handle_registered_tool(name, arguments, startup_tool_warnings or [])
    if handled is not None:
        return handled

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


def _workflow_preflight_failure(name: str, arguments: dict) -> str | None:
    if name not in WORKFLOW_TOOLS_REQUIRING_INSTRUCTIONS:
        return None

    ws = arguments.get("workspace_path")
    if name == "golazo_status" and not arguments.get("work_item_id", "").strip():
        return None

    if not ws:
        return f"{ICON_FAIL} workspace_path is required"

    if has_orchestrator_instructions(ws):
        return None

    return (
        f"{ICON_FAIL} Orchestrator instructions are required before workflow operations. "
        f"Missing: .github/agents/Golazo-Copilot.md in workspace or user Copilot scope\n\n"
        f"Run: golazo_bootstrap(workspace_path=\"{ws}\", mode=\"orchestrator-only\")\n"
        f"Or:  golazo_bootstrap(workspace_path=\"{ws}\", mode=\"orchestrator-only\", scope=\"User\")\n"
        f"Use force=True to overwrite an existing instructions file."
    )


async def runtime_tool_self_check(required_tool_names: set[str] | None = None) -> list[str]:
    """Validate tool registration and dispatch consistency at startup."""
    warnings: list[str] = []
    tool_names = {tool.name for tool in get_tool_definitions()}

    missing_required = sorted((required_tool_names or set()) - tool_names)
    if missing_required:
        warnings.append(
            "Missing required tool registration: " + ", ".join(missing_required)
        )

    missing_dispatch: list[str] = []
    for tool_name in sorted(tool_names):
        try:
            result = await dispatch_tool(tool_name, {}, startup_tool_warnings=[])
        except Exception:
            continue

        first_text = result[0].text if result and hasattr(result[0], "text") else ""
        if isinstance(first_text, str) and first_text.startswith("Unknown tool:"):
            missing_dispatch.append(tool_name)

    if missing_dispatch:
        warnings.append(
            "Advertised tool(s) missing dispatch branch: " + ", ".join(missing_dispatch)
        )

    return warnings
