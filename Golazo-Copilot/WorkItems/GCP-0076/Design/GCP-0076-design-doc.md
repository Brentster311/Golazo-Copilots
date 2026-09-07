# GCP-0076 Design Doc

## Summary

Make `WorkItems/capabilities.yaml` the single canonical capability registry used by bootstrap, work-item creation, status, and capability queries. Preserve legacy root-file migration, remove obsolete same-project duplicate files from this repository, and populate the canonical registry with current Golazo capabilities.

## Problem Statement

GCP-0065 canonicalized capability queries but left bootstrap, work-item creation, and status on the legacy root path. Consequently status can count one file while impact analysis reads another. The canonical registry also contains only one recent capability, so most changes report zero impact and agents receive no prompt to update existing capability cards.

## Business Case

A trustworthy impact registry reduces missed regression surfaces and misleading workflow evidence. Success means every tool reports the same registry, all registered key files validate, and the registry covers the primary user-facing Golazo surfaces.

## Stakeholders

- Golazo contributors performing impact analysis
- Workflow roles reviewing and releasing changes
- Maintainers of nested projects such as AgentLoop

## Requirements

### Functional

- Centralize canonical and legacy relative paths in the capability-registry module.
- Make bootstrap and work-item creation create the canonical file.
- Make status resolve and count the canonical file using the same precedence rules without mutating state.
- Preserve `golazo_capabilities` migration behavior when canonical is absent and legacy exists.
- Replace the top-level placeholder/duplicate layout with a populated canonical registry.
- Keep independent nested-project and test fixture registries.

### Non-Functional

- Preserve existing MCP request and response schemas.
- Use `pathlib` and structured YAML.
- Avoid overwriting existing canonical project data.
- Keep status read-only.

## Proposed Approach

1. Expose shared registry path constants and a read-only resolver alongside the existing migration resolver.
2. Update bootstrap and work-item creation to write `WorkItems/capabilities.yaml` only when neither canonical nor migratable legacy data requires preservation.
3. Update status to count the canonical registry, falling back to legacy only when canonical is absent.
4. Add focused tests for all producers and consumers, coexistence precedence, and repository layout.
5. Populate cards for workflow orchestration, capability-registry management, bootstrap installation, project finalization, and release-policy guidance.
6. Delete only the top-level legacy root registry and obsolete nested package registry; preserve AgentLoop and test fixtures.

## Alternatives Considered

- Keep both paths synchronized: rejected because two writable sources inevitably drift.
- Auto-discover capabilities from source: rejected as unreliable and out of scope.
- Add mutation actions to the MCP tool: deferred; manual structured edits remain auditable.

## Risks And Mitigations

- Data loss during migration: canonical always wins; legacy is moved only when canonical is absent.
- Nested-project damage: cleanup assertions explicitly preserve AgentLoop and test fixtures.
- Registry staleness: Builder policy plus concrete cards and key-file validation make omissions visible.

## Dependencies

PyYAML, existing path and workspace conventions, packaged capability template.

## Migration, Rollout, And Rollback

On rollout, existing legacy-only workspaces migrate on capability query and new workspaces create the canonical path directly. Coexisting files retain canonical precedence. Rollback restores previous producers/readers and deleted placeholder files; capability data remains YAML-compatible.

## Observability

Use status count, `golazo_capabilities(list)`, `impact`, and `validate` as deterministic operational signals.

## Test Strategy

Unit-test path resolution and creation; integration-test bootstrap/work-item/status agreement; validate canonical cards against real files; assert repository duplicates are removed while independent fixtures remain.
