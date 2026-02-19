# GCP-0043 — Test Cases

## Mapping: Acceptance Criteria → Test Cases

| AC # | Acceptance Criterion | Test Case(s) |
|------|---------------------|--------------|
| AC1 | Rejects IDs not matching pattern with clear error | TC1.1–TC1.8 |
| AC2 | Accepts valid pattern IDs | TC2.1–TC2.5 |
| AC3 | POA format section removed | TC3.1 |
| AC4 | All tests pass | TC4.1 |

---

## TC1: Invalid ID Format Rejections

### TC1.1: Rejects free-form ID with no digit suffix
- **Input**: `work_item_id="feature-x"`
- **Expected**: `success=False`, error contains "must match" and includes format description
- **Failure message**: "Free-form IDs without numeric suffix should be rejected by format validation"

### TC1.2: Rejects ID with 5-letter prefix (boundary)
- **Input**: `work_item_id="ABCDE-001"`
- **Expected**: `success=False`, error contains format description
- **Failure message**: "Prefix exceeding 4 letters should be rejected"

### TC1.3: Rejects ID with 2-digit suffix (boundary)
- **Input**: `work_item_id="GCP-01"`
- **Expected**: `success=False`, error contains format description
- **Failure message**: "Suffix with fewer than 3 digits should be rejected"

### TC1.4: Rejects ID with underscore (previously valid)
- **Input**: `work_item_id="valid_id-123"` or `"G_P-001"`
- **Expected**: `success=False`, error contains format description
- **Failure message**: "Underscores should no longer be accepted under the new format pattern"

### TC1.5: Rejects ID with no dash separator
- **Input**: `work_item_id="GCP0001"`
- **Expected**: `success=False`, error contains format description
- **Failure message**: "ID without dash separator should be rejected"

### TC1.6: Rejects ID with digits in prefix
- **Input**: `work_item_id="G2P-001"`
- **Expected**: `success=False`, error contains format description
- **Failure message**: "Prefix must be letters only, digits in prefix should be rejected"

### TC1.7: Rejects ID with letters in suffix
- **Input**: `work_item_id="GCP-00A"`
- **Expected**: `success=False`, error contains format description
- **Failure message**: "Suffix must be digits only, letters in suffix should be rejected"

### TC1.8: Error message includes examples
- **Input**: `work_item_id="invalid"`
- **Expected**: `success=False`, error message contains at least two example valid IDs (e.g., "GCP-0001", "AB-001")
- **Failure message**: "Error message must include example valid IDs to guide the user"

## TC2: Valid ID Format Acceptances

### TC2.1: Accepts minimum valid ID (1-letter prefix, 3-digit suffix)
- **Input**: `work_item_id="A-001"`
- **Expected**: `success=True`, state.json created
- **Failure message**: "Single-letter prefix with 3-digit suffix should be accepted"

### TC2.2: Accepts maximum-length prefix (4 letters)
- **Input**: `work_item_id="TEST-1234"`
- **Expected**: `success=True`, state.json created
- **Failure message**: "4-letter prefix should be accepted"

### TC2.3: Accepts standard GCP format
- **Input**: `work_item_id="GCP-0043"`
- **Expected**: `success=True`, state.json created
- **Failure message**: "Standard GCP-NNNN format should be accepted"

### TC2.4: Accepts WIP-000 (default fallback)
- **Input**: `work_item_id="WIP-000"`
- **Expected**: `success=True`, state.json created
- **Failure message**: "WIP-000 must remain valid as the default fallback"

### TC2.5: Accepts long digit suffix
- **Input**: `work_item_id="GCP-99999"`
- **Expected**: `success=True`, state.json created
- **Failure message**: "Suffixes longer than 3 digits should be accepted (3+ means no upper limit)"

## TC3: Documentation Change

### TC3.1: POA role file no longer contains format requirements section
- **Verification**: Read `project-owner-assistant.md` and confirm the "Work Item ID Format Requirements" heading and its content (pattern, numbering, examples) are absent
- **Failure message**: "Format requirements section should be removed from POA since the tool enforces the format"

## TC4: Regression

### TC4.1: Full test suite passes
- **Verification**: Run `pytest` on all test files; all tests pass including updated IDs
- **Failure message**: "Existing tests must pass after ID updates"

---

## Existing Tests Requiring ID Updates

The following existing tests use free-form IDs that must be changed to pattern-compliant IDs:

| Test | Current ID | Suggested Replacement |
|------|-----------|----------------------|
| `test_creates_state_json` | `feature-x` | `FX-001` |
| `test_state_has_correct_schema_version` | `schema-test` | `ST-001` |
| `test_state_has_correct_work_item_id` | `my-feature` | `MF-001` |
| `test_state_has_correct_profile` | `profile-test` | `PT-001` |
| `test_defaults_profile_to_complete` | `default-profile` | `DP-001` |
| `test_state_starts_in_definition_phase` | `phase-test` | `PH-001` |
| `test_state_starts_with_project_owner_role` | `role-test` | `RT-001` |
| `test_state_has_no_dor_field` | `no-dor-test` | `ND-001` |
| `test_state_has_no_dod_field` | `no-dod-test` | `ND-002` |
| `test_role_history_has_initial_entry` | `history-test` | `HT-001` |
| `test_deviations_empty` | `deviations-test` | `DV-001` |
| `test_creates_directory_if_not_exists` | `create-dir` | `CD-001` |
| `test_returns_role_instructions` | `instructions-test` | `IT-001` |
| `test_rejects_duplicate_work_item` | `duplicate` | `DU-001` |
| `test_rejects_invalid_profile` | `invalid-profile` | `IP-001` |
| `test_old_state_with_dor_dod_loads` | `compat-1` | `CP-001` |
| `test_allows_hyphens_and_underscores` | `valid-id_123` | **Replace test** — see TC2.1–TC2.5 |
