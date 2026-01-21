# GCP-003: Test Cases

## Test Strategy
Manual verification by file inspection. No automated tests needed for documentation changes.

---

## Test Cases

### TC-001: Developer Role - TDD Requirement Present
**Description**: Verify developer.md requires test code before production code
**Steps**:
1. Open `.github/roles/developer.md`
2. Search for "test code FIRST" or equivalent
**Expected**: Text requiring tests before production code exists in Responsibilities

### TC-002: Developer Role - TDD Forbidden Action Present  
**Description**: Verify developer.md forbids code before tests
**Steps**:
1. Open `.github/roles/developer.md`
2. Check Forbidden actions section
**Expected**: Text forbidding production code before test code exists

### TC-003: Builder Role - Branch Creation Present
**Description**: Verify builder.md includes branch creation responsibility
**Steps**:
1. Open `.github/roles/builder.md`
2. Search for "branch" or "checkout"
**Expected**: Instructions for creating `<workitem-id>` branch exist

### TC-004: Builder Role - Commit Operations Present
**Description**: Verify builder.md includes commit/push responsibility
**Steps**:
1. Open `.github/roles/builder.md`
2. Search for "commit" and "push"
**Expected**: Instructions for committing and pushing changes exist

### TC-005: Spine - DoD Branch Checkbox Present
**Description**: Verify copilot-instructions.md DoD includes branch creation
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Find DoD Checklist section
**Expected**: Checkbox for "Feature branch `<workitem-id>` created" exists

### TC-006: Spine - DoD TDD Checkbox Present
**Description**: Verify copilot-instructions.md DoD includes TDD requirement
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Find DoD Checklist section
**Expected**: Checkbox for "Test code written before production code" exists

### TC-007: Spine - State Machine Git Operations
**Description**: Verify state machine documents Builder git responsibilities
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Find State transition rules section
**Expected**: Rules mention Builder handling git before Developer and after Documentor

---

## Coverage Matrix

| Acceptance Criterion | Test Case |
|---------------------|-----------|
| Developer requires tests first | TC-001 |
| Developer forbids code before tests | TC-002 |
| Builder creates branch | TC-003 |
| Builder commits/pushes | TC-004 |
| DoD has branch checkbox | TC-005 |
| DoD has TDD checkbox | TC-006 |
| State machine has git rules | TC-007 |
