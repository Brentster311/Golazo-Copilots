# GCP-0072 Review Comments

## Domain Expert Guidance

### Expertise Consulted

GitHub Copilot agent customization and Agent Skills conventions, using the VS Code bundled Agent Skills reference as the authoritative local guidance.

Azure DevOps service expertise is not required for this slice because bootstrap neither authenticates to Azure DevOps nor reads or updates boards. The installed skill retains responsibility for those runtime operations.

### Recommendations

1. Install the workspace skill at `.github/skills/golazo-ado-sync/SKILL.md` and the personal skill at `~/.copilot/skills/golazo-ado-sync/SKILL.md`.
2. Preserve the exact folder/frontmatter name match: `golazo-ado-sync`.
3. Preserve a meaningful `description`, valid YAML delimiters, and current invocation flags so the skill remains discoverable and user-invocable.
4. Copy the entire packaged skill directory, not only `SKILL.md`, so future scripts, references, and assets remain self-contained.
5. Keep references relative to `SKILL.md`; do not render machine-specific absolute paths into the installed skill.
6. Treat the packaged skill as immutable input and render configuration into a destination copy.

### Risks And Constraints

- A valid file at the wrong root is not discoverable.
- A folder/frontmatter name mismatch or malformed YAML can fail silently.
- Copying only the current Markdown file creates a migration trap when bundled resources are added later.
- The user-level destination must derive from the active user's home directory, not the workspace or process current directory.

### Suggested Design Clarifications

- Define installation as a recursive package-resource copy with a controlled transformation of the configuration section.
- Validate the destination candidate before making it discoverable at the final path.
- Limit installation to `full` bootstrap mode; `orchestrator-only` should retain its narrow promise unless the user story is expanded later.

## Quality Assurance Review

### Findings

1. **Configuration confirmation boundary:** An MCP tool cannot itself pause for interactive input. The design must expose defaults in tool metadata/orchestrator guidance and accept an explicit confirmed configuration in the eventual bootstrap invocation. Calling bootstrap with installation enabled but no confirmation must fail clearly.
2. **Default completeness:** Tests need a canonical expected key/value set so adding, removing, or renaming a packaged default cannot silently desynchronize the confirmation contract.
3. **Atomic destination behavior:** Validation must happen before destination mutation. For force replacement, a failed render or staged copy must preserve the prior installed skill.
4. **Result semantics:** Skill paths should be reported distinctly from orchestrator and role paths so callers can identify what was installed or skipped without parsing messages.
5. **Mode behavior:** `orchestrator-only` must reject or ignore skill-install inputs deterministically. QA recommends rejecting the contradictory request with an actionable error.

### Testability Assessment

All four acceptance criteria are testable with temporary directories, monkeypatched home resolution, package-resource fixtures, and direct inspection of the generated skill tree. No live Azure DevOps calls, credentials, or platform-specific machines are required.

### Approval

Approved for architecture after the design incorporates explicit confirmation state, a canonical configuration schema, atomic replacement semantics, and deterministic `orchestrator-only` behavior.

## Architect Notes

### Decision

Approved with the contracts and boundaries below. These decisions resolve existing design questions without changing the user story.

### Public Input Contract

Add optional `golazo_bootstrap` inputs while preserving all current defaults:

- `install_ado_sync_skill: boolean = false`
- `ado_sync_config_confirmed: boolean = false`
- `ado_sync_config: object | null = null`

When installation is false, the new fields have no side effects. When installation is true:

1. `mode` must be `full`.
2. `ado_sync_config_confirmed` must be true.
3. The effective configuration must contain every required key.
4. Omitted `ado_sync_config` means the user explicitly confirmed the complete packaged defaults.
5. A supplied object is merged over defaults, validated as the complete effective configuration, and reported as customized when any effective value differs.

Required configuration keys use snake_case API names: `organization`, `project`, `team`, `board`, `work_item_type`, `area`, `iteration`, `assignee`, `planned_swimlane_field`, `board_column_field`, and `board_done_field`.

### Default And Rendering Boundary

- Add a structured package resource beside the skill as the canonical machine-readable default set.
- Keep packaged `SKILL.md` complete and human-readable; tests enforce exact parity between its configuration section and the structured defaults.
- Render only the bounded configuration section in a staged copy of the full packaged skill tree.
- Parse defaults with YAML and serialize Markdown bullet values through a dedicated renderer. Do not use broad ad hoc replacements across the document.
- Validate YAML frontmatter, folder/name equality, all required configuration values, and relative bundled-resource integrity before destination replacement.

### Path And File Contracts

- Add skill path resolvers beside current orchestrator path resolvers.
- Workspace: `<workspace>/.github/skills/golazo-ado-sync/`.
- User: `<home>/.copilot/skills/golazo-ado-sync/`.
- Use `pathlib.Path.home()` behind a small resolver boundary that tests can monkeypatch.
- Stage under the destination parent, then rename/replace only after validation. A failed forced replacement must retain the prior destination.

### Result Contract

Add a `skills` result collection containing `name`, `scope`, `target_path`, `status` (`created`, `replaced`, or `skipped`), and `configuration_source` (`defaults` or `customized`). Keep existing `scope`, `target_path`, `files_created`, and `files_skipped` fields unchanged for compatibility. Formatter output may summarize the additive collection but must not print the full configuration.

### Integration Points

- `tools/golazo_bootstrap.py`: validation, orchestration, staged copy, and result data.
- `dispatch/paths.py`: supported skill destination resolution.
- `dispatch/registry.py`: MCP JSON schema and visible packaged defaults.
- `handlers/tools.py`: canonical dispatch argument mapping.
- `formatters/results.py`: additive skill outcome formatting.
- `bootstrap-instructions.md`: require presenting defaults and obtaining confirmation before enabling installation.
- `server.py`: retain compatibility wrappers in sync with modular schema/dispatch behavior until the legacy surface is removed separately.

### Security And Privacy

- No new authentication boundary or dependency is introduced.
- Configuration values are non-secret identifiers, but bootstrap must never accept, store, or echo access tokens or credentials.
- Errors may name invalid fields but must not dump the complete submitted object.
- User-scope writes are limited to the resolved skill directory; reject path-like skill names or caller-controlled destinations.

### Resilience And Performance

- The skill tree is small; recursive copy cost is negligible and no caching is warranted.
- Atomic staging isolates failures and makes retries safe.
- No network calls occur, so no retry or timeout policy is needed.
- Use only Python standard-library file operations plus existing PyYAML; no dependency addition is justified.

### Explicit Default Questions Resolved

- `shutil.copytree` defaults alone do not guarantee safe replacement; stage and replace explicitly.
- `Path.home()` is the expected active-user root and must be injectable in tests.
- UTF-8 is mandatory for Markdown and YAML reads/writes rather than relying on platform encoding.
- Existing destinations skip by default; only `force=True` permits replacement.