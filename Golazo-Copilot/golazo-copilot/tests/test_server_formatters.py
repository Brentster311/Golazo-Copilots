"""Tests for server.py pure formatting functions.

These test the abstraction boundary between tool results (dicts) and
the Markdown text returned to the MCP client.  No MCP infrastructure needed.
"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.server import (
    ICON_CHECK,
    ICON_EMPTY,
    ICON_FAIL,
    ICON_OK,
    ICON_PENDING,
    ICON_WARN,
    _runtime_tool_self_check,
    format_bootstrap_result,
    format_capabilities_result,
    format_consent_result,
    format_create_workitem_result,
    format_status_result,
    format_transition_result,
    resolve_work_items_dir,
)

# ── resolve_work_items_dir ──────────────────────────────────────────────

class TestResolveWorkItemsDir:

    def test_valid_path(self, tmp_path):
        result = resolve_work_items_dir(str(tmp_path))
        assert result == (tmp_path / "WorkItems").resolve()

    def test_none_raises(self):
        with pytest.raises(ValueError, match="workspace_path is required"):
            resolve_work_items_dir(None)

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="workspace_path is required"):
            resolve_work_items_dir("")


class TestToolSelfCheck:

    def test_runtime_self_check_has_no_missing_required_or_dispatch(self):
        warnings = asyncio.run(_runtime_tool_self_check())
        assert all("Missing required tool registration" not in w for w in warnings)
        assert all("missing dispatch branch" not in w for w in warnings)


# ── format_create_workitem_result ───────────────────────────────────────

class TestFormatCreateWorkitemResult:

    def test_success(self):
        result = {
            "success": True,
            "work_item_id": "GCP-001",
            "current_role": "project-owner-assistant",
            "role_instructions": "Do PO things.",
        }
        text = format_create_workitem_result(result)
        assert ICON_OK in text
        assert "GCP-001" in text
        assert "project-owner-assistant" in text
        assert "Do PO things." in text

    def test_failure(self):
        result = {"success": False, "error": "duplicate ID"}
        text = format_create_workitem_result(result)
        assert ICON_FAIL in text
        assert "duplicate ID" in text


# ── format_transition_result ────────────────────────────────────────────

class TestFormatTransitionResult:

    def test_success_no_warning(self):
        result = {
            "success": True,
            "current_role": "program-manager",
            "current_phase": "definition",
            "role_instructions": "PM instructions.",
        }
        text = format_transition_result(result)
        assert ICON_OK in text
        assert "program-manager" in text
        assert "definition" in text
        assert ICON_WARN not in text

    def test_success_with_warning(self):
        result = {
            "success": True,
            "current_role": "architect",
            "current_phase": "definition",
            "role_instructions": "...",
            "warning": "Backward transition!",
        }
        text = format_transition_result(result)
        assert ICON_WARN in text
        assert "Backward transition!" in text

    def test_failure(self):
        result = {"success": False, "error": "Cannot transition"}
        text = format_transition_result(result)
        assert ICON_FAIL in text
        assert "Cannot transition" in text


# ── format_status_result ────────────────────────────────────────────────

class TestFormatStatusResult:

    _ACTIVE_BASE = {
        "active": True,
        "version": "2.104.3",
        "work_item_id": "GCP-001",
        "current_role": "developer",
        "current_phase": "development",
        "next_steps": ["Write code", "Run tests"],
        "role_instructions": "Dev instructions.",
        "deviations": [],
    }

    def test_active_basic(self):
        text = format_status_result(self._ACTIVE_BASE)
        assert "**Golazo Status**" in text
        assert "GCP-001" in text
        assert "**developer**" in text
        assert "development" in text
        assert "Write code" in text
        assert "Dev instructions." in text

    def test_version_warning(self):
        result = {**self._ACTIVE_BASE, "version_warning": "Stale spine!"}
        text = format_status_result(result)
        assert ICON_WARN in text
        assert "Stale spine!" in text

    def test_role_progress(self):
        result = {
            **self._ACTIVE_BASE,
            "role_progress": {"roles_completed": 4, "roles_total": 9},
        }
        text = format_status_result(result)
        assert "4/9 complete" in text

    def test_required_outputs_complete(self):
        result = {
            **self._ACTIVE_BASE,
            "required_outputs": {
                "complete": True,
                "outputs": [
                    {"path": "WorkItems/GCP-001/story.md", "valid": True},
                ],
            },
        }
        text = format_status_result(result)
        assert f"{ICON_OK} Complete" in text
        assert ICON_CHECK in text
        assert "story.md" in text

    def test_required_outputs_incomplete(self):
        result = {
            **self._ACTIVE_BASE,
            "required_outputs": {
                "complete": False,
                "outputs": [
                    {"path": "story.md", "valid": True},
                    {"path": "design.md", "valid": False},
                ],
            },
        }
        text = format_status_result(result)
        assert f"{ICON_PENDING} 1/2" in text
        assert ICON_CHECK in text
        assert ICON_EMPTY in text

    def test_registry_hint(self):
        result = {**self._ACTIVE_BASE, "registry_hint": "12 capabilities registered"}
        text = format_status_result(result)
        assert "12 capabilities registered" in text

    def test_tooling_warnings(self):
        result = {
            **self._ACTIVE_BASE,
            "tooling_warnings": [
                "Missing required tool registration: golazo_update",
            ],
        }
        text = format_status_result(result)
        assert "Tooling self-check warnings" in text
        assert "golazo_update" in text

    def test_deviations(self):
        result = {
            **self._ACTIVE_BASE,
            "deviations": [
                {"id": "dev-1", "action": "skip_outputs", "reason": "spike", "consumed": False},
                {"id": "dev-2", "action": "skip_role", "reason": "done already", "consumed": True},
            ],
        }
        text = format_status_result(result)
        assert "**Deviations:**" in text
        assert "dev-1" in text
        assert "skip_outputs" in text
        assert "(consumed)" in text

    def test_inactive(self):
        result = {"active": False, "version": "2.104.3", "message": "No active work item 'X-001'."}
        text = format_status_result(result)
        assert ICON_WARN in text
        assert "2.104.3" in text
        assert "No active work item" in text

    def test_inactive_no_version(self):
        result = {"active": False, "message": "Not found"}
        text = format_status_result(result)
        assert "Not found" in text
        assert "(v" not in text


# ── format_bootstrap_result ─────────────────────────────────────────────

class TestFormatBootstrapResult:

    def test_success_with_files(self):
        result = {
            "success": True,
            "files_created": [
                ".github/agents/Golazo-Copilot.md",
                ".github/agents/golazo-copilot/roles/developer.md",
            ],
            "files_skipped": [".github/agents/golazo-copilot/roles/architect.md"],
            "message": "Bootstrap complete.",
        }
        text = format_bootstrap_result(result)
        assert ICON_OK in text
        assert "Golazo-Copilot.md" in text
        assert ICON_CHECK in text
        assert "architect.md" in text
        assert ICON_EMPTY in text
        assert "Bootstrap complete." in text

    def test_success_no_files(self):
        result = {
            "success": True,
            "files_created": [],
            "files_skipped": [],
            "message": "Nothing to do.",
        }
        text = format_bootstrap_result(result)
        assert "(none)" in text

    def test_failure_generic(self):
        result = {"success": False, "error": "Permission denied"}
        text = format_bootstrap_result(result)
        assert ICON_FAIL in text
        assert "Permission denied" in text

    def test_failure_no_workspace_markers(self):
        result = {"success": False, "error": "No workspace markers found in /tmp/bad"}
        text = format_bootstrap_result(result)
        assert "Next step" in text
        assert "golazo_bootstrap" in text


# ── format_consent_result ───────────────────────────────────────────────

class TestFormatConsentResult:

    def test_success(self):
        result = {
            "success": True,
            "deviation_id": "dev-abc",
            "action": "skip_outputs",
            "message": "Consent recorded by PO.",
        }
        text = format_consent_result(result)
        assert ICON_OK in text
        assert "dev-abc" in text
        assert "skip_outputs" in text
        assert "Consent recorded by PO." in text

    def test_failure(self):
        result = {"success": False, "error": "Reason too short"}
        text = format_consent_result(result)
        assert ICON_FAIL in text
        assert "Reason too short" in text


# ── format_capabilities_result ──────────────────────────────────────────

class TestFormatCapabilitiesResult:

    def test_error(self):
        result = {"success": False, "error": "File not found"}
        text = format_capabilities_result(result, "list")
        assert ICON_FAIL in text
        assert "File not found" in text

    def test_message_passthrough(self):
        result = {"success": True, "message": "Custom message"}
        text = format_capabilities_result(result, "list")
        assert text == "Custom message"

    def test_list_with_caps(self):
        result = {
            "success": True,
            "capabilities": [
                {"name": "auth", "description": "Authentication"},
                {"name": "billing", "description": "Billing engine"},
            ],
        }
        text = format_capabilities_result(result, "list")
        assert "2 capabilities" in text
        assert "**auth**" in text
        assert "**billing**" in text

    def test_list_empty(self):
        result = {"success": True, "capabilities": []}
        text = format_capabilities_result(result, "list")
        assert "empty" in text

    def test_show(self):
        result = {
            "success": True,
            "capability": {
                "name": "auth",
                "description": "Handles login",
                "key_files": ["src/auth.py"],
                "contracts": ["Must use OAuth2"],
                "depends_on": ["db"],
                "depended_on_by": ["api"],
            },
        }
        text = format_capabilities_result(result, "show")
        assert "**Capability: auth**" in text
        assert "src/auth.py" in text
        assert "OAuth2" in text
        assert "db" in text
        assert "api" in text

    def test_show_empty_collections(self):
        result = {
            "success": True,
            "capability": {
                "name": "bare",
                "description": "Bare cap",
                "key_files": [],
                "contracts": [],
                "depends_on": [],
                "depended_on_by": [],
            },
        }
        text = format_capabilities_result(result, "show")
        assert "(none)" in text

    def test_impact_direct_and_transitive(self):
        result = {
            "success": True,
            "directly_affected": [{"name": "a", "description": "Cap A"}],
            "transitively_affected": [{"name": "b", "description": "Cap B"}],
        }
        text = format_capabilities_result(result, "impact", files=["f1.py", "f2.py"])
        assert "2 files" in text
        assert "2 capabilities affected" in text
        assert "Directly Affected" in text
        assert "Transitively Affected" in text

    def test_impact_no_affected(self):
        result = {
            "success": True,
            "directly_affected": [],
            "transitively_affected": [],
        }
        text = format_capabilities_result(result, "impact", files=["x.py"])
        assert "No capabilities affected" in text

    def test_validate_all_valid(self):
        result = {
            "success": True,
            "results": [{"name": "cap1", "valid": True}],
        }
        text = format_capabilities_result(result, "validate")
        assert ICON_OK in text
        assert "all key_files exist" in text

    def test_validate_some_missing(self):
        result = {
            "success": True,
            "results": [{"name": "cap2", "valid": False, "missing_files": ["a.py", "b.py"]}],
        }
        text = format_capabilities_result(result, "validate")
        assert ICON_FAIL in text
        assert "a.py" in text

    def test_unknown_action_falls_through(self):
        result = {"success": True, "data": 42}
        text = format_capabilities_result(result, "unknown_action")
        assert "42" in text
