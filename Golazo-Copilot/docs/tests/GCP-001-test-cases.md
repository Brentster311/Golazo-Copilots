# GCP-001: Test Cases

## Work Item
GCP-001 — Copy Golazo Copilot Instructions Locally

## Test Strategy
Since this work item involves static file creation (no runtime code), tests will be:
1. **Manual verification** — File existence and content checks
2. **Automated shell script** — Can be run to verify file structure

---

## Acceptance Criteria Mapping

| AC # | Acceptance Criterion | Test Case(s) |
|------|---------------------|--------------|
| AC-1 | `.github/copilot-instructions.md` exists with full Golazo spine content | TC-01, TC-02 |
| AC-2 | `.github/roles/project-owner-assistant.md` exists with full role instructions | TC-03, TC-04 |
| AC-3 | `.github/roles/program-manager.md` exists | TC-05 |
| AC-4 | `.github/roles/reviewer.md` exists | TC-06 |
| AC-5 | `.github/roles/architect.md` exists | TC-07 |
| AC-6 | `.github/roles/tester.md` exists | TC-08 |
| AC-7 | `.github/roles/developer.md` exists | TC-09 |
| AC-8 | `.github/roles/refactor-expert.md` exists | TC-10 |
| AC-9 | `.github/roles/builder.md` exists | TC-11 |
| AC-10 | `.github/roles/documentor.md` exists | TC-12 |
| AC-11 | `.github/roles/retrospective.md` exists | TC-13 |

---

## Test Cases

### TC-01: Spine file exists
**Type**: Existence check  
**Preconditions**: Implementation complete  
**Steps**:
1. Check if `.github/copilot-instructions.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/copilot-instructions.md not found"

### TC-02: Spine file contains required sections
**Type**: Content validation  
**Preconditions**: TC-01 passes  
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Verify file contains "# Golazo Copilot Instructions"
3. Verify file contains "## Absolute enforcement rules"
4. Verify file contains "## Role instruction loading rule"
5. Verify file contains "## Golazo workflow state machine"
**Expected Result**: All sections present  
**Failure Message**: "FAIL: Spine file missing required section: [section name]"

### TC-03: Project Owner Assistant file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/project-owner-assistant.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/project-owner-assistant.md not found"

### TC-04: Project Owner Assistant file has content
**Type**: Content validation  
**Preconditions**: TC-03 passes  
**Steps**:
1. Open `.github/roles/project-owner-assistant.md`
2. Verify file contains "# Role: Project Owner Assistant"
3. Verify file contains "## Purpose"
4. Verify file contains "## Responsibilities"
**Expected Result**: Required sections present  
**Failure Message**: "FAIL: Project Owner Assistant file missing required content"

### TC-05: Program Manager file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/program-manager.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/program-manager.md not found"

### TC-06: Reviewer file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/reviewer.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/reviewer.md not found"

### TC-07: Architect file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/architect.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/architect.md not found"

### TC-08: Tester file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/tester.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/tester.md not found"

### TC-09: Developer file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/developer.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/developer.md not found"

### TC-10: Refactor Expert file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/refactor-expert.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/refactor-expert.md not found"

### TC-11: Builder file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/builder.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/builder.md not found"

### TC-12: Documentor file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/documentor.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/documentor.md not found"

### TC-13: Retrospective file exists
**Type**: Existence check  
**Steps**:
1. Check if `.github/roles/retrospective.md` exists
**Expected Result**: File exists  
**Failure Message**: "FAIL: .github/roles/retrospective.md not found"

---

## Edge Cases

### TC-14: Files are valid UTF-8
**Type**: Encoding validation  
**Steps**:
1. For each file in `.github/` and `.github/roles/`
2. Attempt to read as UTF-8
**Expected Result**: All files read successfully without encoding errors  
**Failure Message**: "FAIL: [filename] is not valid UTF-8"

### TC-15: No broken markdown links in spine
**Type**: Reference validation  
**Steps**:
1. Parse `.github/copilot-instructions.md`
2. Extract all role file references
3. Verify each referenced file exists
**Expected Result**: All referenced files exist  
**Failure Message**: "FAIL: Spine references non-existent file: [path]"

---

## Negative Tests

### TC-16: Spine file is not empty
**Type**: Negative validation  
**Steps**:
1. Check file size of `.github/copilot-instructions.md`
**Expected Result**: File size > 0 bytes  
**Failure Message**: "FAIL: Spine file is empty"

---

## Automated Test Script

```powershell
# GCP-001 Verification Script
$failed = 0
$passed = 0

# Test file existence
$files = @(
    ".github/copilot-instructions.md",
    ".github/roles/project-owner-assistant.md",
    ".github/roles/program-manager.md",
    ".github/roles/reviewer.md",
    ".github/roles/architect.md",
    ".github/roles/tester.md",
    ".github/roles/developer.md",
    ".github/roles/refactor-expert.md",
    ".github/roles/builder.md",
    ".github/roles/documentor.md",
    ".github/roles/retrospective.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "PASS: $file exists" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "FAIL: $file not found" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`nResults: $passed passed, $failed failed"
if ($failed -gt 0) { exit 1 }
```

---

## Test Execution Plan
1. Developer creates all files
2. Run automated verification script
3. Manual review of spine content for completeness
4. Verify Copilot loads instructions (integration test)
