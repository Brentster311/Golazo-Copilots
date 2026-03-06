# GCP-0068 Architect Decision Notes

## Architectural verdict
- Proceed with focused helper-based executable resolution in update preflight.

## Constraints
- Keep `golazo_update` public interface backward compatible.
- Limit behavior change to preflight executable resolution and error messaging.
- Preserve timeout and login validation semantics.

## Security and resilience
- No new attack surface introduced.
- Improve diagnosability via distinct failure categories.

## Implementation guidance
- Use explicit resolver helper (`shutil.which`) with Windows-aware fallback (`az.cmd`).
- Route preflight subprocess through resolved executable path.
- Add tests for platform-specific resolution and existing successful flows.
