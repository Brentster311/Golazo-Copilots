"""Tests for gcp_create_workitem tool."""

import json
import shutil
from pathlib import Path

import pytest

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_create_workitem import gcp_create_workitem
from golazo_copilot.core.persistence import load_state
from golazo_copilot.core.types import WorkItemState


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)


class TestGcpCreateWorkitemSuccess:
    """AC1: gcp_init creates work item with correct state."""

    @pytest.mark.asyncio
    async def test_creates_state_json(self):
        """Should create state.json file."""
        result = await gcp_create_workitem(
            work_item_id="FX-001",
            profile="complete",
            work_items_dir=TEST_WORKITEMS_DIR,
        )

        assert result["success"] is True
        state_path = TEST_WORKITEMS_DIR / "FX-001" / "state.json"
        assert state_path.exists()

    @pytest.mark.asyncio
    async def test_state_has_correct_schema_version(self):
        """Should set schema_version to 1.0."""
        await gcp_create_workitem(work_item_id="ST-001", work_items_dir=TEST_WORKITEMS_DIR)

        state = load_state("ST-001", TEST_WORKITEMS_DIR)
        assert state.schema_version == "1.0"

    @pytest.mark.asyncio
    async def test_state_has_correct_work_item_id(self):
        """Should set work_item_id correctly."""
        await gcp_create_workitem(work_item_id="MF-001", work_items_dir=TEST_WORKITEMS_DIR)

        state = load_state("MF-001", TEST_WORKITEMS_DIR)
        assert state.work_item_id == "MF-001"

    @pytest.mark.asyncio
    async def test_state_has_correct_profile(self):
        """Should set profile correctly."""
        await gcp_create_workitem(
            work_item_id="PT-001",
            profile="express",
            work_items_dir=TEST_WORKITEMS_DIR,
        )

        state = load_state("PT-001", TEST_WORKITEMS_DIR)
        assert state.profile == "express"

    @pytest.mark.asyncio
    async def test_defaults_profile_to_complete(self):
        """Should default profile to 'complete'."""
        await gcp_create_workitem(work_item_id="DP-001", work_items_dir=TEST_WORKITEMS_DIR)

        state = load_state("DP-001", TEST_WORKITEMS_DIR)
        assert state.profile == "complete"

    @pytest.mark.asyncio
    async def test_state_starts_in_definition_phase(self):
        """Should start in definition phase."""
        await gcp_create_workitem(work_item_id="PH-001", work_items_dir=TEST_WORKITEMS_DIR)

        state = load_state("PH-001", TEST_WORKITEMS_DIR)
        assert state.current_phase == "definition"

    @pytest.mark.asyncio
    async def test_state_starts_with_project_owner_role(self):
        """Should start with project-owner-assistant role."""
        await gcp_create_workitem(work_item_id="RT-001", work_items_dir=TEST_WORKITEMS_DIR)

        state = load_state("RT-001", TEST_WORKITEMS_DIR)
        assert state.current_role == "project-owner-assistant"

    @pytest.mark.asyncio
    async def test_state_has_no_dor_field(self):
        """GCP-0031: New state should not have dor field."""
        await gcp_create_workitem(work_item_id="ND-001", work_items_dir=TEST_WORKITEMS_DIR)

        state = load_state("ND-001", TEST_WORKITEMS_DIR)
        assert not hasattr(state, "dor") or "dor" not in state.model_fields

    @pytest.mark.asyncio
    async def test_state_has_no_dod_field(self):
        """GCP-0031: New state should not have dod field."""
        await gcp_create_workitem(work_item_id="ND-002", work_items_dir=TEST_WORKITEMS_DIR)

        state = load_state("ND-002", TEST_WORKITEMS_DIR)
        assert not hasattr(state, "dod") or "dod" not in state.model_fields

    @pytest.mark.asyncio
    async def test_role_history_has_initial_entry(self):
        """Should have project-owner in role history."""
        await gcp_create_workitem(work_item_id="HT-001", work_items_dir=TEST_WORKITEMS_DIR)

        state = load_state("HT-001", TEST_WORKITEMS_DIR)
        assert len(state.role_history) == 1
        assert state.role_history[0].role == "project-owner-assistant"
        assert state.role_history[0].exited_at is None

    @pytest.mark.asyncio
    async def test_deviations_empty(self):
        """Should initialize deviations as empty."""
        await gcp_create_workitem(work_item_id="DV-001", work_items_dir=TEST_WORKITEMS_DIR)

        state = load_state("DV-001", TEST_WORKITEMS_DIR)
        assert state.deviations == []

    @pytest.mark.asyncio
    async def test_creates_directory_if_not_exists(self):
        """Should create WorkItems directory if not exists."""
        assert not TEST_WORKITEMS_DIR.exists()

        await gcp_create_workitem(work_item_id="CD-001", work_items_dir=TEST_WORKITEMS_DIR)

        assert TEST_WORKITEMS_DIR.exists()


