# Role Decision Document: Retrospective

**Work Item**: CALJACK-001  
**Role**: Retrospective  
**Date**: 2025-01-XX  
**Trigger**: User identified TDD violation - Tester did not write automated test files

---

## Issue Identified

The Tester role only created documentation (`docs/tests/CALJACK-001-test-cases.md`) instead of actual automated test files in the codebase. This violated TDD principles where tests should:
1. Exist as runnable code
2. Fail before production code is written
3. Pass after Developer implements features

---

## Evidence

- `docs/roles/CALJACK-001-tester.md` shows Tester only documented tests
- `docs/roles/CALJACK-001-developer.md` shows Developer wrote both tests AND production code
- Actual test files created by Developer, not Tester

---

## Root Cause

The `.github/roles/tester.md` instruction is ambiguous:
- Says "Automated tests where feasible" without clarifying these must be **actual test files**
- Says "Do not write/modify production code" but tests are NOT production code
- No explicit TDD gate requiring tests to fail first

---

## Proposed Changes to `.github/roles/tester.md`

### Change 1: Clarify that Tester writes actual test files

**Current text:**
```markdown
## Required outputs
- `docs/tests/<workitem-id>-test-cases.md`
- `docs/roles/<workitem-id>-tester.md`
- Automated tests where feasible (may be stubbed/skipped only with explicit justification and follow-up plan).
```

**Proposed text:**
```markdown
## Required outputs
- `docs/tests/<workitem-id>-test-cases.md` (test plan documentation)
- `docs/roles/<workitem-id>-tester.md`
- **Actual automated test files** in the project's test directory (e.g., `tests/test_*.py`)
  - Tests must be runnable via the project's test framework (e.g., `pytest`)
  - Tests MUST FAIL initially (no production code exists yet)
  - Tests may be stubbed/skipped only with explicit justification and follow-up plan
```

### Change 2: Clarify what "production code" means

**Current text:**
```markdown
## Forbidden actions
- Do not write/modify production code.
- Do not invent acceptance criteria; send gaps back to **Project Owner**.
```

**Proposed text:**
```markdown
## Forbidden actions
- Do not write/modify **production code** (application code in `src/`, `game/`, `app/`, etc.).
- Test code IS allowed and required - tests are NOT production code.
- Do not invent acceptance criteria; send gaps back to **Project Owner Assistant**.
```

### Change 3: Add TDD verification step

**Add new section:**
```markdown
## TDD Verification (MANDATORY)

Before completing the Tester role:
1. Run the test suite (e.g., `pytest tests/ -v`)
2. Verify tests **FAIL** with meaningful error messages
3. Document the failure output in the role document

If tests pass before Developer writes code, something is wrong:
- Tests may be testing existing code (not new functionality)
- Tests may be incorrectly stubbed
```

---

## Proposed Changes to `.github/copilot-instructions.md`

### Change 1: Clarify DoR includes failing tests

**Current text:**
```markdown
### Definition of Ready (DoR) — before writing production code

You MUST NOT write or modify production code until **ALL** of the following exist for the work item:

1) A User Story document
2) A Design Review document including a business case
3) Review notes from **Reviewer** and **Architect**
4) A Test Plan / Test Cases document (TDD-first)
```

**Proposed text:**
```markdown
### Definition of Ready (DoR) — before writing production code

You MUST NOT write or modify production code until **ALL** of the following exist for the work item:

1) A User Story document
2) A Design Doc document including a business case
3) Review notes from **Reviewer** and **Architect**
4) A Test Plan / Test Cases document (TDD-first)
5) **Automated test files that FAIL** (Tester creates actual test code, not just documentation)
```

---

## Proposed Changes to `.github/roles/developer.md`

### Change 1: Clarify Developer does NOT write new tests

**Current text:**
```markdown
## Responsibilities
- Implement exactly what is specified (User Story + Design Review).
- Add/adjust automated tests so new/changed behavior is covered.
```

**Proposed text:**
```markdown
## Responsibilities
- Implement exactly what is specified (User Story + Design Doc).
- Write production code to make the **existing failing tests pass**.
- May add additional edge case tests if discovered during implementation, but primary tests come from Tester.
```

---

## Summary of Changes

| File | Change |
|------|--------|
| `.github/roles/tester.md` | Clarify Tester writes actual test files, not just docs |
| `.github/roles/tester.md` | Clarify test code is NOT production code |
| `.github/roles/tester.md` | Add TDD verification step (tests must fail) |
| `.github/copilot-instructions.md` | Add "failing tests" to DoR checklist |
| `.github/roles/developer.md` | Clarify Developer makes tests pass, doesn't write new tests |

---

## Next Steps

1. ~~Review proposed changes with Project Owner~~ ? Approved
2. ~~Apply approved changes to instruction files~~ ? Applied
3. Use corrected process for CALJACK-002 onwards

---

## Changes Applied

The following files were updated:

- ? `.github/roles/tester.md` - Clarified Tester writes actual test files, added TDD verification section
- ? `.github/roles/developer.md` - Clarified Developer makes tests pass, doesn't write primary tests
- ? `.github/copilot-instructions.md` - Added "Failing tests exist" to DoR checklist
