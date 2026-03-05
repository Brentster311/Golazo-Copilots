"""Tests for golazo_bootstrap tool."""

import shutil
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.golazo_bootstrap import golazo_bootstrap

TEST_WORKSPACE_DIR = Path(__file__).parent / "test-workspace"


def _safe_rmtree(path: Path, retries: int = 5, delay: float = 0.1) -> None:
    """Remove a directory with small retries for transient Windows file locks."""
    if not path.exists():
        return
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            shutil.rmtree(path)
            return
        except PermissionError as exc:
            last_error = exc
            time.sleep(delay)
    if last_error is not None:
        raise last_error


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKSPACE_DIR.exists():
        _safe_rmtree(TEST_WORKSPACE_DIR)
    TEST_WORKSPACE_DIR.mkdir(parents=True)
    # Create a WorkItems folder to simulate a valid workspace
    (TEST_WORKSPACE_DIR / "WorkItems").mkdir()
    yield
    if TEST_WORKSPACE_DIR.exists():
        _safe_rmtree(TEST_WORKSPACE_DIR)


class TestBootstrapCreatesInstructions:
    """AC1: golazo_bootstrap creates copilot instructions file."""

    @pytest.mark.asyncio
    async def test_creates_copilot_instructions(self):
        """Should create .github/agents/Golazo-Copilot.md."""
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        instructions_path = (
            TEST_WORKSPACE_DIR
            / ".github"
            / "agents"
            / "Golazo-Copilot.md"
        )
        assert instructions_path.exists()

    @pytest.mark.asyncio
    async def test_creates_github_directory(self):
        """Should create .github directory if not exists."""
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        github_dir = TEST_WORKSPACE_DIR / ".github"
        assert github_dir.is_dir()

    @pytest.mark.asyncio
    async def test_returns_files_created(self):
        """Should return list of created files."""
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert ".github/agents/Golazo-Copilot.md" in result["files_created"]


class TestBootstrapInstructionsContent:
    """AC2: Default instructions content is correct."""

    @pytest.mark.asyncio
    async def test_includes_golazo_status_instruction(self):
        """Should include golazo_status tool call instruction."""
        await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        content = (
            TEST_WORKSPACE_DIR
            / ".github"
            / "agents"
            / "Golazo-Copilot.md"
        ).read_text()
        assert "golazo_status" in content

    @pytest.mark.asyncio
    async def test_includes_output_validation_info(self):
        """Should include output validation instructions (replaced evidence-based marking)."""
        await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        content = (
            TEST_WORKSPACE_DIR
            / ".github"
            / "agents"
            / "Golazo-Copilot.md"
        ).read_text()
        assert "required outputs" in content.lower()

    @pytest.mark.asyncio
    async def test_includes_role_transition_info(self):
        """Should include role transition instructions."""
        await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        content = (
            TEST_WORKSPACE_DIR
            / ".github"
            / "agents"
            / "Golazo-Copilot.md"
        ).read_text()
        assert "golazo_transition" in content


class TestBootstrapNoOverwrite:
    """AC3: Does not overwrite existing files."""

    @pytest.mark.asyncio
    async def test_does_not_overwrite_existing(self):
        """Should not overwrite existing instructions file."""
        # Create existing file
        github_dir = TEST_WORKSPACE_DIR / ".github" / "agents"
        github_dir.mkdir(parents=True)
        existing_content = "# Existing Instructions\nDo not overwrite me!"
        (github_dir / "Golazo-Copilot.md").write_text(existing_content)
        
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        assert ".github/agents/Golazo-Copilot.md" in result["files_skipped"]
        
        # Verify content unchanged
        content = (github_dir / "Golazo-Copilot.md").read_text()
        assert content == existing_content

    @pytest.mark.asyncio
    async def test_force_overwrites_existing(self):
        """Should overwrite existing file when force=True."""
        # Create existing file
        github_dir = TEST_WORKSPACE_DIR / ".github" / "agents"
        github_dir.mkdir(parents=True)
        (github_dir / "Golazo-Copilot.md").write_text("Old content")
        
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR, force=True)
        
        assert result["success"] is True
        assert ".github/agents/Golazo-Copilot.md" in result["files_created"]
        
        # Verify content changed
        content = (github_dir / "Golazo-Copilot.md").read_text()
        assert "golazo_status" in content


