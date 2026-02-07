# GCP-0020: Project Owner Assistant Decision Notes

## Role Entry
- **Work Item**: GCP-0020
- **Prior Role**: None (new work item)
- **Entry Condition Met**: New work item creation

---

## Request Analysis

The user needs blocking enforcement for role notes after GCP-0019's warning-only approach proved insufficient. Evidence:
- 16 work items had missing notes despite warnings
- 127 notes created retroactively
- AI assistants acknowledge warnings but don't change behavior

## Scope Decisions

1. **Block instead of warn** - Core change from GCP-0019
2. **Consent-gated bypass** - Allow force with prior gcp_consent
3. **First role exempt** - project-owner-assistant has no prior role
4. **Actionable errors** - Include exact file path in error message

## Assumptions Made

- Blocking can be bypassed with consent (flexibility preserved)
- Breaking change is acceptable (warning-only didn't work)
- Same file naming convention as GCP-0019

## Output Artifacts

- [x] GCP-0020-User-Story.md created
- [x] This decision notes file

## Transition Recommendation

**Ready for**: program-manager (design phase)
