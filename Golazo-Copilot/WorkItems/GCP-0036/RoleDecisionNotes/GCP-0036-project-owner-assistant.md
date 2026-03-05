# GCP-0036 — Project Owner Assistant Decision Notes

## Scope
Single story — change version comment format across all instruction files and remove dynamic stamping. Small, contained change.

## Key decisions
- The new format `<!-- Last Updated in Golazo Copilot Version: X.Y.Z -->` communicates that the version is when content was last changed, not when it was deployed
- Removing dynamic stamping simplifies the bootstrap code and makes the version meaningful
- The version sync warning behavior changes: it now compares "last updated" version vs running version, which is more useful (tells you if the deployed file is from an older release)

## Must-Ask resolution
All established: MCP server, cross-platform, file-based, developers.
