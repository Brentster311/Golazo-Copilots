# EES-00003 — User Story

**Status**: IMPLEMENTED

## Related Work Items
- **Depends on:** EES-00001 (Core Learning Loop)
- **Part of:** Expert System decomposition (see `docs/expert-system-decisions.md`)

---

## User Story

- **Title:** RULEOUT Rule Generation
- **As a:** technical user (developer/engineer)
- **I want:** the system to generate RULEOUT rules from incident evidence — rules that eliminate root cause candidates based on observed facts — so that the diagnostic search space is narrowed even when a positive root cause assignment isn't possible
- **So that:** I can capture elimination reasoning ("we know it's NOT X because...") as reusable expert system knowledge

- **Out of scope:**
  - Problem Solving phase
  - Rule evaluation / testing phase
  - GUI
  - Confidence factors

- **Assumptions:**
  - **Assumption (explicit):** EES-00001 (Core Learning Loop) is complete and functioning.
  - **Assumption (explicit):** RULEOUT rules follow the same flat AND/OR boolean logic as positive rules.
  - **Assumption (explicit):** The AI-assisted extraction proposes RULEOUT candidates from incident text where elimination reasoning is present (e.g., "we ruled out network issues because latency was normal").
  - **Assumption (explicit):** Interface is CLI, consistent with EES-00001.
  - **Assumption (explicit):** Platform is Windows, language is Python, persistence is local YAML files — all inherited from EES-00001.

- **Acceptance Criteria (bulleted, testable):**
  - The system can propose RULEOUT rules from incident text where elimination reasoning is identified
  - The user can confirm, edit, or reject proposed RULEOUT rules
  - RULEOUT rules are persisted in `rules/` with the format: `IF <conditions> THEN RULEOUT <RootCauseName> BECAUSE <reasoning>`
  - RULEOUT rules carry status (CONFIRMED/GAP), source incident IDs, and BECAUSE clause
  - RULEOUT rules are distinguishable from positive rules in YAML output
  - `rootcauses.yaml` is not modified by RULEOUT rules (they reference existing root causes)

- **Non-functional requirements:**
  - RULEOUT BECAUSE clause must be human-readable and capture the diagnostic reasoning
  - RULEOUT rules must not silently remove root causes from the entity list

- **Telemetry / metrics expected:**
  - Count of RULEOUT rules proposed vs. confirmed per incident
  - Total RULEOUT rules in the knowledge base

- **Rollout / rollback notes:**
  - Additive to existing YAML structure; rollback is git revert
