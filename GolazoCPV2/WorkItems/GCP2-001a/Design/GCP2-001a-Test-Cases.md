# GCP2-001a: Requirements Review & Test Cases

**Work Item**: GCP2-001a - Core State Machine  
**Role**: Tester (merged Reviewer + Tester per GCP2-002)  
**Date**: 2026-01-31

---

## Part 1: Requirements Review (Reviewer Responsibilities)

### User Story Review

| Element | Status | Notes |
|---------|--------|-------|
| Title | ? Clear | "Core State Machine" |
| User story format | ? Complete | Well-formed |
| Acceptance criteria | ? Clear | 7 testable items |
| Out of scope | ? Clear | 4 items excluded |

### Design Doc Alignment

| AC | Design Coverage | Status |
|----|-----------------|--------|
| AC-1: GolazoStateMachine class | High-level design | ? |
| AC-2: current_role/phase props | API section | ? |
| AC-3: can_transition() | Transition matrix | ? |
| AC-4: transition() | API section | ? |
| AC-5: check_dor/dod() | API section | ? |
| AC-6: DoR gate | Phase boundaries | ? |
| AC-7: State persistence | Uses GCP2-003 | ? |

### Architect Feedback Integration

**Architect raised 4 issues. All must be addressed:**

| Issue | Resolution | Test Impact |
|-------|------------|-------------|
| `transition()` return type | Change to `tuple[bool, str]` | Update test expectations |
| Role name validation | Add VALID_ROLES check | Add test for invalid role |
| `mark_dor()`/`mark_dod()` methods | Add to API | Add tests for these |
| roleHistory update | Document and implement | Add test for history |

### Ambiguities Identified

**Ambiguity 1**: What happens if user tries to go backward (e.g., developer ? tester)?
- **Decision**: Not allowed. Return `(False, "Cannot go backward")`.

**Ambiguity 2**: Can Builder be called early for branch creation?
- **User Story mentions**: "builder (branch creation at start)"
- **Decision**: Builder has special early-call permission for `branchCreated` DoD item only. Add `create_branch()` method or allow transition to builder before DoR.
- **Recommendation**: Defer special builder logic to GCP2-001b (consent). For now, builder is only after refactor-expert.

**Ambiguity 3**: What if DoR is marked complete but artifacts don't exist?
- **Decision**: State machine trusts the DoR flags. Artifact verification is out of scope (could be future enhancement).

---

## Part 2: Test Cases (Tester Responsibilities)

### Test Coverage Summary

| Category | Count |
|----------|-------|
| Constructor/Init | 2 |
| Properties | 3 |
| can_transition() | 6 |
| transition() | 5 |
| DoR/DoD methods | 6 |
| Edge cases | 4 |
| **Total** | 26 |

---

### TC-01: Constructor with new work item
**Steps**: Create machine for non-existent work item
**Expected**: State created, machine initialized at project-owner

---

### TC-02: Constructor with existing state
**Steps**: Create state, then create machine for same work item
**Expected**: Machine loads existing state, preserves role

---

### TC-03: current_role property
**Steps**: Create machine, read current_role
**Expected**: Returns "project-owner" initially

---

### TC-04: current_phase property
**Steps**: Create machine, read current_phase
**Expected**: Returns "design" initially

---

### TC-05: profile property
**Steps**: Create machine with profile="express", read profile
**Expected**: Returns "express"

---

### TC-06: can_transition() valid next role
**Steps**: At project-owner, call can_transition("program-manager")
**Expected**: Returns (True, "Transition allowed")

---

### TC-07: can_transition() skip role
**Steps**: At project-owner, call can_transition("developer")
**Expected**: Returns (False, "Cannot skip roles...")

---

### TC-08: can_transition() invalid role name
**Steps**: Call can_transition("invalid-role")
**Expected**: Returns (False, "Unknown role: invalid-role")

---

### TC-09: can_transition() backward
**Steps**: At program-manager, call can_transition("project-owner")
**Expected**: Returns (False, "Cannot go backward...")

---

### TC-10: can_transition() to developer without DoR
**Steps**: At architect, DoR incomplete, call can_transition("developer")
**Expected**: Returns (False, "DoR must be complete...")

---

### TC-11: can_transition() to developer with DoR complete
**Steps**: At architect, mark all DoR complete, call can_transition("developer")
**Expected**: Returns (True, "Transition allowed")

---

### TC-12: transition() valid
**Steps**: At project-owner, call transition("program-manager")
**Expected**: Returns (True, "..."), current_role is now program-manager

---

### TC-13: transition() invalid
**Steps**: At project-owner, call transition("developer")
**Expected**: Returns (False, "..."), current_role still project-owner

---

### TC-14: transition() updates roleHistory
**Steps**: Transition from project-owner to program-manager
**Expected**: roleHistory has 2 entries, first has exitedAt set

---

### TC-15: transition() updates phase
**Steps**: Complete DoR, transition to developer
**Expected**: current_phase changes to "development"

---

### TC-16: transition() persists state
**Steps**: Transition, create new machine instance
**Expected**: New instance has updated role

---

### TC-17: check_dor() returns status
**Steps**: Create machine, call check_dor()
**Expected**: Returns dict with all items False

---

### TC-18: check_dod() returns status
**Steps**: Create machine, call check_dod()
**Expected**: Returns dict with all items False

---

### TC-19: mark_dor() sets item
**Steps**: Call mark_dor("userStory", True)
**Expected**: check_dor()["userStory"] is True

---

### TC-20: mark_dod() sets item
**Steps**: Call mark_dod("testsPass", True)
**Expected**: check_dod()["testsPass"] is True

---

### TC-21: mark_dor() persists
**Steps**: Mark item, create new machine instance
**Expected**: Item still marked

---

### TC-22: mark_dor() invalid item
**Steps**: Call mark_dor("invalidItem", True)
**Expected**: Raises ValueError

---

### TC-23: Full workflow traversal
**Steps**: Transition through all roles with DoR/DoD gates
**Expected**: Reaches documentor successfully

---

### TC-24: DoR gate enforcement
**Steps**: Try to reach developer without completing DoR
**Expected**: Blocked at architect?developer transition

---

### TC-25: is_dor_complete() helper
**Steps**: Check with incomplete DoR, complete DoR
**Expected**: Returns False then True

---

### TC-26: is_dod_complete() helper
**Steps**: Check with incomplete DoD, complete DoD
**Expected**: Returns False then True

---

## Traceability Matrix

| AC | Test Cases |
|----|------------|
| AC-1 | TC-01, TC-02 |
| AC-2 | TC-03, TC-04, TC-05 |
| AC-3 | TC-06 to TC-11 |
| AC-4 | TC-12 to TC-16 |
| AC-5 | TC-17 to TC-22 |
| AC-6 | TC-10, TC-11, TC-24 |
| AC-7 | TC-16, TC-21 |

---

## Approval

**Requirements Review**: ? Approved (Architect feedback integrated)
**Test Cases**: ? 26 test cases defined, covering all ACs
