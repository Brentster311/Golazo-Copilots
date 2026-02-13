# Program Manager Decision Notes — EES-00002

## Key Decisions

### PM-1: GAP Rules Use Same Persistence as CONFIRMED Rules
GAP rules are stored in `rules/` with the same `R-NNN` ID scheme. This avoids a separate file format and keeps all rules queryable through `YamlStore.list_rules()`. Differentiation is via `status: GAP`.

### PM-2: Deterministic Detection Over LLM-Based Detection
GAP detection uses deterministic graph analysis (confirmed facts → rule chains → root cause) rather than asking the LLM to identify gaps. The LLM lacks knowledge-base context and would produce unreliable results.

### PM-3: User Confirmation Required for GAPs
GAP rules go through the same confirm/edit/reject flow as CONFIRMED rules. This prevents noise from false-positive GAP detection while keeping the user in control.

### PM-4: Start with Single-Hop Chain Analysis (OQ-1)
Multi-hop rule chain tracing (A→B→C→root cause) is deferred. This first implementation checks: do confirmed facts connect to the root cause through a single rule? Orphaned facts that don't → GAP.

### PM-5: Resolved GAPs Kept for Audit (OQ-3)
When a GAP is fully resolved, its status changes to `RESOLVED` rather than being deleted. This preserves the investigation history and source provenance.

### PM-6: GAPs Not Sent to LLM (OQ-2)
GAP rules are excluded from the ontology/context sent to the LLM during fact extraction. They represent unknown logic that would confuse the extraction prompt.

## Open Items for Architect
- Exact `Rule` model extension (new fields, type annotations)
- `GapDetector` class design and algorithm
- Integration point in `process_incident` workflow
