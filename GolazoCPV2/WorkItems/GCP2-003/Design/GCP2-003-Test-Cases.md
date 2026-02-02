# GCP2-003: Test Cases

**Work Item**: GCP2-003 - Structured State Management  
**Role**: Tester  
**Date**: 2026-01-27

---

## Test Coverage Summary

| Acceptance Criteria | Test Cases | Coverage |
|---------------------|------------|----------|
| AC-1: State file at correct path | TC-01, TC-02 | ? |
| AC-2: State includes core fields | TC-03 | ? |
| AC-3: DoR status object | TC-04 | ? |
| AC-4: DoD status object | TC-05 | ? |
| AC-5: Role history array | TC-06, TC-07 | ? |
| AC-6: Persists across sessions | TC-08 | ? |
| AC-7: Human-readable JSON | TC-09 | ? |
| NFR-1: < 100ms latency | TC-10 | ? |
| Architect recommendations | TC-11 to TC-15 | ? |

---

## Happy Path Tests

### TC-01: Create New State File
**Maps to**: AC-1 (State file created at correct path)

**Preconditions**:
- WorkItems/TEST-001/ directory exists
- No state.json file exists

**Steps**:
1. Call `create("TEST-001", profile="complete")`

**Expected**:
- File created at `WorkItems/TEST-001/state.json`
- File contains valid JSON
- schemaVersion is "1.0"
- workItemId is "TEST-001"
- profile is "complete"

**Cleanup**: Delete TEST-001 directory

---

### TC-02: State File Location Consistency
**Maps to**: AC-1

**Steps**:
1. Create state for "GCP2-003"
2. Verify file path is exactly `WorkItems/GCP2-003/state.json`
3. Create state for "WIP-000"
4. Verify file path is exactly `WorkItems/WIP-000/state.json`

**Expected**: Paths follow `WorkItems/<id>/state.json` pattern exactly

---

### TC-03: Core Fields Present
**Maps to**: AC-2 (workItemId, profile, currentRole, currentPhase, timestamps)

**Steps**:
1. Create new state for "TEST-002"
2. Load state
3. Verify all required fields exist

**Expected**:
```python
assert state.workItemId == "TEST-002"
assert state.profile in ["complete", "express", "spike"]
assert state.currentRole == "project-owner"  # default start
assert state.currentPhase == "design"  # default start
assert state.createdAt is not None  # ISO8601 format
assert state.updatedAt is not None  # ISO8601 format
```

---

### TC-04: DoR Status Object
**Maps to**: AC-3

**Steps**:
1. Create new state
2. Verify dor object has all required fields
3. Verify all default to False

**Expected**:
```python
assert state.dor == {
    "userStory": False,
    "designDoc": False,
    "reviewComments": False,
    "testCases": False
}
```

---

### TC-05: DoD Status Object
**Maps to**: AC-4

**Steps**:
1. Create new state
2. Verify dod object has all required fields
3. Verify all default to False

**Expected**:
```python
assert state.dod == {
    "branchCreated": False,
    "testsWrittenFirst": False,
    "testsPass": False,
    "buildPasses": False,
    "docsUpdated": False,
    "refactorComplete": False,
    "committed": False
}
```

---

### TC-06: Role History Initial Entry
**Maps to**: AC-5

**Steps**:
1. Create new state
2. Verify roleHistory contains initial entry

**Expected**:
```python
assert len(state.roleHistory) == 1
assert state.roleHistory[0]["role"] == "project-owner"
assert state.roleHistory[0]["enteredAt"] is not None
assert state.roleHistory[0]["exitedAt"] is None
```

---

### TC-07: Role History Accumulation
**Maps to**: AC-5

**Steps**:
1. Create new state
2. Simulate role transition: project-owner ? program-manager
3. Save and reload state
4. Verify roleHistory has two entries

**Expected**:
```python
assert len(state.roleHistory) == 2
assert state.roleHistory[0]["exitedAt"] is not None  # first role exited
assert state.roleHistory[1]["role"] == "program-manager"
assert state.roleHistory[1]["exitedAt"] is None  # current role
```

---

### TC-08: Persistence Across Sessions
**Maps to**: AC-6

**Steps**:
1. Create state with custom values
2. Save state
3. Clear all in-memory references (simulate session end)
4. Load state fresh from file
5. Verify all values preserved

**Expected**:
- All fields match original values
- Timestamps unchanged
- roleHistory preserved

---

### TC-09: Human-Readable JSON (Pretty Print)
**Maps to**: AC-7

**Steps**:
1. Create and save state
2. Read raw file content
3. Check formatting

**Expected**:
- JSON has newlines (not single line)
- JSON has indentation (2 or 4 spaces)
- File is readable in text editor

---

## Performance Tests

### TC-10: Read/Write Latency
**Maps to**: NFR-1 (< 100ms)

