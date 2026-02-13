# EES-00005 — User Story

**Status**: IMPLEMENTED

## Related Work Items
- **Depends on:** EES-00001 (Core Learning Loop), EES-00002 (GAP Rules), EES-00003 (RULEOUT Rules), EES-00004 (Rule Evaluation Engine)
- **Part of:** Expert System decomposition (see `docs/expert-system-decisions.md`)

---

## User Story

- **Title:** GUI for Incident Processing and Rule Management
- **As a:** technical user (developer/engineer)
- **I want:** a desktop GUI application on Windows that provides visual interfaces for loading incidents, reviewing/confirming AI-proposed facts, browsing the rule base, viewing the ontology, and running rule evaluations
- **So that:** I can interact with the expert system more efficiently than through CLI, with visual feedback on the rule chain and diagnostic state

- **Out of scope:**
  - Problem Solving phase
  - Web or cross-platform deployment
  - Multi-user collaboration
  - Confidence factors, symptom clusters

- **Assumptions:**
  - **Assumption (explicit):** All prior work items (EES-00001 through EES-00004) are complete — the GUI wraps existing engine functionality.
  - **Assumption (explicit):** Python GUI framework (specific framework TBD in Architect role — e.g., PyQt, Tkinter, or similar).
  - **Assumption (explicit):** The GUI is a desktop application targeting Windows only, per user confirmation.

- **Acceptance Criteria (bulleted, testable):**
  - The user can load a free-text incident file via a file browser dialog
  - AI-proposed facts are displayed in a reviewable list where the user can confirm, edit, or reject each
  - Generated rules are displayed after fact confirmation
  - The ontology (`ontology.yaml`) is browsable in a tree or list view
  - The rule base (`rules/`) is browsable with filtering by status (CONFIRMED/GAP), type (positive/RULEOUT), and source incident
  - The user can run a rule evaluation and view results including root cause candidates, ruleouts, and GAP encounters
  - All changes are persisted to the same YAML files used by the CLI

- **Non-functional requirements:**
  - GUI must be responsive during LLM API calls (non-blocking UI)
  - YAML files remain the single source of truth (GUI and CLI interoperable)

- **Telemetry / metrics expected:**
  - Same metrics as underlying engine operations
  - GUI session duration and operation counts (optional)

- **Rollout / rollback notes:**
  - Desktop application; install/uninstall
  - No migration needed — reads/writes same YAML files
