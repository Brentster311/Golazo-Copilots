# GCP-0065 Architect Notes

## Architecture Decision
Approve design with canonical path contract and migration fallback.

## Key Constraints
- Canonical registry path is `WorkItems/capabilities.yaml`.
- Migration from legacy root path occurs only when canonical file is missing.
- Deterministic behavior required when both files exist (canonical wins).

## Capability Impact Summary
Directly affected capabilities: `tool-capabilities`, `mcp-server`.

## Security/Operability Notes
- Ensure actionable but safe file-operation error messaging.
- Ensure path handling is cross-platform and test-covered.
