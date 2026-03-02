# GCP-0058 — Program Manager Notes

## Decisions
1. Implement capability-registry initialization only within `golazo_create_workitem` scope.
2. Enforce strict create-if-missing behavior for root `capabilities.yaml` with no mutation when the file already exists.
3. Preserve existing create-workitem response contract and success semantics.
4. Require explicit automated coverage for both file-absent and file-present branches.

## Assumptions Applied
- Interface is MCP/API tool invocation flow (not CLI UX redesign).
- Workspace storage is file-based and root-scoped for `capabilities.yaml`.
- “First call” is interpreted as first successful create-workitem call in a workspace where the file is absent.
- Standard use pattern is single-invocation workflow; concurrency hardening is desirable but not expanded beyond story scope.

## Rationale
- Keeps blast radius narrow and aligned with user story boundaries.
- Delivers deterministic registry availability for downstream capability-aware tooling.
- Preserves backward compatibility for existing repositories that already maintain registry content.

## Rejected Options
- Manual/bootstrap-only prerequisite for capability registry creation.
- Automatic creation in unrelated tools or global startup paths.
- Any overwrite/regeneration logic for existing `capabilities.yaml`.

## Risks & Mitigations
- Risk: concurrent first-time creates could race on file creation.
  - Mitigation: prefer atomic create-if-missing semantics and idempotent no-op behavior.
- Risk: template inconsistency across versions.
  - Mitigation: use a single authoritative default template source and assert shape in tests.
- Risk: hidden operational failures if initialization errors are not separated.
  - Mitigation: emit branch/result telemetry and classify initialization failures explicitly.

## Handoff Notes
- Architect: confirm placement of initialization step in `golazo_create_workitem` flow and failure-mode handling.
- QA: validate absent/present branch tests, idempotency guarantees, and unchanged create-workitem success behavior.
- Developer: implement minimal scoped change without introducing mutation of existing `capabilities.yaml`.
