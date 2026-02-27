# SFI-033 — Quality Assurance Decision Notes

## Review Summary
Design is clear, feasible, and well-scoped. Updated to include permanent LLM module removal. No blocking issues.

## Key QA Decisions
1. **Test the stub** — `_launch_llm_analysis` stub must be tested to confirm it shows messagebox and does NOT import any LLM modules.
2. **Test deletions** — Verify `llm_client.py`, `llm_storage.py`, and their test files are actually gone (not just unreferenced).
3. **AsyncBridge testable in isolation** — Unit-testable without Tkinter; exercises the core async-to-sync bridge.
4. **CopilotPanel widget tests** — Structure tests only (widget existence); actual SDK integration is manual-test territory.
5. **Dependency check test** — Panel must gracefully handle missing `github-copilot-sdk` by showing instructions.
6. **Deleted test files**: `test_llm_client.py`, `test_llm_storage.py`, `test_sfi_025.py` — these test removed code and are deleted with their modules.
7. **Capability registry impact** — `reporter-web-app` flagged but is a separate Streamlit app, not affected by Tkinter changes.
