# GCP-010: Test Cases

## Work Item
GCP-010 — Role Transition Announcement

## Acceptance Criteria Mapping

| AC # | Criterion | Test Case |
|------|-----------|-----------|
| AC-1 | Spine contains subsection | TC-01 |
| AC-2 | Format specified | TC-02 |
| AC-3 | Reason required | TC-02 |
| AC-4 | Artifact required | TC-02 |
| AC-5 | VERSION updated | TC-03 |
| AC-6 | CHANGELOG updated | TC-04 |

---

## Test Cases

### TC-01: Subsection Exists
**Type**: Content validation
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Search for "Role Transition Announcement"
**Expected**: Subsection exists in Operating mode section
**Failure**: "FAIL: Role Transition Announcement section not found"

### TC-02: Format Specified
**Type**: Content validation
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Verify section contains:
   - "Transitioning from [Role A] to [Role B]"
   - "Reason for transition"
   - "artifact/output was produced"
**Expected**: All three elements present
**Failure**: "FAIL: Required format elements missing"

### TC-03: VERSION Updated
**Type**: Content validation
**Steps**:
1. Read VERSION file
**Expected**: `1.1.3`
**Failure**: "FAIL: VERSION not updated to 1.1.3"

### TC-04: CHANGELOG Updated
**Type**: Content validation
**Steps**:
1. Search CHANGELOG.md for "GCP-010"
**Expected**: Entry exists
**Failure**: "FAIL: GCP-010 not in CHANGELOG"

---

## Automated Verification

```powershell
$spine = Get-Content ".github/copilot-instructions.md" -Raw
if ($spine -match "Role Transition Announcement") { Write-Host "TC-01: PASS" } else { Write-Host "TC-01: FAIL" }
if ($spine -match "Transitioning from" -and $spine -match "Reason for transition") { Write-Host "TC-02: PASS" } else { Write-Host "TC-02: FAIL" }
if ((Get-Content "VERSION") -eq "1.1.3") { Write-Host "TC-03: PASS" } else { Write-Host "TC-03: FAIL" }
if ((Get-Content "CHANGELOG.md" -Raw) -match "GCP-010") { Write-Host "TC-04: PASS" } else { Write-Host "TC-04: FAIL" }
```
