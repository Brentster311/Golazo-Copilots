# GCP-0073 Documenter Decision Notes

## Documentation Updates

- Added the supported `mcp>=2,<3` range to README prerequisites.
- Documented that MCP 3.x requires a separately validated Golazo release.
- Added the validated v6.0.0 changelog entry after Builder defined the release version.
- Verified the user story, design, review comments, test cases, capability impact, and all prior role notes exist.

## Accuracy Review

- The dependency range matches source and built-wheel metadata.
- MCP 2.0.0 and 2.1.1 validation supports the documented 2.x compatibility claim.
- The clean installed-wheel stdio exchange supports the startup claim.
- No links were introduced.

## Changelog Decision

Builder classified the MCP 1.x compatibility removal as a breaking dependency change and set the canonical version to `6.0.0`. The README changelog now records the MCP 2.x migration, bounded dependency, and validation coverage. Publishing remains out of scope.