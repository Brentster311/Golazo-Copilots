# GCP-0036 — Retrospective

## What went well
- Express profile was the right choice — straightforward format change completed efficiently
- Comprehensive grep verification confirmed zero old-format remnants
- All 137 tests passed on first run after changes

## What didn't go well
- Three separate dynamic stamping locations (bootstrap, loader, status) suggests this concern was scattered. Now that it's static, the concern is properly consolidated in the source files themselves.
- **Critical miss: stale reporting algorithm not updated.** The `_get_deployed_version()` function in `gcp_status.py` still only checks one file (`copilot-instructions.md`) against the package `__version__`. With static per-file version comments, the stale check should now compare each deployed `.github/` file's version comment against its source counterpart. This was not caught during QA, architect, or developer roles.

## Root Cause Analysis
The miss happened because GCP-0036 was scoped narrowly as a "format change" — replace old comment format with new. The roles treated it as a string substitution task and verified the format change was complete (grep for zero old-format matches). But changing from dynamic to static stamping **changed the semantic contract**: previously, the package version was the single source of truth; now, each source file's embedded version is its own truth. The stale-check algorithm depends on that contract, and nobody surfaced that the contract had changed.

### Why did QA/Architect miss this?
1. **No capability inventory.** GCP has no structured index of "features that depend on version comments." The roles relied on ad-hoc reasoning ("what else touches versions?") rather than a checklist.
2. **Grep-only verification.** The test strategy verified format correctness (old format gone, new format present) but not behavioral correctness (does the stale detection still work correctly under the new contract?).
3. **Express profile reduced scrutiny.** The express profile skipped deeper architectural analysis that might have caught the contract change.

## Action items
- **GCP-0037**: Fix stale reporting to compare each deployed MD file's version against its source file's version (not package version)
- **Process improvement**: Consider creating a **Capability Index** — a structured inventory of GCP features (e.g., "version sync check," "output validation," "role progress") with their key code locations and dependencies. Roles could reference this to avoid missing downstream impacts when changing shared contracts.
- Consider removing `_update_version_comment()` entirely in a future cleanup — it's now a no-op pass-through

## Metrics
- 38 files changed, 245 insertions, 44 deletions
- Zero old-format matches remaining
- 1 behavioral regression missed (stale reporting)
