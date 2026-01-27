# GCP-009: Test Cases

## Work Item
GCP-009 — Clarify Project Root Definition for Cross-IDE Compatibility

## Test Strategy
Documentation-only change. Tests verify content correctness and completeness.

---

## Acceptance Criteria Mapping

| AC # | Acceptance Criterion | Test Case(s) |
|------|---------------------|--------------|
| AC-1 | Spine contains "Project Root Definition" section | TC-01 |
| AC-2 | Visual Studio rule documented | TC-02 |
| AC-3 | VS Code rule documented | TC-03 |
| AC-4 | VS Code fallback with confirmation | TC-04 |
| AC-5 | No `<ProjectName>` tokens remain | TC-05 |
| AC-6 | Path examples (correct/incorrect) | TC-06 |
| AC-7 | Repo Root vs Project Root distinction | TC-07 |

---

## Test Cases

### TC-01: Project Root Definition Section Exists
**Type**: Content validation
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Search for "## Project Root Definition"
**Expected Result**: Section exists
**Failure Message**: "FAIL: Project Root Definition section not found in spine"

### TC-02: Visual Studio Rule Present
**Type**: Content validation
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Search for "Visual Studio" in Project Root section
3. Verify rule mentions project file extensions (`.csproj`, `.pyproj`, etc.)
**Expected Result**: VS rule is documented with file extensions
**Failure Message**: "FAIL: Visual Studio Project Root rule not found or incomplete"

### TC-03: VS Code Rule Present
**Type**: Content validation
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Search for "VS Code" in Project Root section
3. Verify manifest list includes: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`
**Expected Result**: VS Code rule with manifest list is documented
**Failure Message**: "FAIL: VS Code Project Root rule not found or incomplete"

### TC-04: VS Code Fallback Requires Confirmation
**Type**: Content validation
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Search for fallback/confirmation guidance
3. Verify it instructs to ask Project Owner when no manifest found
**Expected Result**: Confirmation requirement is documented
**Failure Message**: "FAIL: VS Code fallback confirmation not documented"

### TC-05: No ProjectName Tokens
**Type**: Negative validation
**Steps**:
1. Search `.github/copilot-instructions.md` for `<ProjectName>`
**Expected Result**: Zero matches
**Failure Message**: "FAIL: Found `<ProjectName>` token in spine at line X"

### TC-06: Path Examples Present
**Type**: Content validation
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Find artifact paths section
3. Verify correct/incorrect examples are shown
**Expected Result**: Examples with ? and ? markers exist
**Failure Message**: "FAIL: Path examples not found or missing correct/incorrect markers"

### TC-07: Repo Root vs Project Root Table
**Type**: Content validation
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Search for "Repo Root" and "Project Root" distinction
3. Verify both terms are defined
**Expected Result**: Clear definitions and distinction documented
**Failure Message**: "FAIL: Repo Root vs Project Root distinction not found"

---

## Automated Verification Script

```powershell
# GCP-009 Verification Script
$spine = Get-Content ".github/copilot-instructions.md" -Raw
$failed = 0; $passed = 0

# TC-01
if ($spine -match "## Project Root Definition") { 
    Write-Host "PASS: TC-01 Project Root Definition section exists" -ForegroundColor Green; $passed++ 
} else { 
    Write-Host "FAIL: TC-01 Project Root Definition section not found" -ForegroundColor Red; $failed++ 
}

# TC-02
if ($spine -match "Visual Studio.*\.csproj" -or $spine -match "\.csproj.*\.pyproj") { 
    Write-Host "PASS: TC-02 Visual Studio rule present" -ForegroundColor Green; $passed++ 
} else { 
    Write-Host "FAIL: TC-02 Visual Studio rule not found" -ForegroundColor Red; $failed++ 
}

# TC-03
if ($spine -match "VS Code" -and $spine -match "package\.json") { 
    Write-Host "PASS: TC-03 VS Code rule present" -ForegroundColor Green; $passed++ 
} else { 
    Write-Host "FAIL: TC-03 VS Code rule not found" -ForegroundColor Red; $failed++ 
}

# TC-05
if ($spine -notmatch "<ProjectName>") { 
    Write-Host "PASS: TC-05 No ProjectName tokens" -ForegroundColor Green; $passed++ 
} else { 
    Write-Host "FAIL: TC-05 Found ProjectName token" -ForegroundColor Red; $failed++ 
}

Write-Host "`nResults: $passed passed, $failed failed"
```

---

## Manual Integration Test

### Test: New Work Item Creation
**Preconditions**: Golazo spine updated with GCP-009 changes
**Steps**:
1. Start a new Copilot chat session
2. Say "Create a new work item GCP-TEST"
3. Observe where Copilot attempts to create files
**Expected Result**: Files created in Project Root (next to `.pyproj` in VS, or identified manifest in VS Code)
**Pass Criteria**: No manual path correction needed
