# SFI-027 Design Review Comments

**Reviewer**: QA Role  
**Date**: 2025-07-20  
**Design Doc Reviewed**: SFI-027-design-doc.md  

## Overall Assessment

**Verdict: APPROVED with minor fixes** — The design is well-grounded in POC results, follows existing library patterns, and is additive (no breaking changes). Three issues need resolution before implementation.

---

## Issue 1: Models location mismatch (MUST FIX)

**Severity**: Medium  
**Section**: Module Structure

The design proposes `models/org.py` as a new directory, but the existing codebase uses a single `models.py` file (not a package). Creating a `models/` directory would require converting `models.py` into a `models/__init__.py` package — which changes the file structure for all existing imports.

**Recommendation**: Add `OrgPerson` and `OrgTree` dataclasses directly to the existing `models.py` file. This is simpler, avoids package-migration risk, and follows the current convention. The file is only 135 lines — adding ~25 lines for two dataclasses keeps it manageable.

If the file grows beyond ~250 lines in the future, convert to a package as a separate refactor work item.

---

## Issue 2: Graph API base URL not specified (MUST FIX)

**Severity**: Medium  
**Section**: Implementation — GraphEndpoint

The design says `GraphEndpoint` parallels `ExtendedEndpoints`, which uses `self.config.base_url` (the S360 URL). But Graph API uses `https://graph.microsoft.com/v1.0` — a completely different host.

**Recommendation**: Either:
- (a) Add a `graph_base_url` field to `S360Config` with default `"https://graph.microsoft.com/v1.0"`, or
- (b) Hardcode the Graph base URL as a constant in `graph.py` since it's a stable Microsoft endpoint.

Option (b) is simpler and avoids config sprawl. The existing `config.py` already has `graph_scope` so there's precedent for Graph-specific constants, but a URL constant in `graph.py` keeps Graph concerns co-located.

---

## Issue 3: GraphEndpoint constructor should take `get_token_func` not `auth_manager` (SHOULD FIX)

**Severity**: Low  
**Section**: Implementation

Design says "Constructor takes `auth_manager` reference" but existing endpoints (`ExtendedEndpoints`, `ActionItemsEndpoint`, `DiscoveryEndpoint`) all take `get_token_func: callable`. The `GraphEndpoint` should follow the same pattern but accept `get_graph_token` as the callable.

The client.py init would be:
```python
self._graph = GraphEndpoint(self.config, self._auth.get_graph_token)
```

This is consistent with:
```python
self._extended = ExtendedEndpoints(self.config, self._auth.get_s360_token)
```

---

## Observation 1: `@odata.nextLink` pagination (INFO)

The design correctly notes pagination for `directReports` with >100 results. In practice, no single manager at Microsoft is likely to have >100 direct reports (even skip-levels). Implementing pagination is good defensive coding but should be covered by a unit test with a mocked nextLink response.

---

## Observation 2: OrgPerson `from_graph_response` pattern (INFO)

The existing `UserInfo` dataclass has `from_graph_response()` classmethod. The new `OrgPerson` should follow the same pattern for consistency. Design doesn't explicitly call this out but the test cases should verify this factory method.

---

## Observation 3: Capability Impact (INFO)

Impact analysis shows 10 capabilities affected (1 direct: `accia-s360-client`, 9 transitive). Since this is a purely additive change (new methods, new models, no modifications to existing signatures), the transitive impact is low risk. The existing test suite (`accia-s360-tests`) should continue to pass unchanged.

---

## Checklist

| Area | Status | Notes |
|------|--------|-------|
| Clarity | ✅ Pass | Design is clear and specific |
| Completeness | ⚠️ Fix | Models location + Graph base URL missing |
| Feasibility | ✅ Pass | POC confirmed all technical aspects |
| Naming | ✅ Pass | `GraphEndpoint`, `OrgPerson`, `OrgTree`, `get_manager_chain` are clear |
| Error handling | ✅ Pass | Reuses `S360AuthError`/`S360ApiError`, 429 retry covered |
| Edge cases | ✅ Pass | CEO 404, SC ALT filtering, depth limit |
| Rollback | ✅ Pass | Additive — no breaking changes |
| Test coverage | ✅ Pass | Unit + live integration planned |

---

