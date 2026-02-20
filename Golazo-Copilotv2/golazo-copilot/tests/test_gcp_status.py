"""Tests for gcp_status tool."""

import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_create_workitem import gcp_create_workitem
from golazo_copilot.tools.gcp_transition import gcp_transition, ROLE_SUFFIX_MAP
from golazo_copilot.tools.gcp_status import gcp_status, _get_stale_files, _extract_version, _compute_role_progress, _get_registry_hint


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems"
TEST_WORKSPACE_ROOT = Path(__file__).parent

ALL_ROLES = [
    "project-owner-assistant", "program-manager", "quality-assurance",
    "architect", "developer", "refactor-expert", "builder", "documenter", "retrospective"
]


def create_empty_role_files(workspace_root: Path = TEST_WORKSPACE_ROOT):
    """Create role files with no Required Outputs section for testing."""
    roles_dir = workspace_root / ".github" / "roles"
    roles_dir.mkdir(parents=True, exist_ok=True)
    for role in ALL_ROLES:
        role_file = roles_dir / f"{role}.md"
        role_file.write_text(f"# Role: {role}\n\n## Purpose\nTest role.\n")


def create_test_file(work_item_id: str, filename: str) -> str:
    """Create a test file and return its path."""
    path = TEST_WORKITEMS_DIR / work_item_id / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Test content")
    return str(path)


def create_role_notes(work_item_id: str, role: str, work_items_dir: Path = TEST_WORKITEMS_DIR):
    """Helper to create role notes file for a given role."""
    suffix = ROLE_SUFFIX_MAP.get(role, role)
    notes_dir = work_items_dir / work_item_id / "RoleDecisionNotes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_file = notes_dir / f"{work_item_id}-{suffix}.md"
    notes_file.write_text(f"# {work_item_id}: {role} Notes\n\nTest notes.")
    return notes_file


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    create_empty_role_files()
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    roles_dir = TEST_WORKSPACE_ROOT / ".github"
    if roles_dir.exists():
        shutil.rmtree(roles_dir)


