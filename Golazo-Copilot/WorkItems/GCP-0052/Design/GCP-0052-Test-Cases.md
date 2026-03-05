# GCP-0052 Test Cases

**Work Item:** GCP-0052 — Subagent Handoff Protocol & Integration Testing  
**Author:** Quality Assurance  
**Date:** 2026-02-22

---

## Test Case Overview

| TC ID | Description | Maps to AC | Priority |
|---|---|---|---|
| TC1 | Full 10-role workflow walk (happy path) | AC3 | P0 |
| TC2 | Negative — missing output blocks transition | AC4 | P0 |
| TC3 | Backward transition (developer → architect re-entry) | AC5 | P0 |
| TC4 | Handoff protocol document validation | AC1, AC2 | P1 |
| TC5 | Regression guard — existing tests still pass | AC6 | P0 |
| TC6 | Zero-bridge transition context resolution | Edge case (domain-expert §3.1) | P1 |
| TC7 | ROLE_SUFFIX_MAP mapping correctness | Edge case (domain-expert §4.5) | P1 |

---

## TC1: Full 10-Role Workflow Walk (Happy Path) — AC3

### Purpose
Verify that the complete POA → PM → DE → QA → Architect → Developer → Refactor → Documenter → Builder → Retrospective workflow succeeds when each role produces its required outputs.

### Setup
1. Use `tmp_path` as isolated workspace root.
2. Copy role default files from `golazo_copilot/roles/defaults/` into `tmp_path/.github/roles/` (ensures real front-matter is used).
3. Call `gcp_create_workitem(work_item_id="INT-001", work_items_dir=tmp_path/"WorkItems")` to initialize state.

### Steps

| Step | Role | Action | Assertions |
|---|---|---|---|
| 1 | project-owner-assistant | Call `gcp_role_context`. Create `INT-001-User-Story.md` and `RDN/INT-001-project-owner-assistant.md`. Call `gcp_transition(role="program-manager")`. | Context bundle contains `## Role Instructions`. Transition returns `success=True`, `current_role="program-manager"`. |
| 2 | program-manager | Call `gcp_role_context`. Create `Design/INT-001-design-doc.md` and `RDN/INT-001-program-manager.md`. Call `gcp_transition(role="domain-expert")`. | Context bundle contains User-Story content (input artifact). Transition succeeds. |
| 3 | domain-expert | Call `gcp_role_context`. Create `RDN/INT-001-domain-expert.md`. Call `gcp_transition(role="quality-assurance")`. | Context bundle contains User-Story + design-doc content (reach-back to POA & PM). Transition succeeds. |
| 4 | quality-assurance | Call `gcp_role_context`. Create `Design/INT-001-Review-Comments.md`, `Design/INT-001-Test-Cases.md`, and `RDN/INT-001-quality-assurance.md`. Call `gcp_transition(role="architect")`. | Context bundle contains User-Story + design-doc. Transition succeeds. |
| 5 | architect | Call `gcp_role_context`. Create `Design/INT-001-Capability-Impact.md`, append architect section to `Design/INT-001-Review-Comments.md`, and create `RDN/INT-001-architect.md`. Call `gcp_transition(role="developer")`. | Context bundle contains Review-Comments (from QA). Transition succeeds. Phase changes to `development`. |
| 6 | developer | Call `gcp_role_context`. Create `RDN/INT-001-developer.md`. Call `gcp_transition(role="refactor-expert")`. | Context bundle contains User-Story + design-doc + Review-Comments + Test-Cases. Transition succeeds. |
| 7 | refactor-expert | Call `gcp_role_context`. Create `RDN/INT-001-refactor.md` (note: suffix is `refactor`, not `refactor-expert`). Call `gcp_transition(role="documenter")`. | Context bundle contains developer notes (`RDN/INT-001-developer.md`). Does NOT contain design-doc, User-Story (narrow scope). Transition succeeds. |
| 8 | documenter | Call `gcp_role_context`. Create `RDN/INT-001-documenter.md`. Call `gcp_transition(role="builder")`. | Context bundle contains User-Story + design-doc (reach-back to POA & PM, not from refactor-expert). Transition succeeds. |
| 9 | builder | Call `gcp_role_context`. Create `RDN/INT-001-builder.md`. Call `gcp_transition(role="retrospective")`. | Context bundle contains User-Story (reach-back to POA). Transition succeeds. |
| 10 | retrospective | Call `gcp_role_context`. Create `RDN/INT-001-retrospective.md`. | Context bundle contains all 9 prior RDN files. All marked as present (not `[not yet created]`). |

### Expected Result
All 10 transitions succeed. State ends with `current_role="retrospective"`. `role_history` has 10 entries.

### Failure Messages
- `"gcp_role_context failed at role {role}: {error}"` — if context bundle assembly fails
- `"gcp_transition failed at {from_role} → {to_role}: {error}"` — if transition is blocked
- `"Missing expected input artifact '{artifact}' in {role} context bundle"` — if reach-back fails
- `"Phase should be 'development' after developer transition, got '{phase}'"` — if phase boundary not crossed

