# Design Doc — GCP-0037: Per-File Stale Version Reporting

## Summary
Replace the single-version stale check in `gcp_status` (which compares `.github/copilot-instructions.md` version against `__version__`) with a per-file comparison that checks each deployed file against its package source counterpart.

## Problem Statement
After GCP-0036 made version comments static, the stale check compares the spine's version against `__version__`, but individual role files can be at different versions. A user might have an up-to-date spine but stale role files (or vice versa). The current check gives a misleading "stale" or "not stale" answer when reality is mixed.

## Proposed Approach

### Changes to `gcp_status.py`

**Replace** `_get_deployed_version()` with `_get_stale_files()`:

```python
def _get_stale_files(workspace_root: Path) -> list[dict]:
    """Compare each deployed file's version against its source counterpart.
    
    Returns list of {"file": str, "deployed": str, "source": str} for stale files.
    """
```

**File mapping** (deployed → source):
| Deployed | Source (package) |
|----------|-----------------|
| `.github/copilot-instructions.md` | `golazo_copilot/bootstrap-instructions.md` |
| `.github/roles/{role}.md` | `golazo_copilot/roles/defaults/{role}.md` |

**Algorithm** for each pair:
1. Read deployed file, extract version from `<!-- Last Updated in Golazo Copilot Version: X.Y.Z -->`
2. Read source file (via `importlib.resources`), extract version
3. If both have versions and they differ, add to stale list
4. If either file is missing or has no version comment, skip (not stale)

**Replace** the single `version_warning` string with list-based reporting:
- If stale_files is empty → `version_warning = None`
- If stale_files is non-empty → format as: `"N file(s) are stale: file1 (v1 → v2), file2 (v3 → v4). Run gcp_bootstrap to update."`

### Changes to `server.py`
- Formatter already handles `version_warning` as a string — no changes needed (the string just changes format)

### No changes to
- `gcp_bootstrap.py` (already handles deployment)
- `roles/loader.py` (already loads from package)
- `server.py` formatter (already renders `version_warning`)

## Files Changed
| File | Change |
|------|--------|
| `tools/gcp_status.py` | Replace `_get_deployed_version` with `_get_stale_files`, update warning format |

## Test Strategy
- Unit test: `_get_stale_files` with mixed version scenarios
- Unit test: all files matching → no warning
- Unit test: some files stale → warning lists specific files
- Unit test: missing deployed files → no warning  
- Unit test: files without version comments → skipped
- Integration: `gcp_status` output contains per-file stale info

## Risks
- **Low**: Changing `version_warning` format may break consumers that parse the string (mitigated: only GCP's own `server.py` consumes it, and it just passes through)

## Dependencies
- GCP-0036 (version comment format) — done
