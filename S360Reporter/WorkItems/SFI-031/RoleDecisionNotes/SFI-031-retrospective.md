# SFI-031 — Retrospective

## What Went Well
- **Fast execution**: Small, well-scoped change completed in a single session
- **TDD worked cleanly**: 8/11 tests failed in red phase, all 11 passed after implementation
- **No regressions**: Full suite stayed at same pass/error baseline
- **Atomic write pattern**: Using `mkstemp` + `os.replace` is robust against crash corruption

## What Didn't Go Well
- **Express profile not applied**: Work item was created with `complete` profile before user's preference was captured. No tool exists to change profile after creation.
- **Windows case-insensitivity**: TC-7 initially failed because NTFS treats `brentj_org_tree.json` and `BrentJ_org_tree.json` as the same file. Fixed by checking `os.listdir` names instead of `Path.exists()` with variant casing.

## Action Items
- Consider adding `gcp_update_profile` tool to allow changing profile after creation
- Add a note to test patterns: "On Windows (NTFS), file existence checks are case-insensitive — use `os.listdir` to verify exact filenames"

## Metrics
- Time from start to commit: ~1 session
- New tests: 11
- Regressions: 0
