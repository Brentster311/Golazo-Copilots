# GCP-0072 Developer Decision Notes

## Implementation Summary

- Added canonical machine-readable ADO Sync defaults beside the packaged skill.
- Added workspace and user skill destination resolution.
- Extended full bootstrap with opt-in installation, explicit confirmation, validated default/override merging, complete resource-tree copying, and staged replacement.
- Preserved existing bootstrap defaults and result fields while adding structured skill outcomes.
- Extended modular and legacy MCP schemas and dispatch paths.
- Added bootstrap guidance that requires presenting defaults and obtaining confirmation.
- Delegated legacy bootstrap formatting to the canonical modular formatter.

## TDD Evidence

### Red

`py -3.14 -m pytest tests/test_gcp0072_skill_bootstrap.py -q`

- Result after test harness correction: 9 failed.
- Failures were the missing bootstrap input parameters and MCP schema.

### Green

Focused GCP-0072 suite:

- `15 passed in 1.63s`

Focused bootstrap/dispatch/formatter regression with coverage:

- `98 passed in 4.10s`
- Selected-module total coverage: 83%.

Full package regression with changed-module coverage:

- `522 passed, 3 skipped in 15.56s`
- `dispatch.paths`: 100%
- `dispatch.registry`: 100%
- `formatters.results`: 79%
- `handlers.tools`: 74%
- `tools.golazo_bootstrap`: 90%
- Selected-module total: 84%

Lint:

- Ruff passed for all changed Python source and test files.
- VS Code diagnostics reported no errors in changed Python files.

## Implementation Decisions

- Partial override objects merge over defaults, but empty, non-string, or unknown values fail before installation.
- The complete resource tree is copied through package-resource APIs so future bundled assets are included.
- Installed `defaults.yaml` is rewritten with the effective configuration to keep persisted structured and human-readable values aligned.
- Existing skill directories skip unless `force=True`; forced installation validates staging before replacing the existing directory.
- `orchestrator-only` rejects skill installation before writing orchestrator instructions.
- Formatter output reports outcome metadata without dumping configuration values.

## Environment Note

The only available Python interpreter was 3.14. Repository-declared test tools were installed from the authenticated Azure Artifacts feed before validation.