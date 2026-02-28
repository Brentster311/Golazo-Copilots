# GCP-0035: Rewrite README for Output Validation Architecture

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Rewrite README to Reflect Current Architecture
- **As a**: Developer installing or evaluating Golazo Copilot
- **I want**: The README to accurately describe the current feature set and workflow
- **So that**: I can understand how GCP works without encountering obsolete instructions

---

## Out of Scope
- Changing any production code or tests
- Adding new features
- Rewriting role files or copilot-instructions.md
- Restructuring the golazo-copilot package

---

## Assumptions
- **Assumption (explicit)**: The README is the primary onboarding document for new users
- **Assumption (explicit)**: All correctness issues identified in the review must be fixed (not just updated, but rewritten to reflect the output validation model)
- **Assumption (explicit)**: The README structure (Features → Installation → Configuration → Usage → Troubleshooting) remains the same

---

## Acceptance Criteria

- [ ] **Evidence-Based Validation section removed** — No references to `gcp_mark_dor`, `gcp_mark_dod`, or evidence parameters remain
- [ ] **DoR/DoD sections replaced** — The "DoR Gates" and "DoD Tracking" sections are replaced with a "Role-Based Output Validation" section explaining `## Required Outputs` in role files
- [ ] **Tools table corrected** — Lists only the 5 actual tools: `gcp_create_workitem`, `gcp_status`, `gcp_transition`, `gcp_consent`, `gcp_bootstrap`
- [ ] **Workflow Profiles updated** — Profile descriptions reference role subsets and output validation, not DoR/DoD items
- [ ] **New features documented** — Version sync warning (GCP-0032), role progress display (GCP-0033), TechBestPractices.md (GCP-0028), Required Outputs format (GCP-0026)
- [ ] **Example session corrected** — Shows the actual current workflow (create → status → transition through roles) without referencing mark_dor/mark_dod

---

## Non-Functional Requirements
- README should be scannable — use tables and code blocks appropriately
- Installation instructions must remain accurate (Azure Artifacts feed URL unchanged)
- Troubleshooting section should be preserved and updated if needed

---

## Telemetry / Metrics Expected
- None (documentation only)

## Closure

### Summary of delivery
- Backfilled during closure reconciliation for an already implemented work item.

### Final status confirmation
- Work item `GCP-0035` is IMPLEMENTED and workflow artifacts are complete.
