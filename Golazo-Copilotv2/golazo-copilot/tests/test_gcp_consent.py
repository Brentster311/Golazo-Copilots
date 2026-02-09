"""Tests for gcp_consent tool."""

import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_create_workitem import gcp_create_workitem
from golazo_copilot.tools.gcp_transition import gcp_transition, ROLE_SUFFIX_MAP
from golazo_copilot.tools.gcp_consent import gcp_consent
from golazo_copilot.core.persistence import load_state, save_state


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"
TEST_WORKSPACE = Path(__file__).parent / "test-consent-workspace"
TEST_CONSENT_WORKITEMS_DIR = TEST_WORKSPACE / "WorkItems"
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
    if TEST_WORKSPACE.exists():
        shutil.rmtree(TEST_WORKSPACE)
    create_empty_role_files()
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    if TEST_WORKSPACE.exists():
        shutil.rmtree(TEST_WORKSPACE)
    roles_dir = TEST_WORKSPACE_ROOT / ".github"
    if roles_dir.exists():
        shutil.rmtree(roles_dir)


class TestConsentRecordsDeviation:
    """AC1: gcp_consent records deviation in state."""

    @pytest.mark.asyncio
    async def test_consent_records_deviation(self):
        """Should record deviation in state."""
        await gcp_create_workitem(work_item_id="consent-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_consent(
            work_item_id="consent-1",
            action="skip_outputs",
            reason="Spike exploration - will complete outputs after proof of concept",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        state = load_state("consent-1", TEST_WORKITEMS_DIR)
        assert len(state.deviations) == 1
        assert state.deviations[0].action == "skip_outputs"

    @pytest.mark.asyncio
    async def test_consent_returns_deviation_id(self):
        """Should return deviation ID."""
        await gcp_create_workitem(work_item_id="consent-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_consent(
            work_item_id="consent-2",
            action="skip_outputs",
            reason="Testing deviation ID return",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "deviation_id" in result
        assert result["deviation_id"].startswith("dev-")


class TestConsentRequiredForForce:
    """AC2: Consent required before forced transition (output validation bypass)."""

    def _create_role_file_with_output(self):
        """Create a PO role file with required output in the consent workspace."""
        role_path = TEST_WORKSPACE / ".github" / "roles" / "project-owner-assistant.md"
        role_path.parent.mkdir(parents=True, exist_ok=True)
        role_path.write_text("# Role: PO\n\n## Required Outputs\n- file: WorkItems/{id}/{id}-User-Story.md\n")

    @pytest.mark.asyncio
    async def test_force_fails_without_consent(self):
        """Should fail force transition without prior consent."""
        TEST_CONSENT_WORKITEMS_DIR.mkdir(parents=True, exist_ok=True)
        self._create_role_file_with_output()
        await gcp_create_workitem(work_item_id="force-1", work_items_dir=TEST_CONSENT_WORKITEMS_DIR)
        
        # Create role notes but NOT the required output
        notes_dir = TEST_CONSENT_WORKITEMS_DIR / "force-1" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "force-1-project-owner-assistant.md").write_text("# Notes")
        
        # Try to force without consent
        result = await gcp_transition(
            work_item_id="force-1",
            role="program-manager",
            force=True,
            work_items_dir=TEST_CONSENT_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )
        
        assert result["success"] is False
        assert "consent" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_force_succeeds_with_consent(self):
        """Should succeed force transition after consent."""
        TEST_CONSENT_WORKITEMS_DIR.mkdir(parents=True, exist_ok=True)
        self._create_role_file_with_output()
        await gcp_create_workitem(work_item_id="force-2", work_items_dir=TEST_CONSENT_WORKITEMS_DIR)
        
        # Create role notes but NOT the required output
        notes_dir = TEST_CONSENT_WORKITEMS_DIR / "force-2" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "force-2-project-owner-assistant.md").write_text("# Notes")
        
        # Give consent first
        await gcp_consent(
            work_item_id="force-2",
            action="skip_outputs",
            reason="Spike exploration - completing outputs later",
            work_items_dir=TEST_CONSENT_WORKITEMS_DIR
        )
        
        # Now force should work
        result = await gcp_transition(
            work_item_id="force-2",
            role="program-manager",
            force=True,
            work_items_dir=TEST_CONSENT_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )
        
        assert result["success"] is True


