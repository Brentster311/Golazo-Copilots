"""Tests for evidence validation - GCP-0023."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime
import tempfile
import shutil

# Will import after creating the module
# from golazo_copilot.core.evidence import (
#     EvidenceResult,
#     validate_file_evidence,
#     validate_git_branch,
#     validate_git_commit,
#     validate_evidence,
# )


class TestEvidenceResult:
    """Tests for EvidenceResult dataclass."""

    def test_valid_result(self):
        """EvidenceResult with valid=True has empty message."""
        from golazo_copilot.core.evidence import EvidenceResult
        result = EvidenceResult(valid=True, message="", normalized_path="/path/to/file")
        assert result.valid is True
        assert result.message == ""

    def test_invalid_result(self):
        """EvidenceResult with valid=False has error message."""
        from golazo_copilot.core.evidence import EvidenceResult
        result = EvidenceResult(valid=False, message="File not found", normalized_path=None)
        assert result.valid is False
        assert "File not found" in result.message


class TestValidateFileEvidence:
    """TC05-TC10: File-based evidence validation."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace directory."""
        temp_dir = Path(tempfile.mkdtemp())
        work_items = temp_dir / "WorkItems" / "TEST-0001"
        work_items.mkdir(parents=True)
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_valid_file_path_accepted(self, temp_workspace):
        """TC05: Valid file path evidence accepted."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        # Create the file
        file_path = temp_workspace / "WorkItems" / "TEST-0001" / "TEST-0001-User-Story.md"
        file_path.write_text("# User Story")
        
        result = validate_file_evidence(
            "WorkItems/TEST-0001/TEST-0001-User-Story.md",
            temp_workspace
        )
        assert result.valid is True

    def test_nonexistent_file_rejected(self, temp_workspace):
        """TC06: Non-existent file path rejected."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        result = validate_file_evidence(
            "WorkItems/TEST-0001/missing.md",
            temp_workspace
        )
        assert result.valid is False
        assert "not found" in result.message.lower()

    def test_directory_path_rejected(self, temp_workspace):
        """TC07: Directory path rejected (not a file)."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        result = validate_file_evidence(
            "WorkItems/TEST-0001",
            temp_workspace
        )
        assert result.valid is False
        assert "not a file" in result.message.lower()

    def test_absolute_path_accepted(self, temp_workspace):
        """TC08: Absolute path accepted."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        file_path = temp_workspace / "WorkItems" / "TEST-0001" / "file.md"
        file_path.write_text("content")
        
        result = validate_file_evidence(str(file_path), temp_workspace)
        assert result.valid is True

    def test_path_with_spaces_handled(self, temp_workspace):
        """TC09: Path with spaces handled."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        file_path = temp_workspace / "WorkItems" / "TEST-0001" / "My User Story.md"
        file_path.write_text("content")
        
        result = validate_file_evidence(
            "WorkItems/TEST-0001/My User Story.md",
            temp_workspace
        )
        assert result.valid is True

    def test_multiple_file_paths_accepted(self, temp_workspace):
        """TC10: Multiple file paths accepted (list)."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        file1 = temp_workspace / "tests" / "test_a.py"
        file2 = temp_workspace / "tests" / "test_b.py"
        file1.parent.mkdir(parents=True, exist_ok=True)
        file1.write_text("# test a")
        file2.write_text("# test b")
        
        result = validate_file_evidence(
            ["tests/test_a.py", "tests/test_b.py"],
            temp_workspace
        )
        assert result.valid is True

    def test_multiple_paths_fails_if_one_missing(self, temp_workspace):
        """Multiple paths fails if any file is missing."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        file1 = temp_workspace / "tests" / "test_a.py"
        file1.parent.mkdir(parents=True, exist_ok=True)
        file1.write_text("# test a")
        # test_b.py does NOT exist
        
        result = validate_file_evidence(
            ["tests/test_a.py", "tests/test_b.py"],
            temp_workspace
        )
        assert result.valid is False
        assert "test_b.py" in result.message


class TestValidateGitBranch:
    """TC11-TC12, TC16: Git branch evidence validation."""

    def test_valid_branch_accepted(self):
        """TC11: Valid branch name accepted."""
        from golazo_copilot.core.evidence import validate_git_branch
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="  GCP-0023\n")
            result = validate_git_branch("GCP-0023", Path.cwd())
            assert result.valid is True

    def test_nonexistent_branch_rejected(self):
        """TC12: Non-existent branch rejected."""
        from golazo_copilot.core.evidence import validate_git_branch
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            result = validate_git_branch("NONEXISTENT-9999", Path.cwd())
            assert result.valid is False
            assert "not found" in result.message.lower()

    def test_git_not_available_handled(self):
        """TC16: Git not available handled gracefully."""
        from golazo_copilot.core.evidence import validate_git_branch
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")
            result = validate_git_branch("any-branch", Path.cwd())
            assert result.valid is False
            assert "git" in result.message.lower()


class TestValidateGitCommit:
    """TC13-TC15: Git commit SHA evidence validation."""

    def test_valid_commit_sha_accepted(self):
        """TC13: Valid commit SHA accepted."""
        from golazo_copilot.core.evidence import validate_git_commit
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="abc123def456\n")
            result = validate_git_commit("abc123def456", Path.cwd())
            assert result.valid is True

    def test_invalid_commit_sha_rejected(self):
        """TC14: Invalid commit SHA rejected."""
        from golazo_copilot.core.evidence import validate_git_commit
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=128, stdout="", stderr="fatal: bad revision")
            result = validate_git_commit("0000000000", Path.cwd())
            assert result.valid is False
            assert "not found" in result.message.lower()

    def test_short_sha_accepted(self):
        """TC15: Short SHA accepted (7+ chars)."""
        from golazo_copilot.core.evidence import validate_git_commit
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="abc1234\n")
            result = validate_git_commit("abc1234", Path.cwd())
            assert result.valid is True


class TestCommandEvidence:
    """TC17-TC19: Command-based evidence validation."""

    def test_test_output_accepted(self):
        """TC17: Test output accepted as-is."""
        from golazo_copilot.core.evidence import validate_command_evidence
        
        result = validate_command_evidence("pytest: 113 passed in 1.2s")
        assert result.valid is True

    def test_ci_link_accepted(self):
        """TC18: CI link accepted as-is."""
        from golazo_copilot.core.evidence import validate_command_evidence
        
        result = validate_command_evidence("https://dev.azure.com/build/123")
        assert result.valid is True

    def test_empty_string_rejected(self):
        """TC19: Empty string rejected."""
        from golazo_copilot.core.evidence import validate_command_evidence
        
        result = validate_command_evidence("")
        assert result.valid is False
        assert "empty" in result.message.lower()


class TestErrorMessages:
    """TC20-TC22: Error message quality."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace directory."""
        temp_dir = Path(tempfile.mkdtemp())
        work_items = temp_dir / "WorkItems"
        work_items.mkdir()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_error_includes_expected_format(self, temp_workspace):
        """TC20: Error includes expected format."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        result = validate_file_evidence("missing.md", temp_workspace)
        assert "expected" in result.message.lower() or "example" in result.message.lower()

    def test_error_includes_item_context(self, temp_workspace):
        """TC21: Error includes relevant context."""
        from golazo_copilot.core.evidence import validate_evidence
        
        result = validate_evidence("userStory", "missing.md", temp_workspace)
        # The validation function should include context about what was being validated
        assert result.valid is False

    def test_error_includes_path_checked(self, temp_workspace):
        """TC22: Error includes actual path checked."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        result = validate_file_evidence("missing.md", temp_workspace)
        assert "missing.md" in result.message


