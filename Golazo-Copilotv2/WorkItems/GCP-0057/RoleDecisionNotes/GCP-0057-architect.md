# GCP-0057 — Architect Notes

## Architectural Decisions
1. Treat orchestrator instructions as a hard prerequisite for workflow-role execution.
2. Implement preflight guard at server dispatch boundary for uniform enforcement.
3. Keep `golazo_bootstrap` default/full behavior backward compatible; add `orchestrator-only` as additive mode.
4. Keep failure mode explicit and recoverable via a single remediation command.

## Constraints
- Avoid hidden file mutation in non-bootstrap tools.
- Do not block bootstrap itself or version-only status checks.
- Keep changes localized to bootstrap tool, server schemas/dispatch, and tests.

## Security & Reliability Assessment
- Security impact is low (no new external network surface).
- Reliability improves via deterministic prerequisites and explicit remediation.
- Main operational risk is accidental over-blocking, mitigated by scope-limited preflight checks.

## Handoff to Developer
- Implement with minimal API churn and clear invalid-mode validation.
- Update user-facing text to “orchestrator instructions” / `orchestrator-only` consistently.
- Add regression coverage for mode handling, force semantics, and blocked/unblocked workflow paths.

