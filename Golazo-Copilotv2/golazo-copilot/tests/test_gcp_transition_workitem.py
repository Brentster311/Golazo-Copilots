"""Tests for golazo_transition_workitem project-level sequencing behavior."""

import json
import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.core.persistence import load_state, save_state
from golazo_copilot.tools.golazo_create_workitem import golazo_create_workitem
from golazo_copilot.tools.golazo_transition_workitem import golazo_transition_workitem


TEST_ROOT = Path(__file__).parent / "test-transition-workitem"
TEST_WORKITEMS_DIR = TEST_ROOT / "WorkItems"
GLOBAL_STATE_PATH = TEST_ROOT / "global_state.json"


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up transition-workitem test directory before/after each test."""
    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)
    yield
    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)


async def _create_work_item(work_item_id: str):
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    result = await golazo_create_workitem(
        work_item_id=work_item_id,
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    assert result["success"] is True


def _set_role(work_item_id: str, role: str, phase: str = "completion"):
    state = load_state(work_item_id, TEST_WORKITEMS_DIR)
    state.current_role = role
    state.current_phase = phase
    save_state(work_item_id, state, TEST_WORKITEMS_DIR)


@pytest.mark.asyncio
async def test_transition_workitem_succeeds_from_retrospective_and_returns_next_id():
    await _create_work_item("GCP-0061")
    _set_role("GCP-0061", "retrospective")

    result = await golazo_transition_workitem(
        work_item_id="GCP-0061",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is True
    assert result["completed_work_item"] == "GCP-0061"
    assert result["next_work_item"] == "GCP-0062"


@pytest.mark.asyncio
async def test_transition_workitem_fails_when_not_retrospective():
    await _create_work_item("GCP-0061")
    _set_role("GCP-0061", "builder")

    result = await golazo_transition_workitem(
        work_item_id="GCP-0061",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is False
    assert result["error_code"] == "role_precondition_failed"
    assert result["current_role"] == "builder"


@pytest.mark.asyncio
async def test_transition_workitem_creates_global_state_when_missing():
    await _create_work_item("GCP-0061")
    _set_role("GCP-0061", "retrospective")

    result = await golazo_transition_workitem(
        work_item_id="GCP-0061",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is True
    assert result["global_state_created"] is True
    assert GLOBAL_STATE_PATH.exists()

    global_state = json.loads(GLOBAL_STATE_PATH.read_text(encoding="utf-8"))
    assert global_state["schema_version"] == "1.0"
    assert global_state["next_work_item"] == "GCP-0062"
    assert "created_at" in global_state
    assert "updated_at" in global_state


@pytest.mark.asyncio
async def test_transition_workitem_updates_existing_global_state():
    await _create_work_item("GCP-0061")
    _set_role("GCP-0061", "retrospective")

    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    GLOBAL_STATE_PATH.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "created_at": "2026-01-01T00:00:00.000Z",
                "updated_at": "2026-01-01T00:00:00.000Z",
                "completed_work_items": ["GCP-0060"],
                "next_work_item": "GCP-0061",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = await golazo_transition_workitem(
        work_item_id="GCP-0061",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is True
    assert result["global_state_created"] is False

    global_state = json.loads(GLOBAL_STATE_PATH.read_text(encoding="utf-8"))
    assert "GCP-0061" in global_state["completed_work_items"]
    assert global_state["next_work_item"] == "GCP-0062"


@pytest.mark.asyncio
async def test_transition_workitem_guides_creation_when_next_missing():
    await _create_work_item("GCP-0061")
    _set_role("GCP-0061", "retrospective")

    result = await golazo_transition_workitem(
        work_item_id="GCP-0061",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is True
    assert result["next_work_item_exists"] is False
    assert "golazo_create_workitem" in result["message"]


@pytest.mark.asyncio
async def test_transition_workitem_is_idempotent_for_completed_list():
    await _create_work_item("GCP-0061")
    _set_role("GCP-0061", "retrospective")

    first = await golazo_transition_workitem(
        work_item_id="GCP-0061",
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    second = await golazo_transition_workitem(
        work_item_id="GCP-0061",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert first["success"] is True
    assert second["success"] is True
    global_state = json.loads(GLOBAL_STATE_PATH.read_text(encoding="utf-8"))
    assert global_state["completed_work_items"].count("GCP-0061") == 1