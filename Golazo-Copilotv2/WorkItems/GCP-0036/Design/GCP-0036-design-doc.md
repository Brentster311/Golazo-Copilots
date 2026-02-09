# GCP-0036 Design Document

## Summary
Replace dynamic version stamping in bootstrap with static `<!-- Last Updated in Golazo Copilot Version: X.Y.Z -->` comments across all instruction/role files.

## Problem
`gcp_bootstrap` dynamically overwrites the version comment at deploy time, making the version reflect _when deployed_ rather than _when content last changed_. This is misleading — a file at v2.100.10 might have content unchanged since v2.11.2.

## Approach

### Files to modify (source):
1. **`gcp_bootstrap.py`** — Remove the `re.sub` that stamps `__version__` into instructions
2. **`gcp_status.py`** — Update `_VERSION_PATTERN` regex to match `<!-- Last Updated in Golazo Copilot Version: ([\d.]+) -->`
3. **`bootstrap-instructions.md`** — Change comment format
4. **All 10 role default files** — Change `<!-- Golazo Version: X.Y.Z -->` to `<!-- Last Updated in Golazo Copilot Version: X.Y.Z -->`
5. **Tests** — Update any assertions matching the old format

### What changes:
- Version comment becomes `<!-- Last Updated in Golazo Copilot Version: X.Y.Z -->`
- Bootstrap copies files verbatim (no regex replacement)
- Version sync warning still works but compares "last updated" vs running version

## Test Strategy
- Existing tests updated for new format
- Verify `_get_deployed_version()` reads new format
- Verify bootstrap no longer modifies version comment
