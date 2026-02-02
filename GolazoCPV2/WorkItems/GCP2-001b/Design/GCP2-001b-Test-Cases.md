# GCP2-001b: Requirements Review & Test Cases

**Work Item**: GCP2-001b - Consent Enforcement  
**Role**: Tester (merged Reviewer + Tester per GCP2-002)  
**Date**: 2026-01-31

---

## Part 1: Requirements Review

### User Story Review

| Element | Status | Notes |
|---------|--------|-------|
| Title | ? Clear | "Consent-Based Enforcement" |
| User story format | ? Complete | Well-formed |
| Acceptance criteria | ? Clear | 7 testable items |
| Out of scope | ? Clear | LLM inference excluded |

### Design Doc Alignment

| AC | Design Coverage | Status |
|----|-----------------|--------|
| AC-1: ConsentEnforcer detects skips | Pattern matching design | ? |
| AC-2: Ambiguous triggers clarification | Clarification prompts | ? |
| AC-3: Skips confirmed with role list | SkipResult dataclass | ? |
| AC-4: Warning for quality gates | Quality gate handling | ? |
| AC-5: Deviations logged | Deviation record format | ? |
| AC-6: get_deviations() returns audit | API design | ? |
| AC-7: No action until clarification | Ambiguous handling | ? |

### Architect Feedback Integration

| Issue | Resolution | Test Impact |
|-------|------------|-------------|
| Remove `force_transition()` | ConsentEnforcer only records | Adjust test expectations |
| Add `force` to machine.transition() | Modify GCP2-001a | Add new tests |
| Add `is_quality_gate()` | New method | Add test |
| Add `consent_type` to deviation | Extended record | Verify in tests |

---

## Part 2: Test Cases

### Test Coverage Summary

| Category | Count |
|----------|-------|
| Pattern Detection | 8 |
| Clarification Prompts | 4 |
| Deviation Recording | 5 |
| Quality Gate Warnings | 3 |
| Integration | 3 |
| Edge Cases | 4 |
| **Total** | 27 |

---

### Pattern Detection Tests

**TC-01**: Explicit skip - "skip the tester role"
- **Input**: "skip the tester role"
- **Expected**: RequestAnalysis(type='explicit_skip', detected_skips=['tester'])

**TC-02**: Explicit skip - "skip to developer"
- **Input**: "skip to developer"
- **Expected**: RequestAnalysis(type='explicit_skip', detected_skips=['developer'])

**TC-03**: Explicit skip - "fast-track"
- **Input**: "fast-track this"
- **Expected**: RequestAnalysis(type='explicit_skip')

**TC-04**: Explicit skip - "fast track" (space)
- **Input**: "fast track this"
- **Expected**: RequestAnalysis(type='explicit_skip')

**TC-05**: Ambiguous - "just fix"
- **Input**: "just fix this bug"
- **Expected**: RequestAnalysis(type='ambiguous')

**TC-06**: Ambiguous - "quick fix"
- **Input**: "quick fix please"
- **Expected**: RequestAnalysis(type='ambiguous')

**TC-07**: Normal - technical request
- **Input**: "Add null check to GetUser method"
- **Expected**: RequestAnalysis(type='normal')

**TC-08**: Case insensitive
- **Input**: "SKIP THE TESTER ROLE"
- **Expected**: RequestAnalysis(type='explicit_skip', detected_skips=['tester'])

---

### Clarification Prompt Tests

**TC-09**: Ambiguous generates prompt
- **Input**: RequestAnalysis(type='ambiguous')
- **Expected**: Non-empty clarification string

**TC-10**: Normal has no prompt
- **Input**: RequestAnalysis(type='normal')
- **Expected**: Empty or None

**TC-11**: Explicit skip has no prompt
- **Input**: RequestAnalysis(type='explicit_skip')
- **Expected**: Empty or None (user was explicit)

**TC-12**: Quality gate warning prompt
- **Input**: Skip request for 'tester'
- **Expected**: Warning about quality gate in prompt

---

### Deviation Recording Tests

**TC-13**: Record deviation saves to state
- **Steps**: Call `record_deviation()`, reload state
- **Expected**: Deviation in state.deviations[]

**TC-14**: Deviation includes timestamp
- **Steps**: Record deviation
- **Expected**: `timestamp` field present

**TC-15**: Deviation includes user's exact words
- **Steps**: Record deviation with reason="just fix it"
- **Expected**: `reason` field is "just fix it"

**TC-16**: Deviation includes consent_type
- **Steps**: Record explicit skip
- **Expected**: `consent_type` is "explicit"

**TC-17**: get_deviations() returns all
- **Steps**: Record 3 deviations, call get_deviations()
- **Expected**: List of 3 deviations

---

### Quality Gate Warning Tests

**TC-18**: is_quality_gate("tester") returns True
- **Expected**: True

**TC-19**: is_quality_gate("architect") returns True
- **Expected**: True

**TC-20**: is_quality_gate("developer") returns False
- **Expected**: False

---

### Integration Tests

**TC-21**: Full skip flow - explicit
- **Steps**: Analyze explicit skip, record deviation, force transition
- **Expected**: State updated, deviation logged, role changed

**TC-22**: Full skip flow - ambiguous then confirm
- **Steps**: Analyze ambiguous, get prompt, confirm, record, transition
- **Expected**: Proper flow with clarification step

**TC-23**: Machine.transition() with force=True skips DoR
- **Steps**: At architect (DoR incomplete), transition("developer", force=True)
- **Expected**: Transition succeeds despite incomplete DoR

---

### Edge Cases

**TC-24**: Empty message
- **Input**: ""
- **Expected**: RequestAnalysis(type='normal')

**TC-25**: Multiple patterns match
- **Input**: "just fix this, skip to developer"
- **Expected**: Explicit takes precedence over ambiguous

**TC-26**: Unknown role in skip
- **Input**: "skip the foo role"
- **Expected**: RequestAnalysis with detected_skips=['foo'], validation elsewhere

**TC-27**: Skip to current role
- **Input**: At developer, "skip to developer"
- **Expected**: Handled gracefully (no-op or error)

---

## Traceability Matrix

| AC | Test Cases |
|----|------------|
| AC-1 | TC-01 to TC-08 |
| AC-2 | TC-05, TC-06, TC-09 |
| AC-3 | TC-21, TC-22 |
| AC-4 | TC-12, TC-18 to TC-20 |
| AC-5 | TC-13 to TC-16 |
| AC-6 | TC-17 |
| AC-7 | TC-09, TC-22 |

---

## Approval

**Requirements Review**: ? Approved (Architect feedback integrated)
**Test Cases**: ? 27 test cases defined, covering all ACs
