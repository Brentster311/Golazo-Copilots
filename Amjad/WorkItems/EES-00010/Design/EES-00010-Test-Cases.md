# EES-00010 — Test Cases

## TC1: RuleOutput Construction
- **AC**: A Rule can be constructed with `then` being one of CHANGE_STATE, RULED_OUT, or GAP
- `test_rule_output_change_state`: Create `RuleOutput(kind="CHANGE_STATE", description="X")` — assert kind and description
- `test_rule_output_ruled_out`: Create `RuleOutput(kind="RULED_OUT", description="Y")` — assert kind and description
- `test_rule_output_gap`: Create `RuleOutput(kind="GAP", description="Z")` — assert kind and description

## TC2: Rule with Optional ELSE
- **AC**: A Rule can optionally have an `else_` branch
- `test_rule_without_else`: Create Rule with `else_=None` — assert `else_` is None
- `test_rule_with_else`: Create Rule with `else_=RuleOutput(...)` — assert `else_` is set

## TC3: YAML Round-Trip
- **AC**: Rules serialize to/from YAML in the new format
- `test_rule_to_dict_then_only`: Serialize Rule without ELSE — verify dict has `then` but no `else` key
- `test_rule_to_dict_with_else`: Serialize Rule with ELSE — verify dict has both `then` and `else` keys
- `test_rule_from_dict_then_only`: Deserialize dict without `else` — verify `else_` is None
- `test_rule_from_dict_with_else`: Deserialize dict with `else` — verify `else_` matches
- `test_rule_round_trip`: to_dict → from_dict → to_dict — dicts match

## TC4: Engine THEN Branch Fires
- **AC**: The rule evaluator fires the THEN branch when all conditions are met
- `test_then_fires_change_state`: Rule with CHANGE_STATE then, conditions met — derived fact appears with noun=CHANGE_STATE
- `test_then_fires_ruled_out`: Rule with RULED_OUT then, conditions met — derived fact appears with noun=RULED_OUT
- `test_then_fires_gap`: Rule with GAP then, conditions met — GAP recorded, NOT in working set

## TC5: Engine ELSE Branch Fires
- **AC**: The rule evaluator fires the ELSE branch when conditions are NOT met
- `test_else_fires_when_conditions_not_met`: Rule with ELSE, conditions not met — ELSE output appears as derived fact
- `test_else_not_fired_when_no_else`: Rule without ELSE, conditions not met — no output
- `test_else_not_fired_when_then_fires`: Rule with ELSE, conditions met — only THEN output appears

## TC6: Chaining RULED_OUT
- **AC**: RULED_OUT outputs appear in the working set and can be matched by conditions of other rules
- `test_ruled_out_chains_as_condition`: R1 ELSE produces RULED_OUT, R2 ELSE produces RULED_OUT, R3 conditions require both RULED_OUTs — R3 fires
- `test_ruled_out_chain_incomplete`: Only one RULED_OUT present — R3 does not fire

## TC7: Chaining CHANGE_STATE
- **AC**: CHANGE_STATE outputs appear in the working set and can be matched by conditions
- `test_change_state_chains`: R1 THEN produces CHANGE_STATE, R2 condition matches that CHANGE_STATE — R2 fires

## TC8: GAP Terminal
- `test_gap_not_in_working_set`: Rule fires with GAP — GAP recorded in result but no derived fact added, downstream rule requiring GAP does NOT fire

## TC9: Rule Trace
- `test_trace_records_branch`: Each trace entry includes which branch fired (then/else)

## TC10: RuleGenerator
- `test_is_duplicate_v2`: Two rules with same conditions + then + else_ — duplicate
- `test_filter_rules_v2`: filter_rules works with new RuleOutput types

## TC11: EvaluationResult Convenience
- `test_result_change_states`: `.change_states` returns only CHANGE_STATE outputs
- `test_result_ruled_outs`: `.ruled_outs` returns only RULED_OUT outputs
- `test_result_gaps`: `.gaps` returns only GAP outputs
