# Using GolazoCP with Visual Studio

This guide explains how to set up and use GolazoCP with GitHub Copilot in Visual Studio.

## Prerequisites

- Visual Studio 2022 (17.8 or later)
- GitHub Copilot extension installed (includes Copilot Chat)

## Installation

1. **Extract the zip** to your project root directory:
   ```
   YourProject/
   ??? .github/
   ?   ??? copilot-instructions.md
   ?   ??? roles/
   ?       ??? architect.md
   ?       ??? builder.md
   ?       ??? ... (10 role files)
   ??? YourCode/
   ??? YourProject.sln
   ```

2. **Verify the files are in place**:
   - `.github/copilot-instructions.md` should exist at your solution root
   - `.github/roles/` should contain 10 markdown files

## Using GolazoCP

### Starting a New Work Item

1. Open **GitHub Copilot Chat** (View ? GitHub Copilot ? Open Copilot Chat)

2. Ask Copilot to help with a feature:
   ```
   I want to add user authentication to my application
   ```

3. Copilot will automatically:
   - Detect the Golazo instructions
   - Start with the **Project Owner Assistant** role
   - Ask clarifying questions before writing any code

### Following the Workflow

Copilot will guide you through each role:

| Role | What Happens |
|------|--------------|
| Project Owner Assistant | Creates User Story, asks clarifying questions |
| Program Manager | Creates Design Document |
| Reviewer | Reviews requirements |
| Architect | Reviews technical approach |
| Tester | Defines test cases |
| Developer | Writes tests first, then code |
| Refactor Expert | Improves code quality |
| Builder | Verifies build |
| Documentor | Updates documentation |
| Retrospective | Evaluates process (triggered as needed) |

### Checking the Status

At any time, ask Copilot:
```
What is the current Golazo status?
```

Copilot will show you:
- Current work item ID
- Current role
- Definition of Ready checklist
- Definition of Done checklist

## Troubleshooting

### Copilot Doesn't Follow Golazo Workflow

1. Verify `.github/copilot-instructions.md` exists
2. Close and reopen the Copilot Chat window
3. Start a new chat session

### Copilot Skips Directly to Code

This is a process violation. The instructions explicitly forbid this. Check that:
- The `copilot-instructions.md` file is not corrupted
- You're in a chat session (not inline completions)

### WorkItems Folder Not Created

The workflow expects you to have a `WorkItems/` folder. Create it manually or let Copilot create it when generating the first artifact.

## Tips for Best Results

1. **Be specific** in your initial request
2. **Answer clarifying questions** - don't skip them
3. **Review each artifact** before proceeding to the next role
4. **Use work item IDs** to track related artifacts

## File Locations

GolazoCP creates artifacts in this structure:

```
YourProject/
??? WorkItems/
?   ??? TICKET-001/
?       ??? TICKET-001-User-Story.md
?       ??? Design/
?       ?   ??? TICKET-001-Design-Doc.md
?       ?   ??? TICKET-001-Review-Comments.md
?       ?   ??? TICKET-001-Test-Cases.md
?       ??? RoleDecisionNotes/
?           ??? TICKET-001-project-owner-assistant.md
?           ??? ... (one per role)
```

## Learn More

- [GolazoCP README](README.md)
- [Golazo Methodology](https://microsoft.github.io/golazo/)
