# GCP-0076 Builder Decision Notes

## Release Metadata

- Previous version: 6.0.2
- New version: 6.0.3
- Bump: patch, because this fixes inconsistent registry paths and stale metadata without breaking MCP schemas.
- PEP 440: 6.0.3 is valid and monotonically greater than 6.0.2.
- Added matching newest-first README changelog entry.

## Build

- Command: `py -3.14 -m build`
- Result: built `golazo_copilot-6.0.3.tar.gz` and `golazo_copilot-6.0.3-py3-none-any.whl`.
- Verified wheel metadata reports 6.0.3, the capability template is packaged, and the sdist contains the registry implementation.

## Validation

- Full suite: 551 passed, 3 optional Azure Identity tests skipped.
- Repository-wide Ruff: passed with no findings.
- Coverage run: 89%.

## Capability Registry

- Five capability cards listed successfully.
- All key files validate.
- Representative impact maps registry and release-policy changes directly and bootstrap installation transitively.
