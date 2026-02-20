# Golazo Copilot — Artifact Reference

A complete inventory of every file Golazo produces, consumes, or validates.

---

## 1. Workspace Scaffolding (produced by `gcp_bootstrap`)

These files are created once when a workspace is bootstrapped.

| Artifact | Path | Description |
|----------|------|-------------|
| Copilot instructions | `.github/copilot-instructions.md` | Spine file that tells Copilot how to use the Golazo workflow |
| Role definitions (×9) | `.github/roles/<role>.md` | One file per workflow role — defines purpose, tasks, and required outputs |
| Tech best practices | `.github/roles/TechBestPractices.md` | Coding standards and patterns specific to the project |
| WorkItems directory | `WorkItems/.gitkeep` | Root directory for all work item artifacts |
| Capability registry template | `capabilities.yaml` | Project-level feature/dependency registry |

---

## 2. Per–Work Item Artifacts

Created inside `WorkItems/<id>/` during a work item's lifecycle.

### 2.1 State (machine-managed — never edit directly)

| Artifact | Path | Description |
|----------|------|-------------|
| State file | `WorkItems/<id>/state.json` | Persisted workflow state (role, phase, history, deviations). Managed exclusively by `gcp_*` tools. |

`state.json` schema:

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | `"1.0"` | State format version |
| `work_item_id` | `string` | e.g. `GCP-0045` |
| `profile` | `complete \| express \| spike` | Workflow profile |
| `current_phase` | `definition \| development \| completion` | Current lifecycle phase |
| `current_role` | `string` | Active role name |
| `created_at` / `updated_at` | `ISO 8601` | Timestamps |
| `role_history` | `array` | Chronological list of `{role, entered_at, exited_at}` |
| `deviations` | `array` | Audit trail of `{id, action, reason, role, timestamp, consumed}` |

### 2.2 Definition Phase Artifacts

| Artifact | Path | Produced By | Gate For |
|----------|------|-------------|----------|
| User Story | `WorkItems/<id>/<id>-User-Story.md` | project-owner-assistant | Transition out of PO |
| Design Doc | `WorkItems/<id>/Design/<id>-design-doc.md` | program-manager | Transition out of PM |
| Review Comments | `WorkItems/<id>/Design/<id>-Review-Comments.md` | quality-assurance (created), architect (appends Architect Notes) | Transition out of QA, Architect |
| Test Cases | `WorkItems/<id>/Design/<id>-Test-Cases.md` | quality-assurance | Transition out of QA |
| Capability Impact | `WorkItems/<id>/Design/<id>-Capability-Impact.md` | architect | Transition out of Architect |

### 2.3 Development Phase Artifacts

| Artifact | Path | Produced By | Notes |
|----------|------|-------------|-------|
| Source code changes | *(project-specific)* | developer | Not path-validated |
| Automated tests | *(project-specific)* | developer / QA | Not path-validated |
| Refactored code | *(project-specific)* | refactor-expert | Not path-validated |

### 2.4 Completion Phase Artifacts

| Artifact | Path | Produced By | Notes |
|----------|------|-------------|-------|
| Refactoring Plan | `WorkItems/<id>/Design/<id>-Refactoring-Plan.md` | refactor-expert | Optional — created if improvements identified |
| Retro Plan | `WorkItems/<id>/Design/<id>-Retro-Plan.md` | retrospective | Optional — created if process improvements proposed |

### 2.5 Role Decision Notes (one per role visited)

Every role **requires** a decision notes file before transitioning away.

| Role | Notes File |
|------|-----------|
| project-owner-assistant | `WorkItems/<id>/RoleDecisionNotes/<id>-project-owner-assistant.md` |
| program-manager | `WorkItems/<id>/RoleDecisionNotes/<id>-program-manager.md` |
| quality-assurance | `WorkItems/<id>/RoleDecisionNotes/<id>-quality-assurance.md` |
| architect | `WorkItems/<id>/RoleDecisionNotes/<id>-architect.md` |
| developer | `WorkItems/<id>/RoleDecisionNotes/<id>-developer.md` |
| refactor-expert | `WorkItems/<id>/RoleDecisionNotes/<id>-refactor.md` |
| documenter | `WorkItems/<id>/RoleDecisionNotes/<id>-documenter.md` |
| builder | `WorkItems/<id>/RoleDecisionNotes/<id>-builder.md` |
| retrospective | `WorkItems/<id>/RoleDecisionNotes/<id>-retrospective.md` |

> **Note:** refactor-expert uses the short suffix `-refactor.md`, not `-refactor-expert.md`.

---

## 3. Git Artifacts (produced by builder role)

| Artifact | Type | Description |
|----------|------|-------------|
| Feature branch | `git branch` | Named after the work item ID (e.g. `GCP-0045`) |
| Commit(s) | `git log` | One or more commits with work-item-prefixed messages |

---

## 4. Project-Level Artifacts (consumed, not per–work item)

| Artifact | Path | Used By | Description |
|----------|------|---------|-------------|
| Capability registry | `capabilities.yaml` | architect, `gcp_capabilities` tool | Defines project capabilities, key files, contracts, and dependency graph |
| Copilot instructions | `.github/copilot-instructions.md` | All roles, `gcp_status` (stale check) | Master workflow instructions |
| Role files | `.github/roles/*.md` | `gcp_transition`, `gcp_status` | Define per-role behavior and required outputs |

---

## 5. Artifact Flow by Role

```
project-owner-assistant
  └─ produces: User-Story.md, PO decision notes

program-manager
  └─ produces: design-doc.md, PM decision notes

quality-assurance
  └─ produces: Review-Comments.md, Test-Cases.md, QA decision notes

architect
  └─ produces: Capability-Impact.md, Architect Notes (appended to Review-Comments.md), Architect decision notes
  └─ consumes: capabilities.yaml

developer
  └─ produces: code changes, tests, Developer decision notes

refactor-expert
  └─ produces: refactored code, Refactor decision notes
  └─ optionally: Refactoring-Plan.md

documenter
  └─ produces: updated docs, Documenter decision notes

builder
  └─ produces: git branch, commit(s), Builder decision notes

retrospective
  └─ produces: Retrospective decision notes
  └─ optionally: Retro-Plan.md, proposed instruction/role changes
```

---

## 6. Complete Directory Tree (fully-populated work item)

```
WorkItems/<id>/
├── <id>-User-Story.md
├── state.json
├── Design/
│   ├── <id>-design-doc.md
│   ├── <id>-Review-Comments.md
│   ├── <id>-Test-Cases.md
│   ├── <id>-Capability-Impact.md
│   ├── <id>-Refactoring-Plan.md      (optional)
│   └── <id>-Retro-Plan.md            (optional)
└── RoleDecisionNotes/
    ├── <id>-project-owner-assistant.md
    ├── <id>-program-manager.md
    ├── <id>-quality-assurance.md
    ├── <id>-architect.md
    ├── <id>-developer.md
    ├── <id>-refactor.md
    ├── <id>-documenter.md
    ├── <id>-builder.md
    └── <id>-retrospective.md
```
