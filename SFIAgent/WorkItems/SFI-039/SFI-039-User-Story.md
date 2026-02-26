# SFI-039: Achieve 70% Code Coverage on All Source Files

**Status**: IMPLEMENTED

**User Story**
- **Title**: Achieve 70% Code Coverage on All Source Files
- **As a**: Developer maintaining SFIReporter
- **I want**: Every source file in `src/sfi_reporter/` to have at least 70% test coverage
- **So that**: Regressions are caught early and code quality is maintained across the entire codebase
- **Out of scope**: Refactoring production code; changing existing behavior; adding new features
- **Assumptions**:
  - **Assumption (explicit)**: Tests will use mocks/patches for Tkinter GUI widgets, Graph API calls, and filesystem operations
  - **Assumption (explicit)**: Coverage is measured by `pytest-cov` statement coverage
  - **Assumption (explicit)**: Existing tests remain untouched unless they have bugs
- **Acceptance Criteria** (bulleted, testable):
  - [ ] `app.py` coverage ≥ 70%
  - [ ] `copilot_panel.py` coverage ≥ 70%
  - [ ] `copilot_tools.py` coverage ≥ 70%
  - [ ] `dialogs.py` coverage ≥ 70%
  - [ ] `kpi_analyzer.py` coverage ≥ 70%
  - [ ] `logging_config.py` coverage ≥ 70%
  - [ ] `query_builder.py` coverage ≥ 70%
- **Non-functional requirements**: No new test should take >2s; total suite stays under 120s
- **Telemetry / metrics expected**: `pytest --cov` report shows all files ≥ 70%
- **Rollout / rollback notes**: Test-only changes — no production code modified

## Current Coverage Baseline

| File | Stmts | Current Coverage | Gap to 70% |
|------|------:|:----------------:|:-----------:|
| app.py | 681 | 0% | ~476 stmts |
| copilot_panel.py | 392 | 34% | ~141 stmts |
| copilot_tools.py | 202 | 0% | ~141 stmts |
| dialogs.py | 790 | 14% | ~443 stmts |
| kpi_analyzer.py | 523 | 59% | ~58 stmts |
| logging_config.py | 42 | 0% | ~29 stmts |
| query_builder.py | 430 | 40% | ~129 stmts |

## Closure

- Summary of delivery: Added comprehensive tests for all targeted low-coverage modules and raised every source file to at least 70% coverage.
- Acceptance criteria validation: PASS (all seven listed module thresholds met/exceeded).
- Future work items:
  - Consolidate shared test fixtures (copilot mock + Tk root) into `conftest.py`.
  - Document the copilot test-mocking pattern in contributor guidance.
- Final status confirmation: **IMPLEMENTED**
