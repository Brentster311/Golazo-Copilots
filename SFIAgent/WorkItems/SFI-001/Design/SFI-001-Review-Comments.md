# SFI-001 Design Review Comments

## Date: 2026-02-03

## Overall Assessment: ✅ APPROVED with minor recommendations

The design is clear, feasible, and well-structured. The following comments are recommendations, not blockers.

---

## Clarity and Completeness

### ✅ Strengths
- Clear project structure with separation of concerns
- Well-defined authentication flow
- Good dependency list with version constraints

### 🟡 Recommendations

**R1: Add explicit error types**
- Define custom exception classes (e.g., `S360AuthError`, `S360ApiError`, `S360CacheError`)
- Helps consumers handle errors appropriately

**R2: Define cache key strategy**
- Design doc mentions caching but doesn't specify cache key format
- Recommend: `{endpoint}_{params_hash}_{timestamp}.json`

---

## Feasibility and Sequencing

### ✅ Strengths
- Phased approach (core → discovery → extended) is sensible
- Dependencies are proven (same as reference project)

### 🟡 Recommendations

**R3: Consider discovery as separate module**
- Discovery could be optional import to keep core lightweight
- `from s360_client.discovery import discover_endpoints`

---

## Risk Coverage

### ✅ Addressed
- API changes
- Auth scope changes  
- Rate limiting
- Undocumented behavior

### 🟡 Missing Risks

**R4: Token expiration during long operations**
- If a batch operation takes >1 hour, token may expire mid-operation
- Mitigation: Refresh token before each API call or check expiry

**R5: Concurrent access to cache files**
- If multiple processes use library, cache corruption possible
- Mitigation: Use file locking or accept last-write-wins

---

## Operability

### ✅ Strengths
- Logging plan is adequate
- Local diagnostics planned

### 🟡 Recommendations

**R6: Add connection test utility**
- `s360_client.test_connection()` → returns health status
- Useful for debugging auth/network issues

---

## Edge Cases and Failure Modes

### Identified for test coverage:
1. Empty responses from API
2. Malformed JSON responses
3. Partial success in batch operations
4. Network interruption mid-request
5. Invalid/expired token
6. Cache file corruption
7. Disk full during cache write

---

## Naming Review

### ✅ Good
- `s360_client` - clear package name
- `auth.py`, `client.py`, `cache.py` - standard naming

### 🟡 Suggestions
- Consider `api_client.py` instead of `client.py` (more specific)
- `models.py` → `schemas.py` or `types.py` (Python convention)

---

## Summary of Recommendations

| ID | Recommendation | Priority | Blocking |
|----|----------------|----------|----------|
| R1 | Define custom exception classes | Medium | No |
| R2 | Document cache key strategy | Low | No |
| R3 | Make discovery module optional | Low | No |
| R4 | Handle token refresh in long ops | Medium | No |
| R5 | Consider cache file locking | Low | No |
| R6 | Add connection test utility | Medium | No |

---

## Decision

**APPROVED** - Design is sufficient to proceed to implementation. Recommendations can be addressed during development or as follow-up improvements.

---

# Architect Notes

## Date: 2026-02-03

## Architectural Review: ✅ APPROVED

### 1. Architectural Alignment and Boundaries

**Assessment**: Well-structured with clear boundaries

```
┌─────────────────────────────────────────────────────────┐
│                    Consumer Code                         │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  S360Client (Facade)                     │
│  - Single entry point for all operations                 │
│  - Coordinates auth, caching, API calls                  │
└────┬──────────────┬─────────────────┬───────────────────┘
     │              │                 │
┌────▼────┐   ┌────▼────┐      ┌─────▼─────┐
│  Auth   │   │  Cache  │      │ Endpoints │
│ Module  │   │ Module  │      │  Module   │
└────┬────┘   └────┬────┘      └─────┬─────┘
     │              │                 │
┌────▼────┐   ┌────▼────┐      ┌─────▼─────┐
│ Azure   │   │  Local  │      │   S360    │
│Identity │   │  Files  │      │   APIs    │
└─────────┘   └─────────┘      └───────────┘
```

