# GCP-0031 Review Comments

## Design Review

### Overall Assessment
Design is comprehensive and correctly maps every DoR/DoD touchpoint. The 10-step approach is well-sequenced (leaf-first deletion). The `skip_dor` → `skip_outputs` rename is the right call.

### Findings

#### Finding 1: Pydantic extra="ignore" placement
- **Severity**: Medium
- **Details**: Design says add `model_config = ConfigDict(extra="ignore")` to WorkItemState. Need to verify this doesn't conflict with existing model_config if any.
- **Recommendation**: Check current WorkItemState model_config before implementing. If none exists, add it.

#### Finding 2: _generate_next_steps definition phase logic
- **Severity**: Medium
- **Details**: After removing DoR-based steps, the definition phase needs output-aware logic. GCP-0027 already added remediation for missing outputs, but there may be a gap: when all outputs are present, what does definition phase say?
- **Recommendation**: When all outputs are present in definition phase → "All outputs present — transition to next role". When missing → show remediation (already done).

#### Finding 3: Consent action backward compat in state files
- **Severity**: Low
- **Details**: Existing state.json files may have deviations with `action: "skip_dor"`. After rename, these will have the old string in audit data. This is fine — deviation records are historical, not functional.
- **Recommendation**: No migration needed. Document that old deviation records retain original action strings.

### Scope Verification
All 7 ACs map to specific design steps. No scope creep.

---

## Architect Notes

### AR-1: Backward compatibility strategy is sound
`extra="ignore"` in Pydantic is the correct approach. Old state files with dor/dod fields will silently drop those fields on load. No migration needed.

### AR-2: Consent action rename — check all consumers
The `skip_dor` string appears in: `gcp_consent.py`, `gcp_transition.py` (output validation bypass), `server.py` (enum), and ~15 test locations. All must be updated atomically.

### AR-3: _generate_next_steps must still work for all phases
After removing DoR/DoD params, the function signature is `(state, required_outputs)`. Verify it handles: definition (with/without outputs), development (role-specific), completion (done message).

### Summary
Design approved. No new user stories needed.
