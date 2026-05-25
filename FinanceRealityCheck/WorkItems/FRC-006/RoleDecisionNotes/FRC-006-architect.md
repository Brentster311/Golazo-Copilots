# FRC-006 Architect Notes

## Architecture Decision
- Use a standalone frontend/ React SPA to consume local API contracts from FRC-005.
- Encapsulate HTTP calls in a dedicated API module.
- Keep route-level components small and deterministic.

## Constraints
- No backend behavior changes for FRC-006.
- No dependency on external cloud services for UI startup.
- Error boundaries must be explicit and user-readable.
