# EES-00013 Test Cases

## Overview

Tests for multi-turn tool-calling fact extractor. All tests mock `client.chat.completions.create` to simulate tool-calling sequences. No live LLM calls.

---

## TC-01: Happy Path — Full Extraction

**Maps to**: AC-1 through AC-7  
**Description**: Model calls `get_ontology`, `get_existing_rules`, then submits facts, rules, and root cause. Verify `LLMResponse` is correctly assembled.

**Setup**: Mock response sequence:
1. Turn 1: tool_calls = [`get_ontology()`, `get_existing_rules()`]
2. Turn 2: tool_calls = [`submit_fact(noun="Server", property="CPUUsage", operator=">", value="90")`, `submit_fact(noun="Server", property="MemoryFree", operator="<", value="5%")`]
3. Turn 3: tool_calls = [`submit_rule(conditions={...}, then={kind="CHANGE_STATE", description="Resource exhaustion"}, because="...")`]
4. Turn 4: tool_calls = [`set_root_cause(name="Resource Exhaustion")`]
5. Turn 5: no tool_calls (model sends finish message)

**Expected**:
- `result.facts` has 2 facts with correct fields
- `result.rules` has 1 rule with `then.kind == "CHANGE_STATE"` and `then.description == "Resource exhaustion"`
- `result.root_cause == "Resource Exhaustion"`
- `isinstance(result, LLMResponse)` is True

---

## TC-02: Tool Validation — Invalid Operator in `submit_fact`

**Maps to**: AC-4, AC-6  
**Description**: Model submits a fact with an invalid operator. Handler returns error. Model retries with valid operator.

**Setup**: Mock response sequence:
1. Turn 1: tool_calls = [`submit_fact(operator="LIKE")`]  → handler returns error
2. Turn 2: tool_calls = [`submit_fact(operator="contains")`] → accepted
3. Turn 3: no tool_calls

**Expected**:
- First tool result contains "Invalid operator"
- Final `result.facts` has 1 fact with `operator == "contains"`

---

## TC-03: Tool Validation — Invalid Rule Kind in `submit_rule`

**Maps to**: AC-5, AC-6  
**Description**: Model submits a rule with `kind="POSITIVE"` (invalid). Handler returns error.

**Setup**: Mock response sequence:
1. Turn 1: tool_calls = [`submit_rule(then={kind="POSITIVE", description="..."})`] → error
2. Turn 2: tool_calls = [`submit_rule(then={kind="CHANGE_STATE", description="..."})`] → accepted
3. Turn 3: no tool_calls

**Expected**:
- First tool result contains "Invalid kind"
- Final `result.rules` has 1 rule with `then.kind == "CHANGE_STATE"`

---

## TC-04: Tool Validation — Empty Description in Rule

**Maps to**: AC-5, AC-6  
**Description**: Model submits a rule with empty description.

**Setup**: Mock submit_rule with `then={kind="CHANGE_STATE", description=""}` 

**Expected**: Tool result contains error about empty description. Rule not collected.

---

## TC-05: Tool Validation — Missing Because in Rule

**Maps to**: AC-5, AC-6  
**Description**: Model submits a rule without `because` field.

**Setup**: Mock submit_rule with no `because` key.

**Expected**: Tool result contains error about missing because. Rule not collected.

---

## TC-06: Tool Validation — Variables in Facts Rejected

**Maps to**: AC-4, AC-6  
**Description**: Model submits a fact with `instance="$op"`.

**Setup**: Mock submit_fact with `instance="$op"`.

**Expected**: Tool result contains "Facts must not contain variables".

---

## TC-07: Rule with ELSE Branch

**Maps to**: AC-5  
**Description**: Model submits a rule with both THEN and ELSE branches.

**Setup**: Mock submit_rule with `then={kind="CHANGE_STATE", ...}` and `else={kind="GAP", ...}`.

**Expected**: `result.rules[0].then.kind == "CHANGE_STATE"` and `result.rules[0].else_.kind == "GAP"`.

---

## TC-08: Rule with RULED_OUT Kind

**Maps to**: AC-5  
**Description**: Model submits a rule with `kind="RULED_OUT"`.

**Expected**: `result.rules[0].then.kind == "RULED_OUT"`.

---

## TC-09: Rule with GAP Kind

**Maps to**: AC-5  
**Description**: Model submits a rule with `kind="GAP"`.

**Expected**: `result.rules[0].then.kind == "GAP"`.

---

## TC-10: Max Turns Cutoff

**Maps to**: NFR — Max 10 turns  
**Description**: Model keeps calling tools indefinitely. Loop terminates at max_turns.

**Setup**: Mock returns tool_calls on every turn (infinite). Set `max_turns=3`.

**Expected**:
- Loop exits after 3 turns
- Returns `LLMResponse` with whatever was collected
- WARNING logged about max turns reached

---

## TC-11: No Tool Calls (Plain Text Response)

**Maps to**: Edge case from design  
**Description**: Model responds with plain text, no tool_calls.

