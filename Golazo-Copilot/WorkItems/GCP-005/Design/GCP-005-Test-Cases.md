# Test Cases: GCP-005 - Distribution Package Creator

## Test Strategy
- Unit tests for new `create_package()` function
- Integration test for `--package` CLI flag
- All tests use temporary directories to avoid side effects

---

## Unit Tests

### TC-GCP005-001: Package creates valid zip file
**Given**: All required source files exist (.github/, README.md, USAGE files)  
**When**: `create_package()` is called  
**Then**: A zip file is created at the specified path

### TC-GCP005-002: Package contains .github/copilot-instructions.md
**Given**: Package is created successfully  
**When**: Zip contents are examined  
**Then**: `.github/copilot-instructions.md` exists in the archive

### TC-GCP005-003: Package contains all role files
**Given**: Package is created successfully  
**When**: Zip contents are examined  
**Then**: All 10 role files exist in `.github/roles/`

### TC-GCP005-004: Package contains README.md
**Given**: Package is created successfully  
**When**: Zip contents are examined  
**Then**: `README.md` exists in the archive root

### TC-GCP005-005: Package contains USAGE-VisualStudio.md
**Given**: Package is created successfully  
**When**: Zip contents are examined  
**Then**: `USAGE-VisualStudio.md` exists in the archive root

### TC-GCP005-006: Package contains USAGE-VSCode.md
**Given**: Package is created successfully  
**When**: Zip contents are examined  
**Then**: `USAGE-VSCode.md` exists in the archive root

### TC-GCP005-007: Package fails when .github/ missing
**Given**: Source `.github/` directory does not exist  
**When**: `create_package()` is called  
**Then**: Function returns False and prints error message

### TC-GCP005-008: Package fails when README.md missing
**Given**: Source `README.md` does not exist  
**When**: `create_package()` is called  
**Then**: Function returns False and prints error message

### TC-GCP005-009: Package fails when USAGE files missing
**Given**: USAGE-VisualStudio.md or USAGE-VSCode.md does not exist  
**When**: `create_package()` is called  
**Then**: Function returns False and prints error message

### TC-GCP005-010: Package overwrites existing zip
**Given**: `GolazoCP-dist.zip` already exists  
**When**: `create_package()` is called  
**Then**: Existing zip is replaced with new one

---

## Integration Tests

### TC-GCP005-011: CLI --package flag creates zip
**Given**: Script is run with `--package` flag  
**When**: Command completes  
**Then**: `GolazoCP-dist.zip` exists in current directory

### TC-GCP005-012: CLI --package returns exit code 0 on success
**Given**: All required files exist  
**When**: `python Golazo_Copilot.py --package` is run  
**Then**: Exit code is 0

### TC-GCP005-013: CLI --package outputs zip path on success
**Given**: All required files exist  
**When**: `python Golazo_Copilot.py --package` is run  
**Then**: Output includes path to created zip file

### TC-GCP005-014: CLI --package returns non-zero on failure
**Given**: Required source files are missing  
**When**: `python Golazo_Copilot.py --package` is run  
**Then**: Exit code is non-zero (1)

### TC-GCP005-015: CLI with no flags maintains existing install behavior
**Given**: Script is run without any flags  
**When**: Command completes  
**Then**: Golazo files are installed to repository (unchanged behavior)

---

## Cross-Platform Tests

### TC-GCP005-016: Zip paths use forward slashes
**Given**: Package is created on Windows  
**When**: Zip contents are examined  
**Then**: All paths use forward slashes (not backslashes)
