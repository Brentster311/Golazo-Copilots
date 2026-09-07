# GCP-0072 User Story

**Status**: IN PROGRESS

**User Story**
- Title: Install Golazo ADO Sync skill during bootstrap
- As a: Golazo Copilot user
- I want: the existing MCP bootstrap workflow to confirm the packaged Golazo ADO Sync defaults and install the configured skill at my selected workspace or user scope
- So that: the skill is discoverable by GitHub Copilot with the correct configuration without manual file placement or editing
- Out of scope: Installing additional Golazo skills; changing Azure DevOps synchronization behavior; validating Azure DevOps credentials or remote board configuration during bootstrap; adding a separate CLI or GUI.
- Assumptions:
  - **Assumption (explicit):** Bootstrap presents the configuration through the existing conversational MCP workflow, and confirmed values are passed to the bootstrap tool rather than adding terminal prompts.
  - **Assumption (explicit):** The current `Fixed Configuration` values in the packaged `golazo-ado-sync/SKILL.md` are the initial defaults.
  - **Assumption (explicit):** Workspace installation targets `.github/skills/golazo-ado-sync/`; user installation targets `~/.copilot/skills/golazo-ado-sync/` on Windows, macOS, and Linux.
  - **Assumption (explicit):** Confirmed configuration is persisted in the installed skill files, while the packaged source defaults remain unchanged.
- Acceptance Criteria (bulleted, testable):
  - Bootstrap displays every packaged Golazo ADO Sync configuration default and requires user confirmation or replacement values before installing the skill.
  - With Workspace scope selected, bootstrap installs a valid `golazo-ado-sync` skill under `.github/skills/golazo-ado-sync/` in the requested workspace and persists the confirmed configuration there.
  - With User scope selected, bootstrap installs the same configured skill under `~/.copilot/skills/golazo-ado-sync/`, resolving the home directory correctly on Windows, macOS, and Linux.
  - Bootstrap reports the selected scope, resolved destination, created or skipped files, and whether default or customized configuration was installed; invalid or incomplete configuration fails without a partial skill installation.
- Non-functional requirements: Preserve valid YAML frontmatter and the `golazo-ado-sync` folder/name match; never persist credentials or access tokens; use platform-independent path APIs; do not overwrite an existing installed skill unless the existing bootstrap force behavior explicitly permits it; maintain focused automated coverage above 70% for changed Python modules.
- Telemetry / metrics expected: No external telemetry. The bootstrap result provides deterministic operation details for scope, destination, file outcomes, and configuration source without exposing configuration secrets.
- Rollout / rollback notes: Ship the skill as a package resource and extend bootstrap compatibly so existing callers retain current behavior unless skill installation is requested. Roll back by removing the bootstrap skill-install option and packaged installation behavior; do not automatically delete previously installed user or workspace skill files.