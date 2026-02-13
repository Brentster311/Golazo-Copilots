# EES-00008 Developer Role Notes

## TDD Approach
- **Red phase**: Wrote 12 new tests across 3 test files covering all acceptance criteria.
- **Green phase**: Implemented production code to make all tests pass.
- **Result**: 238 tests pass (226 existing + 12 new), 0 failures.

## Files Modified

### Production Code
| File | Change |
|------|--------|
| `src/ees/models.py` | Added `scope: Literal["rule", "context"] = "rule"` to `Fact`, updated `to_dict()` / `from_dict()` |
| `src/ees/fact_extractor.py` | Updated `_SYSTEM_PROMPT` with scope classification instructions and extraction restrictions |
| `src/ees/gui/adapters.py` | Added `scope` key to `facts_to_rows()` output dict |
| `src/ees/gui/app.py` | Added scope column to `facts_tree`, "Set Rule"/"Set Context" buttons, `_set_fact_scope()` method, scope filter in `_save_all`, scope in detail dialog |
| `src/ees/main.py` | Added scope filter before `filter_rules()` call in CLI path |

### Test Code
| File | Change |
|------|--------|
| `tests/test_models.py` | Added `TestFactScope` (7 tests): defaults, assignment, serialization, roundtrip |
| `tests/test_fact_extractor.py` | Added `TestFactExtractorScope` (3 tests): parse reads scope, defaults, prompt contains instructions |
| `tests/test_gui_adapters.py` | Added 2 tests to `TestFactsToRows`: scope included, scope defaults |

## Key Decisions
1. **`to_condition_dict()` unchanged** — scope is metadata, not a matching condition. Tests verify it's excluded.
2. **`from_dict()` defaults scope to "rule"** — backward compatibility with existing YAML data.
3. **Scope filter applied in both GUI and CLI paths** — `rule_facts = [f for f in confirmed_facts if f.scope == "rule"]` before `filter_rules()`.
4. **Prompt expanded significantly** — explicit allow/deny lists for rule vs context classification, prohibition of GUIDs/resource names in rule-scope facts.
