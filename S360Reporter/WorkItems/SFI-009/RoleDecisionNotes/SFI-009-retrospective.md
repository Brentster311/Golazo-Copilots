# SFI-009 — Retrospective
**What went well**: Massive perf improvement (~6x faster refresh). ThreadPoolExecutor was the right call.
**What didn't go well**: No Golazo artifacts existed at all — not even a Design folder. MAX_KPI_WORKERS changed from 8 to 25 without updating user story.
**Action item**: Keep user story assumptions current when implementation deviates.
