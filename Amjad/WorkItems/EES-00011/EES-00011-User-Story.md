# EES-00011 — V2 Rule Grammar: LLM Prompt & Extraction

**Status**: BACKLOG

**User Story**
- **Title:** V2 Rule Grammar — LLM Prompt & Fact/Rule Extraction
- **As a:** knowledge engineer
- **I want:** the LLM extraction prompt to produce rules in the v2 grammar (IF/THEN with CHANGE_STATE, RULED_OUT, GAP, and optional ELSE)
- **So that:** when I extract facts and rules from an incident, the LLM outputs rules in the new format that the v2 engine can evaluate
- **Out of scope:**
  - Data model and engine changes (EES-00010, prerequisite)
  - GUI changes (EES-00012)
  - BECAUSE clause (deferred)
- **Assumptions:**
  - **Assumption (explicit):** EES-00010 is complete — the data model and engine already support the v2 grammar.
  - **Assumption (explicit):** The LLM YAML output schema will mirror the new model structure.
  - **Assumption (explicit):** Gap detection logic in `gap_detector.py` will be updated to work with the new rule/fact types.
- **Acceptance Criteria (bulleted, testable):**
  - The `_SYSTEM_PROMPT` in `fact_extractor.py` instructs the LLM to produce rules using `CHANGE_STATE("...")`, `RULED_OUT("...")`, and `GAP("...")` output types
  - The prompt includes at least one example rule with an ELSE branch
  - The prompt includes at least one example rule without an ELSE branch
  - Extracted rules parse into the v2 `Rule` model without errors
  - Gap detector produces meaningful results with the new rule format
- **Non-functional requirements:** Prompt changes must not break extraction of facts (Noun.Property = value)
- **Telemetry / metrics expected:** N/A
- **Rollout / rollback notes:** Depends on EES-00010. Existing extracted rules will not match the new format.
