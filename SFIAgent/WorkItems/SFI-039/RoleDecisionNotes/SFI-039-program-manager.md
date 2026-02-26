# SFI-039 Program Manager — Role Decision Notes

## Decisions Made

### 1. New test files rather than extending existing ones
**Decision**: Create 7 new test files instead of appending to `test_query_builder.py`, `test_tk_app.py`, etc.
**Rationale**: Keeps diffs clean, avoids merge conflicts, and makes per-file coverage attribution clearer.

### 2. Three-phase implementation order
**Decision**: Phase 1 (logging_config, kpi_analyzer) → Phase 2 (query_builder, copilot_tools) → Phase 3 (copilot_panel, dialogs, app).
**Rationale**: Start with the simplest files (fewest stmts, no GUI) to build momentum and establish mock patterns. GUI-heavy files come last because they depend on patterns proven in earlier phases.

### 3. Tk mocking strategy — real root + patched I/O
**Decision**: Use a real `tk.Tk()` instance per test class rather than fully mocking tkinter.
**Rationale**: A real root is needed because Tk widgets validate parent references at construction time. All external I/O (Graph API, filesystem, cache) is patched. This balances test realism with isolation.

### 4. `pytest-cov` as the coverage tool
**Decision**: Use `pytest-cov` (statement coverage) as the measurement tool.
**Rationale**: Explicitly stated in the user story. Already used by the team. Branch coverage is desirable but not required for the 70 % gate.

### 5. No production code changes
**Decision**: Strictly test-only changes. No refactoring of source files to improve testability.
**Rationale**: Out of scope per the user story. Avoids introducing regressions in a coverage-focused work item.

### 6. Copilot SDK mocking approach
**Decision**: Mock the `copilot` package at import level using `unittest.mock.patch` / `sys.modules` injection.
**Rationale**: The `copilot` SDK (`CopilotClient`, `define_tool`, `Tool`, `ToolResult`) is an external dependency that may not be installable in all environments. Mocking at the module boundary keeps tests portable.

### 7. Speed budget allocation
**Decision**: No single test > 2 s; total suite < 120 s.
**Rationale**: Directly from the user story NFR. GUI instantiation is the main risk — mitigated by sharing a single `tk.Tk()` root per test class and destroying it only once.

## Assumptions Documented

1. `pytest-cov` is available (it's not listed in `pyproject.toml` dev deps — the developer role should add it if missing).
2. The CI environment has tkinter available. If not, tests should skip gracefully.
3. Coverage percentage is statement-based (not branch-based).
4. Existing tests remain untouched and continue to pass.

## Artifacts Created

- `WorkItems/SFI-039/Design/SFI-039-design-doc.md` — full design document
- `WorkItems/SFI-039/RoleDecisionNotes/SFI-039-program-manager.md` — this file
