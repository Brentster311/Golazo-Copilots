# GCP-0065 Project Owner Assistant Notes

## Scope Decision
Focused scope on path-resolution behavior for capability discovery after moving `capabilities.yaml` under `WorkItems/`.

## Why This Scope
This is a single user-observable outcome: Golazo capability commands continue to function under the new canonical file location.

## Assumptions
- Existing Golazo MCP command interface is unchanged.
- Repository remains cross-platform and path normalization is required.
- Capability data source remains file-based in-repo.

## Story Quality Check
- Acceptance criteria are testable and constrained to one vertical slice.
- Out-of-scope explicitly excludes schema and feature redesign.
