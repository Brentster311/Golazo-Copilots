# SFI-009 — Architect Notes
Retroactive review. ThreadPoolExecutor is stdlib, no new deps. GIL is fine for I/O threads. `status_lock` covers all shared mutable state. MAX_KPI_WORKERS=25 tested without API rate limiting.
