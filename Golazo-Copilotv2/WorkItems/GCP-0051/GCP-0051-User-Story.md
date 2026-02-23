# GCP-0051 User Story

**Status**: IMPLEMENTED

## User Story

- **Title:** Parallel gcp_status Aggregation
- **As a:** Golazo Copilot user
- **I want:** The `gcp_status` tool to run its independent data-gathering operations concurrently instead of sequentially
- **So that:** Status responses are faster (especially for work items with many artifacts or stale-file checks), and the architecture is ready for additional aggregation steps without linear latency growth

- **Out of scope:**
  - Changes to the status response format (the output dict structure stays identical)
  - Changes to other MCP tools
  - Adding new data sources to gcp_status (this is a performance refactor, not a feature add)
  - Subagent orchestration (this is a Python-level async optimization)

- **Assumptions:**
  - **Assumption (explicit):** The five independent operations to parallelize are: (a) output validation (`parse_required_outputs` + `validate_all_outputs`), (b) stale-file detection (`_get_stale_files`), (c) registry hint (`_get_registry_hint`), (d) role progress computation (`_compute_role_progress`), (e) next-step generation (`_generate_next_steps`). State loading and role instruction loading remain sequential (they're prerequisites for the parallel fan-out).
  - **Assumption (explicit):** The implementation uses `asyncio.gather` since the MCP server already runs in an async context. No new threading or multiprocessing.
  - **Assumption (explicit):** Error isolation: if any single aggregation step fails, the others still complete. The failed step's section is populated with an error marker (e.g., `"stale_files": {"error": "..."}`) rather than failing the entire gcp_status call.
  - **Assumption (explicit):** The functions being parallelized are currently sync. They'll be wrapped with `asyncio.to_thread` or refactored to be natively async where the I/O is simple file reads.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] AC1: `gcp_status` produces an identical response dict (same keys, same structure) as before the change — existing tests pass without modification
  - [ ] AC2: The five aggregation operations run concurrently via `asyncio.gather` (or equivalent); a timing test demonstrates that total execution time is approximately `max(individual times)` rather than `sum(individual times)`
  - [ ] AC3: If one aggregation step raises an exception, the others still complete and the response includes an error marker for the failed step instead of a 500-level failure
  - [ ] AC4: New test `test_gcp_status_parallel.py` includes: (a) a timing assertion confirming concurrency, (b) an error-isolation test where one step is mocked to fail
  - [ ] AC5: No new dependencies added (stdlib asyncio only)

- **Non-functional requirements:**
  - Status response latency should decrease by ≥ 30% for a work item in the developer role with 5+ artifacts (measured in test)
  - No behavior change observable to the user — this is a transparent optimization

- **Telemetry / metrics expected:** None

- **Rollout / rollback notes:**
  - Rollout: Bump version, rebuild package. No workspace changes needed — the tool interface is unchanged.
  - Rollback: Revert to sequential gcp_status, rebuild.

## Dependencies

- **Depends on:** None (independent of the subagent work items)
- **Prerequisite for:** None (standalone optimization, but improves the subagent orchestrator experience since it calls gcp_status on every turn)

## Closure

### Summary
Refactored `gcp_status` to run 5 independent data-gathering operations concurrently via `asyncio.gather` + `asyncio.to_thread`. Added error isolation so individual operation failures don't crash the entire status call. 8 new tests validate concurrency, error isolation, and response structure.

### Acceptance Criteria Status
- [x] AC1: Response dict structure identical — 285 existing tests pass unchanged
- [x] AC2: Operations run concurrently — timing test verifies parallel < 250ms for 3×100ms operations
- [x] AC3: Error isolation works — 3 separate failure tests confirm individual operations fail gracefully
- [x] AC4: `test_gcp_status_parallel.py` created with 8 tests covering timing, error isolation, edge cases
- [x] AC5: No new dependencies — stdlib `asyncio` only

### Future Work Items
None identified beyond existing backlog (GCP-0048 through GCP-0052).

### Final Status
**IMPLEMENTED** — committed on branch `GCP-0051`, 293 tests passing.
