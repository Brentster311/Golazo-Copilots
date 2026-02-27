# SFI-036 — Review Comments

## Design Review

### Clarity: ✅ Pass
The design doc clearly maps every symbol to its target module. The migration table is comprehensive.

### Feasibility: ✅ Pass
All 40 symbols verified present in decomposed modules. No blockers.

### Risk Coverage: ✅ Pass
Single risk (missing symbols) already mitigated by verification step.

### Edge Cases

- **Patch targets**: Tests patching `sfi_reporter.tk_app.write_cache` must be updated to patch where the symbol is *used* (i.e., `sfi_reporter.services.write_cache`), not where it's *defined* (`sfi_reporter.cache.write_cache`). The design doc notes this correctly.
- **`__init__.py` re-exports**: Verify that `sfi_reporter/__init__.py` does not re-export from `tk_app`. If it does, that must be updated too.
- **Circular imports**: After retargeting `query_builder.py` to import from `dialogs.py`, verify no circular import chain is introduced (since `dialogs.py` may import from other modules that import `query_builder`).

### Naming: ✅ Pass
No renaming needed — existing module names are clear.

### Recommendations
1. Run `python -c "from sfi_reporter.app import main"` as a quick import smoke test after changes.
2. Run the full test suite as final validation.

---

## Architect Notes

### Architectural Alignment: ✅ Approved
This cleanup completes the SFI-030 decomposition. The target architecture (app → services/models/formatters/dialogs) is correct and already in place.

### Contracts: ✅ No change
No API or data contracts are modified. All symbols retain their existing signatures.

### Security / Privacy: ✅ N/A
No security-relevant changes. No new dependencies, no new network calls.

### Dependency / Coupling: ✅ Improved
Removing the monolith eliminates the ambiguity of having two copies of every symbol. Import paths will now correctly reflect module boundaries.

### Rollback Safety: ✅ Single git revert
No data migration or schema changes involved.

### Circular Import Risk: ⚠️ Low
`query_builder.py` currently imports `SortableTreeview` and `DetailModal` from `tk_app.py`. After retargeting to `dialogs.py`, verify no circular dependency exists between `dialogs.py` ↔ `query_builder.py`. If `dialogs.py` imports from `query_builder.py`, a lazy import may be needed.
