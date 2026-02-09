# GCP-0032 Test Cases

## TC1: Version sync detection

### TC1.1: Matching version — no warning
- **Precondition**: `.github/copilot-instructions.md` contains `<!-- Golazo Copilot Version: {current} -->`
- **Action**: Call `gcp_status()`
- **Expected**: `version_warning` is None
- **Failure**: "Warning shown when versions match"

### TC1.2: Mismatched version — warning present
- **Precondition**: `.github/copilot-instructions.md` contains `<!-- Golazo Copilot Version: 1.0.0 -->`
- **Action**: Call `gcp_status()`
- **Expected**: `version_warning` contains "1.0.0", current version, and "gcp_bootstrap"
- **Failure**: "No warning when versions mismatch"

### TC1.3: File missing — no warning
- **Precondition**: No `.github/copilot-instructions.md`
- **Action**: Call `gcp_status()`
- **Expected**: `version_warning` is None
- **Failure**: "Warning shown when file doesn't exist"

### TC1.4: File without version comment — no warning
- **Precondition**: `.github/copilot-instructions.md` exists but has no version comment
- **Action**: Call `gcp_status()`
- **Expected**: `version_warning` is None
- **Failure**: "Warning shown when file has no version"

## TC2: Server rendering

### TC2.1: Warning rendered in status output
- **Precondition**: Version mismatch detected
- **Action**: Format status output
- **Expected**: `[WARN]` line appears in output with version info
- **Failure**: "Warning not rendered in formatted output"

### TC2.2: No warning line when versions match
- **Precondition**: Versions match
- **Action**: Format status output
- **Expected**: No `[WARN]` stale line in output
- **Failure**: "Stale warning line present when it shouldn't be"
