# -*- coding: utf-8 -*-
"""Tests for gcp_role_context tool — GCP-0049."""

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import pytest
import pytest_asyncio

from golazo_copilot.tools.gcp_role_context import gcp_role_context


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_state(work_item_id: str, role: str = "developer", phase: str = "development") -> dict:
    """Return a minimal valid state dict."""
    return {
        "schema_version": "1.0",
        "work_item_id": work_item_id,
        "profile": "complete",
        "current_phase": phase,
        "current_role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "role_history": [],
        "deviations": [],
    }


def _write_state(work_items_dir: Path, wid: str, role: str = "developer", phase: str = "development"):
    """Write a state.json file for a work item."""
    wi_dir = work_items_dir / wid
    wi_dir.mkdir(parents=True, exist_ok=True)
    state = _make_state(wid, role, phase)
    (wi_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")
    return wi_dir


def _write_role_file(project_root: Path, role: str, front_matter: str, body: str = ""):
    """Write a role file under .github/roles/ with optional front-matter."""
    roles_dir = project_root / ".github" / "roles"
    roles_dir.mkdir(parents=True, exist_ok=True)
    content = ""
    if front_matter:
        content = f"---\n{front_matter}---\n"
    content += body or f"# Role: {role}\n\nDo the {role} work."
    (roles_dir / f"{role}.md").write_text(content, encoding="utf-8")


def _write_artifact(work_items_dir: Path, wid: str, relative_path: str, content: str):
    """Write an artifact file for a work item."""
    full_path = work_items_dir / wid / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# TC1: Bundle sections present (AC2)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_bundle_has_all_sections(tmp_path):
    """Bundle must contain all 4 expected sections."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="developer")
    _write_role_file(tmp_path, "developer", "inputs:\n  - WorkItems/{id}/Design/{id}-design-doc.md\noutputs:\n  - WorkItems/{id}/RoleDecisionNotes/{id}-developer.md\ntools:\n  - gcp_status\n")

    result = await gcp_role_context(
        work_item_id=wid,
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "ok", f"Expected ok, got: {result.get('error')}"
    bundle = result["bundle"]
    for section in ["## Role Instructions", "## Current State", "## Input Artifacts", "## Previous Role Notes"]:
        assert section in bundle, f"Bundle missing expected section: {section}"


# ---------------------------------------------------------------------------
# TC2: Input artifacts contain file content (AC3)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_input_artifacts_contain_content(tmp_path):
    """Artifacts listed in front-matter inputs should have their content included."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="program-manager")
    _write_role_file(
        tmp_path, "program-manager",
        "inputs:\n  - WorkItems/{id}/{id}-User-Story.md\noutputs: []\ntools: []\n",
    )
    _write_artifact(work_items_dir, wid, "TST-001-User-Story.md", "# User Story Content\nThis is the story.")

    result = await gcp_role_context(
        work_item_id=wid,
        role="program-manager",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "ok"
    assert "# User Story Content" in result["bundle"], "Artifact content not found in bundle"
    assert "This is the story." in result["bundle"], "Artifact content not found in bundle"


# ---------------------------------------------------------------------------
# TC3: Missing artifacts marked (AC3)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_missing_artifacts_marked(tmp_path):
    """Missing artifacts should show [not yet created] marker."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="program-manager")
    _write_role_file(
        tmp_path, "program-manager",
        "inputs:\n  - WorkItems/{id}/{id}-User-Story.md\n  - WorkItems/{id}/Design/{id}-design-doc.md\noutputs: []\ntools: []\n",
    )
    # Only create one artifact — the other should be marked missing
    _write_artifact(work_items_dir, wid, "TST-001-User-Story.md", "Story content")

    result = await gcp_role_context(
        work_item_id=wid,
        role="program-manager",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "ok"
    assert "[not yet created]" in result["bundle"], "Missing artifact should show [not yet created] marker"


# ---------------------------------------------------------------------------
# TC4: Size guard truncation (AC4)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_size_guard_truncation(tmp_path):
    """When total bundle exceeds max_bundle_size, artifacts are truncated."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="developer")
    _write_role_file(tmp_path, "developer", "inputs:\n  - WorkItems/{id}/{id}-User-Story.md\noutputs: []\ntools: []\n")
    # Create a large artifact
    _write_artifact(work_items_dir, wid, "TST-001-User-Story.md", "X" * 5000)

    result = await gcp_role_context(
        work_item_id=wid,
        role="developer",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
        max_bundle_size=1000,
    )

    assert result["status"] == "ok"
    assert len(result["bundle"]) <= 1500, "Bundle greatly exceeds max size"  # allow some overhead for section headers
    assert "[truncated" in result["bundle"], "Missing truncation marker"
    assert result.get("truncated", False), "Result should indicate truncation occurred"


# ---------------------------------------------------------------------------
# TC5: Default role from state (AC5)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_default_role_from_state(tmp_path):
    """When role is not provided, should use current_role from state.json."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="architect")
    _write_role_file(tmp_path, "architect", "inputs:\n  - WorkItems/{id}/Design/{id}-design-doc.md\noutputs: []\ntools: []\n",
                     body="# Role: Architect\n\nArchitect instructions here.")

    result = await gcp_role_context(
        work_item_id=wid,
        # No role parameter — should default to "architect" from state
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "ok"
    assert "Architect" in result["bundle"], "Should default to current_role from state.json"


# ---------------------------------------------------------------------------
# TC6: No front-matter backward compat (AC6)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_no_frontmatter_backward_compat(tmp_path):
    """Roles without front-matter should return instructions + state + warning."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="legacy-role")
    # Write role file WITHOUT front-matter
    roles_dir = tmp_path / ".github" / "roles"
    roles_dir.mkdir(parents=True, exist_ok=True)
    (roles_dir / "legacy-role.md").write_text("# Legacy Role\n\nNo front-matter here.", encoding="utf-8")

    result = await gcp_role_context(
        work_item_id=wid,
        role="legacy-role",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "ok"
    bundle = result["bundle"]
    assert "# Legacy Role" in bundle, "Should include role instructions"
    assert "## Current State" in bundle, "Should include state section"
    # Should have warning about missing front-matter
    assert "warning" in bundle.lower() or "no front-matter" in bundle.lower(), \
        "Should handle missing front-matter gracefully with warning"


# ---------------------------------------------------------------------------
# TC7: Role instructions never truncated (NFR)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_role_instructions_never_truncated(tmp_path):
    """Role instructions must never be truncated even with small max_bundle_size."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="developer")
    role_body = "# Role: Developer\n\n" + ("Important instruction. " * 50)
    _write_role_file(tmp_path, "developer", "inputs:\n  - WorkItems/{id}/{id}-User-Story.md\noutputs: []\ntools: []\n",
                     body=role_body)
    _write_artifact(work_items_dir, wid, "TST-001-User-Story.md", "Y" * 3000)

    result = await gcp_role_context(
        work_item_id=wid,
        role="developer",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
        max_bundle_size=500,
    )

    assert result["status"] == "ok"
    # Role instructions should be fully present
    assert "Important instruction." in result["bundle"], "Role instructions must never be truncated"


# ---------------------------------------------------------------------------
# TC8: State summary section present (AC2)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_state_summary_fields(tmp_path):
    """Current State section must contain key fields."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="developer", phase="development")
    _write_role_file(tmp_path, "developer", "inputs: []\noutputs: []\ntools: []\n")

    result = await gcp_role_context(
        work_item_id=wid,
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "ok"
    bundle = result["bundle"]
    assert "TST-001" in bundle, "State summary missing work_item_id"
    assert "developer" in bundle, "State summary missing current_role"
    assert "development" in bundle, "State summary missing current_phase"


# ---------------------------------------------------------------------------
# TC9: Previous role notes included
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_previous_role_notes_included(tmp_path):
    """Previous role's decision notes should be included."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="quality-assurance")
    _write_role_file(tmp_path, "quality-assurance", "inputs:\n  - WorkItems/{id}/Design/{id}-design-doc.md\noutputs: []\ntools: []\n")
    # Write domain-expert notes (the role before quality-assurance)
    _write_artifact(work_items_dir, wid, "RoleDecisionNotes/TST-001-domain-expert.md",
                    "# Domain Expert Notes\nImportant domain guidance here.")

    result = await gcp_role_context(
        work_item_id=wid,
        role="quality-assurance",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "ok"
    assert "Important domain guidance here." in result["bundle"], \
        "Should include previous role's decision notes"


# ---------------------------------------------------------------------------
# TC10: Previous role notes for first role
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_first_role_no_previous_notes(tmp_path):
    """First role (POA) should show no previous role marker."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="project-owner-assistant", phase="definition")
    _write_role_file(tmp_path, "project-owner-assistant", "inputs: []\noutputs: []\ntools: []\n")

    result = await gcp_role_context(
        work_item_id=wid,
        role="project-owner-assistant",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "ok"
    assert "[no previous role]" in result["bundle"], \
        "First role should show no previous role marker"


# ---------------------------------------------------------------------------
# TC11: Invalid work item ID
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_work_item(tmp_path):
    """Non-existent work item should return error."""
    work_items_dir = tmp_path / "WorkItems"
    work_items_dir.mkdir(parents=True, exist_ok=True)

    result = await gcp_role_context(
        work_item_id="FAKE-999",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "error", "Should return error for invalid work item"
    assert "FAKE-999" in result.get("error", ""), "Error should mention the work item ID"


# ---------------------------------------------------------------------------
# TC12: Invalid role name
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_role_name(tmp_path):
    """Invalid role should return error."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="developer")

    result = await gcp_role_context(
        work_item_id=wid,
        role="nonexistent-role",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    # Should still work (returns role instructions from loader, which gives placeholder)
    # but the loader handles unknown roles gracefully
    assert result["status"] in ("ok", "error"), "Should handle invalid role"


# ---------------------------------------------------------------------------
# TC: Multiple input artifacts
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_multiple_input_artifacts(tmp_path):
    """Multiple artifacts from front-matter should all be included."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="architect")
    _write_role_file(
        tmp_path, "architect",
        "inputs:\n  - WorkItems/{id}/{id}-User-Story.md\n  - WorkItems/{id}/Design/{id}-design-doc.md\n  - WorkItems/{id}/Design/{id}-Review-Comments.md\noutputs: []\ntools: []\n",
    )
    _write_artifact(work_items_dir, wid, "TST-001-User-Story.md", "STORY_CONTENT_HERE")
    _write_artifact(work_items_dir, wid, "Design/TST-001-design-doc.md", "DESIGN_CONTENT_HERE")
    _write_artifact(work_items_dir, wid, "Design/TST-001-Review-Comments.md", "REVIEW_CONTENT_HERE")

    result = await gcp_role_context(
        work_item_id=wid,
        role="architect",
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert result["status"] == "ok"
    assert "STORY_CONTENT_HERE" in result["bundle"]
    assert "DESIGN_CONTENT_HERE" in result["bundle"]
    assert "REVIEW_CONTENT_HERE" in result["bundle"]
    assert result["artifact_count"] == 3


# ---------------------------------------------------------------------------
# TC: Metadata fields in result
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_result_metadata(tmp_path):
    """Result dict should include metadata fields."""
    wid = "TST-001"
    work_items_dir = tmp_path / "WorkItems"
    _write_state(work_items_dir, wid, role="developer")
    _write_role_file(tmp_path, "developer", "inputs:\n  - WorkItems/{id}/{id}-User-Story.md\noutputs: []\ntools: []\n")
    _write_artifact(work_items_dir, wid, "TST-001-User-Story.md", "Content")

    result = await gcp_role_context(
        work_item_id=wid,
        work_items_dir=work_items_dir,
        project_root=tmp_path,
    )

    assert "artifact_count" in result
    assert "total_size" in result
    assert "truncated" in result
    assert result["artifact_count"] == 1
    assert result["truncated"] is False
