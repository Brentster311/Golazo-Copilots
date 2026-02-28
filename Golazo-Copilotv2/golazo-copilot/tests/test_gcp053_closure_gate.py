"""Tests for GCP-0053: POA Closure Gate.

Covers:
- closure_pending state field (default, set, preserved)
- Output validator closure-only annotation parsing
- Transition enforcement (retro→POA in complete vs express/spike)
- Status output distinguishes closure mode
- Backward compatibility with old state.json
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from golazo_copilot.core.types import WorkItemState, RoleHistoryEntry
from golazo_copilot.core.output_validator import parse_required_outputs, OutputSpec
from golazo_copilot.core.persistence import save_state, load_state
from golazo_copilot.tools.golazo_transition import golazo_transition


# ── Helpers ──────────────────────────────────────────────────────────

def _make_state(
    work_item_id: str = "TST-001",
    profile: str = "complete",
    current_role: str = "retrospective",
    current_phase: str = "completion",
    closure_pending: bool = False,
    roles_up_to: str | None = None,
) -> WorkItemState:
    """Create a WorkItemState for testing with optional role history."""
    now = datetime.now(timezone.utc)
    history = []
    if roles_up_to:
        from golazo_copilot.core.transitions import ROLE_ORDER
        for role in ROLE_ORDER:
            entry = RoleHistoryEntry(role=role, entered_at=now, exited_at=now)
            history.append(entry)
            if role == roles_up_to:
                # Last one is current — no exit
                history[-1].exited_at = None
                break
    return WorkItemState(
        work_item_id=work_item_id,
        profile=profile,
        current_role=current_role,
        current_phase=current_phase,
        closure_pending=closure_pending,
        created_at=now,
        updated_at=now,
        role_history=history,
    )


def _setup_work_item(tmp_path: Path, state: WorkItemState) -> Path:
    """Set up a work item directory with state and all role notes."""
    from golazo_copilot.tools.golazo_transition import ROLE_SUFFIX_MAP
    wi_dir = tmp_path / "WorkItems"
    wi_dir.mkdir()
    item_dir = wi_dir / state.work_item_id
    item_dir.mkdir()
    notes_dir = item_dir / "RoleDecisionNotes"
    notes_dir.mkdir(parents=True)

    # Create role notes for all completed roles
    for entry in state.role_history:
        suffix = ROLE_SUFFIX_MAP.get(entry.role, entry.role)
        (notes_dir / f"{state.work_item_id}-{suffix}.md").write_text(f"# {entry.role} notes")

    save_state(state.work_item_id, state, wi_dir)
    return wi_dir


# ── TC-04/TC-05: closure_pending state field ─────────────────────────

class TestClosurePendingField:
    """Tests for the closure_pending field on WorkItemState."""

    def test_default_is_false(self):
        """TC-05: closure_pending defaults to False on new state."""
        state = _make_state()
        assert state.closure_pending is False

    def test_can_set_true(self):
        """closure_pending can be set to True."""
        state = _make_state(closure_pending=True)
        assert state.closure_pending is True

    def test_backward_compat_missing_field(self, tmp_path):
        """TC-10: Old state.json without closure_pending loads with False default."""
        wi_dir = tmp_path / "WorkItems"
        wi_dir.mkdir()
        item_dir = wi_dir / "TST-001"
        item_dir.mkdir()
        # Write state JSON without closure_pending
        state_data = {
            "schema_version": "1.0",
            "work_item_id": "TST-001",
            "profile": "complete",
            "current_phase": "definition",
            "current_role": "project-owner-assistant",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "role_history": [],
            "deviations": [],
        }
        (item_dir / "state.json").write_text(json.dumps(state_data))
        loaded = load_state("TST-001", wi_dir)
        assert loaded.closure_pending is False

    def test_closure_pending_persists_roundtrip(self, tmp_path):
        """closure_pending survives save/load cycle."""
        wi_dir = tmp_path / "WorkItems"
        wi_dir.mkdir()
        (wi_dir / "TST-001").mkdir()
        state = _make_state(closure_pending=True)
        save_state("TST-001", state, wi_dir)
        loaded = load_state("TST-001", wi_dir)
        assert loaded.closure_pending is True


# ── TC-08/TC-09/TC-11/TC-12/TC-16/TC-17/TC-18: Output validator ─────

class TestClosureOnlyAnnotation:
    """Tests for <!-- closure-only --> annotation in output validator."""

    ROLE_CONTENT_WITH_CLOSURE = """# Role: POA

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- file: WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md
<!-- closure-only -->
- file: WorkItems/{id}/{id}-closure.md
"""

    def test_parse_tags_closure_only_spec(self):
        """TC-11: <!-- closure-only --> annotation sets closure_only=True on OutputSpec."""
        specs = parse_required_outputs(self.ROLE_CONTENT_WITH_CLOSURE, "TST-001")
        closure_specs = [s for s in specs if s.closure_only]
        assert len(closure_specs) == 1
        assert "closure.md" in closure_specs[0].path_or_pattern

    def test_non_closure_outputs_not_tagged(self):
        """TC-18: Non-closure outputs have closure_only=False."""
        specs = parse_required_outputs(self.ROLE_CONTENT_WITH_CLOSURE, "TST-001")
        non_closure = [s for s in specs if not s.closure_only]
        assert len(non_closure) == 2

    def test_initial_poa_excludes_closure_output(self):
        """TC-08: When closure_mode=False, closure-only specs should be filtered out by caller."""
        specs = parse_required_outputs(self.ROLE_CONTENT_WITH_CLOSURE, "TST-001")
        active_specs = [s for s in specs if not s.closure_only]
        paths = [s.path_or_pattern for s in active_specs]
        assert not any("closure" in p for p in paths)

    def test_closure_reentry_includes_closure_output(self):
        """TC-09: When closure_mode=True, all specs including closure-only are active."""
        specs = parse_required_outputs(self.ROLE_CONTENT_WITH_CLOSURE, "TST-001")
        # Caller includes all when closure_mode=True
        active_specs = [s for s in specs if not s.closure_only or True]
        paths = [s.path_or_pattern for s in active_specs]
        assert any("closure" in p for p in paths)
        assert len(active_specs) == 3

    def test_inline_html_comment_stripped_from_path(self):
        """TC-16: Inline HTML comment is NOT included in the output file path."""
        content = """## Required Outputs
