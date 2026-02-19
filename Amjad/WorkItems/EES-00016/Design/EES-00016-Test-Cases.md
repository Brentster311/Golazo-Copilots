# EES-00016 — Test Cases

## Test Suite: OntologyProperty.validate_value()

### TC-16-01: Enum — valid value
- **Input**: `OntologyProperty("role", "enum", ["admin", "user", "none"], "none")`, `validate_value("admin")`
- **Expected**: `True`

### TC-16-02: Enum — invalid value
- **Input**: Same property, `validate_value("superadmin")`
- **Expected**: `False`

### TC-16-03: Enum — empty values list
- **Input**: `OntologyProperty("role", "enum", [], None)`, `validate_value("anything")`
- **Expected**: `False` (empty enum accepts nothing)

### TC-16-04: Enum — case sensitivity
- **Input**: `OntologyProperty("role", "enum", ["Admin"], None)`, `validate_value("admin")`
- **Expected**: `False` (case-sensitive)

### TC-16-05: Bool — valid true
- **Input**: `OntologyProperty("active", "bool")`, `validate_value("true")`
- **Expected**: `True`

### TC-16-06: Bool — valid false
- **Input**: Same property, `validate_value("false")`
- **Expected**: `True`

### TC-16-07: Bool — invalid (capitalized)
- **Input**: Same property, `validate_value("True")`
- **Expected**: `False`

### TC-16-08: Bool — invalid (yes)
- **Input**: Same property, `validate_value("yes")`
- **Expected**: `False`

### TC-16-09: Long — valid positive
- **Input**: `OntologyProperty("count", "long")`, `validate_value("42")`
- **Expected**: `True`

### TC-16-10: Long — valid negative
- **Input**: Same property, `validate_value("-1")`
- **Expected**: `True`

### TC-16-11: Long — valid zero
- **Input**: Same property, `validate_value("0")`
- **Expected**: `True`

### TC-16-12: Long — invalid (float)
- **Input**: Same property, `validate_value("3.14")`
- **Expected**: `False`

### TC-16-13: Long — invalid (text)
- **Input**: Same property, `validate_value("abc")`
- **Expected**: `False`

### TC-16-14: String type — rejected (type removed)
- **Input**: `OntologyProperty("desc", "string")`, `validate_value("anything at all")`
- **Expected**: `False` — `string` is not a valid type

### TC-16-15: String type — empty string rejected
- **Input**: Same property, `validate_value("")`
- **Expected**: `False`

### TC-16-16: Unknown type — returns False
- **Input**: `OntologyProperty("x", "float")`, `validate_value("3.14")`
- **Expected**: `False` (invalid types always reject)

## Test Suite: OntologyProperty serialization

### TC-16-17: to_dict includes new fields
- **Input**: `OntologyProperty("role", "enum", ["admin", "user"], "user")`
- **Expected**: `{"name": "role", "type": "enum", "values": ["admin", "user"], "default": "user"}`

### TC-16-18: from_dict with all fields
- **Input**: `{"name": "role", "type": "enum", "values": ["admin"], "default": "admin"}`
- **Expected**: `OntologyProperty` with `values=["admin"]`, `default="admin"`

### TC-16-19: from_dict with explicit string type (preserved but invalid)
- **Input**: `{"name": "role", "type": "string"}`
- **Expected**: `OntologyProperty` with `type="string"`, `values=[]`, `default=None` (type preserved but `validate_value()` will reject)

### TC-16-20: from_dict backward compat (minimal)
- **Input**: `{"name": "x"}`
- **Expected**: `type="enum"`, `values=[]`, `default=None`

### TC-16-21: Round-trip serialization
- **Input**: Create `OntologyProperty` with all fields, `to_dict()` then `from_dict()`
- **Expected**: Identical object

## Test Suite: OntologyManager.validate_fact()

### TC-16-22: Valid fact — known noun, known prop, valid value
- **Setup**: Ontology with `User.directoryRole` as enum `["admin", "user"]`
- **Input**: `Fact("User", "$u", "directoryRole", "==", "admin")`
- **Expected**: `[]` (no errors)

### TC-16-23: Unknown noun
- **Setup**: Ontology with `User` only
- **Input**: `Fact("Server", "*", "cpu", "==", "90")`
- **Expected**: `["Unknown noun: Server"]` or similar

### TC-16-24: Known noun, unknown property
- **Setup**: Ontology with `User` having only `directoryRole`
- **Input**: `Fact("User", "*", "email", "==", "foo@bar.com")`
- **Expected**: Error mentioning unknown property

### TC-16-25: Known noun, known prop, invalid value
- **Setup**: Ontology with `User.directoryRole` as enum `["admin", "user"]`
- **Input**: `Fact("User", "$u", "directoryRole", "==", "superadmin")`
- **Expected**: Error mentioning invalid value and listing legal values

### TC-16-26: Case-insensitive noun lookup in validate_fact
- **Setup**: Ontology has `User`
- **Input**: `Fact("user", "*", "directoryRole", "==", "admin")`
- **Expected**: `[]` (noun lookup is case-insensitive per existing behavior)

### TC-16-27: Chaining facts (RULED_OUT/CHANGE_STATE) skip validation
- **Setup**: Any ontology
- **Input**: `Fact("RULED_OUT", "*", "User.directoryRole", "==", "true")`
- **Expected**: `[]` (chaining pseudo-nouns are not validated against ontology)
