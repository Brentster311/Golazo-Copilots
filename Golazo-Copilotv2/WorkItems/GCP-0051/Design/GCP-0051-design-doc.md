# GCP-0051 Design Doc — Parallel `gcp_status` Aggregation

## Summary

Refactor `gcp_status` to run its five independent data-gathering operations concurrently using `asyncio.gather`, reducing response latency without changing the tool's public contract.

## Problem Statement

`gcp_status` currently runs five independent operations **sequentially**:

1. **Output validation** — parses role markdown, checks files/dirs exist
2. **Next-step generation** — builds remediation advice from output results
3. **Missing-notes check** — scans role history for missing decision notes
4. **Stale-file detection** — compares 11 deployed file versions against package source
5. **Registry hint** — parses `capabilities.yaml`

Operations 3–5 have no data dependency on each other or on 1–2. Operations 1 and 2 have a dependency (2 uses 1's results). Total latency is currently `sum(all)` when it could be closer to `max(independent groups)`.

For a work item in the developer role with stale-file checking enabled, this can mean 200–500ms of unnecessary sequential I/O.

## Business Case

- **Why now**: The subagent orchestration architecture (GCP-0050) will call `gcp_status` on every turn. Reducing its latency directly improves the user-perceived responsiveness of the entire workflow.
- **Impact**: Transparent performance improvement — no user-facing changes.
- **KPIs**: ≥30% latency reduction measured in test.

## Stakeholders

- Golazo Copilot package maintainers (code change)
- All Golazo Copilot users (benefit from faster status calls)

## Functional Requirements

1. `gcp_status` response dict structure remains **identical** (same keys, types, values)
2. Five aggregation operations run concurrently where data dependencies allow
3. Individual operation failures are isolated — other operations still complete

## Non-Functional Requirements

- No new dependencies (stdlib `asyncio` only)
- Python ≥3.10 (already the project minimum per `pyproject.toml`)
- No behavior change observable to the user

## Proposed Approach

### Current Sequential Flow

```python
async def gcp_status(...):
    state = load_state(...)              # sequential (prerequisite)
    role_instructions = load_role_instructions(...)  # sequential (prerequisite)
    role_content = get_role_content(...)  # sequential (prerequisite)
    
    # --- These run one after another today ---
    output_specs = parse_required_outputs(role_content, work_item_id)
    validation_result = validate_all_outputs(output_specs, workspace_root)
    next_steps = _generate_next_steps(state, required_outputs)
    missing_notes = [...]  # loop over role_history
    stale_files = _get_stale_files(workspace_root)
    registry_hint = _get_registry_hint(workspace_root)
    role_progress = _compute_role_progress(state)
    
    return {...}
```

### Proposed Parallel Flow

```python
async def gcp_status(...):
    # Phase 1: Sequential prerequisites
    state = load_state(...)
    role_instructions = load_role_instructions(...)
    role_content = get_role_content(...)
    
    # Phase 2: Parallel fan-out (independent operations)
    (
        output_result,
        stale_files_result,
        registry_result,
        progress_result,
        missing_notes_result,
    ) = await asyncio.gather(
        _async_validate_outputs(role_content, work_item_id, workspace_root),
        _async_get_stale_files(workspace_root),
        _async_get_registry_hint(workspace_root),
        _async_compute_role_progress(state),
        _async_check_missing_notes(state, work_item_id, work_items_dir),
        return_exceptions=True,  # error isolation
    )
    
    # Phase 3: Assemble result (handle errors)
    required_outputs = _unwrap_or_error(output_result, "required_outputs")
    next_steps = _generate_next_steps(state, required_outputs)
    ...
    
    return {...}  # identical structure
```

### Async Wrapper Strategy

The current helper functions are sync. Two options:

| Option | Pros | Cons |
|--------|------|------|
| **A) `asyncio.to_thread` wrappers** | Minimal code change, preserves sync functions | Thread pool overhead for fast operations |
| **B) Inline `await` with native async** | No thread overhead | Larger refactor; file reads aren't truly async without `aiofiles` |

**Chosen: Option A** — `asyncio.to_thread` wraps each sync function. The overhead is negligible (microseconds) vs. the I/O being parallelized (milliseconds). No new dependencies. The sync functions remain testable independently.

### Error Isolation

```python
result = await asyncio.gather(..., return_exceptions=True)

def _unwrap_or_error(result, label):
    if isinstance(result, BaseException):
        return {"error": f"{label} failed: {result}"}
    return result
```

Each result slot is checked: if it's an exception, the response section gets an error marker string instead of failing the entire call.

## Alternatives Considered

1. **Do nothing**: Acceptable today, but latency compounds when `gcp_status` is called on every orchestrator turn (GCP-0050).
2. **`concurrent.futures.ThreadPoolExecutor`**: Works but adds manual executor management. `asyncio.to_thread` is simpler and idiomatic in the existing async context.
3. **`aiofiles` for true async I/O**: Would require a new dependency and larger refactor. File reads here are small (< 50KB each) — thread-offloaded sync reads are fast enough.

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Timing-based tests are flaky on CI | Medium | Low | Use generous margins (e.g., parallel < sequential × 0.8) and run timing tests with `@pytest.mark.slow`; allow skip in constrained CI |
| Thread safety of shared state object | Low | Medium | `state` is read-only after load; no mutations during parallel phase |
| `asyncio.to_thread` not available | None | N/A | Requires Python 3.9+; project requires 3.10+ |

## Dependencies

- No external dependencies
- No changes to other MCP tools
- No changes to `state.json` schema

## Migration / Rollout / Rollback

- **Rollout**: Bump version, rebuild package. Tool interface unchanged — no workspace migration needed.
- **Rollback**: Revert `gcp_status.py` to sequential version, rebuild.

## Observability

- No new telemetry
- Error markers in response dict make failures visible to the LLM consumer

## Test Strategy

1. **Existing tests pass unchanged** — response dict structure is identical
2. **New `test_gcp_status_parallel.py`**:
   - Timing test: mock slow operations, verify parallel is faster than sequential
   - Error isolation test: mock one operation to raise, verify others succeed and error marker appears
3. **Negative test**: verify that a failure in `_get_stale_files` doesn't prevent `required_outputs` or `registry_hint` from populating
