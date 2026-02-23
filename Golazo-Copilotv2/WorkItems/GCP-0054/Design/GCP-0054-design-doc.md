# GCP-0054 Design Doc — Rename MCP Tools from `gcp_` to `golazo_`

## Summary

Mechanical rename of all 7 MCP tool names from the `gcp_*` prefix to the `golazo_*` prefix. No behavior, parameter, or logic changes. ~695 occurrences across ~64 operational files.

## Problem Statement

The current `gcp_` tool prefix is an internal abbreviation that could be confused with Google Cloud Platform. Renaming to `golazo_` aligns tool names with the product brand and improves discoverability.

## Business Case

- **Why now**: Brand alignment before wider adoption; easier to rename now than with a larger user base.
- **Impact**: Clearer branding, no functional impact.
- **KPIs**: Zero test regressions (409 existing tests pass).

## Stakeholders

- Golazo Copilot users (breaking change — tool names change)
- Repository maintainers

## Requirements

### Functional

1. Rename 7 tool source files: `gcp_*.py` → `golazo_*.py`
2. Update all imports, registrations, and string references in operational code
3. Update role markdown files (both `src/` defaults and `.github/` deployed copies)
4. Update `capabilities.yaml`, `README.md`, `bootstrap-instructions.md`
5. Update all test file contents (test filenames excluded)

### Non-Functional

- Pure rename — zero behavior changes
- All ~695 occurrences updated; zero stale `gcp_` references in operational files

## Proposed Approach

**Batch find-replace + file renames**, executed in order:

1. **Rename tool source files** (`src/golazo_copilot/tools/gcp_*.py` → `golazo_*.py`)
2. **Batch find-replace** across all operational files:
   - `gcp_status` → `golazo_status`
   - `gcp_transition` → `golazo_transition`
   - `gcp_create_workitem` → `golazo_create_workitem`
   - `gcp_bootstrap` → `golazo_bootstrap`
   - `gcp_consent` → `golazo_consent`
   - `gcp_capabilities` → `golazo_capabilities`
   - `gcp_role_context` → `golazo_role_context`
3. **Verify** no stale `gcp_` tool references remain (grep scan, excluding WorkItems history and test filenames)
4. **Run full test suite** — all 409 tests must pass

### File Categories & Estimated Occurrences

| Category | Files | ~Occurrences |
|---|---|---|
| Tool source files (rename) | 7 | — |
| `server.py` | 1 | 43 |
| `tools/__init__.py` | 1 | 21 |
| Role markdown files | 10 | 33 |
| `.github/` deployed copies | ~5 | 29 |
| Test files (contents only) | 17 | 464 |
| `capabilities.yaml` (×2) | 2 | 30 |
| `README.md` | 1 | 21 |
| `bootstrap-instructions.md` | 1 | 15 |
| `types.py` | 1 | 1 |

## Alternatives Considered

| Alternative | Verdict |
|---|---|
| Alias both prefixes (backward compat) | Rejected — adds complexity for no real gain; clean break is simpler |
| Gradual rename (one tool at a time) | Rejected — atomic rename is safer and faster for a mechanical change |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Missed occurrence causes runtime error | Low | High | Grep scan + full test suite |
| Breaking callers using old `gcp_` names | Certain | Medium | Expected breaking change; `.github/copilot-instructions.md` updated simultaneously |
| Stale MCP server process serves old names | Medium | Medium | Restart MCP server after deployment |

## Dependencies

- None. Self-contained rename.

## Migration / Rollout / Rollback

- **Rollout**: Single atomic commit with all renames + reference updates.
- **Rollback**: `git revert` of the rename commit.
- **Breaking change**: Callers must use `golazo_*` tool names after update.

## Observability

- No new telemetry. Existing test suite is the validation mechanism.

## Test Strategy

- **Safety net**: 409 existing tests cover all tool registrations, role content, server behavior.
- **Verification**: Post-rename grep scan confirms zero stale `gcp_` references in operational files.
- **No new tests needed** — this is a rename, not new functionality.
