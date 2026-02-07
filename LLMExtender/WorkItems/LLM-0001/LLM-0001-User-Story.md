# User Story: LLM-0001

**Status**: IMPLEMENTED

**Decomposed from:** `llm-extender-core` — original story had 23 acceptance criteria across 3 domains (LLM Client, Config, Auth). Split into 3 independent vertical slices per PO role rules (max 7 AC per story).

---

**User Story**

- **Title:** Provider-Abstracted LLM Client with Sync/Async Support
- **As a:** Python developer integrating LLM capabilities into my application
- **I want:** A provider-agnostic `LLMClient` class that I can instantiate with a config object, and use to make synchronous or asynchronous completion calls through a unified interface
- **So that:** I can switch between LLM providers by changing config alone, without modifying any calling code

- **Out of scope:**
  - Auth manager / credential resolution (see LLM-0003)
  - Config persistence to disk (see LLM-0002)
  - Streaming responses
  - Prompt templating or chaining
  - Retry / rate-limiting logic
  - Web server, CLI, or UI of any kind

- **Assumptions:**
  - **Assumption (explicit):** This is a Python library (API only) — no HTTP server, no CLI.
  - **Assumption (explicit):** For this story, the config object accepts an `api_key` string directly. Auth manager integration (LLM-0003) replaces this with strategy-based credential resolution.
  - **Assumption (explicit):** Initial concrete provider: OpenAI-compatible API (covers OpenAI, Together, Groq, LM Studio, etc.).
  - **Assumption (explicit):** Python 3.10+ minimum.
  - **Assumption (explicit):** Cross-platform (Windows, Mac, Linux).
  - **Assumption (explicit):** Target user: technical (Python developers).

- **Acceptance Criteria (bulleted, testable):**
  - [ ] A public `LLMClient` class exists that accepts a config object in its constructor
  - [ ] `LLMClient` exposes a synchronous `complete(prompt) -> str` method
  - [ ] `LLMClient` exposes an asynchronous `acomplete(prompt) -> str` method
  - [ ] An abstract base class / protocol defines the provider interface
  - [ ] At least one concrete provider implementation exists (OpenAI-compatible)
  - [ ] Passing an unsupported provider name raises a clear, descriptive error
  - [ ] All public classes and methods have docstrings and type hints

- **Non-functional requirements:**
  - The abstraction layer must add negligible overhead (< 1ms) on top of provider latency
  - The package must be installable via `pip install -e .`
  - Type hints on all public API surfaces

- **Telemetry / metrics expected:**
  - None for initial version

- **Rollout / rollback notes:**
  - New library — no rollback concerns. Versioned via `pyproject.toml`.
