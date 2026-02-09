"""Integration tests for output validation in transitions - GCP-0025."""

import shutil
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from golazo_copilot.tools.gcp_create_workitem import gcp_create_workitem
from golazo_copilot.tools.gcp_transition import gcp_transition
from golazo_copilot.tools.gcp_status import gcp_status
from golazo_copilot.tools.gcp_consent import gcp_consent


# Use a workspace structure that mirrors real use: workspace/WorkItems
TEST_WORKSPACE = Path(__file__).parent / "test-workspace"
TEST_WORKITEMS_DIR = TEST_WORKSPACE / "WorkItems"


def create_role_file(workspace_root: Path, role: str, content: str):
    """Create a role file in .github/roles/"""
    role_path = workspace_root / ".github" / "roles" / f"{role}.md"
    role_path.parent.mkdir(parents=True, exist_ok=True)
    role_path.write_text(content, encoding="utf-8")


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    if TEST_WORKSPACE.exists():
        shutil.rmtree(TEST_WORKSPACE)
    TEST_WORKITEMS_DIR.mkdir(parents=True, exist_ok=True)
    yield
    if TEST_WORKSPACE.exists():
        shutil.rmtree(TEST_WORKSPACE)


class TestTransitionOutputValidation:
    """TC5: Transition validates outputs."""

    @pytest.mark.asyncio
    async def test_transition_succeeds_when_all_outputs_exist(self):
        """TC5.1: Allow transition when all required outputs exist."""
        # Create role file with required output
        create_role_file(TEST_WORKSPACE, "project-owner-assistant", """
# Role: Project Owner Assistant

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
""")
        
        # Create work item
        await gcp_create_workitem(work_item_id="OUT-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create the required output file
        user_story = TEST_WORKITEMS_DIR / "OUT-001" / "OUT-001-User-Story.md"
        user_story.write_text("# User Story", encoding="utf-8")
        
        # Create role notes (also required)
        notes_dir = TEST_WORKITEMS_DIR / "OUT-001" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "OUT-001-project-owner-assistant.md").write_text("# Notes", encoding="utf-8")
        
        # Transition should succeed
        result = await gcp_transition(
            work_item_id="OUT-001",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )
        
        assert result["success"] is True, f"Expected success but got: {result}"
        assert result["current_role"] == "program-manager"

    @pytest.mark.asyncio
    async def test_transition_blocked_when_output_missing(self):
        """TC5.2: Block transition with clear error when output missing."""
        # Create role file with required output
        create_role_file(TEST_WORKSPACE, "project-owner-assistant", """
# Role: Project Owner Assistant

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
""")
        
        # Create work item
        await gcp_create_workitem(work_item_id="OUT-002", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create role notes but NOT the user story
        notes_dir = TEST_WORKITEMS_DIR / "OUT-002" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "OUT-002-project-owner-assistant.md").write_text("# Notes", encoding="utf-8")
        
        # Transition should fail
        result = await gcp_transition(
            work_item_id="OUT-002",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )
        
        assert result["success"] is False
        assert "missing" in result["error"].lower() or "User-Story" in result.get("missing_outputs", [""])[0]

    @pytest.mark.asyncio
    async def test_transition_force_with_consent(self):
        """TC5.3: Allow force transition when consent recorded."""
        # Create role file with required output
        create_role_file(TEST_WORKSPACE, "project-owner-assistant", """
# Role: Project Owner Assistant

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
""")
        
        # Create work item
        await gcp_create_workitem(work_item_id="OUT-003", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create role notes but NOT the user story
        notes_dir = TEST_WORKITEMS_DIR / "OUT-003" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "OUT-003-project-owner-assistant.md").write_text("# Notes", encoding="utf-8")
        
        # Record consent
        await gcp_consent(
            work_item_id="OUT-003",
            action="skip_outputs",
            reason="Testing force transition with consent",
            work_items_dir=TEST_WORKITEMS_DIR,
        )
        
        # Force transition should succeed
        result = await gcp_transition(
            work_item_id="OUT-003",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
            force=True,
        )
        
        assert result["success"] is True, f"Expected success but got: {result}"

    @pytest.mark.asyncio
    async def test_transition_force_without_consent_fails(self):
        """TC5.4: Block force transition when no consent."""
        # Create role file with required output
        create_role_file(TEST_WORKSPACE, "project-owner-assistant", """
# Role: Project Owner Assistant

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
""")
        
        # Create work item
        await gcp_create_workitem(work_item_id="OUT-004", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create role notes but NOT the user story
        notes_dir = TEST_WORKITEMS_DIR / "OUT-004" / "RoleDecisionNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / "OUT-004-project-owner-assistant.md").write_text("# Notes", encoding="utf-8")
        
        # Force transition without consent should fail
        result = await gcp_transition(
            work_item_id="OUT-004",
            role="program-manager",
            work_items_dir=TEST_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
            force=True,
        )
        
        assert result["success"] is False
        assert "consent" in result["error"].lower()


class TestStatusOutputValidation:
    """TC6: Status shows output validation."""

    @pytest.mark.asyncio
    async def test_status_includes_outputs(self):
        """TC6.1: Status response includes required outputs for current role."""
        # Create role file with required outputs
        create_role_file(TEST_WORKSPACE, "project-owner-assistant", """
# Role: Project Owner Assistant

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- dir: WorkItems/{id}/Design
""")
        
        # Create work item
        await gcp_create_workitem(work_item_id="STAT-001", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Get status
        result = await gcp_status(
            work_item_id="STAT-001",
            work_items_dir=TEST_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )
        
        assert result["active"] is True
        assert "required_outputs" in result
        assert len(result["required_outputs"]["outputs"]) == 2

    @pytest.mark.asyncio
    async def test_status_shows_validation_state(self):
        """TC6.2: Status shows which outputs exist and which are missing."""
        # Create role file with required outputs
        create_role_file(TEST_WORKSPACE, "project-owner-assistant", """
# Role: Project Owner Assistant

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- dir: WorkItems/{id}/Design
""")
        
        # Create work item
        await gcp_create_workitem(work_item_id="STAT-002", work_items_dir=TEST_WORKITEMS_DIR)
        
        # Create one output but not the other
        user_story = TEST_WORKITEMS_DIR / "STAT-002" / "STAT-002-User-Story.md"
        user_story.write_text("# User Story", encoding="utf-8")
        # Design dir NOT created
        
        # Get status
        result = await gcp_status(
            work_item_id="STAT-002",
            work_items_dir=TEST_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )
        
        assert result["active"] is True
        assert result["required_outputs"]["complete"] is False
        
        # Find which outputs are valid/invalid
        outputs = result["required_outputs"]["outputs"]
        user_story_output = next(o for o in outputs if "User-Story" in o["path"])
        design_output = next(o for o in outputs if "Design" in o["path"])
        
        assert user_story_output["valid"] is True
        assert design_output["valid"] is False

    @pytest.mark.asyncio
    async def test_status_next_steps_include_remediation_for_missing(self):
        """TC3.4 (GCP-0027): Next steps should include remediation for missing outputs."""
        # Create role file with required outputs
        create_role_file(TEST_WORKSPACE, "project-owner-assistant", """
# Role: Project Owner Assistant

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- dir: WorkItems/{id}/Design
""")

        # Create work item
        await gcp_create_workitem(work_item_id="REM-001", work_items_dir=TEST_WORKITEMS_DIR)

        # Design dir NOT created, user story NOT created — both missing
        result = await gcp_status(
            work_item_id="REM-001",
            work_items_dir=TEST_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )

        assert result["active"] is True
        next_steps = result["next_steps"]

        # Should include remediation for the missing file
        assert any("Create file" in step and "User-Story" in step for step in next_steps), \
            f"Expected file remediation in next_steps, got: {next_steps}"
        # Should include remediation for the missing directory
        assert any("Create directory" in step and "Design" in step for step in next_steps), \
            f"Expected dir remediation in next_steps, got: {next_steps}"

    @pytest.mark.asyncio
    async def test_status_next_steps_no_remediation_when_all_present(self):
        """TC3.5 (GCP-0027): Next steps should NOT include remediation when all outputs exist."""
        # Create role file with required outputs
        create_role_file(TEST_WORKSPACE, "project-owner-assistant", """
# Role: Project Owner Assistant

## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- dir: WorkItems/{id}/Design
""")

        # Create work item
        await gcp_create_workitem(work_item_id="REM-002", work_items_dir=TEST_WORKITEMS_DIR)

        # Create BOTH required outputs
        user_story = TEST_WORKITEMS_DIR / "REM-002" / "REM-002-User-Story.md"
        user_story.write_text("# User Story", encoding="utf-8")
        design_dir = TEST_WORKITEMS_DIR / "REM-002" / "Design"
        design_dir.mkdir(parents=True, exist_ok=True)

        result = await gcp_status(
            work_item_id="REM-002",
            work_items_dir=TEST_WORKITEMS_DIR,
            project_root=TEST_WORKSPACE,
        )

        assert result["active"] is True
        next_steps = result["next_steps"]

        # Should NOT include any "Create file" or "Create directory" remediation
        assert not any("Create file" in step for step in next_steps), \
            f"Unexpected file remediation in next_steps: {next_steps}"
        assert not any("Create directory" in step for step in next_steps), \
            f"Unexpected dir remediation in next_steps: {next_steps}"