---

## TC2: Negative — Missing Output Blocks Transition — AC4

### Purpose
Verify that `gcp_transition` blocks advancement when a required output is missing and returns a specific error message identifying the missing file.

### Setup
1. Use `tmp_path` as isolated workspace root.
2. Copy role default files into `tmp_path/.github/roles/`.
3. Create work item and advance through POA → PM → DE to reach quality-assurance.

### Steps

| Step | Action | Assertions |
|---|---|---|
| 1 | Advance to quality-assurance by creating outputs for POA, PM, and DE, transitioning normally. | State is at `quality-assurance`. |
| 2 | Create `Design/INT-002-Review-Comments.md` and `RDN/INT-002-quality-assurance.md` but **omit** `Design/INT-002-Test-Cases.md`. | Two of three QA outputs exist. |
| 3 | Call `gcp_transition(role="architect")`. | Returns `success=False`. Error message contains `Test-Cases` or identifies the specific missing file path. |
| 4 | Now create the missing `Design/INT-002-Test-Cases.md` and retry. | `gcp_transition` returns `success=True`, `current_role="architect"`. |

### Expected Result
Step 3 fails with a clear error naming the missing output. Step 4 succeeds after remediation.

### Failure Messages
- `"Transition should have been BLOCKED but succeeded"` — if gate enforcement is missing
- `"Error message should reference 'Test-Cases' but got: {error}"` — if error is generic
- `"Retry after creating missing output should succeed but got: {error}"` — if remediation doesn't work

---

## TC3: Backward Transition — Developer → Architect Re-Entry — AC5

### Purpose
Verify that a backward transition from developer to architect is allowed, that architect receives updated artifacts on re-entry, and that subsequent forward progress uses the freshest content.

### Setup
1. Use `tmp_path` as isolated workspace root.
2. Copy role default files into `tmp_path/.github/roles/`.
3. Create work item and advance through all roles to developer (roles 1–6), creating all required outputs.

### Steps

| Step | Action | Assertions |
|---|---|---|
| 1 | At developer, create developer notes. | `RDN/INT-003-developer.md` exists. |
| 2 | Call `gcp_transition(role="architect")` (backward). | Returns `success=True`. Response contains `warning` key (backward transition warning). `current_role="architect"`. |
| 3 | Call `gcp_role_context` for architect. | Context bundle contains Review-Comments content. Developer notes exist on disk from step 1. |
| 4 | Overwrite `Design/INT-003-Review-Comments.md` with new content including an "Architect Re-Entry Notes" section. Create new architect notes. | Updated file on disk. |
| 5 | Call `gcp_transition(role="developer")` (forward again). | Returns `success=True`, `current_role="developer"`. |
| 6 | Call `gcp_role_context` for developer. | Context bundle contains the **updated** Review-Comments (with "Architect Re-Entry Notes" text), not the original QA-only version. |

### Expected Result
Backward transition succeeds with warning. Re-entered architect sees current artifacts. Developer on re-entry sees updated artifacts, confirming no stale caching.

### Failure Messages
- `"Backward transition should succeed but got: {error}"` — if backward is blocked
- `"Expected 'warning' in backward transition result"` — if warning is missing
- `"Developer context should contain updated Review-Comments content 'Architect Re-Entry Notes' but it was missing"` — if stale cache is served

---

## TC4: Handoff Protocol Document Validation — AC1/AC2

### Purpose
Verify that `WorkItems/Golazo-Subagent-Handoff-Protocol.md` exists, is properly structured, and covers all 10 role transitions.

### Setup
Read the file from the workspace root (not `tmp_path` — this is a static document check).

### Steps

| Step | Action | Assertions |
|---|---|---|
| 1 | Check file exists at `WorkItems/Golazo-Subagent-Handoff-Protocol.md`. | File exists and is non-empty. |
| 2 | Parse document for required sections. | Contains: "Orchestrator Responsibilities" (or equivalent heading), "Subagent Contract" (or equivalent heading), "Artifact Handoff Matrix" (or equivalent heading), "Error Recovery" (or equivalent heading). |
| 3 | Parse the handoff matrix table. | Table has at least 10 rows (one per role transition). All 10 roles appear: `project-owner-assistant`, `program-manager`, `domain-expert`, `quality-assurance`, `architect`, `developer`, `refactor-expert`, `documenter`, `builder`, `retrospective`. |
| 4 | Check line count. | File is ≤ 200 lines (NFR). |
| 5 | Verify matrix distinguishes direct bridge from accumulated inputs. | Matrix or supporting text differentiates "direct bridge" (predecessor outputs ∩ successor inputs) from "reach-back" (successor reads earlier roles). |

### Expected Result
All five checks pass.

