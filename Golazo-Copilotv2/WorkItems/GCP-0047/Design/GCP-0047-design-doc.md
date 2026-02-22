# GCP-0047 Design Doc

## Summary

Improve 8 of 10 role files in the Golazo Copilot workflow to fix logical ordering errors, reduce review redundancies, add missing governance sections, introduce a POA closure transition, and add security review to Architect. Also requires transitions.py, server.py, and copilot-instructions changes for the new retrospective → project-owner-assistant transition.

## Problem Statement

Analysis of the 10-role workflow revealed:
1. **Documenter checks build before Builder runs** — logical impossibility
2. **Builder's branch creation is unreachable** — Builder runs after Documenter, not before Developer
3. **No closure gate** — work items end at Retrospective with no AC validation or final commit
4. **QA and Architect overlap** — both review design for risk, operability, scalability
5. **Domain Expert and Architect overlap** — both cover API design, architecture patterns
6. **Capability registry in 6 roles** — QA and Domain Expert run the same checks as Architect
7. **PM has no governance sections** — the only role missing Decision/Escalation/Success criteria
8. **No security review** — scattered mentions but no structured checklist
9. **No explicit Domain Expert ↔ Architect boundary** — unclear who owns what

## Business Case

**Why now:** These issues cause friction in every work item execution. The Documenter/Builder ordering bug and unreachable Builder branch creation are logical errors that produce inconsistent behavior. The QA/Architect overlap generates redundant review comments. Missing PM governance means design docs vary wildly in quality.

**Impact:** Every future work item benefits from cleaner role definitions.

**KPIs:** Reduced backward transitions caused by role confusion; consistent artifact structure across work items.

## Stakeholders

- Golazo Copilot users (primary — cleaner workflow experience)
- LLM agents executing roles (clearer instructions = better outputs)

## Functional Requirements

### F1: Documenter — Remove build check
- Remove "Verify build passes" from First Action
- Remove "Build passes" from Entry Conditions
- Update First Action to verify implementation is complete and tests pass

### F2: Developer — Add branch creation
- Add branch creation to Developer First Action: check if feature branch `<workitem-id>` exists; if not, create it
- Remove "Before Developer role" branch creation section from Builder

### F3: POA Closure Transition
- Add forward transition: retrospective → project-owner-assistant in `transitions.py` TRANSITIONS dict
- Add "project-owner-assistant" to server.py transition enum (already present but verify)
- Add "Closure" section to POA role file with:
  - Final git commit + push
  - Validate each AC in User Story against implementation (mark as checked/failed)
  - Collect all "new User Story" / "new work item" proposals from all role decision notes
  - Present collected proposals to PO for disposition (create, defer, or discard)
  - Update User Story status to IMPLEMENTED (move from Documenter)
- Update copilot-instructions.md valid roles list to show POA at both position 1 and as closure role
- Update ROLE_ORDER comment or documentation (POA position stays at index 0)

### F4: Sharpen QA → Testability Focus
- Remove from QA Design Review: risk coverage, operability/on-call impact, cost/performance tradeoffs, naming clarity, folder/directory structure
- Keep in QA: clarity/completeness (of requirements, not design), feasibility/sequencing (as it relates to test ordering), edge cases/failure modes
- Move removed bullets to Architect with attribution

### F5: PM Governance Sections
Add to program-manager.md:
- **Decision rules:** When to push back on scope, how to handle conflicting requirements, when alternatives should be elevated
- **Escalation rules:** Scope too large → return to POA; unresolvable dependencies → new User Story
- **Success criteria:** Design doc is reviewable, approach is feasible/staged/measurable

### F6: Domain Expert ↔ Architect Boundary
- Domain Expert: Add boundary statement — provides domain-specific knowledge (Cosmos DB partition design, ML model selection, etc.), NOT structural/architectural decisions
- Architect: Add boundary statement — owns structural decisions; defers to Domain Expert guidance in Review Comments for domain-specific knowledge

