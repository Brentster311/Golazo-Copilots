# GCP-0070 Developer Notes

## Summary

- Removed `golazo_update` from the advertised MCP tool surface, dispatch handlers, shared formatter exports, and legacy server compatibility bindings.
- Replaced self-update guidance with explicit manual `pip install --upgrade` instructions in the bootstrap spine and README, anchored to the MCP server's configured Python environment.
- Deleted the obsolete tool implementation and its dedicated test suite.

## TDD Evidence

- Updated tests first to remove `golazo_update` expectations from modular parity, formatter, and legacy coverage.
- Added bootstrap coverage for the new spine install guidance.
- Ran focused validation:
  - `python -m pytest tests/test_gcp_bootstrap.py tests/test_gcp0061_server_modular_refactor.py tests/test_server_formatters.py tests/test_server_legacy_coverage.py`
  - Result: `81 passed`

## Decisions

- Historical changelog references to `golazo_update` were retained because they document prior releases rather than the current tool contract.
- Installation guidance now points users to the exact Azure Artifacts feed and clarifies that the package must be installed into the same interpreter used by the MCP server.