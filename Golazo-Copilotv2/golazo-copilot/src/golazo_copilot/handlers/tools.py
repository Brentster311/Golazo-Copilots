"""Tool handler implementations/adapters for server dispatch."""

from pathlib import Path

from mcp.types import TextContent

from ..formatters import (
    format_bootstrap_result,
    format_capabilities_result,
    format_consent_result,
    format_create_workitem_result,
    format_git_propose_result,
    format_role_context_result,
    format_status_result,
    format_transition_result,
    format_transition_workitem_result,
)
from ..formatters.results import ICON_FAIL, ICON_WARN
from ..tools.golazo_bootstrap import golazo_bootstrap
from ..tools.golazo_capabilities import golazo_capabilities
from ..tools.golazo_consent import golazo_consent
from ..tools.golazo_create_workitem import golazo_create_workitem
from ..tools.golazo_git_propose import golazo_git_propose
from ..tools.golazo_role_context import golazo_role_context
from ..tools.golazo_status import golazo_status
from ..tools.golazo_transition import golazo_transition
from ..tools.golazo_transition_workitem import golazo_transition_workitem
from ..dispatch.paths import resolve_work_items_dir


async def handle_registered_tool(name: str, arguments: dict, startup_tool_warnings: list[str]) -> list[TextContent] | None:
    """Dispatch known tool names to their handlers.

    Returns None when tool name is not handled.
    """
    if name == "golazo_create_workitem":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_create_workitem(
            work_item_id=arguments["work_item_id"],
            profile=arguments.get("profile", "complete"),
            work_items_dir=work_items_dir,
        )
        return [TextContent(type="text", text=format_create_workitem_result(result))]

    if name == "golazo_transition":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_transition(
            work_item_id=arguments["work_item_id"],
            role=arguments["role"],
            force=arguments.get("force", False),
            work_items_dir=work_items_dir,
        )
        return [TextContent(type="text", text=format_transition_result(result))]

    if name == "golazo_status":
        work_item_id = arguments.get("work_item_id", "").strip()
        if not work_item_id:
            from golazo_copilot import __version__ as version

            warning_lines = ""
            if startup_tool_warnings:
                warning_lines = "\n" + "\n".join(
                    f"{ICON_WARN} Tooling self-check: {warning}"
                    for warning in startup_tool_warnings
                )
            return [TextContent(type="text", text=f"**Golazo Copilot** (v{version}){warning_lines}")]

        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_status(
            work_item_id=work_item_id,
            work_items_dir=work_items_dir,
        )
        if startup_tool_warnings:
            result["tooling_warnings"] = list(startup_tool_warnings)
        return [TextContent(type="text", text=format_status_result(result))]

    if name == "golazo_bootstrap":
        ws = arguments.get("workspace_path")
        if not ws:
            return [TextContent(type="text", text=f"{ICON_FAIL} workspace_path is required")]
        result = await golazo_bootstrap(
            workspace_path=ws,
            mode=arguments.get("mode", "full"),
            force=arguments.get("force", False),
            include_roles=arguments.get("include_roles", True),
        )
        return [TextContent(type="text", text=format_bootstrap_result(result))]

    if name == "golazo_consent":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_consent(
            work_item_id=arguments["work_item_id"],
            action=arguments["action"],
            reason=arguments["reason"],
            work_items_dir=work_items_dir,
        )
        return [TextContent(type="text", text=format_consent_result(result))]

    if name == "golazo_capabilities":
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
        return [
            TextContent(
                type="text",
                text=format_capabilities_result(result, arguments["action"], arguments.get("files")),
            )
        ]

    if name == "golazo_role_context":
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

    if name == "golazo_git_propose":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_git_propose(
            work_item_id=arguments["work_item_id"],
            action=arguments["action"],
            files=arguments.get("files"),
            message=arguments.get("message"),
            branch=arguments.get("branch"),
            work_items_dir=work_items_dir,
        )
        return [TextContent(type="text", text=format_git_propose_result(result))]

    if name == "golazo_transition_workitem":
        work_items_dir = resolve_work_items_dir(arguments.get("workspace_path"))
        result = await golazo_transition_workitem(
            work_item_id=arguments["work_item_id"],
            work_items_dir=work_items_dir,
        )
        return [TextContent(type="text", text=format_transition_workitem_result(result))]

    return None
