"""Additional tests for GCP-0012: Backward role transitions."""

import shutil
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_create_workitem import gcp_create_workitem
from golazo_copilot.tools.gcp_transition import gcp_transition, ROLE_SUFFIX_MAP
from golazo_copilot.core.persistence import load_state


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"
TEST_WORKSPACE_ROOT = Path(__file__).parent

ALL_ROLES = [
    "project-owner-assistant", "program-manager", "quality-assurance",
    "architect", "developer", "refactor-expert", "builder", "documentor", "retrospective"
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
        await gcp_create_workitem(work_item_id="back-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Progress through roles to retrospective
        create_role_notes("back-1", "project-owner-assistant")
        await gcp_transition(work_item_id="back-1", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-1", "program-manager")
        await gcp_transition(work_item_id="back-1", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-1", "quality-assurance")
        await gcp_transition(work_item_id="back-1", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        create_role_notes("back-1", "architect")
        await gcp_transition(work_item_id="back-1", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-1", "developer")
        await gcp_transition(work_item_id="back-1", role="refactor-expert", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-1", "refactor-expert")
        await gcp_transition(work_item_id="back-1", role="builder", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-1", "builder")
        await gcp_transition(work_item_id="back-1", role="documentor", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-1", "documentor")
        await gcp_transition(work_item_id="back-1", role="retrospective", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Now go backward to developer (already has notes from before)
        create_role_notes("back-1", "retrospective")
        result = await gcp_transition(
            work_item_id="back-1",
            role="developer",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["current_role"] == "developer"
        
        # Verify state is intact
        state = load_state("back-1", TEST_WORKITEMS_DIR)
        assert state.current_role == "developer"

    @pytest.mark.asyncio
    async def test_forward_skip_still_fails(self):
        """AC2: Forward transitions should still not allow skipping roles."""
        await gcp_create_workitem(work_item_id="back-2", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-2", "project-owner-assistant")
        await gcp_transition(work_item_id="back-2", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Try to skip quality-assurance (role notes don't help here - sequence is wrong)
        create_role_notes("back-2", "program-manager")
        result = await gcp_transition(
            work_item_id="back-2",
            role="architect",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "cannot transition" in result["error"].lower() or "invalid" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_jump_multiple_roles_backward(self):
        """AC3: Should allow jumping multiple roles backward."""
        await gcp_create_workitem(work_item_id="back-3", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Progress to builder
        create_role_notes("back-3", "project-owner-assistant")
        await gcp_transition(work_item_id="back-3", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-3", "program-manager")
        await gcp_transition(work_item_id="back-3", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-3", "quality-assurance")
        await gcp_transition(work_item_id="back-3", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        create_role_notes("back-3", "architect")
        await gcp_transition(work_item_id="back-3", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-3", "developer")
        await gcp_transition(work_item_id="back-3", role="refactor-expert", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-3", "refactor-expert")
        await gcp_transition(work_item_id="back-3", role="builder", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Jump back 5 roles to program-manager
        create_role_notes("back-3", "builder")
        result = await gcp_transition(
            work_item_id="back-3",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["current_role"] == "program-manager"

    @pytest.mark.asyncio
    async def test_role_history_tracks_backward_transition(self):
        """AC4: Role history should track backward transitions."""
        await gcp_create_workitem(work_item_id="back-4", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-4", "project-owner-assistant")
        await gcp_transition(work_item_id="back-4", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-4", "program-manager")
        await gcp_transition(work_item_id="back-4", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("back-4", "quality-assurance")
        await gcp_transition(work_item_id="back-4", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        create_role_notes("back-4", "architect")
        await gcp_transition(work_item_id="back-4", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Go backward
        create_role_notes("back-4", "developer")
        await gcp_transition(work_item_id="back-4", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("back-4", TEST_WORKITEMS_DIR)
        
        # Should have entries for: project-owner-assistant, program-manager, QA, architect, developer, architect (again)
        assert len(state.role_history) == 6
        assert state.role_history[-1].role == "architect"
        assert state.role_history[-2].role == "developer"
        assert state.role_history[-2].exited_at is not None  # Developer entry should be closed
