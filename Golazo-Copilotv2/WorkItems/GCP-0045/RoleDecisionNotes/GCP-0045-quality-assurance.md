# GCP-0045 — Quality Assurance Decision Notes

## Work Item
**GCP-0045**: Add Golazo Workflow Trigger Phrase Recognition to Copilot Instructions

## Review Outcome
**Approved with 2 minor recommendations** incorporated into the design.

## Decisions

### 1. Manual Testing Only
**Decision**: All test cases are manual acceptance tests — no automated tests.
**Rationale**: The system under test is AI behavior driven by a markdown instruction file. There is no programmatic interface to assert against. Manual testing in fresh chat sessions is the only valid verification method.

### 2. Edge Case: Existing Work-Item IDs
**Decision**: Recommended adding a rule that if the user provides a work-item ID that already exists, the AI should call `gcp_status` instead of `gcp_create_workitem`.
**Rationale**: Prevents confusing error messages from duplicate creation attempts. This is a low-effort addition to the instruction section.

### 3. No-ID Behavior
**Decision**: When "new workitem" is said without an ID, the AI should ask for the ID rather than auto-deriving it.
**Rationale**: Users typically have a specific ID convention in mind. Auto-deriving risks mismatches.

## Capability Impact
No capabilities affected — this change is to the copilot-instructions.md file only, not to any source code.
