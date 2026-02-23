# GCP-0053 Architect Decision Notes

**Work Item:** GCP-0053 — POA Closure Gate  
**Role:** Architect  
**Date:** 2026-02-22  

---

## Architectural Decisions

### AD-1: `closure_pending` as a Terminal, One-Shot Boolean

**Decision:** Add `closure_pending: bool = False` to `WorkItemState`. Set once on retro→POA in complete profile. Never cleared.

**Rationale:**
- Simplest possible implementation — a single boolean with a Pydantic default.
- No schema version bump needed (additive, backward-compatible).
- "Never cleared" eliminates an entire class of lifecycle bugs (when to clear, what if cleared too early, etc.).
- The flag is idempotent: setting `True` when already `True` is a no-op.

**Rejected alternatives:**
- Derive from `role_history` — fragile, requires complex scanning, semantically ambiguous (rework vs. closure).
- New `closure` phase literal — forces enum change, breaks PHASE_MAP consumers, conflates orthogonal concepts.
- 11th role — breaks ROLE_ORDER, VALID_ROLES, progress calculations, test assertions, subagent matrix. Cost far exceeds benefit.

---

### AD-2: Preceding-Line Annotation Convention for Conditional Outputs

**Decision:** Use `<!-- closure-only -->` on a dedicated line immediately before the output spec it applies to.

**Rationale:**
- Avoids the inline HTML-in-path bug entirely (the existing regex captures everything after the colon as the path).
- Works naturally with the existing `if stripped.startswith('<!--'): continue` logic — just needs a small enhancement to tag the next line instead of skipping.
- Extensible: if future roles need other conditional annotations (e.g., `<!-- spike-only -->`), the same preceding-line pattern works.

**Convention definition:**
- The comment must be exactly `<!-- closure-only -->` (with single spaces, lowercase, no extra whitespace).
- It must be on its own line, immediately before the output spec line.
- If a non-output line intervenes, the annotation is discarded (safety against misplacement).

**Defensive addition:** Also update the output line regex to strip inline HTML comments:
```python
r'^\s*-\s*(file|dir|git-branch|git-log):\s*(.+?)\s*(?:<!--.*?-->)?\s*$'
```
This is belt-and-suspenders: the preceding-line convention makes inline comments unnecessary, but the regex handles them correctly if someone adds one.

---

### AD-3: `OutputSpec.closure_only` Field with Caller-Level Filtering

**Decision:** Add `closure_only: bool = False` to `OutputSpec`. Callers filter based on `state.closure_pending`.

**Rationale:**
- Keeps annotation metadata with the spec (clean data model).
- Filtering is trivial: `[s for s in specs if not s.closure_only or closure_mode]`.
- Both `gcp_transition` and `gcp_status` need to filter — doing it at the caller avoids `parse_required_outputs()` needing state context as a parameter.
- The `parse_required_outputs()` function remains state-agnostic (it just parses and tags).

---

### AD-4: Profile Guard — Complete Only

**Decision:** The `closure_pending` flag is only set when `state.profile == "complete"`. Express and spike profiles are unaffected.

