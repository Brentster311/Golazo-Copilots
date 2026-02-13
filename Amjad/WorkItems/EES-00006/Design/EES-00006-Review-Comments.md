# EES-00006 — Review Comments

## Major Findings

**MJ-1: FactExtractor constructor change is a contract change**
The design proposes adding kwargs to `FactExtractor.__init__()`. This changes the public API. The existing CLI path (which uses env vars) must continue to work unchanged. Architect should confirm backward compatibility approach.

## Minor Findings

**MN-1: Default API version mismatch**
The design specifies built-in default `2025-12-11`, but the existing code defaults to `2024-12-01-preview`. The settings manager should use the new default, but the CLI should not change its default. Recommend the built-in defaults live only in settings.py, not change fact_extractor.py's fallback.

**MN-2: Source display format**
The design mentions showing "(from config)" / "(from env)" / "(default)" next to each field. Clarify if this is a label or tooltip — recommend a small label to keep the dialog simple.

**MN-3: Validation timing**
Design says validation happens at LLM call time. Consider adding a "Test Connection" button in the dialog, or at minimum validate URL format on save.

---

## Architect Notes

### MJ-1 Resolution: FactExtractor backward compatibility
**Approach:** Add optional kwargs `endpoint=None, deployment=None, api_version=None` to `FactExtractor.__init__()`. When `None`, the existing env-var lookup runs unchanged. The CLI path never passes kwargs, so behavior is identical. The GUI passes effective settings from `SettingsManager`. Backward-compatible additive change — no contract break.

### MN-1 Resolution: Default API version
Built-in defaults in `settings.py` = `2025-12-11`. The `fact_extractor.py` fallback default (`2024-12-01-preview`) is NOT changed — it only applies via CLI when no kwarg and no env var is set.

### MN-2 Resolution: Source display
Small `ttk.Label` next to each entry field showing "(config)", "(env)", or "(default)".

### MN-3 Resolution: Validation
Defer connection testing to V2. Basic URL format check on save (must start with `https://`). Invalid values show warning but still save.

### Capability Impact
- **fact-extraction**: Contract change (additive kwargs). CLI path unaffected.
- **gui**: Additive — new Settings dialog, new settings.py module.
- **cli-orchestration**: Transitively affected but no actual change needed.

### Architectural Notes
- **AN-1:** `SettingsManager` is standalone — no Tkinter or engine dependencies.
- **AN-2:** Settings file at `{data_dir}/settings.yaml`.
- **AN-3:** GUI holds a `settings` dict loaded at startup, passed to `FactExtractor` on each extract call.
