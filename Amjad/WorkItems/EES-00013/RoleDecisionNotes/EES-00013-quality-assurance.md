# EES-00013 QA Decision Notes

## Key Decisions

### 1. 27 test cases covering all acceptance criteria
- Every AC has at least one test. Several have multiple (validation edge cases).
- Test IDs TC-01 through TC-27.

### 2. Tool handler tests are unit-level
- TC-13/14/15/23/24 test handler functions directly, not through the full loop.
- This isolates validation logic from mock complexity.

### 3. Full loop tests use mock response sequences
- TC-01/02/03/10/11 simulate multi-turn by returning different mock responses per `.create()` call using `side_effect=[...]`.
- This tests the actual loop logic without live LLM calls.

### 4. Existing auth test preserved (TC-21)
- Auth test from EES-00004 is unchanged — constructor behavior isn't affected.

### 5. Old `_parse_response` tests become obsolete
- `TestFactExtractorScope.test_parse_response_*` and `TestFactExtractorRuleout.*` test `_parse_response()` which is being removed.
- These test classes will be replaced by the tool handler tests.
- Old test fixtures (`mock_llm_response.json`, `mock_llm_empty.json`) kept in repo but no longer referenced.

### 6. Review comments addressed in test cases
- C-4 (instance default) → TC-23
- C-5 (unknown tool) → TC-12
- C-6 (multiple set_root_cause) → TC-16
- C-7 (old fixtures) → noted as obsolete, new fixtures for tool-call mocking

### 7. Capability impact acknowledged
- `fact-extraction` directly affected (being refactored)
- `cli-orchestration` and `gui` transitively affected but use `extract()` API which is unchanged
- No additional tests needed for CLI/GUI — they're covered by `extract()` return type test (TC-20)
