# GCP-0075 Retrospective

## What Went Well

- Profile-aware rework caught the ownership flaw before production instruction changes began.
- Focused policy tests established a clear red-green cycle and protected packaged plus bootstrap-generated roles.
- Capability impact and registry validation were both consulted.
- Builder completed versioning, changelog, build, commit, and push in one forward-only role.

## What Didn't Go Well

- The initial design assigned mandatory release metadata to Documenter without checking that Express omits that role.
- Legacy GCP-0066 tests encoded ownership rather than the underlying version-before-changelog invariant, so they required migration.
- The active MCP process continued reporting its previously loaded package version and role text after source changes, demonstrating that installed-package updates require a process reload.
- One full test run encountered transient Windows file locking and timing failures; both passed in isolation and on the next full run.

## Action Items

- During architecture review, map every mandatory responsibility to every supported profile before approval.
- Write policy tests around behavioral invariants and explicit ownership separately, making intentional ownership migrations easier to diagnose.
- After installing a new Golazo package globally, reload VS Code before using runtime role text as release verification.

## Metrics

- All Complete and Express profile ownership assertions pass.
- No canonical role text contains a backward transition or future-role dependency for release metadata.
- Final validation: 544 passed, 3 skipped, 89% coverage.
