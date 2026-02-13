# EES-00006 — User Story

**Status**: IMPLEMENTED

## Related Work Items
- **Depends on:** EES-00005 (GUI Application)
- **Part of:** Expert System decomposition

---

## User Story

- **Title:** Azure OpenAI Configuration Settings in GUI
- **As a:** technical user (developer/engineer)
- **I want:** a Settings dialog in the GUI application where I can configure the Azure OpenAI endpoint, deployment name, and API version, with those settings persisted to a config file
- **So that:** I don't need to set environment variables before launching the app, and I can switch between different Azure OpenAI deployments without restarting

- **Out of scope:**
  - Authentication configuration (continues using ChainedTokenCredential)
  - CLI configuration changes (CLI continues using env vars)
  - Multi-profile/named-configuration support

- **Assumptions:**
  - **Assumption (explicit):** Settings are persisted to a YAML config file in the data directory (e.g., `data/settings.yaml`)
  - **Assumption (explicit):** GUI settings override environment variables when both are present
  - **Assumption (explicit):** The Settings dialog is accessible via File → Settings menu item
  - **Assumption (explicit):** Default values: endpoint `https://open-ai-poc.openai.azure.com/`, deployment `gpt5.2`, API version `2025-12-11`

- **Acceptance Criteria (bulleted, testable):**
  - A Settings dialog is accessible from the File menu
  - The dialog contains fields for: Azure OpenAI Endpoint, Deployment Name, and API Version
  - Clicking Save persists the values to `settings.yaml` in the data directory
  - On app launch, saved settings are loaded and used for LLM calls
  - If a setting is blank in the config, the app falls back to the corresponding environment variable
  - The current effective settings (source: config or env var) are visible in the dialog

- **Non-functional requirements:**
  - Settings file must be human-readable YAML
  - Sensitive values (endpoint URL) should not be obfuscated — this is a local desktop app

- **Telemetry / metrics expected:**
  - None

- **Rollout / rollback notes:**
  - Additive change; existing env-var workflow continues to work
  - Deleting `settings.yaml` reverts to env-var-only behavior
