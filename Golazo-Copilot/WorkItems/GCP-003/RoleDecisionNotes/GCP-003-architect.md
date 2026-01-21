# GCP-003: Architect Decision Document

## Work Item
GCP-003 — Enforce TDD and Builder Git Operations

## Decisions Made
- Git commands are standard and cross-platform
- Builder role becomes the "git gatekeeper" for the workflow
- No structural changes to workflow state machine, just clarification

## Tradeoffs Accepted
- Git errors must be handled gracefully (print message, don't crash)
