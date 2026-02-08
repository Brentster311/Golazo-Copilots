# GCP-0025: Developer Role Notes

## Implementation Summary

Implemented the output validation feature in two phases:

### Phase 1: Core Validator Module

**File**: `golazo_copilot/core/output_validator.py`

Created a new module with:
- `OutputSpec` dataclass - represents a parsed output specification
- `ValidationResult` dataclass - aggregates validation results
- `parse_required_outputs()` - parses `## Required Outputs` section from role files
- `validate_all_outputs()` - validates all specs against workspace
- Individual validators for each type:
  - `_validate_file()` - checks file existence
  - `_validate_dir()` - checks directory existence  
  - `_validate_git_branch()` - verifies git branch exists
  - `_validate_git_log()` - checks for commits matching pattern

**Supported Formats**:
```markdown
## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- dir: WorkItems/{id}/Design
- git-branch: feature/{id}-*
- git-log: Implement {id}
```

### Phase 2: Integration with Tools

**File**: `golazo_copilot/tools/gcp_transition.py`

Added output validation before allowing role transitions:
1. Get workspace root from `work_items_dir.parent`
2. Load current role content via `get_role_content()`
3. Parse Required Outputs section
4. Validate all outputs exist
5. Block transition if any missing (unless force=True with consent)

**File**: `golazo_copilot/tools/gcp_status.py`

Added `required_outputs` field to status response:
```json
{
  "required_outputs": {
    "complete": false,
    "outputs": [
      {"type": "file", "path": "...", "valid": true},
      {"type": "dir", "path": "...", "valid": false}
    ]
  }
}
```

**File**: `golazo_copilot/roles/loader.py`

Added `get_role_content()` function to get raw role file content for parsing.

### Consent Integration

When outputs are missing and force=True:
- Checks for valid consent via `has_valid_consent(state, "skip_dor")`
- Returns consent-specific error message if no consent
- Consumes consent on successful force transition

## Test Coverage

- **20 unit tests** in `test_output_validator.py`:
  - TC1: Parse Required Outputs section (6 tests)
  - TC2: Validate file type (3 tests)  
  - TC3: Validate dir type (3 tests)
  - TC4: Validate git-branch (2 tests) - mocked
  - TC4: Validate git-log (2 tests) - mocked
  - TC5: Validate all outputs aggregation (4 tests)

- **6 integration tests** in `test_output_integration.py`:
  - TC5.1: Transition succeeds with all outputs
  - TC5.2: Transition blocked when output missing
  - TC5.3: Force transition with consent succeeds
  - TC5.4: Force without consent fails
  - TC6.1: Status includes required outputs
  - TC6.2: Status shows validation state

## Design Decisions

1. **Backward Compatibility**: Existing role files without `file:` prefixed lines return empty list, so validation passes. This ensures existing workflows continue to work.

2. **Path Resolution**: Uses `work_items_dir.parent` as workspace root, consistent with existing code patterns.

3. **Error Messages**: Consistent format with existing transition errors - includes missing files list and hint for force option.

4. **Consent Type**: Reuses `skip_dor` consent action for missing outputs, as this is conceptually similar to skipping DoR requirements.
