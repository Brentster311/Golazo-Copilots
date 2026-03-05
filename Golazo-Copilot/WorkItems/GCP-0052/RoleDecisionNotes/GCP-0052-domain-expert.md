# GCP-0052 Domain Expert — Decision Notes

**Work Item:** GCP-0052 — Subagent Handoff Protocol & Integration Testing  
**Role:** Domain Expert  
**Date:** 2026-02-22

---

## Domain Expertise Required

**Domain:** Golazo Copilot workflow methodology — artifact flow, role sequencing, gate enforcement, and MCP tool integration.

This work item is the capstone of the subagent initiative (GCP-0048 through GCP-0052). Domain expertise is critical because the handoff protocol document and integration tests must faithfully represent the actual role file contracts, not an idealized version.

---

## 1. Artifact Flow Analysis — Actual Front-Matter Inventory

The following is the authoritative `inputs:` / `outputs:` extracted from all 10 role default files in `golazo-copilot/src/golazo_copilot/roles/defaults/`.

| # | Role | inputs (from front-matter) | outputs (from front-matter) |
|---|---|---|---|
| 1 | project-owner-assistant | *(none)* | `{id}-User-Story.md`, `RDN/{id}-project-owner-assistant.md` |
| 2 | program-manager | `{id}-User-Story.md` | `Design/{id}-design-doc.md`, `RDN/{id}-program-manager.md` |
| 3 | domain-expert | `{id}-User-Story.md`, `Design/{id}-design-doc.md` | `RDN/{id}-domain-expert.md` |
| 4 | quality-assurance | `{id}-User-Story.md`, `Design/{id}-design-doc.md` | `Design/{id}-Review-Comments.md`, `Design/{id}-Test-Cases.md`, `RDN/{id}-quality-assurance.md` |
| 5 | architect | `{id}-User-Story.md`, `Design/{id}-design-doc.md`, `Design/{id}-Review-Comments.md` | `Design/{id}-Review-Comments.md`, `Design/{id}-Capability-Impact.md`, `RDN/{id}-architect.md` |
| 6 | developer | `{id}-User-Story.md`, `Design/{id}-design-doc.md`, `Design/{id}-Review-Comments.md`, `Design/{id}-Test-Cases.md` | `RDN/{id}-developer.md` |
| 7 | refactor-expert | `RDN/{id}-developer.md` | `RDN/{id}-refactor.md` |
| 8 | documenter | `{id}-User-Story.md`, `Design/{id}-design-doc.md` | `RDN/{id}-documenter.md` |
| 9 | builder | `{id}-User-Story.md` | `RDN/{id}-builder.md` |
| 10 | retrospective | All 9 prior RDN files | `RDN/{id}-retrospective.md` |

*(RDN = `WorkItems/{id}/RoleDecisionNotes/`)*

---

## 2. Design Doc Handoff Matrix — Accuracy Review

The design doc proposes a handoff matrix framed as "bridging artifacts (outputs of From ∩ inputs of To)." Cross-referencing against actual front-matter reveals **six discrepancies** where the matrix conflates accumulated artifacts with direct bridging artifacts.

### Corrected Matrix

| # | From → To | Direct Bridge (From outputs ∩ To inputs) | Accumulated Reach-Back (To reads from earlier roles) | Design Doc Accurate? |
|---|---|---|---|---|
| 1 | POA → PM | `{id}-User-Story.md` | — | **YES** |
| 2 | PM → DE | `Design/{id}-design-doc.md` | `{id}-User-Story.md` (from POA) | **PARTIAL** — design doc lists User-Story as a bridge, but PM doesn't output it; DE reaches back to POA |
| 3 | DE → QA | *(none)* | `{id}-User-Story.md` (POA), `Design/{id}-design-doc.md` (PM) | **NO** — design doc lists User-Story + design-doc, but DE outputs only its decision notes. QA reaches back to POA & PM |
| 4 | QA → Architect | `Design/{id}-Review-Comments.md` | `{id}-User-Story.md` (POA), `Design/{id}-design-doc.md` (PM) | **PARTIAL** — design doc lists all 3, but only Review-Comments is a direct QA→Architect bridge |
| 5 | Architect → Dev | `Design/{id}-Review-Comments.md` | `{id}-User-Story.md` (POA), `Design/{id}-design-doc.md` (PM), `Design/{id}-Test-Cases.md` (QA) | **PARTIAL** — design doc lists all 4, but only Review-Comments bridges from Architect. Test-Cases skips Architect entirely (QA→Dev) |
| 6 | Dev → Refactor | `RDN/{id}-developer.md` | — | **YES** |
| 7 | Refactor → Documenter | *(none)* | `{id}-User-Story.md` (POA), `Design/{id}-design-doc.md` (PM) | **NO** — design doc lists User-Story + design-doc, but Refactor outputs only its decision notes. Documenter reaches back to POA & PM |
| 8 | Documenter → Builder | *(none)* | `{id}-User-Story.md` (POA) | **NO** — design doc lists User-Story, but Documenter doesn't output it. Builder reaches back to POA |
| 9 | Builder → Retro | `RDN/{id}-builder.md` | 8 other RDN files (from roles 1–8) | **PARTIAL** — design doc says "All 9 prior role notes" which is correct for Retro inputs, but only builder-notes is a direct bridge from Builder |
| 10 | Retro → POA (closure) | *(none — POA has `inputs: []`)* | — | **NO** — design doc lists `{id}-retrospective.md` as bridging, but POA has no formal inputs. Closure re-entry is not modeled in front-matter |

