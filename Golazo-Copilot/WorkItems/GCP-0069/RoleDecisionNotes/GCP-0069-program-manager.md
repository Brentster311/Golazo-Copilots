# GCP-0069 Program Manager Decision Notes

## Summary
Defined a minimal backward-compatible design that adds `scope` to bootstrap and fixes the downstream workflow preflight failure by centralizing instruction path resolution.

## Key Decisions
- Keep `Workspace` as the default effective scope for compatibility.
- Treat user-scope support as incomplete unless workflow preflight checks are updated alongside bootstrap.
- Centralize path resolution in shared dispatch helpers to cover both modular router code and legacy server code.

## Alternatives Rejected
- Bootstrap-only change without preflight updates.
- Implicit destination inference without an explicit `scope` parameter.
- Duplicated resolution logic across multiple dispatch entry points.

## Operational Notes
- User-visible recovery messaging should still be simple and actionable.
- The change should remain local to bootstrap, path helpers, tool schema, formatting, and tests.

## Outputs Created
- `WorkItems/GCP-0069/Design/GCP-0069-design-doc.md`
- `WorkItems/GCP-0069/RoleDecisionNotes/GCP-0069-program-manager.md`