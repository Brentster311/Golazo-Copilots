# SFI-031 — Architect Decision Notes

## Decisions
1. **Cache file schema** defined: `{ timestamp, manager_alias, tree: {person, direct_reports} }`.
2. **Atomic writes**: Use `tempfile.NamedTemporaryFile` + `os.replace()` for crash safety.
3. **Serialization**: `OrgTree`→dict is recursive; `OrgPerson`→dict maps all 5 fields. Reconstruction uses `OrgPerson(**d)` and recursive `OrgTree` building.
4. **No architectural concerns**. Change is well-isolated.
