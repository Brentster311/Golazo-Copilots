# GCP-0001 Test Cases

## Overview
Test-first specification for GCP-0001: Initialize Work Item

**Mapped to**: Acceptance Criteria AC1-AC6  
**Test Framework**: pytest  
**Coverage Target**: 100% of acceptance criteria

---

## Test Suite: gcp_init Tool

### TC1: Successful Initialization (AC1)

```python
import pytest
from pathlib import Path
import json
from golazo_copilot.tools.gcp_init import gcp_init
from golazo_copilot.core.persistence import load_state

TEST_WORKITEMS_DIR = Path("test-workitems")

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directory before and after each test."""
    import shutil
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)
    yield
    if TEST_WORKITEMS_DIR.exists():
        shutil.rmtree(TEST_WORKITEMS_DIR)


class TestGcpInitSuccess:
    """TC1: Successful Initialization (AC1)"""
    
    async def test_creates_state_json_with_correct_initial_state(self):
        """Should create state.json with correct initial state."""
        result = await gcp_init(
            work_item_id="feature-x",
            profile="complete",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        
        state_path = TEST_WORKITEMS_DIR / "feature-x" / "state.json"
        assert state_path.exists()
        
        state = json.loads(state_path.read_text())
        assert state["schema_version"] == "1.0"
        assert state["work_item_id"] == "feature-x"
        assert state["profile"] == "complete"
        assert state["current_phase"] == "definition"
        assert state["current_role"] == "project-owner"
        assert state["dor"] == {
            "userStory": False,
            "designDoc": False,
            "reviewComments": False,
            "testCases": False
        }
        assert state["dod"] == {
            "branchCreated": False,
            "testsWrittenFirst": False,
            "testsPass": False,
            "buildPasses": False,
            "docsUpdated": False,
            "refactorComplete": False,
            "committed": False
        }
        assert len(state["role_history"]) == 1
        assert state["role_history"][0]["role"] == "project-owner"
        assert state["role_history"][0]["exited_at"] is None
        assert state["deviations"] == []

    async def test_creates_workitems_directory_if_not_exists(self):
        """Should create WorkItems directory if not exists."""
        assert not TEST_WORKITEMS_DIR.exists()
        
        await gcp_init(work_item_id="new-feature", work_items_dir=TEST_WORKITEMS_DIR)
        
        assert (TEST_WORKITEMS_DIR / "new-feature" / "state.json").exists()

    async def test_sets_timestamps_in_iso_format(self):
        """Should set timestamps in ISO 8601 format."""
        from datetime import datetime
        
        before = datetime.utcnow().isoformat()
        await gcp_init(work_item_id="timestamp-test", work_items_dir=TEST_WORKITEMS_DIR)
        after = datetime.utcnow().isoformat()
        
        state = load_state("timestamp-test", TEST_WORKITEMS_DIR)
        assert before <= state.created_at.isoformat() <= after
        assert state.updated_at == state.created_at

    async def test_defaults_profile_to_complete(self):
        """Should default profile to 'complete' when not specified."""
        await gcp_init(work_item_id="default-profile", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = load_state("default-profile", TEST_WORKITEMS_DIR)
        assert state.profile == "complete"
```

---

### TC2: Role Instructions Returned (AC2)

```python
class TestRoleInstructions:
    """TC2: Role Instructions Returned (AC2)"""
    
    async def test_returns_project_owner_instructions(self):
        """Should return project-owner role instructions on success."""
        result = await gcp_init(
            work_item_id="instructions-test",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is True
        assert result["current_role"] == "project-owner"
        assert result["role_instructions"] is not None
        assert len(result["role_instructions"]) > 100
        assert "Project Owner" in result["role_instructions"]

    async def test_uses_local_role_file_if_exists(self, tmp_path):
        """Should use local role file if exists."""
        # Create local override
        local_roles = tmp_path / ".github" / "roles"
        local_roles.mkdir(parents=True)
        (local_roles / "project-owner.md").write_text("# Custom Project Owner\nLocal override")
        
        result = await gcp_init(
            work_item_id="local-roles",
            work_items_dir=TEST_WORKITEMS_DIR,
            project_root=tmp_path
        )
        
        assert "Custom Project Owner" in result["role_instructions"]
        assert "Local override" in result["role_instructions"]
```

---

### TC3: Default Role Files (AC3)