### F7: Capability Registry Consolidation
- Remove `gcp_capabilities` instructions from: Domain Expert, QA
- Keep in: Architect (impact — REQUIRED), Developer (pre-commit), Refactor Expert (post-refactor), Builder (validate), Retrospective (process audit)

### F8: Security Review in Architect
Add "Security Review" subsection to Architect with mandatory checklist:
- Data exposure analysis
- Auth boundary changes
- Attack surface assessment (new endpoints, input validation)
- Compliance implications (PII, cross-tenant, regulatory)
- Document in Capability-Impact.md under "Security Assessment" heading

## Non-Functional Requirements

- All role files maintain consistent markdown structure
- Changes applied to all 3 copies (source defaults, `.github/roles/`, `golazo-copilot/.github/roles/`)
- Existing tests must continue to pass after transitions.py changes

## Proposed Approach

### Phase 1: Role File Changes (F1, F2, F4, F5, F6, F7, F8)
Edit 8 role markdown files × 3 copies = up to 24 file edits:
- `documenter.md` — remove build check (F1)
- `developer.md` — add branch creation (F2)
- `builder.md` — remove branch creation section (F2)
- `quality-assurance.md` — remove design-quality bullets (F4)
- `architect.md` — add design-quality bullets + security review + boundary (F4, F6, F8)
- `program-manager.md` — add governance sections (F5)
- `domain-expert.md` — add boundary + remove capability registry (F6, F7)
- `project-owner-assistant.md` — add Closure section (F3)

### Phase 2: Transition Engine Changes (F3)
- `transitions.py`: Add "project-owner-assistant" to retrospective's forward transitions list
- `server.py`: Verify "project-owner-assistant" is in the transition role enum
- `copilot-instructions.md` (3 copies) + `bootstrap-instructions.md`: Update role list documentation

### Phase 3: Test Updates (F3)
- Update existing tests that reference role counts or transition expectations
- Add new tests for retrospective → project-owner-assistant transition

## Alternatives Considered

| Alternative | Decision | Rationale |
|-------------|----------|-----------|
| Add Security Reviewer role | Rejected | PO chose option A (expand Architect) to avoid adding an 11th role |
| POA closure as Retrospective expansion | Rejected by PO | PO explicitly wants a real transition back to POA |
| Remove all capability checks except Architect+Builder | Rejected by PO | Developer and Refactor Expert keep their checks |
| Eliminate copy #3 (`golazo-copilot/.github/roles/`) | Deferred | Separate concern, not in scope |

## Risks, Mitigations, Open Questions

| Risk | Severity | Mitigation |
|------|----------|------------|
| Retrospective → POA transition creates unexpected loops | Medium | POA Closure has no forward transition — it's a terminal state. Validate in tests. |
| QA sharpening removes too much | Low | QA keeps edge cases, failure modes, test strategy. Design-quality concerns explicitly move to Architect. |
| 24 file edits across 3 copies drift | Low | Developer verifies all 3 copies match after edits |

**Open question:** Should POA Closure have its own required output (e.g., `{id}-closure.md`) or reuse the existing POA notes file? Recommending a new output: `WorkItems/{id}/RoleDecisionNotes/{id}-closure.md`.

## Dependencies

- GCP-0046 (domain-expert role) must be complete — ✅ Done
- transitions.py architecture supports multiple forward transitions per role — ✅ Already the pattern (lists of targets)

## Rollout / Rollback Plan

- **Rollout:** Bump version, rebuild, deploy to Azure Artifacts, install. New workspaces get updated roles via bootstrap. Existing workspaces need re-bootstrap or manual file copy.
- **Rollback:** Revert commits, rebuild with previous version, redeploy.

## Observability Plan

N/A — role files are static markdown. The transitions.py change is observable via test results.

## Test Strategy Summary

1. **Transition tests:** New test for retrospective → project-owner-assistant (forward, valid)
2. **Regression tests:** Existing transition tests still pass (role counts, sequences)
3. **Role file tests:** Verify all role files exist in all 3 locations
4. **Best practices test:** If a test exists for role file structure consistency, verify PM now passes
