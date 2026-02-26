# SFI-041 Program Manager Notes

## Scope Decision
Focused on a single vertical slice: Action Owner editing and persistence for one action item from the Windows details dialog experience.

## Why This Scope
- Directly maps to the user story’s GUI-only objective for non-technical users.
- Reuses existing `accia_s360` persistence contract (`save_action_owners`) instead of introducing new backend pathways.
- Minimizes delivery risk by avoiding ETA or broader field-editing expansion.

## API Persistence Path Decision
Adopt explicit layered path:
- Dialog interaction in SFIReporter details UI.
- SFIReporter data/client seam via `get_client()`.
- `S360Client.save_action_owners(...)` in `accia_s360`.
- S360 endpoint `/ActionItems/SaveActionOwnersByIds`.

This preserves existing auth and request handling behavior.

## Error Handling Decision (Windows GUI)
Failure handling is mandatory and user-visible:
- On failure, show clear GUI error and do not show success.
- Keep previous owner shown until confirmed success.
- Categorize/log failures for operational follow-up.

## Acceptance Criteria Mapping
- AC1: Details dialog has clear Action Owner control.
- AC2: Save calls S360 through `save_action_owners` and succeeds when API returns success.
- AC3: Reopen/refresh reflects updated owner.
- AC4: Failure path shows user-friendly error and no false success.
- AC5: Entire flow remains GUI-only.

## Constraints & Assumptions
- Windows-only support for this story.
- Required item identifiers are present in detailed item context.
- No auth model changes; existing token flow remains intact.
- Owner input mechanism should be the simplest control that can reliably produce alias + display name.

## Delivery Readiness
Design doc includes sequencing, risks/mitigations, observability, rollout/rollback, and test strategy sufficient for architect and developer execution without scope expansion.
