# GCP-0072 Program Manager Decision Notes

## Decisions

- Keep confirmation and installation in one bootstrap user journey.
- Make skill installation opt-in at the tool API boundary to preserve existing callers.
- Use the selected bootstrap scope for both orchestrator and skill placement while resolving each artifact through its own standard path.
- Preserve confirmed configuration in the installed skill rather than changing packaged resources.
- Apply existing `force` semantics to installation conflicts.

## Business And Operational Rationale

The packaged skill has no user value until Copilot can discover it. Integrating installation with bootstrap minimizes setup steps and gives users one place to choose scope and validate defaults. Atomic failure behavior matters because a partially written `SKILL.md` could be silently ignored or, worse, discovered with incomplete synchronization instructions.

## Scope Guardrails

- No multi-skill catalog.
- No Azure DevOps network calls during bootstrap.
- No CLI prompt implementation.
- No deletion or migration of existing installed skills.
- No change to the skill's runtime synchronization lifecycle.

## Architecture Questions

- Choose the structured configuration input shape.
- Define the rendering/validation boundary for the installed Markdown.
- Decide how skill installation interacts with `orchestrator-only` mode.