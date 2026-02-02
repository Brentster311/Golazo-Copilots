# GCP2-007: Project Owner Assistant Decision Notes

**Work Item**: GCP2-007 - Specialist Roles  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **On-demand invocation**: Specialists are not part of default workflow; invoked when needed.

2. **Phase-agnostic**: Specialists can be called during any phase.

3. **YAML/Markdown definition**: Specialist roles defined in config files, not hardcoded.

4. **Project-specific specialists**: Repos can define custom specialists.

5. **Context-triggered suggestions**: Agent can suggest specialists based on file patterns or content.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Hardcoded specialists | Not extensible |
| Always-present specialists | Adds unnecessary overhead to most work items |
| External API specialists | Adds complexity and dependencies |

---

## Tradeoffs Accepted

- **Trigger patterns may have false positives/negatives**: Acceptable; user can always invoke manually.
- **Deferred to future**: Not implementing specific specialists in MVP.

---

## Known Limitations

- Specialist quality depends on role definition quality
- No specialist "marketplace" for sharing definitions

---

## Must-Ask Checklist Responses

- **Interface type**: Configuration + agent API
- **Target platform**: Cross-platform
- **Data persistence**: Specialist definitions in .github/specialists/
- **User type**: Technical (developers)
