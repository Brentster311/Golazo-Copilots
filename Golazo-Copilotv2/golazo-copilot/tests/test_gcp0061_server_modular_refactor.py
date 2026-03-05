"""GCP-0061 tests: behavior-preserving modular server refactor gates."""

from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot import server


class TestGCP0061ModularBoundaries:

    def test_server_exports_dispatch_from_module(self):
        assert server._dispatch_tool.__module__ == "golazo_copilot.dispatch.router"

    def test_server_exports_formatters_from_module(self):
        assert server.format_status_result.__module__ == "golazo_copilot.formatters.results"


class TestGCP0061ContractParity:

    @pytest.mark.asyncio
    async def test_registered_tool_name_set_is_stable(self):
        tools = await server.list_tools()
        expected = {
            "golazo_create_workitem",
            "golazo_transition",
            "golazo_status",
            "golazo_bootstrap",
            "golazo_consent",
            "golazo_capabilities",
            "golazo_role_context",
            "golazo_git_propose",
            "golazo_transition_workitem",
        }
        actual = {tool.name for tool in tools}
        assert actual == expected

    @pytest.mark.asyncio
    async def test_required_parameter_parity_for_representative_tools(self):
        tools = await server.list_tools()
        tool_map = {t.name: t for t in tools}
        expected_required = {
            "golazo_create_workitem": ["work_item_id", "workspace_path"],
            "golazo_transition": ["work_item_id", "role", "workspace_path"],
            "golazo_status": ["workspace_path"],
            "golazo_bootstrap": ["workspace_path"],
            "golazo_consent": ["work_item_id", "action", "reason", "workspace_path"],
            "golazo_capabilities": ["action", "workspace_path"],
            "golazo_role_context": ["work_item_id", "workspace_path"],
            "golazo_git_propose": ["work_item_id", "action", "workspace_path"],
            "golazo_transition_workitem": ["work_item_id", "workspace_path"],
        }
        for tool_name, required in expected_required.items():
            assert tool_map[tool_name].inputSchema.get("required") == required

    @pytest.mark.asyncio
    async def test_tool_not_found_message_intent_is_stable(self):
        result = await server._dispatch_tool("does_not_exist", {})
        assert result[0].text == "Unknown tool: does_not_exist"

    @pytest.mark.asyncio
    async def test_missing_workspace_error_intent_is_stable(self):
        result = await server._dispatch_tool("golazo_bootstrap", {})
        text = result[0].text
        assert "workspace_path is required" in text

    @pytest.mark.asyncio
    async def test_version_only_status_shape_is_stable(self, tmp_path):
        result = await server._dispatch_tool("golazo_status", {"workspace_path": str(tmp_path)})
        text = result[0].text
        assert text.startswith("**Golazo Copilot**")
