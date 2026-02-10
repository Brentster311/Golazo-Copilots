# SFI-027 Design Doc — MS Graph People Hierarchy

## Summary
Add a new `graph` endpoint module to `accia-s360` that uses Microsoft Graph API to query org hierarchy (manager chain upward, direct reports downward). This replaces reliance on S360's limited hierarchy APIs for org-mapping use cases.

## Problem Statement
SFI-026 (multi-level owner grouping in SFIReporter) failed because S360 provides no reliable API for org hierarchy traversal:

1. **`search(alias)`** returns a `Managers` field (alias list) but requires one API call per owner. With 50+ owners this is slow, fragile, and rate-limited after heavy KPI workload.
2. **`query_people_hierarchy`** returns only shallow team IDs — no members, no nesting.
3. **`get_user_search_groups`** returns AAD GUIDs — not people at all.

Microsoft Graph API provides reliable, well-documented endpoints for exactly this purpose.

## Business Case
- **Why now**: SFI-026 is blocked. The current S360-based approach for org mapping produced wrong results for multi-team managers (97% "Unknown Owner" for alexhowells' view).
- **Impact**: Unblocks SFI-026 2-level grouping. Also enables future features that need org awareness.
- **KPIs**: Correct org resolution rate (target: >90% of service owners mapped to correct L1/L2 managers).

## Stakeholders
- **Consumers**: SFIReporter (SFI-026), any future accia-s360 consumer needing org data
- **Dependencies**: Microsoft Graph API, Azure CLI credential chain

## Functional Requirements

### New Methods on S360Client

| Method | Description |
|---|---|
| `get_manager_chain(alias)` | Walk `/users/{id}/manager` upward, return ordered list |
| `get_direct_reports(alias, exclude_sc_alts=True)` | Call `/directReports`, filter SC ALT accounts |
| `get_org_tree(alias, depth=2)` | Recursive: target user + N levels of direct reports |

### Data Model

```python
@dataclass
class OrgPerson:
    alias: str
    display_name: str
    job_title: str | None
    department: str | None
    object_id: str  # AAD object ID

@dataclass 
class OrgTree:
    person: OrgPerson
    direct_reports: list['OrgTree']  # Recursive
```

### SC ALT Filtering
Exclude accounts where alias starts with `sc-` (case-insensitive) or display name contains "NON EA SC ALT".

## Non-Functional Requirements
- HTTP 429 rate limiting: exponential backoff, max 3 retries, respect `Retry-After` header
- Configurable timeout (default from `S360Config.timeout_seconds`)
- Logging: INFO for each call, WARNING for retries, ERROR for failures

## Proposed Approach

### Module Structure
```
accia-s360/src/accia_s360/
  endpoints/
    graph.py          # NEW — GraphEndpoint class
  models/
    org.py            # NEW — OrgPerson, OrgTree dataclasses
```

### Implementation

1. **`GraphEndpoint`** class (parallel to `ExtendedEndpoints`):
   - Constructor takes `auth_manager` reference for token acquisition
   - Shared `_graph_get(path, params)` helper with retry/429 handling
   - UPN format: `{alias}@microsoft.com`

2. **`get_manager_chain(alias)`**:
   - Loop: GET `/users/{upn}/manager?$select=displayName,mailNickname,jobTitle,department,id`
   - Stop when manager returns 404 (CEO has no manager)
   - Return list ordered: [immediate_manager, ..., CEO]

3. **`get_direct_reports(alias)`**:
   - GET `/users/{upn}/directReports?$select=displayName,mailNickname,jobTitle,department,id`
   - Filter out SC ALTs
   - Handle pagination (`@odata.nextLink`) if >100 reports

4. **`get_org_tree(alias, depth)`**:
   - Get target person info
   - Recursively call `get_direct_reports` up to `depth` levels
   - Return nested `OrgTree`

5. **Client integration**:
   - Add `GraphEndpoint` instance to `S360Client`
   - Expose methods as `client.get_manager_chain()`, etc.

## Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| S360 `search()` chain walking | Rate-limited after KPI calls, wrong manager_alias extraction for multi-team managers |
| S360 `query_people_hierarchy` | Only returns team IDs, no members |
| Azure AD PowerShell / `az ad` CLI | Slower, not programmatic from Python |
| Caching org data permanently | Org changes over time; stale data worse than fresh lookups |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Graph API permissions denied | Low | High | POC confirmed it works with existing Azure CLI creds |
| Rate limiting on large orgs | Medium | Medium | Exponential backoff + depth limit parameter |
| SC ALT pattern changes | Low | Low | Configurable filter, logged when applied |
| Graph API deprecation | Very Low | High | Microsoft's most stable API surface |

## Open Questions
- None — POC confirmed all technical assumptions

## Dependencies
- `requests` (already a dependency)
- Azure CLI credentials (already required for S360)
- MS Graph API v1.0 (stable)

## Migration / Rollout / Rollback
- **Rollout**: New additive methods — no breaking changes. Consumers opt-in.
- **Rollback**: Don't call the new methods. Existing S360-based code unaffected.
- **Migration**: SFI-026 will switch from S360 `search()` chain-walking to `get_org_tree()` / `get_manager_chain()` in a separate work item.

## Observability
- Standard Python logging via `logging.getLogger(__name__)`
- Each Graph API call logged at INFO with alias
- Retries logged at WARNING with attempt count and delay
- Auth/API failures logged at ERROR

## Test Strategy
- **Unit tests**: Mock Graph API responses for all methods, error cases, SC ALT filtering, pagination, 429 retry
- **Live integration test**: `get_manager_chain('muralic')` contains `alexhowells`; `get_direct_reports('muralic')` contains `brentj`; SC ALTs excluded
