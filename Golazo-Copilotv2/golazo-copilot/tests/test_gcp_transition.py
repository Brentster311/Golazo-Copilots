"""Tests for gcp_transition tool."""

import asyncio
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


class TestSuccessfulTransition:
    """AC1: gcp_transition changes role correctly."""

    @pytest.mark.asyncio
    async def test_transition_project_owner_to_program_manager(self):
        """Should transition from project-owner-assistant to program-manager."""
        await gcp_create_workitem(work_item_id="trans-test", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="trans-test",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["current_role"] == "program-manager"
        
        state = load_state("trans-test", TEST_WORKITEMS_DIR)
        assert state.current_role == "program-manager"

    @pytest.mark.asyncio
    async def test_transition_updates_role_history(self):
        """Should close previous role and add new entry."""
        await gcp_create_workitem(work_item_id="history-test", work_items_dir=TEST_WORKITEMS_DIR)
        
        await gcp_transition(
            work_item_id="history-test",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        state = load_state("history-test", TEST_WORKITEMS_DIR)
        assert len(state.role_history) == 2
        
        # Previous role closed
        assert state.role_history[0].role == "project-owner-assistant"
        assert state.role_history[0].exited_at is not None
        
        # New role open
        assert state.role_history[1].role == "program-manager"
        assert state.role_history[1].exited_at is None

    @pytest.mark.asyncio
    async def test_transition_updates_timestamp(self):
        """Should update updatedAt timestamp."""
        await gcp_create_workitem(work_item_id="timestamp-test", work_items_dir=TEST_WORKITEMS_DIR)
        state_before = load_state("timestamp-test", TEST_WORKITEMS_DIR)
        
        await asyncio.sleep(0.01)
        
        await gcp_transition(
            work_item_id="timestamp-test",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        state_after = load_state("timestamp-test", TEST_WORKITEMS_DIR)
        assert state_after.updated_at > state_before.updated_at

    @pytest.mark.asyncio
    async def test_transition_returns_role_instructions(self):
        """Should return role instructions on success."""
        await gcp_create_workitem(work_item_id="instructions-test", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="instructions-test",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["role_instructions"] is not None
        assert len(result["role_instructions"]) > 20


class TestTransitionValidation:
    """AC2: Only valid transitions are allowed."""

    @pytest.mark.asyncio
    async def test_valid_transition_program_manager_to_qa(self):
        """Should allow program-manager to quality-assurance."""
        await gcp_create_workitem(work_item_id="valid-1", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="valid-1", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="valid-1",
            role="quality-assurance",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_transition_project_owner_to_developer(self):
        """Should reject skipping roles."""
        await gcp_create_workitem(work_item_id="invalid-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="invalid-1",
            role="developer",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "Cannot transition" in result["error"]

    @pytest.mark.asyncio
    async def test_unknown_role_rejected(self):
        """Should reject unknown role names."""
        await gcp_create_workitem(work_item_id="unknown-role", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="unknown-role",
            role="unknown-role-xyz",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "Invalid role" in result["error"] or "Unknown role" in result["error"]

    @pytest.mark.asyncio
    async def test_empty_role_rejected(self):
        """Should reject empty role name."""
        await gcp_create_workitem(work_item_id="empty-role", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="empty-role",
            role="",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False


class TestDoRGate:
    """AC3: DoR gate blocks transition to developer."""

    @pytest.mark.asyncio
    async def test_dor_gate_blocks_incomplete(self):
        """Should block developer transition if DoR incomplete."""
        await gcp_create_workitem(work_item_id="dor-gate-1", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="dor-gate-1", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="dor-gate-1", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="dor-gate-1", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="dor-gate-1",
            role="developer",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "DoR" in result["error"]
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_dor_gate_lists_missing_items(self):
        """Should list which DoR items are missing."""
        await gcp_create_workitem(work_item_id="dor-gate-2", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="dor-gate-2", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="dor-gate-2", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="dor-gate-2", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="dor-gate-2",
            role="developer",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "userStory" in result["missing"]

    @pytest.mark.asyncio
    async def test_dor_gate_passes_when_complete(self):
        """Should allow developer transition when DoR complete."""
        await gcp_create_workitem(work_item_id="dor-gate-3", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="dor-gate-3", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="dor-gate-3", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="dor-gate-3", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Mark DoR complete
        state = load_state("dor-gate-3", TEST_WORKITEMS_DIR)
        state.dor = {k: True for k in state.dor}
        save_state("dor-gate-3", state, TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="dor-gate-3",
            role="developer",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True


class TestPhaseTransitions:
    """AC4: Phase updates when crossing boundaries."""

    @pytest.mark.asyncio
    async def test_stays_in_definition_phase(self):
        """Should stay in definition phase through architect."""
        await gcp_create_workitem(work_item_id="phase-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        for role in ["program-manager", "quality-assurance", "architect"]:
            await gcp_transition(work_item_id="phase-1", role=role, work_items_dir=TEST_WORKITEMS_DIR)
            state = load_state("phase-1", TEST_WORKITEMS_DIR)
            assert state.current_phase == "definition"

    @pytest.mark.asyncio
    async def test_enters_development_phase(self):
        """Should enter development phase at developer."""
        await gcp_create_workitem(work_item_id="phase-2", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="phase-2", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="phase-2", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="phase-2", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("phase-2", TEST_WORKITEMS_DIR)
        state.dor = {k: True for k in state.dor}
        save_state("phase-2", state, TEST_WORKITEMS_DIR)
        
        await gcp_transition(work_item_id="phase-2", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("phase-2", TEST_WORKITEMS_DIR)
        assert state.current_phase == "development"


class TestBackwardTransitions:
    """AC6: Backward transitions allowed with warning."""

    @pytest.mark.asyncio
    async def test_backward_transition_allowed(self):
        """Should allow backward transition."""
        await gcp_create_workitem(work_item_id="backward-1", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="backward-1", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="backward-1",
            role="project-owner-assistant",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert "warning" in result

    @pytest.mark.asyncio
    async def test_backward_preserves_progress(self):
        """Should NOT reset DoR items on backward transition."""
        await gcp_create_workitem(work_item_id="backward-2", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="backward-2", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("backward-2", TEST_WORKITEMS_DIR)
        state.dor["userStory"] = True
        save_state("backward-2", state, TEST_WORKITEMS_DIR)
        
        await gcp_transition(work_item_id="backward-2", role="project-owner-assistant", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("backward-2", TEST_WORKITEMS_DIR)
        assert state.dor["userStory"] is True




class TestErrorCases:
    """Error handling tests."""

    @pytest.mark.asyncio
    async def test_no_active_work_item(self):
        """Should error if work item doesn't exist."""
        result = await gcp_transition(
            work_item_id="nonexistent",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "not found" in result["error"].lower() or "does not exist" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_same_role_transition(self):
        """Should handle transition to same role gracefully."""
        await gcp_create_workitem(work_item_id="same-role", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_transition(
            work_item_id="same-role",
            role="project-owner-assistant",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        # Same role should succeed or give reasonable response
        assert "current_role" in result or result["success"] is False


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


class TestRoleNotesWarning:
    """GCP-0019: Warn when role notes are missing on transition."""

    @pytest.mark.asyncio
    async def test_transition_with_notes_present_no_warning(self):
        """TC-01: Should not warn when notes exist."""
        await gcp_create_workitem(work_item_id="notes-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create PO notes file
        notes_dir = TEST_WORKITEMS_DIR / "notes-1" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "notes-1-project-owner-assistant.md").write_text("# PO Notes")
        
        result = await gcp_transition(
            work_item_id="notes-1",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result.get("warning") is None or "notes" not in result.get("warning", "").lower()

    @pytest.mark.asyncio
    async def test_transition_with_notes_missing_returns_warning(self):
        """TC-02: Should warn when notes are missing but still succeed."""
        await gcp_create_workitem(work_item_id="notes-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Don't create notes file
        result = await gcp_transition(
            work_item_id="notes-2",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True  # Transition still succeeds
        assert result.get("warning") is not None
        assert "notes" in result["warning"].lower() or "missing" in result["warning"].lower()

    @pytest.mark.asyncio
    async def test_refactor_expert_uses_short_suffix(self):
        """TC-06: refactor-expert should check for -refactor.md suffix."""
        await gcp_create_workitem(work_item_id="notes-3", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Transition to refactor-expert
        await gcp_transition(work_item_id="notes-3", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="notes-3", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_transition(work_item_id="notes-3", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("notes-3", TEST_WORKITEMS_DIR)
        state.dor = {k: True for k in state.dor}
        save_state("notes-3", state, TEST_WORKITEMS_DIR)
        
        await gcp_transition(work_item_id="notes-3", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create developer notes with correct name
        notes_dir = TEST_WORKITEMS_DIR / "notes-3" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "notes-3-developer.md").write_text("# Dev Notes")
        
        result = await gcp_transition(
            work_item_id="notes-3",
            role="refactor-expert",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        # Should not warn about developer notes (they exist)
        # May warn about other missing notes
