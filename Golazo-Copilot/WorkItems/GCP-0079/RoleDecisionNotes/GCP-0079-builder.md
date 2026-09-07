# GCP-0079 Builder Notes

## Release Metadata

- Previous version: `6.0.4`.
- New version: `6.1.0`.
- Rationale: backward-compatible public creation option and orchestrator workflow behavior require a minor release.
- Canonical version source: `golazo-copilot/pyproject.toml`.
- README changelog entry matches `6.1.0` and is newest-first.

## Build Verification

- `py -3.14 -m build`: passed.
- Wheel: `golazo_copilot-6.1.0-py3-none-any.whl` (96,372 bytes), metadata version `6.1.0`.
- Sdist: `golazo_copilot-6.1.0.tar.gz` (144,478 bytes), metadata version `6.1.0`.
- `py -3.14 -m twine check dist/*`: passed.
- `py -3.14 -m ruff check src tests`: passed.
- `py -3.14 -m pytest -q --tb=short`: 569 passed in 16.00s.

## Capability Registry

All key files exist for all five registered capabilities. The workflow-orchestration card includes the new creation contract, bootstrap key file, and GCP-0079 contract tests.

## Git

Target branch: `brentj/GCP-0079`.
Commit message: `GCP-0079: Offer Planner before the first work item`.
