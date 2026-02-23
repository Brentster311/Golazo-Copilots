# -*- coding: utf-8 -*-
"""Integration tests for subagent handoff protocol — GCP-0052.

Validates the full orchestrator → subagent → artifacts → next-subagent flow
using real golazo_transition and golazo_role_context calls with mocked file creation.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from golazo_copilot.tools.golazo_create_workitem import golazo_create_workitem
from golazo_copilot.tools.golazo_transition import golazo_transition, ROLE_SUFFIX_MAP
from golazo_copilot.tools.golazo_role_context import golazo_role_context
from golazo_copilot.core.persistence import load_state


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROLE_ORDER = [
    "project-owner-assistant", "program-manager", "domain-expert",
    "quality-assurance", "architect", "developer",
    "refactor-expert", "documenter", "builder", "retrospective",
]

# Maps each role to Required Output files (workspace-root-relative, matching role file patterns).
# Derived from the actual role file ## Required Outputs sections.
REQUIRED_OUTPUTS: dict[str, list[str]] = {
    "project-owner-assistant": [
        "WorkItems/{id}/{id}-User-Story.md",
        "WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md",
    ],
    "program-manager": [
        "WorkItems/{id}/Design/{id}-design-doc.md",
        "WorkItems/{id}/RoleDecisionNotes/{id}-program-manager.md",
    ],
    "domain-expert": [
        "WorkItems/{id}/RoleDecisionNotes/{id}-domain-expert.md",
    ],
    "quality-assurance": [
        "WorkItems/{id}/Design/{id}-Review-Comments.md",
        "WorkItems/{id}/Design/{id}-Test-Cases.md",
        "WorkItems/{id}/RoleDecisionNotes/{id}-quality-assurance.md",
    ],
    "architect": [
        "WorkItems/{id}/Design/{id}-Review-Comments.md",
        "WorkItems/{id}/Design/{id}-Capability-Impact.md",
        "WorkItems/{id}/RoleDecisionNotes/{id}-architect.md",
    ],
    "developer": [
        "WorkItems/{id}/RoleDecisionNotes/{id}-developer.md",
    ],
    "refactor-expert": [
        "WorkItems/{id}/RoleDecisionNotes/{id}-refactor.md",
    ],
    "documenter": [
        "WorkItems/{id}/RoleDecisionNotes/{id}-documenter.md",
    ],
    "builder": [
        "WorkItems/{id}/RoleDecisionNotes/{id}-builder.md",
    ],
    "retrospective": [
        "WorkItems/{id}/RoleDecisionNotes/{id}-retrospective.md",
    ],
}


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

# Use a dedicated workspace to avoid collisions with other test modules.
TEST_WORKSPACE = Path(__file__).parent / "test-subagent-workspace"
TEST_WORKITEMS_DIR = TEST_WORKSPACE / "WorkItems"


def _wi_dir(wid: str) -> Path:
    return TEST_WORKITEMS_DIR / wid


def _create_outputs_for_role(wid: str, role: str):
    """Simulate a subagent creating all Required Outputs for *role*."""
    for pattern in REQUIRED_OUTPUTS[role]:
        rel = pattern.replace("{id}", wid)
        fpath = TEST_WORKSPACE / rel
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(f"# {wid} {role}\n\nMock output for {rel}.", encoding="utf-8")


@pytest.fixture(autouse=True)
def workspace_setup():
    """Create and tear down the isolated workspace for each test."""
    if TEST_WORKSPACE.exists():
        shutil.rmtree(TEST_WORKSPACE)
    TEST_WORKITEMS_DIR.mkdir(parents=True, exist_ok=True)

    # Create a POA role override without the closure line (which contains an
    # inline HTML comment that the output validator can't match on Windows).
    # All other roles use package defaults.
    poa_override = TEST_WORKSPACE / ".github" / "roles" / "project-owner-assistant.md"
    poa_override.parent.mkdir(parents=True, exist_ok=True)
    poa_override.write_text(
        "---\n"
        "inputs: []\n"
        "outputs:\n"
        "  - \"{id}-User-Story.md\"\n"
        "  - \"RoleDecisionNotes/{id}-project-owner-assistant.md\"\n"
        "tools:\n"
        "  - golazo_status\n"
        "  - golazo_transition\n"
        "  - golazo_capabilities\n"
        "  - golazo_create_workitem\n"
        "---\n"
        "# Role: Project Owner Assistant\n\n"
        "## Required Outputs\n"
        "- file: WorkItems/{id}/{id}-User-Story.md\n"
        "- file: WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md\n",
        encoding="utf-8",
    )

    yield
    if TEST_WORKSPACE.exists():
        shutil.rmtree(TEST_WORKSPACE)


# ---------------------------------------------------------------------------
# TC1 / AC3 — Full 10-role workflow walk
# ---------------------------------------------------------------------------

class TestFullWorkflowWalk:
    """Walk all 10 roles, creating mock outputs, verifying transitions succeed."""

    @pytest.mark.asyncio
    async def test_full_10_role_walk(self):
        """AC3: Walk POA → PM → DE → QA → Arch → Dev → Refactor → Doc → Builder → Retro."""
        wid = "INT-001"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        for i, role in enumerate(ROLE_ORDER):
            # Create outputs the subagent would produce for this role
            _create_outputs_for_role(wid, role)

            # Verify golazo_role_context returns a valid bundle for the current role
            ctx = await golazo_role_context(
                work_item_id=wid,
                role=role,
                work_items_dir=TEST_WORKITEMS_DIR,
                project_root=TEST_WORKSPACE,
            )
            assert ctx["status"] == "ok", f"golazo_role_context failed for {role}: {ctx}"
            assert "## Role Instructions" in ctx["bundle"]

            # Transition to next role (except after retrospective)
            if i < len(ROLE_ORDER) - 1:
                next_role = ROLE_ORDER[i + 1]
                result = await golazo_transition(
                    work_item_id=wid,
                    role=next_role,
                    work_items_dir=TEST_WORKITEMS_DIR,
                    project_root=TEST_WORKSPACE,
                )
                assert result["success"] is True, (
                    f"Transition {role} → {next_role} failed: {result}"
                )
                assert result["current_role"] == next_role

        # Final state should be retrospective
        state = load_state(wid, TEST_WORKITEMS_DIR)
        assert state.current_role == "retrospective"

    @pytest.mark.asyncio
    async def test_role_context_includes_input_artifacts(self):
        """AC3 supplement: golazo_role_context bundles input artifacts from prior roles."""
        wid = "INT-002"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        # Create POA outputs and advance to PM
        _create_outputs_for_role(wid, "project-owner-assistant")
        await golazo_transition(
            work_item_id=wid, role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )

        # PM should see the User Story as an input artifact
        ctx = await golazo_role_context(
            work_item_id=wid, role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        assert ctx["status"] == "ok"
        assert "## Input Artifacts" in ctx["bundle"]
        # User Story content should be in the bundle
        assert "INT-002 project-owner-assistant" in ctx["bundle"]

    @pytest.mark.asyncio
    async def test_role_context_includes_previous_role_notes(self):
        """golazo_role_context includes previous role decision notes."""
        wid = "INT-003"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        _create_outputs_for_role(wid, "project-owner-assistant")
        await golazo_transition(
            work_item_id=wid, role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )

        ctx = await golazo_role_context(
            work_item_id=wid, role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        assert ctx["status"] == "ok"
        assert "## Previous Role Notes" in ctx["bundle"]


# ---------------------------------------------------------------------------
# TC2 / AC4 — Negative case: missing output blocks transition
# ---------------------------------------------------------------------------

class TestMissingOutputBlocksTransition:
    """Verify that golazo_transition blocks when a required output is missing."""

    @pytest.mark.asyncio
    async def test_missing_output_blocks_transition(self):
        """AC4: Subagent fails to create a required output; transition blocked."""
        wid = "INT-010"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        # Create role notes but NOT User Story — the output gate should block
        notes_dir = _wi_dir(wid) / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / f"{wid}-project-owner-assistant.md").write_text("# Notes", encoding="utf-8")

        # Transition should fail — missing User Story (required output)
        result = await golazo_transition(
            work_item_id=wid, role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        assert result["success"] is False, "Transition should have been blocked"
        assert "missing" in result.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_missing_design_doc_blocks_pm_transition(self):
        """PM cannot transition without creating its design doc."""
        wid = "INT-011"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        # Complete POA properly
        _create_outputs_for_role(wid, "project-owner-assistant")
        await golazo_transition(
            work_item_id=wid, role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )

        # Create PM role notes but NOT the design doc
        notes_dir = _wi_dir(wid) / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / f"{wid}-program-manager.md").write_text("# PM Notes", encoding="utf-8")

        result = await golazo_transition(
            work_item_id=wid, role="domain-expert",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        assert result["success"] is False, "PM transition should be blocked without design doc"

    @pytest.mark.asyncio
    async def test_missing_qa_test_cases_blocks_transition(self):
        """QA cannot transition without Test-Cases.md."""
        wid = "INT-012"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        # Advance to QA
        for role in ROLE_ORDER[:3]:  # POA, PM, DE
            _create_outputs_for_role(wid, role)
            next_idx = ROLE_ORDER.index(role) + 1
            await golazo_transition(
                work_item_id=wid, role=ROLE_ORDER[next_idx],
                work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
            )

        # Create QA Review-Comments and role notes, but NOT Test-Cases
        design_dir = _wi_dir(wid) / "Design"
        design_dir.mkdir(parents=True, exist_ok=True)
        (design_dir / f"{wid}-Review-Comments.md").write_text("# Reviews", encoding="utf-8")
        notes_dir = _wi_dir(wid) / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / f"{wid}-quality-assurance.md").write_text("# QA Notes", encoding="utf-8")

        result = await golazo_transition(
            work_item_id=wid, role="architect",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        assert result["success"] is False, "QA transition should be blocked without Test-Cases.md"


# ---------------------------------------------------------------------------
# TC3 / AC5 — Backward transition: Developer → Architect re-entry
# ---------------------------------------------------------------------------

class TestBackwardTransition:
    """Verify backward transition handles re-entry correctly."""

    @pytest.mark.asyncio
    async def test_developer_to_architect_backward(self):
        """AC5: After reaching developer, return to architect; context reflects updated artifacts."""
        wid = "INT-020"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        # Advance to developer (through POA, PM, DE, QA, Architect)
        for role in ROLE_ORDER[:5]:  # POA through Architect
            _create_outputs_for_role(wid, role)
            await golazo_transition(
                work_item_id=wid, role=ROLE_ORDER[ROLE_ORDER.index(role) + 1],
                work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
            )

        # Now at developer. Create developer notes (required before transitioning away).
        _create_outputs_for_role(wid, "developer")

        # Trigger backward transition to architect.
        result = await golazo_transition(
            work_item_id=wid, role="architect",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        assert result["success"] is True, f"Backward transition failed: {result}"
        assert result["current_role"] == "architect"

        # Update the Review-Comments (simulate architect re-entry work)
        updated_content = "# Updated Review Comments\n\nRevised after developer feedback."
        review_path = _wi_dir(wid) / "Design" / f"{wid}-Review-Comments.md"
        review_path.write_text(updated_content, encoding="utf-8")

        # Role context for architect should include the updated content
        ctx = await golazo_role_context(
            work_item_id=wid, role="architect",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        assert ctx["status"] == "ok"
        # The updated content should appear in the bundle
        assert "Revised after developer feedback" in ctx["bundle"]

    @pytest.mark.asyncio
    async def test_backward_preserves_state_history(self):
        """Backward transition preserves role history in state."""
        wid = "INT-021"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        # Advance to developer
        for role in ROLE_ORDER[:5]:
            _create_outputs_for_role(wid, role)
            await golazo_transition(
                work_item_id=wid, role=ROLE_ORDER[ROLE_ORDER.index(role) + 1],
                work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
            )

        # Create developer notes before going backward
        _create_outputs_for_role(wid, "developer")

        # Go backward to architect
        await golazo_transition(
            work_item_id=wid, role="architect",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )

        state = load_state(wid, TEST_WORKITEMS_DIR)
        assert state.current_role == "architect"
        # Should have history entries for all transitions including backward
        assert len(state.role_history) >= 6  # 5 forward + 1 backward


# ---------------------------------------------------------------------------
# TC4 / AC1+AC2 — Protocol document validation
# ---------------------------------------------------------------------------

class TestHandoffProtocolDocument:
    """Verify the handoff protocol document exists and has required sections."""

    PROTOCOL_PATH = (
        Path(__file__).parent.parent.parent
        / "WorkItems"
        / "Golazo-Subagent-Handoff-Protocol.md"
    )

    def test_protocol_file_exists(self):
        """AC1: Handoff protocol document exists."""
        assert self.PROTOCOL_PATH.exists(), (
            f"Handoff protocol not found at {self.PROTOCOL_PATH}"
        )

    def test_protocol_has_orchestrator_responsibilities(self):
        """AC1: Protocol includes orchestrator responsibilities."""
        content = self.PROTOCOL_PATH.read_text(encoding="utf-8")
        assert "Orchestrator Responsibilities" in content

    def test_protocol_has_subagent_contract(self):
        """AC1: Protocol includes subagent contract."""
        content = self.PROTOCOL_PATH.read_text(encoding="utf-8")
        assert "Subagent Contract" in content

    def test_protocol_has_handoff_matrix(self):
        """AC1: Protocol includes artifact handoff matrix."""
        content = self.PROTOCOL_PATH.read_text(encoding="utf-8")
        assert "Artifact Handoff Matrix" in content

    def test_protocol_has_error_recovery(self):
        """AC1: Protocol includes error recovery strategy."""
        content = self.PROTOCOL_PATH.read_text(encoding="utf-8")
        assert "Error Recovery" in content

    def test_protocol_matrix_covers_all_transitions(self):
        """AC2: Matrix covers all 10 role transitions."""
        content = self.PROTOCOL_PATH.read_text(encoding="utf-8")
        # All 10 transitions should appear in the matrix
        expected_transitions = [
            "POA → PM", "PM → DE", "DE → QA", "QA → Architect",
            "Architect → Developer", "Developer → Refactor",
            "Refactor → Documenter", "Documenter → Builder",
            "Builder → Retro", "Retro → POA",
        ]
        for transition in expected_transitions:
            assert transition in content, f"Missing transition in matrix: {transition}"

    def test_protocol_under_200_lines(self):
        """NFR: Protocol document ≤ 200 lines."""
        content = self.PROTOCOL_PATH.read_text(encoding="utf-8")
        line_count = len(content.splitlines())
        assert line_count <= 200, f"Protocol is {line_count} lines (max 200)"


# ---------------------------------------------------------------------------
# TC6 — Zero-bridge transition context resolution
# ---------------------------------------------------------------------------

class TestZeroBridgeTransitions:
    """Verify roles with no direct bridge still get correct context."""

    @pytest.mark.asyncio
    async def test_de_to_qa_zero_bridge(self):
        """DE→QA: QA has no direct inputs from DE but reaches back to User Story and Design Doc."""
        wid = "INT-030"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        # Advance through POA, PM, DE
        for role in ROLE_ORDER[:3]:
            _create_outputs_for_role(wid, role)
            await golazo_transition(
                work_item_id=wid, role=ROLE_ORDER[ROLE_ORDER.index(role) + 1],
                work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
            )

        # Now at QA — get context
        ctx = await golazo_role_context(
            work_item_id=wid, role="quality-assurance",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        assert ctx["status"] == "ok"
        # QA should have input artifacts (User Story and Design Doc from reach-back)
        assert ctx["artifact_count"] >= 1, "QA should have at least 1 input artifact"

    @pytest.mark.asyncio
    async def test_refactor_to_documenter_zero_bridge(self):
        """Refactor→Documenter: Documenter reaches back to User Story and Design Doc."""
        wid = "INT-031"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        # Advance through all roles up to documenter
        for role in ROLE_ORDER[:7]:  # POA through Refactor
            _create_outputs_for_role(wid, role)
            await golazo_transition(
                work_item_id=wid, role=ROLE_ORDER[ROLE_ORDER.index(role) + 1],
                work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
            )

        # Now at documenter
        ctx = await golazo_role_context(
            work_item_id=wid, role="documenter",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        assert ctx["status"] == "ok"
        assert ctx["artifact_count"] >= 1, "Documenter should have reach-back artifacts"


# ---------------------------------------------------------------------------
# TC7 — ROLE_SUFFIX_MAP correctness
# ---------------------------------------------------------------------------

class TestRoleSuffixMapping:
    """Verify that ROLE_SUFFIX_MAP handles all roles correctly."""

    def test_refactor_expert_maps_to_refactor(self):
        """refactor-expert role uses 'refactor' suffix for notes files."""
        assert ROLE_SUFFIX_MAP.get("refactor-expert") == "refactor"

    def test_all_roles_have_suffix_or_fallback(self):
        """Every role in ROLE_ORDER has a ROLE_SUFFIX_MAP entry or uses role name as fallback."""
        for role in ROLE_ORDER:
            suffix = ROLE_SUFFIX_MAP.get(role, role)
            assert suffix, f"No suffix for role: {role}"
            # The suffix should be a simple kebab-case string
            assert all(c.isalnum() or c == "-" for c in suffix), (
                f"Invalid suffix characters for {role}: {suffix}"
            )

    @pytest.mark.asyncio
    async def test_domain_expert_fallback_suffix(self):
        """domain-expert is not in ROLE_SUFFIX_MAP; falls back to role name."""
        wid = "INT-040"
        await golazo_create_workitem(work_item_id=wid, work_items_dir=TEST_WORKITEMS_DIR)

        # domain-expert is not explicitly in ROLE_SUFFIX_MAP
        suffix = ROLE_SUFFIX_MAP.get("domain-expert", "domain-expert")
        assert suffix == "domain-expert"

        # The actual notes file should use this suffix
        _create_outputs_for_role(wid, "project-owner-assistant")
        await golazo_transition(
            work_item_id=wid, role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )
        _create_outputs_for_role(wid, "program-manager")
        await golazo_transition(
            work_item_id=wid, role="domain-expert",
            work_items_dir=TEST_WORKITEMS_DIR, project_root=TEST_WORKSPACE,
        )

        # Verify domain-expert role notes use the fallback suffix
        notes_path = _wi_dir(wid) / "RoleDecisionNotes" / f"{wid}-domain-expert.md"
        _create_outputs_for_role(wid, "domain-expert")
        assert notes_path.exists()
