# SFI-001 Design Document: S360 API Direct Access Library

## Summary

A Python library that enables programmatic access to Microsoft S360 (Service 360) APIs using Azure CLI authentication. The library will replicate existing API functionality from the reference project, provide mechanisms to discover additional endpoints, and support local caching for improved performance.

---

## Problem Statement

Currently, interacting with S360 requires either:
1. Manual browser-based access (slow, not automatable)
2. Using the existing SFI_Agent project (tightly coupled to specific use cases)

Developers need a clean, reusable library that:
- Handles Azure authentication transparently
- Provides typed interfaces to S360 APIs
- Enables discovery of undocumented endpoints
- Supports automation and integration scenarios

---

## Business Case

### Why Now
- Existing reference project proves the concept works
- Need for cleaner, more maintainable codebase
- Growing demand for S360 automation across teams

### Impact
- Reduced manual effort for S360 operations
- Enables building higher-level automation tools
- Foundation for future CLI and integration tools

### KPIs
- Successful authentication rate
- API call success rate
- Number of discovered/documented endpoints
- Developer adoption (future)

---

## Stakeholders

| Role | Name | Responsibility |
|------|------|----------------|
| Developer | Brent | Primary user, maintainer |
| End Users | Internal teams | API consumers |

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR1 | Authenticate via Azure CLI credential | Must |
| FR2 | Call GetEtaHistoryById endpoint | Must |
| FR3 | Call SaveETAsByIds endpoint | Must |
| FR4 | Get current user info via MS Graph | Must |
| FR5 | Discover available S360 API endpoints | Should |
| FR6 | Cache API responses locally | Should |
| FR7 | Support configurable timeout and retry | Should |

---

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR1 | Python version | 3.10+ |
| NFR2 | API timeout | 30s (configurable) |
| NFR3 | Cache storage | JSON files in AppData |
| NFR4 | Type safety | Full type hints |
| NFR5 | Test coverage | >80% |
| NFR6 | Documentation | README + docstrings |

---

## Proposed Approach (High Level)

### Project Structure
```
SFIAgent/
├── src/
│   └── s360_client/
│       ├── __init__.py
│       ├── auth.py          # Azure authentication
│       ├── client.py        # Main S360 client
│       ├── endpoints/       # API endpoint modules
│       │   ├── __init__.py
│       │   ├── action_items.py
│       │   └── discovery.py
│       ├── cache.py         # Local caching
│       ├── config.py        # Configuration
│       └── models.py        # Data models
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_client.py
│   └── test_endpoints.py
├── pyproject.toml
├── README.md
└── WorkItems/
```

### Authentication Flow
1. Initialize `AzureCliCredential`
2. Request token for S360 scope
3. Cache token in memory (auto-refresh handled by azure-identity)
4. Attach bearer token to all API requests

### API Discovery Strategy
1. Start with known endpoints from reference project
2. Probe common REST patterns (e.g., `/Services`, `/KPIs`, `/Users`)
3. Parse error responses for hints about valid endpoints
4. Document discovered endpoints in structured format

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Extend existing SFI_Agent | Less work | Coupled to specific use case | Rejected |
| Use Selenium/Playwright | Access full web UI | Fragile, slow | Rejected |
| Create async library | Better performance | Added complexity | Deferred |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| S360 API changes | Medium | High | Version pin, error handling |
| Auth scope changes | Low | High | Configurable scopes |
| Rate limiting | Unknown | Medium | Implement retry with backoff |
| Undocumented API behavior | High | Medium | Extensive error handling |

### Open Questions
1. Does S360 have OpenAPI/Swagger documentation? (To investigate)
2. Are there rate limits on API calls?
3. What other endpoints exist beyond ActionItems?

---

## Dependencies

### External
- `azure-identity` >= 1.23.0
- `azure-core` >= 1.24.0
- `requests` >= 2.25.0

### Infrastructure
- Azure CLI installed and authenticated
- Network access to S360 APIs
- Valid Microsoft corporate account

---

## Migration / Rollout / Rollback Plan

### Rollout
1. Phase 1: Core library with known endpoints
2. Phase 2: Discovery mechanism
3. Phase 3: Extended API coverage

### Rollback
- Not applicable (new standalone project)
- Users can pin to specific version if issues arise

---

## Observability Plan

### Logging
- Standard Python logging module
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log API calls, auth events, cache hits/misses

### Local Diagnostics
- Cache inspection utilities
- Token validation helpers
- Connection test functions

---

## Test Strategy Summary

| Test Type | Coverage | Tools |
|-----------|----------|-------|
| Unit tests | Core logic, parsing | pytest, pytest-mock |
| Integration tests | Auth flow (requires az login) | pytest |
| Mock tests | API responses | responses library |

### Test Scenarios
1. Successful authentication
2. Auth failure handling
3. API success responses
4. API error responses (4xx, 5xx)
5. Network timeout handling
6. Cache hit/miss scenarios
7. Token refresh scenarios
