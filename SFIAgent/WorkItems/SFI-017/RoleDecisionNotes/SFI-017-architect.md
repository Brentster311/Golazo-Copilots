# SFI-017 — Architect Notes

## Review
- Separate module `query_builder.py` is the right call — keeps tk_app.py from growing further
- Pure `evaluate_clauses()` function is well-isolated and testable
- Cache in same %TEMP%/sfireporter/ directory is consistent with existing patterns
- No new dependencies, no new network calls — low risk

## No new User Stories needed
Design is clean, no architectural changes required.
