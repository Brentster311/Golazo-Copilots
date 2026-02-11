# GCP-0038: Capability Registry Tool (`gcp_capabilities`)

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Capability Registry Tool
- **As a**: GCP user working on a project
- **I want**: a `gcp_capabilities` MCP tool that maintains a structured registry of my project's features, their key files, contracts, and dependencies — so I can query impact analysis when changing shared contracts
- **So that**: QA and Architect roles (and developers) can see which capabilities are affected by a set of file changes, preventing downstream misses like the one in GCP-0036
- **Out of scope**:
  - Auto-populating the registry from code analysis (manual curation)
  - Enforcing registry updates as a gate (advisory only)
  - Modifying the registry via the tool (manual YAML editing)
  - Role instruction changes to reference the tool (separate follow-on work item — affects QA, Architect, Developer, Refactor Expert, Retrospective roles)
  - Bootstrap scaffolding of `capabilities.yaml` template (separate follow-on)
  - Spine (`bootstrap-instructions.md`) mention of the tool (separate follow-on)
  - `gcp_status` surfacing registry presence or impact hints (separate follow-on)
- **Assumptions**:
  - **Assumption (explicit)**: Interface is MCP tool (same as all other GCP tools) — confirmed by user
  - **Assumption (explicit)**: Storage is a single `capabilities.yaml` at project root — YAML chosen for human readability since roles read it mid-review
  - **Assumption (explicit)**: Cross-platform (Python, same as GCP) — inherited from GCP
  - **Assumption (explicit)**: Users are technical (developers using GCP) — inherited from GCP
  - **Assumption (explicit)**: Granularity is one capability per user-observable feature, with contracts as the linking concept — derived from GCP-0036 retro analysis
- **Acceptance Criteria**:
  - AC1: `gcp_capabilities(action="list")` returns a summary of all capabilities from `capabilities.yaml` (name + description)
  - AC2: `gcp_capabilities(action="show", capability="<name>")` returns the full card: description, key_files, contracts, depends_on, depended_on_by
  - AC3: `gcp_capabilities(action="impact", files=["path/to/file.py"])` returns all capabilities whose `key_files` match any of the given files, plus all transitive dependents
  - AC4: `gcp_capabilities(action="validate")` checks that all `key_files` listed in the registry actually exist, returns pass/fail per capability
  - AC5: If `capabilities.yaml` does not exist, all actions return a clear message indicating no registry found (not an error)
  - AC6: `depended_on_by` is computed automatically from the inverse of `depends_on` — users only specify `depends_on` in YAML
- **Non-functional requirements**:
  - No external dependencies beyond PyYAML (or use only YAML subset parseable by a lightweight approach)
  - Registry validation should complete in <100ms for registries with up to 50 capabilities
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: New additive tool. No breaking changes to existing tools. Projects without `capabilities.yaml` are unaffected.

---

## Integration Points (V1 — in scope)

| # | File | Change |
|---|---|---|
| 1 | `tools/gcp_capabilities.py` | **New** — tool implementation |
| 2 | `server.py` | Import + Tool schema + call_tool handler (follows existing pattern) |
| 3 | `tools/__init__.py` | Export new tool |
| 4 | `tests/test_gcp_capabilities.py` | **New** — test coverage for AC1-AC6 |

## Follow-on Work Items (out of scope — captured for tracking)

| Area | Integration | Roles Affected |
|---|---|---|
| Role instructions | Add impact analysis prompts | QA, Architect, Developer, Refactor Expert, Retrospective |
| Bootstrap | Scaffold `capabilities.yaml` template | gcp_bootstrap |
| Spine | Mention tool in `bootstrap-instructions.md` | All roles (global) |
| Status | Surface `capabilities_registry_found` and impact hints | gcp_status |

Roles with **no benefit** from referencing capabilities: PO Assistant, Program Manager, Builder, Documentor, TechBestPractices.

---

## Capability YAML Schema

```yaml
# capabilities.yaml
capabilities:
  - name: string           # unique identifier
    description: string     # one-line summary
    key_files:              # files that implement this capability
      - path/to/file.py
    contracts:              # shared formats/interfaces this capability owns or depends on
      - "Description of contract"
    depends_on:             # other capability names this depends on
      - capability-name
```

`depended_on_by` is not stored — it is computed at query time from the inverse of all `depends_on` fields.
