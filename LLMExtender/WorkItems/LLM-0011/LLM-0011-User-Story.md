# LLM-0011: Public Context-Prompt API for Pre-Fetched Content

## Status: IMPLEMENTED

## User Story

- **Title:** Public Context-Prompt API for Pre-Fetched Content
- **As a:** developer using LLM Extender who has fetched content outside the library (e.g., via CDP, custom scraper, or file read)
- **I want:** a public method on `LLMClient` to send pre-fetched content as context along with a prompt, and a public `build_context_prompt` utility function
- **So that:** I don't have to import private `_build_context_prompt` or manually construct the augmented prompt format

- **Out of scope:**
  - Changing how `complete_with_url` works internally — it continues to fetch + prompt in one call
  - Multi-document context (multiple URLs/sources in one prompt) — single source only for now
  - Prompt templates or customizable prompt formats — uses the existing format

- **Assumptions:**
  - **Assumption (explicit):** Python library feature — new public API surface.
  - **Assumption (explicit):** The existing `_build_context_prompt` format (`"Content from {url}:\n\n{content}\n\n{prompt}"`) is the canonical format and should be preserved.
  - **Assumption (explicit):** `build_context_prompt` is exported from `llm_extender` top-level package.

- **Acceptance Criteria (bulleted, testable):**
  - `LLMClient.complete_with_context(prompt, content, source_url=None)` sends pre-fetched content + prompt to the LLM and returns the response
  - `LLMClient.acomplete_with_context(prompt, content, source_url=None)` provides the async variant
  - `build_context_prompt(url, content, prompt)` is a public function exported from `llm_extender` (renamed from `_build_context_prompt`)
  - The old private `_build_context_prompt` still works (as an alias) to avoid breaking internal callers
  - `complete_with_url` internally delegates to `complete_with_context` (DRY refactor)
  - All existing tests continue to pass unchanged

- **Non-functional requirements:**
  - No new dependencies
  - Backward compatible — `_build_context_prompt` remains importable

- **Telemetry / metrics expected:**
  - None (library, not a service)

- **Rollout / rollback notes:**
  - Additive feature — new public methods and function, no breaking changes
  - No new dependencies required
