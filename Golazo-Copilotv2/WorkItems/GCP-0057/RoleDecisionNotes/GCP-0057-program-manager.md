# GCP-0057 — Program Manager Notes

## Decisions
1. Make orchestrator-instructions bootstrap a required prerequisite for workflow tool usage.
2. Add `golazo_bootstrap(mode="orchestrator-only")` for minimal setup.
3. Preserve `force=true` overwrite behavior for explicit instructions replacement.
4. Keep full bootstrap mode for backward compatibility.

## Rationale
- Eliminates context ambiguity and repeated token-heavy fallback messaging.
- Gives users an explicit, minimal remediation path.
- Keeps side effects explicit (only bootstrap writes files).

## Rejected Options
- Runtime fallback injection in create/status responses.
- Implicit auto-bootstrap/write files during create/status.

## Risks & Mitigations
- Risk: breaking existing optional-bootstrap workflows.
  - Mitigation: clear remediation messaging and backward-compatible full bootstrap mode.
- Risk: over-blocking calls that should remain available.
  - Mitigation: scope required-instructions gate to workflow tools only.

## Handoff Notes
- QA should validate `orchestrator-only` mode, force overwrite behavior, and missing-instructions gate.
- Architect should confirm gate placement at server/tool boundary for consistency.

