# EES-00006 — Capability Impact

## Impact Analysis Summary

3 files → 3 capabilities affected

| Capability | Impact | Contract Change |
|------------|--------|----------------|
| fact-extraction | Direct — additive kwargs to `FactExtractor.__init__()` | Backward compatible |
| gui | Direct — new settings.py module, SettingsDialog in app.py | Additive |
| cli-orchestration | Transitive — depends on fact-extraction | No change needed |
