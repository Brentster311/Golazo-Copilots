# SFI-027 — Project Owner Assistant Decision Notes

## Decision: Single User Story Scope
The request is a single capability addition (MS Graph people hierarchy) in one library (accia-s360). It produces one user-observable outcome: new API methods for org hierarchy. No decomposition needed.

## Must-Ask Checklist Resolution
| Question | Answer | Source |
|---|---|---|
| Interface type | Python library (new methods on S360Client) | User stated "new capability in accia-s360" |
| Target platform | Cross-platform (Python package) | Existing library is cross-platform |
| Data persistence | In-memory only (consumers cache as needed) | Library pattern — accia-s360 doesn't persist |
| User type | Technical (developers) | Library consumers |

## Key Decisions

### Why MS Graph instead of S360 API?
S360 provides three hierarchy-related APIs, all proven insufficient:
1. **`query_people_hierarchy`** — Returns shallow team IDs and names only. No members, no nesting.
2. **`get_user_search_groups`** — Returns ~280 AAD objectId GUIDs. No names, aliases, or hierarchy info.
3. **`search(alias)`** — Returns `Managers` field (alias list from CEO down) but only for the searched person. Requires N+1 calls to map N owners and is fragile (name resolution, rate limiting after heavy KPI workload).

MS Graph provides:
- `/users/{id}/manager` — walk up the chain
- `/users/{id}/directReports` — walk down one level
- Full user objects with displayName, mailNickname (alias), jobTitle, department
- Reliable, well-documented API with predictable rate limiting

### POC Results (confirmed live)
- `GET /users/muralic@microsoft.com/manager` → alexhowells with full details
- `GET /users/muralic@microsoft.com/directReports` → 7 real directs (brentj, kehsieh, etc.) + 2 SC ALTs
- Walking up from muralic reaches satyan (CEO) in 5 levels
- Walking down 2 levels shows ~60 people in muralic's org
- Existing `get_graph_token()` works without modification

### SC ALT Filtering
MS Graph returns shadow accounts like "Brent Jensen (NON EA SC ALT)" with aliases like `SC-pj467`. These should be filtered out based on:
- Alias prefix `sc-` or `SC-` (case-insensitive)
- Display name containing "NON EA SC ALT"

### Why depth=2 default for get_org_tree?
SFI-026 needs 2-level grouping (viewer → directs → directs' directs). Deeper nesting is out of scope for the consumer but the method should accept a configurable depth parameter for future flexibility.