### Summary of Discrepancies

1. **Transitions 3, 7, 8 have NO direct bridging artifacts** — the successor role reaches back to earlier roles, not to its immediate predecessor. The design doc should distinguish "direct handoff" from "accumulated context."
2. **Transitions 2, 4, 5, 9 overstate the bridge** — they include accumulated artifacts alongside direct bridges.
3. **Transition 10 (Retro → POA closure) is unmodeled** — POA's front-matter `inputs: []` doesn't account for the closure path.

**Recommendation:** The handoff protocol document should present TWO views: (a) the direct bridge per transition, and (b) the full input set per role (showing reach-back). This avoids the confusion of mixing the two.

---

## 3. Edge Cases in Artifact Flow

### 3.1 Roles That Don't Consume Their Predecessor's Outputs

- **domain-expert → quality-assurance:** QA does not consume domain-expert's decision notes. Domain-expert produces only `RDN/{id}-domain-expert.md`, but QA's inputs are `{id}-User-Story.md` and `Design/{id}-design-doc.md`. Domain-expert guidance may optionally be appended to `Design/{id}-Review-Comments.md` (see domain-expert role body text), but this is NOT in the formal `outputs:` front-matter.
- **refactor-expert → documenter:** Documenter does not read refactor notes. It reads User-Story and design-doc from earlier roles.
- **documenter → builder:** Builder does not read documenter notes. It reads only User-Story.

**Impact on tests:** The integration test TC1 should verify that `gcp_role_context` correctly assembles context from non-adjacent roles, not just the immediate predecessor. The test should assert that documenter receives User-Story (from POA, role 1) even though it transitions from refactor-expert (role 7).

### 3.2 Shared/Appended Artifacts

- **`Design/{id}-Review-Comments.md`** is produced by both QA (role 4) and Architect (role 5). Architect lists it in both `inputs:` and `outputs:`. This is an append pattern — Architect adds an "Architect Notes" section to the QA-created file. The integration test should:
  - Create Review-Comments with QA content, transition to Architect
  - Verify Architect can read the QA version
  - Have "Architect" append to it, transition to Developer
  - Verify Developer sees the combined content

### 3.3 Optional/Informational Outputs

- **`Design/{id}-Capability-Impact.md`** is produced by Architect but appears in NO subsequent role's `inputs:`. It's a pure documentation artifact not consumed by any downstream gate. The integration test should verify it doesn't block subsequent transitions even if missing from the "consumed" perspective — but it IS a Required Output for Architect, so `gcp_transition` will still enforce it.

### 3.4 Refactor-Expert Narrow Scope

- Refactor-expert has the narrowest input set of any role: just `RDN/{id}-developer.md`. It doesn't read the User-Story, design-doc, test-cases, or review-comments. This is deliberate — refactoring should be behavior-preserving, so the refactor subagent only needs to know what the developer did. The test should verify that `gcp_role_context` does NOT return design artifacts for refactor-expert.

### 3.5 POA Closure Re-Entry

- POA has `inputs: []` — the front-matter has no mechanism to inject the retrospective notes into the closure context. This is a **gap** in the current role file definitions. The orchestration spine (GCP-0050) presumably handles closure as a special case outside front-matter, or `gcp_role_context` has custom logic for it.
- **Recommendation for test:** TC3 (backward transition) covers this partially, but the handoff protocol should explicitly document that POA closure is a special orchestrator-level concern, not modeled in front-matter. The integration test should verify what `gcp_role_context` actually returns when POA is re-entered after retrospective.

### 3.6 Domain-Expert Optional Review-Comments Contribution

- The domain-expert role body text says: "Create or append to `{id}-Review-Comments.md`" under the "Consultation Output" section. However, `Design/{id}-Review-Comments.md` is NOT in domain-expert's `outputs:` front-matter. This means:
  - `gcp_transition` will NOT enforce that domain-expert creates Review-Comments
  - If domain-expert does create it, QA and Architect will find it, but the gate system doesn't require it
  - This is an **intentional optionality** — some work items need no domain guidance, so Review-Comments is not always created by domain-expert
