# SFI-034 Refactor Expert Decision Notes

## Assessment
The SFI-034 implementation is already well-structured with clean separation of concerns:
- `kpi_analyzer.py` — pure logic module, easily testable, no UI dependencies
- `copilot_panel.py` — thread-safe prompt injection via `send_analysis_prompt()`
- `dialogs.py` — thin integration layer, delegates to analyzer and panel

## Refactoring Applied
- **Stale comment in `__all__`**: Updated `"# LLM Analysis (stub)"` → `"# LLM Analysis"` in `dialogs.py` since the function is no longer a stub.

## Items Considered but Declined
| Item | Reason for Declining |
|------|---------------------|
| Extract `_bg_analyze` closure to module-level function | Adds complexity; closure neatly captures `app`, `kpi_id`, `panel`, `parent` |
| Move `_find_app` to `app.py` | Would create circular import; current location is appropriate |
| Add type hints to `_launch_llm_analysis` parent param | Parent can be any Tk widget type; `tk.Widget` hint would require import and adds no value given the duck-typing pattern |

## Test Verification
All tests remain green after the comment fix — no behavior change.
