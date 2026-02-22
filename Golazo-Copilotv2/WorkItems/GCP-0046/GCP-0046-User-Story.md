# GCP-0046 User Story

**Status**: IMPLEMENTED

## User Story

- **Title:** Add Domain Expert Role to the Definition Phase
- **As a:** Golazo Copilot user
- **I want:** A new "domain-expert" role inserted into the workflow between Program Manager and Quality Assurance that evaluates whether domain expertise is needed and contributes guidance to the shared Review Comments artifact
- **So that:** Work items involving specialized domains (Azure platform services, AI/ML, distributed systems, etc.) receive targeted expert guidance before design review and implementation, reducing late-stage rework caused by missed domain-specific concerns

- **Out of scope:**
  - Adding domain-expert guidance to the Developer or Refactor Expert roles
  - Creating a separate artifact for domain expert feedback (they write to the existing Review Comments file)
  - Automated detection of domain triggers (the role file provides a checklist; the LLM evaluates)
  - Multi-expert parallel consultation orchestration (the role file advises it; the MCP server doesn't enforce it)

- **Assumptions:**
  - **Assumption (explicit):** The new role is named `domain-expert` and is placed at position 3 in ROLE_ORDER (after `program-manager`, before `quality-assurance`)
  - **Assumption (explicit):** The domain-expert role is in the "definition" phase
  - **Assumption (explicit):** Domain experts write their guidance into the same `{id}-Review-Comments.md` artifact that Quality Assurance and Architect use — no new artifact type is created
  - **Assumption (explicit):** The domain-expert role file itself is the primary deliverable — the LLM reads the triggers/checklist and decides which domain experts to simulate
  - **Assumption (explicit):** Forward transition from program-manager goes to domain-expert; forward transition from domain-expert goes to quality-assurance
  - **Assumption (explicit):** Backward transition from domain-expert goes to program-manager; backward from quality-assurance now goes to domain-expert (not directly to program-manager)

- **Acceptance Criteria (bulleted, testable):**
  - [x] AC1: A `domain-expert.md` role file exists at `golazo-copilot/src/golazo_copilot/roles/defaults/domain-expert.md` containing: domain expert identification process, trigger categories (Engineering & AI, Azure Platform, Application & Solution, Integration & Architecture), consultation rules, and required outputs
  - [x] AC2: `TRANSITIONS` dict in `transitions.py` includes `domain-expert` with forward target `quality-assurance` and backward target `program-manager`; `program-manager` forward target updated to `domain-expert`; `quality-assurance` backward target updated to `domain-expert`
  - [x] AC3: `ROLE_ORDER` list includes `domain-expert` at index 2 (between `program-manager` and `quality-assurance`); `PHASE_MAP` maps `domain-expert` to `"definition"`
  - [x] AC4: The domain-expert Required Outputs include `WorkItems/{id}/RoleDecisionNotes/{id}-domain-expert.md` (role decision notes documenting which domain experts were consulted and their guidance)
  - [x] AC5: All existing tests pass and new tests cover the domain-expert transitions (forward, backward, skip-prevention)

- **Non-functional requirements:**
  - The role file must follow the same markdown structure as existing roles (Purpose, First action, Entry conditions, Responsibilities, Forbidden actions, Required Outputs, Decision rules, Escalation rules, Success criteria)
  - Role file should be deployable to `.github/roles/` and `golazo-copilot/.github/roles/` (3-copy pattern)

- **Telemetry / metrics expected:** None (role files are static markdown)

- **Rollout / rollback notes:**
  - Rollout: Bump version, rebuild package, deploy to Azure Artifacts. Bootstrap new workspaces to get the role file. Existing workspaces need manual copy of the new role file to `.github/roles/`.
  - Rollback: Revert the 3 role file copies, revert `transitions.py`, revert tests, rebuild and redeploy.

## Technical Context

### Current Role Sequence (9 roles)
```
project-owner-assistant → program-manager → quality-assurance → architect → developer → refactor-expert → documenter → builder → retrospective
```

### Proposed Role Sequence (10 roles)
```
project-owner-assistant → program-manager → domain-expert → quality-assurance → architect → developer → refactor-expert → documenter → builder → retrospective
```

### Files to Modify
1. `golazo-copilot/src/golazo_copilot/core/transitions.py` — Add `domain-expert` to `TRANSITIONS`, `PHASE_MAP`, `ROLE_ORDER`
2. `golazo-copilot/src/golazo_copilot/roles/defaults/domain-expert.md` — New role file (source default)
3. `.github/roles/domain-expert.md` — Deployed copy
4. `golazo-copilot/.github/roles/domain-expert.md` — Package copy
5. `.github/copilot-instructions.md` — Update valid roles list
6. Test files — New transition tests for domain-expert

### Domain Expert Trigger Categories (from request)
1. **Engineering & AI:** Distributed systems, ML/AI, data engineering, performance/scalability
2. **Azure Platform:** Functions, AKS, Cosmos DB, DevOps pipelines, event-driven messaging
3. **Application & Solution:** Industry-specific, UX/accessibility, data governance
4. **Integration & Architecture:** API design, microservices, real-time systems, cross-service orchestration