- **Recommendation:** The handoff protocol should document this optional artifact pattern explicitly.

---

## 4. Recommendations for Integration Test Design

### 4.1 Test the Reach-Back Pattern, Not Just Direct Handoffs

The most important insight is that the Golazo workflow is NOT a simple linear chain where each role passes artifacts to the next. It's a **write-once, read-many** pattern where artifacts persist and later roles reach back to earlier outputs. The integration test must verify that `gcp_role_context` correctly resolves inputs from non-adjacent predecessors (e.g., documenter reading User-Story from POA).

### 4.2 Verify the Empty-Bridge Transitions

Three transitions (DE→QA, Refactor→Documenter, Documenter→Builder) have no direct artifact bridge. The test should confirm that these transitions succeed via `gcp_transition` (the predecessor's decision notes are the only Required Output enforced) and that the successor's `gcp_role_context` correctly sources its inputs from earlier roles.

### 4.3 Test Review-Comments Append Semantics

The integration test should create Review-Comments during QA, then verify that Architect receives the QA version as input and can append to it. This is the only artifact in the workflow that is both input and output for the same role.

### 4.4 Test Capability-Impact as Non-Consumed Required Output

Verify that Architect is blocked by `gcp_transition` if `Capability-Impact.md` is missing, even though no downstream role consumes it. This validates that Required Outputs are enforced for the producing role regardless of downstream consumption.

### 4.5 Handle the ROLE_SUFFIX_MAP Correctly

The `refactor-expert` role outputs to `{id}-refactor.md` (not `{id}-refactor-expert.md`). The retrospective role reads `{id}-refactor.md`. The test must use the correct suffix mapping; the design doc correctly notes this.

### 4.6 POA Closure Path

If the test walks the full POA→...→Retro→POA(closure) cycle, it should document whether `gcp_role_context` returns anything for POA re-entry (given `inputs: []`), or whether the orchestrator passes context via a different mechanism. This may surface a gap that warrants a follow-up work item.

### 4.7 Negative Test — Pick a Mid-Workflow Transition

TC2 (missing output blocks transition) should target a role with multiple Required Outputs (e.g., QA, which requires Review-Comments, Test-Cases, and QA-notes). Omitting just one and verifying the exact error message tests the granularity of gate enforcement.

### 4.8 Backward Transition — Verify Context Freshness

TC3 should modify at least one artifact after the backward transition (e.g., Architect updates Review-Comments after returning from Developer) and verify that Developer's `gcp_role_context` on re-entry sees the updated file, not a stale cached version.

---

## 5. Assumptions Made

1. **Assumption:** The design doc's handoff matrix is intended to show the full input set available to each role, not strictly the direct bridge from the predecessor. The domain review treats this as an imprecise framing rather than an error.
2. **Assumption:** `gcp_role_context` resolves inputs by checking file existence on disk regardless of which role originally produced the file — i.e., it doesn't track provenance, just path patterns.
3. **Assumption:** The POA closure re-entry is handled by orchestrator-level logic (possibly in the bootstrap spine) rather than by POA's front-matter inputs.
4. **Assumption:** The optional Review-Comments contribution by domain-expert is working as designed (intentionally not gate-enforced).
5. **Assumption:** The `ROLE_SUFFIX_MAP` used by `gcp_transition` correctly maps `refactor-expert` → `refactor` for the output file suffix.

---

## 6. Risks Identified

| Risk | Severity | Mitigation |
|---|---|---|
| Handoff matrix mismatch leads to incorrect test assertions | High | Use the corrected matrix from §2 as the test's ground truth |
| POA closure re-entry is untested because front-matter doesn't model it | Medium | Document as known gap; add defensive test that logs what `gcp_role_context` returns for POA re-entry |
| Review-Comments append pattern causes overwrites instead of appends | Medium | Integration test should assert content from both QA and Architect sections exists after Architect role |
| Capability-Impact.md gate test may be fragile if output validation changes | Low | Keep the test isolated (TC dedicated to Architect outputs) |
| Domain-expert optional Review-Comments creates ghost artifact | Low | Test both paths: domain-expert with and without Review-Comments creation |

---

## 7. Conclusion

The design doc's approach is sound, but the proposed handoff matrix conflates direct bridges with accumulated context. The corrected matrix in §2 should be used as the authoritative reference for both the protocol document and the integration tests. The six discrepancies and five edge cases identified above should be addressed in the developer implementation to ensure the protocol and tests are accurate.

No domain analysis reveals a fundamental design flaw. The work item is ready to proceed to Quality Assurance.
