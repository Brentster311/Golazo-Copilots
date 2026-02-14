# EES-00012 — V2 Rule Grammar: GUI Display

**Status**: IMPLEMENTED

**User Story**
- **Title:** V2 Rule Grammar — GUI Display of CHANGE_STATE / RULED_OUT / GAP rules
- **As a:** knowledge engineer
- **I want:** the GUI to display v2 rules showing THEN and optional ELSE branches with their output entity types, and a live status indicator showing what the LLM is doing during extraction
- **So that:** I can visually review, confirm, and understand the diagnostic branching in extracted rules, and see real-time progress during multi-turn LLM extraction
- **Out of scope:**
  - Data model and engine changes (EES-00010, prerequisite)
  - LLM prompt changes (EES-00011, prerequisite)
  - Rule editing in the GUI (future work)
- **Assumptions:**
  - **Assumption (explicit):** EES-00010 and EES-00011 are complete — the data model, engine, and LLM extraction produce v2 rules.
  - **Assumption (explicit):** The existing Tkinter GUI is the target. No new framework.
  - **Assumption (explicit):** Rules are displayed read-only; editing is out of scope.
- **Acceptance Criteria (bulleted, testable):**
  - The rules list/treeview displays the output entity type (CHANGE_STATE, RULED_OUT, or GAP) for each rule's THEN branch
  - Rules with an ELSE branch show the ELSE output entity type
  - Rules without an ELSE branch display correctly (no blank/error)
  - Double-click detail view shows the full rule in human-readable format including conditions, THEN, and optional ELSE
  - The evaluated-rules view distinguishes which branch fired (THEN vs ELSE) during evaluation
  - During LLM extraction, the status bar continuously updates showing the current LLM activity (e.g. turn number, tool being called, facts/rules submitted so far)
- **Non-functional requirements:** No new dependencies; existing GUI patterns
- **Telemetry / metrics expected:** N/A
- **Rollout / rollback notes:** Depends on EES-00010 and EES-00011. Pure display change, no data risk.