**Setup**: Mock returns a response with `tool_calls=None` (or empty) on first turn.

**Expected**: Returns empty `LLMResponse(facts=[], rules=[], root_cause=None)`.

---

## TC-12: Unknown Tool Name

**Maps to**: Review C-5  
**Description**: Model calls a tool name not in the defined set.

**Setup**: Mock returns `tool_calls=[{function.name="do_something_else", ...}]`.

**Expected**: Tool result contains "Unknown tool" error. Not counted as a submission.

---

## TC-13: `get_ontology` Returns Formatted Ontology

**Maps to**: AC-1  
**Description**: Verify `get_ontology` handler returns ontology as JSON.

**Setup**: Call handler directly with `[OntologyNoun("Server", [OntologyProperty("CPUUsage")])]`.

**Expected**: Returns JSON string containing `"Server"` and `"CPUUsage"`.

---

## TC-14: `get_ontology` Returns Empty Message When No Ontology

**Maps to**: AC-1  
**Description**: Verify handler behavior with empty ontology.

**Setup**: Call handler with `[]`.

**Expected**: Returns JSON or message indicating no ontology exists.

---

## TC-15: `get_existing_rules` Returns Empty List

**Maps to**: AC-1  
**Description**: Since `extract()` doesn't have a rules parameter (per C-1), this returns empty.

**Expected**: Returns `"[]"` or similar empty-list JSON.

---

## TC-16: Multiple `set_root_cause` Calls — Last Wins

**Maps to**: Review C-6  
**Description**: Model calls `set_root_cause` twice with different names.

**Setup**: Mock sequence: `set_root_cause("A")`, then `set_root_cause("B")`.

**Expected**: `result.root_cause == "B"`.

---

## TC-17: `submit_fact` with Ontology Warning

**Maps to**: AC-4  
**Description**: Model submits a fact with a noun not in the ontology.

**Setup**: Ontology has `["Server"]`. Model submits fact with `noun="Storage"`.

**Expected**: Fact accepted (not rejected). Tool result includes ontology warning.

---

## TC-18: `submit_rule` with Empty Conditions

**Maps to**: AC-5  
**Description**: Model submits a rule with `conditions.items = []`.

**Expected**: Tool result contains error about empty conditions.

---

## TC-19: LLM API Failure During Loop

**Maps to**: AC-7, existing TC-25  
**Description**: API call raises exception mid-loop.

**Setup**: First turn succeeds (tool calls processed), second turn raises `Exception("timeout")`.

**Expected**: `LLMError` raised with "LLM API call failed".

---

## TC-20: Extract Returns Same Type — Backward Compat

**Maps to**: AC-7  
**Description**: Verify `extract()` returns `LLMResponse` with v2 `Rule` objects.

**Setup**: Full happy-path mock sequence.

**Expected**:
- `isinstance(result, LLMResponse)`
- `isinstance(result.rules[0].then, RuleOutput)` — NOT `RuleThen`
- `result.rules[0].then.kind` is a valid VALID_OUTPUT_KINDS entry

---

## TC-21: Auth Uses ChainedTokenCredential

**Maps to**: Existing auth test (preserved)  
**Description**: Constructor uses `ChainedTokenCredential(AzureCliCredential, ManagedIdentityCredential)`.

**Expected**: Same as existing test — no change to auth behavior.

---

## TC-22: Scope Field Preserved in Submitted Facts

**Maps to**: AC-4  
**Description**: Facts submitted with `scope="context"` retain that scope.

**Setup**: Mock submit_fact with `scope="context"`.

**Expected**: `result.facts[0].scope == "context"`.

---

## TC-23: `submit_fact` Defaults Instance to "*"

**Maps to**: Review C-4  
**Description**: When `instance` is omitted in tool args, defaults to `"*"`.

**Setup**: Call submit_fact handler with no `instance` key.

**Expected**: Collected fact has `instance == "*"`.

---

## TC-24: `submit_fact` Defaults Scope to "rule"

**Maps to**: AC-4  
**Description**: When `scope` is omitted in tool args, defaults to `"rule"`.

**Setup**: Call submit_fact handler with no `scope` key.

**Expected**: Collected fact has `scope == "rule"`.

---

## TC-25: Token Usage Logged

**Maps to**: NFR — Token logging  
**Description**: Total tokens summed across turns and logged.

**Setup**: Mock responses with `usage.total_tokens = 100` per turn, 3 turns.

**Expected**: Log output contains total tokens >= 300.

---

## TC-26: `submit_rule` — Condition With Invalid Operator

**Maps to**: AC-5, AC-6  
**Description**: Rule condition item has `operator="LIKE"`.

**Expected**: Tool result contains error about invalid operator.

---

## TC-27: Rule with Variable Binding in Conditions

**Maps to**: AC-5  
**Description**: Rule conditions use `instance="$op"` (variables are allowed in rules, not facts).

**Setup**: submit_rule with condition item `instance="$op"`.

**Expected**: Rule accepted. `result.rules[0].conditions.items[0].instance == "$op"`.
