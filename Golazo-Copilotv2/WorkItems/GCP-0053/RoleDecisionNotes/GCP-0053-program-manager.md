# GCP-0053 Program Manager Decision Notes

**Work Item:** GCP-0053 — POA Closure Gate: Enforce POA Re-entry After Retrospective in Complete Mode  
**Role:** Program Manager  
**Date:** 2026-02-22

---

## Key Design Decisions

1. **Closure is a state, not a role.** Adding an 11th role (`closure`) was considered and rejected. It would break `ROLE_ORDER`, `PHASE_MAP`, `VALID_ROLES`, progress calculations, the subagent handoff matrix, every test asserting 10 roles, and user mental models. The POA role already contains the closure instructions — we just need the system to know *when* to enforce them. An explicit `closure_pending` boolean on `WorkItemState` achieves this cleanly.

2. **Explicit flag over history inference.** We could derive "is this closure?" from `role_history` (check if POA was visited before and retro was just exited). Rejected because: (a) backward rework transitions also create repeat POA entries, making inference ambiguous; (b) every consumer would need to implement the same scanning logic; (c) an explicit flag makes intent unambiguous and is O(1) to check.

3. **Profile-gated enforcement, not global.** Closure re-entry is enforced ONLY for `complete` profile. Express and spike profiles end at retrospective as they do today. Every closure code path must be guarded by `state.profile == "complete"`.

4. **Generic annotation convention for conditional outputs.** Rather than hardcoding `{id}-closure.md` as a special case in the output validator, we use an HTML-comment annotation (`<!-- closure-only -->`) in the role markdown. This keeps the validator generic and extensible — if a future role needs conditional outputs, the same pattern works without code changes.

5. **Additive schema change, no version bump on `schema_version`.** Adding `closure_pending: bool = False` to `WorkItemState` is backward-compatible because Pydantic supplies the default when deserializing old `state.json` files. The `schema_version` stays at `"1.0"`. A package version bump is needed, not a schema version bump.

6. **Retrospective role file must explicitly state the handoff.** AC1 requires the retrospective role instructions to tell the LLM to transition to POA in complete mode. This is an advisory text change — no code logic depends on it, but it closes the "instruction gap" that allows the workflow to end silently.

## Scope Boundaries

- **In scope:** `core/types.py`, `core/output_validator.py`, `tools/gcp_transition.py`, `tools/gcp_status.py`, `roles/defaults/retrospective.md`, potentially `roles/defaults/project-owner-assistant.md` (annotation), new tests.
- **Out of scope:** Express/spike profile changes, new MCP tools, multi-iteration loops, closure section content changes.

## Risks Flagged to Architect

1. **Output annotation parsing robustness.** The `<!-- closure-only -->` convention must be strictly defined (exact text, positioning relative to the output line) and tested with edge cases. Recommend the architect define the parsing rule precisely.
2. **Thread safety of `closure_pending`.** `gcp_status` uses `asyncio.gather` with `to_thread`. The `closure_pending` field is read-only during status computation (set only during transition), so no race condition exists — but this should be noted in the design.
3. **Backward compatibility.** A test specifically for loading old `state.json` without `closure_pending` is essential (TC-F in the design doc).

## Open Questions for Architect

1. Should `current_phase` be reported as `"closure"` in status output when in closure mode, or should it stay as `"definition"` (POA's normal phase) with `closure_pending` as a separate field? Recommend keeping phase as-is and adding the flag separately — but this is an architect/UX call.
2. Should the closure-only annotation be inline (`- file: {id}-closure.md <!-- closure-only -->`) or on the preceding line? Recommend preceding line for readability, but the parser needs to handle both or one must be specified.
3. Does the output validator need to pass `closure_pending` explicitly, or should it receive the full `WorkItemState` and derive context itself? Recommend explicit parameter to keep the validator stateless and testable.

## Acceptance Criteria Mapping

| AC | Design Section | Test Coverage |
|----|---------------|--------------|
| AC1 | §2 Profile-Gated Transition + §5 Retrospective Role File Update | TC-A |
| AC2 | §4 Status Output Enhancement | TC-B |
| AC3 | §3 Context-Aware Output Validator | TC-C, TC-G |
| AC4 | §2 Profile-Gated Transition (express/spike guard) | TC-D, TC-E |
| AC5 | §Test Strategy (all TCs) | TC-A through TC-G |