## Architect Notes

**Reviewer**: Architect Role  
**Date**: 2025-07-20  

### Architectural Alignment

The design correctly places `GraphEndpoint` alongside existing endpoint modules (`extended.py`, `action_items.py`, `discovery.py`). It follows the established pattern:
- Endpoint class takes `(config, get_token_func)` constructor
- Uses shared `_make_request`-style helper with error handling
- Delegates through `S360Client` facade

This maintains the single-entry-point architecture where consumers only import `S360Client`.

### API & Data Contracts

**`OrgPerson` dataclass** — Clean contract. Must include `from_graph_response()` classmethod consistent with `UserInfo.from_graph_response()`. The `object_id` field provides forward compatibility for future AAD-based lookups.

**`OrgTree` recursive dataclass** — Well-designed. The self-referential `direct_reports: list['OrgTree']` is idiomatic Python. Consumers traverse with standard attribute access.

**Method signatures (final)**:
```python
def get_manager_chain(self, alias: str) -> list[OrgPerson]
def get_direct_reports(self, alias: str, *, exclude_sc_alts: bool = True) -> list[OrgPerson]
def get_org_tree(self, alias: str, *, depth: int = 2) -> OrgTree
```
Note: `exclude_sc_alts` and `depth` should be keyword-only (using `*` separator) to prevent positional misuse.

### Security & Privacy

1. **Token handling**: Reuses existing `get_graph_token()` which already caches tokens and masks them in logs (`mask_tokens=True` in config). No new security surface.
2. **PII in logs**: Graph responses contain `displayName`, `jobTitle`, `department`. Log only aliases at INFO level, never full names. Full OrgPerson data only at DEBUG.
3. **No token in URLs**: Graph API uses `Authorization: Bearer` header, not query param tokens. Correct approach.
4. **Scope validation**: The existing `graph_scope = "https://graph.microsoft.com/.default"` is correct. Graph User.Read.All is granted via Azure CLI credential chain. No additional permissions needed.

### Resilience & Failure Isolation

1. **429 retry with `Retry-After`**: Correct approach. Implementation must parse `Retry-After` header as both integer seconds and HTTP-date format (Graph API uses integer).
2. **Circuit breaker**: Not needed for this scope — the retry mechanism with max 3 attempts is sufficient for an on-demand library.
3. **Failure isolation**: Graph failures do NOT affect existing S360 API operations. The `_graph` endpoint is a separate instance. If Graph is down, S360 functionality continues.
4. **CEO 404 vs User-Not-Found 404**: Critical distinction noted by QA. Implementation approach: call `/users/{upn}` first to verify user exists (returns 404 if not found), then walk `/manager` chain where 404 means CEO. Alternative: in `get_manager_chain`, the first call is `/users/{upn}/manager` — if it 404s, check if the user exists with a HEAD request. Simpler approach: just catch the first 404 and try `/users/{upn}` to confirm existence.

### Dependency Analysis

- **No new dependencies**: Uses `requests` (already installed) and existing auth infrastructure.
- **Graph API v1.0**: Stable, GA endpoint. No beta API reliance.
- **UPN format**: `{alias}@microsoft.com` is hardcoded. This is correct for Microsoft corp employees. If the library is ever used for external tenants, this would need to be configurable. Out of scope for now.

### Implicit Behavior Defaults to Surface

1. **`requests.get()` default timeout**: The design uses `self.config.timeout_seconds` explicitly — good, no reliance on infinite default.
2. **Graph `$select`**: Explicitly selecting fields reduces response size and avoids receiving PII fields not needed.
3. **`@odata.nextLink` encoding**: Graph pagination URLs are fully qualified — pass them directly to `requests.get()` without base URL concatenation.

### Final Architecture Checklist

| Concern | Status |
|---------|--------|
| Single entry point (S360Client) | ✅ Maintained |
| Consistent endpoint pattern | ✅ get_token_func callable |
| No new dependencies | ✅ |
| Auth reuse | ✅ get_graph_token() |
| Error hierarchy | ✅ S360AuthError / S360ApiError |
| Logging policy | ✅ Alias only at INFO |
| Rollback safety | ✅ Additive, no breaking changes |
| Config changes | Minimal — Graph base URL as constant in graph.py |