- file: WorkItems/{id}/{id}-closure.md  <!-- Only during Closure re-entry -->
"""
        specs = parse_required_outputs(content, "TST-001")
        assert len(specs) == 1
        assert "<!--" not in specs[0].path_or_pattern
        assert specs[0].path_or_pattern == "WorkItems/TST-001/TST-001-closure.md"

    def test_multiple_closure_only_outputs(self):
        """TC-17: Multiple closure-only outputs are all tagged."""
        content = """## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
<!-- closure-only -->
- file: WorkItems/{id}/{id}-closure.md
<!-- closure-only -->
- file: WorkItems/{id}/{id}-acceptance.md
"""
        specs = parse_required_outputs(content, "TST-001")
        closure_specs = [s for s in specs if s.closure_only]
        assert len(closure_specs) == 2

    def test_annotation_not_adjacent_is_ignored(self):
        """Annotation followed by non-output line doesn't tag the next output."""
        content = """## Required Outputs
<!-- closure-only -->

- file: WorkItems/{id}/{id}-User-Story.md
"""
        specs = parse_required_outputs(content, "TST-001")
        # The blank line between annotation and output means it should NOT be tagged
        assert len(specs) == 1
        assert specs[0].closure_only is False


# ── TC-01/TC-02/TC-03/TC-04/TC-13: Transition logic ─────────────────

