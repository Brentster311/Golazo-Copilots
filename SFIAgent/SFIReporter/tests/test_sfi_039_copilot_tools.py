"""Tests for sfi_reporter.copilot_tools — target ≥70 % coverage.

The ``copilot`` package is NOT installed in the test environment, so we inject
mock modules into ``sys.modules`` BEFORE importing anything from sfi_reporter.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Mock the copilot SDK before importing copilot_tools
# ---------------------------------------------------------------------------
_mock_copilot = MagicMock()


class _FakeTool:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _FakeToolResult:
    def __init__(self, **kw):
        self.__dict__.update(kw)


_mock_copilot.Tool = _FakeTool
_mock_copilot.ToolResult = _FakeToolResult
_mock_copilot.define_tool = MagicMock()
sys.modules.setdefault("copilot", _mock_copilot)

# NOW we can safely import
from sfi_reporter.copilot_tools import (  # noqa: E402
    SYSTEM_MESSAGE,
    _MAX_RESULT_LEN,
    _build_get_item_detail,
    _build_get_summary,
    _build_items_for_service,
    _build_list_services,
    _build_read_fetched_doc,
    _build_search_items,
    _build_update_eta,
    _build_web_fetch,
    _get_items,
    _make_tool,
    _summarise_item,
    _truncate,
    build_tools,
    set_current_docs_dir,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    """Run an async handler synchronously."""
    return asyncio.run(coro)


def make_mock_app(items=None, service_stats=None, program_stats=None):
    app = MagicMock()
    app.current_data = {
        "detailed_items": items or [],
        "service_stats": service_stats or {},
        "program_stats": program_stats or {},
        "kpi_stats": {},
        "programs_lookup": {},
    }
    app.root = MagicMock()
    return app


SAMPLE_ITEM = {
    "id": "AI-001",
    "title": "Fix vulnerability",
    "S360_ServiceTreeServiceName": "MyService",
    "SlaType": "OutOfSla",
    "EtaDate": "2026-03-01",
    "dueDate": "2026-02-28",
    "ActionOwnerName": "Alice",
    "S360_AssignedToName": "Bob",
    "ActionItemStatus": "Active",
    "_kpi_name": "KPI-A",
    "_kpi_id": "kpi-a",
    "S360_ServiceId": "svc-1",
    "S360_ProgramIds": ["pgm-1"],
}


# ---------------------------------------------------------------------------
# Tests: helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_get_items_returns_list(self):
        app = make_mock_app(items=[SAMPLE_ITEM])
        assert _get_items(app) == [SAMPLE_ITEM]

    def test_get_items_empty(self):
        app = make_mock_app()
        assert _get_items(app) == []

    def test_get_items_missing_key(self):
        app = MagicMock()
        app.current_data = {}
        assert _get_items(app) == []

    def test_summarise_item(self):
        s = _summarise_item(SAMPLE_ITEM)
        assert s["id"] == "AI-001"
        assert s["title"] == "Fix vulnerability"
        assert s["service"] == "MyService"
        assert s["sla_type"] == "OutOfSla"
        assert s["owner"] == "Alice"
        assert s["kpi"] == "KPI-A"

    def test_summarise_item_empty(self):
        s = _summarise_item({})
        assert s["id"] == ""
        assert s["kpi"] == ""

    def test_truncate_short(self):
        assert _truncate("hello") == "hello"

    def test_truncate_exact_limit(self):
        text = "x" * _MAX_RESULT_LEN
        assert _truncate(text) == text

    def test_truncate_long(self):
        text = "x" * (_MAX_RESULT_LEN + 100)
        result = _truncate(text)
        assert result.endswith("... (truncated)")
        assert len(result) == _MAX_RESULT_LEN + len("\n... (truncated)")


# ---------------------------------------------------------------------------
# Tests: _make_tool
# ---------------------------------------------------------------------------

class TestMakeTool:
    def test_make_tool_basic(self):
        tool = _make_tool("test_tool", "desc", lambda args: "ok")
        assert tool.name == "test_tool"
        assert tool.description == "desc"
        assert tool.handler is not None

    def test_make_tool_handler_success(self):
        tool = _make_tool("t", "d", lambda args: "result")
        res = _run(tool.handler({"arguments": {}}))
        assert res.textResultForLlm == "result"

    def test_make_tool_handler_non_string_result(self):
        tool = _make_tool("t", "d", lambda args: 42)
        res = _run(tool.handler({"arguments": {}}))
        assert res.textResultForLlm == "42"

    def test_make_tool_handler_exception(self):
        def bad_handler(args):
            raise ValueError("boom")

        tool = _make_tool("t", "d", bad_handler)
        res = _run(tool.handler({"arguments": {}}))
        assert "Tool error" in res.textResultForLlm
        assert "boom" in res.textResultForLlm

    def test_make_tool_handler_no_arguments_key(self):
        tool = _make_tool("t", "d", lambda args: json.dumps(args))
        res = _run(tool.handler({}))
        assert res.textResultForLlm == "{}"

    def test_make_tool_async_handler(self):
        async def async_handler(args):
            return "async_result"

        tool = _make_tool("t", "d", async_handler)
        res = _run(tool.handler({"arguments": {}}))
        assert res.textResultForLlm == "async_result"

    def test_make_tool_truncates_long_output(self):
        tool = _make_tool("t", "d", lambda args: "x" * 20_000)
        res = _run(tool.handler({"arguments": {}}))
        assert res.textResultForLlm.endswith("... (truncated)")


# ---------------------------------------------------------------------------
# Tests: build_get_summary
# ---------------------------------------------------------------------------

class TestBuildGetSummary:
    def test_no_data(self):
        app = MagicMock()
        app.current_data = None
        tool = _build_get_summary(app)
        res = _run(tool.handler({"arguments": {}}))
        assert "No data loaded" in res.textResultForLlm

    @patch("sfi_reporter.copilot_tools.json.dumps", wraps=json.dumps)
    def test_with_data(self, _mock_dumps):
        items = [
            {**SAMPLE_ITEM, "SlaType": "OutOfSla", "EtaDate": ""},
            {**SAMPLE_ITEM, "id": "AI-002", "SlaType": "InSla", "EtaDate": "2026-06-01"},
        ]
        svc_stats = {"svc-1": {"name": "MyService", "count": 2, "sla": 1, "invalid_eta": 1}}
        pgm_stats = {"ProgramA": {"count": 2, "sla": 1, "invalid_eta": 1}}
        app = make_mock_app(items=items, service_stats=svc_stats, program_stats=pgm_stats)

        with patch("sfi_reporter.data.is_invalid_eta", side_effect=lambda d: d == ""):
            tool = _build_get_summary(app)
            res = _run(tool.handler({"arguments": {}}))
            data = json.loads(res.textResultForLlm)
            assert data["total_items"] == 2
            assert data["out_of_sla"] == 1
            assert data["invalid_eta"] == 1
            assert len(data["services"]) == 1
            assert len(data["programs"]) == 1


# ---------------------------------------------------------------------------
# Tests: build_search_items
# ---------------------------------------------------------------------------

class TestBuildSearchItems:
    def test_no_data(self):
        app = make_mock_app()
        tool = _build_search_items(app)
        res = _run(tool.handler({"arguments": {"query": "foo"}}))
        assert "No data loaded" in res.textResultForLlm

    def test_search_by_query(self):
        app = make_mock_app(items=[SAMPLE_ITEM])
        tool = _build_search_items(app)
        res = _run(tool.handler({"arguments": {"query": "vulnerability"}}))
        data = json.loads(res.textResultForLlm)
        assert data["count"] == 1

    def test_search_no_match(self):
        app = make_mock_app(items=[SAMPLE_ITEM])
        tool = _build_search_items(app)
        res = _run(tool.handler({"arguments": {"query": "zzzzz"}}))
        data = json.loads(res.textResultForLlm)
        assert data["count"] == 0

    def test_search_sla_filter(self):
        item_in_sla = {**SAMPLE_ITEM, "id": "AI-002", "SlaType": "InSla"}
        app = make_mock_app(items=[SAMPLE_ITEM, item_in_sla])
        tool = _build_search_items(app)
        res = _run(tool.handler({"arguments": {"query": "", "sla_filter": "OutOfSla"}}))
        data = json.loads(res.textResultForLlm)
        assert data["count"] == 1
        assert data["items"][0]["id"] == "AI-001"

    def test_search_limit(self):
        items = [{**SAMPLE_ITEM, "id": f"AI-{i:03d}"} for i in range(50)]
        app = make_mock_app(items=items)
        tool = _build_search_items(app)
        res = _run(tool.handler({"arguments": {"query": "", "limit": 5}}))
        data = json.loads(res.textResultForLlm)
        assert data["count"] == 5

    def test_search_empty_query_returns_all(self):
        app = make_mock_app(items=[SAMPLE_ITEM])
        tool = _build_search_items(app)
        res = _run(tool.handler({"arguments": {"query": ""}}))
        data = json.loads(res.textResultForLlm)
        assert data["count"] == 1


# ---------------------------------------------------------------------------
# Tests: build_get_item_detail
# ---------------------------------------------------------------------------

class TestBuildGetItemDetail:
    def test_found(self):
        app = make_mock_app(items=[SAMPLE_ITEM])
        tool = _build_get_item_detail(app)
        res = _run(tool.handler({"arguments": {"item_id": "AI-001"}}))
        data = json.loads(res.textResultForLlm)
        assert data["id"] == "AI-001"
        assert data["title"] == "Fix vulnerability"
        # Private keys (starting with _) should be excluded
        assert "_kpi_name" not in data
        assert "_kpi_id" not in data

    def test_not_found(self):
        app = make_mock_app(items=[SAMPLE_ITEM])
        tool = _build_get_item_detail(app)
        res = _run(tool.handler({"arguments": {"item_id": "NOPE"}}))
        assert "not found" in res.textResultForLlm


# ---------------------------------------------------------------------------
# Tests: build_list_services
# ---------------------------------------------------------------------------

class TestBuildListServices:
    def test_no_data(self):
        app = make_mock_app()
        tool = _build_list_services(app)
        res = _run(tool.handler({"arguments": {}}))
        assert "No service data" in res.textResultForLlm

    def test_with_services(self):
        svc_stats = {
            "svc-1": {"name": "Alpha", "count": 10, "sla": 2, "invalid_eta": 1},
            "svc-2": {"name": "Beta", "count": 5, "sla": 0, "invalid_eta": 0},
        }
        app = make_mock_app(service_stats=svc_stats)
        tool = _build_list_services(app)
        res = _run(tool.handler({"arguments": {}}))
        data = json.loads(res.textResultForLlm)
        assert len(data) == 2
        # Sorted by total desc
        assert data[0]["name"] == "Alpha"
        assert data[1]["name"] == "Beta"


# ---------------------------------------------------------------------------
# Tests: build_items_for_service
# ---------------------------------------------------------------------------

class TestBuildItemsForService:
    def test_partial_match(self):
        app = make_mock_app(items=[SAMPLE_ITEM])
        tool = _build_items_for_service(app)
        res = _run(tool.handler({"arguments": {"service_name": "myser"}}))
        data = json.loads(res.textResultForLlm)
        assert data["count"] == 1

    def test_no_match(self):
        app = make_mock_app(items=[SAMPLE_ITEM])
        tool = _build_items_for_service(app)
        res = _run(tool.handler({"arguments": {"service_name": "zzz"}}))
        data = json.loads(res.textResultForLlm)
        assert data["count"] == 0


# ---------------------------------------------------------------------------
# Tests: build_update_eta
# ---------------------------------------------------------------------------

class TestBuildUpdateEta:
    def _invoke(self, app, args):
        tool = _build_update_eta(app)
        return _run(tool.handler({"arguments": args}))

    def test_item_not_found(self):
        app = make_mock_app()
        res = self._invoke(app, {"item_id": "NOPE", "new_eta": "2026-06-01"})
        assert "not found" in res.textResultForLlm

    @patch("sfi_reporter.eta_logic.validate_eta_date", return_value=(False, "bad date"))
    def test_invalid_date(self, _mock_validate):
        app = make_mock_app(items=[SAMPLE_ITEM])
        res = self._invoke(app, {"item_id": "AI-001", "new_eta": "not-a-date"})
        assert "Invalid ETA date" in res.textResultForLlm

    @patch("sfi_reporter.data.get_current_user_alias", return_value="testuser")
    @patch("sfi_reporter.data.get_client")
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.eta_logic.validate_eta_date", return_value=(True, ""))
    def test_api_error(self, _v, _b, mock_client, _u):
        mock_client.return_value.save_etas.side_effect = RuntimeError("timeout")
        app = make_mock_app(items=[SAMPLE_ITEM])
        res = self._invoke(app, {"item_id": "AI-001", "new_eta": "2026-06-01"})
        assert "API error" in res.textResultForLlm

    @patch("sfi_reporter.data.is_invalid_eta", return_value=False)
    @patch("sfi_reporter.data.get_current_user_alias", return_value="testuser")
    @patch("sfi_reporter.data.get_client")
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.eta_logic.validate_eta_date", return_value=(True, ""))
    def test_save_failure(self, _v, _b, mock_client, _u, _inv):
        result_obj = MagicMock()
        result_obj.success = False
        result_obj.error_message = "Server error"
        result_obj.failed_items = []
        mock_client.return_value.save_etas.return_value = result_obj
        app = make_mock_app(items=[SAMPLE_ITEM])
        res = self._invoke(app, {"item_id": "AI-001", "new_eta": "2026-06-01"})
        assert "Save failed" in res.textResultForLlm

    @patch("sfi_reporter.data.is_invalid_eta", return_value=False)
    @patch("sfi_reporter.data.get_current_user_alias", return_value="testuser")
    @patch("sfi_reporter.data.get_client")
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.eta_logic.validate_eta_date", return_value=(True, ""))
    def test_success(self, _v, _b, mock_client, _u, _inv):
        result_obj = MagicMock()
        result_obj.success = True
        mock_client.return_value.save_etas.return_value = result_obj

        item = {**SAMPLE_ITEM}
        svc_stats = {"svc-1": {"name": "MyService", "count": 1, "sla": 1, "invalid_eta": 1}}
        kpi_stats = {"kpi-a": {"name": "KPI-A", "count": 1, "sla": 0, "invalid_eta": 1}}
        pgm_stats = {"ProgramA": {"count": 1, "sla": 0, "invalid_eta": 1}}
        app = make_mock_app(items=[item], service_stats=svc_stats, program_stats=pgm_stats)
        app.current_data["kpi_stats"] = kpi_stats
        app.current_data["programs_lookup"] = {"pgm-1": "ProgramA"}

        res = self._invoke(app, {"item_id": "AI-001", "new_eta": "2026-06-01", "notes": "On track"})
        assert "updated to 2026-06-01" in res.textResultForLlm
        # In-memory item should be updated
        assert item["EtaDate"] == "2026-06-01"
        assert item["EtaStatus"] == "On track"

    @patch("sfi_reporter.data.is_invalid_eta", return_value=False)
    @patch("sfi_reporter.data.get_current_user_alias", return_value="testuser")
    @patch("sfi_reporter.data.get_client")
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.eta_logic.validate_eta_date", return_value=(True, ""))
    def test_save_failure_with_failed_items(self, _v, _b, mock_client, _u, _inv):
        result_obj = MagicMock()
        result_obj.success = False
        result_obj.error_message = ""
        result_obj.failed_items = ["AI-001"]
        mock_client.return_value.save_etas.return_value = result_obj
        app = make_mock_app(items=[SAMPLE_ITEM])
        res = self._invoke(app, {"item_id": "AI-001", "new_eta": "2026-06-01"})
        assert "Save failed" in res.textResultForLlm
        assert "AI-001" in res.textResultForLlm


# ---------------------------------------------------------------------------
# Tests: build_web_fetch
# ---------------------------------------------------------------------------

class TestBuildWebFetch:
    def _invoke(self, args):
        tool = _build_web_fetch()
        return _run(tool.handler({"arguments": args}))

    def test_empty_url(self):
        res = self._invoke({"url": ""})
        assert "required" in res.textResultForLlm.lower()

    def test_non_http_url(self):
        res = self._invoke({"url": "ftp://example.com"})
        assert "http" in res.textResultForLlm.lower()

    @patch("sfi_reporter.kpi_analyzer._is_login_page", return_value=False)
    @patch("sfi_reporter.kpi_analyzer.fetch_url_content")
    def test_success(self, mock_fetch, _mock_login):
        mock_fetch.return_value = {
            "content": "Hello world",
            "error": "",
            "method": "urllib",
            "discovered_urls": ["https://example.com/page2"],
        }
        res = self._invoke({"url": "https://example.com"})
        assert "Hello world" in res.textResultForLlm
        assert "Discovered links" in res.textResultForLlm

    @patch("sfi_reporter.kpi_analyzer._is_login_page", return_value=True)
    @patch("sfi_reporter.kpi_analyzer.fetch_url_content")
    def test_login_page(self, mock_fetch, _mock_login):
        mock_fetch.return_value = {
            "content": "<html>Login</html>",
            "error": "",
            "method": "urllib",
            "discovered_urls": [],
        }
        res = self._invoke({"url": "https://example.com"})
        assert "Authentication wall" in res.textResultForLlm

    @patch("sfi_reporter.kpi_analyzer._is_login_page", return_value=False)
    @patch("sfi_reporter.kpi_analyzer.fetch_url_content")
    def test_fetch_error(self, mock_fetch, _mock_login):
        mock_fetch.return_value = {
            "content": "",
            "error": "Connection refused",
            "method": "urllib",
            "discovered_urls": [],
        }
        res = self._invoke({"url": "https://example.com"})
        assert "Failed to fetch" in res.textResultForLlm

    @patch("sfi_reporter.kpi_analyzer._is_login_page", return_value=False)
    @patch("sfi_reporter.kpi_analyzer.fetch_url_content")
    def test_no_content(self, mock_fetch, _mock_login):
        mock_fetch.return_value = {
            "content": "",
            "error": "",
            "method": "urllib",
            "discovered_urls": [],
        }
        res = self._invoke({"url": "https://example.com"})
        assert "No content" in res.textResultForLlm


# ---------------------------------------------------------------------------
# Tests: build_read_fetched_doc
# ---------------------------------------------------------------------------

class TestBuildReadFetchedDoc:
    def _invoke(self, args):
        tool = _build_read_fetched_doc()
        return _run(tool.handler({"arguments": args}))

    def test_empty_filename(self):
        res = self._invoke({"filename": ""})
        assert "required" in res.textResultForLlm.lower()

    def test_no_docs_dir(self):
        set_current_docs_dir("")
        res = self._invoke({"filename": "readme.txt"})
        assert "No docs directory" in res.textResultForLlm

    def test_path_traversal_dotdot(self):
        set_current_docs_dir("/tmp/docs")
        res = self._invoke({"filename": "../etc/passwd"})
        assert "plain filename" in res.textResultForLlm

    def test_path_traversal_slash(self):
        set_current_docs_dir("/tmp/docs")
        res = self._invoke({"filename": "subdir/file.txt"})
        assert "plain filename" in res.textResultForLlm

    def test_file_not_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            set_current_docs_dir(tmpdir)
            # Create one file so the "available" list is populated
            with open(os.path.join(tmpdir, "other.txt"), "w") as f:
                f.write("stuff")
            res = self._invoke({"filename": "nope.txt"})
            assert "not found" in res.textResultForLlm.lower()
            assert "other.txt" in res.textResultForLlm

    def test_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            set_current_docs_dir(tmpdir)
            filepath = os.path.join(tmpdir, "doc.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("Document content here")
            res = self._invoke({"filename": "doc.txt"})
            assert res.textResultForLlm == "Document content here"


# ---------------------------------------------------------------------------
# Tests: set_current_docs_dir
# ---------------------------------------------------------------------------

class TestSetCurrentDocsDir:
    def test_set_and_use(self):
        set_current_docs_dir("/some/path")
        # We verify the module-level var changed by building a tool and checking behavior
        import sfi_reporter.copilot_tools as ct

        assert ct._current_docs_dir == "/some/path"
        set_current_docs_dir("")  # reset


# ---------------------------------------------------------------------------
# Tests: build_tools
# ---------------------------------------------------------------------------

class TestBuildTools:
    def test_returns_eight_tools(self):
        app = make_mock_app()
        tools = build_tools(app)
        assert len(tools) == 8

    def test_tool_names(self):
        app = make_mock_app()
        tools = build_tools(app)
        names = {t.name for t in tools}
        assert names == {
            "get_summary",
            "search_items",
            "get_item_detail",
            "list_services",
            "items_for_service",
            "update_eta",
            "web_fetch",
            "read_fetched_doc",
        }


# ---------------------------------------------------------------------------
# Tests: SYSTEM_MESSAGE
# ---------------------------------------------------------------------------

class TestSystemMessage:
    def test_non_empty(self):
        assert isinstance(SYSTEM_MESSAGE, str)
        assert len(SYSTEM_MESSAGE) > 100

    def test_contains_tool_names(self):
        for name in ("get_summary", "search_items", "update_eta", "web_fetch", "read_fetched_doc"):
            assert name in SYSTEM_MESSAGE


# ---------------------------------------------------------------------------
# Tests: MAX_RESULT_LEN
# ---------------------------------------------------------------------------

class TestMaxResultLen:
    def test_value(self):
        assert _MAX_RESULT_LEN == 8_000
