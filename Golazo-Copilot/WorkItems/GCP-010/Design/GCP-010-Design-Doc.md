# GCP-010: Design Document

## Summary
Add a mandatory "Role Transition Announcement" subsection to the spine's Operating mode section, requiring Copilot to explicitly announce when transitioning between roles.

## Problem Statement
Currently, Copilot transitions between roles without explicit announcement. This makes it difficult to:
- Track which role produced which artifact
- Understand why a transition occurred
- Audit the workflow execution
- Debug issues when artifacts are missing or incorrect

## Business Case

### Why Now
- Observed confusion during GCP-008 and GCP-009 about which role was active
- Workflow transparency improves debugging and trust
- Low implementation cost (documentation only)

### Impact
- **Positive**: Clear role boundaries in output
- **Positive**: Easier to audit workflow execution
- **Positive**: Better debugging when things go wrong

### KPIs
- Role transitions are visible in Copilot output
- Users can identify which role produced each artifact

## Stakeholders
| Role | Interest |
|------|----------|
| Developers | Clear understanding of workflow progress |
| Project Owners | Auditable workflow execution |

## Functional Requirements

### FR-1: Add Role Transition Announcement Subsection
Add to Operating mode section:
```markdown
### Role Transition Announcement (MANDATORY)

When transitioning between roles, explicitly state:
- "**Transitioning from [Role A] to [Role B]**"
- Reason for transition
- What artifact/output was produced by previous role
```

### FR-2: Placement
- Insert after the existing Operating mode bullet points
- Before "Role instruction loading rule" section

## Non-Functional Requirements
- Announcement format is consistent
- Announcements are concise (3-5 lines max)

## Proposed Approach

### Implementation
1. Insert new subsection in spine after Operating mode bullets
2. Use exact format from RC file
3. Update VERSION to 1.1.3
4. Update CHANGELOG

### Content to Add
```markdown
### Role Transition Announcement (MANDATORY)

When transitioning between roles, explicitly state:
- "**Transitioning from [Role A] to [Role B]**"
- Reason for transition
- What artifact/output was produced by previous role
```

## Alternatives Considered

| Alternative | Evaluation | Decision |
|-------------|------------|----------|
| No announcement | Status quo, poor visibility | Rejected |
| Verbose announcement | Too much output | Rejected |
| Announcement in each role file | Duplicative | Rejected — single source in spine |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Copilot ignores instruction | Low | Low | Clear, prominent placement |
| Adds too much output | Low | Low | Keep format concise |

## Dependencies
- None

## Migration / Rollout Plan
- Single commit to spine
- No migration needed

## Test Strategy Summary
1. Verify spine contains new subsection
2. Verify format matches specification
3. Manual test: Start workflow, verify announcements appear
