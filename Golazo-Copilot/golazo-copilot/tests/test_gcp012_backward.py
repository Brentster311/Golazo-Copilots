"""Additional tests for GCP-0012: Backward role transitions."""

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.core.persistence import load_state
from golazo_copilot.tools.golazo_create_workitem import golazo_create_workitem
from golazo_copilot.tools.golazo_transition import ROLE_SUFFIX_MAP, golazo_transition

TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"
TEST_WORKSPACE_ROOT = Path(__file__).parent

ALL_ROLES = [
    "planner",
    "project-owner-assistant", "program-manager", "domain-expert", "quality-assurance",
    "architect", "developer", "refactor-expert", "builder", "documenter", "retrospective"
]


def create_empty_role_files(workspace_root: Path = TEST_WORKSPACE_ROOT):
    """Create role files with no Required Outputs section for testing."""
    roles_dir = workspace_root / ".github" / "roles"
    roles_dir.mkdir(parents=True, exist_ok=True)
    for role in ALL_ROLES:
        role_file = roles_dir / f"{role}.md"
        role_file.write_text(f"# Role: {role}\n\n## Purpose\nTest role.\n")


def create_role_notes(work_item_id: str, role: str, work_items_dir: Path = TEST_WORKITEMS_DIR):
    """Helper to create role notes file for a given role."""
    suffix = ROLE_SUFFIX_MAP.get(role, role)
    notes_dir = work_items_dir / work_item_id / "RoleDecisionNotes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_file = notes_dir / f"{work_item_id}-{suffix}.md"
    notes_file.write_text(f"# {work_item_id}: {role} Notes\n\nTest notes.")
    return notes_file


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


class TestBackwardTransitions:
    """GCP-0012: Tests for backward role transitions."""

    @pytest.mark.asyncio
    async def test_backward_from_retrospective_to_developer(self):
        """AC1: Should allow backward transition from retrospective to developer."""
        await golazo_create_workitem(work_item_id="BCK-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Progress through roles to retrospective
        create_role_notes("BCK-001", "project-owner-assistant")
        await golazo_transition(work_item_id="BCK-001", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-001", "program-manager")
        await golazo_transition(work_item_id="BCK-001", role="domain-expert", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-001", "domain-expert")
        await golazo_transition(work_item_id="BCK-001", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-001", "quality-assurance")
        await golazo_transition(work_item_id="BCK-001", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        create_role_notes("BCK-001", "architect")
        await golazo_transition(work_item_id="BCK-001", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-001", "developer")
        await golazo_transition(work_item_id="BCK-001", role="refactor-expert", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-001", "refactor-expert")
        await golazo_transition(work_item_id="BCK-001", role="builder", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-001", "builder")
        await golazo_transition(work_item_id="BCK-001", role="documenter", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-001", "documenter")
        await golazo_transition(work_item_id="BCK-001", role="retrospective", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Now go backward to developer (already has notes from before)
        create_role_notes("BCK-001", "retrospective")
        result = await golazo_transition(
            work_item_id="BCK-001",
            role="developer",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["current_role"] == "developer"
        
        # Verify state is intact
        state = load_state("BCK-001", TEST_WORKITEMS_DIR)
        assert state.current_role == "developer"

    @pytest.mark.asyncio
    async def test_forward_skip_still_fails(self):
        """AC2: Forward transitions should still not allow skipping roles."""
        await golazo_create_workitem(work_item_id="BCK-002", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-002", "project-owner-assistant")
        await golazo_transition(work_item_id="BCK-002", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Try to skip quality-assurance (role notes don't help here - sequence is wrong)
        create_role_notes("BCK-002", "program-manager")
        result = await golazo_transition(
            work_item_id="BCK-002",
            role="architect",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "cannot transition" in result["error"].lower() or "invalid" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_jump_multiple_roles_backward(self):
        """AC3: Should allow jumping multiple roles backward."""
        await golazo_create_workitem(work_item_id="BCK-003", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Progress to builder
        create_role_notes("BCK-003", "project-owner-assistant")
        await golazo_transition(work_item_id="BCK-003", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-003", "program-manager")
        await golazo_transition(work_item_id="BCK-003", role="domain-expert", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-003", "domain-expert")
        await golazo_transition(work_item_id="BCK-003", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-003", "quality-assurance")
        await golazo_transition(work_item_id="BCK-003", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        create_role_notes("BCK-003", "architect")
        await golazo_transition(work_item_id="BCK-003", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-003", "developer")
        await golazo_transition(work_item_id="BCK-003", role="refactor-expert", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-003", "refactor-expert")
        await golazo_transition(work_item_id="BCK-003", role="builder", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Jump back 5 roles to program-manager
        create_role_notes("BCK-003", "builder")
        result = await golazo_transition(
            work_item_id="BCK-003",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["current_role"] == "program-manager"

    @pytest.mark.asyncio
    async def test_role_history_tracks_backward_transition(self):
        """AC4: Role history should track backward transitions."""
        await golazo_create_workitem(work_item_id="BCK-004", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-004", "project-owner-assistant")
        await golazo_transition(work_item_id="BCK-004", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-004", "program-manager")
        await golazo_transition(work_item_id="BCK-004", role="domain-expert", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-004", "domain-expert")
        await golazo_transition(work_item_id="BCK-004", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BCK-004", "quality-assurance")
        await golazo_transition(work_item_id="BCK-004", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        create_role_notes("BCK-004", "architect")
        await golazo_transition(work_item_id="BCK-004", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Go backward
        create_role_notes("BCK-004", "developer")
        await golazo_transition(work_item_id="BCK-004", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("BCK-004", TEST_WORKITEMS_DIR)
        
        # Should have entries for: project-owner-assistant, program-manager, domain-expert, QA, architect, developer, architect (again)
        assert len(state.role_history) == 7
        assert state.role_history[-1].role == "architect"
        assert state.role_history[-2].role == "developer"
        assert state.role_history[-2].exited_at is not None  # Developer entry should be closed
