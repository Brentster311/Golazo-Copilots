# EES-00018 — Test Cases

## Test Suite: OntologyProperty goal fields

### TC-18-01: OntologyProperty with goal annotations
- **Input**: `OntologyProperty("rootCause", "enum", values=["unknown", "admin_role_missing", "token_expired"], default="unknown", is_goal=True, initial="unknown", terminal=["admin_role_missing", "token_expired"])`
- **Expected**: `is_goal=True`, `initial="unknown"`, `terminal=["admin_role_missing", "token_expired"]`

### TC-18-02: OntologyProperty goal defaults
- **Input**: `OntologyProperty("status", "enum")`
- **Expected**: `is_goal=False`, `initial=None`, `terminal=[]`

### TC-18-03: to_dict includes goal fields when set
- **Input**: Property from TC-18-01
- **Expected**: Dict includes `"is_goal": True`, `"initial": "unknown"`, `"terminal": [...]`

### TC-18-04: to_dict omits goal fields when default
- **Input**: `OntologyProperty("status", "enum")`
- **Expected**: Dict does NOT include `is_goal`, `initial`, or `terminal` keys

### TC-18-05: from_dict with goal fields
- **Input**: `{"name": "rootCause", "type": "enum", "values": [...], "is_goal": true, "initial": "unknown", "terminal": ["admin_role_missing"]}`
- **Expected**: `is_goal=True`, `initial="unknown"`, `terminal=["admin_role_missing"]`

### TC-18-06: from_dict without goal fields (backward compat)
- **Input**: `{"name": "status", "type": "enum"}`
- **Expected**: `is_goal=False`, `initial=None`, `terminal=[]`

### TC-18-07: Round-trip with goal fields
- **Input**: Create with goal fields, `to_dict()` then `from_dict()`
- **Expected**: All fields match

## Test Suite: Goal dataclass

### TC-18-08: Goal construction
- **Input**: `Goal(noun="Incident", instance="$inc", property="rootCause", initial="unknown", terminal=["admin_role_missing", "token_expired"])`
- **Expected**: All fields accessible

### TC-18-09: Goal.to_dict and from_dict round-trip
- **Input**: Goal from TC-18-08
- **Expected**: `Goal.from_dict(goal.to_dict())` has identical fields

## Test Suite: EvaluationResult.goal_status

### TC-18-10: EvaluationResult with goal_status
- **Input**: `EvaluationResult(..., goal_status="resolved")`
- **Expected**: `goal_status == "resolved"`

### TC-18-11: EvaluationResult default goal_status
- **Input**: `EvaluationResult(...)` without goal_status
- **Expected**: `goal_status is None`

### TC-18-12: to_dict includes goal_status
- **Input**: Result with `goal_status="escalated"`
- **Expected**: `to_dict()` has `"goal_status": "escalated"`

### TC-18-13: to_dict with goal_status=None
- **Input**: Result without goal_status
- **Expected**: `to_dict()` has `"goal_status": None`

## Test Suite: RuleEvaluator goal-based termination

### TC-18-14: Goal resolved — evaluation stops
- **Setup**: Ontology: `Incident.rootCause` enum ["unknown", "admin_role_missing"]. Goal: initial="unknown", terminal=["admin_role_missing"]. Rules: R1 condition met → CHANGE_STATE target Incident.rootCause = "admin_role_missing". R2 would fire after R1 but shouldn't run.
- **Input**: `evaluate(input_facts, goal=goal)`
- **Expected**: `goal_status="resolved"`, R1 fired, R2 NOT fired (early termination)

### TC-18-15: Goal escalated — GAP fires
- **Setup**: Goal with initial="unknown", terminal=["admin_role_missing"]. Rules: R1 condition not met → ELSE GAP.
- **Input**: `evaluate(input_facts, goal=goal)`
- **Expected**: `goal_status="escalated"`

### TC-18-16: Goal in_progress — max iterations
- **Setup**: Goal with terminal=["admin_role_missing"]. Rules: R1 fires CHANGE_STATE but writes non-terminal value "pending". No more rules.
- **Input**: `evaluate(input_facts, goal=goal)`
- **Expected**: `goal_status="in_progress"` (fixed-point reached, goal not satisfied)

### TC-18-17: No goal — backward compat
- **Setup**: Same rules as previous tests.
- **Input**: `evaluate(input_facts)` or `evaluate(input_facts, goal=None)`
- **Expected**: `goal_status is None`, all rules fire as before (no early termination)

### TC-18-18: Goal initial fact seeded
- **Setup**: Goal with noun="Incident", instance="$inc", property="rootCause", initial="unknown". Input facts do NOT include a rootCause fact.
- **Input**: `evaluate(input_facts, goal=goal)`
- **Expected**: Working set includes `Fact("Incident", "$inc", "rootCause", "==", "unknown")` — rules can match against it

### TC-18-19: Goal immediately resolved (initial in terminal)
- **Setup**: Goal with initial="done", terminal=["done"].
- **Input**: `evaluate(input_facts, goal=goal)`
- **Expected**: `goal_status="resolved"`, no rules fire (terminated before first iteration — or after first pass where check happens)

### TC-18-20: Multiple GAPs in same iteration
- **Setup**: Goal in_progress. Two rules both fire GAP in same iteration.
- **Input**: `evaluate(input_facts, goal=goal)`
- **Expected**: `goal_status="escalated"`, both GAP outputs recorded

### TC-18-21: Resolution rule uses structured CHANGE_STATE target
- **Setup**: Goal: Incident.rootCause. Rule: structured CHANGE_STATE target_noun=Incident, target_property=rootCause, value="admin_role_missing".
- **Input**: `evaluate(input_facts, goal=goal)`
- **Expected**: `goal_status="resolved"`, derived fact is `Fact("Incident", "$inc", "rootCause", "==", "admin_role_missing")`
