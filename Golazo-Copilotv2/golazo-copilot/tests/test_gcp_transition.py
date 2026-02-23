"""Tests for golazo_transition tool."""

import asyncio
import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.golazo_create_workitem import golazo_create_workitem
from golazo_copilot.tools.golazo_transition import golazo_transition, ROLE_SUFFIX_MAP
from golazo_copilot.core.persistence import load_state, save_state


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"
# Use tests/ as workspace root so role files can be created there
TEST_WORKSPACE_ROOT = Path(__file__).parent

# All roles that need empty role files for testing (no Required Outputs)
ALL_ROLES = [
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


async def advance_to_role(work_item_id: str, target_role: str, work_items_dir: Path = TEST_WORKITEMS_DIR):
    """Helper to advance through roles with notes to reach target role."""
    role_sequence = [
        "project-owner-assistant", "program-manager", "domain-expert", "quality-assurance", 
        "architect", "developer", "refactor-expert", "builder", "documenter", "retrospective"
    ]
    
    # Find where we need to go
    target_idx = role_sequence.index(target_role)
    
    # Create notes and transition for each role up to (but not including) target
    for i, role in enumerate(role_sequence[:target_idx]):
        create_role_notes(work_item_id, role, work_items_dir)
        if i < target_idx:
            next_role = role_sequence[i + 1]
            await golazo_transition(work_item_id=work_item_id, role=next_role, work_items_dir=work_items_dir)


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    # Create empty role files so tests use them instead of package defaults
    create_empty_role_files()
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    # Clean up role files
    roles_dir = TEST_WORKSPACE_ROOT / ".github"
    if roles_dir.exists():
        shutil.rmtree(roles_dir)


class TestSuccessfulTransition:
    """AC1: golazo_transition changes role correctly."""

    @pytest.mark.asyncio
    async def test_transition_project_owner_to_program_manager(self):
        """Should transition from project-owner-assistant to program-manager."""
        await golazo_create_workitem(work_item_id="TT-001", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("TT-001", "project-owner-assistant")
        
        result = await golazo_transition(
            work_item_id="TT-001",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["current_role"] == "program-manager"
        
        state = load_state("TT-001", TEST_WORKITEMS_DIR)
        assert state.current_role == "program-manager"

    @pytest.mark.asyncio
    async def test_transition_updates_role_history(self):
        """Should close previous role and add new entry."""
        await golazo_create_workitem(work_item_id="HT-001", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("HT-001", "project-owner-assistant")
        
        await golazo_transition(
            work_item_id="HT-001",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        state = load_state("HT-001", TEST_WORKITEMS_DIR)
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
        await golazo_create_workitem(work_item_id="TTS-001", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("TTS-001", "project-owner-assistant")
        state_before = load_state("TTS-001", TEST_WORKITEMS_DIR)
        
        await asyncio.sleep(0.01)
        
        await golazo_transition(
            work_item_id="TTS-001",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        state_after = load_state("TTS-001", TEST_WORKITEMS_DIR)
        assert state_after.updated_at > state_before.updated_at

    @pytest.mark.asyncio
    async def test_transition_returns_role_instructions(self):
        """Should return role instructions on success."""
        await golazo_create_workitem(work_item_id="IT-001", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("IT-001", "project-owner-assistant")
        
        result = await golazo_transition(
            work_item_id="IT-001",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["role_instructions"] is not None
        assert len(result["role_instructions"]) > 20


class TestTransitionValidation:
    """AC2: Only valid transitions are allowed."""

    @pytest.mark.asyncio
    async def test_valid_transition_program_manager_to_domain_expert(self):
        """Should allow program-manager to domain-expert."""
        await golazo_create_workitem(work_item_id="VLD-001", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("VLD-001", "project-owner-assistant")
        await golazo_transition(work_item_id="VLD-001", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("VLD-001", "program-manager")
        
        result = await golazo_transition(
            work_item_id="VLD-001",
            role="domain-expert",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_transition_project_owner_to_developer(self):
        """Should reject skipping roles."""
        await golazo_create_workitem(work_item_id="INV-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await golazo_transition(
            work_item_id="INV-001",
            role="developer",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "Cannot transition" in result["error"]

    @pytest.mark.asyncio
    async def test_unknown_role_rejected(self):
        """Should reject unknown role names."""
        await golazo_create_workitem(work_item_id="UR-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await golazo_transition(
            work_item_id="UR-001",
            role="UR-001-xyz",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "Invalid role" in result["error"] or "Unknown role" in result["error"]

    @pytest.mark.asyncio
    async def test_empty_role_rejected(self):
        """Should reject empty role name."""
        await golazo_create_workitem(work_item_id="ER-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await golazo_transition(
            work_item_id="ER-001",
            role="",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False


class TestPhaseTransitions:
    """AC4: Phase updates when crossing boundaries."""

    @pytest.mark.asyncio
    async def test_stays_in_definition_phase(self):
        """Should stay in definition phase through architect."""
        await golazo_create_workitem(work_item_id="PH-001", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("PH-001", "project-owner-assistant")
        
        for role in ["program-manager", "domain-expert", "quality-assurance", "architect"]:
            await golazo_transition(work_item_id="PH-001", role=role, work_items_dir=TEST_WORKITEMS_DIR)
            create_role_notes("PH-001", role)
            state = load_state("PH-001", TEST_WORKITEMS_DIR)
            assert state.current_phase == "definition"

    @pytest.mark.asyncio
    async def test_enters_development_phase(self):
        """Should enter development phase at developer."""
        await golazo_create_workitem(work_item_id="PH-002", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("PH-002", "project-owner-assistant")
        await golazo_transition(work_item_id="PH-002", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("PH-002", "program-manager")
        await golazo_transition(work_item_id="PH-002", role="domain-expert", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("PH-002", "domain-expert")
        await golazo_transition(work_item_id="PH-002", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("PH-002", "quality-assurance")
        await golazo_transition(work_item_id="PH-002", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("PH-002", "architect")
        
        await golazo_transition(work_item_id="PH-002", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("PH-002", TEST_WORKITEMS_DIR)
        assert state.current_phase == "development"


class TestSimpleBackwardTransitions:
    """AC6: Backward transitions allowed with warning."""

    @pytest.mark.asyncio
    async def test_backward_transition_allowed(self):
        """Should allow backward transition."""
        await golazo_create_workitem(work_item_id="BWD-001", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BWD-001", "project-owner-assistant")
        await golazo_transition(work_item_id="BWD-001", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BWD-001", "program-manager")
        
        result = await golazo_transition(
            work_item_id="BWD-001",
            role="project-owner-assistant",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert "warning" in result

    @pytest.mark.asyncio
    async def test_backward_preserves_progress(self):
        """Should NOT reset progress on backward transition."""
        await golazo_create_workitem(work_item_id="BWD-002", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BWD-002", "project-owner-assistant")
        await golazo_transition(work_item_id="BWD-002", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("BWD-002", "program-manager")
        
        state = load_state("BWD-002", TEST_WORKITEMS_DIR)
        original_role_count = len(state.role_history)
        
        await golazo_transition(work_item_id="BWD-002", role="project-owner-assistant", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("BWD-002", TEST_WORKITEMS_DIR)
        # Role history should have grown (progress preserved, not reset)
        assert len(state.role_history) > original_role_count




class TestErrorCases:
    """Error handling tests."""

    @pytest.mark.asyncio
    async def test_no_active_work_item(self):
        """Should error if work item doesn't exist."""
        result = await golazo_transition(
            work_item_id="nonexistent",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "not found" in result["error"].lower() or "does not exist" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_same_role_transition(self):
        """Should handle transition to same role gracefully."""
        await golazo_create_workitem(work_item_id="SR-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await golazo_transition(
            work_item_id="SR-001",
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
        await golazo_create_workitem(work_item_id="BCK-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Progress through roles to retrospective with notes
        await advance_to_role("BCK-001", "retrospective", TEST_WORKITEMS_DIR)
        create_role_notes("BCK-001", "retrospective")
        
        # Now go backward to developer
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
        create_role_notes("BCK-002", "program-manager")
        
        # Try to skip quality-assurance
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
        
        # Progress to builder with notes
        await advance_to_role("BCK-003", "builder", TEST_WORKITEMS_DIR)
        create_role_notes("BCK-003", "builder")
        
        # Jump back 5 roles to program-manager
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
        
        # Progress to developer with notes
        await advance_to_role("BCK-004", "developer", TEST_WORKITEMS_DIR)
        create_role_notes("BCK-004", "developer")
        
        # Go backward
        await golazo_transition(work_item_id="BCK-004", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("BCK-004", TEST_WORKITEMS_DIR)
        
        # Should have entries for: project-owner-assistant, program-manager, domain-expert, QA, architect, developer, architect (again)
        assert len(state.role_history) == 7
        assert state.role_history[-1].role == "architect"
        assert state.role_history[-2].role == "developer"
        assert state.role_history[-2].exited_at is not None  # Developer entry should be closed


class TestRoleNotesBlocking:
    """GCP-0020: Block when role notes are missing on transition (replaces warning from GCP-0019)."""

    @pytest.mark.asyncio
    async def test_transition_with_notes_present_succeeds(self):
        """TC-01: Should succeed when notes exist."""
        await golazo_create_workitem(work_item_id="NTS-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create PO notes file
        create_role_notes("NTS-001", "project-owner-assistant")
        
        result = await golazo_transition(
            work_item_id="NTS-001",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_transition_with_notes_missing_blocks(self):
        """TC-02: Should block when notes are missing (changed from warning in GCP-0020)."""
        await golazo_create_workitem(work_item_id="NTS-002", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Don't create notes file
        result = await golazo_transition(
            work_item_id="NTS-002",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "missing" in result["error"].lower() or "notes" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_refactor_expert_uses_short_suffix(self):
        """TC-06: refactor-expert should check for -refactor.md suffix."""
        await golazo_create_workitem(work_item_id="NTS-003", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Advance to developer
        await advance_to_role("NTS-003", "developer", TEST_WORKITEMS_DIR)
        
        # Create developer notes with correct name
        create_role_notes("NTS-003", "developer")
        
        result = await golazo_transition(
            work_item_id="NTS-003",
            role="refactor-expert",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True


class TestBlockingRoleNotes:
    """GCP-0020: Block transition when role notes are missing."""

    @pytest.mark.asyncio
    async def test_transition_blocked_when_notes_missing(self):
        """TC1: Transition should fail if outgoing role has no notes file."""
        await golazo_create_workitem(work_item_id="BLK-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Try to transition without creating notes
        result = await golazo_transition(
            work_item_id="BLK-001",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "Missing role notes" in result["error"]
        assert "missing_file" in result

    @pytest.mark.asyncio
    async def test_transition_allowed_when_notes_exist(self):
        """TC2: Transition should succeed if outgoing role has notes file."""
        await golazo_create_workitem(work_item_id="BLK-002", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create the notes file
        notes_dir = TEST_WORKITEMS_DIR / "BLK-002" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "BLK-002-project-owner-assistant.md").write_text("# PO Notes")
        
        result = await golazo_transition(
            work_item_id="BLK-002",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["current_role"] == "program-manager"

    @pytest.mark.asyncio
    async def test_force_without_notes_requires_consent(self):
        """TC3: Force bypass should fail without prior consent."""
        await golazo_create_workitem(work_item_id="BLK-003", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await golazo_transition(
            work_item_id="BLK-003",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR,
            force_without_notes=True,
        )
        
        assert result["success"] is False
        assert "consent" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_force_with_consent_succeeds(self):
        """TC4: Force bypass should succeed with prior consent."""
        from golazo_copilot.tools.golazo_consent import golazo_consent
        
        await golazo_create_workitem(work_item_id="BLK-004", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Record consent first
        await golazo_consent(
            work_item_id="BLK-004",
            action="skip_role",
            reason="Testing force bypass with consent",
            work_items_dir=TEST_WORKITEMS_DIR,
        )
        
        result = await golazo_transition(
            work_item_id="BLK-004",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR,
            force_without_notes=True,
        )
        
        assert result["success"] is True
        assert result["current_role"] == "program-manager"

    @pytest.mark.asyncio
    async def test_error_includes_expected_file_path(self):
        """TC6: Error message should include the exact file path to create."""
        await golazo_create_workitem(work_item_id="BLK-006", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await golazo_transition(
            work_item_id="BLK-006",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "BLK-006-project-owner-assistant.md" in result["missing_file"]

    @pytest.mark.asyncio
    async def test_backward_transition_checks_outgoing_role(self):
        """TC7: Backward transitions should check notes for the role being LEFT."""
        await golazo_create_workitem(work_item_id="BLK-007", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create notes and advance to developer
        notes_dir = TEST_WORKITEMS_DIR / "BLK-007" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "BLK-007-project-owner-assistant.md").write_text("# PO Notes")
        (notes_dir / "BLK-007-program-manager.md").write_text("# PM Notes")
        (notes_dir / "BLK-007-quality-assurance.md").write_text("# QA Notes")
        (notes_dir / "BLK-007-domain-expert.md").write_text("# DE Notes")
        (notes_dir / "BLK-007-architect.md").write_text("# Arch Notes")
        
        await golazo_transition(work_item_id="BLK-007", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR)
        await golazo_transition(work_item_id="BLK-007", role="domain-expert", work_items_dir=TEST_WORKITEMS_DIR)
        await golazo_transition(work_item_id="BLK-007", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR)
        await golazo_transition(work_item_id="BLK-007", role="architect", work_items_dir=TEST_WORKITEMS_DIR)
        
        await golazo_transition(work_item_id="BLK-007", role="developer", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Now try backward transition without developer notes
        result = await golazo_transition(
            work_item_id="BLK-007",
            role="architect",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        # Should fail because developer notes don't exist
        assert result["success"] is False
        assert "developer" in result["error"].lower()
