# Review Comments: WIP-001 - Retirement Savings Calculator

**Reviewer**: Reviewer Role  
**Date**: 2025-01-26  
**Status**: ? APPROVED WITH MINOR RECOMMENDATIONS

---

## 1. Overall Assessment

| Aspect | Rating | Notes |
|--------|--------|-------|
| Clarity | ? Good | Requirements and approach are clear |
| Feasibility | ? Good | Stack is appropriate, scope is achievable |
| Risk Coverage | ? Good | Key risks identified with mitigations |
| Operability | ? Good | Local app, minimal ops concerns |
| Completeness | ? Good | All sections present and thorough |

**Verdict**: Ready to proceed to Architect and Tester roles.

---

## 2. User Story Review

### Strengths
- Clear "As a / I want / So that" structure
- Acceptance criteria are testable and bounded (7 items - at limit)
- Out of scope is well-defined
- Assumptions are explicitly labeled

### Minor Observations

| Item | Observation | Severity | Action |
|------|-------------|----------|--------|
| AC-4/AC-5 | "Save" and "Load" are separate criteria but could clarify if these are buttons, menu items, or automatic | Low | **Non-functional clarification** - Designer/Developer discretion |
| Assumption | "Single-user mode" should clarify what happens if user tries to open app twice | Low | Addressed in risks |

**No scope/behavior changes required** - observations are implementation details.

---

## 3. Design Document Review

### Strengths
- Comprehensive technology justification
- Clear project structure
- Formula documented with variable definitions
- User flow diagram is helpful
- Test strategy aligns with TDD requirements

### Technical Review

| Aspect | Finding | Severity | Recommendation |
|--------|---------|----------|----------------|
| **Formula accuracy** | Compound interest formula is correct for monthly compounding | ? None | Verified |
| **Input validation** | Design mentions validation but doesn't list specific rules | Low | Add validation rules table in Architect phase |
| **Error handling** | JSON read/write error handling not detailed | Low | Architect should specify |
| **File path** | `data/savings.json` - should clarify if path is relative to app or user home | Low | Architect should specify |

### Edge Cases to Address

| Edge Case | Current Coverage | Recommendation |
|-----------|------------------|----------------|
| User enters 0% return rate | Not specified | Handle division by zero in formula |
| User enters same current/retirement age | Not specified | Validate retirement_age > current_age |
| JSON file doesn't exist on first load | Not specified | Create empty/default on first run |
| JSON file is corrupted/invalid | Mentioned in risks | Architect should specify recovery behavior |

---

## 4. Naming Review

| Proposed Name | Assessment | Alternative (if any) |
|---------------|------------|----------------------|
| `calculator.py` | ? Clear | - |
| `storage.py` | ? Clear | - |
| `routes.py` | ? Standard Flask convention | - |
| `savings.json` | ? Descriptive | - |
| `result.html` | ?? Consider | `projection.html` (more specific) |

**Non-functional clarification**: `result.html` vs `projection.html` is developer discretion.

---

## 5. Risk Assessment

| Risk from Design Doc | Reviewer Assessment |
|----------------------|---------------------|
| File corruption on crash | Mitigation adequate |
| Browser compatibility | Low risk, standard HTML |
| Calculation errors | Mitigated by TDD approach |
| Invalid user data | Needs validation rules defined |

### Additional Risk Identified

| Risk | Likelihood | Impact | Recommended Mitigation |
|------|------------|--------|------------------------|
| Return rate entered as whole number vs decimal (5 vs 0.05) | High | Medium | UI should clarify expected format (e.g., "Enter 7 for 7%") |

**Note**: This is a UX clarification, not a scope change. No new User Story required.

---

## 6. Operability Review

| Concern | Assessment |
|---------|------------|
| Startup complexity | Low - single command |
| Failure modes | File I/O only; no external dependencies |
| Debugging | Flask debug mode adequate |
| Data recovery | User's responsibility (documented) |

? No operability concerns for local development app.

---

## 7. Verdict & Recommendations

### Approved for Next Phase ?

The design is **complete and feasible**. Minor items below should be addressed by Architect:

1. **Define input validation rules** (min/max values, format expectations)
2. **Specify 0% return rate handling** (edge case for formula)
3. **Clarify file path resolution** (relative to app root)
4. **Add UI hint for return rate format** (whole number percentage)

### No New User Stories Required

All observations are implementation details or non-functional clarifications within existing scope.

---

## 8. Checklist for Architect

- [ ] Define input validation rules table
- [ ] Specify edge case handling for 0% return rate
- [ ] Clarify data file path resolution strategy
- [ ] Review and approve project structure
- [ ] Validate technology choices
