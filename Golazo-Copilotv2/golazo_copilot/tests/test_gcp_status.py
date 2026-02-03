"""Tests for gcp_status tool."""

import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_init import gcp_init
from golazo_copilot.tools.gcp_transition import gcp_transition
from golazo_copilot.tools.gcp_mark import gcp_mark_dor
from golazo_copilot.tools.gcp_status import gcp_status


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)


class TestStatusBasic:
    """Basic status tests."""

    @pytest.mark.asyncio
    async def test_returns_active_status(self):
        """Should return active=True for initialized work item."""
        await gcp_init(work_item_id="status-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="status-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["active"] is True
        assert result["work_item_id"] == "status-1"

    @pytest.mark.asyncio
    async def test_returns_current_role_and_phase(self):
        """Should return current role and phase."""
        await gcp_init(work_item_id="status-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="status-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["current_role"] == "project-owner-assistant"
        assert result["current_phase"] == "definition"

    @pytest.mark.asyncio
    async def test_returns_role_instructions(self):
        """Should return role instructions."""
        await gcp_init(work_item_id="status-3", work_items_dir=TEST_WORKITEMS_DIR)
        
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
        await gcp_init(work_item_id="dor-status-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="dor-status-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["dor"]["complete"] is False
        assert len(result["dor"]["missing"]) == 4

    @pytest.mark.asyncio
    async def test_dor_status_after_marking(self):
        """Should reflect marked items."""
        await gcp_init(work_item_id="dor-status-2", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_mark_dor(
            work_item_id="dor-status-2",
            items={"userStory": True, "designDoc": True},
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        result = await gcp_status(
            work_item_id="dor-status-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["dor"]["items"]["userStory"] is True
        assert result["dor"]["items"]["designDoc"] is True
        assert len(result["dor"]["missing"]) == 2


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
        await gcp_init(work_item_id="trans-status", work_items_dir=TEST_WORKITEMS_DIR)
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
