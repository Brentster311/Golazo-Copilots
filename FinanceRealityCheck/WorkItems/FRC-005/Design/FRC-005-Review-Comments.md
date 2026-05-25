# FRC-005 Review Comments

## Domain Expert Guidance
- Expose deterministic startup and health contract to support non-technical validation.
- Keep summary endpoint as capability-focused contract, not dynamic analytics payload.
- Prefer local-only bind defaults (`127.0.0.1`) for safety.

## Quality Assurance Review
- Add endpoint tests for HTTP 200 and deterministic payload fields.
- Verify startup runner accepts host/port args without traceback.
- Ensure README includes exact run command and health verification command.
- Keep all pre-existing planner tests green.

## Architect Notes
- Add explicit `create_app()` boundary in API module to keep server wiring separate from domain logic.
- Keep endpoint responses stable/versioned to protect future UI integration.
- Startup defaults should bind localhost only unless caller overrides.
- Avoid loading real institution connectors at app startup.