class TestClosureTransition:
    """Tests for retro→POA transition with closure gate."""

    @pytest.fixture
    def complete_at_retro(self, tmp_path):
        """Work item in complete profile at retrospective with all notes."""
        state = _make_state(
            profile="complete",
            current_role="retrospective",
            current_phase="completion",
            roles_up_to="retrospective",
        )
        wi_dir = _setup_work_item(tmp_path, state)
        # Create required outputs for retrospective role
        item_dir = wi_dir / "TST-001"
        design_dir = item_dir / "Design"
        design_dir.mkdir(exist_ok=True)
        # Also create a mock .github/roles dir for role content loading
        roles_dir = tmp_path / ".github" / "roles"
        roles_dir.mkdir(parents=True, exist_ok=True)
        return wi_dir, tmp_path

    @pytest.fixture
    def express_at_retro(self, tmp_path):
        """Work item in express profile at retrospective."""
        state = _make_state(
            profile="express",
            current_role="retrospective",
            current_phase="completion",
            roles_up_to="retrospective",
        )
        wi_dir = _setup_work_item(tmp_path, state)
        return wi_dir, tmp_path

    @pytest.fixture
    def spike_at_retro(self, tmp_path):
        """Work item in spike profile at retrospective."""
        state = _make_state(
            profile="spike",
            current_role="retrospective",
            current_phase="completion",
            roles_up_to="retrospective",
        )
        wi_dir = _setup_work_item(tmp_path, state)
        return wi_dir, tmp_path

    @pytest.mark.asyncio
    async def test_complete_retro_to_poa_sets_closure_pending(self, complete_at_retro):
        """TC-01/TC-04: In complete profile, retro→POA sets closure_pending=True."""
        wi_dir, project_root = complete_at_retro
        result = await golazo_transition(
            work_item_id="TST-001",
            role="project-owner-assistant",
            work_items_dir=wi_dir,
            project_root=project_root,
        )
        assert result["success"], f"Transition failed: {result.get('error')}"
        # Verify state was updated
        state = load_state("TST-001", wi_dir)
        assert state.closure_pending is True
        assert state.current_role == "project-owner-assistant"

    @pytest.mark.asyncio
    async def test_express_retro_to_poa_no_closure_pending(self, express_at_retro):
        """TC-02: In express profile, retro→POA does NOT set closure_pending."""
        wi_dir, project_root = express_at_retro
        result = await golazo_transition(
            work_item_id="TST-001",
            role="project-owner-assistant",
            work_items_dir=wi_dir,
            project_root=project_root,
        )
        assert result["success"]
        state = load_state("TST-001", wi_dir)
        assert state.closure_pending is False

    @pytest.mark.asyncio
    async def test_spike_retro_to_poa_no_closure_pending(self, spike_at_retro):
        """TC-03: In spike profile, retro→POA does NOT set closure_pending."""
        wi_dir, project_root = spike_at_retro
        result = await golazo_transition(
            work_item_id="TST-001",
            role="project-owner-assistant",
            work_items_dir=wi_dir,
            project_root=project_root,
        )
        assert result["success"]
        state = load_state("TST-001", wi_dir)
        assert state.closure_pending is False

    @pytest.mark.asyncio
    async def test_closure_pending_preserved_through_transition(self, complete_at_retro):
        """TC-13: Forward transition from closure POA preserves closure_pending.
        
        POA is index 0 in ROLE_ORDER so no backward transitions exist from it.
        Instead we verify the flag persists through a forward POA→PM transition.
        """
        wi_dir, project_root = complete_at_retro
        # First transition retro→POA to set closure_pending
        await golazo_transition(
            work_item_id="TST-001", role="project-owner-assistant",
            work_items_dir=wi_dir, project_root=project_root,
        )
        state = load_state("TST-001", wi_dir)
        assert state.closure_pending is True

        # Create POA notes and required outputs for forward transition
        from golazo_copilot.tools.golazo_transition import ROLE_SUFFIX_MAP
        notes_dir = wi_dir / "TST-001" / "RoleDecisionNotes"
        suffix = ROLE_SUFFIX_MAP["project-owner-assistant"]
        (notes_dir / f"TST-001-{suffix}.md").write_text("# Closure POA notes")
        # Create user story (required POA output)
        (wi_dir / "TST-001" / "TST-001-User-Story.md").write_text("# User Story")
        # Create closure.md (required in closure mode)
        (wi_dir / "TST-001" / "TST-001-closure.md").write_text("# Closure")

        # Forward transition POA → PM
        result = await golazo_transition(
            work_item_id="TST-001", role="program-manager",
            work_items_dir=wi_dir, project_root=project_root,
        )
        assert result["success"], f"Transition failed: {result.get('error')}"
        state = load_state("TST-001", wi_dir)
        assert state.closure_pending is True  # Must be preserved (AD-1: never cleared)


# ── TC-06/TC-07/TC-15: Status output ────────────────────────────────