class TestConsentActions:
    """AC3: Supported consent actions."""

    @pytest.mark.asyncio
    async def test_skip_outputs_action(self):
        """Should accept skip_outputs action."""
        await gcp_create_workitem(work_item_id="action-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_consent(
            work_item_id="action-1",
            action="skip_outputs",
            reason="Testing skip_outputs action",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_action_rejected(self):
        """Should reject invalid action."""
        await gcp_create_workitem(work_item_id="action-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_consent(
            work_item_id="action-2",
            action="invalid_action",
            reason="Testing invalid action",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "action" in result["error"].lower()


class TestReasonRequired:
    """AC4: Reason is required."""

    @pytest.mark.asyncio
    async def test_consent_without_reason_fails(self):
        """Should fail without reason."""
        await gcp_create_workitem(work_item_id="reason-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_consent(
            work_item_id="reason-1",
            action="skip_outputs",
            reason="",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "reason" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_short_reason_fails(self):
        """Should fail with reason < 10 characters."""
        await gcp_create_workitem(work_item_id="reason-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_consent(
            work_item_id="reason-2",
            action="skip_outputs",
            reason="short",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "10" in result["error"] or "characters" in result["error"].lower()


class TestDeviationAuditTrail:
    """AC5: Deviation audit trail."""

    @pytest.mark.asyncio
    async def test_deviation_has_required_fields(self):
        """Should record all required fields."""
        await gcp_create_workitem(work_item_id="audit-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        await gcp_consent(
            work_item_id="audit-1",
            action="skip_outputs",
            reason="Spike exploration - will complete outputs later",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        state = load_state("audit-1", TEST_WORKITEMS_DIR)
        deviation = state.deviations[0]
        
        assert deviation.id is not None
        assert deviation.action is not None
        assert deviation.reason is not None
        assert deviation.role is not None
        assert deviation.timestamp is not None


class TestConsentSingleUse:
    """AC6: Consent is single-use."""

    def _create_role_file_with_output(self):
        """Create a PO role file with required output in the consent workspace."""
        role_path = TEST_WORKSPACE / ".github" / "roles" / "project-owner-assistant.md"
        role_path.parent.mkdir(parents=True, exist_ok=True)
        role_path.write_text("# Role: PO\n\n## Required Outputs\n- file: WorkItems/{id}/{id}-User-Story.md\n")
        # Also create PM role file with no outputs
        pm_role = TEST_WORKSPACE / ".github" / "roles" / "program-manager.md"
        pm_role.write_text("# Role: PM\n\n## Purpose\nTest role.\n")

    @pytest.mark.asyncio
    async def test_consent_consumed_after_use(self):
        """Should consume consent after forced action."""
        TEST_CONSENT_WORKITEMS_DIR.mkdir(parents=True, exist_ok=True)
        self._create_role_file_with_output()
        await gcp_create_workitem(work_item_id="single-1", work_items_dir=TEST_CONSENT_WORKITEMS_DIR)
        
        # Create role notes but NOT the required output
        notes_dir = TEST_CONSENT_WORKITEMS_DIR / "single-1" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "single-1-project-owner-assistant.md").write_text("# Notes")
        
        # Give consent
        await gcp_consent(
            work_item_id="single-1",
            action="skip_outputs",
            reason="First force - spike exploration",
            work_items_dir=TEST_CONSENT_WORKITEMS_DIR
        )
        
        # First force succeeds
        result1 = await gcp_transition(
            work_item_id="single-1",
            role="program-manager",
            force=True,
            work_items_dir=TEST_CONSENT_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )
        assert result1["success"] is True
        
        # Create PM notes then go back to PO
        (notes_dir / "single-1-program-manager.md").write_text("# PM Notes")
        await gcp_transition(
            work_item_id="single-1",
            role="project-owner-assistant",
            work_items_dir=TEST_CONSENT_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )
        
        # Second force fails (consent consumed)
        (notes_dir / "single-1-project-owner-assistant.md").write_text("# PO Notes 2")
        result2 = await gcp_transition(
            work_item_id="single-1",
            role="program-manager",
            force=True,
            work_items_dir=TEST_CONSENT_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )
        assert result2["success"] is False
        assert "consent" in result2["error"].lower()


class TestConsentMessageFormat:
    """GCP-0014: Consent message should indicate Project Owner."""

    @pytest.mark.asyncio
    async def test_consent_message_mentions_project_owner(self):
        """Should include 'Project Owner' in success message."""
        await gcp_create_workitem(work_item_id="po-msg-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_consent(
            work_item_id="po-msg-1",
            action="skip_outputs",
            reason="PO approved bypass for spike exploration",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert "project owner" in result["message"].lower()

