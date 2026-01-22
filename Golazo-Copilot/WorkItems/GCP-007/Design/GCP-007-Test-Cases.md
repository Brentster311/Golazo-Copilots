# GCP-007: Test Cases

**Work Item**: GCP-007 - Golazo Copilot Update Detection and Upgrade  
**Date**: 2026-01-20

---

## Test Case Mapping to Acceptance Criteria

| Acceptance Criteria | Test Case(s) |
|---------------------|--------------|
| Instructions include update check section | TC-101 |
| Fetch remote VERSION from GitHub | TC-102, TC-103 |
| Extract local version from spine | TC-104 |
| Display version comparison | TC-105 |
| Ask user for confirmation | TC-106 |
| Backup before upgrade | TC-107, TC-108 |
| Download updated files | TC-109, TC-110 |
| Report success/failure | TC-111, TC-112 |

---

## Test Cases

### TC-101: Spine contains update check instructions
**Type**: Happy path  
**Preconditions**: `.github/copilot-instructions.md` exists  
**Steps**:
1. Read spine file
2. Search for "## Golazo Update Check" section

**Expected**: Section exists with check instructions  
**Failure message**: "Spine file missing update check section"

---

### TC-102: Fetch remote VERSION successfully
**Type**: Integration  
**Preconditions**: Internet access available  
**Steps**:
1. Run PowerShell command:
   ```powershell
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Brentster311/Golazo-Copilots/main/VERSION" -UseBasicParsing
   ```
2. Check response status

**Expected**: HTTP 200, content is valid semver  
**Failure message**: "Failed to fetch remote VERSION: {error}"

---

### TC-103: Handle network timeout gracefully
**Type**: Negative  
**Preconditions**: None  
**Steps**:
1. Simulate network timeout (invalid URL or firewall)
2. Observe Copilot behavior

**Expected**: Message "Could not check for updates. Continuing normally."  
**Failure message**: "Network timeout caused crash or blocking behavior"

---

### TC-104: Extract local version from spine comment
**Type**: Happy path  
**Preconditions**: Spine has version comment (GCP-006 complete)  
**Steps**:
1. Read first line of spine
2. Extract version using regex `<!-- Golazo Version: (\d+\.\d+\.\d+) -->`

**Expected**: Version extracted (e.g., "1.0.0")  
**Failure message**: "Could not extract version from spine file"

---

### TC-105: Detect newer version available
**Type**: Happy path  
**Preconditions**: Local version < remote version  
**Steps**:
1. Local version = 1.0.0
2. Remote version = 1.1.0
3. Compare versions

**Expected**: "Golazo v1.0.0 installed. v1.1.0 available."  
**Failure message**: "Version comparison failed to detect upgrade"

---

### TC-106: User declines upgrade
**Type**: Happy path  
**Preconditions**: Upgrade available, user prompted  
**Steps**:
1. User responds "no" to upgrade prompt
2. Observe behavior

**Expected**: No files modified, normal operation continues  
**Failure message**: "User declined but files were modified"

---

### TC-107: Backup created before upgrade
**Type**: Happy path  
**Preconditions**: User confirms upgrade  
**Steps**:
1. User responds "yes" to upgrade
2. Check `.github/backup/` directory

**Expected**: Timestamped subdirectory created with original files  
**Failure message**: "Backup not created before upgrade"

---

### TC-108: Backup contains all original files
**Type**: Validation  
**Preconditions**: TC-107 passes  
**Steps**:
1. List files in backup directory
2. Compare to expected file list (1 spine + 10 roles)

**Expected**: All 11 files present in backup  
**Failure message**: "Backup missing files: {missing_files}"

---

### TC-109: All files downloaded successfully
**Type**: Integration  
**Preconditions**: User confirms upgrade, backup complete  
**Steps**:
1. Download all 11 files from GitHub
2. Verify each file exists and is non-empty

**Expected**: All 11 files downloaded and saved  
**Failure message**: "Download failed for: {filename}"

---

### TC-110: Partial download triggers abort
**Type**: Negative  
**Preconditions**: Simulated download failure mid-process  
**Steps**:
1. Download 5 files successfully
2. Simulate failure on file 6
3. Observe behavior

**Expected**: Upgrade aborted, original files restored from backup  
**Failure message**: "Partial download left system in inconsistent state"

---

### TC-111: Success message after upgrade
**Type**: Happy path  
**Preconditions**: All downloads successful  
**Steps**:
1. Complete upgrade process
2. Observe output

**Expected**: "? Golazo upgraded to v{new_version}"  
**Failure message**: "Success message not displayed after upgrade"

---

### TC-112: Failure message on error
**Type**: Negative  
**Preconditions**: Download fails  
**Steps**:
1. Simulate download failure
2. Observe output

**Expected**: "? Upgrade failed: {reason}. Original files preserved in backup."  
**Failure message**: "Error message not displayed on failure"

---

### TC-113: Timestamp file created after check
**Type**: Happy path  
**Preconditions**: Version check performed  
**Steps**:
1. Perform version check
2. Check for `.github/.golazo-update-check`

**Expected**: File exists with ISO 8601 timestamp  
**Failure message**: "Timestamp file not created after check"

---

### TC-114: Skip check if within 24 hours
**Type**: Happy path  
**Preconditions**: Timestamp file exists with recent time  
**Steps**:
1. Set timestamp to 1 hour ago
2. Start new session
3. Observe if check is performed

**Expected**: Check skipped, no network request  
**Failure message**: "Check performed despite recent timestamp"

---

### TC-115: Check if timestamp older than 24 hours
**Type**: Happy path  
**Preconditions**: Timestamp file exists with old time  
**Steps**:
1. Set timestamp to 25 hours ago
2. Start new session
3. Observe if check is performed

**Expected**: Check performed  
**Failure message**: "Check not performed despite stale timestamp"

---

## Edge Cases

### TC-116: Invalid remote VERSION format
**Type**: Edge case  
**Steps**:
1. Remote VERSION contains "invalid-version"
2. Perform check

**Expected**: Treat as "up to date", no error shown  
**Failure message**: "Invalid remote version caused crash"

---

### TC-117: Local version newer than remote
**Type**: Edge case  
**Steps**:
1. Local = 2.0.0, Remote = 1.0.0
2. Perform check

**Expected**: "Golazo is up to date (v2.0.0)"  
**Failure message**: "Offered downgrade instead of showing up to date"

---

### TC-118: No write permission to .github/
**Type**: Negative  
**Steps**:
1. Make .github/ read-only
2. Attempt upgrade

**Expected**: Error message about permissions, no partial changes  
**Failure message**: "Upgrade attempted without write permission"

---

## Manual Test Cases (Copilot Behavior)

### TC-M01: Copilot shows version comparison correctly
**Type**: Manual  
**Steps**:
1. Install old version of Golazo
2. Ensure remote has newer version
3. Start Copilot session
4. Observe first Golazo Status output

**Expected**: Version comparison message appears  
**Verification**: Visual inspection

---

### TC-M02: Copilot displays changelog before upgrade
**Type**: Manual  
**Steps**:
1. New version available
2. User considers upgrade
3. Copilot fetches and displays CHANGELOG entries

**Expected**: Only changes between current and target version shown  
**Verification**: Visual inspection

---

## Test Implementation Notes

- Most tests require simulation of Copilot behavior (manual)
- TC-102, TC-103 can be automated as PowerShell scripts
- TC-107, TC-108, TC-109 require file system inspection
- Consider creating test harness for version comparison logic
