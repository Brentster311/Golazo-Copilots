# SFI-009 — Developer Notes
Implemented in `get_detailed_action_items()` in data.py. Uses ThreadPoolExecutor with min(MAX_KPI_WORKERS, total) workers, `as_completed()` for result collection, thread-safe progress via `status_lock`. 139 tests pass.
