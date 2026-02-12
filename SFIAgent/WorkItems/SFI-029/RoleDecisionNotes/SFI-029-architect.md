# SFI-029 — Architect Decision Notes

## Architecture
- `OrgAncestry.path` as variable-length tuple replaces fixed `level1`/`level2`
- New `flatten_org_tree()` helper creates display_name → ancestry lookup
- Tree population walks `path` to create N-level nested groups
- No new external dependencies; same auth model

## Approved Design
- Clean separation: data (flatten tree) → mapping (match names) → UI (build groups)
- Backward-compatible aggregation (rollup at any level)
