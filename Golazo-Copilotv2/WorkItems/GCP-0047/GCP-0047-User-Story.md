# GCP-0047 User Story

**Status**: IMPLEMENTED

## User Story

- **Title:** SDLC Role Improvements — Fix Gaps and Reduce Redundancies
- **As a:** Golazo Copilot user
- **I want:** The 10-role workflow improved to fix logical ordering errors, reduce review redundancies, add missing governance sections, and introduce a POA closure step after retrospective
- **So that:** Every work item produces consistent, non-overlapping role outputs with correct entry conditions, clear ownership of design-quality vs. testability concerns, and a proper closure gate that validates acceptance criteria before the work item is finalized

- **Out of scope:**
  - Adding new roles (no Security Reviewer role — security is folded into Architect)
  - Changes to server.py MCP tool handlers (formatting, request handling)
  - Removing or reordering existing roles in ROLE_ORDER

- **Assumptions:**
  - **Assumption (explicit):** "POA re-entry after Retrospective" means adding a real forward transition from retrospective → project-owner-assistant in transitions.py, plus a new "Closure" section in the POA role file. The workflow becomes: ...→ retrospective → project-owner-assistant (closure). This requires transitions.py changes, server.py enum update, test updates, and copilot-instructions updates.
  - **Assumption (explicit):** "Sharpen QA to testability only" means removing design-quality bullets from QA that overlap with Architect (risk coverage, operability, cost/performance tradeoffs) but keeping QA's ownership of Review-Comments.md for test-related critique
  - **Assumption (explicit):** "Consolidate capability registry" means removing `gcp_capabilities` instructions from Domain Expert and QA roles only. Developer and Refactor Expert keep their capability registry checks. Architect keeps impact analysis, Builder keeps validation.
  - **Assumption (explicit):** Security review expansion in Architect means adding a mandatory security checklist subsection, not a new required output file
  - **Assumption (explicit):** Branch creation moves from Builder to Developer's first action / entry conditions
  - **Assumption (explicit):** All changes apply to the source defaults copy (`roles/defaults/`). The 2 deployed copies (`.github/roles/` and `golazo-copilot/.github/roles/`) are updated to match.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] AC1: Documenter role file no longer references build verification in its First Action or Entry Conditions
  - [ ] AC2: Developer role file includes branch creation in its First Action (check/create feature branch before writing tests); Builder role file no longer contains the "Before Developer role" branch creation section
  - [ ] AC3: transitions.py has a forward transition from retrospective → project-owner-assistant; POA role file includes a "Closure" section with: (a) final git commit, (b) AC validation against User Story, (c) collect pending/future work items proposed by all roles and present to PO for disposition; server.py enum includes project-owner-assistant as a valid transition target from retrospective
  - [ ] AC4: QA role file is focused on testability — design-quality bullets (risk coverage, operability, cost/performance tradeoffs, naming clarity, folder structure) moved to Architect; QA retains test strategy, edge cases, failure modes, and Review-Comments ownership for test critique
  - [ ] AC5: Program Manager role file has Decision Rules, Escalation Rules, and Success Criteria sections consistent with the structure used by all other roles

- **Non-functional requirements:**
  - Role file markdown structure must remain consistent across all roles (Purpose, First action, Entry conditions, Responsibilities, Forbidden actions, Required Outputs, Decision rules, Escalation rules, Success criteria)
  - Changes must be applied to all 3 copies of each modified role file

- **Telemetry / metrics expected:** None (role files are static markdown)

- **Rollout / rollback notes:**
  - Rollout: Bump version, rebuild package, deploy to Azure Artifacts. Bootstrap new workspaces to get updated roles. Existing workspaces need manual re-bootstrap or file copy.
  - Rollback: Revert role file changes, rebuild with previous version.

## Additional Changes (from analysis items #2, #3, #5, #6, #10A)

### Domain Expert ↔ Architect Boundary Clarification
- Add explicit boundary note to Domain Expert: "Provide domain-specific knowledge (e.g., Cosmos DB partition design, ML model selection), not structural/architectural decisions"
- Add boundary note to Architect: "Structural decisions and system design; defer to Domain Expert for domain-specific knowledge cited in Review Comments"

### Capability Registry Consolidation
- Remove `gcp_capabilities` instructions from: Domain Expert, QA
- Keep: Architect (impact analysis — REQUIRED), Developer (pre-commit check), Refactor Expert (post-refactor check), Builder (validate)
- Retrospective: Keep the "check whether gcp_capabilities was consulted" responsibility (process review, not a code check)

### Security Review in Architect (#10A)
- Add a "Security Review" subsection to Architect responsibilities with a mandatory checklist:
  - Data exposure: what data does this feature touch, who should/shouldn't access it?
  - Auth boundary changes: new or modified authentication/authorization flows?
  - Attack surface: new API endpoints, input validation, privilege escalation paths?
  - Compliance: PII handling, cross-tenant access, regulatory implications?
  - Document findings in Capability-Impact.md under a "Security Assessment" heading
