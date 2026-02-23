# GCP-0054 Program Manager Decision Notes

## Approach Selection

**Decision**: Atomic batch find-replace + file renames in a single commit.

**Rationale**:
- This is a pure mechanical rename with no logic changes — complexity is in breadth, not depth.
- Atomic commit ensures no intermediate broken state.
- The existing 409-test suite provides a complete safety net; no new tests required.

## Key Decisions

1. **No backward compatibility aliases** — Clean break is simpler. The `gcp_` prefix will not co-exist with `golazo_`.
2. **Test filenames excluded from rename** — Per user story scope. Only references *inside* test files are updated.
3. **Historical WorkItems excluded** — Past design docs and decision notes retain original `gcp_` references as historical record.
4. **Single-pass execution** — All 7 renames applied together, not one-at-a-time, to avoid partial states.

## Risk Acceptance

- Breaking change for callers is accepted and expected — this is the purpose of the work item.
- MCP server restart required after deployment — noted in design doc rollout section.
