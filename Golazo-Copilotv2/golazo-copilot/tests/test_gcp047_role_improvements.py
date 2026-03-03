"""Tests for GCP-0047: SDLC Role Improvements — Fix Gaps and Reduce Redundancies.

Tests cover:
- Documenter: no build check (AC1)
- Developer: branch creation present (AC2)
- Builder: no branch creation section (AC2)
- Retrospective → POA transition (AC3)
- POA Closure section (AC3)
- QA: testability focus, no design-quality overlap (AC4)
- PM: governance sections (AC5)
- Architect: security review + design-quality bullets
- Domain Expert: boundary statement, no capability registry
- Capability registry consolidation
"""

import re
from importlib import resources

import pytest

from golazo_copilot.core.transitions import TRANSITIONS, ROLE_ORDER


def _read_role(role_name: str) -> str:
    """Read a role file from the package defaults."""
    role_files = resources.files("golazo_copilot.roles.defaults")
    return role_files.joinpath(f"{role_name}.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# AC1: Documenter — no build check
# ---------------------------------------------------------------------------
class TestDocumenterNoBuildCheck:
    """TC-1: Documenter role file should not reference build verification."""

    def test_no_build_in_first_action(self):
        content = _read_role("documenter")
        # Extract First Action section
        first_action = re.search(r"## First action\n(.*?)(?=\n## )", content, re.DOTALL)
        assert first_action, "Documenter missing First Action section"
        assert "build" not in first_action.group(1).lower(), \
            "Documenter First Action should not reference build verification"

    def test_no_build_in_entry_conditions(self):
        content = _read_role("documenter")
        entry = re.search(r"## Entry conditions\n(.*?)(?=\n## )", content, re.DOTALL)
        assert entry, "Documenter missing Entry Conditions section"
        assert "build" not in entry.group(1).lower(), \
            "Documenter Entry Conditions should not reference build"

    def test_no_implemented_status_responsibility(self):
        """TC-17: Documenter should not assign IMPLEMENTED status (moved to POA Closure)."""
        content = _read_role("documenter")
        resp = re.search(r"## Responsibilities\n(.*?)(?=\n## )", content, re.DOTALL)
        assert resp, "Documenter missing Responsibilities section"
        assert "implemented" not in resp.group(1).lower(), \
            "Documenter should not handle IMPLEMENTED status (moved to POA Closure)"


# ---------------------------------------------------------------------------
# AC2: Developer — branch creation; Builder — no branch creation
# ---------------------------------------------------------------------------
class TestDeveloperBranchCreation:
    """TC-2: Developer role file should include branch creation in First Action."""

    def test_developer_has_branch_creation(self):
        content = _read_role("developer")
        first_action = re.search(r"## First action\n(.*?)(?=\n## )", content, re.DOTALL)
        assert first_action, "Developer missing First Action section"
        text = first_action.group(1).lower()
        assert "branch" in text or "git checkout" in text, \
            "Developer First Action should include branch creation"

    def test_developer_branch_creation_uses_alias_and_workitem(self):
        """TC-2b: Developer branch command uses <useralias>/<workitem-id> format."""
        content = _read_role("developer")
        first_action = re.search(r"## First action\n(.*?)(?=\n## )", content, re.DOTALL)
        assert first_action, "Developer missing First Action section"

        text = first_action.group(1)
        assert "git checkout -b <useralias>/<workitem-id>" in text, (
            "Developer First Action must require branch format <useralias>/<workitem-id>"
        )

    def test_developer_branch_creation_rejects_legacy_workitem_only_pattern(self):
        """TC-2c: Developer branch command must not use legacy <workitem-id>-only format."""
        content = _read_role("developer")
        first_action = re.search(r"## First action\n(.*?)(?=\n## )", content, re.DOTALL)
        assert first_action, "Developer missing First Action section"

        text = first_action.group(1)
        assert "git checkout -b <workitem-id>" not in text, (
            "Developer First Action must not allow legacy <workitem-id>-only branch format"
        )


class TestBuilderNoBranchCreation:
    """TC-3: Builder role file should not contain branch creation instructions."""

    def test_no_before_developer_section(self):
        content = _read_role("builder")
        assert "before developer" not in content.lower(), \
            "Builder should not contain 'Before Developer role' section"

    def test_no_branch_creation_in_responsibilities(self):
        content = _read_role("builder")
        resp = re.search(r"## Responsibilities\n(.*?)(?=\n## Forbidden)", content, re.DOTALL)
        assert resp, "Builder missing Responsibilities section"
        assert "git checkout -b" not in resp.group(1), \
            "Builder should not contain branch creation command"


# ---------------------------------------------------------------------------
# AC3: Retrospective → POA transition + POA Closure section
# ---------------------------------------------------------------------------
class TestRetrospectiveToPOATransition:
    """TC-4: transitions.py allows retrospective → project-owner-assistant."""

    def test_transition_exists(self):
        retro_targets = TRANSITIONS.get("retrospective", [])
        assert "project-owner-assistant" in retro_targets, \
            "TRANSITIONS['retrospective'] must include 'project-owner-assistant'"


class TestPOAClosureSection:
    """TC-5/6/7: POA role file contains a Closure section with required content."""

    def test_closure_section_exists(self):
        content = _read_role("project-owner-assistant")
        assert "## Closure" in content, \
            "POA role file must contain a '## Closure' section"

    def test_closure_has_ac_validation(self):
        content = _read_role("project-owner-assistant")
        closure = re.search(r"## Closure\n(.*)", content, re.DOTALL)
        assert closure, "POA missing Closure section"
        text = closure.group(1).lower()
        assert "acceptance criteria" in text, \
            "POA Closure must reference acceptance criteria validation"

    def test_closure_has_pending_work_items(self):
        content = _read_role("project-owner-assistant")
        closure = re.search(r"## Closure\n(.*)", content, re.DOTALL)
        assert closure, "POA missing Closure section"
        text = closure.group(1).lower()
        assert "pending" in text or "future work" in text or "new work item" in text, \
            "POA Closure must reference collecting pending/future work items"

    def test_closure_has_final_commit(self):
        content = _read_role("project-owner-assistant")
        closure = re.search(r"## Closure\n(.*)", content, re.DOTALL)
        assert closure, "POA missing Closure section"
        text = closure.group(1).lower()
        assert "commit" in text, \
            "POA Closure must reference final git commit"

    def test_closure_is_terminal(self):
        """TC-6: POA Closure must instruct not to transition further."""
        content = _read_role("project-owner-assistant")
        closure = re.search(r"## Closure\n(.*)", content, re.DOTALL)
        assert closure, "POA missing Closure section"
        text = closure.group(1).lower()
        assert "do not transition" in text or "final role" in text or "end of the workflow" in text, \
            "POA Closure must explicitly state this is the end of the workflow"

    def test_closure_updates_user_story(self):
        """TC-7: POA Closure should update the User Story (not create a separate closure doc)."""
        content = _read_role("project-owner-assistant")
        closure = re.search(r"## Closure\n(.*)", content, re.DOTALL)
        assert closure, "POA missing Closure section"
        text = closure.group(1).lower()
        assert "update user story" in text or "user-story" in text, \
            "POA Closure must instruct to update the User Story with closure info"


# ---------------------------------------------------------------------------
# AC4: QA — testability focus, no design-quality overlap
# ---------------------------------------------------------------------------
class TestQATestabilityFocus:
    """TC-8: QA should not contain design-quality bullets that belong to Architect."""

    REMOVED_PHRASES = [
        "risk coverage",
        "operability",
        "on-call impact",
        "cost / performance",
        "cost/performance",
        "naming clarity",
        "folder/directory structure",
        "folder structure",
    ]

    @pytest.mark.parametrize("phrase", REMOVED_PHRASES)
    def test_qa_does_not_contain_design_quality_phrase(self, phrase):
        content = _read_role("quality-assurance")
        design_review = re.search(r"### Design Review\n(.*?)(?=\n### |\n## )", content, re.DOTALL)
        if design_review:
            assert phrase not in design_review.group(1).lower(), \
                f"QA Design Review should not contain '{phrase}' (moved to Architect)"

    def test_qa_no_capability_registry(self):
        """TC-14: QA should not contain golazo_capabilities instructions."""
        content = _read_role("quality-assurance")
        assert "golazo_capabilities" not in content, \
            "QA should not contain golazo_capabilities (consolidated to Architect)"


class TestArchitectDesignQuality:
    """TC-9: Architect should contain design-quality bullets moved from QA."""

    def test_architect_has_risk_or_operability(self):
        content = _read_role("architect")
        text = content.lower()
        assert "risk" in text or "operability" in text, \
            "Architect should contain risk/operability bullets from QA"

    def test_architect_has_naming_or_structure(self):
        content = _read_role("architect")
        text = content.lower()
        assert "naming" in text or "folder" in text or "structure" in text, \
            "Architect should contain naming/structure bullets from QA"


# ---------------------------------------------------------------------------
# AC5: PM — governance sections
# ---------------------------------------------------------------------------
class TestPMGovernanceSections:
    """TC-10: PM must have Decision rules, Escalation rules, Success criteria."""

    def test_pm_has_decision_rules(self):
        content = _read_role("program-manager")
        assert "## Decision rules" in content, \
            "PM missing '## Decision rules' section"

    def test_pm_has_escalation_rules(self):
        content = _read_role("program-manager")
        assert "## Escalation rules" in content, \
            "PM missing '## Escalation rules' section"

    def test_pm_has_success_criteria(self):
        content = _read_role("program-manager")
        assert "## Success criteria" in content, \
            "PM missing '## Success criteria' section"


# ---------------------------------------------------------------------------
# Architect — Security Review
# ---------------------------------------------------------------------------
class TestArchitectSecurityReview:
    """TC-11: Architect should contain a Security Review checklist."""

    def test_security_review_section(self):
        content = _read_role("architect")
        assert "security review" in content.lower(), \
            "Architect must contain a 'Security Review' section"

    def test_security_checklist_items(self):
        content = _read_role("architect").lower()
        assert "data exposure" in content, "Architect security checklist missing 'data exposure'"
        assert "auth" in content, "Architect security checklist missing auth reference"
        assert "attack surface" in content, "Architect security checklist missing 'attack surface'"


# ---------------------------------------------------------------------------
# Domain Expert — boundary + no capability registry
# ---------------------------------------------------------------------------
class TestDomainExpertBoundary:
    """TC-12/13: Domain Expert boundary statement and no capability registry."""

    def test_boundary_statement(self):
        content = _read_role("domain-expert").lower()
        # Must contain a statement distinguishing domain from architectural
        has_boundary = (
            ("structural" in content and "architectural" in content and "not" in content)
            or "scope boundary" in content
        )
        assert has_boundary, \
            "Domain Expert must contain boundary distinguishing domain knowledge from architectural decisions"

    def test_no_capability_registry(self):
        """TC-13: Domain Expert should not contain golazo_capabilities."""
        content = _read_role("domain-expert")
        assert "golazo_capabilities" not in content, \
            "Domain Expert should not contain golazo_capabilities (consolidated to Architect)"
