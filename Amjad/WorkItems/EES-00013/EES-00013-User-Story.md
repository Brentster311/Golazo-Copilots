# EES-00013 — Multi-Turn Tool-Calling Fact Extractor

**Status**: IMPLEMENTED

**User Story**
- **Title**: Refactor FactExtractor to multi-turn tool-calling architecture
- **As a**: troubleshooting engineer using the expert system
- **I want**: the LLM to extract facts and propose rules through a multi-turn tool-calling conversation (instead of a single-shot JSON dump)
- **So that**: the model can inspect existing ontology/rules before proposing new ones, submit structured outputs via schema-validated tool parameters, and iterate on rejected submissions — leading to higher-quality rule generation
- **Out of scope**:
  - Copilot SDK integration (keep existing Azure OpenAI SDK)
  - GUI changes (extraction is invoked the same way from GUI/CLI)
  - Changes to the rule evaluator or engine
  - Interactive chat panel (separate future work item)
- **Assumptions**:
  - **Assumption (explicit)**: Azure OpenAI gpt-5.2 deployment supports tool/function calling — confirmed, available since OpenAI SDK v1.0
  - **Assumption (explicit)**: The existing `openai>=1.0` dependency is sufficient — no new packages needed
  - **Assumption (explicit)**: The `FactExtractor.extract()` return type (`LLMResponse`) stays the same — callers are unaffected
  - **Assumption (explicit)**: v2 rule grammar (CHANGE_STATE / RULED_OUT / GAP with optional ELSE) from EES-00010 is the target output format
- **Acceptance Criteria (bulleted, testable)**:
  - The LLM is given tools: `get_ontology`, `get_existing_rules`, `submit_fact`, `submit_rule`, `set_root_cause`
  - Each tool has a JSON schema that enforces v2 grammar structure (e.g., `submit_rule` requires `kind` ∈ {CHANGE_STATE, RULED_OUT, GAP})
  - The extractor runs an agentic loop: send prompt → process tool_calls → append tool results → repeat until model stops calling tools
  - `submit_fact` validates against VALID_OPERATORS and existing ontology nouns/properties
  - `submit_rule` validates against v2 grammar (valid kind, non-empty description, conditions reference known facts)
  - Invalid tool calls return validation errors so the model can self-correct
  - `FactExtractor.extract()` still returns `LLMResponse` — existing callers (GUI, CLI) are unaffected
- **Non-functional requirements**:
  - Max 10 turns to prevent runaway loops (configurable)
  - Total token usage logged for observability
  - No new dependencies added
- **Telemetry / metrics expected**:
  - Number of turns per extraction
  - Number of tool calls per extraction
  - Number of validation rejections per extraction
- **Rollout / rollback notes**:
  - Supersedes EES-00011 (which was prompt-only update for v2 grammar)
  - Backward compatible — same `extract()` signature, same return type
