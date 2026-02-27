"""Tests for GCP-0055: Profile-aware role-skipping for express and spike profiles.

AC1: Express profile enforces 5-role sequence (POA → QA → Dev → Builder → Retro)
AC2: Spike profile enforces 5-role sequence (POA → Domain-Expert → Architect → Dev → Retro)
AC3: Complete profile behavior unchanged (all 10 roles)
AC4: golazo_status reports correct role sequence for active profile
AC5: All existing tests pass with zero regressions; new tests cover express and spike
AC6: Backward transitions within a profile's role sequence work correctly
"""

import asyncio
import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.core.transitions import (
    PROFILE_ROLES,
    ROLE_ORDER,
    get_role_order_for_profile,
    validate_transition,
    is_backward_transition,
    _build_transitions_for_profile,
)
from golazo_copilot.tools.golazo_create_workitem import golazo_create_workitem
from golazo_copilot.tools.golazo_transition import golazo_transition, ROLE_SUFFIX_MAP
from golazo_copilot.tools.golazo_status import golazo_status as golazo_status_tool
from golazo_copilot.core.persistence import load_state, save_state


TEST_WORKITEMS_DIR = Path(__file__).parent / "test-workitems-profiles"
TEST_WORKSPACE_ROOT = Path(__file__).parent

ALL_ROLES = [
    "project-owner-assistant", "program-manager", "domain-expert", "quality-assurance",
    "architect", "developer", "refactor-expert", "builder", "documenter", "retrospective"
]


def create_empty_role_files(workspace_root: Path = TEST_WORKSPACE_ROOT):
    """Create role files with no Required Outputs section for testing."""
    roles_dir = workspace_root / ".github" / "roles"
    roles_dir.mkdir(parents=True, exist_ok=True)
    for role in ALL_ROLES:
        role_file = roles_dir / f"{role}.md"
        role_file.write_text(f"# Role: {role}\n\n## Purpose\nTest role.\n")


def create_role_notes(work_item_id: str, role: str, work_items_dir: Path = TEST_WORKITEMS_DIR):
    """Helper to create role notes file for a given role."""
    suffix = ROLE_SUFFIX_MAP.get(role, role)
    notes_dir = work_items_dir / work_item_id / "RoleDecisionNotes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_file = notes_dir / f"{work_item_id}-{suffix}.md"
    notes_file.write_text(f"# {work_item_id}: {role} Notes\n\nTest notes.")
    return notes_file


async def advance_through_profile(work_item_id: str, target_role: str, profile: str,
                                   work_items_dir: Path = TEST_WORKITEMS_DIR):
    """Advance through roles in a profile's sequence to reach target_role."""
    role_sequence = get_role_order_for_profile(profile)
    target_idx = role_sequence.index(target_role)

    for i, role in enumerate(role_sequence[:target_idx]):
        create_role_notes(work_item_id, role, work_items_dir)
        next_role = role_sequence[i + 1]
        result = await golazo_transition(
            work_item_id=work_item_id, role=next_role, work_items_dir=work_items_dir
        )
        assert result["success"], f"Failed transitioning to {next_role}: {result.get('error')}"


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


# ── AC1: Express profile enforces 5-role sequence ────────────────────


class TestExpressProfileSequence:
    """AC1: Express profile transitions enforce POA → QA → Dev → Builder → Retro."""

    def test_express_role_order(self):
        """Express PROFILE_ROLES has exactly 5 roles in correct order."""
        assert PROFILE_ROLES["express"] == [
            "project-owner-assistant",
            "quality-assurance",
            "developer",
            "builder",
            "retrospective",
        ]

    def test_express_forward_poa_to_qa(self):
        """POA → QA is valid forward transition for express."""
        valid, err = validate_transition("project-owner-assistant", "quality-assurance", profile="express")
        assert valid is True
        assert err is None

    def test_express_rejects_poa_to_pm(self):
        """POA → PM is rejected — PM is not in express profile."""
        valid, err = validate_transition("project-owner-assistant", "program-manager", profile="express")
        assert valid is False
        assert "not part of the 'express' profile" in err

    def test_express_rejects_skipped_roles(self):
        """All skipped roles (PM, domain-expert, architect, refactor-expert, documenter) are rejected."""
        skipped = ["program-manager", "domain-expert", "architect", "refactor-expert", "documenter"]
        for skipped_role in skipped:
            valid, err = validate_transition("project-owner-assistant", skipped_role, profile="express")
            assert valid is False, f"Should reject transition to {skipped_role}"

    @pytest.mark.asyncio
    async def test_express_full_traversal(self):
        """Can traverse all 5 express roles end-to-end."""
        await golazo_create_workitem(
            work_item_id="EXP-001", profile="express", work_items_dir=TEST_WORKITEMS_DIR
        )
        expected_sequence = ["quality-assurance", "developer", "builder", "retrospective"]
        current = "project-owner-assistant"
        for next_role in expected_sequence:
            create_role_notes("EXP-001", current, TEST_WORKITEMS_DIR)
            result = await golazo_transition(
                work_item_id="EXP-001", role=next_role, work_items_dir=TEST_WORKITEMS_DIR
            )
            assert result["success"], f"Failed {current} → {next_role}: {result.get('error')}"
            current = next_role

        state = load_state("EXP-001", TEST_WORKITEMS_DIR)
        assert state.current_role == "retrospective"

    @pytest.mark.asyncio
    async def test_express_rejects_skipped_role_at_runtime(self):
        """Runtime transition to a skipped role is rejected."""
        await golazo_create_workitem(
            work_item_id="EXP-002", profile="express", work_items_dir=TEST_WORKITEMS_DIR
        )
        create_role_notes("EXP-002", "project-owner-assistant", TEST_WORKITEMS_DIR)
        # Try to go to program-manager (skipped in express)
        result = await golazo_transition(
            work_item_id="EXP-002", role="program-manager", work_items_dir=TEST_WORKITEMS_DIR
        )
        assert result["success"] is False
        assert "not part of the 'express' profile" in result["error"]


