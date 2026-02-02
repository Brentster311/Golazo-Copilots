# GCP2-002: Workflow Phases and Role Structure

**Status**: Draft  
**Priority**: Medium  
**Size**: M  
**Created**: 2026-01-27  
**Updated**: 2026-01-27

## User Story

**As a** developer working on projects of varying complexity,  
**I want** a phase-based workflow with clear role responsibilities and simplified options for smaller changes,  
**So that** I get appropriate rigor for complex work and efficiency for simple fixes.

## Background

Golazo V1 has 10 sequential roles in a flat list. This creates issues:
- No clear grouping of related activities
- Reviewer and Tester have overlapping quality concerns
- No mechanism for changes to "ripple back" to earlier roles
- Fast-Track too narrow (config-only)

## V2 Role Structure

### Role Consolidation

**Reviewer + Tester ? Tester**

The Tester role now encompasses:
- Requirements review (clarity, completeness, edge cases)
- Scope validation (preventing scope creep)
- Test case creation (TDD preparation)

This consolidation makes sense because:
- Both roles share a "quality lens" perspective
- Test thinking should happen during design, not after
- Reduces handoff friction

### V2 Roles (8 Core + Retro + Specialists)

| Role | Phase | Responsibilities |
|------|-------|------------------|
| **Project Owner** | Design | Define requirements, acceptance criteria, scope |
| **Program Manager** | Design | Break down work, identify dependencies, scope management |
| **Tester** | Design | Review requirements, identify edge cases, create test cases |
| **Architect** | Design | Technical design, patterns, dependencies, constraints |
| **Developer** | Development | Implement code following TDD (red-green-refactor) |
| **Refactor Expert** | Development | Clean up code without behavior change |
| **Builder** | Release | Build, run tests, verify deployment readiness |
| **Documentor** | Release | Update docs, ensure artifact completeness |
| **Retro** | Any | Triggered anytime to evaluate process issues |
| **Specialists** | Any | Domain experts (see GCP2-007) |

## Three-Phase Model

### Phase 1: Design

```
Project Owner ? Program Manager ? Tester ? Architect
```

**Purpose**: Define WHAT we're building and HOW  
**Exit Criteria (DoR)**:
- [ ] User Story exists with acceptance criteria
- [ ] Scope clearly bounded (in/out of scope)
- [ ] Test cases documented
- [ ] Design document approved

### Phase 2: Development

```
Developer ? Refactor Expert
```

**Purpose**: BUILD it right  
**Entry Criteria**: DoR complete  
**Exit Criteria**:
- [ ] Tests written first (TDD red phase)
- [ ] Code implemented (TDD green phase)
- [ ] Tests pass
- [ ] Refactor complete (no behavior change)

### Phase 3: Release & Validation

```
Builder ? Documentor ? [Validation Gate]
```

**Purpose**: VERIFY everything is complete and consistent  
**Validation Gate Checks**:
- [ ] All artifacts exist in correct locations
- [ ] All acceptance criteria pass
- [ ] All artifacts agree (no contradictions)
- [ ] Build passes
- [ ] Deployment validated (if applicable)

### Artifact Reconciliation (Ripple Back)

When changes occur during Development or Release:

```
Change detected (e.g., PO changes requirement)
         ?
???????????????????????????????????????????
? RIPPLE BACK TO DESIGN PHASE            ?
?                                         ?
? Affected roles must:                    ?
?  1. Revisit their artifacts             ?
?  2. Weigh in on the change              ?
?  3. Update their artifacts              ?
?  4. Re-approve if needed                ?
???????????????????????????????????????????
         ?
Resume from where change was detected
```

**Example**: PO decides to add a new field during Developer phase
1. Architect reviews: Does this change the design?
2. Tester reviews: Are test cases still valid?
3. Program Manager reviews: Does scope change?
4. All update artifacts as needed
5. Developer continues with updated requirements

## Workflow Profiles

| Profile | Phases | Roles | Use Case |
|---------|--------|-------|----------|
| **Complete** | All 3 | All 8 roles | Features, architectural changes, anything with risk |
| **Express** | Design (PO + Tester) + Dev + Release | PO, Tester, Developer, Builder | Bug fixes, small enhancements |
| **Spike** | Design (PO only) + Dev (partial) | PO, Developer | Experimental/throwaway code, no artifacts required |

### Profile Selection

- **Complete**: Default for all new work
- **Express**: User must explicitly request ("express mode", "quick fix")
- **Spike**: User must explicitly request ("spike this", "just experimenting")

### Profile Escalation

If complexity is discovered during Express/Spike:
```
Agent: "This change affects [X]. Recommend upgrading to Complete workflow.
        Continue with Express, or switch to Complete?"
```

## Guides Integration

Existing guides from `.github/guides/` remain active:
- `powershell-terminal.md` - Terminal encoding rules
- `golazo-update.md` - Version checking
- `standard-checker.md` - Checks existing patterns before proposing new ones (renamed from PatternProposals.md)

Guides are loaded contextually by the agent when relevant (not always in context).

## Specialist Roles (Future)

The architecture must support adding Specialist roles (see **GCP2-007**):
- Specialists can be invoked during any phase
- Examples: Kusto Expert, NLP Expert, Security Specialist
- Specialists produce their own decision artifacts
- Agent determines when to invoke specialists based on context

### Extensibility Requirements

1. [ ] Role registry supports adding new roles without code changes
2. [ ] Roles have metadata: name, phase affinity, trigger conditions
3. [ ] Specialist roles can be project-specific (defined in repo config)
4. [ ] Agent can invoke specialists mid-workflow when expertise needed

## Acceptance Criteria

### Phase Structure
1. [ ] Three-phase model implemented (Design, Development, Release)
2. [ ] Each phase has clear entry/exit criteria
3. [ ] Validation gate performs artifact consistency checks

### Role Changes
4. [ ] Tester role includes former Reviewer responsibilities
5. [ ] 8 core roles + Retro + extensible Specialists
6. [ ] Retro can be triggered at any point in workflow

### Artifact Reconciliation
7. [ ] Changes trigger ripple-back to affected Design phase roles
8. [ ] Affected roles must update artifacts before proceeding
9. [ ] Reconciliation is logged in work item state

### Profiles
10. [ ] Complete profile uses all roles (default)
11. [ ] Express profile: PO ? Tester ? Developer ? Builder
12. [ ] Spike profile: PO ? Developer (no artifacts required)
13. [ ] Profile escalation supported

### Extensibility
14. [ ] Architecture supports adding Specialist roles (GCP2-007)
15. [ ] Role definitions are data-driven, not hardcoded

## Out of Scope

- Implementing specific Specialist roles (covered in GCP2-007)
- Removing TDD requirement for production code
- Parallel role execution (roles remain sequential within phases)

## Dependencies

- GCP2-001 (Agent architecture for consent-based enforcement)
- GCP2-003 (State management for tracking phase/role progress)

## Related

- GCP2-007 (Specialist Roles - future)
