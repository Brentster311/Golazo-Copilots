"""
Tests for Golazo_Copilot.py

Run with: pytest tests/test_golazo_copilot.py -v
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Golazo_Copilot import (
    find_repo_root,
    get_script_directory,
    ensure_directory,
    copy_file,
    install_golazo,
    main,
)


class TestFindRepoRoot:
    """Tests for find_repo_root function."""
    
    def test_finds_repo_root_from_subdirectory(self):
        """TC-001: Find repo root when .git exists in parent directory."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Create .git directory
            (tmp_path / ".git").mkdir()
            # Create nested subdirectory
            nested = tmp_path / "subdir" / "nested"
            nested.mkdir(parents=True)
            
            result = find_repo_root(nested)
            
            assert result == tmp_path
    
    def test_returns_none_when_not_in_repo(self):
        """TC-002: Return None when not in a git repository."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # No .git directory
            
            result = find_repo_root(tmp_path)
            
            assert result is None
    
    def test_finds_repo_root_at_root(self):
        """TC-003: Find repo root when already at root."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / ".git").mkdir()
            
            result = find_repo_root(tmp_path)
            
            assert result == tmp_path


class TestGetScriptDirectory:
    """Tests for get_script_directory function."""
    
    def test_returns_script_location(self):
        """TC-004: Get directory containing the script."""
        result = get_script_directory()
        
        assert result.is_dir()
        assert (result / "Golazo_Copilot.py").exists()


class TestEnsureDirectory:
    """Tests for ensure_directory function."""
    
    def test_creates_missing_directory(self):
        """TC-005: Create directory when it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            new_dir = tmp_path / "new" / "nested" / "dir"
            
            ensure_directory(new_dir)
            
            assert new_dir.exists()
            assert new_dir.is_dir()
    
    def test_handles_existing_directory(self):
        """TC-006: No error when directory already exists."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            existing = tmp_path / "existing"
            existing.mkdir()
            
            # Should not raise
            ensure_directory(existing)
            
            assert existing.exists()


class TestCopyFile:
    """Tests for copy_file function."""
    
    def test_copies_file_successfully(self):
        """TC-007: Copy file to destination."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.txt"
            source.write_text("test content")
            destination = tmp_path / "destination.txt"
            
            result = copy_file(source, destination)
            
            assert result is True
            assert destination.exists()
            assert destination.read_text() == "test content"
    
    def test_overwrites_existing_file(self):
        """TC-008: Overwrite existing destination file."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.txt"
            source.write_text("new content")
            destination = tmp_path / "destination.txt"
            destination.write_text("old content")
            
            result = copy_file(source, destination)
            
            assert result is True
            assert destination.read_text() == "new content"


class TestInstallGolazo:
    """Tests for install_golazo function."""
    
    def test_full_installation(self):
        """TC-009: Install all Golazo files to target repo."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / ".git").mkdir()
            
            result = install_golazo(tmp_path)
            
            assert result is True
            assert (tmp_path / ".github" / "copilot-instructions.md").exists()
            assert (tmp_path / ".github" / "roles").is_dir()
            # Check at least some role files exist
            role_files = list((tmp_path / ".github" / "roles").glob("*.md"))
            assert len(role_files) >= 10


class TestMain:
    """Tests for main function."""
    
    def test_exit_code_0_on_success(self, monkeypatch):
        """TC-010: CLI returns 0 on successful installation."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / ".git").mkdir()
            original_cwd = Path.cwd()
            try:
                monkeypatch.chdir(tmp_path)
                result = main()
                assert result == 0
            finally:
                monkeypatch.chdir(original_cwd)
    
    def test_exit_code_1_when_not_in_repo(self, monkeypatch):
        """TC-011: CLI returns 1 when not in git repo."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # No .git directory
            original_cwd = Path.cwd()
            try:
                monkeypatch.chdir(tmp_path)
                result = main()
                assert result == 1
            finally:
                monkeypatch.chdir(original_cwd)


class TestReadme:
    """Tests for README.md content."""
    
    def test_readme_exists(self):
        """TC-014: README.md file exists at repo root."""
        script_dir = get_script_directory()
        readme = script_dir / "README.md"
        
        assert readme.exists(), "README.md should exist at project root"
    
    def test_readme_contains_required_sections(self):
        """TC-015: README has all required sections."""
        script_dir = get_script_directory()
        readme = script_dir / "README.md"
        
        if not readme.exists():
            pytest.skip("README.md not yet created")
        
        content = readme.read_text().lower()
        
        # Check for Golazo explanation
        assert "golazo" in content, "README should explain what Golazo is"
        
        # Check for role mentions
        roles = [
            "project owner", "program manager", "reviewer", "architect",
            "tester", "developer", "refactor", "builder", "documentor", "retrospective"
        ]
        for role in roles:
            assert role in content, f"README should mention {role} role"
        
        # Check for artifact structure
        assert "workitems" in content, "README should document WorkItems structure"
        
        # Check for retrospective example
        assert "retrospective" in content and "example" in content, \
            "README should include retrospective example"
