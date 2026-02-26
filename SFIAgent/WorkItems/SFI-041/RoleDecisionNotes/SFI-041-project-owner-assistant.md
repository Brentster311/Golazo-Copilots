# SFI-041 Project Owner Assistant Decision Notes

## Scope Decision
- Defined one user-observable outcome: non-technical users can update and persist Action Owner from the SFIReporter details dialog.
- Kept story as a single vertical slice (GUI input + save action + persisted result verification + failure feedback).
- Avoided decomposition because all requested behavior supports one cohesive interaction in the same UI surface.

## Confirmed User Decisions (explicit)
- Interface type: GUI details dialog in SFIReporter.
- Target platform: Windows only.
- Data persistence: Yes — persist by setting Action Owner via an API in the s360 package.
- Primary user type: non-technical users.

## Assumptions (explicit)
- The existing s360 auth/session model can be reused for Action Owner write operations.
- A stable action-item identifier is available from the details dialog context for API updates.
- The Action Owner control can use existing SFIReporter interaction conventions to minimize user training.

## Acceptance Criteria Rationale
- Criteria are constrained to five testable checks covering:
  1) Action Owner control is visible in details dialog,
  2) Successful save path persists through s360 API,
  3) Persisted value is observable after refresh/reopen,
  4) Failure handling is user-friendly and accurate,
  5) End-to-end flow remains GUI-only for non-technical users.

## Risks / Dependencies
- Dependency: s360 package must provide a reliable Action Owner write endpoint/operation.
- Dependency: Reporter details dialog and data refresh path must surface persisted values consistently.
- Risk: API validation or authorization constraints may reject some owner values; explicit UX error handling is required.
