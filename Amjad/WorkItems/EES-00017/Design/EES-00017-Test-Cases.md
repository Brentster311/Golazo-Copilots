# EES-00017 — Test Cases

## Test Suite: RuleOutput.to_fact() — structured path

### TC-17-01: Structured CHANGE_STATE produces correct Fact
- **Input**: `RuleOutput("CHANGE_STATE", "", target_noun="User", target_instance="$u", target_property="adminRole", value="confirmed")`
- **Call**: `to_fact()`
- **Expected**: `Fact(noun="User", instance="$u", property="adminRole", operator="==", value="confirmed")`

### TC-17-02: Structured CHANGE_STATE with wildcard instance
- **Input**: `RuleOutput("CHANGE_STATE", "", target_noun="Tenant", target_instance=None, target_property="status", value="active")`
- **Call**: `to_fact()`
- **Expected**: `Fact(noun="Tenant", instance="*", property="status", operator="==", value="active")`

### TC-17-03: Legacy CHANGE_STATE produces pseudo-fact (unchanged)
- **Input**: `RuleOutput("CHANGE_STATE", "User.adminRole => confirmed")`
- **Call**: `to_fact()`
- **Expected**: `Fact(noun="CHANGE_STATE", instance="*", property="User.adminRole => confirmed", operator="==", value="true")`

### TC-17-04: RULED_OUT to_fact unchanged
- **Input**: `RuleOutput("RULED_OUT", "User.adminRole")`
- **Call**: `to_fact()`
- **Expected**: `Fact(noun="RULED_OUT", instance="*", property="User.adminRole", operator="==", value="true")`

### TC-17-05: GAP to_fact unchanged
- **Input**: `RuleOutput("GAP", "NeedMemoryData")`
- **Call**: `to_fact()`
- **Expected**: `Fact(noun="GAP", instance="*", property="NeedMemoryData", operator="==", value="true")`

## Test Suite: RuleOutput.validate() — ontology checks

### TC-17-06: Valid structured output — no errors
- **Setup**: Ontology with `User.adminRole` as enum `["confirmed", "denied", "pending"]`
- **Input**: `RuleOutput("CHANGE_STATE", "", target_noun="User", target_instance="$u", target_property="adminRole", value="confirmed")`
- **Expected**: `[]`

### TC-17-07: Unknown target noun
- **Setup**: Ontology with `User` only
- **Input**: `RuleOutput("CHANGE_STATE", "", target_noun="Server", target_instance="*", target_property="cpu", value="high")`
- **Expected**: 1 error containing "Server"

### TC-17-08: Unknown target property
- **Setup**: Ontology with `User.adminRole` only
- **Input**: `RuleOutput("CHANGE_STATE", "", target_noun="User", target_instance="$u", target_property="email", value="test")`
- **Expected**: 1 error containing "email"

### TC-17-09: Invalid target value
- **Setup**: Ontology with `User.adminRole` as enum `["confirmed", "denied"]`
- **Input**: `RuleOutput("CHANGE_STATE", "", target_noun="User", target_instance="$u", target_property="adminRole", value="superadmin")`
- **Expected**: 1 error containing "superadmin"

### TC-17-10: Legacy CHANGE_STATE — validate returns empty (no validation)
- **Input**: `RuleOutput("CHANGE_STATE", "User.adminRole => confirmed")`
- **Expected**: `[]` (legacy format not validated)

### TC-17-11: RULED_OUT — validate returns empty
- **Input**: `RuleOutput("RULED_OUT", "User.adminRole")`
- **Expected**: `[]`

### TC-17-12: GAP — validate returns empty
- **Input**: `RuleOutput("GAP", "NeedMemoryData")`
- **Expected**: `[]`

### TC-17-13: Partial structured fields — error
- **Input**: `RuleOutput("CHANGE_STATE", "", target_noun="User", target_instance=None, target_property=None, value=None)`
- **Expected**: 1 error about incomplete structured fields (target_property and value are required when target_noun is set)

## Test Suite: RuleOutput serialization

### TC-17-14: to_dict — structured CHANGE_STATE
- **Input**: `RuleOutput("CHANGE_STATE", "human note", target_noun="User", target_instance="$u", target_property="adminRole", value="confirmed")`
- **Expected**: `{"kind": "CHANGE_STATE", "description": "human note", "target_noun": "User", "target_instance": "$u", "target_property": "adminRole", "value": "confirmed"}`

### TC-17-15: to_dict — legacy CHANGE_STATE (no structured fields)
- **Input**: `RuleOutput("CHANGE_STATE", "User.adminRole => confirmed")`
- **Expected**: `{"kind": "CHANGE_STATE", "description": "User.adminRole => confirmed"}`

### TC-17-16: to_dict — RULED_OUT (description only)
- **Input**: `RuleOutput("RULED_OUT", "User.adminRole")`
- **Expected**: `{"kind": "RULED_OUT", "description": "User.adminRole"}`

### TC-17-17: from_dict — structured CHANGE_STATE
- **Input**: `{"kind": "CHANGE_STATE", "description": "", "target_noun": "Tenant", "target_instance": "*", "target_property": "status", "value": "active"}`
- **Expected**: `target_noun="Tenant"`, `target_property="status"`, `value="active"`

### TC-17-18: from_dict — legacy CHANGE_STATE
- **Input**: `{"kind": "CHANGE_STATE", "description": "User.adminRole => confirmed"}`
- **Expected**: `target_noun=None`, `description="User.adminRole => confirmed"`

### TC-17-19: from_dict — RULED_OUT (no structured fields)
- **Input**: `{"kind": "RULED_OUT", "description": "User.adminRole"}`
- **Expected**: `target_noun=None`

### TC-17-20: Round-trip — structured
- **Input**: Create structured `RuleOutput`, `to_dict()` then `from_dict()`
- **Expected**: Identical field values

### TC-17-21: Round-trip — legacy
- **Input**: Create legacy `RuleOutput("CHANGE_STATE", "desc")`, `to_dict()` then `from_dict()`
- **Expected**: Identical field values

## Test Suite: Existing tests remain green

### TC-17-22: Existing RuleOutput constructions still work
- **Verify**: All existing tests that construct `RuleOutput(kind=..., description=...)` pass without modification (new fields default to None)

### TC-17-23: Rule.from_dict with legacy YAML
- **Input**: Existing R-001.yaml format `{kind: CHANGE_STATE, description: "User.adminRole => confirmed"}`
- **Expected**: Loads successfully, `target_noun` is None
