# GCP2-008: Requirements Review & Test Cases

**Work Item**: GCP2-008 - Configuration System  
**Role**: Tester (merged Reviewer + Tester)  
**Date**: 2026-01-31

---

## Part 1: Requirements Review

### Design Doc Alignment

| AC | Design Coverage | Status |
|----|-----------------|--------|
| AC-1: GolazoConfig loads from YAML | Config loading design | ? |
| AC-2: Defaults when no file | Default values section | ? |
| AC-3: StateMachine uses config | Refactoring section | ? |
| AC-4: Schema documented | Schema section | ? |
| AC-5: Existing tests pass | Migration strategy | ? |
| AC-6: New tests for config | Test strategy | ? |

### Architect Feedback Integration

| Issue | Resolution |
|-------|------------|
| Immutable config | Use frozen dataclass |
| ConsentEnforcer config | Pass via constructor |
| Schema versioning | Add version check |

---

## Part 2: Test Cases

### Test Coverage Summary

| Category | Count |
|----------|-------|
| Config Loading | 6 |
| Default Values | 4 |
| Machine Integration | 5 |
| Consent Integration | 3 |
| Error Handling | 4 |
| **Total** | 22 |

---

### Config Loading Tests

**TC-01**: Load from golazo.yaml
- **Setup**: Create `golazo.yaml` with custom roles
- **Expected**: Config.roles matches file

**TC-02**: Load from .golazo/config.yaml
- **Setup**: Create `.golazo/config.yaml`, no `golazo.yaml`
- **Expected**: Config loaded from nested path

**TC-03**: golazo.yaml takes precedence
- **Setup**: Both files exist with different values
- **Expected**: `golazo.yaml` values used

**TC-04**: Config is immutable
- **Setup**: Load config, try to modify
- **Expected**: Raises error (frozen)

**TC-05**: Schema version check
- **Setup**: Config with `version: "1.0"`
- **Expected**: Loads successfully

**TC-06**: Unknown version
- **Setup**: Config with `version: "99.0"`
- **Expected**: Raises ValueError

---

### Default Values Tests

**TC-07**: No config file uses defaults
- **Setup**: No config file exists
- **Expected**: Default roles, transitions, etc.

**TC-08**: Default roles match current
- **Expected**: 8 roles: project-owner through documentor

**TC-09**: Default transitions match current
- **Expected**: Linear flow project-owner ? documentor

**TC-10**: Default DoR/DoD items match current
- **Expected**: 4 DoR items, 7 DoD items

---

### Machine Integration Tests

**TC-11**: Machine uses config roles
- **Setup**: Config with custom roles
- **Expected**: `can_transition` validates against config roles

**TC-12**: Machine uses config transitions
- **Setup**: Config with custom transitions
- **Expected**: Transition validation uses config

**TC-13**: Machine uses config DoR
- **Setup**: Config with 2 DoR items
- **Expected**: `is_dor_complete()` checks only those 2

**TC-14**: Existing machine tests pass
- **Expected**: All 21 machine tests pass unchanged

**TC-15**: Machine without config uses defaults
- **Setup**: Create machine without explicit config
- **Expected**: Uses default config

---

### Consent Integration Tests

**TC-16**: ConsentEnforcer uses config quality gates
- **Setup**: Config with custom quality gates
- **Expected**: `is_quality_gate()` uses config

**TC-17**: Existing consent tests pass
- **Expected**: All 24 consent tests pass unchanged

**TC-18**: ConsentEnforcer inherits machine config
- **Setup**: Create enforcer from machine with config
- **Expected**: Enforcer uses same config

---

### Error Handling Tests

**TC-19**: Invalid YAML syntax
- **Setup**: Malformed YAML file
- **Expected**: Clear error message with line number

**TC-20**: Invalid type for roles
- **Setup**: `roles: "not a list"`
- **Expected**: TypeError with helpful message

**TC-21**: Unknown keys warn but load
- **Setup**: Config with `unknown_key: value`
- **Expected**: Warning logged, config loads

**TC-22**: Empty config file
- **Setup**: Empty `golazo.yaml`
- **Expected**: Uses all defaults

---

## Traceability Matrix

| AC | Test Cases |
|----|------------|
| AC-1 | TC-01, TC-02, TC-03 |
| AC-2 | TC-07, TC-08, TC-09, TC-10 |
| AC-3 | TC-11, TC-12, TC-13, TC-15 |
| AC-4 | TC-05, TC-06 |
| AC-5 | TC-14, TC-17 |
| AC-6 | All new tests |

---

## Approval

**Requirements Review**: ? Approved
**Test Cases**: ? 22 test cases defined
