"""Tests for GCP-0051: Parallel gcp_status aggregation.

Validates:
- TC-2: Concurrent execution timing
- TC-3: Error isolation — stale files failure
- TC-4: Error isolation — registry hint failure
- TC-5: Error isolation — output validation failure
- TC-7: _generate_next_steps handles error in output_result gracefully
- TC-8: Pure computation operations don't block
"""

import asyncio
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_create_workitem import gcp_create_workitem
from golazo_copilot.tools.gcp_status import (
    gcp_status,
    _get_stale_files,
    _get_registry_hint,
    _compute_role_progress,
    _generate_next_steps,
)

TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"
TEST_WORKSPACE_ROOT = Path(__file__).parent

ALL_ROLES = [
    "project-owner-assistant", "program-manager", "domain-expert",
    "quality-assurance", "architect", "developer", "refactor-expert",
    "builder", "documenter", "retrospective",
]


def create_empty_role_files(workspace_root: Path = TEST_WORKSPACE_ROOT):
    """Create role files with no Required Outputs section for testing."""
    roles_dir = workspace_root / ".github" / "roles"
    roles_dir.mkdir(parents=True, exist_ok=True)
    for role in ALL_ROLES:
        role_file = roles_dir / f"{role}.md"
        role_file.write_text(f"# Role: {role}\n\n## Purpose\nTest role.\n")


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    create_empty_role_files()
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    roles_dir = TEST_WORKSPACE_ROOT / ".github"
    if roles_dir.exists():
        shutil.rmtree(roles_dir)


async def _create_test_work_item(work_item_id: str = "TST-051"):
    """Helper: create a work item for testing."""
    result = await gcp_create_workitem(
        work_item_id=work_item_id,
        work_items_dir=TEST_WORKITEMS_DIR,
    )
    return result


# ---------------------------------------------------------------------------
# TC-2: Concurrent execution timing
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_parallel_execution_faster_than_sequential():
    """Operations run concurrently — total time ≈ max(individual) not sum."""
    await _create_test_work_item()

    delay = 0.1  # 100ms per operation

    original_stale = _get_stale_files
    original_registry = _get_registry_hint
    original_progress = _compute_role_progress

    def slow_stale_files(workspace_root):
        time.sleep(delay)
        return []

    def slow_registry_hint(workspace_root):
        time.sleep(delay)
        return None

    def slow_compute_progress(state):
        time.sleep(delay)
        return original_progress(state)

    with patch(
        "golazo_copilot.tools.gcp_status._get_stale_files", side_effect=slow_stale_files
    ), patch(
        "golazo_copilot.tools.gcp_status._get_registry_hint", side_effect=slow_registry_hint
    ), patch(
        "golazo_copilot.tools.gcp_status._compute_role_progress", side_effect=slow_compute_progress
    ):
        start = time.monotonic()
        result = await gcp_status(
            work_item_id="TST-051",
            work_items_dir=TEST_WORKITEMS_DIR,
        )
        elapsed = time.monotonic() - start

    assert result["active"] is True
    # If 3 operations each take 100ms sequentially = 300ms.
    # If parallel, should be ~100ms. Allow generous margin: < 250ms.
    assert elapsed < 0.25, (
        f"gcp_status took {elapsed:.2f}s — expected <0.25s if operations ran in parallel"
    )


# ---------------------------------------------------------------------------
# TC-3: Error isolation — stale files failure
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_error_isolation_stale_files():
    """Stale file check failure doesn't crash the entire gcp_status call."""
    await _create_test_work_item()

    def exploding_stale_files(workspace_root):
        raise RuntimeError("disk read failed")

    with patch(
        "golazo_copilot.tools.gcp_status._get_stale_files", side_effect=exploding_stale_files
    ):
        result = await gcp_status(
            work_item_id="TST-051",
            work_items_dir=TEST_WORKITEMS_DIR,
        )

    assert result["active"] is True, (
        "gcp_status should not fail entirely when stale-file check fails"
    )
    # Other fields should still be populated
    assert "required_outputs" in result
    assert "role_progress" in result
    assert "next_steps" in result


