# SFI-002 Architect Notes

## Architectural Review Summary
Reviewed design and QA comments for accia-s360 package refactoring.

## Key Architectural Decisions

### 1. Package Boundaries
- Package has clear single responsibility: S360 API client
- No cross-cutting concerns (logging, config, etc.) forced on consumers
- Cache is internal detail, should be optional

### 2. Public API Surface
Defined explicit public contract:
- `S360Client` - Main entry point
- `S360Auth` - Authentication helper (if needed separately)
- `__version__` - Package version

All other modules are internal implementation.

### 3. Error Handling Contract
Recommended custom exception hierarchy:
- `S360Error` - Base exception
- `S360AuthError` - Authentication failures
- `S360ApiError` - API request failures with status code

### 4. Security Considerations
- Tokens must not be logged
- Cache may contain PII - document implications
- Consider `cache_enabled` parameter for consumers who want to disable

## Implicit Assumptions Surfaced

| Assumption | Default Behavior | Recommendation |
|------------|------------------|----------------|
| requests timeout | None (infinite) | Set 30s explicit timeout |
| JSON encoding | Assumes UTF-8 | Verify response handling |
| Cache permissions | OS default | Document security implications |

## Dependencies Approved
- `azure-identity>=1.15.0,<2.0.0` - Stable, Microsoft-maintained
- `requests>=2.31.0` - Ubiquitous, stable

## Risks Assessed
- **Blast radius:** Low - client library only
- **Rollback:** Safe - version pinning supported
- **State:** No shared state, no migrations

## Recommendations for Developer
1. Add explicit request timeout (30 seconds)
2. Define custom exception classes
3. Document public API in `__init__.py`
4. Add `py.typed` marker for type checking support

## Decision
✅ **Approved for development** - No blocking issues

## Next Role
Developer to implement package structure
