# GCP-0046 Design Document

## Summary
Add a `domain-expert` role to the Golazo Copilot workflow, inserted between Program Manager and Quality Assurance in the definition phase. This role evaluates whether specialized domain expertise is needed for a work item, simulates consultation with relevant domain experts, and contributes guidance to the shared Review Comments artifact.

## Problem Statement
Currently, the workflow moves directly from Program Manager (design doc) to Quality Assurance (design review + test cases). When work items involve specialized domains — Azure platform services, distributed systems, AI/ML, data engineering — there is no structured checkpoint to ensure domain-specific concerns are identified before the design is reviewed and approved. This can lead to late-stage rework when domain-specific issues surface during development or refactoring.

## Business Case
- **Why now:** The workflow already has 9 roles covering the full software lifecycle, but lacks a domain expertise checkpoint. As work items grow in technical complexity, the gap between "general design" and "domain-aware design" becomes costly.
- **Impact:** Reduces rework from missed domain concerns; improves design quality for specialized work items; creates an auditable record of domain consultation decisions.
- **KPIs:** Not directly measurable via telemetry (role files are static markdown). Success measured by: domain expertise captured in Review Comments for relevant work items; no increase in design-phase rework.

## Stakeholders
- Golazo Copilot users (all developers using the workflow)
- Golazo Copilot maintainers (must update transitions, tests, documentation)

## Functional Requirements

### FR1: Domain Expert Role File
Create `domain-expert.md` following the standard role file structure with:
- Domain expert identification process (4-step)
- Trigger categories for when domain experts should be proposed
- Example domain expert triggers (NLP/LLM, Cosmos DB, Azure DevOps, etc.)
- Consultation rules (timing, scope, documentation requirements)
- Required output: role decision notes only (Review Comments is a shared artifact)

### FR2: Transition Logic Changes
Modify `transitions.py`:

| Constant | Change |
|----------|--------|
| `TRANSITIONS` | Add `"domain-expert": ["quality-assurance", "program-manager"]`; change `"program-manager"` forward from `["quality-assurance", ...]` to `["domain-expert", ...]`; change `"quality-assurance"` backward from `[..., "program-manager"]` to `[..., "domain-expert"]` |
| `PHASE_MAP` | Add `"domain-expert": "definition"` |
| `ROLE_ORDER` | Insert `"domain-expert"` at index 2 (after `program-manager`) |

### FR3: Three-Copy Role File Deployment
Create the role file in all three locations:
1. `golazo-copilot/src/golazo_copilot/roles/defaults/domain-expert.md` (source)
2. `.github/roles/domain-expert.md` (deployed workspace)
3. `golazo-copilot/.github/roles/domain-expert.md` (package)

### FR4: Update copilot-instructions.md
Update the valid roles list in `.github/copilot-instructions.md` to include `domain-expert` at position 3.

## Non-Functional Requirements
- All 242+ existing tests must continue to pass
- New tests must cover domain-expert forward/backward/skip transitions
- Role file follows identical markdown structure to existing roles

## Proposed Approach

### Step 1: Modify transitions.py
```python
TRANSITIONS = {
    "project-owner-assistant": ["program-manager"],
    "program-manager": ["domain-expert", "project-owner-assistant"],      # changed
    "domain-expert": ["quality-assurance", "program-manager"],            # new
    "quality-assurance": ["architect", "domain-expert"],                  # changed
    "architect": ["developer", "quality-assurance"],
    "developer": ["refactor-expert", "architect"],
    "refactor-expert": ["documenter", "developer"],
    "documenter": ["builder", "refactor-expert"],
    "builder": ["retrospective", "documenter"],
    "retrospective": ["builder"],
}

PHASE_MAP = {
    ...existing...
    "domain-expert": "definition",                                        # new
}

ROLE_ORDER = [
    "project-owner-assistant",
    "program-manager",
    "domain-expert",            # new — index 2
    "quality-assurance",
    "architect",
    ...
]
```

### Step 2: Create domain-expert.md role file
The role file will include:
- **First action:** Analyze work item for domain expertise needs
- **Responsibilities:** 4-step identification process, trigger evaluation, consultation documentation
- **Domain trigger categories:** Engineering & AI, Azure Platform, Application & Solution, Integration & Architecture
- **Consultation rules:** Participates between PM and QA, provides guidance not implementation decisions, writes to Review Comments
- **Required Outputs:** `WorkItems/{id}/RoleDecisionNotes/{id}-domain-expert.md`

### Step 3: Deploy to all 3 locations
Copy the role file to `.github/roles/` and `golazo-copilot/.github/roles/`.

### Step 4: Update copilot-instructions.md
Add `domain-expert` to the numbered valid roles list.

### Step 5: Write tests
- Forward transition: program-manager → domain-expert ✓
- Forward transition: domain-expert → quality-assurance ✓
- Backward transition: domain-expert → program-manager ✓
- Backward transition: quality-assurance → domain-expert ✓
- Skip prevention: program-manager → quality-assurance ✗ (must go through domain-expert)
- Phase check: domain-expert is in "definition"

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Add domain expertise to the PM role | Overloads PM with two distinct responsibilities; hard to audit separately |
| Add domain expertise to the QA role | QA reviews the design; domain expertise should inform the design before review |
| Create a separate Domain-Expert-Guidance.md artifact | Unnecessary complexity; Review Comments already serves as the shared critique artifact |
| Make domain-expert optional/skippable without consent | Undermines the workflow enforcement model; if needed it should be a gate, if not needed the role can document "no domain expertise required" and transition |

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Existing work items in flight have state.json with old role sequence | Backward transitions are index-based and always allowed; forward transitions check the TRANSITIONS dict. Old state.json files referencing pre-domain-expert roles will still work because the transition logic validates against the dict, not hardcoded indices. |
| Test count increase | All existing transition tests may reference hardcoded role indices; these need updating. Run full test suite before merge. |
| Skip from PM → QA no longer valid | This is intentional — the domain-expert step is mandatory. Document in release notes. |

## Dependencies
- None external. Only changes internal to the golazo-copilot package.

## Migration / Rollout / Rollback Plan
- **Rollout:** Bump version to 2.104.5, rebuild, deploy to Azure Artifacts. New bootstrapped workspaces get the role automatically. Existing workspaces need the role file copied to `.github/roles/`.
- **Rollback:** Revert commits, rebuild with previous version, redeploy.

## Observability Plan
- N/A — role files are static markdown with no runtime telemetry.

## Test Strategy Summary
- Unit tests for transition validation (forward, backward, skip-prevention)
- Unit test for phase mapping
- Verify role file exists in all 3 locations
- Run existing test suite to confirm no regressions