```python
class TestDefaultRoleFiles:
    """TC3: Default Role Files in Package (AC3)"""
    
    @pytest.mark.parametrize("role", [
        "project-owner",
        "program-manager",
        "quality-assurance",
        "architect",
        "developer",
        "refactor-expert",
        "builder",
        "Documenter"
    ])
    def test_default_role_file_exists(self, role):
        """Should include default role instruction files."""
        from golazo_copilot.roles.loader import load_default_role
        
        content = load_default_role(role)
        assert content is not None
        assert len(content) > 100

    @pytest.mark.parametrize("role", [
        "project-owner",
        "program-manager",
        "quality-assurance",
        "architect",
        "developer",
        "refactor-expert",
        "builder",
        "Documenter"
    ])
    def test_role_file_contains_required_sections(self, role):
        """Role file should contain purpose and outputs."""
        from golazo_copilot.roles.loader import load_default_role
        
        content = load_default_role(role).lower()
        assert "purpose" in content or "responsibilities" in content
        assert "output" in content or "deliverable" in content
```

---

### TC4: state://current Resource (AC4)

```python
class TestStateResource:
    """TC4: state://current Resource (AC4)"""
    
    async def test_returns_current_state_after_init(self):
        """Should return current state after init."""
        from golazo_copilot.resources.state_current import get_current_state
        
        await gcp_init(work_item_id="resource-test", work_items_dir=TEST_WORKITEMS_DIR)
        
        state = await get_current_state()
        assert state["work_item_id"] == "resource-test"
        assert state["current_role"] == "project-owner"

    async def test_returns_error_if_no_active_work_item(self):
        """Should return error if no work item initialized."""
        from golazo_copilot.resources.state_current import get_current_state
        
        # Clear any active work item
        # ...
        
        with pytest.raises(Exception, match="No active work item"):
            await get_current_state()
```

---

### TC5: Error Handling (AC5)

```python
class TestErrorHandling:
    """TC5: Idempotency & Error Handling (AC5)"""
    
    async def test_rejects_duplicate_work_item_id(self):
        """Should reject duplicate work item ID."""
        await gcp_init(work_item_id="duplicate", work_items_dir=TEST_WORKITEMS_DIR)
        
        result = await gcp_init(work_item_id="duplicate", work_items_dir=TEST_WORKITEMS_DIR)
        
        assert result["success"] is False
        assert "already exists" in result["error"]
        assert "gcp_switch" in result["error"]

    async def test_rejects_work_item_id_with_spaces(self):
        """Should reject workItemId with spaces."""
        result = await gcp_init(work_item_id="has spaces", work_items_dir=TEST_WORKITEMS_DIR)
        
        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    async def test_rejects_work_item_id_with_forward_slash(self):
        """Should reject workItemId with forward slash."""
        result = await gcp_init(work_item_id="has/slash", work_items_dir=TEST_WORKITEMS_DIR)
        
        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    async def test_rejects_work_item_id_with_backslash(self):
        """Should reject workItemId with backslash."""
        result = await gcp_init(work_item_id="has\\backslash", work_items_dir=TEST_WORKITEMS_DIR)
        
        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    async def test_allows_hyphens_and_underscores(self):
        """Should allow hyphens and underscores."""
        result = await gcp_init(work_item_id="valid-id_123", work_items_dir=TEST_WORKITEMS_DIR)
        
        assert result["success"] is True

    async def test_rejects_empty_work_item_id(self):
        """Should reject empty workItemId."""
        result = await gcp_init(work_item_id="", work_items_dir=TEST_WORKITEMS_DIR)
        
        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    async def test_rejects_dot_as_work_item_id(self):
        """Should reject '.' as workItemId."""
        result = await gcp_init(work_item_id=".", work_items_dir=TEST_WORKITEMS_DIR)
        
        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    async def test_rejects_dotdot_as_work_item_id(self):
        """Should reject '..' as workItemId."""
        result = await gcp_init(work_item_id="..", work_items_dir=TEST_WORKITEMS_DIR)
        
        assert result["success"] is False
        assert "Invalid work item ID" in result["error"]

    async def test_rejects_work_item_id_over_100_chars(self):
        """Should reject workItemId longer than 100 characters."""
        long_id = "a" * 101
        result = await gcp_init(work_item_id=long_id, work_items_dir=TEST_WORKITEMS_DIR)
        
        assert result["success"] is False
        assert "too long" in result["error"]

    async def test_rejects_invalid_profile(self):
        """Should reject invalid profile."""
        result = await gcp_init(
            work_item_id="invalid-profile",
            profile="invalid",
            work_items_dir=TEST_WORKITEMS_DIR
        )
        
        assert result["success"] is False
        assert "Invalid profile" in result["error"]
```

---

## Coverage Matrix

| AC | Test Cases | Count |
|----|------------|-------|
| AC1 | TC1.1-1.4 | 4 |
| AC2 | TC2.1-2.2 | 2 |
| AC3 | TC3.1-3.2 (x8 roles) | 16 |
| AC4 | TC4.1-4.2 | 2 |
| AC5 | TC5.1-5.10 | 10 |
| AC6 | TC6.1 | 1 |
| **Total** | | **35** |

---

## Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=golazo_copilot

# Run specific test file
pytest tests/test_gcp_init.py

# Run with verbose output
pytest -v
```
