# EES-00014 — QA Notes

## Key Decisions
1. Removing `because`-specific tests (TC-05 missing/empty because) since the field no longer exists.
2. Adding one new test: `Rule.from_dict` silently ignores old `because` data.
3. The `_confirm_root_cause` function in `main.py` must be updated/removed — it depends on `LLMResponse.root_cause`.
