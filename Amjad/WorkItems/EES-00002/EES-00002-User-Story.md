# EES-00002 — User Story

**Status**: IMPLEMENTED

## Related Work Items
- **Depends on:** EES-00001 (Core Learning Loop)
- **Part of:** Expert System decomposition (see `docs/expert-system-decisions.md`)

---

## User Story

- **Title:** GAP Rule Detection and Refinement
- **As a:** technical user (developer/engineer)
- **I want:** the system to detect when an incident provides a known starting chain and a known ending chain but is missing intermediate steps, automatically create explicit GAP rules bridging them, and refine those GAP rules as subsequent incidents fill in the missing steps
- **So that:** incomplete diagnostic knowledge is captured rather than lost, and iteratively improved as more incidents are processed

- **Out of scope:**
  - Problem Solving phase
  - RULEOUT rules
  - Rule evaluation / testing phase
  - GUI

- **Assumptions:**
  - **Assumption (explicit):** EES-00001 (Core Learning Loop) is complete and functioning — incidents can be loaded, facts extracted, and rules persisted.
  - **Assumption (explicit):** GAP detection is performed during rule generation when the system identifies confirmed facts that don't chain to a root cause through existing rules.
  - **Assumption (explicit):** GAP refinement occurs when a new incident introduces rules that overlap with an existing GAP's input/output boundaries.
  - **Assumption (explicit):** Interface is CLI, consistent with EES-00001.
  - **Assumption (explicit):** Platform is Windows, language is Python, persistence is local YAML files — all inherited from EES-00001.

- **Acceptance Criteria (bulleted, testable):**
  - When an incident produces confirmed facts that lead to a root cause but no complete rule chain connects them, the system creates a GAP rule with REQUIRES (input), PRODUCES (output), and NOTE fields
  - GAP rules are persisted in `rules/` with status: GAP and source incident IDs
  - When a subsequent incident introduces rules that partially or fully fill a GAP, the GAP rule is decomposed into confirmed rules plus a smaller GAP (or eliminated entirely)
  - The system reports when a GAP is narrowed or resolved
  - GAP rules are distinguishable from CONFIRMED rules in the YAML output

- **Non-functional requirements:**
  - GAP rules must clearly show what is known (inputs/outputs) and what is unknown (the gap itself)
  - No data loss when decomposing a GAP — source incident provenance is preserved

- **Telemetry / metrics expected:**
  - Count of GAP rules created per incident
  - Count of GAP rules refined or resolved per incident
  - Total open GAP rules in the knowledge base

- **Rollout / rollback notes:**
  - Additive to existing YAML structure; rollback is git revert
