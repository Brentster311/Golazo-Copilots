# SFI-026 Retrospective

## What Went Well

1. **Deep research before coding** — Sub-agent thoroughly analyzed existing `get_org_mapping` algorithm, prior work items (SFI-013, SFI-014), and the management chain data model. This prevented misunderstanding the chain structure.
2. **TDD discipline** — Wrote all 26 tests before production code. The red-green cycle caught the `get_client` patch target issue early.
3. **OrgAncestry NamedTuple** — Clean data model that preserves backward compatibility with legacy string mappings via `_get_level1()` helper.
4. **Zero regressions** — 233 existing tests remain green. No behavior changes to 1-level or IC views.
5. **Comprehensive test coverage** — 6 test categories covering org mapping, aggregation, drill-down, and backward compatibility.

## What Didn't Go Well

1. **Patch target mistake** — Tests initially used `@patch("sfi_reporter.tk_app.get_client")` but `get_client` is lazily imported from `sfi_reporter.data`. Cost one debug cycle.
2. **Dependency chain friction** — Had to install httpx, llm_extender, and sfi-reporter (all --no-deps) to get imports working. The `accia_s360` package is not on PyPI, causing cascading install issues.
3. **No integration test** — The `_update_tables` rendering logic (treeview insertion) is tested only through the unit tests on the data functions, not through a UI integration test. This is a coverage gap.

## Action Items

| # | Action | Priority |
|---|--------|----------|
| 1 | Document lazy-import patch targets in a `TESTING.md` for S360Reporter (e.g., "always patch `sfi_reporter.data.get_client`, not `sfi_reporter.tk_app.get_client`") | Medium |
| 2 | Add `accia-s360` to a local dev requirements or document the `--no-deps` workaround | Low |
| 3 | Consider a headless treeview rendering test (mock tk.Tk + Treeview) for `_update_tables` in a future work item | Low |

## Metrics

- **Test pass rate**: 26/26 new + 233/233 existing = 100% relevant pass rate
- **Regressions**: 0
- **Commit size**: 14 files, +2529/-263 lines (includes all Golazo artifacts)
- **Roles completed**: 9/9
