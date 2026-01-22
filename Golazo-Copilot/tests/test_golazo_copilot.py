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


# =============================================================================
# GCP-006: Versioning Tests
# =============================================================================

class TestVersioning:
    """Tests for GCP-006: Version metadata in Golazo files."""
    
    VERSION_PATTERN = r'<!-- Golazo Version: (\d+\.\d+\.\d+) -->'
    
    def test_version_file_exists(self):
        """TC-005: VERSION file exists at repo root."""
        script_dir = get_script_directory()
        version_file = script_dir / "VERSION"
        
        assert version_file.exists(), "VERSION file not found at repository root"
    
    def test_version_file_valid_semver(self):
        """TC-006: VERSION file contains valid semver."""
        import re
        script_dir = get_script_directory()
        version_file = script_dir / "VERSION"
        
        if not version_file.exists():
            pytest.skip("VERSION file not yet created")
        
        content = version_file.read_text().strip()
        semver_pattern = r'^\d+\.\d+\.\d+$'
        
        assert re.match(semver_pattern, content), \
            f"VERSION file contains invalid version: '{content}'"
    
    def test_changelog_exists(self):
        """TC-007: CHANGELOG.md exists at repo root."""
        script_dir = get_script_directory()
        changelog = script_dir / "CHANGELOG.md"
        
        assert changelog.exists(), "CHANGELOG.md not found at repository root"
    
    def test_changelog_contains_current_version(self):
        """TC-008: CHANGELOG.md contains entry for current version."""
        script_dir = get_script_directory()
        version_file = script_dir / "VERSION"
        changelog = script_dir / "CHANGELOG.md"
        
        if not version_file.exists() or not changelog.exists():
            pytest.skip("VERSION or CHANGELOG not yet created")
        
        current_version = version_file.read_text().strip()
        changelog_content = changelog.read_text()
        
        # Look for version heading like ## [1.0.0]
        assert f"[{current_version}]" in changelog_content, \
            f"CHANGELOG.md missing entry for version {current_version}"
    
    def test_spine_has_version_comment(self):
        """TC-001: Spine file contains version comment on line 1."""
        import re
        script_dir = get_script_directory()
        spine = script_dir / ".github" / "copilot-instructions.md"
        
        assert spine.exists(), "Spine file not found"
        
        first_line = spine.read_text().split('\n')[0]
        
        assert re.match(self.VERSION_PATTERN, first_line), \
            f"Spine file missing version comment on line 1. Found: '{first_line}'"
    
    def test_spine_version_is_valid_semver(self):
        """TC-002: Spine version is valid semver."""
        import re
        script_dir = get_script_directory()
        spine = script_dir / ".github" / "copilot-instructions.md"
        
        if not spine.exists():
            pytest.skip("Spine file not found")
        
        first_line = spine.read_text().split('\n')[0]
        match = re.match(self.VERSION_PATTERN, first_line)
        
        if not match:
            pytest.skip("Spine doesn't have version comment yet")
        
        version = match.group(1)
        semver_pattern = r'^\d+\.\d+\.\d+$'
        
        assert re.match(semver_pattern, version), \
            f"Spine version '{version}' is not valid semver"
    
    def test_all_role_files_have_version_comment(self):
        """TC-003: All role files contain version comment."""
        import re
        script_dir = get_script_directory()
        roles_dir = script_dir / ".github" / "roles"
        
        expected_roles = [
            "project-owner-assistant.md",
            "program-manager.md",
            "reviewer.md",
            "architect.md",
            "tester.md",
            "developer.md",
            "refactor-expert.md",
            "builder.md",
            "documentor.md",
            "retrospective.md",
        ]
        
        missing = []
        for role_file in expected_roles:
            path = roles_dir / role_file
            if not path.exists():
                missing.append(f"{role_file} (file not found)")
                continue
            
            first_line = path.read_text().split('\n')[0]
            if not re.match(self.VERSION_PATTERN, first_line):
                missing.append(f"{role_file} (missing version comment)")
        
        assert not missing, f"Role files missing version comment: {missing}"
    
    def test_all_versions_match(self):
        """TC-004: All role file versions match spine version."""
        import re
        script_dir = get_script_directory()
        spine = script_dir / ".github" / "copilot-instructions.md"
        roles_dir = script_dir / ".github" / "roles"
        
        if not spine.exists():
            pytest.skip("Spine file not found")
        
        spine_first_line = spine.read_text().split('\n')[0]
        spine_match = re.match(self.VERSION_PATTERN, spine_first_line)
        
        if not spine_match:
            pytest.skip("Spine doesn't have version comment yet")
        
        spine_version = spine_match.group(1)
        
        mismatches = []
        for role_file in roles_dir.glob("*.md"):
            first_line = role_file.read_text().split('\n')[0]
            match = re.match(self.VERSION_PATTERN, first_line)
            if match:
                file_version = match.group(1)
                if file_version != spine_version:
                    mismatches.append(f"{role_file.name}: {file_version}")
        
        assert not mismatches, \
            f"Version mismatch: spine={spine_version}, mismatches: {mismatches}"
    
    def test_version_file_matches_spine(self):
        """Verify VERSION file matches spine version comment."""
        import re
        script_dir = get_script_directory()
        version_file = script_dir / "VERSION"
        spine = script_dir / ".github" / "copilot-instructions.md"
        
        if not version_file.exists() or not spine.exists():
            pytest.skip("VERSION or spine not found")
        
        file_version = version_file.read_text().strip()
        
        spine_first_line = spine.read_text().split('\n')[0]
        spine_match = re.match(self.VERSION_PATTERN, spine_first_line)
        
        if not spine_match:
            pytest.skip("Spine doesn't have version comment yet")
        
        spine_version = spine_match.group(1)
        
        assert file_version == spine_version, \
            f"VERSION file ({file_version}) doesn't match spine ({spine_version})"


class TestPackageVersioning:
    """Tests for GCP-006: VERSION and CHANGELOG in package."""
    
    def test_package_includes_version_file(self):
        """TC-009: Package includes VERSION file."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            create_package(output_zip)
            
            with zipfile.ZipFile(output_zip, 'r') as zf:
                names = zf.namelist()
                assert "VERSION" in names, \
                    "GolazoCP-dist.zip does not contain VERSION file"
    
    def test_package_includes_changelog(self):
        """TC-010: Package includes CHANGELOG.md."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_zip = tmp_path / "GolazoCP-dist.zip"
            
            create_package(output_zip)
            
            with zipfile.ZipFile(output_zip, 'r') as zf:
                names = zf.namelist()
                assert "CHANGELOG.md" in names, \
                    "GolazoCP-dist.zip does not contain CHANGELOG.md"


class TestVersionEdgeCases:
    """Edge case tests for versioning (GCP-006)."""
    
    def test_version_file_trailing_newline(self):
        """TC-011: VERSION file handles trailing newline correctly."""
        script_dir = get_script_directory()
        version_file = script_dir / "VERSION"
        
        if not version_file.exists():
            pytest.skip("VERSION file not yet created")
        
        # Read raw bytes to check for newline
        raw_content = version_file.read_bytes()
        content = version_file.read_text()
        
        # Strip should give clean version regardless of trailing newline
        version = content.strip()
        
        import re
        assert re.match(r'^\d+\.\d+\.\d+$', version), \
            f"VERSION parsing failed: got '{version}'"
