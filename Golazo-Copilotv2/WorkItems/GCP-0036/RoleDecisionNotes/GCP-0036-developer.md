# GCP-0036 — Developer Role Notes

## Changes Made

### Production Code
1. **gcp_status.py**: Updated `_VERSION_PATTERN` regex from `<!-- Golazo Copilot Version: -->` to `<!-- Last Updated in Golazo Copilot Version: -->`
2. **gcp_bootstrap.py**: Removed dynamic `re.sub` version stamping in `_get_default_instructions()`. Content is now returned as-is from source. Fallback string also updated.
3. **roles/loader.py**: Removed dynamic version stamping from `_update_version_comment()` — now a pass-through. Removed unused `re` and `__version__` imports.
4. **bootstrap-instructions.md**: Updated version comment to new format
5. **All 9 role source files**: Updated from `<!-- Golazo Version: X.Y.Z -->` to `<!-- Last Updated in Golazo Copilot Version: 2.100.10 -->` (also bumped stale versions to 2.100.10)
6. **All 10 deployed .github/ copies**: Same format change

### Test Code
7. **test_gcp_status.py**: Updated 5 version comment strings to new format
8. **test_gcp_bootstrap.py**: Updated 2 assertion strings to new format

## Verification
- 137 tests pass
- Grep for old format across source and .github returns zero matches
