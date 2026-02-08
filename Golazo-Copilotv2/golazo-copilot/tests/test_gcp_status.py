"""Tests for gcp_status tool."""

import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_create_workitem import gcp_create_workitem
from golazo_copilot.tools.gcp_transition import gcp_transition, ROLE_SUFFIX_MAP
from golazo_copilot.tools.gcp_status import gcp_status


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


def create_test_file(work_item_id: str, filename: str) -> str:
    """Create a test file and return its path."""
    path = TEST_WORKITEMS_DIR / work_item_id / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Test content")
    return str(path)


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


class TestStatusBasic:
    """Basic status tests."""

    @pytest.mark.asyncio
    async def test_returns_active_status(self):
        """Should return active=True for initialized work item."""
        await gcp_create_workitem(work_item_id="status-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="status-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["active"] is True
        assert result["work_item_id"] == "status-1"

    @pytest.mark.asyncio
    async def test_returns_current_role_and_phase(self):
        """Should return current role and phase."""
        await gcp_create_workitem(work_item_id="status-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="status-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["current_role"] == "project-owner-assistant"
        assert result["current_phase"] == "definition"

    @pytest.mark.asyncio
    async def test_returns_role_instructions(self):
        """Should return role instructions."""
        await gcp_create_workitem(work_item_id="status-3", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="status-3",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "role_instructions" in result
        assert len(result["role_instructions"]) > 50


class TestStatusDoRDoD:
    """DoR/DoD status tests."""

    @pytest.mark.asyncio
    async def test_dor_status_initially_incomplete(self):
        """Should show DoR incomplete initially."""
        await gcp_create_workitem(work_item_id="dor-status-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="dor-status-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["dor"]["complete"] is False
        assert len(result["dor"]["missing"]) == 4


class TestStatusNoWorkItem:
    """No work item tests."""

    @pytest.mark.asyncio
    async def test_no_work_item_returns_inactive(self):
        """Should return active=False if no work item."""
        result = await gcp_status(
            work_item_id="nonexistent",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["active"] is False
        assert "No active work item" in result.get("message", "") or "does not exist" in result.get("message", "")


class TestStatusAfterTransition:
    """Status after transitions."""

    @pytest.mark.asyncio
    async def test_status_reflects_transition(self):
        """Should reflect current role after transition."""
        await gcp_create_workitem(work_item_id="trans-status", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("trans-status", "project-owner-assistant")
        await gcp_transition(
            work_item_id="trans-status",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        result = await gcp_status(
            work_item_id="trans-status",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["current_role"] == "program-manager"


class TestStatusDeviations:
    """GCP-0014: Status should show deviations."""

    @pytest.mark.asyncio
    async def test_status_includes_deviations_list(self):
        """Should include deviations in status."""
        from golazo_copilot.tools.gcp_consent import gcp_consent
        
        await gcp_create_workitem(work_item_id="dev-status-1", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_consent(
            work_item_id="dev-status-1",
            action="skip_dor",
            reason="PO approved spike exploration",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        result = await gcp_status(
            work_item_id="dev-status-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "deviations" in result
        assert len(result["deviations"]) == 1
        assert result["deviations"][0]["action"] == "skip_dor"
        assert result["deviations"][0]["reason"] == "PO approved spike exploration"

    @pytest.mark.asyncio
    async def test_status_empty_deviations_list(self):
        """Should return empty list when no deviations."""
        await gcp_create_workitem(work_item_id="dev-status-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="dev-status-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "deviations" in result
        assert result["deviations"] == []

    @pytest.mark.asyncio
    async def test_status_deviation_has_required_fields(self):
        """Should include id, action, reason, timestamp, consumed."""
        from golazo_copilot.tools.gcp_consent import gcp_consent
        
        await gcp_create_workitem(work_item_id="dev-status-3", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_consent(
            work_item_id="dev-status-3",
            action="skip_role",
            reason="Work already implemented - syncing state",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        result = await gcp_status(
            work_item_id="dev-status-3",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        deviation = result["deviations"][0]
        assert "id" in deviation
        assert "action" in deviation
        assert "reason" in deviation
        assert "timestamp" in deviation
        assert "consumed" in deviation


class TestStatusMissingNotes:
    """GCP-0019: Status should show missing role notes."""

    @pytest.mark.asyncio
    async def test_status_includes_missing_notes_list(self):
        """TC-04: Should list roles missing decision notes."""
        await gcp_create_workitem(work_item_id="missing-notes-1", work_items_dir=TEST_WORKITEMS_DIR)
        # Create PO notes before transition (required by blocking enforcement)
        create_role_notes("missing-notes-1", "project-owner-assistant")
        await gcp_transition(
            work_item_id="missing-notes-1",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        result = await gcp_status(
            work_item_id="missing-notes-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "missing_notes" in result
        # Current role (PM) is not checked, only completed roles
        # PO notes exist, so should not be in missing list

    @pytest.mark.asyncio
    async def test_status_all_notes_present_empty_list(self):
        """TC-05: Should return empty list when all notes exist."""
        await gcp_create_workitem(work_item_id="missing-notes-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create PO notes
        notes_dir = TEST_WORKITEMS_DIR / "missing-notes-2" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "missing-notes-2-project-owner-assistant.md").write_text("# PO Notes")
        
        result = await gcp_status(
            work_item_id="missing-notes-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "missing_notes" in result
        # Only PO role has been visited, and notes exist
        assert "project-owner-assistant" not in result["missing_notes"]