class TestBootstrapWorkItems:
    """AC4: Creates WorkItems directory."""

    @pytest.mark.asyncio
    async def test_creates_workitems_directory(self):
        """Should create WorkItems directory."""
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        workitems_dir = TEST_WORKSPACE_DIR / "WorkItems"
        assert workitems_dir.is_dir()

    @pytest.mark.asyncio
    async def test_creates_gitkeep(self):
        """Should create .gitkeep in WorkItems."""
        await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        gitkeep = TEST_WORKSPACE_DIR / "WorkItems" / ".gitkeep"
        assert gitkeep.exists()


class TestBootstrapRoleFiles:
    """AC5: Optional role files."""

    @pytest.mark.asyncio
    async def test_copies_roles_by_default(self):
        """Should copy role files by default."""
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True
        roles_dir = TEST_WORKSPACE_DIR / ".github" / "agents" / "golazo-copilot" / "roles"
        assert roles_dir.is_dir()
        assert (roles_dir / "project-owner-assistant.md").exists()

    @pytest.mark.asyncio
    async def test_does_not_copy_roles_when_excluded(self):
        """Should not copy role files when include_roles=False."""
        await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR, include_roles=False)
        
        roles_dir = TEST_WORKSPACE_DIR / ".github" / "agents" / "golazo-copilot" / "roles"
        assert not roles_dir.exists()

    @pytest.mark.asyncio
    async def test_copies_roles_when_requested(self):
        """Should copy role files when include_roles=True."""
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR, include_roles=True)
        
        assert result["success"] is True
        roles_dir = TEST_WORKSPACE_DIR / ".github" / "agents" / "golazo-copilot" / "roles"
        assert roles_dir.is_dir()
        assert (roles_dir / "project-owner-assistant.md").exists()
        assert (roles_dir / "program-manager.md").exists()


class TestBootstrapWorkspaceDetection:
    """AC6: Workspace detection."""

    @pytest.mark.asyncio
    async def test_detects_git_workspace(self):
        """Should detect workspace with WorkItems folder."""
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_fails_without_workspace_markers(self):
        """Should fail if no workspace detected."""
        # Remove WorkItems folder
        shutil.rmtree(TEST_WORKSPACE_DIR / "WorkItems")
        
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is False
        assert "workspace" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_git_alone_is_not_valid_marker(self):
        """Should NOT recognize .git as a workspace marker."""
        # Remove WorkItems, add .git
        shutil.rmtree(TEST_WORKSPACE_DIR / "WorkItems")
        (TEST_WORKSPACE_DIR / ".git").mkdir()
        
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        assert result["success"] is False


class TestBootstrapVersionConsistency:
    """AC7: Version in generated files matches package version."""

    @pytest.mark.asyncio
    async def test_instructions_version_matches_package(self):
        """Bootstrap should embed a version comment in instructions."""
        await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)
        
        content = (
            TEST_WORKSPACE_DIR
            / ".github"
            / "agents"
            / "Golazo-Copilot.md"
        ).read_text()
        assert "Last Updated in Golazo Copilot Version:" in content

    def test_role_loader_updates_version(self):
        """Role loader should include version comment in loaded roles."""
        from golazo_copilot.roles.loader import load_default_role
        
        content = load_default_role("developer")
        assert "Last Updated in Golazo Copilot Version:" in content


