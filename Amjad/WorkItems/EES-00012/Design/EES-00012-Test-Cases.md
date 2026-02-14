# EES-00012 — Test Cases

## TC-01: `rules_to_rows` with v2 CHANGE_STATE rule

**AC:** Rules list displays CHANGE_STATE output type  
**Steps:** Create Rule with `then=RuleOutput(kind="CHANGE_STATE", description="ServerOverloaded")`, no `else_`. Call `rules_to_rows()`.  
**Expected:** Row `then` contains `CHANGE_STATE("ServerOverloaded")`. Row `else` is empty string.

## TC-02: `rules_to_rows` with v2 RULED_OUT rule

**AC:** Rules list displays RULED_OUT output type  
**Steps:** Create Rule with `then=RuleOutput(kind="RULED_OUT", description="NetworkIssue")`. Call `rules_to_rows()`.  
**Expected:** Row `then` contains `RULED_OUT("NetworkIssue")`.

## TC-03: `rules_to_rows` with v2 GAP rule

**AC:** Rules list displays GAP output type  
**Steps:** Create Rule with `then=RuleOutput(kind="GAP", description="NeedMemoryData")`. Call `rules_to_rows()`.  
**Expected:** Row `then` contains `GAP("NeedMemoryData")`.

## TC-04: `rules_to_rows` with ELSE branch

**AC:** Rules with ELSE branch show ELSE output type  
**Steps:** Create Rule with `then=RuleOutput(kind="CHANGE_STATE", description="HighCPU")` and `else_=RuleOutput(kind="RULED_OUT", description="CPUNormal")`. Call `rules_to_rows()`.  
**Expected:** Row `then` contains `CHANGE_STATE("HighCPU")`. Row `else` contains `RULED_OUT("CPUNormal")`.

## TC-05: `rules_to_rows` without ELSE branch

**AC:** Rules without ELSE display correctly (no blank/error)  
**Steps:** Create Rule with `else_=None`. Call `rules_to_rows()`.  
**Expected:** Row `else` is empty string. No crash.

## TC-06: `rules_to_rows` preserves conditions formatting

**AC:** Conditions display correctly with v2 rules  
**Steps:** Create Rule with 2 AND conditions. Call `rules_to_rows()`.  
**Expected:** Row `conditions` joins items with " AND ".

## TC-07: `eval_result_to_display` with v2 outputs — CHANGE_STATE

**AC:** Evaluation display shows CHANGE_STATE outputs  
**Steps:** Build `EvaluationResult` with `outputs=[{rule_id, branch="then", output=RuleOutput(kind="CHANGE_STATE", ...)}]`. Call `eval_result_to_display()`.  
**Expected:** Display has `change_states` list with entry showing rule_id, branch, description.

## TC-08: `eval_result_to_display` with ELSE branch fired

**AC:** Evaluation view distinguishes which branch fired  
**Steps:** Build `EvaluationResult` with `outputs=[{rule_id, branch="else", output=RuleOutput(kind="RULED_OUT", ...)}]`. Call `eval_result_to_display()`.  
**Expected:** Display entry shows `branch="else"`.

## TC-09: `eval_result_to_display` with mixed output kinds

**AC:** All v2 output kinds represented in display  
**Steps:** Build result with CHANGE_STATE, RULED_OUT, and GAP outputs. Call `eval_result_to_display()`.  
**Expected:** Display has entries for all three kinds.

## TC-10: `eval_result_to_display` empty results

**AC:** Empty results display without crash  
**Steps:** Build result with no fired_rules and empty outputs. Call `eval_result_to_display()`.  
**Expected:** All output lists empty, no crash.

## TC-11: `on_status` callback called during extraction

**AC:** Status bar continuously updates during LLM extraction  
**Steps:** Create `FactExtractor` with mocked client. Call `extract()` with `on_status=mock_fn`. Mock returns tool calls for 2 turns.  
**Expected:** `mock_fn` called with messages containing turn numbers and tool names.

## TC-12: `on_status` callback receives turn info

**AC:** Status shows turn number  
**Steps:** Mock client returns 3 turns of tool calls. Pass `on_status` callback.  
**Expected:** Callback receives messages matching `"Turn 1..."`, `"Turn 2..."`, `"Turn 3..."`.

## TC-13: `on_status` callback receives tool name

**AC:** Status shows tool being called  
**Steps:** Mock client returns tool calls for `get_ontology`, `submit_fact`. Pass `on_status` callback.  
**Expected:** Status messages include tool names like `"get_ontology"`, `"submit_fact"`.

## TC-14: `on_status=None` (default) — no crash

**AC:** Backward compatibility  
**Steps:** Call `extract()` without `on_status` parameter (or `on_status=None`).  
**Expected:** Extraction works normally, no crash from None callback.

## TC-15: `on_status` receives summary after each turn

**AC:** Status shows accumulated fact/rule count  
**Steps:** Mock client submits 2 facts in turn 1. Pass `on_status` callback.  
**Expected:** Summary message includes count like `"2 facts"`.

## TC-16: `_format_eval_display` shows branch label

**AC:** Evaluation view distinguishes THEN vs ELSE  
**Steps:** Build display dict with `branch="else"` entry. Call `_format_eval_display()`.  
**Expected:** Output text includes `"(ELSE)"` marker next to the rule.

## TC-17: `_format_eval_display` shows v2 output kinds

**AC:** Evaluation shows CHANGE_STATE, RULED_OUT, GAP sections  
**Steps:** Build display dict with all three output kinds. Call `_format_eval_display()`.  
**Expected:** Output text has sections/labels for CHANGE_STATE, RULED_OUT, GAP.

## TC-18: Existing `rules_to_rows` tests still pass (regression)

**AC:** No regression in existing adapter tests  
**Steps:** Run full test suite.  
**Expected:** All 253+ tests pass.
