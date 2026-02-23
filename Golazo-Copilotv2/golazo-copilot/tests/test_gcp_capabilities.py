"""Tests for golazo_capabilities tool."""

import sys
import os
import pytest

# Ensure project is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from golazo_copilot.tools.golazo_capabilities import golazo_capabilities

# Test workspace directory
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_WORKSPACE_DIR = None  # Set per-test via tmp_path


SAMPLE_YAML = """\
capabilities:
  - name: bootstrap
    description: Deploys instructions and role files to workspace
    key_files:
      - src/tools/golazo_bootstrap.py
      - src/bootstrap-instructions.md
    contracts:
      - "Version comment format in all deployed files"
    depends_on: []

  - name: role-deployment
    description: Copies role files to .github/roles/
    key_files:
      - src/tools/golazo_bootstrap.py
    contracts:
      - "Role file naming convention"
    depends_on:
      - bootstrap

  - name: stale-detection
    description: Detects stale deployed files by comparing version comments
    key_files:
      - src/tools/golazo_status.py
    contracts:
      - "<!-- Last Updated in Golazo Copilot Version: X.Y.Z -->"
    depends_on:
      - bootstrap
      - role-deployment

  - name: output-validation
    description: Validates required outputs before role transitions
    key_files:
      - src/core/output_validator.py
    contracts:
      - "## Required Outputs section format"
    depends_on:
      - role-deployment
"""

DIAMOND_YAML = """\
capabilities:
  - name: base
    description: Base capability
    key_files:
      - src/base.py
    contracts: []
    depends_on: []

  - name: left
    description: Left branch
    key_files:
      - src/left.py
    contracts: []
    depends_on:
      - base

  - name: right
    description: Right branch
    key_files:
      - src/right.py
    contracts: []
    depends_on:
      - base

  - name: top
    description: Top node depends on both branches
    key_files:
      - src/top.py
    contracts: []
    depends_on:
      - left
      - right
"""

