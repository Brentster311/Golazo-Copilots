# GCP-0049 — Retrospective Notes

## What Went Well
- TDD approach caught artifact path resolution bug immediately (5 red tests → quick fix → all green)
- Existing codebase patterns (3-layer tool architecture) made implementation straightforward
- YAML front-matter from GCP-0048 was well-structured and easy to parse
- Capability registry was accurately maintained throughout

## What Didn't Go Well
- Initial YAML parsing issue with `{id}` tokens — the `{` character at the start of a YAML list item is interpreted as a flow mapping, not a plain scalar. Required a retry-with-quoting fallback.
- Artifact path resolution needed two modes: workspace-root-relative (for `WorkItems/{id}/...` patterns from real role files) and work-item-relative (for shorter patterns). This wasn't obvious from the design doc.

## Action Items
1. **Process:** When designing tools that consume YAML with template variables, note YAML special characters in the design doc
2. **Process:** Test fixtures should mirror the actual file format as closely as possible

## Metrics
- 14 new tests, 371 total, 0 regressions
- Implementation time: single session, no blockers