# ── AC2: Spike profile enforces 5-role sequence ─────────────────────


class TestSpikeProfileSequence:
    """AC2: Spike profile transitions enforce POA → Domain-Expert → Architect → Dev → Retro."""

    def test_spike_role_order(self):
        """Spike PROFILE_ROLES has exactly 5 roles in correct order."""
        assert PROFILE_ROLES["spike"] == [
            "project-owner-assistant",
            "domain-expert",
            "architect",
            "developer",
            "retrospective",
        ]

    def test_spike_forward_poa_to_domain_expert(self):
        """POA → domain-expert is valid forward transition for spike."""
        valid, err = validate_transition("project-owner-assistant", "domain-expert", profile="spike")
        assert valid is True

    def test_spike_rejects_poa_to_pm(self):
        """POA → PM is rejected — PM is not in spike profile."""
        valid, err = validate_transition("project-owner-assistant", "program-manager", profile="spike")
        assert valid is False

    def test_spike_rejects_skipped_roles(self):
        """All skipped roles (PM, QA, refactor-expert, documenter, builder) are rejected."""
        skipped = ["program-manager", "quality-assurance", "refactor-expert", "documenter", "builder"]
        for skipped_role in skipped:
            valid, err = validate_transition("project-owner-assistant", skipped_role, profile="spike")
            assert valid is False, f"Should reject transition to {skipped_role}"

    @pytest.mark.asyncio
    async def test_spike_full_traversal(self):
        """Can traverse all 5 spike roles end-to-end."""
        await golazo_create_workitem(
            work_item_id="SPK-001", profile="spike", work_items_dir=TEST_WORKITEMS_DIR
        )
        expected_sequence = ["domain-expert", "architect", "developer", "retrospective"]
        current = "project-owner-assistant"
        for next_role in expected_sequence:
            create_role_notes("SPK-001", current, TEST_WORKITEMS_DIR)
            result = await golazo_transition(
                work_item_id="SPK-001", role=next_role, work_items_dir=TEST_WORKITEMS_DIR
            )
            assert result["success"], f"Failed {current} → {next_role}: {result.get('error')}"
            current = next_role

        state = load_state("SPK-001", TEST_WORKITEMS_DIR)
        assert state.current_role == "retrospective"


# ── AC3: Complete profile unchanged ──────────────────────────────────


class TestCompleteProfileUnchanged:
    """AC3: Complete profile behavior is unchanged — all 10 roles."""

    def test_complete_role_order_matches_original(self):
        """Complete profile uses the full ROLE_ORDER."""
        assert PROFILE_ROLES["complete"] is ROLE_ORDER

    def test_complete_forward_transitions_all_valid(self):
        """All 10 sequential forward transitions are valid for complete."""
        for i in range(len(ROLE_ORDER) - 1):
            valid, err = validate_transition(ROLE_ORDER[i], ROLE_ORDER[i + 1], profile="complete")
            assert valid is True, f"Should allow {ROLE_ORDER[i]} → {ROLE_ORDER[i+1]}"

    def test_complete_no_skipping(self):
        """Skipping a role in complete profile is rejected."""
        valid, err = validate_transition("project-owner-assistant", "domain-expert", profile="complete")
        assert valid is False

    def test_default_profile_is_complete(self):
        """validate_transition without profile arg uses complete."""
        valid, err = validate_transition("project-owner-assistant", "program-manager")
        assert valid is True
        valid, err = validate_transition("project-owner-assistant", "quality-assurance")
        assert valid is False


# ── AC4: golazo_status reports correct profile role sequence ─────────


