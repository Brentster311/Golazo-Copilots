# GCP-0020: Test Cases

## Test Strategy

All tests follow TDD-first principles. Tests written before implementation.

---

## Test Cases

### TC1: Block transition when notes missing
```python
async def test_transition_blocked_when_notes_missing():
    """Transition should fail if outgoing role has no notes file."""
    # Given: Work item in developer role, no developer notes file
    # When: gcp_transition(role="refactor-expert")
    # Then: Returns success=False, error contains "Missing role notes"
    # And: Error contains expected file path
```

### TC2: Allow transition when notes exist
```python
async def test_transition_allowed_when_notes_exist():
    """Transition should succeed if outgoing role has notes file."""
    # Given: Work item in developer role, developer notes file exists
    # When: gcp_transition(role="refactor-expert")
    # Then: Returns success=True
```

### TC3: Force without consent fails
```python
async def test_force_without_notes_requires_consent():
    """Force bypass should fail without prior consent."""
    # Given: Work item in developer role, no notes, no consent
    # When: gcp_transition(role="refactor-expert", force_without_notes=True)
    # Then: Returns success=False
    # And: Error contains "Cannot force without consent"
```

### TC4: Force with consent succeeds
```python
async def test_force_with_consent_succeeds():
    """Force bypass should succeed with prior consent."""
    # Given: Work item in developer role, no notes
    # And: gcp_consent(action="skip_role", reason="Spike exploration")
    # When: gcp_transition(role="refactor-expert", force_without_notes=True)
    # Then: Returns success=True
```

### TC5: First role exempt
```python
async def test_first_role_exempt_from_notes_check():
    """Project-owner-assistant entry doesn't require prior notes."""
    # Given: New work item (no prior role)
    # When: Transition to program-manager (from project-owner-assistant)
    # Then: Success (project-owner-assistant notes not required for ENTRY)
    # Note: BUT notes ARE required when LEAVING project-owner-assistant
```

### TC6: Error includes file path
```python
async def test_error_includes_expected_file_path():
    """Error message should include the exact file path to create."""
    # Given: Work item in developer role, no notes
    # When: gcp_transition(role="refactor-expert")
    # Then: Error contains "WorkItems/GCP-TEST/RoleDecisionNotes/GCP-TEST-developer.md"
```

### TC7: Backward transition checks outgoing role
```python
async def test_backward_transition_checks_outgoing_role():
    """Backward transitions should check notes for the role being LEFT."""
    # Given: Work item in developer role, no developer notes
    # When: gcp_transition(role="architect")  # backward
    # Then: Returns success=False (missing developer notes)
```

### TC8: Consumed consent cannot be reused
```python
async def test_consent_consumed_after_force():
    """After force bypass, consent should be consumed."""
    # Given: Work item with consent recorded
    # And: Force transition succeeds
    # When: Second force transition attempted
    # Then: Returns success=False (consent already consumed)
```

---

## Coverage Matrix

| Acceptance Criteria | Test Cases |
|---------------------|------------|
| Block when notes missing | TC1 |
| Actionable error with path | TC1, TC6 |
| Force requires consent | TC3, TC4 |
| First role exempt | TC5 |
| Backward transitions | TC7 |
| Consent consumption | TC8 |
