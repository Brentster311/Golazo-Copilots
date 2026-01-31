# GCP2-007: Specialist Roles

**Status**: BACKLOG  
**Priority**: Low  
**Size**: L  
**Created**: 2026-01-27

---

## User Story

- **Title**: Specialist Roles
- **As a**: Developer working on projects requiring domain expertise
- **I want**: To invoke specialist roles (e.g., Kusto Expert, NLP Expert) during the workflow
- **So that**: Domain-specific knowledge is applied at the right time without bloating every workflow

- **Out of scope**:
  - Implementing specific specialist content (instructions, guides)
  - AI model fine-tuning for specialist knowledge
  - External API integrations for specialist knowledge
  - Specialist marketplace for sharing definitions

- **Assumptions**:
  - **Assumption (explicit)**: Specialists defined in YAML/Markdown config files
  - **Assumption (explicit)**: Specialists invoked explicitly by user or suggested by agent
  - **Assumption (explicit)**: Specialist definitions stored in `.github/specialists/`

- **Acceptance Criteria**:
  - [ ] Specialist roles can be defined in YAML/Markdown format
  - [ ] Specialists can be invoked explicitly by user request
  - [ ] Agent can suggest specialists based on file patterns or content keywords
  - [ ] Specialists produce decision artifacts in RoleDecisionNotes/
  - [ ] Specialists can be invoked at any workflow phase
  - [ ] `golazo specialists` command lists available specialists
  - [ ] Project-level specialist definitions in `.github/specialists/`

- **Non-functional requirements**:
  - Specialist definitions are data-driven (no code changes to add new specialists)
  - Trigger patterns should have low false-positive rate

- **Telemetry / metrics expected**:
  - None for MVP

- **Rollout / rollback notes**:
  - Extensibility feature; can ship without any specialists defined

---

## Background

Not every work item needs every type of expertise. However, when domain knowledge is required, it should be:
- Available on-demand
- Integrated into the workflow (not a separate process)
- Producing auditable artifacts like other roles

---

## Example Specialists

| Specialist | Triggers | Use Case |
|------------|----------|----------|
| Kusto Expert | `.kql` files, KQL keywords | Query review and optimization |
| Security Specialist | Auth code, secrets | Security review |
| Database Expert | SQL files, ORM code | Query optimization |

---

## Specialist Definition Format

```yaml
name: Kusto Expert
id: kusto-expert
triggers:
  - file_patterns: ["*.kql", "*.kusto"]
  - content_patterns: ["kusto", "KQL"]
responsibilities:
  - Review Kusto queries for correctness
  - Suggest query optimizations
```

---

## Dependencies

- GCP2-001 (Agent architecture for role invocation)
- GCP2-002 (Phase structure for specialist integration)
- GCP2-003 (State management for tracking specialist invocations)

## Invocation Methods

### 1. Explicit User Request
```
User: "I need the Kusto Expert to review these queries"
Agent: "Invoking Kusto Expert role..."
```

### 2. Agent Suggestion (Context-Triggered)
```
Agent: "I notice this work item involves Kusto queries. 
        Would you like to invoke the Kusto Expert for review?"
```

### 3. Profile Inclusion
```yaml
# In project config
profiles:
  telemetry-feature:
    includes: [kusto-expert, security-specialist]
```

## Specialist Definition Schema

```yaml
# .github/specialists/kusto-expert.md or .github/roles/specialists/kusto-expert.yaml
name: Kusto Expert
id: kusto-expert
description: Reviews and optimizes Kusto (KQL) queries for Azure Data Explorer

triggers:
  # Conditions that prompt agent to suggest this specialist
  - file_patterns: ["*.kql", "*.kusto"]
  - content_patterns: ["kusto", "KQL", "Azure Data Explorer", "ADX"]
  - user_keywords: ["kusto expert", "kql review"]

responsibilities:
  - Review Kusto queries for correctness and efficiency
  - Suggest query optimizations
  - Identify potential performance issues
  - Recommend best practices for schema design

artifacts:
  - "WorkItems/<id>/RoleDecisionNotes/<id>-kusto-expert.md"

forbidden:
  - Writing production code (advisory only)
  - Changing queries without Developer approval

guides:
  - ".github/guides/kusto-best-practices.md"  # Optional specialist-specific guide
```

## Example Specialists

| Specialist | Triggers | Primary Phase |
|------------|----------|---------------|
| **Kusto Expert** | .kql files, KQL content | Design, Development |
| **NLP Expert** | NLP libraries, text processing | Design |
| **Security Specialist** | Auth code, secrets, permissions | Design, Release |
| **Database Expert** | SQL files, ORM code, migrations | Design, Development |
| **API Design Specialist** | OpenAPI specs, REST endpoints | Design |
| **Performance Specialist** | Perf tests, benchmarks, profiling | Development, Release |
| **Accessibility Specialist** | UI code, WCAG references | Design, Release |
| **Localization Specialist** | i18n, resource files, translations | Development |

## Workflow Integration

### Specialist During Design Phase
```
PO ? PM ? Tester ? Architect ? [Kusto Expert] ? (continue)
                                     ?
                         Produces: kusto-expert.md
                         Reviews: query design
```

### Specialist During Development Phase
```
Developer ? [Security Specialist] ? Refactor Expert
                    ?
        Produces: security-specialist.md
        Reviews: auth implementation
```

### Multiple Specialists
```
Developer ? [Kusto Expert] ? [Security Specialist] ? Refactor Expert
```

## Acceptance Criteria

### Core Functionality
1. [ ] Specialist roles can be defined in YAML/Markdown format
2. [ ] Specialists can be invoked explicitly by user
3. [ ] Agent can suggest specialists based on context triggers
4. [ ] Specialists produce decision artifacts like other roles
5. [ ] Specialists can be invoked at any phase

### Configuration
6. [ ] Project-level specialist definitions in `.github/specialists/` or `.github/roles/`
7. [ ] Global specialists provided by Golazo (Kusto, Security, etc.)
8. [ ] Profiles can include specialists by default

### Integration
9. [ ] Specialist invocation logged in work item state
10. [ ] Specialist artifacts included in validation gate checks
11. [ ] Specialists can reference their own guides

### Discoverability
12. [ ] `golazo specialists` command lists available specialists
13. [ ] Agent describes available specialists when asked

## Out of Scope

- Implementing specific specialist content (instructions, guides)
- AI model fine-tuning for specialist knowledge
- External API integrations for specialist knowledge

## Dependencies

- GCP2-001 (Agent architecture for role invocation)
- GCP2-002 (Phase structure for specialist integration)
- GCP2-003 (State management for tracking specialist invocations)

## Future Considerations

- **Specialist Marketplace**: Share specialist definitions across repos
- **Specialist Chaining**: One specialist can recommend another
- **Specialist Confidence**: Agent rates how confident it is in specialist suggestions
- **Custom LLM Prompts**: Specialists could have custom system prompts for better domain knowledge
