# GCP-0072 Builder Decision Notes

## Versioning

- Previous version: `5.0.2`.
- Release version: `5.1.0`.
- Format: valid PEP 440.
- Rationale: backward-compatible minor feature adding optional public bootstrap inputs and packaged skill installation.
- Canonical source: `golazo-copilot/pyproject.toml` only.

## Capability Registry

The invalid `example-capability` placeholder was replaced with `bootstrap-skill-installation`, including implementation, schema, formatter, packaged-resource, and test key files plus the additive public contracts.

`golazo_capabilities(action="validate")` result:

- `[OK] bootstrap-skill-installation: all key_files exist`.

## Test And Lint Verification

- Full suite: `522 passed, 3 skipped`.
- Changed-module selected coverage: 85%; every changed module exceeded 70%.
- Focused GCP-0072 suite after refactor: `15 passed`.
- Documentation/version regression suite: `56 passed`.
- Ruff: all changed Python files passed.
- `git diff --check -- .`: passed with no whitespace errors.

## Build Verification

Command:

`py -3.14 -m build`

Artifacts:

- `dist/golazo_copilot-5.1.0.tar.gz`
- `dist/golazo_copilot-5.1.0-py3-none-any.whl`

Result: build succeeded with no project build errors. The `build` frontend was installed from the authenticated Azure Artifacts feed because it was not initially present.

## Package Content And Install Verification

- Inspected the wheel archive and verified it contains:
  - `golazo_copilot/skills/golazo-ado-sync/SKILL.md`
  - `golazo_copilot/skills/golazo-ado-sync/defaults.yaml`
- Installed the exact wheel into Python 3.14 with `--force-reinstall --no-deps`.
- Verified installed metadata version: `5.1.0`.
- Ran bootstrap from outside the source tree against a temporary workspace.
- Verified result status `created` and both installed skill files at `.github/skills/golazo-ado-sync/`.

The only install warning was that the Python Scripts directory is not on `PATH`; the MCP configuration invokes the module through `py -3.14`, so this does not affect server operation.

## Git Operations

- Feature branch created: `brentj/GCP-0072`.
- Project Owner explicitly authorized commit and push during POA closure.
- Implementation commit: `794fe9b` (`GCP-0072: Install Golazo ADO Sync skill during bootstrap`).
- Branch pushed to `origin/brentj/GCP-0072` with upstream tracking configured.
- Numerous pre-existing changes in sibling projects were left untouched.