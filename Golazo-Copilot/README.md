# Golazo Copilot

A structured, role-based workflow for AI-assisted software development with GitHub Copilot.

## What is Golazo?

**Golazo** is a methodology that transforms how you work with AI coding assistants. Instead of letting AI write code immediately, Golazo enforces a disciplined workflow with **gates, roles, and auditable artifacts** — ensuring quality, traceability, and thoughtful design before any code is written.

Think of it as **Kanban meets AI pair programming**: every feature goes through defined roles (Project Owner, Architect, Tester, Developer, etc.), and each role produces documentation explaining *why* decisions were made.

📚 **Learn more about Golazo**: [https://microsoft.github.io/golazo/](https://microsoft.github.io/golazo/)

## Benefits

| Benefit | Description |
|---------|-------------|
| **No Cowboy Coding** | AI can't skip to implementation — it must complete design and test planning first |
| **Audit Trail** | Every decision is documented; you can trace *why* any code exists |
| **TDD by Default** | Test cases are written before code (Definition of Ready requires them) |
| **Consistent Process** | Same workflow for every feature, every time |
| **Scope Control** | Clear "out of scope" definitions prevent feature creep |
| **Role Separation** | Different "hats" catch different issues (Reviewer vs Architect vs Tester) |
| **Checks and Balances** | Each role reviews the previous role's work — no single point of failure in decision-making |

## Quick Start

### Install Golazo in Your Repository

```bash
# Clone the Golazo Copilot repository
git clone https://github.com/Brentster311/Golazo-Copilots.git

# Navigate to your target project
cd /path/to/your/project

# Run the installer
python /path/to/Golazo-Copilots/Golazo-Copilot/Golazo_Copilot.py
```

This installs:
- `.github/copilot-instructions.md` — The "spine" that controls Copilot's behavior
- `.github/roles/*.md` — Detailed instructions for each of the 10 roles

### Start Using Golazo

1. Open your project in VS Code with GitHub Copilot
2. Ask Copilot to help with a feature: *"I want to add user authentication"*
3. Copilot will automatically follow the Golazo workflow, starting with the **Project Owner Assistant** role

## The 10 Roles

Golazo defines 10 sequential roles. Each role has specific responsibilities and produces artifacts:

| # | Role | Purpose | Key Output |
|---|------|---------|------------|
| 1 | **Project Owner Assistant** | Translate request into testable User Story | `<id>-User-Story.md` |
| 2 | **Program Manager** | Create Design Document with business case | `<id>-Design-Doc.md` |
| 3 | **Reviewer** | Review requirements for clarity and completeness | `<id>-Review-Comments.md` |
| 4 | **Architect** | Review technical approach and patterns | (in Review-Comments.md) |
| 5 | **Tester** | Define test cases (TDD-first) | `<id>-Test-Cases.md` |
| 6 | **Developer** | Implement code and tests | Code + tests |
| 7 | **Refactor Expert** | Improve code quality without behavior change | Refactored code |
| 8 | **Builder** | Verify build and deployment | Build verification |
| 9 | **Documentor** | Update all documentation | Updated docs |
| 10 | **Retrospective** | Evaluate process and propose improvements | Process changes |

### Role Flow

```
1. Project Owner    5. Tester           9. Documentor
        |                |                   |
        v                v                   v
2. Program Manager  6. Developer       10. Retrospective
        |                |
        v                v
3. Reviewer         7. Refactor Expert
        |                |
        v                v
4. Architect        8. Builder
```

## Artifact Structure

All work items are organized in a `WorkItems/` folder:

```
YourProject/
??? WorkItems/
    ??? TICKET-001/
        ??? TICKET-001-User-Story.md
        ??? Design/
        ?   ??? TICKET-001-Design-Doc.md
        ?   ??? TICKET-001-Review-Comments.md
        ?   ??? TICKET-001-Test-Cases.md
        ??? RoleDecisionNotes/
            ??? TICKET-001-project-owner-assistant.md
            ??? TICKET-001-program-manager.md
            ??? TICKET-001-reviewer.md
            ??? TICKET-001-architect.md
            ??? TICKET-001-tester.md
            ??? TICKET-001-developer.md
            ??? TICKET-001-refactor.md
            ??? TICKET-001-builder.md
            ??? TICKET-001-documentor.md
```

### Why This Structure?

- **Everything for a work item is together** — no hunting across folders
- **Role notes explain decisions** — not just *what* was built, but *why*
- **Git-friendly** — easy to see all changes for a feature in one PR
- **Auditable** — compliance and review teams can trace any decision

## Definition of Ready (DoR)

Copilot **cannot write production code** until ALL of these exist:

- [ ] User Story document
- [ ] Design Document with business case
- [ ] Review Comments from Reviewer and Architect
- [ ] Test Cases document

This is enforced automatically — Copilot will refuse to write code and redirect you to create missing artifacts.

## Definition of Done (DoD)

Work is not complete until:

- [ ] All automated tests pass
- [ ] New behavior is covered by tests
- [ ] Build passes
- [ ] All docs updated
- [ ] Refactor pass completed (no behavior change)
- [ ] Changes committed to git

## Using the Retrospective Role (Example)

The **Retrospective** role is triggered when something goes wrong or friction is detected in the workflow. It proposes changes to the *process*, not the *product*.

### Example Scenario

You notice that Reviewer and Architect feedback keeps getting lost because it's in two separate documents.

### Triggering a Retrospective

Ask Copilot:
> "I want to run a retrospective. The problem is that Reviewer and Architect feedback is hard to track because it's split across documents."

### Retrospective Output

Copilot (as Retrospective role) might produce:

```markdown
# Retrospective: RETRO-001

## Problem Observed
Reviewer and Architect feedback split across multiple documents, 
making it hard to track what was addressed.

## Root Cause Analysis
- Original design had separate review notes per role
- No single source of truth for review status

## Proposed Process Change
Merge Reviewer and Architect feedback into single 
`<id>-Review-Comments.md` with sections for each role.

## Impact Assessment
- Reduces artifact count
- Clearer tracking of addressed vs pending comments
- Minor update to copilot-instructions.md required

## Recommendation
Update `.github/copilot-instructions.md` to specify combined 
Review-Comments.md format.
```

The Retrospective output becomes input for a *new work item* to update the Golazo instructions themselves.

## Configuration

The workflow is controlled by `.github/copilot-instructions.md`. You can customize:

- Work item ID format
- Artifact locations
- Role-specific rules
- Gate requirements

**Warning**: Changes to the spine affect all future work items. Use the Retrospective process to propose changes.

## FAQ

### Can I skip roles?

**No.** The Golazo workflow is strictly sequential. Skipping roles is a process violation. If you need to move faster, the answer is smaller scope (smaller User Stories), not skipping steps.

### What if Copilot writes code before DoR is complete?

This is a process violation. The instructions explicitly forbid this. If it happens, check that `.github/copilot-instructions.md` is correctly loaded.

### Can I use Golazo without Copilot?

The artifacts and workflow can be used manually or with any AI assistant. The `.github/copilot-instructions.md` file is specific to GitHub Copilot, but the methodology is tool-agnostic.

### How do I handle urgent hotfixes?

Create a minimal User Story with "hotfix" scope. The workflow still applies, but acceptance criteria can be minimal. Document the urgency in the User Story.

## License

MIT License — see LICENSE file for details.

## Contributing

Contributions welcome! Please follow the Golazo workflow when contributing:

1. Create a User Story for your proposed change
2. Go through the full role sequence
3. Submit PR with all artifacts

