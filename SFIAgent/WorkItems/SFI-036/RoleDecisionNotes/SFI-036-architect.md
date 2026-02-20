# SFI-036 — Architect Decision Notes

1. **Approved as-is** — The refactoring completes the SFI-030 decomposition with no architectural risk.
2. **Circular import watch** — Flag `query_builder.py` → `dialogs.py` retarget as potential circular import. Verify during implementation.
3. **No capability impact** — This is a pure code organization change; no capability contracts are affected.
