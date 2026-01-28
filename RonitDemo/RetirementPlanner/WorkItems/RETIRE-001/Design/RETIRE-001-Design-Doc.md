# Design Document: RETIRE-001

## Summary
Build an MVP Windows GUI application that allows a user to input their current financial situation and retirement goals, then calculates whether they are on track to achieve their desired monthly retirement income.

## Problem Statement
Planning for retirement requires understanding the gap between current savings trajectory and future income needs. Without a tool to perform these calculations, users must rely on mental math, spreadsheets, or complex online tools that may not fit their specific needs.

## Business Case

### Why Now
- User needs a personalized retirement planning tool
- Existing solutions are either too complex or lack flexibility
- MVP approach allows rapid iteration based on real usage

### Impact
- Provides immediate visibility into retirement readiness
- Enables informed decisions about savings rate adjustments
- Foundation for more sophisticated features (inflation, taxes, Social Security)

### KPIs (for MVP)
- Application launches successfully
- User can complete full input ? projection workflow in under 2 minutes
- Data persists correctly between sessions

## Stakeholders
| Role | Name/Description | Interest |
|------|------------------|----------|
| User | Project Owner (technical) | Primary user, will test and iterate |
| Developer | Copilot-assisted | Implementation |

## Functional Requirements
| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | Input field for current age (integer, 18-100) | AC-1 |
| FR-2 | Input field for retirement age (integer, > current age, ? 100) | AC-1 |
| FR-3 | Input field for current savings (decimal, ? 0) | AC-2 |
| FR-4 | Input field for monthly contribution (decimal, ? 0) | AC-3 |
| FR-5 | Input field for desired monthly retirement income (decimal, > 0) | AC-4 |
| FR-6 | Calculate projected retirement savings using compound interest | AC-5 |
| FR-7 | Display on-track status with gap amount if applicable | AC-6 |
| FR-8 | Save user data to local file on input change or explicit save | AC-7 |
| FR-9 | Load user data from local file on application launch | AC-7 |

## Non-Functional Requirements
| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-1 | Windows GUI using Python | Runs on Windows 10/11 |
| NFR-2 | Data persistence abstraction | Interface defined, file-based implementation |
| NFR-3 | Input validation with user-friendly errors | No crashes on invalid input |
| NFR-4 | Responsive UI | Calculations complete in < 1 second |

## Proposed Approach

### Architecture Overview
```
???????????????????????????????????????????????????????????
?                    Presentation Layer                    ?
?                  (Tkinter GUI - Windows)                 ?
???????????????????????????????????????????????????????????
?                    Business Logic Layer                  ?
?              (RetirementCalculator Service)              ?
???????????????????????????????????????????????????????????
?                   Data Access Layer                      ?
?     ???????????????????????????????????????????????     ?
?     ?         IDataRepository (Interface)          ?     ?
?     ???????????????????????????????????????????????     ?
?                          ?                               ?
?     ???????????????????????????????????????????????     ?
?     ?      JsonFileRepository (Implementation)     ?     ?
?     ???????????????????????????????????????????????     ?
???????????????????????????????????????????????????????????
```

### Technology Stack
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.x | User familiarity, rapid development |
| GUI Framework | Tkinter | Built into Python, no extra dependencies, Windows-native look |
| Data Format | JSON | Human-readable, easy to debug, no dependencies |
| Testing | pytest | Standard Python testing framework |

### Component Breakdown
1. **Models** (`models/`)
   - `UserProfile`: Dataclass holding user's financial data
   - `ProjectionResult`: Dataclass holding calculation results

2. **Repository** (`repository/`)
   - `IDataRepository`: Abstract base class (interface)
   - `JsonFileRepository`: JSON file implementation

3. **Services** (`services/`)
   - `RetirementCalculator`: Business logic for projections

4. **UI** (`ui/`)
   - `MainWindow`: Tkinter-based main application window

5. **App Entry** (`main.py`)
   - Application bootstrap and dependency injection

### Calculation Formula (MVP)
```
Future Value = P × (1 + r)^n + PMT × [((1 + r)^n - 1) / r]

Where:
- P = Current savings (principal)
- r = Annual return rate (assumption: 7% default)
- n = Years until retirement
- PMT = Annual contribution (monthly × 12)

Required Nest Egg = (Desired Monthly Income × 12) / Safe Withdrawal Rate (4%)

On Track = Future Value >= Required Nest Egg
Gap = Required Nest Egg - Future Value
```

## Alternatives Considered

### GUI Framework Alternatives
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Tkinter | Built-in, simple, lightweight | Dated appearance | **Selected** - No dependencies, MVP focus |
| PyQt/PySide | Modern look, powerful | Large dependency, licensing | Rejected for MVP |
| Dear PyGui | Modern, fast | Extra dependency | Future consideration |

### Data Storage Alternatives
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| JSON file | Simple, readable | No encryption | **Selected** - MVP simplicity |
| SQLite | Queryable, robust | Overkill for single record | Future option |
| Pickle | Easy Python serialization | Not human-readable | Rejected |

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Calculation accuracy expectations | Medium | Medium | Clearly label as "estimate" in UI |
| User enters unrealistic values | Medium | Low | Input validation with reasonable bounds |
| File corruption | Low | Medium | Graceful handling, start fresh if corrupt |

## Open Questions
1. Should we allow user to configure expected return rate? **Decision**: Hard-code 7% for MVP, make configurable in future story.
2. Safe withdrawal rate assumption? **Decision**: Use 4% rule as default.

## Dependencies
- Python 3.8+ (standard library only for MVP)
- No external packages required for core functionality
- pytest for testing (dev dependency)

## Migration / Rollout / Rollback Plan
- **Rollout**: Local installation, user runs `python main.py` or bundled executable
- **Rollback**: User deletes application folder
- **Data Migration**: N/A (new application)

## Observability Plan
- MVP: No telemetry (local app, user privacy)
- Error handling: Display user-friendly messages, log to console for debugging

## Test Strategy Summary
| Test Type | Scope | Tools |
|-----------|-------|-------|
| Unit Tests | Calculator service, Repository | pytest |
| Integration Tests | End-to-end data flow | pytest |
| Manual Testing | GUI interactions | User acceptance |

## File Structure (Proposed)
```
RetirementPlanner/
??? src/
?   ??? __init__.py
?   ??? main.py
?   ??? models/
?   ?   ??? __init__.py
?   ?   ??? user_profile.py
?   ??? repository/
?   ?   ??? __init__.py
?   ?   ??? base_repository.py
?   ?   ??? json_file_repository.py
?   ??? services/
?   ?   ??? __init__.py
?   ?   ??? retirement_calculator.py
?   ??? ui/
?       ??? __init__.py
?       ??? main_window.py
??? tests/
?   ??? __init__.py
?   ??? test_retirement_calculator.py
?   ??? test_json_file_repository.py
??? data/
?   ??? (user_profile.json created at runtime)
??? WorkItems/
    ??? RETIRE-001/
        ??? (artifacts)
```
