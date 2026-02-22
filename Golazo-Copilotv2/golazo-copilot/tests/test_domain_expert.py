"""Tests for GCP-0046: Domain Expert role addition.

Tests cover:
- Forward/backward transitions involving domain-expert
- Skip prevention (PM cannot skip to QA)
- Phase mapping
- ROLE_ORDER position
- VALID_ROLES membership
- Self-transition
- is_backward_transition checks
- Role file existence (3 copies)
- ROLE_ORDER count (10 roles)
"""

import os
import pytest

from golazo_copilot.core.transitions import (
    PHASE_MAP,
    ROLE_ORDER,
    TRANSITIONS,
    VALID_ROLES,
    get_phase_for_role,
    is_backward_transition,
    validate_transition,
)


class TestDomainExpertTransitions:
    """TC-1 through TC-6: Forward/backward/skip transitions."""

    def test_forward_pm_to_domain_expert(self):
        """TC-1: PM → domain-expert succeeds."""
        valid, err = validate_transition("program-manager", "domain-expert")
        assert valid is True
        assert err is None

    def test_forward_domain_expert_to_qa(self):
        """TC-2: domain-expert → QA succeeds."""
        valid, err = validate_transition("domain-expert", "quality-assurance")
        assert valid is True
        assert err is None

    def test_backward_domain_expert_to_pm(self):
        """TC-3: domain-expert → PM succeeds (backward)."""
        valid, err = validate_transition("domain-expert", "program-manager")
        assert valid is True
        assert err is None

    def test_backward_qa_to_domain_expert(self):
        """TC-4: QA → domain-expert succeeds (backward)."""
        valid, err = validate_transition("quality-assurance", "domain-expert")
        assert valid is True
        assert err is None

    def test_skip_pm_to_qa_blocked(self):
        """TC-5: PM cannot skip domain-expert to reach QA."""
        valid, err = validate_transition("program-manager", "quality-assurance")
        assert valid is False
        assert "Cannot transition" in err
        assert "domain-expert" in err

    def test_skip_domain_expert_to_architect_blocked(self):
        """TC-6: domain-expert cannot skip QA to reach architect."""
        valid, err = validate_transition("domain-expert", "architect")
        assert valid is False
        assert "Cannot transition" in err


class TestDomainExpertMetadata:
    """TC-7 through TC-10, TC-17: Phase, order, membership, self-transition, count."""

    def test_phase_is_definition(self):
        """TC-7: domain-expert is in the definition phase."""
        assert get_phase_for_role("domain-expert") == "definition"

    def test_role_order_position(self):
        """TC-8: domain-expert is at index 2 in ROLE_ORDER."""
        assert ROLE_ORDER.index("domain-expert") == 2
        assert ROLE_ORDER[1] == "program-manager"
        assert ROLE_ORDER[3] == "quality-assurance"

    def test_in_valid_roles(self):
        """TC-9: domain-expert is in VALID_ROLES."""
        assert "domain-expert" in VALID_ROLES

    def test_self_transition(self):
        """TC-10: domain-expert → domain-expert (self) succeeds."""
        valid, err = validate_transition("domain-expert", "domain-expert")
        assert valid is True
        assert err is None

    def test_role_order_count(self):
        """TC-17: ROLE_ORDER has exactly 10 entries."""
        assert len(ROLE_ORDER) == 10


class TestDomainExpertBackwardDetection:
    """TC-11, TC-12: is_backward_transition checks."""

    def test_domain_expert_to_pm_is_backward(self):
        """TC-11: domain-expert → PM is backward."""
        assert is_backward_transition("domain-expert", "program-manager") is True

    def test_pm_to_domain_expert_is_not_backward(self):
        """TC-12: PM → domain-expert is NOT backward (it's forward)."""
        assert is_backward_transition("program-manager", "domain-expert") is False


class TestDomainExpertRoleFiles:
    """TC-13 through TC-15: Role file existence in all 3 locations."""

    # 2 levels up from tests/ = golazo-copilot/ (package root)
    PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 3 levels up from tests/ = Golazo-Copilotv2/ (workspace root)
    WORKSPACE_ROOT = os.path.dirname(PACKAGE_ROOT)

    def test_source_default_exists(self):
        """TC-13: domain-expert.md exists in source defaults."""
        path = os.path.join(
            self.PACKAGE_ROOT, "src", "golazo_copilot", "roles", "defaults", "domain-expert.md"
        )
        assert os.path.isfile(path), f"Missing: {path}"
        content = open(path, encoding="utf-8").read()
        assert "# Role: Domain Expert" in content

    def test_deployed_github_exists(self):
        """TC-14: domain-expert.md exists in .github/roles/."""
        path = os.path.join(
            self.WORKSPACE_ROOT, ".github", "roles", "domain-expert.md"
        )
        assert os.path.isfile(path), f"Missing: {path}"
        content = open(path, encoding="utf-8").read()
        assert "# Role: Domain Expert" in content

    def test_package_github_exists(self):
        """TC-15: domain-expert.md exists in golazo-copilot/.github/roles/."""
        path = os.path.join(
            self.PACKAGE_ROOT, ".github", "roles", "domain-expert.md"
        )
        assert os.path.isfile(path), f"Missing: {path}"
        content = open(path, encoding="utf-8").read()
        assert "# Role: Domain Expert" in content
