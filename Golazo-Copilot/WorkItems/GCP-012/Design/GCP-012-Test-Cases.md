# GCP-012: Test Cases

## Acceptance Criteria Mapping

| AC # | Criterion | Test |
|------|-----------|------|
| AC-1 | Guide file exists | TC-01 |
| AC-2 | Version header | TC-02 |
| AC-3 | "When to Use" section | TC-03 |
| AC-4 | 4-step process | TC-04 |
| AC-5 | Fail-Fast Rule | TC-05 |
| AC-6 | Spine references guide | TC-06 |
| AC-7 | VERSION = 1.1.5 | TC-07 |
| AC-8 | CHANGELOG updated | TC-08 |

## Automated Verification
```powershell
# TC-01
if (Test-Path ".github/guides/PatternProposals.md") { Write-Host "TC-01: PASS" } else { Write-Host "TC-01: FAIL" }

# TC-02-05
$guide = Get-Content ".github/guides/PatternProposals.md" -Raw
if ($guide -match "Golazo Version: 1.1.5") { Write-Host "TC-02: PASS" } else { Write-Host "TC-02: FAIL" }
if ($guide -match "When to Use") { Write-Host "TC-03: PASS" } else { Write-Host "TC-03: FAIL" }
if ($guide -match "SEARCH" -and $guide -match "COUNT" -and $guide -match "PRESENT" -and $guide -match "APPROVAL") { Write-Host "TC-04: PASS" } else { Write-Host "TC-04: FAIL" }
if ($guide -match "Fail-Fast") { Write-Host "TC-05: PASS" } else { Write-Host "TC-05: FAIL" }

# TC-06
$spine = Get-Content ".github/copilot-instructions.md" -Raw
if ($spine -match "PatternProposals.md") { Write-Host "TC-06: PASS" } else { Write-Host "TC-06: FAIL" }

# TC-07-08
if ((Get-Content "VERSION") -eq "1.1.5") { Write-Host "TC-07: PASS" } else { Write-Host "TC-07: FAIL" }
if ((Get-Content "CHANGELOG.md" -Raw) -match "GCP-012") { Write-Host "TC-08: PASS" } else { Write-Host "TC-08: FAIL" }
```
