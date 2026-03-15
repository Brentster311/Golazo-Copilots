# GCP-0070 Documenter Notes

## Documentation Review

- Updated `README.md` to remove `golazo_update` from the advertised tool list and deleted the obsolete tool reference section.
- Reworked the README update guidance to use direct `pip install --upgrade` commands against the Azure Artifacts feed, explicitly tied to the Python interpreter configured in `mcp.json`.
- Updated `src/golazo_copilot/bootstrap-instructions.md` so newly bootstrapped spines point users to the supported package installation path instead of a self-update MCP tool.

## Accuracy Checks

- Verified the current MCP tool surface no longer exposes `golazo_update`.
- Verified the bootstrap tests now assert the manual package-install guidance is present in generated instructions.
- Intentionally retained historical changelog mentions of `golazo_update`; they describe past releases and do not advertise a current supported feature.

## Result

- User-facing documentation now matches the implementation: package install and upgrade happen through `pip`, not through a Golazo MCP tool.