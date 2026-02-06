# GCP-0018: Add Version Management to Builder Role

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Add Version Management Requirements to Builder Role
- **As a**: Developer using Golazo workflow
- **I want**: Clear versioning guidance in the Builder role instructions
- **So that**: Version bumps follow consistent semantic versioning across all projects

---

## Out of Scope
- Automated version bumping tools
- CI/CD integration for versioning
- Language-specific version management scripts

---

## Assumptions
- **Assumption (explicit)**: Semantic versioning (MAJOR.MINOR.PATCH) is the standard
- **Assumption (explicit)**: Instructions should be language-agnostic

---

## Acceptance Criteria

- [x] Builder role includes Version Management section
- [x] MAJOR/MINOR/PATCH bump guidance is documented
- [x] Version update process is language-agnostic
- [x] Clear rules for when to bump vs skip version changes

---

## Implementation Note

This work item was created **retroactively** to document a change made to `golazo-instructions/roles/builder.md`. The change was committed before a work item was created, violating the Golazo workflow. This work item documents the change and the consent deviation.

**Lesson learned**: Before modifying files in `golazo-instructions/` or `.github/`, always ask the user if they want a work item created.

---

## Non-Functional Requirements
- Instructions must be clear and actionable
- Must not conflict with existing Builder responsibilities

---

## Telemetry / Metrics Expected
- None required
