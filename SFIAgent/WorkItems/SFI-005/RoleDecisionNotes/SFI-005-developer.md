# SFI-005 — Developer Notes
Feature implemented in `do_refresh()` (tk_app.py) and `get_detailed_action_items()` (data.py). Status messages: "Connecting...", "Retrieved N services for {alias}", "Fetching KPIs: X/Y complete", success/error at end. Test: `test_refresh_with_status_callback` — 84 tests pass.
