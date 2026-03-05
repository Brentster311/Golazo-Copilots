# GCP-0052 Quality Assurance — Decision Notes

**Work Item:** GCP-0052 — Subagent Handoff Protocol & Integration Testing  
**Role:** Quality Assurance  
**Date:** 2026-02-22

---

## Decisions Made

### D1: Use domain expert's corrected handoff matrix as ground truth
The design doc's handoff matrix conflates direct bridges with accumulated reach-back inputs. The domain expert (§2) identified six discrepancies. The corrected matrix must be used for both the protocol document and test assertions. This ensures tests validate real behavior, not idealized assumptions.

### D2: Target QA role for negative test (TC2)
QA has three Required Outputs (`Review-Comments.md`, `Test-Cases.md`, `quality-assurance.md`), making it ideal for testing granular gate enforcement. Omitting a single output (`Test-Cases.md`) while others exist tests that the error message is specific, not generic.

### D3: Add zero-bridge transition test (TC6)
Three transitions (DE→QA, Refactor→Documenter, Documenter→Builder) have no direct artifact bridge. This is the most surprising aspect of the workflow for new contributors. A dedicated test case verifies that `gcp_role_context` resolves inputs from non-adjacent roles.

### D4: Add ROLE_SUFFIX_MAP test (TC7)
`refactor-expert` → `refactor` suffix mapping and `domain-expert` default fallthrough are implicit behaviors that could silently break. A targeted test makes this contract explicit.

### D5: Document POA closure as known gap, do not test nonexistent behavior
POA has `inputs: []` — there is no front-matter mechanism for retrospective → POA closure context injection. Rather than writing a test against undefined behavior, the protocol document should document this as a known limitation. A follow-up work item can address it if needed.

### D6: Use real package default role files in tests
Tests should copy role files from `golazo_copilot/roles/defaults/` into `tmp_path/.github/roles/` rather than using inline stubs. This makes TC1 authoritative — if front-matter changes, tests catch the drift immediately.

### D7: Backward transition test (TC3) must verify artifact freshness
TC3 doesn't just verify backward transition succeeds — it must verify that after architect updates `Review-Comments.md` on re-entry, developer's `gcp_role_context` returns the updated content. This confirms no stale caching.

---

## Risks Flagged

| Risk | Severity | Mitigation |
|---|---|---|
| Handoff matrix in protocol doc diverges from actual front-matter over time | High | Integration test TC1 uses real role files; drift is caught on every test run |
| POA closure re-entry has no formal input contract | Medium | Documented as known gap in Review Comments and protocol doc |
| Review-Comments append pattern could lead to overwrites | Medium | TC1 Step 5 and TC3 verify content from both QA and Architect persists |
| `domain-expert` implicit ROLE_SUFFIX_MAP fallthrough | Low | TC7 explicitly tests the default behavior |

---

## Files Reviewed
- `WorkItems/GCP-0052/GCP-0052-User-Story.md` — acceptance criteria reference
- `WorkItems/GCP-0052/Design/GCP-0052-design-doc.md` — design under review
- `WorkItems/GCP-0052/RoleDecisionNotes/GCP-0052-domain-expert.md` — corrected matrix and edge cases
- `golazo-copilot/tests/test_output_integration.py` — existing integration test patterns
- `golazo-copilot/tests/test_gcp_role_context.py` — role context test patterns
- `golazo-copilot/tests/test_gcp_transition.py` — transition and backward transition test patterns
- `golazo-copilot/src/golazo_copilot/tools/gcp_transition.py` — ROLE_SUFFIX_MAP source

---

## Summary
Design approved with corrections. Seven test cases defined (TC1–TC7) covering all six acceptance criteria plus two edge cases from the domain expert review. The corrected handoff matrix, zero-bridge transitions, and ROLE_SUFFIX_MAP mapping are the most critical items for the developer to get right. POA closure re-entry is documented as a known gap.
