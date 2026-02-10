# SFI-026 — Program Manager Decision Notes

## Work Item
**ID**: SFI-026
**Title**: Multi-Level Owner Grouping in Services Table

## Key Design Decisions

### 1. Extend Existing Algorithm vs. Rewrite
**Decision**: Extend `get_org_mapping()` to return a tuple `(level1, level2)` instead of a single ancestor string.

**Rationale**: The current algorithm already queries the S360 management-chain API and traverses the chain. Extracting one additional level from the same chain data is a minimal, low-risk change. A full rewrite (e.g., recursive N-level) was considered but rejected because no user needs 3+ levels and the complexity would be disproportionate.

### 2. Auto-Detect Hierarchy Depth vs. Config Flag
**Decision**: Auto-detect based on whether any `level2_name` values are non-None in the mapping result.

**Rationale**: This means 1-level managers automatically get their existing behavior and 2-level managers automatically get the new behavior, with zero configuration. A config flag would add user friction and potential misconfiguration.

### 3. Preserve Existing 1-Level Code Path
**Decision**: When all `level2_name` values are None (1-level manager), the existing display logic executes unchanged.

**Rationale**: This is the safest approach for backward compatibility. The existing 1-level code was hard-fought (SFI-013 + SFI-014 bug fixes). Touching it unnecessarily introduces regression risk.

### 4. Two Aggregation Dicts vs. Nested Dict
**Decision**: Use two flat dicts (`level1_stats` and `level2_stats`) rather than a nested dict structure.

**Rationale**: Flat dicts are simpler to iterate when building the treeview and when computing drill-down filters. A nested dict would require recursive traversal for aggregation.

## Alternatives Decision Log

| Alternative | Considered | Decision | Why |
|-------------|-----------|----------|-----|
| Recursive N-level | Yes | Rejected | YAGNI — no 3+ level users exist |
| Flat table + column | Yes | Rejected | Loses collapsible visual hierarchy |
| Separate tabs | Yes | Rejected | Fragments the view |
| Feature flag | Yes | Rejected | Auto-detection is simpler and zero-config |

## Risk Acceptance

- **Regression risk**: Accepted as medium, mitigated by preserving the 1-level code path and explicit regression tests
- **Performance risk**: Accepted as low, since no new API calls are needed
- **"Unknown Owner" edge cases**: Accepted as medium, mitigated by AC-7 and regression tests from SFI-014

## Operational Considerations

- **Desktop app**: No on-call, no server-side monitoring needed
- **Rollback**: Previous PyInstaller build serves as rollback
- **Dependencies**: Zero new dependencies — all existing libraries sufficient
