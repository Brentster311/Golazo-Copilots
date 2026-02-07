# Design Document: WIP-001 - Retirement Savings Calculator

**Status**: DRAFT  
**Author**: Program Manager  
**Date**: 2025-01-26  
**User Story**: [WIP-001-User-Story.md](../WIP-001-User-Story.md)

---

## 1. Summary

Build a browser-based retirement savings calculator web application using Flask. The app allows non-technical users to input their financial parameters and receive a projection of their retirement savings. Data persists locally via JSON files.

---

## 2. Problem Statement

Individuals planning for retirement need a simple, accessible tool to understand if their current savings trajectory will meet their retirement goals. Existing tools are often:
- Overly complex with too many inputs
- Require account creation or personal data sharing
- Embedded in financial product sales funnels
- Not available offline or locally

Users need a **private, simple, local tool** that provides quick retirement projections without friction.

---

## 3. Business Case

### Why Now?
- Foundation for a multi-feature retirement planning suite (WIP-002 through WIP-005)
- Establishes project architecture and patterns for future development
- Delivers immediate user value with minimal scope

### Impact
| Metric | Expected Outcome |
|--------|------------------|
| User adoption | Single user (Project Owner) initially |
| Time to value | < 1 day development cycle |
| Feature foundation | Enables 4 subsequent features |

### Key Performance Indicators (KPIs)
| KPI | Target | Measurement |
|-----|--------|-------------|
| Core calculation accuracy | 100% | Unit tests pass |
| Page load time | < 2 seconds | Manual verification |
| Save/load functionality | Works reliably | Integration tests |
| Input validation | All invalid inputs rejected | Test coverage |

---

## 4. Stakeholders

| Role | Name/Description | Interest |
|------|------------------|----------|
| Project Owner | End user | Needs accurate retirement projections |
| Developer | Copilot/Team | Implements solution |
| Tester | Copilot/Team | Validates functionality |

---

## 5. Functional Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-01 | Web app accessible at localhost:5000 | Must | AC-1 |
| FR-02 | Input form: current age, retirement age, current savings, monthly contribution, annual return rate | Must | AC-2 |
| FR-03 | Calculate and display projected savings at retirement | Must | AC-3 |
| FR-04 | Save calculation inputs to JSON file | Must | AC-4 |
| FR-05 | Load previously saved inputs from JSON file | Must | AC-5 |
| FR-06 | Validate all inputs with user-friendly error messages | Must | AC-6 |
| FR-07 | Clean, accessible UI | Must | AC-7 |

---

## 6. Non-Functional Requirements

| ID | Requirement | Target | Verification |
|----|-------------|--------|--------------|
| NFR-01 | Page load time | < 2 seconds | Manual timing |
| NFR-02 | Form validation feedback | Immediate (< 100ms) | Manual test |
| NFR-03 | Accessibility | Proper labels, contrast | Manual review |
| NFR-04 | Error messages | No technical jargon | Manual review |
| NFR-05 | Browser compatibility | Chrome, Edge, Firefox | Manual test |

---

## 7. Proposed Approach

### 7.1 Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Backend | Python 3.x + Flask | Simple, well-documented, good for prototypes |
| Frontend | HTML + Jinja2 templates + CSS | Native Flask templating, no JS framework needed |
| Styling | Simple CSS (no framework) | Minimal dependencies, easy to customize |
| Data Storage | JSON files | Human-readable, no database setup required |
| Testing | pytest | Standard Python testing framework |

### 7.2 Project Structure

```
RetirementPlanner/
??? app/
?   ??? __init__.py          # Flask app factory
?   ??? routes.py            # Route handlers
?   ??? calculator.py        # Calculation logic
?   ??? storage.py           # JSON file operations
?   ??? templates/
?       ??? base.html        # Base template
?       ??? index.html       # Calculator form
?       ??? result.html      # Results display
??? static/
?   ??? style.css            # Styling
??? data/                    # User data storage (gitignored)
?   ??? savings.json
??? tests/
?   ??? test_calculator.py   # Unit tests
?   ??? test_storage.py      # Storage tests
?   ??? test_routes.py       # Integration tests
??? requirements.txt
??? run.py                   # Application entry point
```

### 7.3 Core Calculation Formula

**Future Value of Savings with Regular Contributions (Compound Interest)**:

```
FV = PV × (1 + r)^n + PMT × [((1 + r)^n - 1) / r]

Where:
- FV  = Future Value (projected savings)
- PV  = Present Value (current savings)
- r   = Monthly interest rate (annual rate / 12)
- n   = Number of months until retirement
- PMT = Monthly contribution
```

### 7.4 User Flow

```
[User visits localhost:5000]
         ?
         ?
[Display calculator form]
         ?
         ?
[User enters: age, retirement age, savings, contribution, return rate]
         ?
         ?
[Validate inputs] ??(invalid)??? [Show error messages]
         ?                              ?
      (valid)                           ?
         ?                              ?
         ?                              ?
[Calculate projection]                  ?
         ?                              ?
         ?                              ?
[Display results] ???????????????????????
         ?
         ?
[Option to save inputs to file]
```

---

## 8. Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Django | Full-featured, admin panel | Overkill for simple app | Rejected |
| FastAPI | Modern, async | Better for APIs, not server-rendered HTML | Rejected |
| SQLite database | Better for complex queries | Unnecessary complexity for single-user | Rejected |
| React frontend | Rich interactivity | Over-engineered for forms | Rejected |
| Bootstrap CSS | Quick styling | External dependency | Rejected |

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| File corruption on crash | Low | Medium | Validate JSON on read; backup before write |
| Browser compatibility issues | Low | Low | Test on major browsers; use standard HTML/CSS |
| Calculation errors | Medium | High | Comprehensive unit tests; validate against known values |
| User enters invalid data | High | Low | Client + server-side validation |

---

## 10. Open Questions

| Question | Status | Resolution |
|----------|--------|------------|
| Should we include a graph visualization? | Deferred | Not in WIP-001 scope; consider for future story |
| Should we support multiple saved profiles? | Deferred | Single profile for WIP-001; multi-profile in future |

---

## 11. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Python 3.8+ | Runtime | Standard installation |
| Flask 2.x | Library | pip install |
| pytest | Dev dependency | pip install |

No external services or APIs required.

---

## 12. Migration / Rollout / Rollback Plan

### Rollout
1. Install Python dependencies: `pip install -r requirements.txt`
2. Run application: `python run.py`
3. Access at `http://localhost:5000`

### Rollback
- Delete application folder
- No system-level changes to undo

### Data Migration
- N/A (greenfield project)

---

## 13. Observability Plan

| Aspect | Approach |
|--------|----------|
| Logging | Python `logging` module to console |
| Monitoring | N/A (local app) |
| Alerting | N/A (local app) |
| Debugging | Flask debug mode during development |

---

## 14. Test Strategy Summary

| Test Type | Scope | Tools |
|-----------|-------|-------|
| Unit tests | Calculator logic, validation | pytest |
| Integration tests | Routes, save/load | pytest + Flask test client |
| Manual tests | UI, accessibility, browser compat | Human verification |

**Test-First Approach**: All calculation logic and validation will have tests written before implementation code (TDD).

---

## 15. Approval Checklist

- [ ] Reviewer has reviewed this document
- [ ] Architect has validated technical approach
- [ ] Test cases have been defined
- [ ] Ready for Developer role
