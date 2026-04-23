**Status**: IMPLEMENTED

**User Story**
- **Title**: Agile Thinker Reviewer Agents — 12 Author Perspectives as VS Code Custom Agents
- **As a**: Author working on the OFP delivery response (OFP_Delivery.md and future TIM work items)
- **I want**: Each of the 12 Agile thinkers analyzed in the Agile/ corpus available as an invokable VS Code custom agent that reviews work from that author's perspective
- **So that**: At any point while writing the OFP response, I can ask a specific thinker to review what I've written and provide their perspective — grounded in how they actually approach delivery, accountability, and organizational performance

**Out of scope**:
- Modifying the source Agile/*.md files
- Creating agents for authors not in the Agile/ corpus
- Any writing or editing capabilities — agents are read-only reviewers
- The HBR-AWARE-Summary, comparison, Insights, My-View-Summary, and similar non-author-specific files

**Assumptions**:
- **Assumption (explicit)**: The 12 authors in scope are: Al Shalloway, Christopher Alexander, Daniel Pink, Donald Reinertsen, Eric Ries, Joseph Grenny (Influencer), Kent Beck, Dean Leffingwell, Mary Poppendieck, Simon Sinek, Brafman & Beckstrom (Starfish/Spider), and Stephen Covey
- **Assumption (explicit)**: The right VS Code primitive is `.agent.md` in `.github/agents/` — persistent personas that appear in the agent picker and can be invoked on demand with `read` and `search` tools
- **Assumption (explicit)**: Each agent's instructional content is derived from the corresponding Agile/*.md file in the workspace
- **Assumption (explicit)**: Agents are workspace-scoped (`.github/agents/`), not user-profile-scoped, because the context is specific to this OFP work

**Acceptance Criteria**:
- [x] `.github/agents/` directory exists containing exactly 12 `.agent.md` files — one per author
- [x] Each file has valid YAML frontmatter with a `description` that includes the author's name and trigger phrases for invocation ("review from [Author]'s perspective", "what would [Author] say")
- [x] Each agent's body accurately represents that author's critical lens and key questions as documented in the Agile/ corpus — no invented positions
- [x] Each agent is configured with `tools: [read, search]` (read-only reviewers) and `user-invocable: true`
- [x] All 12 files committed to git

## Closure

**Delivered**: 12 `.agent.md` files in `.github/agents/` — one per Agile thinker in the corpus, each in first-person author voice with 4+ distinct questions/concerns derived from the corresponding `Agile/*.md` source file.

**Commit**: `cd36286` — "TIM-0005: Agile Thinker Reviewer Agents -- 12 Author Perspectives as VS Code Custom Agents" (master, 2026-04-12)

### Acceptance Criteria Results

| AC | Criterion | Result |
|----|-----------|--------|
| AC1 | 12 `.agent.md` files in `.github/agents/` | PASS |
| AC2 | Valid YAML frontmatter with description, name, tools | PASS |
| AC3 | Body accurately represents author's lens (no invented positions) | PASS |
| AC4 | `tools: [read, search]` + `user-invocable: true` | PASS |
| AC5 | All 12 committed to git | PASS |

**Note on AC2 UX validation**: The agent picker UI display requires VS Code to load the agents at runtime. Source-based verification confirms correct YAML structure and `name` fields. Runtime agent picker confirmation should be validated by the Project Owner when next opening this workspace in VS Code.

### Agents Delivered

| Agent | Author |
|-------|--------|
| al-shalloway.agent.md | Al Shalloway |
| christopher-alexander.agent.md | Christopher Alexander |
| daniel-pink.agent.md | Daniel Pink |
| dean-leffingwell.agent.md | Dean Leffingwell |
| donald-reinertsen.agent.md | Donald Reinertsen |
| eric-ries.agent.md | Eric Ries |
| joseph-grenny.agent.md | Joseph Grenny (Influencer) |
| kent-beck.agent.md | Kent Beck |
| mary-poppendieck.agent.md | Mary Poppendieck |
| simon-sinek.agent.md | Simon Sinek |
| starfish-spider.agent.md | Brafman & Beckstrom |
| stephen-covey.agent.md | Stephen Covey |

### Future Work Items

- **TIM-0006+**: OFP response sections — each section can now be reviewed by any of the 12 agents before finalization

**Final status: IMPLEMENTED**

**Non-functional requirements**:
- Each agent body should be concise enough to fit within a context window without overwhelming it — focus on the author's most distinctive questions and concerns, not a verbatim copy of the src file
- Tone: Each agent speaks in first person as the author ("I would ask…", "My concern is…")
- Agent names should be recognizable: "Simon Sinek", "Kent Beck", etc.

**Telemetry / metrics expected**: N/A

**Rollout / rollback notes**: Agent files can be individually removed or updated without affecting other work items. The `.github/agents/` directory is additive — no existing files are modified.
