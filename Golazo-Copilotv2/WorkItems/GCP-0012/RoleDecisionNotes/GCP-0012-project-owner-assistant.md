# GCP-0012: Project Owner Assistant Decision Notes

## Role Entry
- **Work Item**: GCP-0012
- **Prior Role**: None (first role)
- **Entry Condition Met**: User reported workflow bug - retrospective role blocked from going backward

---

## Decisions Made

### D1: Scope - Backward Transitions Only
**Decision**: Only enable backward transitions; keep forward skip restrictions  
**Rationale**: The bug is specifically about being stuck at retrospective with no way to go back. Forward skipping is still undesirable (bypasses quality gates).

### D2: Preserve All Progress When Going Backward
**Decision**: DoR/DoD items remain marked when transitioning backward  
**Rationale**: User may be going back to refine, not redo. Clearing progress would be destructive. If they want to unmark items, `gcp_mark_dor/dod` can do that explicitly.

### D3: Allow Backward to ANY Prior Role
**Decision**: No restrictions on how far back you can go  
**Rationale**: Simplicity. If developer realizes program-manager made a mistake, they should be able to jump directly back rather than step-by-step.

### D4: Track in Role History
**Decision**: Backward transitions create new role_history entries  
**Rationale**: Maintains audit trail of workflow movement. Important for retrospectives to see how many times team had to backtrack.

---

## Output Artifacts Created
- [x] User Story at `WorkItems/GCP-0012/GCP-0012-User-Story.md`
- [x] Decision notes (this file)

---

## Transition Recommendation
**Ready for**: program-manager

**Justification**: User story is complete with 4 testable acceptance criteria. All fundamental questions answered. Scope is clear and focused on the bug fix.
