"""Tests for server dispatcher preflight behavior."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.server import ICON_FAIL, ICON_OK, _dispatch_tool


class TestWorkflowPreflight:

    @pytest.mark.asyncio
    async def test_blocks_workflow_tool_when_instructions_missing(self, tmp_path, monkeypatch):
        workspace = tmp_path
        (workspace / "WorkItems").mkdir()
        monkeypatch.setattr("golazo_copilot.dispatch.paths.Path.home", lambda: tmp_path / "clean-home")

        result = await _dispatch_tool(
            "golazo_create_workitem",
            {
                "work_item_id": "GCP-9001",
                "workspace_path": str(workspace),
            },
        )

        text = result[0].text
        assert ICON_FAIL in text
        assert "Orchestrator instructions are required" in text
        assert "mode=\"orchestrator-only\"" in text

    @pytest.mark.asyncio
    async def test_allows_workflow_tool_when_instructions_present(self, tmp_path):
        workspace = tmp_path
        (workspace / "WorkItems").mkdir()
        agents = workspace / ".github" / "agents"
        agents.mkdir(parents=True)
        (agents / "Golazo-Copilot.md").write_text("# Instructions", encoding="utf-8")

        result = await _dispatch_tool(
            "golazo_create_workitem",
            {
                "work_item_id": "GCP-9002",
                "workspace_path": str(workspace),
            },
        )

        text = result[0].text
        assert ICON_OK in text
        assert "created" in text.lower()

    @pytest.mark.asyncio
    async def test_allows_workflow_tool_when_only_user_scope_instructions_present(self, tmp_path, monkeypatch):
        workspace = tmp_path
        (workspace / "WorkItems").mkdir()
        user_home = tmp_path / "user-home"
        monkeypatch.setattr("golazo_copilot.dispatch.paths.Path.home", lambda: user_home)
        agents = user_home / ".copilot" / "agents"
        agents.mkdir(parents=True)
        (agents / "Golazo-Copilot.md").write_text("# Instructions", encoding="utf-8")

        result = await _dispatch_tool(
            "golazo_create_workitem",
            {
                "work_item_id": "GCP-9002",
                "workspace_path": str(workspace),
            },
        )

        text = result[0].text
        assert ICON_OK in text
        assert "created" in text.lower()

    @pytest.mark.asyncio
    async def test_version_only_status_bypasses_preflight(self, tmp_path):
        workspace = tmp_path
        (workspace / "WorkItems").mkdir()

        result = await _dispatch_tool(
            "golazo_status",
            {
                "workspace_path": str(workspace),
            },
        )

        text = result[0].text
        assert "Golazo Copilot" in text
        assert "Orchestrator instructions are required" not in text

    @pytest.mark.asyncio
    async def test_git_propose_blocks_when_instructions_missing(self, tmp_path, monkeypatch):
        workspace = tmp_path
        (workspace / "WorkItems").mkdir()
        monkeypatch.setattr("golazo_copilot.dispatch.paths.Path.home", lambda: tmp_path / "clean-home")

        result = await _dispatch_tool(
            "golazo_git_propose",
            {
                "work_item_id": "GCP-9003",
                "action": "add",
                "files": ["a.txt"],
                "workspace_path": str(workspace),
            },
        )

        text = result[0].text
        assert ICON_FAIL in text
        assert "Orchestrator instructions are required" in text
