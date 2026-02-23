# Golazo Subagent Handoff Protocol

> How artifacts and context flow between sequential role subagents in the Golazo Copilot V2 orchestrator architecture.

---

## 1. Orchestrator Responsibilities

The orchestrator (Copilot in the host chat window) owns the workflow loop. At each role boundary it:

1. **Queries state** — `golazo_status(work_item_id)` returns current role, phase, progress, missing outputs.
2. **Assembles context** — `golazo_role_context(work_item_id)` builds a self-contained bundle: role instructions, current state summary, input artifacts (from YAML front-matter), and previous role notes.
3. **Spawns subagent** — `runSubagent(description, prompt)` with the bundle as the prompt. The subagent performs the role's creative work.
4. **Collects output** — Reads the subagent's return message (summary of files created, decisions made).
5. **Verifies gate** — `golazo_transition(work_item_id, role)` validates Required Outputs exist and advances state.
6. **Displays summary** — Shows completed role, artifacts created, next role, any warnings.
7. **Repeats** from step 1 until retrospective completes and POA closure is done.

**The orchestrator never writes design docs, code, tests, or role notes itself.**

---

## 2. Subagent Contract

Each subagent receives:
- Role instructions (from role file, with YAML front-matter stripped)
- Current state summary (role, phase, progress, deviations)
- Input artifact contents (resolved from front-matter `inputs:`)
- Previous role decision notes (if not the first role)

Each subagent must:
- Create all files listed in `## Required Outputs` of the role instructions
- Follow role-specific decision rules and constraints
- Return a brief summary (files created, key decisions)
- **Never** call `golazo_transition` (orchestrator handles this)
- **Never** ask the user questions (make documented assumptions)

---

## 3. Artifact Handoff Matrix

The matrix below maps each role transition to (a) the direct bridge artifacts (role N output ∩ role N+1 input) and (b) reach-back artifacts (role N+1 reads from earlier roles).

| # | From → To | Direct Bridge | Reach-Back |
|---|-----------|---------------|------------|
| 1 | **POA → PM** | `{id}-User-Story.md` | — |
| 2 | **PM → DE** | `Design/{id}-design-doc.md` | `{id}-User-Story.md` |
| 3 | **DE → QA** | *(none)* | `{id}-User-Story.md`, `Design/{id}-design-doc.md` |
| 4 | **QA → Architect** | `Design/{id}-Review-Comments.md` | `{id}-User-Story.md`, `Design/{id}-design-doc.md` |
| 5 | **Architect → Developer** | `Design/{id}-Review-Comments.md` (appended) | `{id}-User-Story.md`, `Design/{id}-design-doc.md`, `Design/{id}-Test-Cases.md` |
| 6 | **Developer → Refactor** | `RoleDecisionNotes/{id}-developer.md` | — |
| 7 | **Refactor → Documenter** | *(none)* | `{id}-User-Story.md`, `Design/{id}-design-doc.md` |
| 8 | **Documenter → Builder** | *(none)* | `{id}-User-Story.md` |
| 9 | **Builder → Retro** | `RoleDecisionNotes/{id}-builder.md` | All 8 prior role notes |
| 10 | **Retro → POA Closure** | *(orchestrator handles)* | *(POA has no front-matter inputs)* |

### Key Observations

- **Zero-bridge transitions** (3, 7, 8): The successor role has no inputs that the predecessor directly produced. It reaches back to earlier artifacts (User Story, Design Doc). `golazo_role_context` handles this transparently — it resolves all inputs listed in the successor's front-matter regardless of which role originally produced them.
- **Append pattern** (transition 5): Both QA and Architect list `Design/{id}-Review-Comments.md` as an output. Architect appends to the QA-created file. The Developer receives the combined content.
- **Retrospective reach-back** (transition 9): Retrospective's front-matter lists all 9 prior role note files as inputs, providing a complete audit trail.
- **POA Closure** (transition 10): POA has `inputs: []` in its front-matter. The closure re-entry is orchestrator-managed: the orchestrator reads the retrospective notes and creates the closure document directly.

---

## 4. Error Recovery Strategy

### Subagent Fails to Create Required Output

1. `golazo_transition` returns `success: false` with `missing_outputs` listing the expected file paths.
2. Orchestrator displays the error to the user.
3. Orchestrator re-spawns the subagent for the same role with an updated prompt including the error message.
4. If the second attempt fails, orchestrator switches to **inline mode** (performs the work itself).

### Subagent Produces Unexpected Output

- Extra files are ignored by the gate; only Required Outputs are validated.
- Incorrectly-named files will cause the gate to block. The orchestrator must inspect and either rename or re-spawn.

### Subagent Returns Empty or Error Response

1. Orchestrator logs the failure.
2. Falls back to inline execution for the current role.
3. Continues with subagent mode for subsequent roles (single-role fallback, not session-wide).

### Backward Transition Triggered

If a subagent (e.g., Developer) discovers a design flaw:
1. The subagent reports the issue in its return summary.
2. The orchestrator calls `golazo_transition` with a prior role (e.g., `architect`).
3. State preserves all existing artifacts; the re-entered role receives updated context via `golazo_role_context`.
4. New artifacts overwrite the prior versions (e.g., updated Review-Comments).

---

## 5. Context Limits

- `golazo_role_context` enforces a **100KB** max bundle size (configurable via `max_bundle_size`).
- If inputs exceed the limit, artifact contents are proportionally truncated with a `[TRUNCATED]` marker.
- Role instructions and state summary are never truncated.
- Large binary or generated files should not be listed in role front-matter `inputs:`.

---

## 6. Quick Reference

```
Orchestrator Loop:
  golazo_status → golazo_role_context → runSubagent → verify outputs → golazo_transition → summary → repeat

Subagent Rules:
  ✓ Create Required Outputs    ✗ Call golazo_transition
  ✓ Follow role instructions   ✗ Ask user questions
  ✓ Return summary             ✗ Skip outputs
```
