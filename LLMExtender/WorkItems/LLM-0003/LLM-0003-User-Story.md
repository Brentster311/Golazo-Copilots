# User Story: LLM-0003

**Status**: IMPLEMENTED

**Decomposed from:** `llm-extender-core` — original story had 23 acceptance criteria across 3 domains (LLM Client, Config, Auth). Split into 3 independent vertical slices per PO role rules (max 7 AC per story).

---

**User Story**

- **Title:** Pluggable Auth Manager with Multiple Credential Strategies
- **As a:** Python developer using the LLM Extender library
- **I want:** A pluggable authentication manager that resolves credentials at runtime through different strategies (environment variable, Azure MSI, custom callback), without ever persisting or logging secrets
- **So that:** I can connect to LLM providers using the auth mechanism appropriate for my deployment environment (local dev, CI, Azure cloud, etc.) while maintaining strict secret hygiene

- **Out of scope:**
  - LLM client / provider abstraction (see LLM-0001)
  - Config file persistence (see LLM-0002 — auth strategy *type* is stored in config, not credentials)
  - OAuth / OIDC flows
  - Key rotation
  - Web server, CLI, or UI of any kind

- **Assumptions:**
  - **Assumption (explicit):** This is a Python library (API only).
  - **Assumption (explicit):** Auth strategies are selected via the config's `auth_strategy` field (e.g., `"env_var"`, `"msi"`, `"callback"`).
  - **Assumption (explicit):** `ManagedIdentityAuth` uses the `azure-identity` library (optional dependency).
  - **Assumption (explicit):** `CallbackAuth` accepts any callable `() -> str` that returns a credential string.
  - **Assumption (explicit):** "Never persisted or logged" means: not written to disk, not in `__repr__`/`__str__`, not emitted at any Python logging level.
  - **Assumption (explicit):** Python 3.10+ minimum. Cross-platform.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] An abstract base class / protocol defines the auth strategy interface with a `resolve() -> str` method
  - [ ] `EnvVarAuth` strategy resolves an API key from a named environment variable
  - [ ] `ManagedIdentityAuth` strategy acquires a token via Azure MSI
  - [ ] `CallbackAuth` strategy accepts a user-supplied callable that returns a credential
  - [ ] Auth credentials are never persisted to disk or logged at any log level
  - [ ] `repr()` and `str()` of auth objects do NOT expose secret values
  - [ ] Missing or invalid credentials raise a clear, descriptive error

- **Non-functional requirements:**
  - **Security:** No secret/key/token value may be written to disk, logged, or included in `__repr__`/`__str__` output under any circumstances
  - Type hints on all public API surfaces
  - The package must be installable via `pip install -e .`

- **Telemetry / metrics expected:**
  - None for initial version

- **Rollout / rollback notes:**
  - New library — no rollback concerns.
