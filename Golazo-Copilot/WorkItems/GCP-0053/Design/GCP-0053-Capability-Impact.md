# GCP-0053 Capability Impact Analysis

**Work Item:** GCP-0053 — POA Closure Gate  
**Author:** Architect  
**Date:** 2026-02-22  

---

## Impact Analysis Input

**Files analyzed:**
- `golazo-copilot/src/golazo_copilot/core/types.py`
- `golazo-copilot/src/golazo_copilot/core/transitions.py`
- `golazo-copilot/src/golazo_copilot/core/output_validator.py`
- `golazo-copilot/src/golazo_copilot/tools/gcp_transition.py`
- `golazo-copilot/src/golazo_copilot/tools/gcp_status.py`

---

## Results: 10 Capabilities Affected

### Directly Affected (5)

| Capability | Description | GCP-0053 Change |
|-----------|------------|----------------|
| **state-model** | Pydantic types for work-item state (`WorkItemState`, `Deviation`, `RoleHistoryEntry`) | Add `closure_pending: bool = False` to `WorkItemState`. Additive, backward-compatible. |
| **transitions** | Role ordering, phase mapping, and forward/backward transition validation | **No code changes.** `TRANSITIONS["retrospective"]` already includes `"project-owner-assistant"`. Impact is indirect — the transition tool uses this dict but the dict itself doesn't change. |
| **output-validation** | Parse Required Outputs from role files and validate file/dir/git artefacts | Add `closure_only: bool = False` to `OutputSpec`. Modify `parse_required_outputs()` to recognize `<!-- closure-only -->` preceding-line annotation. Update regex defensively to strip inline HTML comments. |
| **tool-transition** | Transition between workflow roles with gate enforcement and consent checks | Set `closure_pending = True` on state when transitioning from `retrospective` → `project-owner-assistant` in `complete` profile. Filter closure-only `OutputSpec` entries based on `state.closure_pending`. |
| **tool-status** | Comprehensive workflow status: progress, outputs, stale-file detection, registry hints | Include `closure_pending` in status response. Filter closure-only outputs from validation. Add closure-specific next steps in `_generate_next_steps()`. Update `format_status_result()` to display closure mode indicator. |

### Transitively Affected (5)

| Capability | Description | Risk Assessment |
|-----------|------------|-----------------|
| **mcp-server** | MCP server entry point — registers all tools, routes calls, formats responses | **Low risk.** `format_status_result()` needs a small update to display `closure_pending`. `format_transition_result()` unchanged — the response shape already supports extra fields. |
| **persistence** | Atomic JSON read/write for work-item state files | **No risk.** Pydantic serialization handles the new `closure_pending` field automatically. `load_state()` / `save_state()` need no changes. |
| **tool-create-workitem** | Create a new work item with initial state and role instructions | **No risk.** New work items get `closure_pending=False` via Pydantic default. No code changes needed. |
| **tool-consent** | Record and validate Project Owner consent for workflow deviations | **No risk.** Consent logic is independent of closure state. No interaction. |
| **tool-role-context** | Assemble a self-contained context bundle for a role — instructions, state, input artifacts, previous notes | **Low risk.** Bundles include state, so `closure_pending` will be included automatically. No code changes needed. |

---

## Change Surface Summary

| File | Lines Changed (est.) | Risk |
|------|---------------------|------|
| `core/types.py` | +1 (add field) | Very Low |
| `core/output_validator.py` | +15 (field, annotation parsing, regex) | Medium |
| `tools/gcp_transition.py` | +10 (set flag, filter outputs) | Medium |
| `tools/gcp_status.py` | +12 (pass flag, filter outputs, next steps) | Medium |
| `server.py` | +5 (format closure indicator) | Low |
| `roles/defaults/project-owner-assistant.md` | +3 (add closure output) | Low |
| `roles/defaults/retrospective.md` | +8 (add transition guidance section) | Low |
| `core/transitions.py` | 0 (no changes) | None |

**Total estimated: ~54 lines of production code + role file updates**

---

## Dependency Graph

```
WorkItemState (types.py)
    └── closure_pending: bool = False
            ├── gcp_transition.py — SETS flag on retro→POA (complete)
            ├── gcp_status.py — READS flag for display + next steps
            └── persistence.py — serializes/deserializes (no change needed)

OutputSpec (output_validator.py)
    └── closure_only: bool = False
            ├── parse_required_outputs() — tags spec from <!-- closure-only -->
            ├── gcp_transition.py — FILTERS specs before validation
            └── gcp_status.py — FILTERS specs before display

Role Files
    ├── project-owner-assistant.md — ADDS closure output with annotation
    └── retrospective.md — ADDS transition guidance section
```

---

## Test Impact

All 19 test cases from the QA test plan (GCP-0053-Test-Cases.md) map cleanly to the affected capabilities:

| Capability | Test Cases |
|-----------|-----------|
| state-model | TC-04, TC-05, TC-10, TC-13 |
| output-validation | TC-08, TC-09, TC-11, TC-12, TC-16, TC-17, TC-18 |
| tool-transition | TC-01, TC-02, TC-03, TC-04 |
| tool-status | TC-06, TC-07, TC-15 |
| role files | TC-14 |
| regression | TC-19 |

---

## Risk Summary

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Backward compat break (missing field in old state.json) | Low | High | Pydantic default handles it; TC-10 covers |
| Output regex captures HTML comment in path | Low (prevented by design) | Medium | Preceding-line convention + defensive regex; TC-16 covers |
| Express/spike accidentally get closure enforcement | Low | Medium | Profile guard in gcp_transition; TC-02/TC-03 cover |
| format_status_result display breaks | Low | Low | Simple string addition; existing formatter tests verify shape |
