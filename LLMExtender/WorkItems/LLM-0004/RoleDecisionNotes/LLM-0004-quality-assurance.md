# LLM-0004 — Quality Assurance Notes

## Date: 2026-02-07

## Design Review Findings
- Design doc is clear and actionable. No blocking issues.
- D2 (shared base) is well-motivated by PO — shared HTTP plumbing is ~60 lines, subclasses are ~15 lines each.
- Refactor of existing `OpenAIProvider` carries regression risk — mitigated by 30 existing tests.

## Test Strategy
- 21 test cases covering all 7 acceptance criteria plus design decisions D2/D3.
- Tests use `respx` for HTTP mocking (consistent with LLM-0001 test patterns).
- TC-20 is a meta-test: "existing tests still pass" — validated by running full suite after refactor.
- No integration tests against live Azure (would require credentials in CI). Manual verification by PO post-implementation.

## Decisions
- Split tests across 3 files: `test_azure_openai_provider.py` (18), `test_base_openai_provider.py` (2), config addition (1).
- Payload test (TC-14) explicitly verifies `model` key is absent — this is the key behavioral difference from OpenAI.
