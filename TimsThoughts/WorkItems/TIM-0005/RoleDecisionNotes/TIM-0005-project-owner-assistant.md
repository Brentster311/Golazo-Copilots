# TIM-0005 — Project Owner Assistant Decision Notes

## Scope Decision: 12 Authors

The Agile/ directory contains the following author-specific files used as source:
1. `alshalloway.md` → Al Shalloway
2. `ChristopherAlexander.md` → Christopher Alexander
3. `danielpink.md` → Daniel Pink
4. `DonaldReineertson.md` → Donald Reinertsen
5. `EricRies.md` → Eric Ries
6. `Influencer-Grenny.md` → Joseph Grenny (Influencer framework)
7. `kentBeck.md` → Kent Beck
8. `Leffingwell.md` → Dean Leffingwell
9. `marypoppendeick.md` → Mary Poppendieck
10. `SimonSinek.md` → Simon Sinek
11. `Starfish.md` → Brafman & Beckstrom
12. `StephenCovey.md` → Stephen Covey

Excluded non-author files: comparison.md, HBR-AWARE-Summary.md, Insights.md, My-View-Summary.md, more golazo notes.md, more observations.md, Thinking.MD, Value Stream Mapping.md, Tim-PPT analysis files, TimsDocs-Summary-APA.md, Offsite-Agenda.

## Technology Decision: Custom Agents (.agent.md)

The right VS Code primitive is **Custom Agents** (`.agent.md` in `.github/agents/`):
- Appear in agent picker → user can select by name
- Persistent personas (not single-shot prompts)
- Can be invoked as subagents by Golazo Copilot
- `read, search` tools = sufficient for a read-only reviewer

The alternative (`.prompt.md`) was rejected: prompts are single-task, not persistent personas.

## Scope Validation

5 ACs at the limit — borderline. Kept as one work item because:
- All 12 agents share identical structure (only content changes)
- A partial delivery (some agents but not all) would be inconsistent
- Single commit of all 12 is coherent and testable

## Must-Ask Checklist Resolution
- **Interface type**: VS Code agent picker — established by the "skills" framing and the existing Golazo Copilot agent infrastructure in this workspace
- **Target platform**: Windows / VS Code (workspace-scoped `.github/agents/`)
- **Data persistence**: Files in `.github/agents/` committed to git
