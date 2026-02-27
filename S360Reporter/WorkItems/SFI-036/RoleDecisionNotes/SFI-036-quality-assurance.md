# SFI-036 — Quality Assurance Decision Notes

1. **No new tests needed** — This is a pure refactoring. Existing tests validate behavior; we just need them to pass with updated import paths.
2. **Grep verification** — Added TC-3 and TC-4 to confirm no stale `tk_app` references remain after cleanup.
3. **Patch target correctness** — Flagged in review comments that `mocker.patch` targets must follow Python's import binding rules (patch where used, not where defined).
