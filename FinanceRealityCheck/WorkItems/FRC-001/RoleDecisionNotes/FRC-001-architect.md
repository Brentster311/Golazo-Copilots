# FRC-001 Architect Notes

## Architecture Decision
Approved architecture direction with constraints:
- Layered boundaries between connectors, normalization, persistence, and planning logic.
- API contract-driven behavior with explicit error taxonomy.
- Local encrypted persistence as non-negotiable requirement.

## Key Architectural Requirements
- Canonical transaction model is required across connectors.
- Sync must be idempotent and account-isolated for partial failure tolerance.
- Storage and logs must not expose sensitive plaintext.
- Service defaults (sqlite transaction semantics and datetime parsing) must be tested explicitly.

## Security/Privacy Review Outcome
- Security posture acceptable if encryption-at-rest is implemented for payloads and tokens and key management remains local and outside repo.

## Capability Registry Outcome
- Impact analysis over current design artifacts reports zero affected capabilities due placeholder registry.
- Follow-up action: register real capabilities once implementation files exist.

## Decision
Architect gate approved for implementation.
