# GCP-0025 Test Cases

## Test Strategy

Tests will be organized by phase and component. All tests use pytest with async support.

---

## Phase 1: Output Validator Tests

### TC1: Parse Required Outputs Section

#### TC1.1: Parse file output
```python
def test_parse_file_output():
    """Parse 'file: path/to/file.md' from role file."""
    content = """
## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
"""
    outputs = parse_required_outputs(content, "GCP-0025")
    assert outputs == [
        {"type": "file", "path": "WorkItems/GCP-0025/GCP-0025-User-Story.md"}
    ]
```

#### TC1.2: Parse directory output
```python
def test_parse_dir_output():
    """Parse 'dir: path/to/dir' from role file."""
    content = """
## Required Outputs
- dir: WorkItems/{id}/Design
"""
    outputs = parse_required_outputs(content, "GCP-0025")
    assert outputs == [
        {"type": "dir", "path": "WorkItems/GCP-0025/Design"}
    ]
```

#### TC1.3: Parse git-branch output
```python
def test_parse_git_branch_output():
    """Parse 'git-branch: pattern' from role file."""
    content = """
## Required Outputs
- git-branch: feature/{id}*
"""
    outputs = parse_required_outputs(content, "GCP-0025")
    assert outputs == [
        {"type": "git-branch", "pattern": "feature/GCP-0025*"}
    ]
```

#### TC1.4: Parse multiple outputs
```python
def test_parse_multiple_outputs():
    """Parse multiple output lines."""
    content = """
## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- file: WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md
"""
    outputs = parse_required_outputs(content, "GCP-0025")
    assert len(outputs) == 2
```

#### TC1.5: Handle missing section
```python
def test_parse_missing_section():
    """Return empty list if no Required Outputs section."""
    content = "# Role: Test\n\nNo outputs here."
    outputs = parse_required_outputs(content, "GCP-0025")
    assert outputs == []
```

#### TC1.6: Handle empty section
```python
def test_parse_empty_section():
    """Return empty list if Required Outputs section is empty."""
    content = """
## Required Outputs

## Next Section
"""
    outputs = parse_required_outputs(content, "GCP-0025")
    assert outputs == []
```

#### TC1.7: Ignore comments in section
```python
def test_parse_ignores_comments():
    """Ignore HTML comments in Required Outputs section."""
    content = """
## Required Outputs
<!-- This is validated on exit -->
- file: WorkItems/{id}/{id}-User-Story.md
"""
    outputs = parse_required_outputs(content, "GCP-0025")
    assert len(outputs) == 1
    assert outputs[0]["type"] == "file"
```

---

### TC2: Validate File Output

#### TC2.1: Valid file exists
```python
def test_validate_file_exists(tmp_path):
    """Return valid when file exists."""
    (tmp_path / "test.md").touch()
    result = validate_output({"type": "file", "path": "test.md"}, tmp_path)
    assert result.valid is True
```

#### TC2.2: File does not exist
```python
def test_validate_file_not_exists(tmp_path):
    """Return invalid with clear message when file missing."""
    result = validate_output({"type": "file", "path": "missing.md"}, tmp_path)
    assert result.valid is False
    assert "missing.md" in result.message
    assert "not found" in result.message.lower()
```

#### TC2.3: Path is directory not file
```python
def test_validate_file_is_directory(tmp_path):
    """Return invalid when path exists but is a directory."""
    (tmp_path / "subdir").mkdir()
    result = validate_output({"type": "file", "path": "subdir"}, tmp_path)
    assert result.valid is False
    assert "directory" in result.message.lower() or "not a file" in result.message.lower()
```

---

### TC3: Validate Directory Output

#### TC3.1: Valid directory exists
```python
def test_validate_dir_exists(tmp_path):
    """Return valid when directory exists."""
    (tmp_path / "Design").mkdir()
    result = validate_output({"type": "dir", "path": "Design"}, tmp_path)
    assert result.valid is True
```

#### TC3.2: Directory does not exist
```python
def test_validate_dir_not_exists(tmp_path):
    """Return invalid when directory missing."""
    result = validate_output({"type": "dir", "path": "Missing"}, tmp_path)
    assert result.valid is False
```

---

### TC4: Validate Git Branch Output

#### TC4.1: Branch exists
```python
def test_validate_git_branch_exists(tmp_path, monkeypatch):
    """Return valid when git branch exists."""
    # Mock git branch --list to return branch
    def mock_run(*args, **kwargs):
        class Result:
            stdout = "  feature/GCP-0025-refactor\n"
            stderr = ""
            returncode = 0
        return Result()
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    result = validate_output({"type": "git-branch", "pattern": "feature/GCP-0025*"}, tmp_path)
    assert result.valid is True
```

#### TC4.2: Branch does not exist
```python
def test_validate_git_branch_not_exists(tmp_path, monkeypatch):
    """Return invalid when no matching branch."""
    def mock_run(*args, **kwargs):
        class Result:
            stdout = ""
            stderr = ""
            returncode = 0
        return Result()
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    result = validate_output({"type": "git-branch", "pattern": "feature/GCP-9999*"}, tmp_path)
    assert result.valid is False
```

---

## Phase 2: Integration Tests

### TC5: Transition Validates Outputs

#### TC5.1: Transition succeeds when all outputs exist
```python
async def test_transition_succeeds_with_all_outputs():
    """Allow transition when all required outputs exist."""
    # Create work item, create required files
    # Transition should succeed
```

#### TC5.2: Transition blocked when output missing
```python
async def test_transition_blocked_missing_output():
    """Block transition with clear error when output missing."""
    # Create work item, don't create required files
    # Transition should fail with specific missing file in error
```

#### TC5.3: Force transition with consent
```python
async def test_transition_force_with_consent():
    """Allow force transition when consent recorded."""
    # Create work item, don't create required files
    # Record consent
    # Force transition should succeed
```

#### TC5.4: Force transition without consent fails
```python
async def test_transition_force_without_consent_fails():
    """Block force transition when no consent."""
    # Create work item, don't create required files
    # Force transition should fail
```

### TC6: Status Shows Output Validation

#### TC6.1: Status includes output list
```python
async def test_status_includes_outputs():
    """Status response includes required outputs for current role."""
    # Create work item
    # Check status includes outputs list
```

#### TC6.2: Status shows validation state
```python
async def test_status_shows_validation_state():
    """Status shows which outputs exist and which are missing."""
    # Create work item, create some but not all outputs
    # Status should show checkmarks for existing, X for missing
```

---

## Phase 3: Removal Tests

### TC7: Removed Tools Return Error

#### TC7.1: gcp_mark_dor returns error (if called via old instructions)
```python
async def test_mark_dor_removed():
    """Calling removed gcp_mark_dor returns helpful error."""
    # This test verifies the tool is not in the server's tool list
```

### TC8: Backward Compatibility

#### TC8.1: Old state.json loads without error
```python
async def test_old_state_loads():
    """State.json with dor/dod fields loads without error."""
    # Create state.json with old format including dor/dod
    # Load should succeed, dor/dod ignored
```

---

## Test Count Summary

| Phase | Test Cases |
|-------|-----------|
| Phase 1: Parsing | 7 |
| Phase 1: File validation | 3 |
| Phase 1: Dir validation | 2 |
| Phase 1: Git branch validation | 2 |
| Phase 2: Transition | 4 |
| Phase 2: Status | 2 |
| Phase 3: Removal | 2 |
| **Total** | **22** |