# ---------------------------------------------------------------------------
# TC-4: Error isolation — registry hint failure
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_error_isolation_registry_hint():
    """Registry hint failure doesn't block other status operations."""
    await _create_test_work_item()

    def exploding_registry(workspace_root):
        raise Exception("parse fail")

    with patch(
        "golazo_copilot.tools.gcp_status._get_registry_hint", side_effect=exploding_registry
    ):
        result = await gcp_status(
            work_item_id="TST-051",
            work_items_dir=TEST_WORKITEMS_DIR,
        )

    assert result["active"] is True, (
        "Registry hint failure should not block other status operations"
    )
    assert "required_outputs" in result
    assert "role_progress" in result


# ---------------------------------------------------------------------------
# TC-5: Error isolation — output validation failure
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_error_isolation_output_validation():
    """Output validation crash doesn't kill the whole status call."""
    await _create_test_work_item()

    with patch(
        "golazo_copilot.tools.gcp_status.validate_all_outputs",
        side_effect=Exception("validator crash"),
    ):
        result = await gcp_status(
            work_item_id="TST-051",
            work_items_dir=TEST_WORKITEMS_DIR,
        )

    assert result["active"] is True, (
        "Output validation failure should not crash gcp_status"
    )
    # required_outputs should have a safe fallback
    assert "required_outputs" in result
    # next_steps should still generate
    assert "next_steps" in result
    assert isinstance(result["next_steps"], list)


# ---------------------------------------------------------------------------
# TC-7: _generate_next_steps handles empty output list
# ---------------------------------------------------------------------------
def test_generate_next_steps_with_empty_outputs():
    """_generate_next_steps doesn't crash when passed empty output list."""
    # Create a minimal mock state
    state = MagicMock()
    state.current_phase = "definition"
    state.current_role = "project-owner-assistant"

    steps = _generate_next_steps(state, required_outputs=[])
    assert isinstance(steps, list)
    assert len(steps) > 0, (
        "_generate_next_steps should handle empty/missing output data without crashing"
    )


def test_generate_next_steps_with_none_outputs():
    """_generate_next_steps doesn't crash when passed None."""
    state = MagicMock()
    state.current_phase = "development"
    state.current_role = "developer"

    steps = _generate_next_steps(state, required_outputs=None)
    assert isinstance(steps, list)
    assert len(steps) > 0


# ---------------------------------------------------------------------------
# TC-8: Pure computation is fast
# ---------------------------------------------------------------------------
def test_compute_role_progress_is_fast():
    """_compute_role_progress completes in < 10ms (pure in-memory)."""
    state = MagicMock()
    state.role_history = []
    state.current_role = "project-owner-assistant"

    start = time.monotonic()
    result = _compute_role_progress(state)
    elapsed = time.monotonic() - start

    assert elapsed < 0.01, f"_compute_role_progress took {elapsed:.4f}s — expected < 10ms"
    assert "roles" in result
    assert "roles_completed" in result
    assert "roles_total" in result


# ---------------------------------------------------------------------------
# TC-1: Response structure unchanged (regression check)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_response_structure_unchanged():
    """Response dict has all expected keys after parallelization."""
    await _create_test_work_item()

    result = await gcp_status(
        work_item_id="TST-051",
        work_items_dir=TEST_WORKITEMS_DIR,
    )

    expected_keys = {
        "active", "version", "work_item_id", "profile",
        "current_phase", "current_role", "required_outputs",
        "role_progress", "deviations", "missing_notes",
        "version_warning", "registry_hint", "role_instructions",
        "next_steps",
    }
    assert expected_keys.issubset(result.keys()), (
        f"Missing keys: {expected_keys - result.keys()}"
    )
