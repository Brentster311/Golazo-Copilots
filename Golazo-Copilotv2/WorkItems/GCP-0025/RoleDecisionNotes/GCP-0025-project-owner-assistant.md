# GCP-0025 Project Owner Assistant Notes

## Decision Log

### Why this refactor?

1. **Evidence parameter causes friction** - Agent must know exact evidence format, leads to infinite loops when validation fails
2. **DoR/DoD marking is redundant** - We already require role notes files, why also require manual marking?
3. **Role files already define outputs** - Just make them the source of truth and validate automatically

### Scope decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Remove gcp_mark_dor/dod | Yes | These tools add friction without value |
| Role-based validation | Yes | Natural alignment with workflow |
| Breaking change (v3.0.0) | Yes | Clean break better than complex migration |
| Keep role notes | Yes | Still valuable for decision documentation |
| Keep consent mechanism | Yes | Need escape hatch for edge cases |

### Key design decisions

1. **Required outputs in role files** - Use `## Required Outputs` markdown section with parseable rules
2. **Validation types**:
   - `file: <path>` - Check file exists
   - `git-branch: <pattern>` - Check git branch exists
   - `git-commit: <pattern>` - Check git log for pattern
3. **Validation on transition OUT** - Current role's outputs checked before moving to next role
4. **Status shows validation state** - So agent knows what's missing before attempting transition

### Questions answered

- Q: What about DoD items like testsPass, buildPasses?
- A: These become required outputs for specific roles. Tests must pass before leaving Developer role, build must pass before leaving Builder role.

### Risk assessment

| Risk | Mitigation |
|------|------------|
| Breaking existing workflows | Document migration path, bump to v3.0.0 |
| Role files become complex | Keep validation rules simple, limit to 3 types |
| Performance (running git commands) | Cache validation results during single status/transition call |
