# GCP-006: Test Cases

**Work Item**: GCP-006 - Add Versioning to Golazo Instruction Files  
**Date**: 2026-01-20

---

## Test Case Mapping to Acceptance Criteria

| Acceptance Criteria | Test Case(s) |
|---------------------|--------------|
| Spine contains version header | TC-001, TC-002 |
| Role files contain version comment | TC-003, TC-004 |
| VERSION file exists at repo root | TC-005, TC-006 |
| CHANGELOG.md exists at repo root | TC-007, TC-008 |
| `--package` includes VERSION and CHANGELOG | TC-009, TC-010 |
| Version format follows semver | TC-002, TC-006 |

---

## Test Cases

### TC-001: Spine file contains version comment
**Type**: Happy path  
**Preconditions**: `.github/copilot-instructions.md` exists  
**Steps**:
1. Read first line of `.github/copilot-instructions.md`
2. Check line matches pattern `<!-- Golazo Version: X.Y.Z -->`

**Expected**: First line is `<!-- Golazo Version: 1.0.0 -->`  
**Failure message**: "Spine file missing version comment on line 1"

---

### TC-002: Spine version is valid semver
**Type**: Validation  
**Preconditions**: TC-001 passes  
**Steps**:
1. Extract version string from spine comment
2. Validate against semver regex `^\d+\.\d+\.\d+$`

**Expected**: Version matches semver pattern  
**Failure message**: "Spine version '{version}' is not valid semver"

---

### TC-003: All role files contain version comment
**Type**: Happy path  
**Preconditions**: All 10 role files exist in `.github/roles/`  
**Steps**:
1. For each file in `.github/roles/*.md`:
   - Read first line
   - Verify matches `<!-- Golazo Version: X.Y.Z -->`

**Expected**: All 10 files have version comment on line 1  
**Failure message**: "Role file '{filename}' missing version comment"

**Role files to check**:
- project-owner-assistant.md
- program-manager.md
- reviewer.md
- architect.md
- tester.md
- developer.md
- refactor-expert.md
- builder.md
- documentor.md
- retrospective.md

---

### TC-004: All role file versions match spine version
**Type**: Consistency  
**Preconditions**: TC-001 and TC-003 pass  
**Steps**:
1. Extract version from spine file
2. For each role file, extract version
3. Compare all versions

**Expected**: All versions are identical  
**Failure message**: "Version mismatch: spine={spine_ver}, {filename}={file_ver}"

---

### TC-005: VERSION file exists at repo root
**Type**: Happy path  
**Preconditions**: None  
**Steps**:
1. Check file exists at `./VERSION`
2. Read contents

**Expected**: File exists and is readable  
**Failure message**: "VERSION file not found at repository root"

---

### TC-006: VERSION file contains valid semver
**Type**: Validation  
**Preconditions**: TC-005 passes  
**Steps**:
1. Read VERSION file content
2. Strip whitespace
3. Validate against `^\d+\.\d+\.\d+$`

**Expected**: Content is valid semver (e.g., "1.0.0")  
**Failure message**: "VERSION file contains invalid version: '{content}'"

---

### TC-007: CHANGELOG.md exists at repo root
**Type**: Happy path  
**Preconditions**: None  
**Steps**:
1. Check file exists at `./CHANGELOG.md`
2. Read contents

**Expected**: File exists and is readable  
**Failure message**: "CHANGELOG.md not found at repository root"

---

### TC-008: CHANGELOG.md contains current version entry
**Type**: Validation  
**Preconditions**: TC-005 and TC-007 pass  
**Steps**:
1. Read VERSION file to get current version
2. Search CHANGELOG.md for `## [X.Y.Z]` heading

**Expected**: CHANGELOG contains entry for current version  
**Failure message**: "CHANGELOG.md missing entry for version {version}"

---

### TC-009: Package includes VERSION file
**Type**: Integration  
**Preconditions**: `Golazo_Copilot.py` exists  
**Steps**:
1. Run `python Golazo_Copilot.py --package`
2. Open generated `GolazoCP-dist.zip`
3. Check for `VERSION` in archive

**Expected**: VERSION file present in zip  
**Failure message**: "GolazoCP-dist.zip does not contain VERSION file"

---

### TC-010: Package includes CHANGELOG.md
**Type**: Integration  
**Preconditions**: `Golazo_Copilot.py` exists  
**Steps**:
1. Run `python Golazo_Copilot.py --package`
2. Open generated `GolazoCP-dist.zip`
3. Check for `CHANGELOG.md` in archive

**Expected**: CHANGELOG.md file present in zip  
**Failure message**: "GolazoCP-dist.zip does not contain CHANGELOG.md"

---

## Edge Cases

### TC-011: VERSION file has trailing newline
**Type**: Edge case  
**Steps**:
1. Create VERSION file with content "1.0.0\n"
2. Run version extraction logic

**Expected**: Version parsed correctly as "1.0.0"  
**Failure message**: "Trailing newline caused version parse failure"

---

### TC-012: Empty VERSION file
**Type**: Negative  
**Steps**:
1. Create empty VERSION file
2. Attempt to read version

**Expected**: Clear error message, not crash  
**Failure message**: "Empty VERSION file not handled gracefully"

---

## Automated Test Implementation

Tests will be added to `tests/test_golazo_copilot.py`:
- `test_version_file_exists()`
- `test_version_file_valid_semver()`
- `test_changelog_exists()`
- `test_spine_has_version_comment()`
- `test_role_files_have_version_comments()`
- `test_all_versions_match()`
- `test_package_includes_version()`
- `test_package_includes_changelog()`
