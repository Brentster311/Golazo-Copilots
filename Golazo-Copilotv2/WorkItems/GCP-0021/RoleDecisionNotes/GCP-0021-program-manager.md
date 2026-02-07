# GCP-0021: Program Manager Notes

## Design Decisions

### Approach
Simple role file update - no new tools or blocking logic needed. The rationale requirement is enforced through existing role notes blocking (GCP-0020).

### Placement in Role File
Adding new section after "Responsibilities" and before "Forbidden actions" - this puts the checklist where it will be read during active refactoring.

### Conciseness
Kept principles table to 2 columns (Principle, Look For) to ensure it's scannable. Full rationale framework documented separately.

## Open Questions Resolved
- Q: Should we validate rationale format programmatically?
- A: No - GCP-0020's role notes blocking is sufficient. Content validation is manual.

## Dependencies
None - standalone documentation change.
