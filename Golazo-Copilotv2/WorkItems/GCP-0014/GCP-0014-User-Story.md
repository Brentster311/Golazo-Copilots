# GCP-0014: Project Owner Consent Required for Gate Bypass

**Status**: BACKLOG

---

## User Story

- **Title**: Require Project Owner Consent (Not Assistant) for Gate Bypass
- **As a**: Project Owner
- **I want**: The `gcp_consent` tool to require my explicit consent and rationale before bypassing workflow gates
- **So that**: Gate bypasses are properly authorized by me (the human), not the AI assistant, and the reasoning is permanently recorded

---

## Out of Scope
- Multi-level approval chains (e.g., PO + Tech Lead)
- Consent expiration or time-limited approvals
- Consent revocation after recording

---

## Assumptions
- **Assumption (explicit)**: The PO provides consent via chat message, which Copilot then passes to gcp_consent
- **Assumption (explicit)**: Rationale is a free-text string provided by the PO

---

## Acceptance Criteria

- [ ] `gcp_consent` requires a `rationale` parameter (minimum 10 characters) provided by the Project Owner
- [ ] If `gcp_consent` is called without rationale, it returns an error prompting for PO rationale
- [ ] The recorded deviation includes the PO's rationale in the `state.json`
- [ ] `gcp_status` shows recorded deviations with their rationale text
- [ ] The tool description clearly states that consent must come from the Project Owner, not the assistant

---

## Non-Functional Requirements
- Rationale text stored in state.json should be human-readable
- No truncation of rationale (store full text)

---

## Telemetry / Metrics Expected
- Count of consent actions by type (skip_dor, skip_dod, etc.)

---

## Rollout / Rollback Notes
- Breaking change if existing code calls gcp_consent without rationale
- Migration: existing deviations without rationale remain valid (grandfathered)
