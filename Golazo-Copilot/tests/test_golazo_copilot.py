"""
Tests for Golazo_Copilot.py

Run with: pytest tests/test_golazo_copilot.py -v
"""

import sys
import shutil
import tempfile
import zipfile
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
    create_package,
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







import os

class TestMain:
    """Tests for main function."""
    
    def test_exit_code_0_on_success(self, monkeypatch):
        """TC-010: CLI returns 0 on successful installation."""
        original_cwd = os.getcwd()
        tmp_path = None
        try:
            tmp_path = Path(tempfile.mkdtemp())
            (tmp_path / ".git").mkdir()
            monkeypatch.chdir(tmp_path)
            monkeypatch.setattr(sys, 'argv', ['Golazo_Copilot.py'])
            result = main()
            assert result == 0
        finally:
            os.chdir(original_cwd)
            if tmp_path:
                shutil.rmtree(tmp_path, ignore_errors=True)
    
    def test_exit_code_1_when_not_in_repo(self, monkeypatch):
        """TC-011: CLI returns 1 when not in git repo."""
        original_cwd = os.getcwd()
        tmp_path = None
        try:
            tmp_path = Path(tempfile.mkdtemp())
            # No .git directory
            monkeypatch.chdir(tmp_path)
            monkeypatch.setattr(sys, 'argv', ['Golazo_Copilot.py'])
            result = main()
            assert result == 1
        finally:
            os.chdir(original_cwd)
            if tmp_path:
                shutil.rmtree(tmp_path, ignore_errors=True)





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


class TestCreatePackage:
    """Tests for create_package function (GCP-005)."""
    
    def test_creates_zip_file(self):
        """TC-GCP005-001: Package creates valid zip file."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            result = create_package(output_zip)
            
            assert result is True
            assert output_zip.exists()
            assert zipfile.is_zipfile(output_zip)
    
    def test_contains_copilot_instructions(self):
        """TC-GCP005-002: Package contains .github/copilot-instructions.md."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            create_package(output_zip)
            
            with zipfile.ZipFile(output_zip, 'r') as zf:
                names = zf.namelist()
                assert ".github/copilot-instructions.md" in names
    
    def test_contains_all_role_files(self):
        """TC-GCP005-003: Package contains all role files."""
        expected_roles = [
            "architect.md", "builder.md", "developer.md", "documentor.md",
            "program-manager.md", "project-owner-assistant.md", "refactor-expert.md",
            "retrospective.md", "reviewer.md", "tester.md"
        ]
        
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            create_package(output_zip)
            
            with zipfile.ZipFile(output_zip, 'r') as zf:
                names = zf.namelist()
                for role in expected_roles:
                    expected_path = f".github/roles/{role}"
                    assert expected_path in names, f"Missing role file: {role}"
    
    def test_contains_readme(self):
        """TC-GCP005-004: Package contains README.md."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            create_package(output_zip)
            
            with zipfile.ZipFile(output_zip, 'r') as zf:
                names = zf.namelist()
                assert "README.md" in names
    
    def test_contains_usage_visual_studio(self):
        """TC-GCP005-005: Package contains USAGE-VisualStudio.md."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            create_package(output_zip)
            
            with zipfile.ZipFile(output_zip, 'r') as zf:
                names = zf.namelist()
                assert "USAGE-VisualStudio.md" in names
    
    def test_contains_usage_vscode(self):
        """TC-GCP005-006: Package contains USAGE-VSCode.md."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            create_package(output_zip)
            
            with zipfile.ZipFile(output_zip, 'r') as zf:
                names = zf.namelist()
                assert "USAGE-VSCode.md" in names
    
    def test_overwrites_existing_zip(self):
        """TC-GCP005-010: Package overwrites existing zip."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            # Create an existing zip with dummy content
            with zipfile.ZipFile(output_zip, 'w') as zf:
                zf.writestr("dummy.txt", "old content")
            
            old_size = output_zip.stat().st_size
            
            # Create new package
            result = create_package(output_zip)
            
            assert result is True
            new_size = output_zip.stat().st_size
            assert new_size != old_size  # Size changed, file was replaced
            
            # Verify new content
            with zipfile.ZipFile(output_zip, 'r') as zf:
                names = zf.namelist()
                assert "dummy.txt" not in names
                assert "README.md" in names
    
    def test_zip_uses_forward_slashes(self):
        """TC-GCP005-016: Zip paths use forward slashes."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            create_package(output_zip)
            
            with zipfile.ZipFile(output_zip, 'r') as zf:
                for name in zf.namelist():
                    assert "\\" not in name, f"Path contains backslash: {name}"


class TestPackageCLI:
    """Integration tests for --package CLI flag (GCP-005)."""
    
    def test_package_flag_creates_zip(self, monkeypatch):
        """TC-GCP005-011: CLI --package flag creates zip."""
        original_cwd = os.getcwd()
        tmp_path = None
        try:
            tmp_path = Path(tempfile.mkdtemp())
            monkeypatch.chdir(tmp_path)
            monkeypatch.setattr(sys, 'argv', ['Golazo_Copilot.py', '--package'])
            
            result = main()
            
            assert result == 0
            assert (tmp_path / "GolazoCP-dist.zip").exists()
        finally:
            os.chdir(original_cwd)
            if tmp_path:
                shutil.rmtree(tmp_path, ignore_errors=True)
    
    def test_package_outputs_path(self, monkeypatch, capsys):
        """TC-GCP005-013: CLI --package outputs zip path on success."""
        original_cwd = os.getcwd()
        tmp_path = None
        try:
            tmp_path = Path(tempfile.mkdtemp())
            monkeypatch.chdir(tmp_path)
            monkeypatch.setattr(sys, 'argv', ['Golazo_Copilot.py', '--package'])
            
            main()
            
            captured = capsys.readouterr()
            assert "GolazoCP-dist.zip" in captured.out
        finally:
            os.chdir(original_cwd)
            if tmp_path:
                shutil.rmtree(tmp_path, ignore_errors=True)
    
    def test_no_flag_still_installs(self, monkeypatch):
        """TC-GCP005-015: CLI with no flags maintains existing install behavior."""
        original_cwd = os.getcwd()
        tmp_path = None
        try:
            tmp_path = Path(tempfile.mkdtemp())
            (tmp_path / ".git").mkdir()
            monkeypatch.chdir(tmp_path)
            monkeypatch.setattr(sys, 'argv', ['Golazo_Copilot.py'])
            
            result = main()
            
            assert result == 0
            assert (tmp_path / ".github" / "copilot-instructions.md").exists()
        finally:
            os.chdir(original_cwd)
            if tmp_path:
                shutil.rmtree(tmp_path, ignore_errors=True)
