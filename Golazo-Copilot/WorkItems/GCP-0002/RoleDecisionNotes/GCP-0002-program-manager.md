# GCP-0002: Program Manager Decision Notes

## Role Entry
- **Work Item**: GCP-0002 - Role Transitions
- **Prior Role**: Project Owner Assistant
- **Entry Condition Met**: User Story exists ?

---

## Decisions Made

### D1: Hard-Coded Transition Matrix
**Decision**: Implement transitions as hard-coded Python dict, not config-driven

**Alternatives Considered**:
- Config-driven (gcp.yaml): More flexible but adds complexity
- Database lookup: Overkill for simple workflow

**Rationale**: 
- v1 needs to ship quickly
- Config-driven deferred to GCP-0008
- Hard-coded is testable and predictable

---

### D2: DoR Gate Only at Developer
**Decision**: Only gate at `developer` role entry

**Rationale**:
- Definition phase doesn't need gates (building artifacts)
- Development phase requires complete artifacts
- Simplifies implementation

---

### D3: Preserve Progress on Backward Transitions
**Decision**: Never reset DoR/DoD items on backward transition

**Rationale**:
- User may go back to fix one thing
- Shouldn't lose all progress
- Audit trail still tracks the back-and-forth

---

### D4: Phase Tracking via Map
**Decision**: Use PHASE_MAP dict to determine phase from role

**Rationale**:
- Simple lookup
- Easy to test
- Phase derived from role, not stored separately

---

## Tradeoffs Accepted

1. **Flexibility vs Simplicity**: Hard-coded transitions are less flexible but ship faster
2. **Strictness vs Usability**: DoR gate can be overridden with consent (future GCP-0005)

---

## Output Artifacts Created
- [x] `WorkItems/GCP-0002/Design/GCP-0002-design-doc.md`
- [x] `WorkItems/GCP-0002/RoleDecisionNotes/GCP-0002-program-manager.md` (this file)

---

## Transition Recommendation
**Ready for**: Quality Assurance

Design Doc complete. Ready for QA review and Test Cases.
