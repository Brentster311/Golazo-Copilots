"""Copilot SDK tools that give the chat model access to live S360Reporter data.

Each tool is defined via ``copilot.define_tool`` and receives a reference to the
running ``SFIReporterApp`` instance so it can query ``current_data``.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from copilot import define_tool, Tool

if TYPE_CHECKING:
    from s360_reporter.S360Reporter import SFIReporterApp

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

        from s360_reporter.data import is_invalid_eta
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
        from s360_reporter.eta_logic import validate_eta_date, build_eta_update
        from s360_reporter.data import get_client, get_current_user_alias, is_invalid_eta

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
# Tool: web_fetch
# ---------------------------------------------------------------------------

def _build_web_fetch() -> Tool:
    """Tool that lets the LLM fetch any URL (SPA-aware via CDP/Playwright)."""

    def handler(args):
        url = args.get("url", "").strip()
        if not url:
            return "Error: 'url' parameter is required."
        if not url.lower().startswith(("http://", "https://")):
            return "Error: only http/https URLs are supported."

        from s360_reporter.kpi_analyzer import fetch_url_content, _is_login_page

        result = fetch_url_content(url)
        content = result.get("content", "")
        error = result.get("error", "")
        method = result.get("method", "urllib")
        discovered = result.get("discovered_urls", [])

        parts: list[str] = []
        if content and _is_login_page(content):
            parts.append(
                f"Authentication wall detected ({method}). This URL requires "
                "interactive login — content is not available for analysis."
            )
        elif content:
            parts.append(f"Fetched via {method} ({len(content)} chars):\n{content}")
        elif error:
            parts.append(f"Failed to fetch ({method}): {error}")
        else:
            parts.append(f"No content returned ({method}).")

        if discovered:
            parts.append("\nDiscovered links on page:")
            for durl in discovered[:20]:
                parts.append(f"  - {durl}")

        return "\n".join(parts)

    return _make_tool(
        "web_fetch",
        "Fetch and extract text content from a URL. Supports SPAs and "
        "JavaScript-rendered dashboards via headless Chromium (CDP). "
        "Falls back to plain HTTP if Chromium is unavailable. "
        "Also reports any links discovered on the page.",
        handler,
        {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The HTTP/HTTPS URL to fetch.",
                },
            },
            "required": ["url"],
        },
    )


# ---------------------------------------------------------------------------
# Tool: read_fetched_doc
# ---------------------------------------------------------------------------

# Tracks the most recent docs_dir set by send_analysis_prompt
_current_docs_dir: str = ""


def set_current_docs_dir(docs_dir: str) -> None:
    """Set the current docs directory for read_fetched_doc lookups."""
    global _current_docs_dir
    _current_docs_dir = docs_dir


def _build_read_fetched_doc() -> Tool:
    """Tool that lets the LLM read a pre-fetched document saved to disk."""

    def handler(args):
        import os
        filename = args.get("filename", "").strip()
        if not filename:
            return "Error: 'filename' parameter is required."

        if not _current_docs_dir:
            return "Error: No docs directory is set. Run an analysis first."

        # Security: prevent path traversal
        if os.sep in filename or "/" in filename or ".." in filename:
            return "Error: filename must be a plain filename, not a path."

        filepath = os.path.join(_current_docs_dir, filename)
        if not os.path.isfile(filepath):
            # List available files to help the LLM
            available = [f for f in os.listdir(_current_docs_dir)
                         if not f.startswith("_") and f.endswith(".txt")]
            return (f"File '{filename}' not found.\n"
                    f"Available docs: {', '.join(available[:20])}")

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as exc:
            return f"Error reading file: {exc}"

    return _make_tool(
        "read_fetched_doc",
        "Read a pre-fetched documentation file saved to disk during KPI analysis. "
        "Pass the filename from the documentation manifest shown in the analysis prompt. "
        "Returns the full text content of the saved document.",
        handler,
        {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The filename of the saved document (e.g. 'lens_msftcloudes_com__dashboard__a1b2c3d4.txt').",
                },
            },
            "required": ["filename"],
        },
    )


# ---------------------------------------------------------------------------
# Public: build all tools + system message
# ---------------------------------------------------------------------------

SYSTEM_MESSAGE = (
    "You are an SFI action-item assistant embedded in the S360Reporter desktop app. "
    "You help the user understand and manage their Security Foundation Index (SFI) and "
    "QEI (Quality Engineering Index) action items.\n\n"
    "You have tools to query the currently loaded data:\n"
    "- get_summary: dashboard overview\n"
    "- search_items: text search and SLA filtering\n"
    "- get_item_detail: full details for one item by ID\n"
    "- list_services: list all services with stats\n"
    "- items_for_service: items for a specific service\n"
    "- update_eta: update the ETA date for an action item via the S360 API\n"
    "- web_fetch: fetch and extract text from a URL (supports SPAs/dashboards)\n"
    "- read_fetched_doc: read a pre-fetched document saved to disk during analysis\n\n"
    "Guidelines:\n"
    "- Use tools to answer data questions — don't guess.\n"
    "- If no data is loaded, tell the user to click 'Refresh Data'.\n"
    "- Be concise. OutOfSla = overdue, InSla = on track.\n"
    "- For simple greetings, respond without calling tools.\n"
    "- When updating ETAs, always confirm the item ID and date with the user first.\n"
    "- ETA dates must be in YYYY-MM-DD format, today or later, within 1 year.\n\n"
    "KPI analysis workflow:\n"
    "- When analyzing a KPI, documentation URLs are pre-fetched and saved to disk.\n"
    "- The prompt includes a manifest of saved files with filenames and char counts.\n"
    "- Use read_fetched_doc to read the most relevant files on demand.\n"
    "- Start with the largest/most relevant docs; skip FAILED entries.\n"
    "- You do NOT need to read every file — focus on what answers the questions.\n\n"
    "URL exploration (interactive chat):\n"
    "- Use web_fetch to visit URLs the user provides or that you discover.\n"
    "- If access is blocked (auth/iframe/network), report the limitation, "
    "request alternate data or screenshots, and proceed with partial analysis.\n"
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
        _build_web_fetch(),
        _build_read_fetched_doc(),
    ]
