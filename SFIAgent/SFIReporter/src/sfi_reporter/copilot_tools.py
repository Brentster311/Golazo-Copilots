"""Copilot SDK tools that give the chat model access to live SFI Reporter data.

Each tool is defined via ``copilot.define_tool`` and receives a reference to the
running ``SFIReporterApp`` instance so it can query ``current_data``.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from copilot import define_tool, Tool

if TYPE_CHECKING:
    from sfi_reporter.app import SFIReporterApp

logger = logging.getLogger(__name__)

# Maximum characters to return from any single tool (avoid token overflow)
_MAX_RESULT_LEN = 8_000


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _get_items(app: "SFIReporterApp") -> list[dict]:
    """Return the current detailed action items (may be empty)."""
    return app.current_data.get("detailed_items", [])


def _summarise_item(item: dict) -> dict:
    """Return the most useful fields from a detailed action-item dict."""
    return {
        "id": item.get("id", ""),
        "title": item.get("title", ""),
        "service": item.get("S360_ServiceTreeServiceName", ""),
        "sla_type": item.get("SlaType", ""),
        "eta_date": item.get("EtaDate", ""),
        "due_date": item.get("dueDate", ""),
        "owner": item.get("ActionOwnerName", ""),
        "assigned_to": item.get("S360_AssignedToName", ""),
        "status": item.get("ActionItemStatus", ""),
        "kpi": item.get("_kpi_name", item.get("_kpi_id", "")),
    }


def _truncate(text: str) -> str:
    """Truncate tool output to avoid token overflow."""
    if len(text) <= _MAX_RESULT_LEN:
        return text
    return text[:_MAX_RESULT_LEN] + "\n... (truncated)"


def _make_tool(name: str, description: str, handler, parameters: dict | None = None) -> Tool:
    """Create a Tool without pydantic — uses a plain JSON schema dict.

    This avoids pydantic-generated ``anyOf``, ``$defs``, and ``title``
    fields that the Copilot API rejects with 400 ``invalid_request_body``.
    """
    import asyncio
    from copilot import ToolResult

    async def _async_handler(invocation):
        try:
            args = invocation.get("arguments") or {}
            result = handler(args)
            if asyncio.iscoroutine(result):
                result = await result
            text = str(result) if not isinstance(result, str) else result
            return ToolResult(textResultForLlm=_truncate(text))
        except Exception as exc:
            logger.exception("Tool %s failed", name)
            return ToolResult(
                textResultForLlm=f"Tool error: {exc}",
                resultType="failure",
                error=str(exc),
            )

    return Tool(
        name=name,
        description=description,
        handler=_async_handler,
        parameters=parameters,
    )


# ---------------------------------------------------------------------------
# Tool: get_summary
# ---------------------------------------------------------------------------

def _build_get_summary(app: "SFIReporterApp") -> Tool:
    def handler(_args):
        data = app.current_data
        if not data:
            return "No data loaded. Ask the user to click Refresh Data first."

        items = data.get("detailed_items", [])
        svc_stats = data.get("service_stats", {})
        pgm_stats = data.get("program_stats", {})

        total = len(items)
        out_of_sla = sum(1 for i in items if i.get("SlaType") == "OutOfSla")

        from sfi_reporter.data import is_invalid_eta
        invalid_eta = sum(1 for i in items if is_invalid_eta(i.get("EtaDate")))

        services = [
            {"name": s["name"], "total": s["count"], "out_of_sla": s["sla"], "invalid_eta": s["invalid_eta"]}
            for s in svc_stats.values()
        ]
        programs = [
            {"name": k, "total": v["count"], "out_of_sla": v["sla"], "invalid_eta": v["invalid_eta"]}
            for k, v in pgm_stats.items()
        ]

        summary = {
            "total_items": total,
            "out_of_sla": out_of_sla,
            "invalid_eta": invalid_eta,
            "services": sorted(services, key=lambda s: s["total"], reverse=True),
            "programs": sorted(programs, key=lambda p: p["total"], reverse=True),
        }
        return json.dumps(summary)

    return _make_tool(
        "get_summary",
        "Get a high-level summary of the loaded SFI data: total items, out-of-SLA count, "
        "invalid-ETA count, and per-service / per-program breakdowns.",
        handler,
    )


# ---------------------------------------------------------------------------
# Tool: search_items
# ---------------------------------------------------------------------------

def _build_search_items(app: "SFIReporterApp") -> Tool:
    def handler(args):
        items = _get_items(app)
        if not items:
            return "No data loaded."

        q = (args.get("query") or "").lower()
        sla_filter = args.get("sla_filter") or ""
        limit = int(args.get("limit", 20))

        results = []
        for item in items:
            if sla_filter and item.get("SlaType") != sla_filter:
                continue
            searchable = " ".join(str(item.get(f, "")) for f in (
                "title", "S360_ServiceTreeServiceName",
                "ActionOwnerName", "_kpi_name", "_kpi_id",
                "S360_AssignedToName", "ActionOwnerAlias",
            )).lower()
            if q and q not in searchable:
                continue
            results.append(_summarise_item(item))
            if len(results) >= limit:
                break

        return json.dumps({"count": len(results), "items": results})

    return _make_tool(
        "search_items",
        "Search and filter loaded action items by text query and/or SLA status.",
        handler,
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Text to search for in titles, services, owners, KPIs. Case-insensitive."},
                "sla_filter": {"type": "string", "description": "Optional: 'OutOfSla' or 'InSla'."},
                "limit": {"type": "integer", "description": "Max results (default 20)."},
            },
            "required": ["query"],
        },
    )


# ---------------------------------------------------------------------------
# Tool: get_item_detail
# ---------------------------------------------------------------------------

def _build_get_item_detail(app: "SFIReporterApp") -> Tool:
    def handler(args):
        item_id = args.get("item_id", "")
        for item in _get_items(app):
            if item.get("id") == item_id:
                safe = {k: v for k, v in item.items()
                        if not k.startswith("_") and isinstance(v, (str, int, float, bool, list, dict, type(None)))}
                return json.dumps(safe, default=str)
        return f"Item '{item_id}' not found."

    return _make_tool(
        "get_item_detail",
        "Get all available fields for a specific action item by its ID.",
        handler,
        {
            "type": "object",
            "properties": {
                "item_id": {"type": "string", "description": "The action item ID."},
            },
            "required": ["item_id"],
        },
    )


# ---------------------------------------------------------------------------
# Tool: list_services
# ---------------------------------------------------------------------------

def _build_list_services(app: "SFIReporterApp") -> Tool:
    def handler(_args):
        svc_stats = app.current_data.get("service_stats", {})
        if not svc_stats:
            return "No service data loaded."
        services = [
            {"name": s["name"], "total": s["count"], "out_of_sla": s["sla"], "invalid_eta": s["invalid_eta"]}
            for s in svc_stats.values()
        ]
        services.sort(key=lambda s: s["total"], reverse=True)
        return json.dumps(services)

    return _make_tool(
        "list_services",
        "List all services with their action item counts, out-of-SLA, and invalid-ETA counts.",
        handler,
    )


# ---------------------------------------------------------------------------
# Tool: items_for_service
# ---------------------------------------------------------------------------

def _build_items_for_service(app: "SFIReporterApp") -> Tool:
    def handler(args):
        items = _get_items(app)
        q = (args.get("service_name") or "").lower()
        matches = [
            _summarise_item(i) for i in items
            if q in (i.get("S360_ServiceTreeServiceName") or "").lower()
        ]
        return json.dumps({"count": len(matches), "items": matches})

    return _make_tool(
        "items_for_service",
        "List all action items for a specific service (by name, partial match).",
        handler,
        {
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "description": "Service name to filter by (case-insensitive partial match)."},
            },
            "required": ["service_name"],
        },
    )


# ---------------------------------------------------------------------------
# Tool: update_eta
# ---------------------------------------------------------------------------

def _build_update_eta(app: "SFIReporterApp") -> Tool:
    def handler(args):
        from sfi_reporter.eta_logic import validate_eta_date, build_eta_update
        from sfi_reporter.data import get_client, get_current_user_alias, is_invalid_eta

        item_id = args.get("item_id", "")
        new_eta = args.get("new_eta", "")
        notes = args.get("notes", "")

        # Find the item
        item = None
        for i in _get_items(app):
            if i.get("id") == item_id:
                item = i
                break
        if item is None:
            return f"Item '{item_id}' not found in loaded data."

        # Validate the date
        ok, msg = validate_eta_date(new_eta)
        if not ok:
            return f"Invalid ETA date: {msg}"

        # Build the update
        update = build_eta_update(
            item,
            new_eta,
            notes=notes,
            fallback_alias=get_current_user_alias() or "",
        )

        # Save via API
        try:
            client = get_client()
            result = client.save_etas([update])
        except Exception as exc:
            return f"API error saving ETA: {exc}"

        if not result.success:
            err = result.error_message or ", ".join(result.failed_items)
            return f"Save failed: {err}"

        # Update in-memory data so subsequent reads reflect the change
        item["EtaDate"] = new_eta
        if notes:
            item["EtaStatus"] = notes

        # Recalculate invalid-ETA counts
        data = app.current_data
        if data:
            detailed = data.get("detailed_items", [])
            for stats_dict in (data.get("service_stats", {}),
                               data.get("kpi_stats", {}),
                               data.get("program_stats", {})):
                for key in stats_dict:
                    stats_dict[key]["invalid_eta"] = 0
            for row in detailed:
                if is_invalid_eta(row.get("EtaDate")):
                    svc_id = row.get("S360_ServiceId", "Unknown")
                    kpi_id = row.get("_kpi_id", "Unknown")
                    if svc_id in data.get("service_stats", {}):
                        data["service_stats"][svc_id]["invalid_eta"] += 1
                    if kpi_id in data.get("kpi_stats", {}):
                        data["kpi_stats"][kpi_id]["invalid_eta"] += 1
                    pid_list = row.get("S360_ProgramIds") or []
                    if pid_list:
                        programs_lookup = data.get("programs_lookup", {})
                        pname = programs_lookup.get(pid_list[0], "Other Program")
                        if pname in data.get("program_stats", {}):
                            data["program_stats"][pname]["invalid_eta"] += 1

        # Refresh the UI tables
        try:
            app.root.after(0, lambda: app._refresh_tables_after_eta_update())
        except Exception:
            pass  # UI refresh is best-effort

        title = item.get("title", item_id)
        return f"ETA for '{title}' updated to {new_eta}."

    return _make_tool(
        "update_eta",
        "Update the ETA date for a specific action item. Saves to the S360 API and "
        "refreshes the in-memory data. Date must be YYYY-MM-DD, today or later, within 1 year.",
        handler,
        {
            "type": "object",
            "properties": {
                "item_id": {"type": "string", "description": "The action item ID to update."},
                "new_eta": {"type": "string", "description": "New ETA date in YYYY-MM-DD format."},
                "notes": {"type": "string", "description": "Optional status note to save with the ETA."},
            },
            "required": ["item_id", "new_eta"],
        },
    )


# ---------------------------------------------------------------------------
# Public: build all tools + system message
# ---------------------------------------------------------------------------

SYSTEM_MESSAGE = (
    "You are an SFI action-item assistant embedded in the SFI Reporter desktop app. "
    "You help the user understand and manage their Security Foundation Index (SFI) and "
    "QEI (Quality Engineering Index) action items.\n\n"
    "You have tools to query the currently loaded data:\n"
    "- get_summary: dashboard overview\n"
    "- search_items: text search and SLA filtering\n"
    "- get_item_detail: full details for one item by ID\n"
    "- list_services: list all services with stats\n"
    "- items_for_service: items for a specific service\n"
    "- update_eta: update the ETA date for an action item via the S360 API\n\n"
    "Guidelines:\n"
    "- Use tools to answer data questions — don't guess.\n"
    "- If no data is loaded, tell the user to click 'Refresh Data'.\n"
    "- Be concise. OutOfSla = overdue, InSla = on track.\n"
    "- For simple greetings, respond without calling tools.\n"
    "- When updating ETAs, always confirm the item ID and date with the user first.\n"
    "- ETA dates must be in YYYY-MM-DD format, today or later, within 1 year.\n"
)


def build_tools(app: "SFIReporterApp") -> list:
    """Build all Copilot SDK tools bound to the given app instance."""
    return [
        _build_get_summary(app),
        _build_search_items(app),
        _build_get_item_detail(app),
        _build_list_services(app),
        _build_items_for_service(app),
        _build_update_eta(app),
    ]
