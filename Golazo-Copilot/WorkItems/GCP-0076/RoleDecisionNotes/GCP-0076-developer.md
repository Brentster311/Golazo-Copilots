# GCP-0076 Developer Decision Notes

## Implementation

- Added shared read-only, migration, and ensure helpers for canonical registry resolution.
- Updated bootstrap and work-item creation to create or migrate `WorkItems/capabilities.yaml` without overwriting project data.
- Updated status to use canonical-first, read-only resolution.
- Populated the top-level canonical registry with five current Golazo capability cards.
- Removed obsolete top-level and nested-package legacy registries.
- Migrated the test workspace fixture to `tests/WorkItems/capabilities.yaml` and preserved AgentLoop's independent registry.
- Updated legacy tests and added focused canonical-path, impact, validation, and layout coverage.

## TDD Evidence

- Initial focused run: 6 failed, 1 passed.
- After shared path implementation: 2 failed, 5 passed, isolating registry population and cleanup.
- Final focused suite: 7 passed.
- Registry-aware regression suites: 139 passed.
- Full suite: 551 passed, 3 optional Azure Identity tests skipped.
- Coverage run: 89%; the pre-existing 10 ms timing assertion is instrumentation-sensitive and passed in isolation.
- Repository-wide Ruff: passed after three mechanical import-order fixes.

## Runtime Evidence

- Live list: five capabilities.
- Live validation: all key files exist for all five cards.
- Representative impact: capability registry and release policy directly affected; bootstrap installation transitively affected.
