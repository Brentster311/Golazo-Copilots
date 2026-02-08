"""Tests for output_validator module - GCP-0025."""

import subprocess
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.core.output_validator import (
    parse_required_outputs,
    validate_output,
    validate_all_outputs,
    OutputSpec,
    ValidationResult,
)


class TestParseRequiredOutputs:
    """TC1: Parse Required Outputs Section."""

    def test_parse_file_output(self):
        """TC1.1: Parse 'file: path/to/file.md' from role file."""
        content = """
# Role: Test

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
"""
        outputs = parse_required_outputs(content, "GCP-0025")
        assert len(outputs) == 1
        assert outputs[0].type == "file"
        assert outputs[0].path_or_pattern == "WorkItems/GCP-0025/GCP-0025-User-Story.md"

    def test_parse_dir_output(self):
        """TC1.2: Parse 'dir: path/to/dir' from role file."""
        content = """
## Required Outputs
- dir: WorkItems/{id}/Design
"""
        outputs = parse_required_outputs(content, "GCP-0025")
        assert len(outputs) == 1
        assert outputs[0].type == "dir"
        assert outputs[0].path_or_pattern == "WorkItems/GCP-0025/Design"

    def test_parse_git_branch_output(self):
        """TC1.3: Parse 'git-branch: pattern' from role file."""
        content = """
## Required Outputs
- git-branch: feature/{id}*
"""
        outputs = parse_required_outputs(content, "GCP-0025")
        assert len(outputs) == 1
        assert outputs[0].type == "git-branch"
        assert outputs[0].path_or_pattern == "feature/GCP-0025*"

    def test_parse_git_log_output(self):
        """TC1.3b: Parse 'git-log: pattern' from role file."""
        content = """
## Required Outputs
- git-log: {id}
"""
        outputs = parse_required_outputs(content, "GCP-0025")
        assert len(outputs) == 1
        assert outputs[0].type == "git-log"
        assert outputs[0].path_or_pattern == "GCP-0025"

    def test_parse_multiple_outputs(self):
        """TC1.4: Parse multiple output lines."""
        content = """
## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- file: WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md
- dir: WorkItems/{id}/Design
"""
        outputs = parse_required_outputs(content, "GCP-0025")
        assert len(outputs) == 3

    def test_parse_missing_section(self):
        """TC1.5: Return empty list if no Required Outputs section."""
        content = "# Role: Test\n\nNo outputs here."
        outputs = parse_required_outputs(content, "GCP-0025")
        assert outputs == []

    def test_parse_empty_section(self):
        """TC1.6: Return empty list if Required Outputs section is empty."""
        content = """
## Required Outputs

## Next Section
Some content here.
"""
        outputs = parse_required_outputs(content, "GCP-0025")
        assert outputs == []

    def test_parse_ignores_comments(self):
        """TC1.7: Ignore HTML comments in Required Outputs section."""
        content = """
## Required Outputs
<!-- This is validated on exit -->
- file: WorkItems/{id}/{id}-User-Story.md
"""
        outputs = parse_required_outputs(content, "GCP-0025")
        assert len(outputs) == 1
        assert outputs[0].type == "file"


class TestValidateFileOutput:
    """TC2: Validate File Output."""

    def test_validate_file_exists(self, tmp_path):
        """TC2.1: Return valid when file exists."""
        (tmp_path / "test.md").touch()
        spec = OutputSpec(type="file", path_or_pattern="test.md")
        result = validate_output(spec, tmp_path)
        assert result["valid"] is True

    def test_validate_file_not_exists(self, tmp_path):
        """TC2.2: Return invalid with clear message when file missing."""
        spec = OutputSpec(type="file", path_or_pattern="missing.md")
        result = validate_output(spec, tmp_path)
        assert result["valid"] is False
        assert "missing.md" in result["message"]

    def test_validate_file_is_directory(self, tmp_path):
        """TC2.3: Return invalid when path exists but is a directory."""
        (tmp_path / "subdir").mkdir()
        spec = OutputSpec(type="file", path_or_pattern="subdir")
        result = validate_output(spec, tmp_path)
        assert result["valid"] is False
        assert "not a file" in result["message"].lower() or "directory" in result["message"].lower()


