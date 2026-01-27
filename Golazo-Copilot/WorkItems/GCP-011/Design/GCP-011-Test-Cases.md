# GCP-011: Test Cases

## Acceptance Criteria Mapping

| AC # | Criterion | Test |
|------|-----------|------|
| AC-1 | Each role has Entry conditions | TC-01 |
| AC-2-11 | Correct artifacts per role | TC-02 |
| AC-12 | VERSION updated | TC-03 |
| AC-13 | CHANGELOG updated | TC-04 |

## Test Cases

### TC-01: Entry Conditions Section Exists
For each role file in `.github/roles/*.md`, verify "Entry conditions" or "## Entry conditions" exists.

### TC-02: Correct Artifacts Per Role
| Role | Expected Pattern |
|------|-----------------|
| project-owner-assistant | "None" or "first role" |
| program-manager | "User Story" |
| reviewer | "Design Doc" |
| architect | "Design Doc" |
| tester | "Review Comments" |
| developer | "DoR" or all 4 artifacts |
| refactor-expert | "tests" |
| builder | "Tests exist" |
| documentor | "Build passes" |
| retrospective | "complete" or "blocked" |

### TC-03: VERSION = 1.1.4
### TC-04: CHANGELOG contains "GCP-011"

## Automated Verification
```powershell
$roles = Get-ChildItem ".github/roles/*.md"
foreach ($role in $roles) {
    $content = Get-Content $role.FullName -Raw
    if ($content -match "Entry conditions") { 
        Write-Host "PASS: $($role.Name)" -ForegroundColor Green 
    } else { 
        Write-Host "FAIL: $($role.Name)" -ForegroundColor Red 
    }
}
```
