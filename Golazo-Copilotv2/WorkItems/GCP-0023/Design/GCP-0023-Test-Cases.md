# GCP-0023 Test Cases

## Test Case Mapping to Acceptance Criteria

| AC# | Acceptance Criterion | Test Cases |
|-----|---------------------|------------|
| AC1 | `gcp_mark_dor` rejects calls without `evidence` parameter | TC01, TC02 |
| AC2 | `gcp_mark_dod` rejects calls without `evidence` parameter | TC03, TC04 |
| AC3 | File-based evidence: system verifies file exists | TC05-TC10 |
| AC4 | Git-based evidence: system verifies via git commands | TC11-TC16 |
| AC5 | Command-based evidence: accepts command output or CI link | TC17-TC19 |
| AC6 | Error messages clearly state what's missing | TC20-TC22 |
| AC7 | Existing tests updated to provide evidence | TC23 |
| AC8 | State.json stores evidence alongside boolean | TC24-TC26 |

---

## Test Cases

### TC01: DoR mark without evidence fails
**Given:** Valid work item exists  
**When:** `gcp_mark_dor(work_item_id="TEST-0001", item="userStory")` called without `evidence`  
**Then:** Returns `success=False` with error containing "evidence"  
**Expected Error:** "Missing required parameter 'evidence'"

### TC02: DoR mark with evidence succeeds
**Given:** Valid work item exists, User Story file exists  
**When:** `gcp_mark_dor(work_item_id="TEST-0001", item="userStory", evidence="WorkItems/TEST-0001/TEST-0001-User-Story.md")`  
**Then:** Returns `success=True`, DoR userStory is marked complete

### TC03: DoD mark without evidence fails
**Given:** Valid work item exists  
**When:** `gcp_mark_dod(work_item_id="TEST-0001", item="testsPass")` called without `evidence`  
**Then:** Returns `success=False` with error containing "evidence"

### TC04: DoD mark with evidence succeeds
**Given:** Valid work item exists  
**When:** `gcp_mark_dod(work_item_id="TEST-0001", item="testsPass", evidence="pytest passed: 113 tests")`  
**Then:** Returns `success=True`, DoD testsPass is marked complete

---

### File Evidence Validation

### TC05: Valid file path evidence accepted
**Given:** File `WorkItems/TEST-0001/TEST-0001-User-Story.md` exists  
**When:** Mark with `evidence="WorkItems/TEST-0001/TEST-0001-User-Story.md"`  
**Then:** Validation succeeds

### TC06: Non-existent file path rejected
**Given:** File `WorkItems/TEST-0001/missing.md` does NOT exist  
**When:** Mark with `evidence="WorkItems/TEST-0001/missing.md"`  
**Then:** Returns `success=False`, error mentions file not found

### TC07: Directory path rejected (not a file)
**Given:** `WorkItems/TEST-0001/` is a directory  
**When:** Mark with `evidence="WorkItems/TEST-0001/"`  
**Then:** Returns `success=False`, error mentions "not a file"

### TC08: Absolute path accepted
**Given:** File exists at absolute path  
**When:** Mark with absolute path as evidence  
**Then:** Validation succeeds

### TC09: Path with spaces handled
**Given:** File `WorkItems/TEST-0001/My User Story.md` exists  
**When:** Mark with `evidence="WorkItems/TEST-0001/My User Story.md"`  
**Then:** Validation succeeds

### TC10: Multiple file paths accepted (list)
**Given:** Multiple test files exist  
**When:** Mark `testsWrittenFirst` with `evidence=["tests/test_a.py", "tests/test_b.py"]`  
**Then:** Validation succeeds if ALL files exist

---

### Git Evidence Validation

### TC11: Valid branch name accepted
**Given:** Git branch `GCP-0023` exists  
**When:** Mark `branchCreated` with `evidence="GCP-0023"`  
**Then:** Validation succeeds

### TC12: Non-existent branch rejected
**Given:** Git branch `NONEXISTENT-9999` does NOT exist  
**When:** Mark `branchCreated` with `evidence="NONEXISTENT-9999"`  
**Then:** Returns `success=False`, error mentions branch not found

### TC13: Valid commit SHA accepted
**Given:** Commit `abc123def` exists in repo  
**When:** Mark `committed` with `evidence="abc123def"`  
**Then:** Validation succeeds

### TC14: Invalid commit SHA rejected
**Given:** Commit `0000000000` does NOT exist  
**When:** Mark `committed` with `evidence="0000000000"`  
**Then:** Returns `success=False`, error mentions commit not found

### TC15: Short SHA accepted (7+ chars)
**Given:** Commit exists with full SHA starting with `abc1234`  
**When:** Mark with `evidence="abc1234"`  
**Then:** Validation succeeds

### TC16: Git not available handled gracefully
**Given:** Git is not in PATH  
**When:** Mark `branchCreated` with any evidence  
**Then:** Returns `success=False`, error mentions git not available

---

### Command-Based Evidence

### TC17: Test output accepted as-is
**Given:** Valid work item  
**When:** Mark `testsPass` with `evidence="pytest: 113 passed in 1.2s"`  
**Then:** Validation succeeds (no verification of content)

### TC18: CI link accepted as-is
**Given:** Valid work item  
**When:** Mark `buildPasses` with `evidence="https://dev.azure.com/build/123"`  
**Then:** Validation succeeds

### TC19: Empty string rejected
**Given:** Valid work item  
**When:** Mark `testsPass` with `evidence=""`  
**Then:** Returns `success=False`, error mentions empty evidence

---

### Error Messages

### TC20: Error includes expected format
**Given:** Mark fails due to missing file  
**When:** Error returned  
**Then:** Error contains example of expected format

### TC21: Error includes item name
**Given:** Mark fails for `userStory`  
**When:** Error returned  
**Then:** Error contains "userStory"

### TC22: Error includes actual path checked
**Given:** Mark fails for non-existent file  
**When:** Error returned  
**Then:** Error contains the path that was checked

---

### Backward Compatibility

### TC23: Old state.json format still works
**Given:** state.json with old format `{ "dor": { "userStory": true } }`  
**When:** `gcp_status` called  
**Then:** Status shows userStory as complete (no errors)

---

### Evidence Storage

### TC24: Evidence stored in state.json
**Given:** Mark succeeds with evidence  
**When:** state.json read  
**Then:** Contains `{ "dor": { "userStory": { "complete": true, "evidence": "..." } } }`

### TC25: Timestamp stored with evidence
**Given:** Mark succeeds  
**When:** state.json read  
**Then:** Contains `validated_at` with ISO8601 timestamp

### TC26: Multiple marks preserve all evidence
**Given:** userStory and designDoc both marked  
**When:** state.json read  
**Then:** Both have their respective evidence stored

---

### Edge Cases

### TC27: N/A evidence for refactorComplete
**Given:** Valid work item  
**When:** Mark `refactorComplete` with `evidence="N/A: No refactoring needed for this change"`  
**Then:** Validation succeeds

### TC28: N/A without reason rejected
**Given:** Valid work item  
**When:** Mark `refactorComplete` with `evidence="N/A"`  
**Then:** Returns `success=False`, error mentions reason required

### TC29: Unicode in file path
**Given:** File `WorkItems/TEST-0001/设计文档.md` exists  
**When:** Mark with that path  
**Then:** Validation succeeds

### TC30: Very long evidence truncated in display
**Given:** Evidence string >500 chars  
**When:** Stored and displayed  
**Then:** Stored in full, display truncated with "..."