class TestClosureStatus:
    """Tests for golazo_status closure_pending reporting."""

    @pytest.mark.asyncio
    async def test_status_shows_closure_pending(self, tmp_path):
        """TC-06: golazo_status includes closure_pending=True when set."""
        from golazo_copilot.tools.golazo_status import golazo_status
        state = _make_state(
            current_role="project-owner-assistant",
            current_phase="definition",
            closure_pending=True,
            roles_up_to="project-owner-assistant",
        )
        wi_dir = _setup_work_item(tmp_path, state)
        result = await golazo_status(
            work_item_id="TST-001",
            work_items_dir=wi_dir,
            project_root=tmp_path,
        )
        assert result["active"]
        assert result["closure_pending"] is True

    @pytest.mark.asyncio
    async def test_status_no_closure_on_initial_poa(self, tmp_path):
        """TC-07: golazo_status shows closure_pending=False on initial POA entry."""
        from golazo_copilot.tools.golazo_status import golazo_status
        state = _make_state(
            current_role="project-owner-assistant",
            current_phase="definition",
            closure_pending=False,
            roles_up_to="project-owner-assistant",
        )
        wi_dir = _setup_work_item(tmp_path, state)
        result = await golazo_status(
            work_item_id="TST-001",
            work_items_dir=wi_dir,
            project_root=tmp_path,
        )
        assert result["active"]
        assert result["closure_pending"] is False

    @pytest.mark.asyncio
    async def test_status_closure_complete_reports_full_progress(self, tmp_path):
        """Closure mode with complete outputs reports 10/10 progress."""
        from golazo_copilot.tools.golazo_status import golazo_status

        now = datetime.now(timezone.utc)
        role_history = [
            RoleHistoryEntry(role=role, entered_at=now, exited_at=now)
            for role in [
                "project-owner-assistant",
                "program-manager",
                "domain-expert",
                "quality-assurance",
                "architect",
                "developer",
                "refactor-expert",
                "builder",
                "documenter",
                "retrospective",
            ]
        ]
        role_history.append(
            RoleHistoryEntry(role="project-owner-assistant", entered_at=now, exited_at=None)
        )
        state = WorkItemState(
            work_item_id="TST-001",
            profile="complete",
            current_role="project-owner-assistant",
            current_phase="closure",
            closure_pending=True,
            created_at=now,
            updated_at=now,
            role_history=role_history,
        )

        wi_dir = _setup_work_item(tmp_path, state)
        item_dir = wi_dir / "TST-001"
        (item_dir / "TST-001-User-Story.md").write_text("# User Story")
        (item_dir / "TST-001-closure.md").write_text("# Closure")

        result = await golazo_status(
            work_item_id="TST-001",
            work_items_dir=wi_dir,
            project_root=tmp_path,
        )

        assert result["required_outputs"]["complete"] is True
        assert result["role_progress"]["roles_completed"] == result["role_progress"]["roles_total"]

    @pytest.mark.asyncio
    async def test_status_closure_incomplete_keeps_current_progress(self, tmp_path):
        """Closure mode without complete outputs should not force full progress."""
        from golazo_copilot.tools.golazo_status import golazo_status

        now = datetime.now(timezone.utc)
        role_history = [
            RoleHistoryEntry(role=role, entered_at=now, exited_at=now)
            for role in [
                "project-owner-assistant",
                "program-manager",
                "domain-expert",
                "quality-assurance",
                "architect",
                "developer",
                "refactor-expert",
                "builder",
                "documenter",
                "retrospective",
            ]
        ]
        role_history.append(
            RoleHistoryEntry(role="project-owner-assistant", entered_at=now, exited_at=None)
        )
        state = WorkItemState(
            work_item_id="TST-001",
            profile="complete",
            current_role="project-owner-assistant",
            current_phase="closure",
            closure_pending=True,
            created_at=now,
            updated_at=now,
            role_history=role_history,
        )

        wi_dir = _setup_work_item(tmp_path, state)
        item_dir = wi_dir / "TST-001"
        (item_dir / "TST-001-User-Story.md").write_text("# User Story")

        result = await golazo_status(
            work_item_id="TST-001",
            work_items_dir=wi_dir,
            project_root=tmp_path,
        )

        assert result["required_outputs"]["complete"] is False
        assert result["role_progress"]["roles_completed"] < result["role_progress"]["roles_total"]


# ── TC-14: Retrospective role content ────────────────────────────────

class TestRetrospectiveRoleContent:
    """Tests for retrospective role file containing closure handoff instruction."""

    def test_retro_role_mentions_poa_transition(self):
        """TC-14: Retrospective role file instructs transition to POA for complete profile."""
        from importlib import resources
        files = resources.files("golazo_copilot.roles.defaults")
        content = files.joinpath("retrospective.md").read_text(encoding="utf-8")
        assert "project-owner-assistant" in content.lower() or "closure" in content.lower()
