# GCP-008 - Test Cases

## Test Strategy

This is a structural refactor of markdown instruction files. Tests verify:
1. File existence and structure
2. Content migration completeness
3. Version consistency
4. Upgrade process integrity

Since this is documentation/instruction refactoring (not code), tests are manual verification steps.

---

## Test Cases

### TC-001: PowerShell Guide File Exists
**Maps to AC**: New file `.github/guides/powershell-terminal.md` exists containing all PowerShell/encoding rules

**Steps**:
1. Verify file exists at `.github/guides/powershell-terminal.md`
2. Verify file starts with `<!-- Golazo Version: 1.1.0 -->`
3. Verify file contains "When to Use" section
4. Verify file contains "CRITICAL" warning about PowerShell encoding
5. Verify file contains `cmd /c` pattern documentation

**Expected**: All verifications pass

---

### TC-002: Golazo Update Guide File Exists
**Maps to AC**: New file `.github/guides/golazo-update.md` exists containing all Golazo update logic

**Steps**:
1. Verify file exists at `.github/guides/golazo-update.md`
2. Verify file starts with `<!-- Golazo Version: 1.1.0 -->`
3. Verify file contains "When to Use" section
4. Verify file contains "When to Check" section
5. Verify file contains "How to Check for Updates" section
6. Verify file contains "Upgrade Process" section
7. Verify file contains "Files Downloaded During Upgrade" list

**Expected**: All verifications pass

---

### TC-003: Spine Reduced and Contains References
**Maps to AC**: Spine is reduced by ~130 lines with references to the new guides

**Steps**:
1. Verify spine version header is `<!-- Golazo Version: 1.1.0 -->`
2. Verify spine does NOT contain "Terminal file writing rules (Windows/PowerShell)" section
3. Verify spine does NOT contain "Golazo Update Check (GCP-007)" section
4. Verify spine contains "Context-Specific Guides" section
5. Verify spine references `.github/guides/powershell-terminal.md`
6. Verify spine references `.github/guides/golazo-update.md`

**Expected**: All verifications pass

---

### TC-004: Version Files Updated
**Maps to AC**: VERSION file updated to 1.1.0, CHANGELOG updated

**Steps**:
1. Verify `Golazo-Copilot/VERSION` contains `1.1.0`
2. Verify `Golazo-Copilot/CHANGELOG.md` contains `## [1.1.0]` entry
3. Verify changelog entry mentions GCP-008

**Expected**: All verifications pass

---

### TC-005: Guide Files Listed in Upgrade Process
**Maps to AC**: (Implicit from Reviewer concern)

**Steps**:
1. In `golazo-update.md`, verify "Files Downloaded During Upgrade" includes:
   - `.github/guides/powershell-terminal.md`
   - `.github/guides/golazo-update.md`
2. Verify upgrade commands include `New-Item -ItemType Directory -Path ".github/guides" -Force`
3. Verify backup commands include guide files with `-ErrorAction SilentlyContinue`

**Expected**: All verifications pass

---

### TC-006: Workflow Behavior Unchanged
**Maps to AC**: All existing Golazo workflow behavior remains unchanged

**Steps**:
1. Start new Golazo session
2. Verify status header format unchanged
3. Verify role sequence unchanged
4. Verify DoR/DoD gates enforced
5. Verify artifact path conventions unchanged

**Expected**: Workflow operates identically to pre-refactor

---

### TC-007: No Content Duplication
**Maps to NFR**: Extraction should be clean cut (no partial duplication)

**Steps**:
1. Verify spine does not contain "PowerShell" in section headers
2. Verify spine does not contain "Update Check" in section headers
3. Verify guides do not duplicate workflow rules (roles, gates, artifacts)

**Expected**: Clean separation; no duplication

---

## Negative Test Cases

### TC-N01: Missing Guide Doesn't Break Workflow
**Steps**:
1. Temporarily rename `.github/guides/powershell-terminal.md`
2. Start Golazo workflow
3. Verify workflow proceeds normally (guide is optional context)

**Expected**: Workflow works; terminal operations lack guidance but don't fail

---

## Test Execution Checklist

| Test ID | Description | Result | Notes |
|---------|-------------|--------|-------|
| TC-001 | PowerShell guide exists | ? | |
| TC-002 | Update guide exists | ? | |
| TC-003 | Spine reduced with refs | ? | |
| TC-004 | Version files updated | ? | |
| TC-005 | Guides in upgrade list | ? | |
| TC-006 | Workflow unchanged | ? | |
| TC-007 | No duplication | ? | |
| TC-N01 | Missing guide resilience | ? | |