class TestValidateDirOutput:
    """TC3: Validate Directory Output."""

    def test_validate_dir_exists(self, tmp_path):
        """TC3.1: Return valid when directory exists."""
        (tmp_path / "Design").mkdir()
        spec = OutputSpec(type="dir", path_or_pattern="Design")
        result = validate_output(spec, tmp_path)
        assert result["valid"] is True

    def test_validate_dir_not_exists(self, tmp_path):
        """TC3.2: Return invalid when directory missing."""
        spec = OutputSpec(type="dir", path_or_pattern="Missing")
        result = validate_output(spec, tmp_path)
        assert result["valid"] is False


class TestValidateGitBranchOutput:
    """TC4: Validate Git Branch Output."""

    def test_validate_git_branch_exists(self, tmp_path, monkeypatch):
        """TC4.1: Return valid when git branch exists."""
        def mock_run(*args, **kwargs):
            class Result:
                stdout = "  feature/GCP-0025-refactor\n"
                stderr = ""
                returncode = 0
            return Result()
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        spec = OutputSpec(type="git-branch", path_or_pattern="feature/GCP-0025*")
        result = validate_output(spec, tmp_path)
        assert result["valid"] is True

    def test_validate_git_branch_not_exists(self, tmp_path, monkeypatch):
        """TC4.2: Return invalid when no matching branch."""
        def mock_run(*args, **kwargs):
            class Result:
                stdout = ""
                stderr = ""
                returncode = 0
            return Result()
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        spec = OutputSpec(type="git-branch", path_or_pattern="feature/GCP-9999*")
        result = validate_output(spec, tmp_path)
        assert result["valid"] is False


class TestValidateGitLogOutput:
    """TC4b: Validate Git Log Output."""

    def test_validate_git_log_exists(self, tmp_path, monkeypatch):
        """Return valid when commit message matches pattern."""
        def mock_run(*args, **kwargs):
            class Result:
                stdout = "abc1234 feat: GCP-0025 initial commit\n"
                stderr = ""
                returncode = 0
            return Result()
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        spec = OutputSpec(type="git-log", path_or_pattern="GCP-0025")
        result = validate_output(spec, tmp_path)
        assert result["valid"] is True

    def test_validate_git_log_not_exists(self, tmp_path, monkeypatch):
        """Return invalid when no commit matches pattern."""
        def mock_run(*args, **kwargs):
            class Result:
                stdout = ""
                stderr = ""
                returncode = 0
            return Result()
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        spec = OutputSpec(type="git-log", path_or_pattern="GCP-9999")
        result = validate_output(spec, tmp_path)
        assert result["valid"] is False


class TestValidateAllOutputs:
    """TC5 partial: Validate all outputs at once."""

    def test_all_valid(self, tmp_path):
        """Return valid when all outputs exist."""
        (tmp_path / "file.md").touch()
        (tmp_path / "dir").mkdir()
        
        specs = [
            OutputSpec(type="file", path_or_pattern="file.md"),
            OutputSpec(type="dir", path_or_pattern="dir"),
        ]
        result = validate_all_outputs(specs, tmp_path)
        assert result.valid is True
        assert len(result.outputs) == 2

    def test_some_invalid(self, tmp_path):
        """Return invalid when some outputs missing."""
        (tmp_path / "file.md").touch()
        # dir not created
        
        specs = [
            OutputSpec(type="file", path_or_pattern="file.md"),
            OutputSpec(type="dir", path_or_pattern="missing-dir"),
        ]
        result = validate_all_outputs(specs, tmp_path)
        assert result.valid is False
        assert "missing-dir" in result.message

    def test_empty_specs(self, tmp_path):
        """Return valid when no outputs required."""
        result = validate_all_outputs([], tmp_path)
        assert result.valid is True
