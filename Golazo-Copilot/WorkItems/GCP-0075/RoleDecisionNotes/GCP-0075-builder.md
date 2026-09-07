# GCP-0075 Builder Decision Notes

## Release Metadata

- Previous version: 6.0.1
- New version: 6.0.2
- Bump: patch, because this corrects workflow instructions and policy tests without changing runtime APIs.
- PEP 440 validation: 6.0.2 is valid and monotonically greater than 6.0.1.
- Added the matching newest-first README changelog entry before the final commit.

## Build

- Command: `py -3.14 -m build`
- Result: built `golazo_copilot-6.0.2.tar.gz` and `golazo_copilot-6.0.2-py3-none-any.whl` successfully.
- Verified wheel metadata reports 6.0.2 and both wheel and sdist contain the corrected Builder and Documenter role files.

## Validation

- Full suite: 544 passed, 3 skipped, 89% coverage.
- Two transient Windows/timing failures passed immediately in isolation; the subsequent full suite was green.
- Ruff passed for both changed test modules.

## Capability Registry

- Impact analysis: zero registered capabilities affected.
- Registry validation: `bootstrap-skill-installation` key files all exist.
