# GCP-0020: Architect Decision Notes

## Role Entry
- **Work Item**: GCP-0020
- **Prior Role**: quality-assurance
- **Entry Condition Met**: User Story, Design Doc, Review Comments exist

---

## Decisions Made

### D1: Backward Transition Handling
**Decision**: Always check outgoing role's notes, regardless of transition direction
**Rationale**: Simple, consistent rule - "you must document your role before leaving it"

### D2: Consent Consumption
**Decision**: Force bypass consumes the consent (one-time use)
**Rationale**: Consistent with existing consent behavior from GCP-0005

### D3: Error Response Contract
**Decision**: Failed transitions return `{success: false, error, missing_file, hint}`
**Rationale**: Actionable errors help users fix the issue immediately

### D4: Fail-Safe Behavior
**Decision**: File system errors during check → block transition
**Rationale**: Prefer safety over convenience when errors occur

---

## Architecture Review

- ✅ Reuses existing `get_role_notes_path()` function
- ✅ Reuses consent mechanism from GCP-0005
- ✅ Single file modification (`gcp_transition.py`)
- ✅ No new dependencies
- ✅ No security concerns

---

## Output Artifacts Created
- [x] Architect Notes section added to Review Comments
- [x] This decision notes file

---

## Transition Recommendation
**Ready for**: developer (DoR complete, architecture approved)
