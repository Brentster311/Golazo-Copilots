# LLM-0012 — Quality Assurance Decision Notes

## Review Summary
Design approved with minor clarifications (api_version default, model vs deployment name mapping). No blockers identified.

## Test Strategy Rationale
- 13 test cases covering all 7 acceptance criteria
- Heavy reliance on mocks for unit tests (Azure SDK mocking) — no real Azure calls in CI
- One live integration test marked `@pytest.mark.live`
- Edge cases: zero deployments, 403 access denied, subscription errors, non-OpenAI resources
- TC-10 validates the end-to-end contract: discovery output → LLMClient → working completion
