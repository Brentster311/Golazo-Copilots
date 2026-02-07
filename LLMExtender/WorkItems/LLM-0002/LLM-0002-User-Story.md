# User Story: LLM-0002

**Status**: CANCELLED

**Cancellation Reason:** PO decision — persistent config (JSON/YAML load/save) removed from scope. All remaining value (LLMConfig dataclass, repr safety) was already delivered in LLM-0001. Config is constructor-only.

**Decomposed from:** `llm-extender-core` — original story had 23 acceptance criteria across 3 domains (LLM Client, Config, Auth). Split into 3 independent vertical slices per PO role rules (max 7 AC per story).

---

**User Story**

- **Title:** Configuration Management with JSON/YAML Persistence
- **As a:** Python developer using the LLM Extender library
- **I want:** A configuration system that can be built programmatically or loaded from a JSON/YAML file, and saved back to disk without ever persisting security artifacts
- **So that:** I can manage LLM settings in human-readable config files, share them safely across environments, and never risk leaking secrets to disk

- **Out of scope:**
  - LLM client / provider abstraction (see LLM-0001)
  - Auth credential resolution (see LLM-0003 — config only stores the auth *strategy type*, not credentials)
  - Encryption of config files
  - Config file watching / hot-reload
  - Web server, CLI, or UI of any kind

- **Assumptions:**
  - **Assumption (explicit):** This is a Python library (API only).
  - **Assumption (explicit):** Config is implemented as a dataclass internally.
  - **Assumption (explicit):** Config fields include: provider name, model name, auth strategy type, endpoint URL, and optional provider-specific parameters.
  - **Assumption (explicit):** "Security artifacts" = API keys, tokens, secrets, passwords, credentials. These are NEVER written to disk.
  - **Assumption (explicit):** YAML support requires `pyyaml` as an optional dependency.
  - **Assumption (explicit):** Python 3.10+ minimum. Cross-platform.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] A `LLMConfig` dataclass exists with fields for provider, model, auth strategy type, and endpoint
  - [ ] Config can be loaded from a JSON file via a class method (e.g., `LLMConfig.from_json(path)`)
  - [ ] Config can be loaded from a YAML file via a class method (e.g., `LLMConfig.from_yaml(path)`)
  - [ ] Config can be saved to disk as JSON or YAML via instance methods
  - [ ] Persisted config files NEVER contain security artifacts (keys, tokens, secrets)
  - [ ] `repr()` and `str()` of config objects do NOT expose secret values
  - [ ] Loading a config file that contains a known secret field raises an error or strips it with a warning

- **Non-functional requirements:**
  - Config persistence format must be human-readable (JSON or YAML)
  - Type hints on all public API surfaces
  - The package must be installable via `pip install -e .`

- **Telemetry / metrics expected:**
  - None for initial version

- **Rollout / rollback notes:**
  - New library — no rollback concerns.
