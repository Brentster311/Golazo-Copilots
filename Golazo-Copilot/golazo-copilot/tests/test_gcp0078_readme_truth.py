"""README contract tests for GCP-0078."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.core.transitions import COMPLETE_PROFILE_ROLE_ORDER
from golazo_copilot.dispatch.registry import get_tool_definitions

README = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")


def test_readme_has_one_independent_persistence_feature():
    features = README.split("### Feature Details", maxsplit=1)[0]

    assert "**Persistent state tracking**" not in features
    assert features.lower().count("persistence") == 1
    assert README.count("#### Independent Workflow-State Persistence") == 1
    assert "#### Persistent State Tracking" not in README
    assert "does not isolate Git branches" in README


def test_readme_complete_profile_matches_registered_roles():
    assert len(COMPLETE_PROFILE_ROLE_ORDER) == 11
    assert "Full 11-role workflow + POA closure" in README
    assert "`4/11` in complete profile" in README
    assert "1. **Planner**" in README
    assert "New work items initialize at **Project Owner Assistant**" in README
    assert "`planner`, `project-owner-assistant`" in README


def test_readme_documents_every_registered_tool():
    discovery = README.split("### Step 5: Bootstrap", maxsplit=1)[0]
    reference = README.split("### Available MCP Tools", maxsplit=1)[1]

    for tool in get_tool_definitions():
        assert f"`{tool.name}`" in discovery, f"Discovery list omits {tool.name}"
        assert f"#### `{tool.name}`" in reference, f"Reference omits {tool.name}"


def test_readme_describes_supported_bypass_semantics():
    assert "Allows output-gate bypass via `golazo_consent` + `force=True`" in README
    assert "Role-note bypass is not exposed through the public MCP interface" in README
    assert "golazo_consent(action='skip_role')" not in README
    assert "Role notes enforcement** – Blocks transitions when role decision notes are missing" in README
    assert "missing (bypass with consent)" not in README
    assert "Force output-gate bypass" in README
    assert "Force transition even if gates not met" not in README


def test_readme_uses_configured_interpreter_installation():
    assert "same Python environment referenced by your VS Code MCP configuration" in README
    assert "global Python environment" not in README


def test_readme_states_operational_boundaries():
    assert "does not execute Git commands" in README
    assert "does not create the next work item" in README
    assert "Resume an existing work item by passing its `work_item_id`" in README
    assert "No MCP tool cancels or deletes a work item" in README