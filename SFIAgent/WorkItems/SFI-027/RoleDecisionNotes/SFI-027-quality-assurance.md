# SFI-027 QA Decision Notes

**Role**: Quality Assurance  
**Date**: 2025-07-20  

## Decisions Made

### 1. Models location — keep in `models.py`
Design proposed `models/org.py` (new package). Recommended against this — adding `OrgPerson` and `OrgTree` to the existing `models.py` file (135 lines → ~160 lines) is simpler and avoids package migration risk. Documented in Review Comments Issue 1.

### 2. Graph base URL — hardcode in `graph.py`
Design didn't specify where the Graph API base URL lives. Recommended hardcoding `GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"` as a module constant in `graph.py`. It's a stable Microsoft endpoint and doesn't need user configuration. Documented in Review Comments Issue 2.

### 3. Constructor pattern — `get_token_func` callable
GraphEndpoint should take `get_token_func: callable` matching the existing endpoint pattern, not an `auth_manager` reference. Client passes `self._auth.get_graph_token`. Documented in Review Comments Issue 3.

### 4. Test organization — 2 files
- `test_graph_endpoint.py` — 34 unit tests (all mocked, no network)
- `test_graph_live.py` — 6 live integration tests (`@pytest.mark.live`)

### 5. Cycle protection added to test plan
The design doesn't mention graph cycles in the manager chain (A→B→A). Added test T06 to verify the implementation terminates safely. Max 10 iterations is the implicit depth limit from the user story's "Org trees deeper than 10 levels" out-of-scope clause.

### 6. 404 semantics differ by context
- `/users/{upn}/manager` returning 404 → chain termination (CEO reached) → not an error
- `/users/{upn}/directReports` returning 404 → user not found → raise `S360ApiError`
- `/users/{nonexistent}/manager` returning 404 → user not found → raise `S360ApiError`

The implementation must distinguish these cases. Test T30 covers the user-not-found case; T03 covers the CEO-termination case.

### 7. Capability impact is low risk
10 capabilities affected but all transitively. No existing contracts change. Existing `accia-s360-tests` must continue passing unchanged.

## Items Deferred
- None — all design issues can be resolved during implementation without scope changes.

## Risks Flagged
- If `models.py` approaches 250+ lines in the future, convert to package in a separate work item.
- SC ALT pattern (`sc-*` prefix) is an assumption based on observed data — may need updating if Microsoft changes naming conventions.
