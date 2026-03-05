"""Additional dispatch coverage for handlers/tools branches."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot import server
from golazo_copilot.dispatch import router


@pytest.mark.asyncio
async def test_dispatch_transition_workitem_branch(monkeypatch, tmp_path):
    workspace = tmp_path
    (workspace / "WorkItems").mkdir()
    agents = workspace / ".github" / "agents"
    agents.mkdir(parents=True)
    (agents / "Golazo-Copilot.md").write_text("# ok", encoding="utf-8")

    handler_globals = router.handle_registered_tool.__globals__

    async def fake_transition_workitem(*, work_item_id, work_items_dir):
        assert work_item_id == "GCP-9010"
        assert work_items_dir == (workspace / "WorkItems").resolve()
        return {"success": True, "message": "done"}

    monkeypatch.setitem(handler_globals, "golazo_transition_workitem", fake_transition_workitem)
    monkeypatch.setitem(handler_globals, "format_transition_workitem_result", lambda result: result["message"])

    result = await server._dispatch_tool(
        "golazo_transition_workitem",
        {"workspace_path": str(workspace), "work_item_id": "GCP-9010"},
    )
    assert result[0].text == "done"


@pytest.mark.asyncio
async def test_dispatch_status_includes_startup_warnings(monkeypatch, tmp_path):
    workspace = tmp_path
    (workspace / "WorkItems").mkdir()
    agents = workspace / ".github" / "agents"
    agents.mkdir(parents=True)
    (agents / "Golazo-Copilot.md").write_text("# ok", encoding="utf-8")

    handler_globals = router.handle_registered_tool.__globals__

    async def fake_status(*, work_item_id, work_items_dir):
        assert work_item_id == "GCP-9011"
        return {
            "active": True,
            "version": "x",
            "work_item_id": "GCP-9011",
            "current_role": "developer",
            "current_phase": "development",
            "next_steps": ["n1"],
            "role_instructions": "ri",
            "deviations": [],
        }

    monkeypatch.setitem(handler_globals, "golazo_status", fake_status)

    result = await server._dispatch_tool(
        "golazo_status",
        {"workspace_path": str(workspace), "work_item_id": "GCP-9011"},
        ["warn-x"],
    )
    text = result[0].text
    assert "Tooling self-check warnings" in text
    assert "warn-x" in text
