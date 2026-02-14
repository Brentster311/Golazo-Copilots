# EES-00014 — Test Cases

## Existing Tests to Update (remove `because`/`root_cause` references)

### TC-01: Update test_models.py
- Remove `because=` kwargs from Rule construction
- Remove `root_cause=` from LLMResponse construction if present
- Verify `Rule.to_dict()` no longer emits `because`

### TC-02: Update test_fact_extractor.py
- Remove `"because"` from all `submit_rule` tool call args
- Remove `set_root_cause` tool calls from mock responses
- Remove assertions on `result.root_cause`
- Remove `test_missing_because_rejected` and `test_empty_because_rejected` tests (no longer applicable)
- Update status callback tests that reference `set_root_cause` label

### TC-03: Update test_gui_adapters.py
- Remove `because=` from Rule construction in adapter tests
- Verify `rules_to_rows()` output no longer contains `"because"` key

### TC-04: Update test_yaml_store.py
- Remove `because=` from Rule construction
- Remove `root_cause_identified=` from Incident construction if `root_cause_identified` is being removed (check scope)
- Verify round-trip still works with remaining fields

### TC-05: Update test_main.py
- Remove `because=` from Rule construction
- Remove `root_cause=` from LLMResponse construction
- Remove/update `_confirm_root_cause` tests if function is removed
- Remove `set_root_cause` references from mock data

## New Validation Tests

### TC-06: Rule.from_dict ignores old `because` field
- Input: dict with `"because": "old explanation"`
- Expected: Rule loads without error, no `because` attribute

### TC-07: submit_rule without `because` accepted
- Verify `submit_rule` tool schema does not include `because`
- Verify a valid rule submission without `because` is accepted

## Pass Criterion
- All tests pass (count should be ~260+ after removing `because`-specific tests)
