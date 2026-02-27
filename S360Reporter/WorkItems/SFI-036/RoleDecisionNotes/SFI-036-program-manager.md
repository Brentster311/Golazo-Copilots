# SFI-036 — Program Manager Decision Notes

## Key Decisions

1. **Single-phase approach** — No staged rollout needed; this is an internal refactoring with no user-facing impact.
2. **Verify-first strategy** — All 40 symbols confirmed present in decomposed modules before any changes begin. This eliminates the #1 risk.
3. **Patch paths** — Tests using `mocker.patch('sfi_reporter.tk_app.write_cache')` must target `sfi_reporter.services.write_cache` (where `write_cache` is imported) not `sfi_reporter.cache.write_cache`, to correctly intercept the reference used by production code.
4. **BUILD_MANIFEST.md** — Include as in-scope since it documents the PyInstaller command.
