# GCP-0027 Architect Role Notes

## Role: Architect
## Date: 2025-07-22

## Key Decisions

### D1: Reorder computation in gcp_status.py
Move the output validation block (lines 78-91) above the `_generate_next_steps()` call (line 53). This is required because `_generate_next_steps` needs the validation results to generate remediation text. Minimal-change approach — just reorder, don't restructure.

### D2: _generate_next_steps signature
Add `required_outputs: list[dict] | None = None` as an optional parameter. Reuse the existing dict structure `[{"path", "type", "valid"}]` — no new data classes needed.

### D3: Remediation text format
Use type-based mapping: `file` → "Create file:", `dir` → "Create directory:", fallback → "Ensure <type>:". Append the resolved path. This is forward-compatible with new output types.

### D4: server.py rendering placement
Required outputs section goes between DoR/DoD bullets and the Next Steps header. Only render when outputs list is non-empty. Use checklist format with `[x]`/`[ ]` indicators.

### D5: bootstrap-instructions.md scope
Remove `gcp_mark_dor`/`gcp_mark_dod` references and `evidence=` parameters. Update version header. Do NOT rewrite the entire file.

## Architectural Concerns Addressed
- **Call ordering**: AR-1 identifies a sequencing issue — must fix before implementing
- **Coupling**: AR-3 addresses forward-compatibility for new output types
- **Blast radius**: AR-7 confirms all changes are additive or removals — clean rollback via git revert

## Escalations
None. No scope changes or new user stories needed.

## Approval
Design approved with AR-1 adjustment (reorder computation blocks).