class TestStatusProfileAware:
    """AC4: golazo_status reports the correct role sequence for the active profile."""

    @pytest.mark.asyncio
    async def test_express_status_shows_5_roles(self):
        """Status for express work item shows 5-role progress."""
        await golazo_create_workitem(
            work_item_id="EXP-010", profile="express", work_items_dir=TEST_WORKITEMS_DIR
        )
        result = await golazo_status_tool(
            work_item_id="EXP-010", work_items_dir=TEST_WORKITEMS_DIR
        )
        assert result["active"] is True
        assert result["role_progress"]["roles_total"] == 5
        role_names = [r["role"] for r in result["role_progress"]["roles"]]
        assert role_names == [
            "project-owner-assistant", "quality-assurance",
            "developer", "builder", "retrospective",
        ]

    @pytest.mark.asyncio
    async def test_spike_status_shows_5_roles(self):
        """Status for spike work item shows 5-role progress."""
        await golazo_create_workitem(
            work_item_id="SPK-010", profile="spike", work_items_dir=TEST_WORKITEMS_DIR
        )
        result = await golazo_status_tool(
            work_item_id="SPK-010", work_items_dir=TEST_WORKITEMS_DIR
        )
        assert result["active"] is True
        assert result["role_progress"]["roles_total"] == 5
        role_names = [r["role"] for r in result["role_progress"]["roles"]]
        assert role_names == [
            "project-owner-assistant", "domain-expert",
            "architect", "developer", "retrospective",
        ]

    @pytest.mark.asyncio
    async def test_complete_status_shows_10_roles(self):
        """Status for complete work item still shows 10 roles."""
        await golazo_create_workitem(
            work_item_id="CMP-010", profile="complete", work_items_dir=TEST_WORKITEMS_DIR
        )
        result = await golazo_status_tool(
            work_item_id="CMP-010", work_items_dir=TEST_WORKITEMS_DIR
        )
        assert result["active"] is True
        assert result["role_progress"]["roles_total"] == 10


# ── AC6: Backward transitions within profile sequence ────────────────


class TestBackwardTransitions:
    """AC6: Backward transitions within a profile's role sequence work correctly."""

    def test_express_backward_qa_to_poa(self):
        """Express: QA can go back to POA."""
        valid, err = validate_transition("quality-assurance", "project-owner-assistant", profile="express")
        assert valid is True

    def test_express_backward_dev_to_qa(self):
        """Express: Dev can go back to QA."""
        valid, err = validate_transition("developer", "quality-assurance", profile="express")
        assert valid is True

    def test_express_backward_retro_to_builder(self):
        """Express: Retro can go back to Builder."""
        valid, err = validate_transition("retrospective", "builder", profile="express")
        assert valid is True

    def test_spike_backward_architect_to_domain_expert(self):
        """Spike: Architect can go back to Domain-Expert."""
        valid, err = validate_transition("architect", "domain-expert", profile="spike")
        assert valid is True

    def test_spike_backward_dev_to_poa(self):
        """Spike: Dev can go back to POA (skip multiple backward)."""
        valid, err = validate_transition("developer", "project-owner-assistant", profile="spike")
        assert valid is True

    @pytest.mark.asyncio
    async def test_express_backward_at_runtime(self):
        """Express: backward transition works at runtime with state."""
        await golazo_create_workitem(
            work_item_id="EXP-020", profile="express", work_items_dir=TEST_WORKITEMS_DIR
        )
        # Advance to QA
        create_role_notes("EXP-020", "project-owner-assistant", TEST_WORKITEMS_DIR)
        result = await golazo_transition(
            work_item_id="EXP-020", role="quality-assurance", work_items_dir=TEST_WORKITEMS_DIR
        )
        assert result["success"]
        # Go back to POA
        create_role_notes("EXP-020", "quality-assurance", TEST_WORKITEMS_DIR)
        result = await golazo_transition(
            work_item_id="EXP-020", role="project-owner-assistant", work_items_dir=TEST_WORKITEMS_DIR
        )
        assert result["success"]
        assert result["current_role"] == "project-owner-assistant"


# ── Edge cases ───────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases for profile role-skipping."""

    def test_get_role_order_for_unknown_profile_falls_back(self):
        """Unknown profile falls back to full ROLE_ORDER."""
        roles = get_role_order_for_profile("nonexistent")
        assert roles == ROLE_ORDER

    def test_same_role_transition_always_allowed(self):
        """Same role → same role is always allowed regardless of profile."""
        for profile in ["complete", "express", "spike"]:
            valid, err = validate_transition("project-owner-assistant", "project-owner-assistant", profile=profile)
            assert valid is True

    def test_express_no_forward_skip(self):
        """Express: cannot skip from POA to Dev (must go POA → QA → Dev)."""
        valid, err = validate_transition("project-owner-assistant", "developer", profile="express")
        assert valid is False

    def test_spike_no_forward_skip(self):
        """Spike: cannot skip from POA to Architect (must go POA → Domain-Expert → Architect)."""
        valid, err = validate_transition("project-owner-assistant", "architect", profile="spike")
        assert valid is False
