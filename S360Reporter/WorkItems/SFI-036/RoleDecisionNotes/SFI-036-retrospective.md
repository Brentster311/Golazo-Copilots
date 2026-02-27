# SFI-036 — Retrospective

## What went well

- **Thorough verification before changes** — Confirming all 40 symbols existed in decomposed modules before any edits prevented surprises.
- **Automated migration** — Using a Python script to handle 120+ import retargets was efficient and avoided manual transcription errors.
- **Quick feedback loop** — Running tests immediately after changes caught the 2 test expectation mismatches fast.
- **Net -2,658 lines** — Significant codebase simplification in a single work item.

## What didn't go well

- **Multi-line import regex edge case** — The migration script's multi-line import handler treated comma-separated names in parenthesized imports as a single name, causing 3 `OrgAncestry` imports to land in the wrong module. Required manual fix.
- **Pre-existing test drift** — The `test_tk_app.py` tests for "Unknown Owner" / "No Owner" expected the old monolith's behavior, not `services.py`'s `"No Owner in ST"`. This masked a behavioral difference between the two codebases.
- **Live test failures** — 3 pre-existing live test failures exist in `test_sfi_026_live.py` due to data drift (brentj now shows as manager). Not caused by this WI but noticed during verification.

## Action items

1. **Fix live test expectations** — Create a work item to update `test_sfi_026_live.py` test expectations for brentj's current org status.
2. **Rename `test_tk_app.py`** — Consider renaming to `test_core.py` or `test_services_formatters.py` since it no longer tests a file called `tk_app.py`.

## Metrics

- Lines removed: 3,288
- Lines added: 630 (mostly work item docs)
- Net production code delta: ~-3,100 lines
- Test pass rate: 314/314 (non-live) = 100%
