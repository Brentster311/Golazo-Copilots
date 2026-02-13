# EES-00001 — User Story

**Status**: IMPLEMENTED

## Decomposition Rationale

The full expert system encompasses multiple user-observable outcomes: incident ingestion, fact extraction, rule generation, GAP management, RULEOUT logic, rule evaluation/testing, and GUI interaction. This is too large for a single story. The work is decomposed into vertical slices:

1. **EES-00001 (this work item):** Core learning loop — load a free-text incident, AI-assisted fact extraction, rule generation, and YAML persistence with iterative ontology management.
2. **EES-00002:** GAP rule detection and refinement across incidents.
3. **EES-00003:** RULEOUT rule generation.
4. **EES-00004:** Rule evaluation engine (testing phase).
5. **EES-00005:** GUI for incident processing and rule management.

---

## User Story

- **Title:** Core Learning Loop — Incident to Rules
- **As a:** technical user (developer/engineer)
- **I want:** to load a free-text incident, review AI-proposed fact extractions (`Noun(instance).Property operator value`), confirm, edit, reject, or specialize them, and have the system generate expert system rules and persist them as YAML files
- **So that:** I can iteratively build a knowledge base of troubleshooting rules from documented incidents

- **Out of scope:**
  - Problem Solving phase (action plans, remediation)
  - GUI (this story uses CLI interaction only for the learning loop; GUI is a separate story)
  - Rule evaluation / testing phase
  - RULEOUT rules
  - GAP rule detection and refinement
  - Confidence factors, symptom clusters, OBSERVED/INFERRED distinction
  - Batch processing of multiple incidents

- **Assumptions:**
  - **Assumption (explicit):** CLI is acceptable for this first slice — user confirmed GUI as the ultimate interface, but the core engine must exist before a GUI wraps it. CLI provides the fastest path to a testable vertical slice.
  - **Assumption (explicit):** A single incident is processed per invocation. Batch processing is a future enhancement.
  - **Assumption (explicit):** The AI-assisted fact extraction will use an LLM via API call (e.g., OpenAI or similar). The specific provider is an implementation detail to be decided in the Architect role.
  - **Assumption (explicit):** YAML is stored in a local directory structure: `incidents/`, `rules/`, `ontology.yaml`, `rootcauses.yaml`.

- **Acceptance Criteria (bulleted, testable):**
  - Given a free-text incident file, the system proposes a list of `Noun(instance).Property operator value` facts extracted from the text, defaulting to generalized (`*`) instances
  - The user can confirm, edit, reject, or specialize (set a specific instance) each proposed fact before it is persisted
  - Confirmed facts are saved to an incident YAML file in `incidents/` with the source text and extracted facts
  - New Noun.Property pairs not already in `ontology.yaml` are added to the ontology; existing matches are reused
  - The system generates flat AND-only or OR-only `IF/THEN` rules from the confirmed facts and persists them to `rules/` as YAML with status CONFIRMED, source incident IDs, and a BECAUSE clause
  - If a RootCause is identified in the incident, it is added to `rootcauses.yaml` as an entity with Name and a placeholder ActionPlan
  - All YAML files are valid and parseable after each operation

- **Non-functional requirements:**
  - Rules and ontology must be human-readable in YAML
  - System must not silently drop or modify user-confirmed facts
  - Ontology matching should be case-insensitive to reduce duplicates

- **Telemetry / metrics expected:**
  - Count of facts proposed vs. confirmed vs. rejected per incident
  - Count of new ontology entries added per incident
  - Count of rules generated per incident

- **Rollout / rollback notes:**
  - Local YAML files only; rollback is file deletion or git revert
  - No external service dependencies beyond the LLM API
