# TIM-0005 Design Doc — Agile Thinker Reviewer Agents

## Summary

Create 12 VS Code custom agent files (`.agent.md`) — one per Agile thinker already analyzed in `Agile/*.md` — so that each author's critical perspective is available on demand as an invokable reviewer persona during OFP response writing.

## Problem Statement

The OFP corpus analysis in `Agile/` contains rich, author-specific critiques of Tim's delivery thinking. Currently those perspectives are passive documents — the user must open and read them manually to recall a given thinker's angle. Converting each analysis into a VS Code custom agent makes these perspectives interactive and on-demand: the user simply switches to a named agent and asks "review what I've written" or "what would Kent Beck say about this section?"

## Business Case

| | |
|---|---|
| **Why now** | TIM-0004 created OFP_Delivery.md. Writing the actual OFP response (TIM-0006+) starts next. Having all 12 reviewer agents ready before that work begins means each response section can be tested against multiple thinker lenses before being finalized. |
| **Impact** | Transforms 12 static analysis files into active, conversational reviewers available throughout the response-writing phase |
| **KPI** | All 12 agents appear in VS Code agent picker; each produces on-point review commentary when invoked |

## Stakeholders

- **Author**: The person writing the OFP response — primary beneficiary
- **Golazo Copilot**: Orchestrator that can invoke these agents as subagents for structured reviews

## Functional Requirements

1. `.github/agents/` directory exists in workspace root
2. 12 `.agent.md` files, named by author (e.g., `simon-sinek.agent.md`, `kent-beck.agent.md`)
3. Each file: valid YAML frontmatter (`name`, `description`, `tools`, `user-invocable: true`)
4. `description` includes author name + trigger phrases for discoverability
5. Body: first-person author voice; key questions, concerns, and frameworks from Agile/*.md; concise enough to be effective in context
6. Tools: `[read, search]` — read-only reviewers

## Non-Functional Requirements

- Each agent body: ~200–400 words — delivers the author's sharpest, most distinctive questions without verbatim-copying the entire analysis
- YAML frontmatter: no unescaped colons (quoted descriptions); spaces not tabs; `name` matches intent
- Agent names displayed in picker must be recognizable to the user (real author names, not slugs)

## Agent Manifest

| Agent File | Author | Source File |
|---|---|---|
| `al-shalloway.agent.md` | Al Shalloway | Agile/alshalloway.md |
| `christopher-alexander.agent.md` | Christopher Alexander | Agile/ChristopherAlexander.md |
| `daniel-pink.agent.md` | Daniel Pink | Agile/danielpink.md |
| `donald-reinertsen.agent.md` | Donald Reinertsen | Agile/DonaldReineertson.md |
| `eric-ries.agent.md` | Eric Ries | Agile/EricRies.md |
| `joseph-grenny.agent.md` | Joseph Grenny (Influencer) | Agile/Influencer-Grenny.md |
| `kent-beck.agent.md` | Kent Beck | Agile/kentBeck.md |
| `dean-leffingwell.agent.md` | Dean Leffingwell | Agile/Leffingwell.md |
| `mary-poppendieck.agent.md` | Mary Poppendieck | Agile/marypoppendeick.md |
| `simon-sinek.agent.md` | Simon Sinek | Agile/SimonSinek.md |
| `starfish-spider.agent.md` | Brafman & Beckstrom | Agile/Starfish.md |
| `stephen-covey.agent.md` | Stephen Covey | Agile/StephenCovey.md |

## Proposed Approach

1. Create `.github/agents/` directory
2. Create all 12 `.agent.md` files in one developer pass
3. Each file body: distill the author's 3–5 most distinctive questions and frameworks from the Agile/*.md source; write in first person; reference the source file as context if useful
4. Commit all 12 in a single commit

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| `.prompt.md` files | Prompts are single-shot tasks, not persistent personas; can't be asked "review this" repeatedly |
| `copilot-instructions.md` with all 12 | Always-on, not selective; would bloat every interaction |
| User-profile scope | These agents are specific to this OFP corpus; workspace scope is correct |

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| YAML frontmatter silent failures | Quote all description values; validate syntax before commit |
| Agent body too long → context waste | Hard cap ~400 words per agent body; distill, don't copy |
| Author perspective drift from source | Each body is derived directly from Agile/*.md; no invented positions |

## Dependencies

- Agile/*.md source files (all exist — no blockers)
- VS Code agent customization support (already in use via Golazo Copilot)

## Rollout / Rollback

- No code changes. Agent files are additive.
- Rollback: delete or comment out individual `.agent.md` files
- No effect on existing work items or OFP_Delivery.md

## Observability Plan

N/A — file artifacts. Manual verification via VS Code agent picker.

## Test Strategy Summary

Manual verification:
- TC-01: 12 `.agent.md` files exist in `.github/agents/`
- TC-02: Each file has valid YAML frontmatter (parseable, no syntax errors)
- TC-03: Each description contains author name + trigger phrases
- TC-04: Each body is in first-person author voice with at least 3 distinct questions/concerns
- TC-05: Git log confirms commit
