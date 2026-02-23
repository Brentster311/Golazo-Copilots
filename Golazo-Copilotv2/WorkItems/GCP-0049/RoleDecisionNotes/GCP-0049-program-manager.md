# GCP-0049 — Program Manager Notes

## Design Decisions
1. Follow existing 3-layer tool pattern (registration → dispatch → logic) for consistency
2. Eager file reading over lazy loading — subagents may not have filesystem access
3. 100KB default cap with truncation — protects LLM context windows
4. Previous role notes limited to immediately preceding role (not full history) to keep bundle lean

## Sequencing
- Single deliverable: `tools/gcp_role_context.py` + server.py registration + tests
- No phased rollout needed — it's a new additive tool

## Open Questions
- None — user story is sufficiently detailed
