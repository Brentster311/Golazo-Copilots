"""Tests for gcp_mark_dor and gcp_mark_dod tools."""

import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_init import gcp_init
from golazo_copilot.tools.gcp_mark import gcp_mark_dor, gcp_mark_dod
from golazo_copilot.core.persistence import load_state


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)


class TestMarkDorSingle:
    """AC1: Mark single DoR item."""

    @pytest.mark.asyncio
    async def test_mark_user_story_complete(self):
        """Should mark userStory as complete."""
        await gcp_init(work_item_id="mark-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dor(
            work_item_id="mark-1",
            item="userStory",
            complete=True,
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["items"]["userStory"] is True
        
        state = load_state("mark-1", TEST_WORKITEMS_DIR)
        assert state.dor["userStory"] is True

    @pytest.mark.asyncio
    async def test_mark_updates_timestamp(self):
        """Should update updatedAt."""
        await gcp_init(work_item_id="mark-2", work_items_dir=TEST_WORKITEMS_DIR)
        state_before = load_state("mark-2", TEST_WORKITEMS_DIR)
        
        await gcp_mark_dor(
            work_item_id="mark-2",
            item="userStory",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        state_after = load_state("mark-2", TEST_WORKITEMS_DIR)
        assert state_after.updated_at > state_before.updated_at


class TestMarkDodSingle:
    """AC2: Mark single DoD item."""

    @pytest.mark.asyncio
    async def test_mark_tests_pass_complete(self):
        """Should mark testsPass as complete."""
        await gcp_init(work_item_id="dod-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dod(
            work_item_id="dod-1",
            item="testsPass",
            complete=True,
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["items"]["testsPass"] is True


class TestBulkUpdate:
    """AC3: Bulk update support."""

    @pytest.mark.asyncio
    async def test_mark_multiple_dor_items(self):
        """Should mark multiple items at once."""
        await gcp_init(work_item_id="bulk-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dor(
            work_item_id="bulk-1",
            items={"userStory": True, "designDoc": True},
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["items"]["userStory"] is True
        assert result["items"]["designDoc"] is True
        assert result["items"]["reviewComments"] is False


class TestItemValidation:
    """AC4: Item validation."""

    @pytest.mark.asyncio
    async def test_invalid_dor_item_rejected(self):
        """Should reject unknown DoR item."""
        await gcp_init(work_item_id="invalid-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dor(
            work_item_id="invalid-1",
            item="userStories",  # Wrong name
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "Unknown" in result["error"] or "Invalid" in result["error"]

    @pytest.mark.asyncio
    async def test_invalid_dod_item_rejected(self):
        """Should reject unknown DoD item."""
        await gcp_init(work_item_id="invalid-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dod(
            work_item_id="invalid-2",
            item="testsPassing",  # Wrong name
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False


class TestUnmarking:
    """AC7: Unmarking items."""

    @pytest.mark.asyncio
    async def test_unmark_item(self):
        """Should unmark an item with warning."""
        await gcp_init(work_item_id="unmark-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        # First mark it
        await gcp_mark_dor(
            work_item_id="unmark-1",
            item="userStory",
            complete=True,
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        # Then unmark
        result = await gcp_mark_dor(
            work_item_id="unmark-1",
            item="userStory",
            complete=False,
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["items"]["userStory"] is False
        assert "warning" in result


class TestGateStatus:
    """AC8: Gate status calculation."""

    @pytest.mark.asyncio
    async def test_complete_flag_false_when_missing(self):
        """Should show complete=False when items missing."""
        await gcp_init(work_item_id="gate-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dor(
            work_item_id="gate-1",
            item="userStory",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["complete"] is False
        assert "missing" in result
        assert len(result["missing"]) == 3

    @pytest.mark.asyncio
    async def test_complete_flag_true_when_all_done(self):
        """Should show complete=True when all items done."""
        await gcp_init(work_item_id="gate-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dor(
            work_item_id="gate-2",
            items={
                "userStory": True,
                "designDoc": True,
                "reviewComments": True,
                "testCases": True
            },
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["complete"] is True
        assert len(result["missing"]) == 0


class TestErrorCases:
    """Error handling."""

    @pytest.mark.asyncio
    async def test_no_work_item(self):
        """Should error if no work item."""
        result = await gcp_mark_dor(
            work_item_id="nonexistent",
            item="userStory",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "not found" in result["error"].lower() or "does not exist" in result["error"].lower()
