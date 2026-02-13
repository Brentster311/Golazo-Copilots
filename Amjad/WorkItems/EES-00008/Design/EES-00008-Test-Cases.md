# EES-00008 — Test Cases

## Capability: data-models (Fact scope field)

### TC-1: Fact scope defaults to "rule"
- **Input**: `Fact(noun="VM", instance="*", property="VMSize", operator="==", value="Standard_NC24")`
- **Expected**: `fact.scope == "rule"`
- **Failure message**: "Fact scope should default to 'rule' for backward compatibility"

### TC-2: Fact scope can be set to "context"
- **Input**: `Fact(noun="RG", instance="*", property="Name", operator="==", value="my-rg", scope="context")`
- **Expected**: `fact.scope == "context"`

### TC-3: Fact.to_dict() includes scope
- **Input**: Fact with scope="context"
- **Expected**: `fact.to_dict()["scope"] == "context"`

### TC-4: Fact.from_dict() reads scope
- **Input**: `{"noun": "VM", "instance": "*", "property": "VMSize", "operator": "==", "value": "A100", "status": "confirmed", "scope": "context"}`
- **Expected**: `fact.scope == "context"`

### TC-5: Fact.from_dict() defaults scope to "rule" when absent (backward compat)
- **Input**: `{"noun": "VM", "instance": "*", "property": "VMSize", "operator": "==", "value": "A100", "status": "confirmed"}`
- **Expected**: `fact.scope == "rule"`

### TC-6: Fact.to_condition_dict() does NOT include scope
- **Input**: Fact with scope="context"
- **Expected**: `"scope" not in fact.to_condition_dict()`

## Capability: fact-extraction (LLM prompt & parse)

### TC-7: _parse_response reads scope from LLM JSON
- **Input**: LLM JSON with `"facts": [{"noun": "VM", ..., "scope": "context"}]`
- **Expected**: Parsed fact has `scope == "context"`

### TC-8: _parse_response defaults scope to "rule" when absent
- **Input**: LLM JSON with `"facts": [{"noun": "VM", ...}]` (no scope key)
- **Expected**: Parsed fact has `scope == "rule"`

### TC-9: System prompt contains scope classification instructions
- **Input**: Read `_SYSTEM_PROMPT` string
- **Expected**: Contains "scope" and instructions about rule vs context classification
- **Expected**: Contains prohibition of GUIDs, resource names, subscription IDs

## Capability: gui (scope column and toggle)

### TC-10: facts_to_rows includes scope field
- **Input**: `facts_to_rows([Fact(..., scope="context")])`
- **Expected**: Row dict contains `"scope": "context"`

### TC-11: _save_all filters by scope before rule generation
- **Setup**: 3 confirmed facts: 2 with scope="rule", 1 with scope="context"
- **Expected**: Only the 2 rule-scoped facts are passed to RuleGenerator
- **Expected**: All 3 facts (both scopes) are saved on the Incident record

## Capability: cli-orchestration (CLI scope filter)

### TC-12: CLI confirmed_facts filter by scope
- **Input**: `confirmed_facts` list includes context-scoped facts  
- **Expected**: Only rule-scoped facts passed to `gen.filter_rules()`
- **Note**: CLI `_confirm_facts` may need scope support too — verify during implementation
