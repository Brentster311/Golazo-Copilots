# SFI-028 Refactor Expert Notes

## Review Summary
Reviewed `get_org_mapping()`, `get_service_owners()`, `do_refresh()` in tk_app.py and `test_sfi_028.py`.

## Findings

### Production Code
1. **`"'s Team"` fallback duplicated 3x** in `fetch_owner` (pre-existing, not from SFI-028) — extract helper. Deferred: not in scope.
2. **`all_owners` set built redundantly** in `do_refresh` — `get_service_owners` already computes it internally. Minor duplication.
3. **Lazy imports inside functions** — `ThreadPoolExecutor`, `get_client` etc. imported at call time. Pre-existing pattern in the codebase; changing would violate repo conventions.
4. **`completed = [0]` mutable counter** — Pre-existing pattern, not introduced by SFI-028.

### Test Code
1. **Mock setup repeated in every test** — could extract to a pytest fixture. Low risk but adds indirection.
2. **Tests T2-T5 follow same pattern** — candidate for `@pytest.mark.parametrize`. Would reduce ~60 LOC.
3. **`_chain_registry()` and `_owner_aliases()` rebuilt per call** — could be module-level constants.

## Decision
**No refactoring applied.** Rationale:
- Express profile — minimize risk of behavioral regression
- Production code changes are confined and well-structured
- Most findings are pre-existing patterns (not introduced by SFI-028)
- Test parametrize opportunity noted for future cleanup
- All 42/42 tests pass; PyInstaller build succeeds

## Recommendations for Future Work Items
- Extract `"'s Team"` fallback into `_team_fallback(service_name)` helper
- Parametrize org-mapping test cases (T2-T5) to reduce duplication
- Consider extracting test fixture for common mock setup pattern
