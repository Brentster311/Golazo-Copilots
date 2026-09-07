# GCP-0076 Capability Impact

## Current Analysis

The current registry reports only `bootstrap-skill-installation` as directly affected because that is the sole existing card. Capability-registry, status, work-item creation, workflow orchestration, finalization, and release-policy files are currently untracked; this blind spot is part of the defect being corrected.

## Contract Implications

- Canonical registry location remains `WorkItems/capabilities.yaml`.
- Existing MCP action schemas remain unchanged.
- Bootstrap and work-item creation change output location from legacy root to canonical.
- Status changes its registry count source to canonical-first read-only resolution.
- Legacy-only workspaces retain migration compatibility through mutating setup/query operations.

## Transitive Impact

No transitive capabilities are represented in the current registry. The populated registry will express dependencies where one capability relies on another.

## Security And Reliability

No secrets or user data are introduced. Canonical precedence prevents legacy data from overriding current data, and migration is constrained to the supplied workspace root.