class TestGcpCreateWorkitemRoleInstructions:
    """AC2: Returns role instructions."""

    @pytest.mark.asyncio
    async def test_returns_role_instructions(self):
        """Should return role instructions on success."""
        result = await gcp_create_workitem(work_item_id="IT-001", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is True
        assert result["current_role"] == "project-owner-assistant"
        assert result["role_instructions"] is not None
        assert len(result["role_instructions"]) > 50


class TestGcpCreateWorkitemErrorHandling:
    """AC5: Error handling."""

    @pytest.mark.asyncio
    async def test_rejects_duplicate_work_item(self):
        """Should reject duplicate work item ID."""
        await gcp_create_workitem(work_item_id="DU-001", work_items_dir=TEST_WORKITEMS_DIR)

        result = await gcp_create_workitem(work_item_id="DU-001", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "already exists" in result["error"]
        assert "gcp_switch" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_empty_id(self):
        """Should reject empty work item ID."""
        result = await gcp_create_workitem(work_item_id="", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_spaces(self):
        """Should reject work item ID with spaces."""
        result = await gcp_create_workitem(work_item_id="has spaces", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_forward_slash(self):
        """Should reject work item ID with forward slash."""
        result = await gcp_create_workitem(work_item_id="has/slash", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_backslash(self):
        """Should reject work item ID with backslash."""
        result = await gcp_create_workitem(work_item_id="has\\backslash", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_accepts_standard_format(self):
        """GCP-0043: Should accept IDs matching pattern (1-4 letters, dash, 3+ digits)."""
        result = await gcp_create_workitem(work_item_id="GCP-0043", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_accepts_single_letter_prefix(self):
        """GCP-0043 TC2.1: Should accept minimum valid ID (1-letter prefix, 3-digit suffix)."""
        result = await gcp_create_workitem(work_item_id="A-001", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_accepts_four_letter_prefix(self):
        """GCP-0043 TC2.2: Should accept maximum-length prefix (4 letters)."""
        result = await gcp_create_workitem(work_item_id="TEST-1234", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_accepts_wip_fallback(self):
        """GCP-0043 TC2.4: WIP-000 must remain valid as the default fallback."""
        result = await gcp_create_workitem(work_item_id="WIP-000", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_accepts_long_digit_suffix(self):
        """GCP-0043 TC2.5: Suffixes longer than 3 digits should be accepted."""
        result = await gcp_create_workitem(work_item_id="GCP-99999", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_rejects_freeform_id(self):
        """GCP-0043 TC1.1: Should reject free-form IDs without proper format."""
        result = await gcp_create_workitem(work_item_id="feature-x", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_five_letter_prefix(self):
        """GCP-0043 TC1.2: Should reject prefix exceeding 4 letters."""
        result = await gcp_create_workitem(work_item_id="ABCDE-001", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_two_digit_suffix(self):
        """GCP-0043 TC1.3: Should reject suffix with fewer than 3 digits."""
        result = await gcp_create_workitem(work_item_id="GCP-01", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_underscore(self):
        """GCP-0043 TC1.4: Underscores should no longer be accepted."""
        result = await gcp_create_workitem(work_item_id="G_P-001", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_no_dash(self):
        """GCP-0043 TC1.5: Should reject ID without dash separator."""
        result = await gcp_create_workitem(work_item_id="GCP0001", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_digits_in_prefix(self):
        """GCP-0043 TC1.6: Prefix must be letters only."""
        result = await gcp_create_workitem(work_item_id="G2P-001", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_letters_in_suffix(self):
        """GCP-0043 TC1.7: Suffix must be digits only."""
        result = await gcp_create_workitem(work_item_id="GCP-00A", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_error_message_includes_examples(self):
        """GCP-0043 TC1.8: Error message must include example valid IDs."""
        result = await gcp_create_workitem(work_item_id="invalid", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "GCP-0001" in result["error"] or "AB-001" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_dot(self):
        """Should reject '.' as work item ID."""
        result = await gcp_create_workitem(work_item_id=".", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_dotdot(self):
        """Should reject '..' as work item ID."""
        result = await gcp_create_workitem(work_item_id="..", work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_too_long(self):
        """Should reject work item ID over 100 chars."""
        result = await gcp_create_workitem(work_item_id="a" * 101, work_items_dir=TEST_WORKITEMS_DIR)

        assert result["success"] is False
        assert "too long" in result["error"]

    @pytest.mark.asyncio
    async def test_rejects_invalid_profile(self):
        """Should reject invalid profile."""
        result = await gcp_create_workitem(
            work_item_id="IP-001",
            profile="invalid",
            work_items_dir=TEST_WORKITEMS_DIR,
        )

        assert result["success"] is False
        assert "Invalid profile" in result["error"]


class TestGcpBackwardCompatibility:
    """GCP-0031: Old state.json with dor/dod fields should load without error."""

    @pytest.mark.asyncio
    async def test_old_state_with_dor_dod_loads(self):
        """TC1.2: State files containing dor/dod should load silently."""
        # Create a new work item first (to get correct structure)
        await gcp_create_workitem(work_item_id="CP-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Manually inject legacy dor/dod into the state.json
        state_path = TEST_WORKITEMS_DIR / "CP-001" / "state.json"
        raw = json.loads(state_path.read_text())
        raw["dor"] = {"userStory": True, "designDoc": False, "reviewComments": False, "testCases": False}
        raw["dod"] = {"branchCreated": False, "testsWrittenFirst": False}
        state_path.write_text(json.dumps(raw))
        
        # Should load without error (extra="ignore" handles unknown fields)
        state = load_state("CP-001", TEST_WORKITEMS_DIR)
        assert state.work_item_id == "CP-001"
        assert state.current_role == "project-owner-assistant"
