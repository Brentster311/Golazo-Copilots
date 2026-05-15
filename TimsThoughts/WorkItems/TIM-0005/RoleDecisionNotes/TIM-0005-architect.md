# TIM-0005 — Architect Decision Notes

## Architectural Assessment

New `.agent.md` files in `.github/agents/`. No architectural concerns.

## Key Decisions

- **Location confirmed**: `.github/agents/` — workspace-scoped, coexists safely with `golazo-copilot/` subfolder
- **Tools confirmed**: `[read, search]` — minimal, appropriate for read-only reviewer personas
- **Naming**: lowercase-kebab-case filenames + human-readable `name:` field in frontmatter
- **No cross-agent dependencies**: Each agent is independent; no orchestration or handoff between author agents

## Security

No concerns. No credentials, no personal data, no external service integration.

## Capability Impact

Zero. Confirmed via `golazo_capabilities`.
