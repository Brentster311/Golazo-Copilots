# SFI-009 — Review Comments

## Design Review: Approved
- ✅ ThreadPoolExecutor is the right tool for I/O-bound parallelism
- ✅ `as_completed()` allows progressive result collection
- ✅ Individual failure isolation prevents one bad KPI from aborting all

## Architect Notes
- ✅ GIL is not a bottleneck for I/O-bound threads
- ✅ `status_lock` protects `completed_count` and `failed_kpis` mutations
- ⚠️ MAX_KPI_WORKERS was raised from 8 to 25 — no rate limiting issues observed with S360 API
