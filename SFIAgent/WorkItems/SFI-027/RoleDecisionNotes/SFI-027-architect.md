# SFI-027 Architect Decision Notes

**Role**: Architect  
**Date**: 2025-07-20  

## Decisions Made

### 1. Method signatures use keyword-only params
`get_direct_reports(alias, *, exclude_sc_alts=True)` and `get_org_tree(alias, *, depth=2)` use the `*` separator to force keyword-only arguments. Prevents `get_org_tree("muralic", 5)` positional misuse.

### 2. PII logging policy
Graph responses contain `displayName`, `jobTitle`, `department` — all PII-adjacent. Policy:
- **INFO**: Log alias only (e.g., "Querying manager chain for muralic")
- **DEBUG**: Full OrgPerson data allowed
- **WARNING/ERROR**: Include alias + error details, no personal names

### 3. CEO vs User-Not-Found 404 disambiguation
Both return HTTP 404 from different Graph endpoints. Strategy:
- `get_manager_chain`: first `/manager` call 404 → try `/users/{upn}` to confirm user exists. If user exists → CEO (return empty chain). If user doesn't exist → raise `S360ApiError`.
- `get_direct_reports`: `/directReports` 404 → user not found → raise `S360ApiError`.

### 4. Graph base URL as module constant
`GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"` in `graph.py`. Not configurable via `S360Config` — avoids config sprawl for a stable Microsoft endpoint.

### 5. OrgPerson added to existing `models.py`
Confirmed QA recommendation. Keep models in single file. `OrgPerson` and `OrgTree` added to `models.py` alongside `UserInfo`, `EtaHistoryItem`, etc. Re-export from `__init__.py`.

### 6. `@odata.nextLink` pagination — pass full URL
Graph pagination returns fully qualified URLs. The `_graph_get` helper must accept either a relative path (prepend base URL) or an absolute URL (use as-is). Check for `https://` prefix.

### 7. UPN format hardcoded
`{alias}@microsoft.com` is correct for Microsoft corp. If multi-tenant support is ever needed, create a new work item. Out of scope.

### 8. Retry-After parsing
Graph API sends `Retry-After` as integer seconds (not HTTP-date). Parse as `int(response.headers.get("Retry-After", "1"))` with fallback to exponential backoff.

## Architecture Risks Accepted
- UPN format assumes `@microsoft.com` — acceptable for internal tooling.
- No circuit breaker — retry max 3 is sufficient for library-level calls.
- No caching in library — consumers (SFIReporter) manage their own cache.

## Items Deferred
- Multi-tenant UPN support → future work item if needed.
- `models/` package conversion → future work item if models.py exceeds ~250 lines.
