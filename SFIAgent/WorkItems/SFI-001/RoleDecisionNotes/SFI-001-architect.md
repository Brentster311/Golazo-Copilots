# SFI-001 Architect Decision Notes

## Date: 2026-02-03

### Review Summary

**Verdict**: APPROVED for implementation

### Key Architectural Decisions

#### 1. Facade Pattern for Client
**Decision**: Single `S360Client` class as entry point
**Rationale**: Simplifies consumer code, hides complexity of auth/cache coordination.

#### 2. Dataclasses for DTOs
**Decision**: Use `@dataclass` for all data transfer objects
**Rationale**: Type safety, auto-generated `__init__`, `__repr__`, IDE support.

#### 3. No Token Caching
**Decision**: Do NOT cache bearer tokens locally
**Rationale**: `AzureCliCredential` handles token caching internally. Storing tokens ourselves is a security anti-pattern.

#### 4. Cache Location
**Decision**: Use `%LOCALAPPDATA%\s360_client\cache\` on Windows
**Rationale**: Standard location, user-isolated, survives app reinstalls.

```python
from pathlib import Path
import os

def get_default_cache_dir() -> Path:
    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    else:
        base = Path.home() / '.cache'
    return base / 's360_client' / 'cache'
```

#### 5. Retry Strategy
**Decision**: Retry once with 2s delay for 429, 503, 504 only
**Rationale**: Simple, covers transient failures, doesn't mask real errors.

#### 6. Logging Pattern
**Decision**: `logging.getLogger(__name__)` in each module
**Rationale**: Standard Python pattern, allows granular log control.

### Security Decisions

| Decision | Rationale |
|----------|-----------|
| No credentials in code | Use Azure CLI session |
| No token logging | Prevent credential leaks |
| AppData for cache | User-isolated storage |
| No cache encryption | AppData is user-protected; encryption adds complexity |

### Contract Definitions

Defined explicit interfaces in Review Comments. Key types:
- `S360Config`: Configuration dataclass
- `EtaHistoryItem`: Response model for ETA history
- `EtaUpdate`: Request model for saving ETAs
- `SaveResult`: Response model for save operations
- `UserInfo`: Current user information

### Module Dependencies

```
s360_client/
├── __init__.py      → Exports S360Client, exceptions, models
├── auth.py          → Depends on: azure-identity, config
├── cache.py         → Depends on: config (no external deps)
├── client.py        → Depends on: auth, cache, endpoints
├── config.py        → No dependencies
├── exceptions.py    → No dependencies
├── models.py        → No dependencies
└── endpoints/
    ├── __init__.py
    ├── action_items.py → Depends on: requests, models, exceptions
    └── discovery.py    → Depends on: requests, models, exceptions
```

### Questions Resolved

| Question | Resolution |
|----------|------------|
| Token caching | Let azure-identity handle it |
| Async support | Defer to future story |
| Rate limit handling | Simple retry with backoff |
| Cache format | JSON (human-readable, debuggable) |

### Handoff to Developer

1. Start with `exceptions.py` and `models.py` (no dependencies)
2. Then `config.py` (defines defaults)
3. Then `auth.py` (needs config)
4. Then `cache.py` (needs config)
5. Then `endpoints/` modules (need models, exceptions)
6. Finally `client.py` (facade that ties it together)

### No New User Stories

The design is appropriate for the stated scope. No architectural changes required.
