# Test Cases — GCP-0037

## TC1: All files up-to-date → no warning
- Setup: All deployed files have same version as source
- Expected: `version_warning` is None

## TC2: Spine stale, roles current → warning lists spine only
- Setup: `.github/copilot-instructions.md` has v2.100.10, source has v2.101.0, roles match
- Expected: warning mentions `copilot-instructions.md`

## TC3: One role stale → warning lists that role
- Setup: `developer.md` deployed has v2.100.10, source has v2.101.0, all others match
- Expected: warning mentions `developer.md`

## TC4: Multiple files stale → warning lists all
- Setup: 3 files have old versions
- Expected: warning lists all 3 with their version pairs

## TC5: Deployed file missing → no warning for that file
- Setup: `.github/roles/architect.md` doesn't exist
- Expected: not listed as stale (bootstrap issue, not stale issue)

## TC6: Deployed file has no version comment → skipped
- Setup: deployed file exists but has no `<!-- Last Updated... -->` line
- Expected: not listed as stale

## TC7: Source file has no version comment → skipped
- Setup: source package file has no version comment
- Expected: not listed as stale

## TC8: No .github directory → no warning
- Setup: workspace has no `.github/` at all
- Expected: `version_warning` is None

## TC9: _get_stale_files returns correct structure
- Setup: one stale file
- Expected: returns `[{"file": "...", "deployed": "2.100.10", "source": "2.101.0"}]`

## TC10: Warning message format
- Setup: 2 stale files
- Expected: message matches `"2 file(s) are stale: ... Run gcp_bootstrap to update."`