class TestBootstrapCapabilitiesTemplate:
    """Tests for capabilities.yaml template scaffolding."""

    @pytest.mark.asyncio
    async def test_creates_capabilities_yaml(self):
        """TC1: Bootstrap creates capabilities.yaml when absent."""
        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR)

        assert result["success"] is True
        cap_path = TEST_WORKSPACE_DIR / "capabilities.yaml"
        assert cap_path.exists()
        assert "capabilities.yaml" in result["files_created"]

    @pytest.mark.asyncio
    async def test_skips_capabilities_yaml_when_exists(self):
        """TC2: Bootstrap skips capabilities.yaml when exists and force=False."""
        cap_path = TEST_WORKSPACE_DIR / "capabilities.yaml"
        cap_path.write_text("custom: content\n", encoding="utf-8")

        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR, force=False)

        assert "capabilities.yaml" in result["files_skipped"]
        assert cap_path.read_text(encoding="utf-8") == "custom: content\n"

    @pytest.mark.asyncio
    async def test_does_not_overwrite_capabilities_yaml_when_force(self):
        """TC3: Bootstrap never overwrites capabilities.yaml, even when force=True."""
        cap_path = TEST_WORKSPACE_DIR / "capabilities.yaml"
        cap_path.write_text("custom: content\n", encoding="utf-8")

        result = await golazo_bootstrap(workspace_path=TEST_WORKSPACE_DIR, force=True)

        assert "capabilities.yaml" in result["files_skipped"]
        assert cap_path.read_text(encoding="utf-8") == "custom: content\n"

    def test_template_is_valid_yaml(self):
        """TC4: Template is valid YAML with capabilities key."""
        from importlib import resources as res

        import yaml

        files_pkg = res.files("golazo_copilot")
        raw = files_pkg.joinpath("capabilities-template.yaml").read_text(encoding="utf-8")
        data = yaml.safe_load(raw)

        assert isinstance(data, dict)
        assert "capabilities" in data
        assert isinstance(data["capabilities"], list)
        assert len(data["capabilities"]) >= 1

    def test_template_example_has_expected_fields(self):
        """TC5: Template example capability has all expected fields."""
        from importlib import resources as res

        import yaml

        files_pkg = res.files("golazo_copilot")
        raw = files_pkg.joinpath("capabilities-template.yaml").read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        cap = data["capabilities"][0]

        assert "name" in cap and isinstance(cap["name"], str) and cap["name"]
        assert "description" in cap
        assert "key_files" in cap

    def test_template_starts_with_comment(self):
        """TC6: Template contains YAML comment header."""
        from importlib import resources as res

        files_pkg = res.files("golazo_copilot")
        raw = files_pkg.joinpath("capabilities-template.yaml").read_text(encoding="utf-8")

        assert raw.startswith("#")

    @pytest.mark.asyncio
    async def test_creates_capabilities_without_roles(self):
        """TC7: Bootstrap with include_roles=False still creates capabilities.yaml."""
        result = await golazo_bootstrap(
            workspace_path=TEST_WORKSPACE_DIR, include_roles=False
        )

        assert result["success"] is True
        assert "capabilities.yaml" in result["files_created"]
        assert (TEST_WORKSPACE_DIR / "capabilities.yaml").exists()


class TestBootstrapModes:
    """Tests for bootstrap mode selection behavior."""

    @pytest.mark.asyncio
    async def test_orchestrator_only_creates_only_instructions(self):
        """orchestrator-only should avoid full scaffolding side-effects."""
        result = await golazo_bootstrap(
            workspace_path=TEST_WORKSPACE_DIR,
            mode="orchestrator-only",
        )

        assert result["success"] is True
        assert ".github/agents/Golazo-Copilot.md" in result["files_created"]
        assert not (TEST_WORKSPACE_DIR / "capabilities.yaml").exists()
        assert not (TEST_WORKSPACE_DIR / ".github" / "agents" / "golazo-copilot" / "roles").exists()
        assert not (TEST_WORKSPACE_DIR / "WorkItems" / ".gitkeep").exists()

    @pytest.mark.asyncio
    async def test_invalid_mode_fails(self):
        """Unknown mode should return a validation error."""
        result = await golazo_bootstrap(
            workspace_path=TEST_WORKSPACE_DIR,
            mode="unknown",
        )

        assert result["success"] is False
        assert "Invalid mode" in result["error"]
        assert "orchestrator-only" in result["error"]

    @pytest.mark.asyncio
    async def test_explicit_full_mode_matches_default(self):
        """Explicit full mode should preserve legacy behavior."""
        result = await golazo_bootstrap(
            workspace_path=TEST_WORKSPACE_DIR,
            mode="full",
        )

        assert result["success"] is True
        assert ".github/agents/Golazo-Copilot.md" in result["files_created"]
        assert (TEST_WORKSPACE_DIR / "capabilities.yaml").exists()
        assert (TEST_WORKSPACE_DIR / ".github" / "agents" / "golazo-copilot" / "roles").exists()
