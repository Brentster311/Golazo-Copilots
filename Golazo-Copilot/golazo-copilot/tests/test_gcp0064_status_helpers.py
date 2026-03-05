"""Focused tests for GCP-0064 status helper extraction."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.status_helpers import (
    apply_closure_completion_override,
    build_version_warning,
    unwrap_parallel_results,
)


class _State:
    def __init__(self, profile: str = "complete"):
        self.profile = profile


def test_unwrap_parallel_results_uses_safe_defaults_on_errors():
    """Error isolation keeps safe defaults for failed operations."""
    state = _State(profile="complete")

    result = unwrap_parallel_results(
        output_result=RuntimeError("validator failed"),
        missing_notes_result=["program-manager"],
        stale_files_result=RuntimeError("stale failed"),
        registry_result=RuntimeError("registry failed"),
        progress_result=RuntimeError("progress failed"),
        state=state,
    )

    assert result["outputs_complete"] is True
    assert result["required_outputs"] == []
    assert result["missing_notes"] == ["program-manager"]
    assert result["stale_files"] == []
    assert result["registry_hint"] is None
    assert result["role_progress"]["roles"] == []
    assert result["role_progress"]["roles_completed"] == 0


def test_apply_closure_completion_override_marks_po_complete():
    """Closure mode marks project-owner-assistant complete when outputs complete."""
    role_progress = {
        "roles": [
            {"role": "project-owner-assistant", "status": "in-progress"},
            {"role": "program-manager", "status": "pending"},
        ],
        "roles_completed": 0,
        "roles_total": 2,
    }

    result = apply_closure_completion_override(
        role_progress=role_progress,
        closure_mode=True,
        current_role="project-owner-assistant",
        outputs_complete=True,
    )

    assert result["roles_completed"] == 2
    po_entry = next(r for r in result["roles"] if r["role"] == "project-owner-assistant")
    assert po_entry["status"] == "completed"


def test_build_version_warning_formats_all_stale_files():
    """Version warning includes count and all file/version details."""
    warning = build_version_warning(
        [
            {"file": "a.md", "deployed": "1.0.0", "source": "2.0.0"},
            {"file": "b.md", "deployed": "1.1.0", "source": "2.1.0"},
        ]
    )

    assert warning is not None
    assert "2 file(s) are stale" in warning
    assert "a.md (v1.0.0 → v2.0.0)" in warning
    assert "b.md (v1.1.0 → v2.1.0)" in warning
    assert "golazo_bootstrap" in warning
