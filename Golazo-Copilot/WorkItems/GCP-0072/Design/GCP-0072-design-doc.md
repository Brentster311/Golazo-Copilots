# GCP-0072 Design: Bootstrap Installation of Golazo ADO Sync

## Summary

Extend the existing `golazo_bootstrap` MCP workflow so a user can review the packaged `golazo-ado-sync` configuration defaults, confirm or replace them, and install the resulting skill at workspace or user scope. The installed skill must use GitHub Copilot's supported skill locations and remain valid across Windows, macOS, and Linux.

## Problem Statement

Golazo Copilot packages its first skill under `golazo_copilot/skills/golazo-ado-sync`, but bootstrap does not copy that resource into a location where GitHub Copilot discovers skills. Users would need to know the supported paths and manually edit organization-specific configuration embedded in `SKILL.md`. This is error-prone and makes package installation incomplete from the user's perspective.

## Business Case

### Why Now

The first packaged skill now exists, so bootstrap needs a supported installation path before users can reliably consume it.

### Impact

- Removes manual skill placement and configuration editing.
- Makes installation scope explicit and repeatable.
- Establishes a pattern for future packaged skills without introducing a generalized catalog prematurely.

### KPIs

- Both supported scopes produce a discoverable, valid skill in automated tests.
- All packaged defaults are represented in the confirmation contract.
- Failed validation or writes leave no partial destination.
- Existing bootstrap calls continue to pass unchanged.

## Stakeholders

- Golazo Copilot users bootstrapping workspaces.
- Maintainers of packaged Golazo skills.
- Teams relying on the Azure DevOps synchronization defaults.

## Functional Requirements

1. The bootstrap interaction exposes all configuration values from the packaged `golazo-ado-sync` skill as defaults before installation.
2. The user can accept all defaults or provide replacement values through the existing MCP bootstrap workflow.
3. Workspace scope installs to `<workspace>/.github/skills/golazo-ado-sync/`.
4. User scope installs to `~/.copilot/skills/golazo-ado-sync/`.
5. The installed `SKILL.md` retains valid frontmatter and contains the confirmed configuration.
6. Invalid or incomplete configuration fails before the destination is committed.
7. Existing destinations are skipped unless `force` permits replacement.
8. The result reports scope, resolved destination, created/skipped files, and whether defaults or customized values were used.

## Non-Functional Requirements

- Use `pathlib` and home-directory resolution without platform-specific string assembly.
- Preserve backward compatibility for existing bootstrap callers.
- Do not write credentials or access tokens.
- Keep packaged defaults immutable during installation.
- Avoid partial installations through validate-before-write and staged replacement where needed.
- Maintain more than 70% focused coverage for changed Python modules.

## Proposed Approach

1. Model the ADO Sync configuration as structured bootstrap input with packaged defaults.
2. Extend the MCP tool schema and orchestrator guidance so Copilot presents those values for confirmation before invoking installation.
3. Add scope-aware skill path resolution alongside the existing orchestrator path helpers.
4. Load the packaged skill directory through package-resource APIs, render confirmed configuration into the destination copy, validate the result, and then commit it to the selected destination.
5. Return structured installation details through the existing bootstrap result and formatter paths.
6. Keep skill installation opt-in for API compatibility; the conversational bootstrap guidance should offer it as part of the normal full bootstrap flow.

## Alternatives Considered

### Install Unconditionally With Fixed Values

Rejected because it prevents confirmation and makes organization-specific defaults appear universal.

### Require Manual Copying

Rejected because users must know discovery paths and can create malformed skill frontmatter or configuration.

### Create A Separate Skill Installer Tool

Deferred. Bootstrap is the requested interface and already owns scope selection and package scaffolding. A separate catalog becomes useful only when multiple independently managed skills exist.

### Store Configuration Outside The Skill

Rejected for this slice because the user selected persistence beside the installed skill, and no runtime external configuration contract currently exists.

## Risks And Mitigations

- **Configuration drift:** Keep one structured default definition and test it against every packaged field.
- **Malformed Markdown or YAML:** Render only the configuration section and validate frontmatter and required values before installation.
- **Partial replacement:** Stage content before replacing an existing destination.
- **Home path differences:** Resolve with standard path APIs and inject/mock the home path in tests.
- **Breaking current callers:** Add optional inputs with defaults preserving current behavior.
- **Accidental secret capture:** Treat configuration as non-secret metadata and reject or redact credential-like runtime data from result output.

## Open Questions

- Architecture should decide whether confirmed configuration is represented as one typed object or individual MCP arguments.
- Architecture should decide whether `orchestrator-only` mode may install a skill or whether skill installation is limited to `full` mode.

## Dependencies

- Python package-resource support for the bundled skill directory.
- Existing bootstrap scope normalization and force semantics.
- GitHub Copilot skill locations: `.github/skills/<name>/` and `~/.copilot/skills/<name>/`.

## Migration, Rollout, And Rollback

- Add packaged skill resources and optional bootstrap fields in a backward-compatible release.
- Exercise workspace and user installations in isolated temporary paths before publishing.
- Existing installations are not migrated or removed automatically.
- Rollback disables/removes the optional installation behavior while leaving previously installed skills untouched.

## Observability Plan

No external telemetry is added. Bootstrap returns deterministic fields for selected scope, destination path, created/skipped outcomes, and default/customized configuration source. Errors identify the failed validation or file operation without exposing tokens or credentials.

## Test Strategy Summary

- Unit-test scope normalization and destination resolution for workspace and mocked Windows/POSIX home paths.
- Verify all packaged defaults are exposed and persist unchanged when accepted.
- Verify customized values persist without changing package resources.
- Verify no-force skip, force replacement, invalid configuration, and simulated write failure behavior.
- Verify generated `SKILL.md` frontmatter and folder-name contract.
- Run existing bootstrap and server-dispatch regression suites with coverage for changed modules.