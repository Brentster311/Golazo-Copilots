"""Tests for GCP-0074 POA closure project finalization."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.core.persistence import load_state, save_state
from golazo_copilot.core.types import RoleHistoryEntry
from golazo_copilot.dispatch.registry import get_tool_definitions
from golazo_copilot.tools.golazo_create_workitem import golazo_create_workitem
from golazo_copilot.tools.golazo_transition_workitem import golazo_transition_workitem


async def _create_work_item(work_items_dir: Path, work_item_id: str = "GCP-0074") -> None:
    result = await golazo_create_workitem(
        work_item_id=work_item_id,
        work_items_dir=work_items_dir,
    )
    assert result["success"] is True


def _set_closure_state(
    work_items_dir: Path,
    work_item_id: str = "GCP-0074",
    *,
    retrospective_complete: bool = True,
    closure_pending: bool = True,
    story_status: str = "IMPLEMENTED",
    include_poa_note: bool = True,
    include_closure: bool = True,
) -> None:
    now = datetime.now(timezone.utc)
    state = load_state(work_item_id, work_items_dir)
    state.role_history[-1].exited_at = now
    if retrospective_complete:
        state.role_history.append(
            RoleHistoryEntry(role="retrospective", entered_at=now, exited_at=now)
        )
    state.role_history.append(
        RoleHistoryEntry(role="project-owner-assistant", entered_at=now, exited_at=None)
    )
    state.current_role = "project-owner-assistant"
    state.current_phase = "closure"
    state.closure_pending = closure_pending
    save_state(work_item_id, state, work_items_dir)

    work_item_dir = work_items_dir / work_item_id
    (work_item_dir / f"{work_item_id}-User-Story.md").write_text(
        f"# Story\n\n**Status**: {story_status}\n",
        encoding="utf-8",
    )
    if include_poa_note:
        notes_dir = work_item_dir / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / f"{work_item_id}-project-owner-assistant.md").write_text(
            "# POA closure\n",
            encoding="utf-8",
        )
    if include_closure:
        (work_item_dir / f"{work_item_id}-closure.md").write_text(
            "# Closure\n",
            encoding="utf-8",
        )


@pytest.mark.asyncio
async def test_finalizes_completed_poa_closure(tmp_path: Path):
    work_items_dir = tmp_path / "WorkItems"
    await _create_work_item(work_items_dir)
    _set_closure_state(work_items_dir)

    result = await golazo_transition_workitem("GCP-0074", work_items_dir)

    assert result["success"] is True
    assert result["completed_work_item"] == "GCP-0074"
    assert result["next_work_item"] == "GCP-0075"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("role", "closure_pending", "retrospective_complete"),
    [
        ("retrospective", False, True),
        ("project-owner-assistant", False, True),
        ("project-owner-assistant", True, False),
        ("builder", False, False),
    ],
)
async def test_rejects_incomplete_closure_lifecycle(
    tmp_path: Path,
    role: str,
    closure_pending: bool,
    retrospective_complete: bool,
):
    work_items_dir = tmp_path / "WorkItems"
    await _create_work_item(work_items_dir)
    _set_closure_state(
        work_items_dir,
        retrospective_complete=retrospective_complete,
        closure_pending=closure_pending,
    )
    state = load_state("GCP-0074", work_items_dir)
    state.current_role = role
    save_state("GCP-0074", state, work_items_dir)

    result = await golazo_transition_workitem("GCP-0074", work_items_dir)

    assert result["success"] is False
    assert result["error_code"] == "closure_precondition_failed"
    assert not (tmp_path / "global_state.json").exists()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("include_poa_note", "include_closure", "missing_name"),
    [
        (False, True, "project-owner-assistant.md"),
        (True, False, "GCP-0074-closure.md"),
    ],
)
async def test_rejects_missing_closure_evidence(
    tmp_path: Path,
    include_poa_note: bool,
    include_closure: bool,
    missing_name: str,
):
    work_items_dir = tmp_path / "WorkItems"
    await _create_work_item(work_items_dir)
    _set_closure_state(
        work_items_dir,
        include_poa_note=include_poa_note,
        include_closure=include_closure,
    )

    result = await golazo_transition_workitem("GCP-0074", work_items_dir)

    assert result["success"] is False
    assert result["error_code"] == "closure_evidence_missing"
    assert missing_name in result["error"]


@pytest.mark.asyncio
async def test_rejects_story_that_is_not_implemented(tmp_path: Path):
    work_items_dir = tmp_path / "WorkItems"
    await _create_work_item(work_items_dir)
    _set_closure_state(work_items_dir, story_status="IN PROGRESS")

    result = await golazo_transition_workitem("GCP-0074", work_items_dir)

    assert result["success"] is False
    assert result["error_code"] == "closure_status_invalid"
    assert "IMPLEMENTED" in result["error"]


@pytest.mark.asyncio
async def test_closed_work_item_retry_is_idempotent(tmp_path: Path):
    work_items_dir = tmp_path / "WorkItems"
    await _create_work_item(work_items_dir)
    _set_closure_state(work_items_dir)

    first = await golazo_transition_workitem("GCP-0074", work_items_dir)
    second = await golazo_transition_workitem("GCP-0074", work_items_dir)

    assert first["success"] is True
    assert second["success"] is True
    global_state = json.loads((tmp_path / "global_state.json").read_text(encoding="utf-8"))
    assert global_state["completed_work_items"].count("GCP-0074") == 1


def test_transition_workitem_schema_describes_poa_closure():
    tool = next(tool for tool in get_tool_definitions() if tool.name == "golazo_transition_workitem")

    assert "POA closure" in tool.description
    assert "POA closure" in tool.input_schema["properties"]["work_item_id"]["description"]