### 2. API and Data Contracts

**Recommendation**: Define explicit contracts

```python
# Proposed interfaces (for architect-doc.md)

class S360Client:
    def __init__(self, config: S360Config | None = None) -> None: ...
    def get_eta_history(self, kpi_id: str, action_item_id: str) -> list[EtaHistoryItem]: ...
    def save_etas(self, updates: list[EtaUpdate]) -> SaveResult: ...
    def get_current_user(self) -> UserInfo: ...
    def discover_endpoints(self) -> list[EndpointInfo]: ...

@dataclass
class S360Config:
    base_url: str = "https://api.vnext.s360.msftcloudes.com/v1"
    timeout_seconds: int = 30
    cache_enabled: bool = True
    cache_expiry_minutes: int = 60
    cache_directory: Path | None = None  # None = use default AppData

@dataclass
class EtaHistoryItem:
    id: str
    eta: datetime
    status: str
    notes: str
    created_at: datetime

@dataclass  
class EtaUpdate:
    kpi_id: str
    service_id: str
    action_item_id: str
    new_eta: datetime
    notes: str
    sla_type: str = "InSla"

@dataclass
class SaveResult:
    success: bool
    failed_items: list[str]
    error_message: str | None
```

### 3. Security and Privacy

| Concern | Mitigation |
|---------|------------|
| Token exposure in logs | Never log tokens; mask in debug output |
| Token exposure in cache | Do NOT cache tokens - azure-identity handles this |
| Cache contains sensitive data | Store in user's AppData (per-user isolation) |
| Credential theft | Use AzureCliCredential (no credentials in code) |

**Required**: Add warning in README about not committing cache files.

### 4. Scalability and Resilience

**Current scope**: Single-user local tool - scalability not a concern.

**Resilience patterns to implement**:
- Retry with exponential backoff for transient failures (429, 503)
- Circuit breaker pattern NOT needed for v1 (single-user)
- Graceful degradation: return cached data if API fails (configurable)

### 5. Dependency Analysis

| Dependency | Risk | Mitigation |
|------------|------|------------|
| azure-identity | Low | Microsoft-maintained, stable |
| azure-core | Low | Required by azure-identity |
| requests | Low | Industry standard |
| S360 API | Medium | Version pin, defensive parsing |

### 6. Failure Isolation

```
Failure Mode          → Impact           → Handling
─────────────────────────────────────────────────────
Auth failure          → No operations    → Clear error, suggest az login
API timeout           → Single op fails  → Retry once, then raise
API 5xx               → Single op fails  → Return cached (if available)
Cache corruption      → Increased API    → Delete cache, continue
Network down          → All ops fail     → Clear error message
```

### 7. Implicit Behavior Questions (for PO)

These are defaults that may surprise users:

1. **requests timeout**: Default is `None` (infinite). Design specifies 30s - good.
2. **JSON encoding**: `requests` uses UTF-8 by default - expected for S360.
3. **Cache file permissions**: Will use OS defaults. On Windows, AppData is user-isolated.
4. **Token refresh**: `AzureCliCredential` auto-refreshes. User doesn't need to handle.

**Decision**: All defaults are acceptable for this use case. Document in README.

### 8. New User Stories Identified

None - design is appropriate for scope.

### Architect Approval

✅ **APPROVED** for implementation

The design is:
- Well-bounded with clear module separation
- Secure (no credential storage, token masking)
- Resilient (retry, caching, graceful errors)
- Testable (injectable dependencies)

**Priority recommendations for Developer**:
1. Implement custom exceptions first (affects all modules)
2. Use dataclasses for all DTOs (type safety)
3. Add `__all__` to each module (explicit public API)
4. Use `logging.getLogger(__name__)` pattern