CIRCULAR_YAML = """\
capabilities:
  - name: alpha
    description: Alpha capability
    key_files:
      - src/alpha.py
    contracts: []
    depends_on:
      - beta

  - name: beta
    description: Beta capability
    key_files:
      - src/beta.py
    contracts: []
    depends_on:
      - alpha
"""


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace with sample capabilities.yaml."""
    (tmp_path / "capabilities.yaml").write_text(SAMPLE_YAML, encoding="utf-8")
    # Create key_files so validate passes
    for f in [
        "src/tools/golazo_bootstrap.py",
        "src/bootstrap-instructions.md",
        "src/tools/golazo_status.py",
        "src/core/output_validator.py",
    ]:
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("# placeholder", encoding="utf-8")
    return tmp_path


@pytest.fixture
def diamond_workspace(tmp_path):
    """Create a workspace with diamond dependency pattern."""
    (tmp_path / "capabilities.yaml").write_text(DIAMOND_YAML, encoding="utf-8")
    for f in ["src/base.py", "src/left.py", "src/right.py", "src/top.py"]:
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("# placeholder", encoding="utf-8")
    return tmp_path


@pytest.fixture
def circular_workspace(tmp_path):
    """Create a workspace with circular dependencies."""
    (tmp_path / "capabilities.yaml").write_text(CIRCULAR_YAML, encoding="utf-8")
    for f in ["src/alpha.py", "src/beta.py"]:
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("# placeholder", encoding="utf-8")
    return tmp_path


@pytest.fixture
def empty_workspace(tmp_path):
    """Create a workspace without capabilities.yaml."""
    return tmp_path


class TestListAction:
    """TC-1: List action (AC1)."""

    @pytest.mark.asyncio
    async def test_list_returns_all_capabilities(self, workspace):
        """TC-1.1: Returns all capability names + descriptions."""
        result = await golazo_capabilities(action="list", workspace_path=workspace)
        assert result["success"] is True
        caps = result["capabilities"]
        assert len(caps) == 4
        names = [c["name"] for c in caps]
        assert "bootstrap" in names
        assert "stale-detection" in names

    @pytest.mark.asyncio
    async def test_list_empty_capabilities(self, tmp_path):
        """TC-1.2: Empty capabilities list returns empty, no error."""
        (tmp_path / "capabilities.yaml").write_text(
            "capabilities: []\n", encoding="utf-8"
        )
        result = await golazo_capabilities(action="list", workspace_path=tmp_path)
        assert result["success"] is True
        assert result["capabilities"] == []


class TestShowAction:
    """TC-2: Show action (AC2)."""

    @pytest.mark.asyncio
    async def test_show_returns_full_card(self, workspace):
        """TC-2.1: Returns full card including computed depended_on_by."""
        result = await golazo_capabilities(
            action="show", capability="bootstrap", workspace_path=workspace
        )
        assert result["success"] is True
        cap = result["capability"]
        assert cap["name"] == "bootstrap"
        assert cap["description"] == "Deploys instructions and role files to workspace"
        assert "src/tools/golazo_bootstrap.py" in cap["key_files"]
        assert len(cap["contracts"]) > 0
        # bootstrap is depended on by role-deployment and stale-detection
        assert "role-deployment" in cap["depended_on_by"]
        assert "stale-detection" in cap["depended_on_by"]

    @pytest.mark.asyncio
    async def test_show_nonexistent_capability(self, workspace):
        """TC-2.2: Non-existent capability returns clear message."""
        result = await golazo_capabilities(
            action="show", capability="nonexistent", workspace_path=workspace
        )
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_show_without_capability_param(self, workspace):
        """TC-2.3: Missing capability parameter returns error."""
        result = await golazo_capabilities(
            action="show", workspace_path=workspace
        )
        assert result["success"] is False


class TestImpactAction:
    """TC-3: Impact action (AC3)."""

    @pytest.mark.asyncio
    async def test_impact_direct_match(self, workspace):
        """TC-3.1: Returns directly affected capabilities."""
        result = await golazo_capabilities(
            action="impact",
            files=["src/tools/golazo_status.py"],
            workspace_path=workspace,
        )
        assert result["success"] is True
        direct_names = [c["name"] for c in result["directly_affected"]]
        assert "stale-detection" in direct_names

    @pytest.mark.asyncio
    async def test_impact_transitive_dependents(self, workspace):
        """TC-3.2: Returns transitive dependents."""
        result = await golazo_capabilities(
            action="impact",
            files=["src/bootstrap-instructions.md"],
            workspace_path=workspace,
        )
        assert result["success"] is True
        direct_names = [c["name"] for c in result["directly_affected"]]
        assert "bootstrap" in direct_names
        transitive_names = [c["name"] for c in result["transitively_affected"]]
        # role-deployment and stale-detection depend on bootstrap
        assert "role-deployment" in transitive_names
        assert "stale-detection" in transitive_names
        # output-validation depends on role-deployment
        assert "output-validation" in transitive_names

    @pytest.mark.asyncio
    async def test_impact_diamond_no_duplicates(self, diamond_workspace):
        """TC-3.3: Diamond dependency returns all without duplicates."""
        result = await golazo_capabilities(
            action="impact",
            files=["src/base.py"],
            workspace_path=diamond_workspace,
        )
        assert result["success"] is True
        direct_names = [c["name"] for c in result["directly_affected"]]
        assert "base" in direct_names
        transitive_names = [c["name"] for c in result["transitively_affected"]]
        assert "left" in transitive_names
        assert "right" in transitive_names
        assert "top" in transitive_names
        # No duplicates
        assert len(transitive_names) == len(set(transitive_names))

    @pytest.mark.asyncio
    async def test_impact_no_matches(self, workspace):
        """TC-3.4: Files matching zero capabilities returns empty result."""
        result = await golazo_capabilities(
            action="impact",
            files=["src/nonexistent.py"],
            workspace_path=workspace,
        )
        assert result["success"] is True
        assert result["directly_affected"] == []
        assert result["transitively_affected"] == []

    @pytest.mark.asyncio
    async def test_impact_suffix_matching(self, workspace):
        """TC-3.5: Suffix matching works."""
        result = await golazo_capabilities(
            action="impact",
            files=["golazo_status.py"],
            workspace_path=workspace,
        )
        assert result["success"] is True
        direct_names = [c["name"] for c in result["directly_affected"]]
        assert "stale-detection" in direct_names

    @pytest.mark.asyncio
    async def test_impact_exact_match_priority(self, workspace):
        """TC-3.6: Exact match takes priority over suffix match."""
        result = await golazo_capabilities(
            action="impact",
            files=["src/tools/golazo_bootstrap.py"],
            workspace_path=workspace,
        )
        assert result["success"] is True
        direct_names = [c["name"] for c in result["directly_affected"]]
        # Both bootstrap and role-deployment have this as key_file
        assert "bootstrap" in direct_names
        assert "role-deployment" in direct_names


class TestValidateAction:
    """TC-4: Validate action (AC4)."""

    @pytest.mark.asyncio
    async def test_validate_all_pass(self, workspace):
        """TC-4.1: All key_files exist → all pass."""
        result = await golazo_capabilities(
            action="validate", workspace_path=workspace
        )
        assert result["success"] is True
        for cap in result["results"]:
            assert cap["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_some_missing(self, workspace):
        """TC-4.2: Missing key_files → those capabilities fail."""
        # Remove a file
        (workspace / "src" / "tools" / "golazo_status.py").unlink()
        result = await golazo_capabilities(
            action="validate", workspace_path=workspace
        )
        assert result["success"] is True
        stale = next(r for r in result["results"] if r["name"] == "stale-detection")
        assert stale["valid"] is False
        assert "src/tools/golazo_status.py" in stale["missing_files"]


class TestMissingRegistry:
    """TC-5: Missing registry (AC5)."""

    @pytest.mark.asyncio
    async def test_no_registry(self, empty_workspace):
        """TC-5.1: No capabilities.yaml → clear message, success=true."""
        result = await golazo_capabilities(
            action="list", workspace_path=empty_workspace
        )
        assert result["success"] is True
        assert "no registry" in result.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_malformed_yaml(self, tmp_path):
        """TC-5.2: Malformed YAML → clear error message."""
        (tmp_path / "capabilities.yaml").write_text(
            "capabilities: [invalid: yaml: here", encoding="utf-8"
        )
        result = await golazo_capabilities(
            action="list", workspace_path=tmp_path
        )
        assert result["success"] is False
        assert "error" in result


class TestDependedOnBy:
    """TC-6: Depended-on-by computation (AC6)."""

    @pytest.mark.asyncio
    async def test_depended_on_by_computed(self, workspace):
        """TC-6.1: A depends on B → B's card shows depended_on_by: [A]."""
        result = await golazo_capabilities(
            action="show", capability="bootstrap", workspace_path=workspace
        )
        cap = result["capability"]
        assert "role-deployment" in cap["depended_on_by"]
        assert "stale-detection" in cap["depended_on_by"]

    @pytest.mark.asyncio
    async def test_no_dependents(self, workspace):
        """TC-6.2: No dependents → depended_on_by is empty."""
        result = await golazo_capabilities(
            action="show", capability="output-validation", workspace_path=workspace
        )
        cap = result["capability"]
        assert cap["depended_on_by"] == []

    @pytest.mark.asyncio
    async def test_circular_depended_on_by(self, circular_workspace):
        """TC-6.3: Circular → both show each other, no infinite loop."""
        result = await golazo_capabilities(
            action="show", capability="alpha", workspace_path=circular_workspace
        )
        cap = result["capability"]
        assert "beta" in cap["depended_on_by"]


class TestCycleHandling:
    """TC-7: Cycle handling."""

    @pytest.mark.asyncio
    async def test_circular_impact_no_infinite_loop(self, circular_workspace):
        """TC-7.1: Circular depends_on does not cause infinite loop."""
        result = await golazo_capabilities(
            action="impact",
            files=["src/alpha.py"],
            workspace_path=circular_workspace,
        )
        assert result["success"] is True
        direct_names = [c["name"] for c in result["directly_affected"]]
        assert "alpha" in direct_names
        # beta depends on alpha (circular), should appear in transitives
        all_names = (
            [c["name"] for c in result["directly_affected"]]
            + [c["name"] for c in result["transitively_affected"]]
        )
        assert "beta" in all_names
