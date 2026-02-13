# EES-00003 — Design Doc: RULEOUT Rule Generation

## Summary
Extend the Expert System learning loop to generate **RULEOUT** rules — elimination rules that capture "it's NOT X because..." reasoning from incident evidence. RULEOUT rules narrow the diagnostic search space by removing root cause candidates based on observed facts.

## Problem Statement
The current system only generates **positive** rules (`IF conditions THEN Noun.Property = value`). When an incident contains elimination reasoning — e.g., "we ruled out network issues because latency was normal" — that diagnostic knowledge is lost. RULEOUT rules capture this elimination reasoning as reusable expert knowledge.

## Business Case
- **Why now:** Core learning loop (EES-00001) and GAP detection (EES-00002) are complete. RULEOUT is the next logical expansion before the evaluation engine (EES-00004).
- **Impact:** Enables the expert system to narrow root cause candidates, making diagnostics faster and more accurate.
- **KPIs:** Count of RULEOUT rules proposed vs. confirmed per incident; total RULEOUT rules in knowledge base.

## Stakeholders
- Technical user (developer/engineer) — primary user of CLI
- Future evaluation engine (EES-00004) — consumer of RULEOUT rules

## Functional Requirements

### FR-1: Model Extension — Rule Type
- Add `type: Literal["positive", "ruleout"]` to the `Rule` model.
- For RULEOUT rules, `then` stores: `noun="RULEOUT"`, `instance="*"`, `property="Target"`, `value=<RootCauseName>`.
- Default type for all existing rules: `"positive"` (backward compatible via `.get()`).

### FR-2: LLM Prompt Extension
- Update `_SYSTEM_PROMPT` in `fact_extractor.py` to also propose RULEOUT rules from incident text.
- RULEOUT rules appear in the same `rules` array with `"type": "ruleout"` and `then.noun = "RULEOUT"`.
- `_parse_response` must set `rule.type` from the LLM response (defaulting to `"positive"` if absent).

### FR-3: User Confirmation Flow
- `_confirm_rules` in `main.py` already handles all proposed rules.
- Display RULEOUT rules distinctly: `IF <conditions> THEN RULEOUT <RootCauseName> BECAUSE <reasoning>`.
- Same actions: confirm / edit BECAUSE / reject.

### FR-4: Deduplication
- `RuleGenerator.is_duplicate()` already compares `conditions` + `then` dicts.
- Since RULEOUT rules have distinct `then` dicts (`noun="RULEOUT"`), they will naturally deduplicate correctly against both positive and other RULEOUT rules.
- `filter_rules` works unchanged — condition fact validation is type-agnostic.

### FR-5: Persistence
- RULEOUT rules are saved to `rules/` like positive rules, with `type: ruleout` in YAML.
- `rootcauses.yaml` is **NOT** modified by RULEOUT rules (they only reference existing root causes, they don't create new ones).

### FR-6: GAP Detection Interaction
- RULEOUT rules participate in GAP detection the same way positive rules do — their condition facts are considered "connected" when evaluating orphaned facts.
- `GapDetector.detect_gaps()` needs a minor update: check if a rule's `then.noun` is either "RootCause" or "RULEOUT" to consider its conditions as connected to root cause reasoning.

### FR-7: Summary Output
- Extend the summary in `process_incident` to report RULEOUT rule counts alongside positive rule counts.

## Non-Functional Requirements
- RULEOUT BECAUSE clauses must be human-readable.
- RULEOUT rules must not silently remove root causes from the entity list.
- Backward compatible: existing YAML files load without changes (type defaults to "positive").

## Proposed Approach

### Step 1: Model Changes (`models.py`)
- Change `Rule.type` from `Literal["positive"]` to `Literal["positive", "ruleout"]`.
- `to_dict()` / `from_dict()` already handle `type` field — no changes needed.

### Step 2: LLM Prompt Changes (`fact_extractor.py`)
- Extend `_SYSTEM_PROMPT` with RULEOUT rule format.
- Update `_parse_response` to read `type` from each rule dict and set it on the `Rule` object.

### Step 3: CLI Display Changes (`main.py`)
- Update `_confirm_rules` to format RULEOUT rules distinctly.
- Update `_format_rule_conditions` or add a parallel formatter for RULEOUT display.
- Update summary to split positive/RULEOUT counts.
- Do NOT add RULEOUT root causes to `rootcauses.yaml`.

### Step 4: GAP Detector Update (`gap_detector.py`)
- In `detect_gaps()`, broaden the rule-connection check: a rule targets root cause reasoning if `then.noun.lower()` is `"rootcause"` OR `"ruleout"`.

### Step 5: No changes needed
- `rule_generator.py` — dedup logic is type-agnostic.
- `yaml_store.py` — already stores all Rule fields.
- `ontology_manager.py` — no interaction with rule types.
- `incident_loader.py` — no interaction with rule types.

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|----------------|
| Separate RULEOUT model class | Unnecessary complexity. RULEOUT rules share the same structure as positive rules; only `type` and `then` convention differ. |
| `then.property = "RULEOUT"` with `then.noun = "RootCause"` | Confusing semantics. Using `noun="RULEOUT"` makes the intent obvious in YAML output. |
| Separate `ruleouts/` directory | Breaks existing `list_rules()` aggregation and adds unnecessary complexity. |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| LLM doesn't reliably propose RULEOUT rules | Explicit prompt engineering with examples; user confirmation acts as safety net |
| RULEOUT rules create false negatives in evaluation | Out of scope for EES-00003 (evaluation is EES-00004); but BECAUSE clause provides auditability |
| Backward compatibility break | Type defaults to "positive" in `from_dict()` — existing rules load unchanged |

## Open Questions
None — all design decisions resolved by existing `expert-system-decisions.md`.

## Dependencies
- EES-00001 (Core Learning Loop) — complete
- EES-00002 (GAP Detection) — complete

## Migration / Rollout / Rollback
- **Additive only:** New `type` field with default `"positive"`. Zero migration needed.
- **Rollback:** Git revert. Existing rules load as before (type defaults to positive).

## Observability Plan
- Summary output includes RULEOUT counts per incident.
- YAML files contain `type: ruleout` for easy grep/audit.

## Test Strategy Summary
- **Unit tests:** Model serialization with type=ruleout, backward compat, parse unchanged.
- **Unit tests:** `_parse_response` with RULEOUT rules in LLM output.
- **Unit tests:** `is_duplicate` with RULEOUT rules (cross-type dedup).
- **Unit tests:** `detect_gaps` with RULEOUT rules contributing to connected facts.
- **Integration tests:** Full `process_incident` flow with mixed positive + RULEOUT rules.
- **Negative tests:** RULEOUT rules don't modify `rootcauses.yaml`.
