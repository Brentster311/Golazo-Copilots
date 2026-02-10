# Developer Notes — GCP-0037

## Implementation Summary
Replaced `_get_deployed_version()` (single-file check) with `_get_stale_files()` (per-file check) in `gcp_status.py`.

### New Functions
- `_extract_version(content)` — Extracts version from version comment
- `_get_source_version(package_name, resource_filename)` — Reads source file version via `importlib.resources`
- `_get_stale_files(workspace_root)` — Compares all 11 deployed files against source counterparts

### New Constant
- `_DEPLOYED_TO_SOURCE` — List of (deployed_path, package_name, resource_filename) tuples

### Removed
- `_get_deployed_version()` — Replaced by per-file approach

### Test Changes
- Replaced `TestVersionSync` (5 tests) with `TestPerFileStaleReporting` (10 tests)
- Net gain: +4 tests (156 → 160 total)

## Test Results
160 passed, 0 failed.
