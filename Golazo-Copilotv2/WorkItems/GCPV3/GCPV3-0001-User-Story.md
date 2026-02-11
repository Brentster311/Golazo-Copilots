# GCPV3-0001: Custom Roles in Workflow

**Status**: BACKLOG

**Origin**: Cut from GCP v2 (GCP-0015)

---

## User Story

- **Title**: Allow Users to Add Custom Roles to the Workflow
- **As a**: Team using Golazo Copilot
- **I want**: To define custom roles that integrate into the workflow sequence
- **So that**: Our team's specific processes (e.g., Security Review, Accessibility Check) can be enforced by GCP

---

## Out of Scope
- Removing or renaming built-in roles
- Custom role dependencies (e.g., "Security must come after Architect")
- Role-specific DoR/DoD items (each role having its own checklist)
- GUI for role management

---

## Assumptions
- Custom roles are defined in a configuration file (e.g., `gcp.yaml` or `.github/gcp-config.yaml`)
- Custom role instructions are loaded from `.github/roles/{custom-role}.md`
- Custom roles are inserted at a specified position in the workflow sequence

---

## Acceptance Criteria

- [ ] Users can define custom roles in a configuration file
- [ ] Custom roles appear in `gcp_status` role sequence
- [ ] `gcp_transition` validates transitions to/from custom roles
- [ ] Custom role instructions are loaded from `.github/roles/{role-name}.md`
- [ ] If custom role file is missing, a helpful error message is returned
- [ ] Built-in roles continue to work unchanged when no custom roles are defined

---

## Non-Functional Requirements
- Configuration file format should be YAML for human readability
- Maximum of 20 roles total (built-in + custom) to prevent workflow bloat

---

## Telemetry / Metrics Expected
- Count of workspaces using custom roles
- Most common custom role names
