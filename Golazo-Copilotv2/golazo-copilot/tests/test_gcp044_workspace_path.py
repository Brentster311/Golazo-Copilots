"""Tests for GCP-0044: workspace_path required on all MCP tools."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.server import list_tools, call_tool, resolve_work_items_dir


# ---------------------------------------------------------------------------
# TC1: Schema Validation
# ---------------------------------------------------------------------------
class TestSchemaRequiresWorkspacePath:
    """TC1.1: All tool schemas include workspace_path in required."""

    @pytest.mark.asyncio
    async def test_all_tools_require_workspace_path(self):
        """Every tool schema must list workspace_path as required."""
        tools = await list_tools()
        assert len(tools) == 7, f"Expected 7 tools, got {len(tools)}"
        for tool in tools:
            required = tool.inputSchema.get("required", [])
            assert "workspace_path" in required, (
                f"Tool '{tool.name}' does not include workspace_path in required params"
            )


# ---------------------------------------------------------------------------
# TC2: Runtime Validation — Missing workspace_path
# ---------------------------------------------------------------------------
class TestRuntimeMissingWorkspacePath:
    """TC2.1–TC2.3: Missing workspace_path returns clear error."""

    @pytest.mark.asyncio
    async def test_create_workitem_without_workspace_path(self):
        """golazo_create_workitem should fail when workspace_path is missing."""
        result = await call_tool("golazo_create_workitem", {"work_item_id": "TST-001"})
        text = result[0].text
        assert "workspace_path" in text.lower() or "workspace_path is required" in text, (
            f"golazo_create_workitem should fail when workspace_path is missing, got: {text}"
        )

    @pytest.mark.asyncio
    async def test_transition_without_workspace_path(self):
        """golazo_transition should fail when workspace_path is missing."""
        result = await call_tool("golazo_transition", {
            "work_item_id": "TST-001",
            "role": "program-manager"
        })
        text = result[0].text
        assert "workspace_path" in text.lower() or "workspace_path is required" in text, (
            f"golazo_transition should fail when workspace_path is missing, got: {text}"
        )

    @pytest.mark.asyncio
    async def test_bootstrap_without_workspace_path(self):
        """golazo_bootstrap should fail when workspace_path is missing."""
        result = await call_tool("golazo_bootstrap", {})
        text = result[0].text
        assert "workspace_path" in text.lower() or "workspace_path is required" in text, (
            f"golazo_bootstrap should fail when workspace_path is missing, got: {text}"
        )


# ---------------------------------------------------------------------------
# TC3: resolve_work_items_dir Unit Tests
# ---------------------------------------------------------------------------
class TestResolveWorkItemsDir:
    """TC3.1–TC3.3: resolve_work_items_dir validation."""

    def test_none_raises_value_error(self):
        """resolve_work_items_dir(None) should raise ValueError, not fall back to cwd."""
        with pytest.raises(ValueError, match="(?i)workspace_path"):
            resolve_work_items_dir(None)

    def test_empty_string_raises_value_error(self):
        """resolve_work_items_dir('') should raise ValueError."""
        with pytest.raises(ValueError, match="(?i)workspace_path"):
            resolve_work_items_dir("")

    def test_valid_path_resolves_correctly(self):
        """Valid workspace_path should resolve to WorkItems subdirectory."""
        result = resolve_work_items_dir("C:\\my\\workspace")
        assert result == Path("C:\\my\\workspace\\WorkItems").resolve()
