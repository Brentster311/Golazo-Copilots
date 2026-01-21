# GCP-002: Test Cases

## Test Strategy
- Unit tests using `pytest` with `tempfile` for filesystem isolation
- Tests located in `tests/test_golazo_copilot.py`
- No mocking of standard library — use real temp directories

---

## Unit Tests

### TC-001: find_repo_root — Success Case
**Description**: Find repo root when .git exists in parent directory  
**Preconditions**: Temp directory with `.git/` folder and nested subdirectory  
**Steps**:
1. Create temp dir with `.git/` subfolder
2. Create `subdir/nested/` inside temp dir
3. Call `find_repo_root(subdir/nested)`
**Expected Result**: Returns path to temp dir (the one with `.git/`)

### TC-002: find_repo_root — Not in Git Repo
**Description**: Return None when not in a git repository  
**Preconditions**: Temp directory without `.git/` folder  
**Steps**:
1. Create temp dir (no `.git/`)
2. Call `find_repo_root(temp_dir)`
**Expected Result**: Returns `None`

### TC-003: find_repo_root — At Repo Root
**Description**: Find repo root when already at root  
**Preconditions**: Temp directory with `.git/` folder  
**Steps**:
1. Create temp dir with `.git/` subfolder
2. Call `find_repo_root(temp_dir)`
**Expected Result**: Returns path to temp dir

### TC-004: get_script_directory — Returns Script Location
**Description**: Get directory containing the script  
**Preconditions**: None  
**Steps**:
1. Call `get_script_directory()`
**Expected Result**: Returns `Path` object pointing to directory containing `Golazo_Copilot.py`

### TC-005: ensure_directory — Creates Missing Directory
**Description**: Create directory when it doesn't exist  
**Preconditions**: Temp directory  
**Steps**:
1. Define path to non-existent subdirectory
2. Call `ensure_directory(path)`
**Expected Result**: Directory exists after call

### TC-006: ensure_directory — Handles Existing Directory
**Description**: No error when directory already exists  
**Preconditions**: Temp directory with existing subdirectory  
**Steps**:
1. Create subdirectory
2. Call `ensure_directory(path)` on same path
**Expected Result**: No exception; directory still exists

### TC-007: copy_file — Success Case
**Description**: Copy file to destination  
**Preconditions**: Temp directory with source file  
**Steps**:
1. Create source file with known content
2. Call `copy_file(source, destination)`
**Expected Result**: Destination file exists with same content

### TC-008: copy_file — Overwrites Existing
**Description**: Overwrite existing destination file  
**Preconditions**: Both source and destination files exist with different content  
**Steps**:
1. Create source file with content "new"
2. Create destination file with content "old"
3. Call `copy_file(source, destination)`
**Expected Result**: Destination file contains "new"

---

## Integration Tests

### TC-009: install_golazo — Full Installation
**Description**: Install all Golazo files to target repo  
**Preconditions**: 
- Temp directory initialized as git repo (has `.git/`)
- Source `.github/` directory exists with all files
**Steps**:
1. Create temp git repo
2. Call `install_golazo(temp_repo_path)`
3. Verify all files exist
**Expected Result**: 
- `.github/copilot-instructions.md` exists
- All 10 `.github/roles/*.md` files exist

### TC-010: main — Exit Code 0 on Success
**Description**: CLI returns 0 on successful installation  
**Preconditions**: Current directory is inside a git repo  
**Steps**:
1. Create temp git repo
2. Change to temp repo directory
3. Run `main()`
**Expected Result**: Returns `0`

### TC-011: main — Exit Code 1 When Not in Repo
**Description**: CLI returns 1 when not in git repo  
**Preconditions**: Current directory is not inside a git repo  
**Steps**:
1. Create temp directory (no `.git/`)
2. Change to temp directory
3. Run `main()`
**Expected Result**: Returns `1`

---

## Edge Case Tests

### TC-012: Permission Error Handling
**Description**: Handle permission denied gracefully  
**Preconditions**: Directory without write permission (skip on Windows)  
**Steps**:
1. Create temp git repo
2. Remove write permission from `.github/`
3. Call `install_golazo()`
**Expected Result**: Returns `False`; prints error message; no exception raised

### TC-013: Source Files Missing
**Description**: Handle missing source files gracefully  
**Preconditions**: Script directory without `.github/` folder  
**Steps**:
1. Temporarily rename `.github/` directory
2. Run `main()`
3. Restore `.github/` directory
**Expected Result**: Returns `1`; prints helpful error message

---

## README Validation Tests

### TC-014: README Exists
**Description**: README.md file exists at repo root  
**Preconditions**: None  
**Steps**:
1. Check for `README.md` at repo root
**Expected Result**: File exists

### TC-015: README Contains Required Sections
**Description**: README has all required sections  
**Preconditions**: README.md exists  
**Steps**:
1. Read README.md content
2. Check for section headings
**Expected Result**: Contains:
- "What is Golazo" or equivalent
- All 10 role names
- "WorkItems" artifact structure mention
- "Retrospective" example section

---

## Test Coverage Matrix

| Function | Happy Path | Error Path | Edge Cases |
|----------|------------|------------|------------|
| `find_repo_root()` | TC-001, TC-003 | TC-002 | — |
| `get_script_directory()` | TC-004 | — | — |
| `ensure_directory()` | TC-005 | — | TC-006 |
| `copy_file()` | TC-007 | TC-012 | TC-008 |
| `install_golazo()` | TC-009 | TC-013 | — |
| `main()` | TC-010 | TC-011 | — |
| README | TC-014, TC-015 | — | — |
