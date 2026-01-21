# RETRO-001: TDD Violation - Code Written Before Tests

**Triggered during**: GCP-002  
**Date**: 2026-01-20  
**Status**: RESOLVED

## Problem Observed
Developer role wrote production code (`Golazo_Copilot.py`) before test code (`tests/test_golazo_copilot.py`), violating TDD (Test-Driven Development) principles.

## Root Cause Analysis
1. Developer role instructions didn't explicitly require tests FIRST
2. "Add/adjust tests" was listed but not sequenced before code
3. No forbidden action preventing code-before-tests
4. Tester role created Test Cases *document* but Developer didn't write test *code* first

## Proposed Process Change
Update Developer role instructions to:
1. Add "Write test code FIRST" to Responsibilities
2. Add "May NOT write production code before test code" to Forbidden actions

## Impact Assessment
- Enforces TDD discipline
- Tests become a gate, not an afterthought
- Minor update to `.github/roles/developer.md` required

## Resolution
Updated `.github/roles/developer.md`:
- Added to Responsibilities: "Write test code FIRST based on Test Cases document (TDD red phase)"
- Added to Forbidden actions: "May NOT write production code before test code exists for new functionality"

Updated `.github/copilot-instructions.md`:
- Added to DoD: "Test code written before production code"
- Added to state machine: "Developer must write test code before production code (TDD)"

## Lessons Learned
- Explicit sequencing matters — "write tests" is not the same as "write tests FIRST"
- Forbidden actions are powerful enforcement mechanisms
