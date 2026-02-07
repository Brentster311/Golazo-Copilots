# GCP-0020: Program Manager Decision Notes

## Role Entry
- **Work Item**: GCP-0020
- **Prior Role**: project-owner-assistant
- **Entry Condition Met**: User Story exists

---

## Decisions Made

### D1: Block vs Warn
**Decision**: Block transitions when notes missing (change from GCP-0019)
**Rationale**: Warning-only proved insufficient - 127 retroactive notes required

### D2: Consent-gated Bypass
**Decision**: Allow `force_without_notes=True` with prior `gcp_consent`
**Rationale**: Maintains flexibility for spikes while requiring explicit acknowledgment

### D3: First Role Exempt
**Decision**: project-owner-assistant doesn't need prior role notes
**Rationale**: It's the first role - there's no prior role to have notes from

### D4: Actionable Errors
**Decision**: Error messages include exact file path to create
**Rationale**: Makes it easy to fix the issue immediately

---

## Output Artifacts Created
- [x] Design doc at `WorkItems/GCP-0020/Design/GCP-0020-design-doc.md`
- [x] This decision notes file

---

## Transition Recommendation
**Ready for**: quality-assurance