**Steps**:
1. Create state file
2. Measure time for load() operation (100 iterations, take average)
3. Measure time for save() operation (100 iterations, take average)

**Expected**:
- load() average < 100ms
- save() average < 100ms
- No operation exceeds 500ms (outlier threshold)

---

## Edge Case Tests

### TC-11: Missing State File
**Maps to**: Resilience (Architect recommendation)

**Steps**:
1. Call load() for non-existent work item

**Expected**:
- Returns None (not exception)
- No file created
- Appropriate log message

---

### TC-12: Empty WorkItems Directory
**Steps**:
1. Ensure WorkItems directory is empty
2. Call create() for new work item

**Expected**:
- Directory created if needed
- State file created successfully

---

### TC-13: Work Item ID with Special Characters
**Maps to**: Path safety (Architect recommendation)

**Test Data**:
| Input | Expected Result |
|-------|-----------------|
| "GCP2-003" | ? Valid |
| "WIP-000" | ? Valid |
| "feature/login" | ? Rejected (contains /) |
| "../etc/passwd" | ? Rejected (path traversal) |
| "test\\item" | ? Rejected (contains \\) |
| "" | ? Rejected (empty) |
| "a" * 256 | ? Rejected (too long) |

**Expected**: Invalid IDs raise `ValueError` with clear message

---

## Error Handling Tests

### TC-14: Corrupted JSON File
**Maps to**: Resilience (Architect recommendation), PO Decision

**Steps**:
1. Create valid state file at `WorkItems/TEST-014/state.json`
2. Manually corrupt JSON (e.g., remove closing brace)
3. Call load("TEST-014")

**Expected**:
- Original file renamed to `state.json.corrupted`
- Fresh state.json created with defaults
- Warning logged: "state.json was corrupted. Backed up to state.json.corrupted and created fresh state."
- Returns fresh State object (not None, not exception)

**Verification**:
- `state.json.corrupted` exists with original corrupt content
- `state.json` exists with valid fresh state

---

### TC-15: Missing Required Fields
**Maps to**: Schema validation

**Steps**:
1. Create state file with missing `currentRole` field
2. Call load()

**Expected**:
- Either: use default value and log warning
- Or: raise clear error indicating missing field

---

### TC-16: Old Schema Version
**Maps to**: Schema migration (NFR-3)

**Steps**:
1. Create state file with schemaVersion "0.9" (older)
2. Call load()

**Expected**:
- Either: migrate to current schema automatically
- Or: raise clear error with migration instructions

---

## Security Tests

### TC-17: Path Traversal Prevention
**Maps to**: Security (Architect recommendation)

**Steps**:
1. Attempt to create state with workItemId = "../../../etc/passwd"
2. Attempt to load state with similar malicious ID

**Expected**:
- Creation fails with clear error
- Load fails with clear error
- No file operations outside WorkItems/ directory

---

## Negative Tests

### TC-18: Save Without Required Fields
**Steps**:
1. Construct State object with None for workItemId
2. Call save()

**Expected**:
- Raises ValidationError
- Does not create corrupt file

---

### TC-19: Concurrent Write (Future)
**Maps to**: GCP2-006 consideration

**Note**: Deferred. Single-user assumption for MVP.
**Future test**: Verify behavior when two processes write simultaneously.

---

## Test Implementation Notes

### Test File Structure
```
tests/
??? test_state.py          # Unit tests for state module
??? test_state_integration.py  # End-to-end tests
??? fixtures/
    ??? valid_state.json   # Sample valid state
    ??? corrupted_state.json  # Sample corrupted state
```

### Test Framework
- pytest (standard for Python projects)
- pytest-benchmark for TC-10 (performance)

### Mocking Strategy
- Use `tmp_path` fixture for isolated file operations
- No mocking of file system (test real behavior)

---

## Traceability Matrix

| Test Case | Acceptance Criteria | Architect Note | Priority |
|-----------|---------------------|----------------|----------|
| TC-01 | AC-1 | - | High |
| TC-02 | AC-1 | - | High |
| TC-03 | AC-2 | - | High |
| TC-04 | AC-3 | - | High |
| TC-05 | AC-4 | - | High |
| TC-06 | AC-5 | - | High |
| TC-07 | AC-5 | - | High |
| TC-08 | AC-6 | - | High |
| TC-09 | AC-7 | - | Medium |
| TC-10 | NFR-1 | - | Medium |
| TC-11 | - | Resilience | High |
| TC-12 | - | - | Medium |
| TC-13 | - | Path safety | High |
| TC-14 | - | Resilience | High |
| TC-15 | - | Schema validation | Medium |
| TC-16 | NFR-3 | Schema migration | Medium |
| TC-17 | - | Security | High |
| TC-18 | - | - | Medium |
| TC-19 | - | GCP2-006 | Deferred |
