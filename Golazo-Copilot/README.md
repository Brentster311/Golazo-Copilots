# Golazo Copilot (GolazoCP)

A structured, role-based workflow for AI-assisted software development with GitHub Copilot.

**Current Version**: 1.1.5

## What is GolazoCP?

**GolazoCP** is a methodology that transforms how you work with AI coding assistants. Instead of letting AI write code immediately, GolazoCP enforces a disciplined workflow with **gates, roles, and auditable artifacts** — ensuring quality, traceability, and thoughtful design before any code is written.

GolazoCP, adapted from the Golazo agile practice, is sort of **Kanban meets AI pair programming**: every feature goes through defined roles (Project Owner, Architect, Tester, Developer, etc.), and each role produces documentation explaining *why* decisions were made.

📚 **Learn more about Golazo**: [https://microsoft.github.io/golazo/](https://microsoft.github.io/golazo/)

## Benefits

| Benefit | Description |
|---------|-------------|
| **Structured Development** | AI follows a deliberate process — design and test planning are completed before implementation |
| **Audit Trail** | Every decision is documented; you can trace *why* any code exists |
| **TDD by Default** | Test cases are written before code (Definition of Ready requires them) |
| **Consistent Process** | Same workflow for every feature, every time |
| **Scope Control** | Clear "out of scope" definitions prevent feature creep |
| **Role Separation** | Different "hats" catch different issues (Reviewer vs Architect vs Tester) |
| **Checks and Balances** | Each role reviews the previous role's work — no single point of failure in decision-making |
| **Role Transition Visibility** | Copilot announces when transitioning between roles, showing what was produced |
| **Pattern Consistency** | Infrastructure changes require research of existing patterns before proposing new ones |

## Quick Start

### Installation

Download `GolazoCP-dist.zip` and extract it to your project root, or follow the detailed installation guides:

- **[Visual Studio Setup](USAGE-VisualStudio.md)** — Full instructions for VS users
- **[VS Code Setup](USAGE-VSCode.md)** — Full instructions for VS Code users

### What Gets Installed

```
.github/
├── copilot-instructions.md     # The "spine" controlling Copilot behavior
├── roles/                      # 10 role instruction files
│   ├── project-owner-assistant.md
│   ├── program-manager.md
│   ├── reviewer.md
│   ├── architect.md
│   ├── tester.md
│   ├── developer.md
│   ├── refactor-expert.md
│   ├── builder.md
│   ├── documentor.md
│   └── retrospective.md
└── guides/                     # Context-specific technical guides
    ├── powershell-terminal.md  # Terminal encoding rules
    ├── golazo-update.md        # Version checking and upgrades
    └── PatternProposals.md     # Infrastructure pattern research
```

### Start Using GolazoCP

1. Open your project in VS Code or Visual Studio with GitHub Copilot
2. Ask Copilot to help with a feature: *"I want to add user authentication"*
3. Copilot will automatically follow the Golazo workflow, starting with the **Project Owner Assistant** role

## The 10 Roles

GolazoCP defines 10 sequential roles. Each role has specific responsibilities, **entrance criteria** (required artifacts before starting), and produces artifacts. When transitioning between roles, Copilot announces the transition with the reason and what was produced.

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

### Role Transitions

When Copilot transitions between roles, it announces:
- **"Transitioning from [Role A] to [Role B]"**
- Reason for the transition
- What artifact/output was produced by the previous role

This makes the workflow visible and auditable.


## Artifact Structure

All work items are organized in a `WorkItems/` folder:

```
YourProject/
  WorkItems/
    TICKET-001/
      TICKET-001-User-Story.md
      Design/
        TICKET-001-Design-Doc.md
        TICKET-001-Review-Comments.md
        TICKET-001-Test-Cases.md
      RoleDecisionNotes/
        TICKET-001-project-owner-assistant.md
        TICKET-001-program-manager.md
        TICKET-001-reviewer.md
        TICKET-001-architect.md
        TICKET-001-tester.md
        TICKET-001-developer.md
        TICKET-001-refactor.md
        TICKET-001-builder.md
        TICKET-001-documentor.md
```

### Why This Structure?

- **Everything for a work item is together** — no hunting across folders
- **Role notes explain decisions** — not just *what* was built, but *why*
- **Git-friendly** — easy to see all changes for a feature in one PR
- **Auditable** — compliance and review teams can trace any decision

## Definition of Ready (DoR)

GolazoCP **cannot write production code** until ALL of these exist:

- [ ] User Story document
- [ ] Design Document with business case
- [ ] Review Comments from Reviewer and Architect
- [ ] Test Cases documented and automated (TDD)

This is enforced automatically — Golazo will refuse to write code and redirect you to create missing artifacts.

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

You notice that Copilot wrote production code before writing the test code, violating TDD principles.

### Triggering a Retrospective

Ask Copilot:
> "I want to run a retrospective. The problem is: why did you write code before the test cases?"

### Retrospective Output

Copilot (as Retrospective role) might produce:

```markdown
# Retrospective: RETRO-001

## Problem Observed
Developer role wrote production code before test code, 
violating TDD (Test-Driven Development) principles.

## Root Cause Analysis
- Developer role instructions didn't explicitly require tests FIRST
- "Add/adjust tests" was listed but not sequenced before code
- No forbidden action preventing code-before-tests

## Proposed Process Change
Update Developer role instructions to:
1. Add "Write test code FIRST" to Responsibilities
2. Add "May NOT write production code before test code" to Forbidden actions

## Impact Assessment
- Enforces TDD discipline
- Tests become a gate, not an afterthought
- Minor update to .github/roles/developer.md required

## Recommendation
Update `.github/roles/developer.md` to explicitly require 
test code before production code.
```

The Retrospective output becomes input for a *new work item* to update the Golazo instructions themselves.

## Configuration

The workflow is controlled by `.github/copilot-instructions.md`. You can customize:

- Work item ID format
- Artifact locations
- Role-specific rules
- Gate requirements

**Warning**: Changes to the spine affect all future work items. Use the Retrospective process to propose changes.

## Context-Specific Guides

GolazoCP includes technical guides that are loaded when relevant:

| Guide | When Loaded |
|-------|-------------|
| **PowerShell Terminal** | Writing files via terminal, encoding errors |
| **Golazo Updates** | Checking for newer versions, upgrading |
| **Pattern Proposals** | Infrastructure, pipeline, or config changes |

The **Pattern Proposals** guide ensures Copilot researches existing patterns before proposing new infrastructure or configuration approaches. It follows a 4-step process: SEARCH → COUNT → PRESENT → APPROVE.

## FAQ

### Can I skip roles?

**No.** The Golazo workflow is strictly sequential. Skipping roles is a process violation. If you need to move faster, the answer is smaller scope (smaller User Stories), not skipping steps.

### What if Copilot writes code before DoR is complete?

This is a process violation. The instructions explicitly forbid this. If it happens, check that `.github/copilot-instructions.md` is correctly loaded.

### Can I use Golazo without Copilot?

The artifacts and workflow can be used manually or with any AI assistant. The `.github/copilot-instructions.md` file is specific to GitHub Copilot, but the methodology is tool-agnostic.

### How do I check for updates?

Ask Copilot: *"Check for Golazo updates"* — it will compare your local version against the latest and offer to upgrade if a newer version is available.

### What is "Project Root"?

**Project Root** is where Golazo creates artifacts (the `WorkItems/` folder). In Visual Studio, it's the directory containing your project file (`.csproj`, `.pyproj`, etc.). In VS Code, it's the directory containing a project manifest (`package.json`, `pyproject.toml`, etc.).

## License

MIT License — see LICENSE file for details.

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.


