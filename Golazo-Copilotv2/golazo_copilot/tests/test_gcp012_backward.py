"""Additional tests for GCP-0012: Backward role transitions."""

import shutil
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_create_workitem import gcp_create_workitem
from golazo_copilot.tools.gcp_transition import gcp_transition
from golazo_copilot.core.persistence import load_state, save_state


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)


class TestBackwardTransitions:
    """GCP-0012: Tests for backward role transitions."""

    @pytest.mark.asyncio
    async def test_backward_from_retrospective_to_developer(self):
        """AC1: Should allow backward transition from retrospective to developer."""
        await gcp_create_workitem(work_item_id="back-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Progress through roles to retrospective
        await gcp_transition(work_item_id="back-1", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-1", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-1", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Mark DoR complete
        state = load_state("back-1", TEST_WORKITEMS_DIR)
        state.dor = {k: True for k in state.dor}
        save_state("back-1", state, TEST_WORKITEMS_DIR)
        
        await gcp_transition(work_item_id="back-1", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-1", role="refactor-expert", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-1", role="builder", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-1", role="documentor", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-1", role="retrospective", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Now go backward to developer
        result = await gcp_transition(
            work_item_id="back-1",
            role="developer",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["current_role"] == "developer"
        
        # Verify progress preserved
        state = load_state("back-1", TEST_WORKITEMS_DIR)
        assert all(state.dor.values())  # DoR should still be complete

    @pytest.mark.asyncio
    async def test_forward_skip_still_fails(self):
        """AC2: Forward transitions should still not allow skipping roles."""
        await gcp_create_workitem(work_item_id="back-2", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-2", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Try to skip quality-assurance
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
        await gcp_transition(work_item_id="back-3", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-3", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-3", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("back-3", TEST_WORKITEMS_DIR)
        state.dor = {k: True for k in state.dor}
        save_state("back-3", state, TEST_WORKITEMS_DIR)
        
        await gcp_transition(work_item_id="back-3", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-3", role="refactor-expert", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-3", role="builder", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Jump back 5 roles to program-manager
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
        await gcp_transition(work_item_id="back-4", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-4", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="back-4", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("back-4", TEST_WORKITEMS_DIR)
        state.dor = {k: True for k in state.dor}
        save_state("back-4", state, TEST_WORKITEMS_DIR)
        
        await gcp_transition(work_item_id="back-4", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Go backward
        await gcp_transition(work_item_id="back-4", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("back-4", TEST_WORKITEMS_DIR)
        
        # Should have entries for: project-owner-assistant, program-manager, QA, architect, developer, architect (again)
        assert len(state.role_history) == 6
        assert state.role_history[-1].role == "architect"
        assert state.role_history[-2].role == "developer"
        assert state.role_history[-2].exited_at is not None  # Developer entry should be closed
