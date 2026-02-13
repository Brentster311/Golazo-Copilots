# EES-00003 — Review Comments

## Design Review

### Findings

| ID | Severity | Area | Finding | Recommendation |
|----|----------|------|---------|----------------|
| MJ-1 | Major | FR-1 | `Rule.type` Literal change from `Literal["positive"]` to `Literal["positive", "ruleout"]` — what about GAP rules that are RULEOUT type? A GAP rule could theoretically be a "ruleout gap". Design doc doesn't address this combination. | Architect to confirm: GAP rules are always type="positive" in current design. If RULEOUT GAPs are possible, clarify the interaction. |
| MJ-2 | Major | FR-6 | `detect_gaps()` broadening: the check `then.noun.lower() in ("rootcause", "ruleout")` means RULEOUT rule conditions are considered "connected". But RULEOUT rules eliminate — they don't confirm. Should their conditions really prevent GAP detection? | Architect to resolve: if a fact is consumed by a RULEOUT rule but NOT by a positive rule, is it truly "connected" to the root cause? Semantically yes — the fact contributes to diagnostic reasoning. Confirm this interpretation. |
| MN-1 | Minor | FR-3 | Display format for RULEOUT rules in `_confirm_rules` shows `THEN RULEOUT <RootCauseName>`. Ensure the display extracts the root cause name from `then.value`, not from `then.property`. | Verify display logic reads `rule.then.value` for RULEOUT target. |
| MN-2 | Minor | FR-5 | Design says rootcauses.yaml is NOT modified by RULEOUT rules. The current `process_incident` adds root cause unconditionally if confirmed. Need to ensure RULEOUT rules' referenced root causes don't leak into the rootcause creation path. | The existing root cause save path uses `_confirm_root_cause()` result, not rules. This is already correct — no change needed. Confirm in architect review. |
| MN-3 | Minor | FR-7 | Summary should distinguish positive vs. RULEOUT counts. Design says "extend summary" but doesn't specify exact format. | Propose: `Rules: N positive, M ruleout generated`. |

### Overall Assessment
**Conditionally Approved** — Design is clean and additive. Two major findings (MJ-1, MJ-2) require architect resolution before implementation. Minor findings are clarification-level.

---

## Architect Notes

### MJ-1 Resolution: RULEOUT + GAP Interaction
**Decision:** RULEOUT rules CAN have GAP status. A RULEOUT GAP represents: "we know something eliminates root cause X, but we don't know the full intermediate reasoning." This is a valid diagnostic scenario. The existing `Rule.status` already supports `CONFIRMED|GAP|RESOLVED` independent of `Rule.type`. No model changes needed beyond expanding `type` to accept `"ruleout"`.

### MJ-2 Resolution: RULEOUT Conditions in GAP Detection
**Decision:** RULEOUT rule conditions ARE considered "connected" for GAP detection purposes. Rationale: a RULEOUT rule eliminates a root cause candidate — the facts used for elimination are diagnostically relevant and should not be flagged as orphaned. Broadening `detect_gaps()` to include `then.noun.lower() == "ruleout"` is correct.

### MN-1 Resolution: Display Format
**Confirmed:** `_confirm_rules` will display RULEOUT rules as `THEN RULEOUT <rule.then.value>`. The `then.value` contains the root cause name.

### MN-2 Resolution: rootcauses.yaml Isolation
**Confirmed:** The root cause save path in `process_incident` uses the result of `_confirm_root_cause()`, not rule `then` values. RULEOUT rules referencing root cause names do not trigger root cause creation. No code change needed.

### MN-3 Resolution: Summary Format
**Decision:** Summary will show `Rules: N positive, M ruleout generated` to distinguish types.

### Capability Impact
Files affected: `models.py`, `fact_extractor.py`, `main.py`, `gap_detector.py`. Capabilities impacted:
- **data-models**: `Rule.type` Literal expanded — backward compatible
- **fact-extraction**: Prompt + `_parse_response` extended — contract unchanged (`extract() -> LLMResponse`)
- **cli-orchestration**: Display + summary changes — contract unchanged (`process_incident()`)
- GAP detector key file not in capabilities.yaml — adding it is out of scope for EES-00003.
