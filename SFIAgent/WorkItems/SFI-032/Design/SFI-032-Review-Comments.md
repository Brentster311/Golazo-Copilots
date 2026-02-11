# SFI-032 — Review Comments

## Design Review
- Clear and well-scoped refactor. No new behavior, just moving cache location.
- **APPROVED** — no blocking issues.

## Architect Notes
- Cache methods as instance methods is correct (need `self.config`).
- `config.cache_enabled` flag respected — good.
- No security/privacy concerns beyond SFI-031 (same data cached, different directory).
- **APPROVED**.
