# GCP-0025 Program Manager Notes

## Decision Log

### Design decisions made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Validation types | file, dir, git-branch, git-log | Cover common cases without over-engineering |
| Path placeholder | `{id}` only | Keep simple, one replacement |
| Validation timing | On transition OUT | Natural checkpoint in workflow |
| State.json changes | Ignore old dor/dod | Simpler than migration |
| Version bump | 3.0.0 | Breaking change warrants major version |

### What required outputs per role?

| Role | Required Outputs |
|------|-----------------|
| project-owner-assistant | User Story, role notes |
| program-manager | Design doc, role notes |
| quality-assurance | Review comments, role notes |
| architect | (optional technical design), role notes |
| developer | Source code changes, tests written, role notes |
| refactor-expert | Refactoring complete, role notes |
| builder | Build passes, role notes |
| Documenter | Docs updated, role notes |
| retrospective | Retro notes |

### Open items resolved

- **Git branch validation**: Pattern matching with `git branch --list <pattern>`
- **Tests pass validation**: For Developer role, run `pytest --co -q` or just check test files exist?
  - Decision: Check test files exist (file validation). Running tests is too slow/risky.

### Phasing rationale

1. **Phase 1 (output validation)** - Can be developed and tested independently
2. **Phase 2 (integration)** - Minimal changes to existing tools
3. **Phase 3 (removal)** - Clean up after new system is working
