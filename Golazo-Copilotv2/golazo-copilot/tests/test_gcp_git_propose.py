"""Tests for GCP-0060: golazo_git_propose proposal-gated git intent capture."""

import json
import re
import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.core.persistence import load_state, save_state
from golazo_copilot.tools.golazo_consent import golazo_consent
from golazo_copilot.tools.golazo_create_workitem import golazo_create_workitem
from golazo_copilot.tools.golazo_git_propose import golazo_git_propose


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)


async def _create_work_item(work_item_id: str = "GP-001"):
    result = await golazo_create_workitem(
        work_item_id=work_item_id,
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    assert result["success"] is True


def _remove_git_actions_field(work_item_id: str):
    state_path = TEST_WORKITEMS_DIR / work_item_id / "state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload.pop("git_actions", None)
    state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _utc_iso8601_z(ts: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", ts))


@pytest.mark.asyncio
async def test_git_propose_initializes_git_actions_for_legacy_state():
    """TC-001: legacy state missing git_actions is initialized on first propose."""
    await _create_work_item("GP-001")
    _remove_git_actions_field("GP-001")

    result = await golazo_git_propose(
        work_item_id="GP-001",
        action="add",
        files=["a.txt"],
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is True
    state = load_state("GP-001", TEST_WORKITEMS_DIR)
    assert isinstance(state.git_actions, list), (
        "Expected legacy state to initialize 'git_actions' as list on first proposal."
    )
    assert len(state.git_actions) == 1


@pytest.mark.asyncio
async def test_git_propose_schema_valid_roundtrip_after_initialization():
    """TC-002: initialized git_actions survives standard load/save round-trip."""
    await _create_work_item("GP-002")
    _remove_git_actions_field("GP-002")

    result = await golazo_git_propose(
        work_item_id="GP-002",
        action="add",
        files=["a.txt"],
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    assert result["success"] is True

    state = load_state("GP-002", TEST_WORKITEMS_DIR)
    save_state("GP-002", state, TEST_WORKITEMS_DIR)
    reloaded = load_state("GP-002", TEST_WORKITEMS_DIR)

    assert isinstance(reloaded.git_actions, list), (
        "Expected schema-valid state after load/save round-trip with initialized 'git_actions'."
    )
    assert len(reloaded.git_actions) == 1


@pytest.mark.asyncio
async def test_git_propose_add_persists_required_fields():
    """TC-003: add action appends action/status/timestamp/files."""
    await _create_work_item("GP-003")

    result = await golazo_git_propose(
        work_item_id="GP-003",
        action="add",
        files=["src/a.py", "README.md"],
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    assert result["success"] is True

    state = load_state("GP-003", TEST_WORKITEMS_DIR)
    entry = state.git_actions[-1]

    assert entry["action"] == "add"
    assert "status" in entry
    assert "timestamp" in entry
    assert entry["files"] == ["src/a.py", "README.md"], (
        "Expected appended add proposal with action/status/timestamp/files."
    )


@pytest.mark.asyncio
async def test_git_propose_timestamp_utc_iso8601_z():
    """TC-004: persisted timestamp is UTC ISO-8601 with trailing Z."""
    await _create_work_item("GP-004")

    result = await golazo_git_propose(
        work_item_id="GP-004",
        action="add",
        files=["x.txt"],
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    assert result["success"] is True

    state = load_state("GP-004", TEST_WORKITEMS_DIR)
    ts = state.git_actions[-1]["timestamp"]
    assert _utc_iso8601_z(ts), (
        "Expected proposal timestamp in UTC ISO-8601 format with trailing 'Z'."
    )


@pytest.mark.asyncio
async def test_git_propose_commit_requires_message():
    """TC-005: commit without message fails deterministically and does not mutate state."""
    await _create_work_item("GP-005")
    before_count = len(load_state("GP-005", TEST_WORKITEMS_DIR).git_actions)

    result = await golazo_git_propose(
        work_item_id="GP-005",
        action="commit",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is False
    assert result["error_code"] == "parameter_required"
    assert result["parameter"] == "message", (
        "Expected deterministic parameter-required error for missing 'message' on commit."
    )
    after_count = len(load_state("GP-005", TEST_WORKITEMS_DIR).git_actions)
    assert after_count == before_count


@pytest.mark.asyncio
async def test_git_propose_push_requires_branch():
    """TC-006: push without branch fails deterministically and does not mutate state."""
    await _create_work_item("GP-006")
    before_count = len(load_state("GP-006", TEST_WORKITEMS_DIR).git_actions)

    result = await golazo_git_propose(
        work_item_id="GP-006",
        action="push",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is False
    assert result["error_code"] == "parameter_required"
    assert result["parameter"] == "branch", (
        "Expected deterministic parameter-required error for missing 'branch' on push."
    )
    after_count = len(load_state("GP-006", TEST_WORKITEMS_DIR).git_actions)
    assert after_count == before_count


@pytest.mark.asyncio
async def test_git_propose_branch_requires_branch():
    """TC-007: branch action without branch name fails deterministically."""
    await _create_work_item("GP-007")
    before_count = len(load_state("GP-007", TEST_WORKITEMS_DIR).git_actions)

    result = await golazo_git_propose(
        work_item_id="GP-007",
        action="branch",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is False
    assert result["error_code"] == "parameter_required"
    assert result["parameter"] == "branch", (
        "Expected deterministic parameter-required error for missing 'branch' on branch action."
    )
    after_count = len(load_state("GP-007", TEST_WORKITEMS_DIR).git_actions)
    assert after_count == before_count


@pytest.mark.asyncio
async def test_git_propose_missing_workitem_returns_create_guidance():
    """TC-008: missing work item returns deterministic not-found with create guidance."""
    result = await golazo_git_propose(
        work_item_id="GP-999",
        action="add",
        files=["a.txt"],
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    assert result["success"] is False
    assert result["error_code"] == "workitem_not_found"
    assert "golazo_create_workitem" in result["error"], (
        "Expected not-found error with explicit create-work-item guidance."
    )


@pytest.mark.asyncio
async def test_git_propose_append_only_history():
    """TC-009: prior proposal entries remain unchanged and new entry appends at tail."""
    await _create_work_item("GP-009")
    await golazo_git_propose(
        work_item_id="GP-009",
        action="add",
        files=["a.txt"],
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    await golazo_git_propose(
        work_item_id="GP-009",
        action="commit",
        message="first commit",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    before_entries = list(load_state("GP-009", TEST_WORKITEMS_DIR).git_actions)

    result = await golazo_git_propose(
        work_item_id="GP-009",
        action="push",
        branch="main",
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    assert result["success"] is True

    after_entries = load_state("GP-009", TEST_WORKITEMS_DIR).git_actions
    assert after_entries[:-1] == before_entries, (
        "Expected append-only behavior: prior proposal entries must not be mutated or reordered."
    )
    assert after_entries[-1]["action"] == "push"


@pytest.mark.asyncio
async def test_git_propose_persists_across_roundtrip():
    """TC-010: proposal history survives other workflow load/save paths."""
    await _create_work_item("GP-010")

    await golazo_git_propose(
        work_item_id="GP-010",
        action="add",
        files=["x.txt"],
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    before = list(load_state("GP-010", TEST_WORKITEMS_DIR).git_actions)

    consent_result = await golazo_consent(
        work_item_id="GP-010",
        action="custom",
        reason="verify git actions survive workflow roundtrip",
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    assert consent_result["success"] is True

    after = load_state("GP-010", TEST_WORKITEMS_DIR).git_actions
    assert after == before, (
        "Expected 'git_actions' history to persist unchanged across workflow load/save round-trips."
    )