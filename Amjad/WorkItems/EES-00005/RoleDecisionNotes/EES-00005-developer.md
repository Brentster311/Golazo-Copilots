# Developer Decision Notes — EES-00005

## Summary

Implemented the Tkinter-based GUI for incident processing, knowledge base browsing, and rule evaluation.

## TDD Cycle

### RED Phase
- Wrote 18 tests in `tests/test_gui_adapters.py` covering:
  - `facts_to_rows()` — 4 tests (basic, confirmed status, rejected, empty)
  - `rules_to_rows()` — 3 tests (basic positive, ruleout, empty)
  - `ontology_to_tree()` — 2 tests (basic, empty)
  - `filter_rules()` — 3 tests (all, by status, by type)
  - `eval_result_to_display()` — 4 tests (root causes, ruled out, GAPs, empty)
  - `run_in_worker()` — 2 tests (error callback, success callback)
- Verified RED: `ModuleNotFoundError: No module named 'ees.gui'`

### GREEN Phase
- Created `src/ees/gui/__init__.py` — package init
- Created `src/ees/gui/adapters.py` — pure adapter functions (model → display data)
- Created `src/ees/gui/workers.py` — `run_in_worker()` with daemon threading
- Created `src/ees/gui/app.py` — main `EESApp` class with:
  - **Process Incident tab**: file browse, LLM extraction via worker, fact confirmation, rule preview, save all
  - **Knowledge Base tab**: rules (filterable by status/type), ontology tree, root causes list
  - **Evaluate tab**: one-per-line fact input, rule evaluation, formatted results display
- Created `src/ees/gui/__main__.py` — `python -m ees.gui` support
- Added `ees-gui = "ees.gui.app:main"` entry point to `pyproject.toml`
- All 207 tests pass (189 existing + 18 new)

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Adapter pattern for testability | Pure functions in `adapters.py` are fully testable without Tk; GUI only calls adapters |
| Daemon threads for LLM calls | `run_in_worker()` with `on_complete`/`on_error` callbacks; `root.after(0, ...)` for thread-safe UI updates |
| Client-side filtering | `filter_rules()` in adapters, KB tab uses combobox filters with Refresh button |
| One-per-line fact input | Evaluate tab uses multi-line `tk.Text`, each line parsed via `Fact.parse()` |
| `--data-dir` CLI argument | Allows pointing GUI at any data directory; also changeable via File menu |
| No inline Treeview editing | Per architect MJ-1 resolution, fact confirmation uses status buttons instead |

## Files Changed

| File | Action |
|------|--------|
| `src/ees/gui/__init__.py` | Created — package init |
| `src/ees/gui/adapters.py` | Created — pure adapter functions |
| `src/ees/gui/workers.py` | Created — background worker threading |
| `src/ees/gui/app.py` | Created — main GUI application |
| `src/ees/gui/__main__.py` | Created — `python -m ees.gui` entry |
| `tests/test_gui_adapters.py` | Created — 18 unit tests |
| `pyproject.toml` | Modified — added `ees-gui` entry point |

## Tests

- 207 total tests pass
- 18 new tests for GUI adapters/workers
- 0 test regressions
