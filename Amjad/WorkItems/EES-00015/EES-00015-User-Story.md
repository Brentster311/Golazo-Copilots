# EES-00015: Highlight Rule-Used Facts and Confirm Used

**Status**: IN PROGRESS

**User Story**
- **Title**: Highlight rule-consumed facts and one-click confirm
- **As a**: Knowledge engineer reviewing proposed facts and rules
- **I want**: Facts that are referenced by at least one proposed rule's conditions to appear bold in the facts table, with a "Confirm Used" button that confirms only those facts
- **So that**: I can instantly see which facts matter for the rules and confirm them in one click without reviewing each one individually

- **Out of scope**:
  - Editing or filtering rules based on used/unused facts
  - Highlighting facts used in THEN/ELSE outputs (only IF conditions)
  - Persisting the bold/used state to disk

- **Assumptions**:
  - **Assumption (explicit)**: "Used by rules" means the fact's (noun, property) pair appears in at least one proposed rule's condition items (excluding chaining conditions like RULED_OUT/CHANGE_STATE/GAP). This mirrors the existing fact-constraint validation logic.
  - **Assumption (explicit)**: Bold is applied via a Treeview tag with a bold font. The existing GUI already uses ttk.Treeview for the facts table.

- **Acceptance Criteria (bulleted, testable)**:
  - After extraction, facts whose (noun.lower, property.lower) match any proposed rule condition item are displayed with bold text in the facts Treeview
  - Chaining conditions (RULED_OUT, CHANGE_STATE, GAP) do not count as "used" when determining bold facts
  - A "Confirm Used" button appears in the fact action bar with a tooltip
  - Clicking "Confirm Used" sets status to "confirmed" only for facts that are used by rules, leaving unused facts unchanged
  - The bold styling updates dynamically if the user re-extracts facts
  - A pure-function `facts_used_by_rules()` adapter exists and is unit-tested

- **Non-functional requirements**: Bold rendering must not slow down table population
- **Telemetry / metrics expected**: N/A
- **Rollout / rollback notes**: Purely additive GUI change, no data format changes
