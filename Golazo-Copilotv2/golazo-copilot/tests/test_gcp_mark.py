"""Tests for gcp_mark_dor and gcp_mark_dod tools."""

import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_create_workitem import gcp_create_workitem
from golazo_copilot.tools.gcp_mark import gcp_mark_dor, gcp_mark_dod
from golazo_copilot.core.persistence import load_state


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"


def create_test_file(work_item_id: str, filename: str) -> str:
    """Create a test file and return its path."""
    path = TEST_WORKITEMS_DIR / work_item_id / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Test content")
    return str(path)


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
        """Should mark userStory as complete with evidence."""
        await gcp_create_workitem(work_item_id="mark-1", work_items_dir=TEST_WORKITEMS_DIR)
        evidence_path = create_test_file("mark-1", "mark-1-User-Story.md")
        
        result = await gcp_mark_dor(
            work_item_id="mark-1",
            item="userStory",
            complete=True,
            evidence=evidence_path,
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["items"]["userStory"] is True
        
        state = load_state("mark-1", TEST_WORKITEMS_DIR)
        assert state.dor["userStory"].complete is True
        assert state.dor["userStory"].evidence is not None

    @pytest.mark.asyncio
    async def test_mark_updates_timestamp(self):
        """Should update updatedAt."""
        await gcp_create_workitem(work_item_id="mark-2", work_items_dir=TEST_WORKITEMS_DIR)
        evidence_path = create_test_file("mark-2", "mark-2-User-Story.md")
        state_before = load_state("mark-2", TEST_WORKITEMS_DIR)
        
        await gcp_mark_dor(
            work_item_id="mark-2",
            item="userStory",
            evidence=evidence_path,
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        state_after = load_state("mark-2", TEST_WORKITEMS_DIR)
        assert state_after.updated_at > state_before.updated_at


class TestMarkDodSingle:
    """AC2: Mark single DoD item."""

    @pytest.mark.asyncio
    async def test_mark_tests_pass_complete(self):
        """Should mark testsPass as complete with evidence."""
        await gcp_create_workitem(work_item_id="dod-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dod(
            work_item_id="dod-1",
            item="testsPass",
            complete=True,
            evidence="pytest output: 29 passed",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["items"]["testsPass"] is True


class TestBulkUpdate:
    """AC3: Bulk update support."""

    @pytest.mark.asyncio
    async def test_mark_multiple_dor_items(self):
        """Should mark multiple items at once with evidence."""
        await gcp_create_workitem(work_item_id="bulk-1", work_items_dir=TEST_WORKITEMS_DIR)
        create_test_file("bulk-1", "bulk-1-User-Story.md")
        create_test_file("bulk-1", "design-doc.md")
        
        result = await gcp_mark_dor(
            work_item_id="bulk-1",
            items={"userStory": True, "designDoc": True},
            evidence="bulk-1-User-Story.md, design-doc.md",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["items"]["userStory"] is True
        assert result["items"]["designDoc"] is True
        assert result["items"]["reviewComments"] is False


class TestEvidenceRequired:
    """Evidence is required when marking complete."""

    @pytest.mark.asyncio
    async def test_mark_without_evidence_fails(self):
        """Should fail without evidence for marking complete."""
        await gcp_create_workitem(work_item_id="noevidence", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dor(
            work_item_id="noevidence",
            item="userStory",
            complete=True,
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "evidence" in result["error"].lower() or "missing" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_invalid_file_evidence_fails(self):
        """Should fail with invalid file evidence."""
        await gcp_create_workitem(work_item_id="badfile", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dor(
            work_item_id="badfile",
            item="userStory",
            evidence="/nonexistent/file.md",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "not found" in result["error"].lower() or "does not exist" in result["error"].lower()


class TestItemValidation:
    """AC4: Item validation."""

    @pytest.mark.asyncio
    async def test_invalid_dor_item_rejected(self):
        """Should reject unknown DoR item."""
        await gcp_create_workitem(work_item_id="invalid-1", work_items_dir=TEST_WORKITEMS_DIR)
        
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
        await gcp_create_workitem(work_item_id="invalid-2", work_items_dir=TEST_WORKITEMS_DIR)
        
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
        """Should unmark an item with warning (no evidence required for unmarking)."""
        await gcp_create_workitem(work_item_id="unmark-1", work_items_dir=TEST_WORKITEMS_DIR)
        evidence_path = create_test_file("unmark-1", "unmark-1-User-Story.md")
        
        # First mark it with evidence
        await gcp_mark_dor(
            work_item_id="unmark-1",
            item="userStory",
            complete=True,
            evidence=evidence_path,
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        # Then unmark (no evidence needed for unmarking)
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
        await gcp_create_workitem(work_item_id="gate-1", work_items_dir=TEST_WORKITEMS_DIR)
        evidence_path = create_test_file("gate-1", "gate-1-User-Story.md")
        
        result = await gcp_mark_dor(
            work_item_id="gate-1",
            item="userStory",
            evidence=evidence_path,
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["complete"] is False
        assert "missing" in result
        assert len(result["missing"]) == 3

    @pytest.mark.asyncio
    async def test_complete_flag_true_when_all_done(self):
        """Should show complete=True when all items done."""
        await gcp_create_workitem(work_item_id="gate-2", work_items_dir=TEST_WORKITEMS_DIR)
        # Create test files for all DoR items
        create_test_file("gate-2", "gate-2-User-Story.md")
        create_test_file("gate-2", "design-doc.md")
        create_test_file("gate-2", "review-comments.md")
        create_test_file("gate-2", "test-cases.md")
        
        result = await gcp_mark_dor(
            work_item_id="gate-2",
            items={
                "userStory": True,
                "designDoc": True,
                "reviewComments": True,
                "testCases": True
            },
            evidence="gate-2-User-Story.md, design-doc.md, review-comments.md, test-cases.md",
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


class TestBranchCreatedEvidence:
    """Tests for branchCreated DoD item with git branch evidence."""

    @pytest.mark.asyncio
    async def test_branch_created_with_valid_branch(self, monkeypatch):
        """Should succeed when branch exists (simulates agent sending branchCreated)."""
        import subprocess
        
        await gcp_create_workitem(work_item_id="LLM-0004", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Mock git branch --list to return the branch name (simulating existing branch)
        def mock_run(*args, **kwargs):
            if args[0][0] == "git" and args[0][1] == "branch":
                class MockResult:
                    stdout = "* feature/LLM-0004-azure-openai-provider\n"
                    stderr = ""
                    returncode = 0
                return MockResult()
            return subprocess.run(*args, **kwargs)
        
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        # This simulates exactly what the agent sends:
        # {
        #   "complete": true,
        #   "evidence": "feature/LLM-0004-azure-openai-provider",
        #   "item": "branchCreated",
        #   "work_item_id": "LLM-0004",
        #   "workspace_path": "..."
        # }
        result = await gcp_mark_dod(
            work_item_id="LLM-0004",
            item="branchCreated",
            complete=True,
            evidence="feature/LLM-0004-azure-openai-provider",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True, f"Expected success but got: {result}"
        assert result["items"]["branchCreated"] is True
        assert result["evidence"] == "feature/LLM-0004-azure-openai-provider"

    @pytest.mark.asyncio
    async def test_branch_created_with_nonexistent_branch(self, monkeypatch):
        """Should fail when branch does not exist."""
        import subprocess
        
        await gcp_create_workitem(work_item_id="branch-fail", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Mock git branch --list to return empty (branch doesn't exist)
        def mock_run(*args, **kwargs):
            if args[0][0] == "git" and args[0][1] == "branch":
                class MockResult:
                    stdout = ""
                    stderr = ""
                    returncode = 0
                return MockResult()
            return subprocess.run(*args, **kwargs)
        
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        result = await gcp_mark_dod(
            work_item_id="branch-fail",
            item="branchCreated",
            complete=True,
            evidence="feature/nonexistent-branch",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "not found" in result["error"].lower() or "branch" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_branch_created_with_empty_evidence(self):
        """Should fail when branch name is empty."""
        await gcp_create_workitem(work_item_id="branch-empty", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_mark_dod(
            work_item_id="branch-empty",
            item="branchCreated",
            complete=True,
            evidence="",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "empty" in result["error"].lower() or "evidence" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_branch_created_with_formatted_evidence(self, monkeypatch):
        """Should extract branch name from 'git branch: name @ sha' format."""
        import subprocess
        
        await gcp_create_workitem(work_item_id="branch-fmt", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Mock git branch --list to return the branch name
        def mock_run(*args, **kwargs):
            if args[0][0] == "git" and args[0][1] == "branch":
                # Check that we're looking for the extracted branch name, not the full string
                branch_arg = args[0][3] if len(args[0]) > 3 else ""
                if branch_arg == "feature/LLM-0004-azure-openai-provider":
                    class MockResult:
                        stdout = "* feature/LLM-0004-azure-openai-provider\n"
                        stderr = ""
                        returncode = 0
                    return MockResult()
                # Return empty for the full string (would fail if not extracted)
                class MockResult:
                    stdout = ""
                    stderr = ""
                    returncode = 0
                return MockResult()
            return subprocess.run(*args, **kwargs)
        
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        # This is EXACTLY what the agent sends - formatted evidence with sha:
        result = await gcp_mark_dod(
            work_item_id="branch-fmt",
            item="branchCreated",
            complete=True,
            evidence="git branch: feature/LLM-0004-azure-openai-provider @ 2d2bd22",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True, f"Expected success but got: {result}"
        assert result["items"]["branchCreated"] is True
        # Should store the extracted branch name, not the full string
        assert result["evidence"] == "feature/LLM-0004-azure-openai-provider"

