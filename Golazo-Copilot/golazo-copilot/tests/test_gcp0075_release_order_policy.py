"""Policy tests for GCP-0075 release metadata ownership."""

import sys
from importlib import resources
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.core.transitions import PROFILE_ROLES
from golazo_copilot.tools.golazo_bootstrap import golazo_bootstrap


def _role_content(role: str) -> str:
    return (
        resources.files("golazo_copilot.roles.defaults")
        .joinpath(f"{role}.md")
        .read_text(encoding="utf-8")
    )


def test_builder_owns_complete_release_metadata_sequence():
    builder = _role_content("builder")

    assert "Builder owns release metadata" in builder
    assert "bump the version" in builder
    assert "PEP 440" in builder
    assert "changelog" in builder
    assert "before the final commit" in builder


def test_documenter_excludes_release_metadata_and_future_builder_dependencies():
    documenter = _role_content("documenter")

    assert "Release versioning and changelog maintenance are owned by Builder" in documenter
    assert "Use the version from builder notes" not in documenter
    assert "release version is defined/updated" not in documenter
    assert "Code changes committed" not in documenter


def test_builder_has_no_backward_documenter_dependency():
    builder = _role_content("builder")

    assert "before transitioning to **Documenter**" not in builder
    assert "after Documenter" not in builder
    assert "transition back" not in builder.lower()


def test_release_owner_exists_in_complete_and_express_profiles():
    complete = PROFILE_ROLES["complete"]
    express = PROFILE_ROLES["express"]

    assert complete.index("documenter") < complete.index("builder")
    assert "builder" in express
    assert "documenter" not in express


def test_readme_matches_release_order_policy():
    readme = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")

    assert "Documenter reviews user-facing documentation; Builder owns versioning, changelog, build, commit, and push." in readme
    assert readme.index("`documenter`, `builder`, `retrospective`") > 0
    assert "must currently be at role `retrospective`" not in readme


@pytest.mark.asyncio
async def test_force_bootstrap_copies_corrected_release_roles(tmp_path: Path):
    (tmp_path / "WorkItems").mkdir()

    result = await golazo_bootstrap(
        workspace_path=tmp_path,
        include_roles=True,
        force=True,
    )

    assert result["success"] is True
    generated_roles = tmp_path / ".github" / "agents" / "golazo-copilot" / "roles"
    for role in ("documenter", "builder"):
        assert (generated_roles / f"{role}.md").read_text(encoding="utf-8") == _role_content(role)
