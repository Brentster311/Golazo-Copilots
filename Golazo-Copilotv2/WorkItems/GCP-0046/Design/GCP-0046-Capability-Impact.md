# GCP-0046 Capability Impact Analysis

## Impact Analysis Results

### Files Analyzed
- `golazo-copilot/src/golazo_copilot/core/transitions.py`
- `.github/copilot-instructions.md`

### Directly Affected Capabilities
| Capability | Impact |
|-----------|--------|
| **transitions** | Role ordering, phase mapping, and forward/backward transition validation — all three constants (`TRANSITIONS`, `PHASE_MAP`, `ROLE_ORDER`) are modified |

### Transitively Affected Capabilities
| Capability | Impact |
|-----------|--------|
| **tool-transition** | Uses `validate_transition()` and `is_backward_transition()` — both will correctly handle the new role since they read from the updated dicts. No code changes needed in this capability. |
| **tool-status** | Iterates `ROLE_ORDER` for progress display — will automatically show the new role. `roles_total` will change from 9 to 10. No code changes needed. |
| **mcp-server** | Routes calls to tool modules — no changes needed; the server dispatches by tool name, not by role name. |

### Contract Implications
- **New public interface:** `"domain-expert"` is now a valid value for the `role` parameter in `gcp_transition` and `gcp_status`
- **Changed behavior:** `program-manager` can no longer transition forward to `quality-assurance` directly — must go through `domain-expert`
- **No removed interfaces:** All existing role names remain valid

### Risk Assessment
- **Low risk:** All transitively affected capabilities read from the constants; they don't need code changes
- **Medium risk:** Existing tests that assert PM → QA transitions will fail and need updating
- **No risk:** The new role file is purely additive — no existing role files are modified
