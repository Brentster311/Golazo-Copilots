# GCP-0057 QA Review Comments

## Overall Assessment
- Design is implementable and scoped.
- Terminology shift to `orchestrator-only` is clearer and should reduce confusion.

## Strengths
- Explicit preflight gate addresses missing-instructions root cause.
- `orchestrator-only` mode minimizes workspace mutation while enforcing prerequisites.
- `force=true` overwrite behavior is explicitly planned.

## Gaps / Clarifications Needed
1. Specify exactly which tools are blocked when instructions are missing.
2. Confirm `golazo_status(work_item_id="")` (version query) remains available without bootstrap.
3. Define backward compatibility for any legacy alias handling (`spine-only` accepted or not).

## Risk-Focused Recommendations
- Ensure blocked response includes a copy-paste-safe command with provided `workspace_path`.
- Add tests for malformed mode values and unknown mode error text.
- Validate no unrelated files are created in `orchestrator-only` mode.

## Architect Notes
- Gate placement should be enforced in server dispatch for consistency across tools.
- Preflight check must be scoped to workflow tools only to avoid blocking diagnostics/bootstrap itself.
- Public contract impact is additive (`mode` parameter); default behavior must remain full bootstrap for backward compatibility.
- Security posture is unchanged; no new external entry points or secret handling paths are introduced.
- Ensure remediation message avoids leaking environment details beyond required local path guidance.

