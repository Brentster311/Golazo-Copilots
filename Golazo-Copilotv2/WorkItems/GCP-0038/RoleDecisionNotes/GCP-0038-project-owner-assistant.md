# GCP-0038 — Project Owner Assistant Notes

## Decision
Created as the "Capability Index" process improvement from GCP-0036 retro, pivoted to a general-purpose GCP tool (not internal-only).

## Scope Rationale
- Single story: one tool with four actions. All actions share the same data model and parsing logic.
- Role instruction updates to auto-surface impact analysis in QA/Architect are a separate work item — this story delivers the tool, the next integrates it.
- Registry editing via tool is out of scope to keep V1 simple (YAML is human-editable).

## Granularity Decision
Analyzed GCP-0036 miss: the minimum registry entry that would have caught it was one capability ("stale-detection") with one contract ("version comment format") and one dependency ("bootstrap"). This confirms **one capability per user-observable feature** as the right grain — not per-module, not per-function.

## Must-Ask Checklist
- Interface: MCP tool (confirmed by user)
- Platform: Cross-platform/Python (inherited)
- Persistence: YAML file at project root
- User type: Technical developers