**Rationale:**
- Express and spike profiles have shorter workflows where formal closure is not required.
- The retro→POA transition remains *allowed* for all profiles (it's in `TRANSITIONS`), but only `complete` profile gets the `closure_pending` flag and the role-instruction mandate.
- Single guard clause in `gcp_transition.py` keeps the logic simple and auditable.

---

### AD-5: Status Display — Separate `closure_pending` Field, Not Phase Override

**Decision:** Include `closure_pending` as a separate boolean in the status response. Do not override `current_phase`.

**Rationale:**
- `PHASE_MAP` derives phase from role deterministically. Making it context-dependent would require changes throughout the codebase.
- A separate field is explicit and doesn't confuse consumers that expect `current_phase` to be one of three values.
- The `format_status_result()` function adds a visual `**CLOSURE MODE**` indicator next to the role name.

---

### AD-6: No Changes to `TRANSITIONS` Dict or `ROLE_ORDER`

**Decision:** `TRANSITIONS` and `ROLE_ORDER` remain unchanged.

**Rationale:**
- `TRANSITIONS["retrospective"]` already lists `"project-owner-assistant"` as the forward target. The transition is allowed.
- Enforcement comes from the role instructions (retrospective tells the agent to transition to POA in complete mode) and from the `closure_pending` flag (which enables closure-specific output gating).
- `ROLE_ORDER` stays at 10 roles. No 11th role. Progress calculations are unaffected.

---

## Implementation Plan

### Phase 1: State Model (types.py)
**File:** `golazo-copilot/src/golazo_copilot/core/types.py`
- Add `closure_pending: bool = False` to `WorkItemState` class, after the `deviations` field.

### Phase 2: Output Validator (output_validator.py)
**File:** `golazo-copilot/src/golazo_copilot/core/output_validator.py`

1. Add `closure_only: bool = False` field to `OutputSpec` dataclass.
2. Modify `parse_required_outputs()`:
   - Add `next_is_closure_only` flag, initially `False`.
   - When encountering `<!-- closure-only -->` exactly, set flag to `True` and `continue`.
   - When creating `OutputSpec`, pass `closure_only=next_is_closure_only`, then reset flag.
   - Reset flag on non-matching lines too (prevent stale annotation).
3. Update `line_pattern` regex to defensively strip inline HTML comments:
   ```python
   line_pattern = r'^\s*-\s*(file|dir|git-branch|git-log):\s*(.+?)\s*(?:<!--.*?-->)?\s*$'
   ```

### Phase 3: Transition Tool (gcp_transition.py)
**File:** `golazo-copilot/src/golazo_copilot/tools/gcp_transition.py`

1. After computing output specs, filter closure-only specs:
   ```python
   closure_mode = getattr(state, 'closure_pending', False)
   output_specs = [s for s in output_specs if not s.closure_only or closure_mode]
   ```
2. After updating state (role, phase, history) but before `save_state()`, add:
   ```python
   if (
       state.profile == "complete"
       and current_role == "retrospective"
       and role == "project-owner-assistant"
   ):
       state.closure_pending = True
   ```

### Phase 4: Status Tool (gcp_status.py)
**File:** `golazo-copilot/src/golazo_copilot/tools/gcp_status.py`

1. After parsing output specs, filter closure-only specs:
   ```python
   closure_mode = getattr(state, 'closure_pending', False)
   output_specs = [s for s in output_specs if not s.closure_only or closure_mode]
   ```
2. Add `closure_pending` to the return dict:
   ```python
   "closure_pending": getattr(state, 'closure_pending', False),
   ```
3. Update `_generate_next_steps()` signature to accept `closure_pending: bool = False`.
4. Add closure-specific next steps when `closure_pending and state.current_role == "project-owner-assistant"`:
   ```python
   if closure_pending and state.current_role == "project-owner-assistant":
       steps.append("Perform closure: verify acceptance criteria, confirm final commit, create closure.md")
       steps.append("Update User Story status to IMPLEMENTED")
       return steps
   ```
5. Update caller to pass `closure_pending=getattr(state, 'closure_pending', False)`.

### Phase 5: Server Formatter (server.py)
**File:** `golazo-copilot/src/golazo_copilot/server.py`

1. In `format_status_result()`, add closure indicator after Current Role:
   ```python
   closure_label = ""
   if result.get("closure_pending"):
       closure_label = f" {ICON_WARN} **CLOSURE MODE**"
   ```
   Then use `{closure_label}` in the formatted string on the Current Role line.

### Phase 6: Role File Updates

**File:** `golazo-copilot/src/golazo_copilot/roles/defaults/project-owner-assistant.md`
1. Add closure output to Required Outputs section:
   ```markdown
   <!-- closure-only -->
   - file: WorkItems/{id}/{id}-closure.md
   ```
2. Add `WorkItems/{id}/{id}-closure.md` to YAML front-matter `outputs:` list.

**File:** `golazo-copilot/src/golazo_copilot/roles/defaults/retrospective.md`
1. Add a `## Transition Guidance` section before `## Decision rules`:
   ```markdown
   ## Transition Guidance
   - **Complete profile:** After completing retrospective, transition to `project-owner-assistant` for formal closure. Use `gcp_transition(role="project-owner-assistant")`.
   - **Express / Spike profiles:** The workflow ends here. No further transition is required.
   ```

### Phase 7: Tests
**File:** `golazo-copilot/tests/test_gcp053_closure_gate.py` (new)
- Implement all 19 test cases from GCP-0053-Test-Cases.md.
- Reuse existing helpers (`advance_to_role()`, `create_role_notes()`).
- Use `pytest.mark.asyncio` for async tests.

---

## Concerns and Open Items

### Concern 1: `format_status_result()` currently doesn't receive `closure_pending`
The status return dict gains a `closure_pending` key. The `format_status_result()` function reads from the result dict, so it will have access. No function signature change needed.

### Concern 2: Existing test assertions on `OutputSpec`
Tests that construct `OutputSpec` without `closure_only` will still work because the field defaults to `False`. No regressions expected.

### Concern 3: `_DEPLOYED_TO_SOURCE` list in gcp_status.py
No changes needed — the deployed-file stale detection is unrelated to closure. The POA and retrospective role files are already in the list.

### Concern 4: Version bump
A version bump (e.g., 2.106.0 → 2.107.0) is required after implementation, and the version comment in modified role files should be updated. This is standard practice.

---

## Summary

The design is sound. The `closure_pending` boolean is the right primitive — it's simple, additive, backward-compatible, and idempotent. The preceding-line annotation convention for conditional outputs is clean and extensible. The 5-file change surface is well-bounded with no impact to the transition matrix or role ordering. All 6 QA required clarifications have been addressed with specific implementation guidance. The capability impact analysis confirms 5 directly affected and 5 transitively affected capabilities, all at low-to-medium risk.
