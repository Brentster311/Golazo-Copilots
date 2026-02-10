"""Tests for gcp_bootstrap tool."""

import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_bootstrap import gcp_bootstrap


TEST_WORKSPACE_DIR = Path(__file__).parent / "test-workspace"


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKSPACE_DIR.exists():
        shutil.rmtree(TEST_WORKSPACE_DIR)
    TEST_WORKSPACE_DIR.mkdir(parents=True)
    # Create a WorkItems folder to simulate a valid workspace
    (TEST_WORKSPACE_DIR / "WorkItems").mkdir()
    yield
    if TEST_WORKSPACE_DIR.exists():
        shutil.rmtree(TEST_WORKSPACE_DIR)


class TestBootstrapCreatesInstructions:
    """AC1: gcp_bootstrap creates copilot instructions file."""

    @pytest.mark.asyncio
    async def test_creates_copilot_instructions(self):
        """Should create .github/copilot-instructions.md."""
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        instructions_path = TEST_WORKSPACE_DIR / ".github" / "copilot-instructions.md"
        assert instructions_path.exists()

    @pytest.mark.asyncio
    async def test_creates_github_directory(self):
        """Should create .github directory if not exists."""
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        github_dir = TEST_WORKSPACE_DIR / ".github"
        assert github_dir.is_dir()

    @pytest.mark.asyncio
    async def test_returns_files_created(self):
        """Should return list of created files."""
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert ".github/copilot-instructions.md" in result["files_created"]


class TestBootstrapInstructionsContent:
    """AC2: Default instructions content is correct."""

    @pytest.mark.asyncio
    async def test_includes_gcp_status_instruction(self):
        """Should include gcp_status tool call instruction."""
        await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        content = (TEST_WORKSPACE_DIR / ".github" / "copilot-instructions.md").read_text()
        assert "gcp_status" in content

    @pytest.mark.asyncio
    async def test_includes_output_validation_info(self):
        """Should include output validation instructions (replaced evidence-based marking)."""
        await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        content = (TEST_WORKSPACE_DIR / ".github" / "copilot-instructions.md").read_text()
        assert "required outputs" in content.lower()

    @pytest.mark.asyncio
    async def test_includes_role_transition_info(self):
        """Should include role transition instructions."""
        await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        content = (TEST_WORKSPACE_DIR / ".github" / "copilot-instructions.md").read_text()
        assert "gcp_transition" in content


class TestBootstrapNoOverwrite:
    """AC3: Does not overwrite existing files."""

    @pytest.mark.asyncio
    async def test_does_not_overwrite_existing(self):
        """Should not overwrite existing instructions file."""
        # Create existing file
        github_dir = TEST_WORKSPACE_DIR / ".github"
        github_dir.mkdir(parents=True)
        existing_content = "# Existing Instructions\nDo not overwrite me!"
        (github_dir / "copilot-instructions.md").write_text(existing_content)
        
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        assert ".github/copilot-instructions.md" in result["files_skipped"]
        
        # Verify content unchanged
        content = (github_dir / "copilot-instructions.md").read_text()
        assert content == existing_content

    @pytest.mark.asyncio
    async def test_force_overwrites_existing(self):
        """Should overwrite existing file when force=True."""
        # Create existing file
        github_dir = TEST_WORKSPACE_DIR / ".github"
        github_dir.mkdir(parents=True)
        (github_dir / "copilot-instructions.md").write_text("Old content")
        
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR, force=True)
        
        assert result["success"] is True
        assert ".github/copilot-instructions.md" in result["files_created"]
        
        # Verify content changed
        content = (github_dir / "copilot-instructions.md").read_text()
        assert "gcp_status" in content


class TestBootstrapWorkItems:
    """AC4: Creates WorkItems directory."""

    @pytest.mark.asyncio
    async def test_creates_workitems_directory(self):
        """Should create WorkItems directory."""
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        workitems_dir = TEST_WORKSPACE_DIR / "WorkItems"
        assert workitems_dir.is_dir()

    @pytest.mark.asyncio
    async def test_creates_gitkeep(self):
        """Should create .gitkeep in WorkItems."""
        await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        gitkeep = TEST_WORKSPACE_DIR / "WorkItems" / ".gitkeep"
        assert gitkeep.exists()


class TestBootstrapRoleFiles:
    """AC5: Optional role files."""

    @pytest.mark.asyncio
    async def test_copies_roles_by_default(self):
        """Should copy role files by default."""
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        roles_dir = TEST_WORKSPACE_DIR / ".github" / "roles"
        assert roles_dir.is_dir()
        assert (roles_dir / "project-owner-assistant.md").exists()

    @pytest.mark.asyncio
    async def test_does_not_copy_roles_when_excluded(self):
        """Should not copy role files when include_roles=False."""
        await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR, include_roles=False)
        
        roles_dir = TEST_WORKSPACE_DIR / ".github" / "roles"
        assert not roles_dir.exists()

    @pytest.mark.asyncio
    async def test_copies_roles_when_requested(self):
        """Should copy role files when include_roles=True."""
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR, include_roles=True)
        
        assert result["success"] is True
        roles_dir = TEST_WORKSPACE_DIR / ".github" / "roles"
        assert roles_dir.is_dir()
        assert (roles_dir / "project-owner-assistant.md").exists()
        assert (roles_dir / "program-manager.md").exists()


class TestBootstrapWorkspaceDetection:
    """AC6: Workspace detection."""

    @pytest.mark.asyncio
    async def test_detects_git_workspace(self):
        """Should detect workspace with WorkItems folder."""
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_fails_without_workspace_markers(self):
        """Should fail if no workspace detected."""
        # Remove WorkItems folder
        shutil.rmtree(TEST_WORKSPACE_DIR / "WorkItems")
        
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is False
        assert "workspace" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_git_alone_is_not_valid_marker(self):
        """Should NOT recognize .git as a workspace marker."""
        # Remove WorkItems, add .git
        shutil.rmtree(TEST_WORKSPACE_DIR / "WorkItems")
        (TEST_WORKSPACE_DIR / ".git").mkdir()
        
        result = await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is False


class TestBootstrapVersionConsistency:
    """AC7: Version in generated files matches package version."""

    @pytest.mark.asyncio
    async def test_instructions_version_matches_package(self):
        """Bootstrap should embed a version comment in instructions."""
        await gcp_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        content = (TEST_WORKSPACE_DIR / ".github" / "copilot-instructions.md").read_text()
        assert "Last Updated in Golazo Copilot Version:" in content

    def test_role_loader_updates_version(self):
        """Role loader should include version comment in loaded roles."""
        from golazo_copilot.roles.loader import load_default_role
        
        content = load_default_role("developer")
        assert "Last Updated in Golazo Copilot Version:" in content