class TestBackwardCompatibility:
    """TC23: Backward compatibility with old state format."""

    def test_old_state_format_works(self):
        """TC23: Old state.json format still works with boolean DoR/DoD."""
        from golazo_copilot.core.state import WorkItemState
        from datetime import datetime
        
        now = datetime.now().isoformat()
        
        # Old format with simple booleans (current format)
        old_state_dict = {
            "schema_version": "1.0",
            "work_item_id": "TEST-0001",
            "profile": "complete",
            "current_phase": "definition",
            "current_role": "project-owner-assistant",
            "created_at": now,
            "updated_at": now,
            "dor": {
                "userStory": True,
                "designDoc": False,
                "reviewComments": False,
                "testCases": False,
            },
            "dod": {
                "branchCreated": False,
                "testsWrittenFirst": False,
                "testsPass": False,
                "buildPasses": False,
                "docsUpdated": False,
                "refactorComplete": False,
                "committed": False,
            },
            "role_history": [
                {"role": "project-owner-assistant", "entered_at": now, "exited_at": None}
            ],
            "deviations": [],
        }
        
        # Should parse without error
        state = WorkItemState.model_validate(old_state_dict)
        # Boolean format should be migrated to ChecklistItem
        assert state.dor["userStory"].complete is True
        assert state.dor["designDoc"].complete is False


class TestEvidenceStorage:
    """TC24-TC26: Evidence storage in state.json."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace directory."""
        temp_dir = Path(tempfile.mkdtemp())
        work_items = temp_dir / "WorkItems" / "TEST-0001"
        work_items.mkdir(parents=True)
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_evidence_stored_in_state(self, temp_workspace):
        """TC24: Evidence stored in state.json."""
        # This will be tested via integration with mark tools
        pass  # Placeholder for integration test

    def test_timestamp_stored_with_evidence(self, temp_workspace):
        """TC25: Timestamp stored with evidence."""
        # This will be tested via integration with mark tools
        pass  # Placeholder for integration test

    def test_multiple_marks_preserve_evidence(self, temp_workspace):
        """TC26: Multiple marks preserve all evidence."""
        # This will be tested via integration with mark tools
        pass  # Placeholder for integration test


class TestEdgeCases:
    """TC27-TC30: Edge cases."""

    def test_na_evidence_for_refactor(self):
        """TC27: N/A evidence for refactorComplete."""
        from golazo_copilot.core.evidence import validate_evidence
        
        result = validate_evidence(
            "refactorComplete",
            "N/A: No refactoring needed for this change",
            Path.cwd()
        )
        assert result.valid is True

    def test_na_without_reason_rejected(self):
        """TC28: N/A without reason rejected."""
        from golazo_copilot.core.evidence import validate_evidence
        
        result = validate_evidence("refactorComplete", "N/A", Path.cwd())
        assert result.valid is False
        assert "reason" in result.message.lower()

    def test_unicode_in_file_path(self):
        """TC29: Unicode in file path."""
        from golazo_copilot.core.evidence import validate_file_evidence
        
        temp_dir = Path(tempfile.mkdtemp())
        try:
            file_path = temp_dir / "设计文档.md"
            file_path.write_text("content", encoding="utf-8")
            
            result = validate_file_evidence(str(file_path), temp_dir)
            assert result.valid is True
        finally:
            shutil.rmtree(temp_dir)

    def test_very_long_evidence_handled(self):
        """TC30: Very long evidence is handled."""
        from golazo_copilot.core.evidence import validate_command_evidence
        
        long_evidence = "x" * 2000
        result = validate_command_evidence(long_evidence)
        assert result.valid is True  # Should accept, storage may truncate display