### Failure Messages
- `"Handoff protocol file not found at expected path"` — if file is missing
- `"Missing required section: '{section}'"` — if a section is absent
- `"Handoff matrix missing transition for role '{role}'"` — if a role is not covered
- `"Protocol document exceeds 200-line limit: {count} lines"` — if too long
- `"Matrix does not distinguish direct bridge from accumulated reach-back"` — if conflation exists

---

## TC5: Regression Guard — AC6

### Purpose
Confirm all existing tests continue to pass after GCP-0052 changes.

### Method
Run `pytest golazo-copilot/tests/` and verify exit code 0 with all tests passing.

### Assertions
- Exit code is 0.
- No test failures or errors in output.
- Test count is ≥ 371 (the existing baseline).

### Failure Messages
- `"Regression detected: {N} test(s) failed"` — if any existing tests break.
- `"Test count dropped below baseline: {count} < 371"` — if tests were accidentally removed.

---

## TC6: Zero-Bridge Transition Context Resolution — Edge Case

### Purpose
Verify that `gcp_role_context` correctly resolves inputs from non-adjacent roles when the immediate predecessor produces no overlapping artifacts (zero-bridge transitions identified by domain expert).

### Setup
1. Use `tmp_path` as isolated workspace root.
2. Copy role default files into `tmp_path/.github/roles/`.
3. Create work item and advance through POA → PM → DE.

### Steps

| Step | Action | Assertions |
|---|---|---|
| 1 | At domain-expert, create only `RDN/INT-006-domain-expert.md` (DE's sole required output). Transition to quality-assurance. | Transition succeeds. |
| 2 | Call `gcp_role_context` for quality-assurance. | Context bundle contains `INT-006-User-Story.md` content (from POA, role 1) and `Design/INT-006-design-doc.md` content (from PM, role 2). Neither was produced by DE (role 3). |
| 3 | Similarly, advance through QA → Architect → Developer → Refactor-Expert. At refactor-expert, create `RDN/INT-006-refactor.md`. Transition to documenter. | Transition succeeds. |
| 4 | Call `gcp_role_context` for documenter. | Context bundle contains User-Story (from POA) and design-doc (from PM). Neither was produced by refactor-expert. |

### Expected Result
`gcp_role_context` successfully resolves inputs from earlier roles, not just the immediate predecessor. Zero-bridge transitions do not prevent context assembly.

### Failure Messages
- `"QA context should contain User-Story from POA but it was missing"` — if reach-back fails for QA
- `"Documenter context should contain design-doc from PM but it was missing"` — if reach-back fails for documenter

---

## TC7: ROLE_SUFFIX_MAP Mapping Correctness — Edge Case

### Purpose
Verify that role notes files use the correct suffix per `ROLE_SUFFIX_MAP`, especially `refactor-expert` → `refactor` and `domain-expert` → `domain-expert` (default fallthrough).

### Setup
Use `tmp_path` workspace.

### Steps

| Step | Action | Assertions |
|---|---|---|
| 1 | Import `ROLE_SUFFIX_MAP` from `golazo_copilot.tools.gcp_transition`. | Map is importable. |
| 2 | Assert `ROLE_SUFFIX_MAP["refactor-expert"] == "refactor"`. | Suffix is shortened. |
| 3 | Assert `ROLE_SUFFIX_MAP.get("domain-expert", "domain-expert") == "domain-expert"`. | Defaults to full role name (domain-expert is NOT in the map). |
| 4 | Create work item, advance to refactor-expert. Create `RDN/INT-007-refactor.md`. Call `gcp_transition(role="documenter")`. | Transition succeeds — `gcp_transition` finds the notes file with suffix `refactor`, not `refactor-expert`. |
| 5 | Verify that creating `RDN/INT-007-refactor-expert.md` instead of `RDN/INT-007-refactor.md` would NOT satisfy the notes check. | `check_role_notes_exist` returns False for the wrong suffix. |

### Expected Result
ROLE_SUFFIX_MAP is authoritative for file naming. Tests use the correct suffix.

### Failure Messages
- `"ROLE_SUFFIX_MAP maps refactor-expert to '{actual}', expected 'refactor'"` — if mapping changed
- `"Transition should succeed with correct suffix 'refactor' but failed: {error}"` — if suffix lookup broken
- `"Wrong suffix 'refactor-expert' should NOT satisfy notes check but it did"` — if gate is too lenient

---

## Traceability Matrix

| AC | Test Case(s) | Coverage |
|---|---|---|
| AC1 | TC4 (steps 1–2, 5) | Protocol exists with required sections |
| AC2 | TC4 (step 3) | Matrix covers all 10 transitions |
| AC3 | TC1 (all steps) | Full 10-role workflow with context + transition assertions |
| AC4 | TC2 (steps 2–4) | Missing output blocks, then remediation succeeds |
| AC5 | TC3 (steps 2–6) | Backward transition with artifact freshness verification |
| AC6 | TC5 | All existing tests pass |
| Edge: zero-bridge | TC6 | Context resolution for non-adjacent role inputs |
| Edge: ROLE_SUFFIX_MAP | TC7 | Correct suffix for refactor-expert and domain-expert |
