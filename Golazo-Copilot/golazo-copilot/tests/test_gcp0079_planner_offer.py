"""Planner-first creation contract tests for GCP-0079."""

import importlib
import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.core.persistence import load_state
from golazo_copilot.dispatch.registry import get_tool_definitions
from golazo_copilot.handlers import tools as tool_handlers
from golazo_copilot.tools.golazo_bootstrap import golazo_bootstrap
from golazo_copilot.tools.golazo_create_workitem import golazo_create_workitem

bootstrap_module = importlib.import_module("golazo_copilot.tools.golazo_bootstrap")


@pytest.mark.asyncio
async def test_first_complete_work_item_can_start_in_planner(tmp_path: Path):
    work_items = tmp_path / "WorkItems"

    result = await golazo_create_workitem(
        work_item_id="NEW-001",
        profile="complete",
        initial_role="planner",
        work_items_dir=work_items,
    )

    assert result["success"] is True
    assert result["current_role"] == "planner"
    assert "# Role: Planner" in result["role_instructions"]
    state = load_state("NEW-001", work_items)
    assert state.current_role == "planner"
    assert [entry.role for entry in state.role_history] == ["planner"]


@pytest.mark.asyncio
async def test_omitted_initial_role_preserves_poa_default(tmp_path: Path):
    work_items = tmp_path / "WorkItems"

    result = await golazo_create_workitem("NEW-002", work_items_dir=work_items)

    assert result["success"] is True
    assert result["current_role"] == "project-owner-assistant"


@pytest.mark.asyncio
@pytest.mark.parametrize("profile", ["express", "spike"])
async def test_planner_initial_role_requires_complete_profile(tmp_path: Path, profile: str):
    work_items = tmp_path / "WorkItems"

    result = await golazo_create_workitem(
        "NEW-003",
        profile=profile,
        initial_role="planner",
        work_items_dir=work_items,
    )

    assert result["success"] is False
    assert "complete" in result["error"].lower()
    assert not (work_items / "NEW-003" / "state.json").exists()
    assert not (tmp_path / "capabilities.yaml").exists()


@pytest.mark.asyncio
async def test_planner_initial_role_requires_first_work_item(tmp_path: Path):
    work_items = tmp_path / "WorkItems"
    await golazo_create_workitem("OLD-001", work_items_dir=work_items)

    result = await golazo_create_workitem(
        "NEW-004",
        initial_role="planner",
        work_items_dir=work_items,
    )

    assert result["success"] is False
    assert "first work item" in result["error"].lower()
    assert not (work_items / "NEW-004" / "state.json").exists()


@pytest.mark.asyncio
async def test_non_state_workspace_files_do_not_block_planner(tmp_path: Path):
    work_items = tmp_path / "WorkItems"
    (work_items / "notes").mkdir(parents=True)
    (work_items / "capabilities.yaml").write_text("capabilities: []\n", encoding="utf-8")
    (tmp_path / "global_state.json").write_text("{}\n", encoding="utf-8")

    result = await golazo_create_workitem(
        "NEW-005",
        initial_role="planner",
        work_items_dir=work_items,
    )

    assert result["success"] is True
    assert result["current_role"] == "planner"


@pytest.mark.asyncio
async def test_nested_state_file_does_not_block_planner(tmp_path: Path):
    work_items = tmp_path / "WorkItems"
    nested = work_items / "fixtures" / "archived"
    nested.mkdir(parents=True)
    (nested / "state.json").write_text("{}\n", encoding="utf-8")

    result = await golazo_create_workitem(
        "NEW-009",
        initial_role="planner",
        work_items_dir=work_items,
    )

    assert result["success"] is True
    assert result["current_role"] == "planner"


@pytest.mark.asyncio
async def test_direct_tool_rejects_unknown_initial_role(tmp_path: Path):
    result = await golazo_create_workitem(
        "NEW-006",
        initial_role="developer",
        work_items_dir=tmp_path / "WorkItems",
    )

    assert result["success"] is False
    assert "initial_role" in result["error"]


def test_registered_schema_exposes_optional_initial_role():
    create_tool = next(tool for tool in get_tool_definitions() if tool.name == "golazo_create_workitem")
    initial_role = create_tool.input_schema["properties"]["initial_role"]

    assert initial_role["enum"] == ["project-owner-assistant", "planner"]
    assert initial_role["default"] == "project-owner-assistant"
    assert "initial_role" not in create_tool.input_schema["required"]


@pytest.mark.asyncio
async def test_registered_handler_forwards_initial_role(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    captured: dict = {}

    async def fake_create_workitem(**kwargs):
        captured.update(kwargs)
        return {
            "success": True,
            "work_item_id": "NEW-007",
            "current_role": "planner",
            "role_instructions": "planner",
        }

    monkeypatch.setattr(tool_handlers, "golazo_create_workitem", fake_create_workitem)
    await tool_handlers.handle_registered_tool(
        "golazo_create_workitem",
        {
            "workspace_path": str(tmp_path),
            "work_item_id": "NEW-007",
            "profile": "complete",
            "initial_role": "planner",
        },
        [],
    )

    assert captured["initial_role"] == "planner"


@pytest.mark.asyncio
async def test_bootstrap_and_readme_offer_planner_before_first_creation(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'fixture'\n", encoding="utf-8")
    result = await golazo_bootstrap(workspace_path=tmp_path, mode="orchestrator-only")
    assert result["success"] is True
    deployed = (tmp_path / ".github" / "agents" / "Golazo-Copilot.md").read_text(encoding="utf-8")
    packaged = (Path(__file__).parent.parent / "src" / "golazo_copilot" / "bootstrap-instructions.md").read_text(encoding="utf-8")
    fallback_source = inspect.getsource(bootstrap_module._get_default_instructions)
    readme = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")

    for content in (deployed, packaged, fallback_source, readme):
        assert "initial_role=\"planner\"" in content
        assert "first work item" in content.lower()
        assert "offer" in content.lower()


@pytest.mark.asyncio
async def test_existing_item_error_does_not_reference_missing_switch_tool(tmp_path: Path):
    work_items = tmp_path / "WorkItems"
    await golazo_create_workitem("NEW-008", work_items_dir=work_items)

    result = await golazo_create_workitem("NEW-008", work_items_dir=work_items)

    assert result["success"] is False
    assert "golazo_switch" not in result["error"]
    assert "work_item_id" in result["error"]