class TestStatusBasic:
    """Basic status tests."""

    @pytest.mark.asyncio
    async def test_returns_active_status(self):
        """Should return active=True for initialized work item."""
        await gcp_create_workitem(work_item_id="status-1", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="status-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["active"] is True
        assert result["work_item_id"] == "status-1"

    @pytest.mark.asyncio
    async def test_returns_current_role_and_phase(self):
        """Should return current role and phase."""
        await gcp_create_workitem(work_item_id="status-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="status-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["current_role"] == "project-owner-assistant"
        assert result["current_phase"] == "definition"

    @pytest.mark.asyncio
    async def test_returns_role_instructions(self):
        """Should return role instructions."""
        await gcp_create_workitem(work_item_id="status-3", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="status-3",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "role_instructions" in result
        assert len(result["role_instructions"]) > 50


class TestStatusNoWorkItem:
    """No work item tests."""

    @pytest.mark.asyncio
    async def test_no_work_item_returns_inactive(self):
        """Should return active=False if no work item."""
        result = await gcp_status(
            work_item_id="nonexistent",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["active"] is False
        assert "No active work item" in result.get("message", "") or "does not exist" in result.get("message", "")


class TestStatusAfterTransition:
    """Status after transitions."""

    @pytest.mark.asyncio
    async def test_status_reflects_transition(self):
        """Should reflect current role after transition."""
        await gcp_create_workitem(work_item_id="trans-status", work_items_dir=TEST_WORKITEMS_DIR)
        create_role_notes("trans-status", "project-owner-assistant")
        await gcp_transition(
            work_item_id="trans-status",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        result = await gcp_status(
            work_item_id="trans-status",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["current_role"] == "program-manager"


class TestStatusDeviations:
    """GCP-0014: Status should show deviations."""

    @pytest.mark.asyncio
    async def test_status_includes_deviations_list(self):
        """Should include deviations in status."""
        from golazo_copilot.tools.gcp_consent import gcp_consent
        
        await gcp_create_workitem(work_item_id="dev-status-1", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_consent(
            work_item_id="dev-status-1",
            action="skip_outputs",
            reason="PO approved spike exploration",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        result = await gcp_status(
            work_item_id="dev-status-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "deviations" in result
        assert len(result["deviations"]) == 1
        assert result["deviations"][0]["action"] == "skip_outputs"
        assert result["deviations"][0]["reason"] == "PO approved spike exploration"

    @pytest.mark.asyncio
    async def test_status_empty_deviations_list(self):
        """Should return empty list when no deviations."""
        await gcp_create_workitem(work_item_id="dev-status-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_status(
            work_item_id="dev-status-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "deviations" in result
        assert result["deviations"] == []

    @pytest.mark.asyncio
    async def test_status_deviation_has_required_fields(self):
        """Should include id, action, reason, timestamp, consumed."""
        from golazo_copilot.tools.gcp_consent import gcp_consent
        
        await gcp_create_workitem(work_item_id="dev-status-3", work_items_dir=TEST_WORKITEMS_DIR)
        await gcp_consent(
            work_item_id="dev-status-3",
            action="skip_role",
            reason="Work already implemented - syncing state",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        result = await gcp_status(
            work_item_id="dev-status-3",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        deviation = result["deviations"][0]
        assert "id" in deviation
        assert "action" in deviation
        assert "reason" in deviation
        assert "timestamp" in deviation
        assert "consumed" in deviation


class TestStatusMissingNotes:
    """GCP-0019: Status should show missing role notes."""

    @pytest.mark.asyncio
    async def test_status_includes_missing_notes_list(self):
        """TC-04: Should list roles missing decision notes."""
        await gcp_create_workitem(work_item_id="missing-notes-1", work_items_dir=TEST_WORKITEMS_DIR)
        # Create PO notes before transition (required by blocking enforcement)
        create_role_notes("missing-notes-1", "project-owner-assistant")
        await gcp_transition(
            work_item_id="missing-notes-1",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        result = await gcp_status(
            work_item_id="missing-notes-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "missing_notes" in result
        # Current role (PM) is not checked, only completed roles
        # PO notes exist, so should not be in missing list

    @pytest.mark.asyncio
    async def test_status_all_notes_present_empty_list(self):
        """TC-05: Should return empty list when all notes exist."""
        await gcp_create_workitem(work_item_id="missing-notes-2", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create PO notes
        notes_dir = TEST_WORKITEMS_DIR / "missing-notes-2" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "missing-notes-2-project-owner-assistant.md").write_text("# PO Notes")
        
        result = await gcp_status(
            work_item_id="missing-notes-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert "missing_notes" in result
        # Only PO role has been visited, and notes exist
        assert "project-owner-assistant" not in result["missing_notes"]


class TestPerFileStaleReporting:
    """GCP-0037: Per-file stale version reporting tests."""

    def test_all_files_up_to_date_no_stale(self, tmp_path):
        """TC1: All deployed files match source → empty stale list."""
        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        roles_dir = github_dir / "roles"
        roles_dir.mkdir()
        # Write spine with current source version
        from golazo_copilot.tools.gcp_status import _extract_version
        from importlib import resources
        source_files = resources.files("golazo_copilot")
        source_spine = source_files.joinpath("bootstrap-instructions.md").read_text(encoding="utf-8")
        spine_ver = _extract_version(source_spine)
        (github_dir / "copilot-instructions.md").write_text(
            f"<!-- Last Updated in Golazo Copilot Version: {spine_ver} -->\n# Instructions"
        )
        # Write each role with matching source version
        source_roles = resources.files("golazo_copilot.roles.defaults")
        from golazo_copilot.tools.gcp_status import _DEPLOYED_TO_SOURCE
        for deployed_rel, _, _ in _DEPLOYED_TO_SOURCE:
            if deployed_rel == ".github/copilot-instructions.md":
                continue
            role_name = deployed_rel.split("/")[-1]
            try:
                source_content = source_roles.joinpath(role_name).read_text(encoding="utf-8")
                ver = _extract_version(source_content)
            except Exception:
                ver = "2.101.0"
            (roles_dir / role_name).write_text(
                f"<!-- Last Updated in Golazo Copilot Version: {ver} -->\n# {role_name}"
            )

        result = _get_stale_files(tmp_path)
        assert result == []

    def test_spine_stale_only(self, tmp_path):
        """TC2: Spine stale, roles match → only spine listed."""
        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").write_text(
            "<!-- Last Updated in Golazo Copilot Version: 0.0.1 -->\n# Old spine"
        )
        result = _get_stale_files(tmp_path)
        stale_names = [s["file"] for s in result]
        assert "copilot-instructions.md" in stale_names
        assert result[0]["deployed"] == "0.0.1"

    def test_one_role_stale(self, tmp_path):
        """TC3: One role file stale → that role listed."""
        github_dir = tmp_path / ".github"
        roles_dir = github_dir / "roles"
        roles_dir.mkdir(parents=True)
        (roles_dir / "developer.md").write_text(
            "<!-- Last Updated in Golazo Copilot Version: 0.0.1 -->\n# Dev"
        )
        result = _get_stale_files(tmp_path)
        stale_names = [s["file"] for s in result]
        assert "developer.md" in stale_names

    def test_multiple_files_stale(self, tmp_path):
        """TC4: Multiple stale files → all listed."""
        github_dir = tmp_path / ".github"
        roles_dir = github_dir / "roles"
        roles_dir.mkdir(parents=True)
        (github_dir / "copilot-instructions.md").write_text(
            "<!-- Last Updated in Golazo Copilot Version: 0.0.1 -->\n# Old"
        )
        (roles_dir / "developer.md").write_text(
            "<!-- Last Updated in Golazo Copilot Version: 0.0.2 -->\n# Old dev"
        )
        (roles_dir / "architect.md").write_text(
            "<!-- Last Updated in Golazo Copilot Version: 0.0.3 -->\n# Old arch"
        )
        result = _get_stale_files(tmp_path)
        assert len(result) >= 3

    def test_missing_deployed_file_not_listed(self, tmp_path):
        """TC5: Missing deployed file → not listed as stale."""
        # No .github/roles/architect.md at all
        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        result = _get_stale_files(tmp_path)
        stale_names = [s["file"] for s in result]
        assert "architect.md" not in stale_names

    def test_deployed_no_version_comment_skipped(self, tmp_path):
        """TC6: Deployed file has no version comment → skipped."""
        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").write_text("# No version here")
        result = _get_stale_files(tmp_path)
        stale_names = [s["file"] for s in result]
        assert "copilot-instructions.md" not in stale_names

    def test_no_github_directory_no_stale(self, tmp_path):
        """TC8: No .github directory → empty stale list."""
        result = _get_stale_files(tmp_path)
        assert result == []

    def test_stale_file_structure(self, tmp_path):
        """TC9: Stale file entry has correct keys."""
        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").write_text(
            "<!-- Last Updated in Golazo Copilot Version: 0.0.1 -->\n# Old"
        )
        result = _get_stale_files(tmp_path)
        stale = [s for s in result if s["file"] == "copilot-instructions.md"]
        assert len(stale) == 1
        assert "deployed" in stale[0]
        assert "source" in stale[0]
        assert stale[0]["deployed"] == "0.0.1"

    @pytest.mark.asyncio
    async def test_status_includes_per_file_version_warning(self):
        """TC10: gcp_status version_warning lists specific stale files."""
        from golazo_copilot import __version__
        await gcp_create_workitem(work_item_id="stale-pf-1", work_items_dir=TEST_WORKITEMS_DIR)

        workspace_root = TEST_WORKITEMS_DIR.parent
        instructions_dir = workspace_root / ".github"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = instructions_dir / "copilot-instructions.md"
        original = instructions_file.read_text(encoding="utf-8") if instructions_file.exists() else None

        instructions_file.write_text("<!-- Last Updated in Golazo Copilot Version: 0.0.1 -->\n# Old")

        try:
            result = await gcp_status(
                work_item_id="stale-pf-1",
                work_items_dir=TEST_WORKITEMS_DIR
            )
            assert result.get("version_warning") is not None
            assert "copilot-instructions.md" in result["version_warning"]
            assert "gcp_bootstrap" in result["version_warning"]
        finally:
            if original:
                instructions_file.write_text(original)
            else:
                instructions_file.write_text(
                    f"<!-- Last Updated in Golazo Copilot Version: {__version__} -->\n# Restored"
                )

    @pytest.mark.asyncio
    async def test_status_no_warning_when_all_match(self):
        """TC2.2: gcp_status returns no version_warning when versions match."""
        from golazo_copilot import __version__
        await gcp_create_workitem(work_item_id="stale-pf-2", work_items_dir=TEST_WORKITEMS_DIR)

        workspace_root = TEST_WORKITEMS_DIR.parent
        instructions_dir = workspace_root / ".github"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        instructions_file = instructions_dir / "copilot-instructions.md"
        instructions_file.write_text(
            f"<!-- Last Updated in Golazo Copilot Version: {__version__} -->\n# Current"
        )

        result = await gcp_status(
            work_item_id="stale-pf-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        assert result.get("version_warning") is None


class TestRoleProgress:
    """GCP-0033: Role progress display tests."""

    @pytest.mark.asyncio
    async def test_fresh_work_item_zero_completed(self):
        """TC1.1: Fresh work item has 0 completed, PO in-progress."""
        await gcp_create_workitem(work_item_id="progress-1", work_items_dir=TEST_WORKITEMS_DIR)

        result = await gcp_status(
            work_item_id="progress-1",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        progress = result["role_progress"]
        assert progress["roles_completed"] == 0
        assert progress["roles_total"] == 9

        # PO should be in-progress
        po = next(r for r in progress["roles"] if r["role"] == "project-owner-assistant")
        assert po["status"] == "in-progress"

        # All others should be pending
        for entry in progress["roles"]:
            if entry["role"] != "project-owner-assistant":
                assert entry["status"] == "pending", f"{entry['role']} should be pending"

    @pytest.mark.asyncio
    async def test_after_transitions_correct_count(self):
        """TC1.2: After transitions, completed count is correct."""
        await gcp_create_workitem(work_item_id="progress-2", work_items_dir=TEST_WORKITEMS_DIR)

        # Create required outputs for PO role
        create_role_notes("progress-2", "project-owner-assistant")
        create_test_file("progress-2", "progress-2-User-Story.md")

        # Transition to PM
        await gcp_transition(
            work_item_id="progress-2", role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR
        )

        result = await gcp_status(
            work_item_id="progress-2",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        progress = result["role_progress"]
        assert progress["roles_completed"] == 1  # PO completed

        po = next(r for r in progress["roles"] if r["role"] == "project-owner-assistant")
        assert po["status"] == "completed"

        pm = next(r for r in progress["roles"] if r["role"] == "program-manager")
        assert pm["status"] == "in-progress"

    @pytest.mark.asyncio
    async def test_role_progress_list_has_all_roles(self):
        """TC1.3: Progress list contains all 9 workflow roles."""
        await gcp_create_workitem(work_item_id="progress-3", work_items_dir=TEST_WORKITEMS_DIR)

        result = await gcp_status(
            work_item_id="progress-3",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        progress = result["role_progress"]
        role_names = [r["role"] for r in progress["roles"]]
        assert len(role_names) == 9
        assert "project-owner-assistant" in role_names
        assert "retrospective" in role_names


class TestRegistryHint:
    """GCP-0042: Capability registry hint in status output."""

    def test_no_capabilities_yaml_returns_none(self, tmp_path):
        """TC1: No capabilities.yaml → returns None."""
        assert _get_registry_hint(tmp_path) is None

    def test_valid_yaml_returns_count_hint(self, tmp_path):
        """TC2: Valid capabilities.yaml → returns count hint."""
        (tmp_path / "capabilities.yaml").write_text(
            "capabilities:\n  - name: a\n  - name: b\n",
            encoding="utf-8",
        )
        hint = _get_registry_hint(tmp_path)
        assert hint is not None
        assert "2" in hint
        assert "gcp_capabilities" in hint

    def test_malformed_yaml_returns_warning(self, tmp_path):
        """TC3: Malformed YAML → returns warning (no crash)."""
        (tmp_path / "capabilities.yaml").write_text(
            "{{not: valid: yaml::",
            encoding="utf-8",
        )
        hint = _get_registry_hint(tmp_path)
        assert hint is not None
        assert "failed to parse" in hint

    def test_missing_capabilities_key_returns_warning(self, tmp_path):
        """TC4: Valid YAML but no capabilities key → returns warning."""
        (tmp_path / "capabilities.yaml").write_text(
            "other: stuff\n",
            encoding="utf-8",
        )
        hint = _get_registry_hint(tmp_path)
        assert hint is not None
        assert "missing" in hint.lower()

    def test_empty_capabilities_list_returns_zero(self, tmp_path):
        """TC5: Empty capabilities list → returns '0'."""
        (tmp_path / "capabilities.yaml").write_text(
            "capabilities: []\n",
            encoding="utf-8",
        )
        hint = _get_registry_hint(tmp_path)
        assert hint is not None
        assert "0" in hint

    @pytest.mark.asyncio
    async def test_status_includes_registry_hint_key(self):
        """TC6: gcp_status includes registry_hint key when capabilities.yaml exists."""
        wi_id = "reg-hint-1"
        await gcp_create_workitem(work_item_id=wi_id, work_items_dir=TEST_WORKITEMS_DIR)
        # Create capabilities.yaml in workspace root (parent of WorkItems)
        workspace_root = TEST_WORKITEMS_DIR.parent
        cap_path = workspace_root / "capabilities.yaml"
        cap_path.write_text("capabilities:\n  - name: test\n", encoding="utf-8")
        try:
            result = await gcp_status(work_item_id=wi_id, work_items_dir=TEST_WORKITEMS_DIR)
            assert "registry_hint" in result
            assert result["registry_hint"] is not None
            assert "1" in result["registry_hint"]
        finally:
            cap_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_status_registry_hint_none_when_absent(self):
        """TC7: gcp_status registry_hint is None when no capabilities.yaml."""
        wi_id = "reg-hint-2"
        await gcp_create_workitem(work_item_id=wi_id, work_items_dir=TEST_WORKITEMS_DIR)
        result = await gcp_status(work_item_id=wi_id, work_items_dir=TEST_WORKITEMS_DIR)
        assert result.get("registry_hint") is None
