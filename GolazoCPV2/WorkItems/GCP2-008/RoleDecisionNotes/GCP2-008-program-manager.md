# GCP2-008: Program Manager Decision Notes

**Work Item**: GCP2-008 - Configuration System  
**Role**: Program Manager  
**Date**: 2026-01-31

---

## Decisions Made

1. **YAML over JSON/TOML**: YAML supports comments, familiar to devs.

2. **Config file locations**: `golazo.yaml` first, then `.golazo/config.yaml`.

3. **Defaults match current behavior**: No breaking changes.

4. **PyYAML dependency**: Standard, widely used.

5. **Config passed to constructors**: Not global state.

---

## Open Questions for Architect

- Should config be immutable after load?
- Config validation: strict or lenient?
- Should `consent.py` also receive config, or read from machine?
