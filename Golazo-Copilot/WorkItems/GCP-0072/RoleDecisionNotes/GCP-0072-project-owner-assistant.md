# GCP-0072 Project Owner Assistant Decision Notes

## Request Interpretation

The requested user-visible outcome is a bootstrap flow that installs the first packaged Golazo skill, `golazo-ado-sync`, into a GitHub Copilot-supported workspace or user location after the user confirms its packaged configuration defaults.

## Confirmed Product Decisions

- Interface: Extend the existing MCP `golazo_bootstrap` workflow.
- Platforms: Support Windows, macOS, and Linux.
- Persistence: Store confirmed configuration with the installed skill at the selected scope.
- Workspace destination: `.github/skills/golazo-ado-sync/`.
- User destination: `~/.copilot/skills/golazo-ado-sync/`.

## Scope Decisions

- This is one vertical slice because confirming configuration and installing the resulting skill are successive steps in one bootstrap interaction.
- Only `golazo-ado-sync` is included. A generalized catalog or multi-skill selection experience is deferred until another packaged skill creates a concrete need.
- Azure DevOps authentication and live board validation remain runtime responsibilities of the skill, not bootstrap responsibilities.
- Existing skill installations follow bootstrap's established force/no-force overwrite semantics to avoid a second conflict policy.

## Evidence Reviewed

- The packaged `golazo-ado-sync/SKILL.md` contains the default organization, project, team, board, work item, area, iteration, assignee, and board-field configuration.
- Current bootstrap supports Workspace and User scopes for orchestrator instructions but does not install skills.
- GitHub Copilot skill conventions define `.github/skills/<name>/` for workspace scope and `~/.copilot/skills/<name>/` for personal scope.
- The capability registry currently contains only a placeholder capability, so no registered production capability changes the story scope.

## Risks And Guardrails

- Configuration must be represented structurally during confirmation and rendering so values containing backslashes remain intact.
- Failure must be atomic enough to avoid leaving a discoverable but incomplete skill directory.
- Bootstrap output must not expose credentials or tokens; the current defaults contain identifiers but no authentication secrets.
- Existing bootstrap callers must remain compatible.

## Closure Review

- All four acceptance criteria passed through behavior tests and built-wheel smoke validation.
- Full regression result: `522 passed, 3 skipped`.
- Built and installed package version: `5.1.0`.
- Capability registry validation passed for `bootstrap-skill-installation`.
- Project Owner authorized commit and push; implementation commit `794fe9b` is available on `origin/brentj/GCP-0072`.