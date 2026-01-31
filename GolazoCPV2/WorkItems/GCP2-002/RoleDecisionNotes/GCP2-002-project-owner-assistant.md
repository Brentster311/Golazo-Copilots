# GCP2-002: Project Owner Assistant Decision Notes

**Work Item**: GCP2-002 - Workflow Phases and Role Structure  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **Three-phase model**: Design ? Development ? Release provides clear groupings and gates.

2. **Reviewer + Tester merged into Tester**: Both roles share a "quality lens" perspective; consolidation reduces handoff friction.

3. **Tester in Design phase**: Test thinking should happen early, not after implementation.

4. **Tester required in Express profile**: Even quick fixes benefit from quality review.

5. **Ripple-back mechanism**: Changes during Development/Release trigger affected Design roles to revisit artifacts.

6. **Retro can be triggered anytime**: Not tied to workflow completion.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Keep 10 roles | Excessive ceremony; Reviewer/Tester overlap |
| Remove Tester from Express | Loses quality perspective for quick fixes |
| Four profiles | Three is sufficient (Complete/Express/Spike) |

---

## Tradeoffs Accepted

- **No parallel role execution**: Roles remain sequential within phases.
- **Ripple-back adds complexity**: Worth it for artifact consistency.

---

## Known Limitations

- Adding new roles requires configuration changes
- Ripple-back logic may be complex to implement

---

## Must-Ask Checklist Responses

- **Interface type**: Configuration/definition (consumed by state machine)
- **Target platform**: Cross-platform
- **Data persistence**: Role definitions may be in code or config
- **User type**: Technical (developers)
