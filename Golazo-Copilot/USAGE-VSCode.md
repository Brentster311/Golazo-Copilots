# Using GolazoCP with VS Code

This guide explains how to set up and use GolazoCP with GitHub Copilot in Visual Studio Code.

## Prerequisites

- Visual Studio Code (1.85 or later)
- GitHub Copilot extension installed
- GitHub Copilot Chat extension installed

## Installation

1. **Extract the zip** to your project root directory:
   ```
   your-project/
   ??? .github/
   ?   ??? copilot-instructions.md
   ?   ??? roles/
   ?       ??? architect.md
   ?       ??? builder.md
   ?       ??? ... (10 role files)
   ??? src/
   ??? package.json (or other project files)
   ```

2. **Verify the files are in place**:
   - `.github/copilot-instructions.md` should exist at your workspace root
   - `.github/roles/` should contain 10 markdown files

## Using GolazoCP

### Starting a New Work Item

1. Open **GitHub Copilot Chat**:
   - Click the Copilot icon in the sidebar, or
   - Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (Mac)

2. Ask Copilot to help with a feature:
   ```
   I want to add user authentication to my application
   ```

3. Copilot will automatically:
   - Detect the Golazo instructions from `.github/copilot-instructions.md`
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

## Using @workspace

For better context awareness, use the `@workspace` command:

```
@workspace I want to add a new API endpoint for user profiles
```

This helps Copilot understand your project structure when making recommendations.

## Troubleshooting

### Copilot Doesn't Follow Golazo Workflow

1. Verify `.github/copilot-instructions.md` exists at workspace root
2. Reload VS Code (`Ctrl+Shift+P` ? "Developer: Reload Window")
3. Start a new chat session

### Copilot Skips Directly to Code

This is a process violation. The instructions explicitly forbid this. Check that:
- The `copilot-instructions.md` file is not corrupted
- You're in Copilot Chat (not inline completions - those don't use custom instructions)

### Instructions Not Being Picked Up

VS Code looks for instructions at `.github/copilot-instructions.md`. Ensure:
- The file is at the workspace root, not in a subfolder
- The filename is exactly `copilot-instructions.md` (case-sensitive on some systems)

## Tips for Best Results

1. **Be specific** in your initial request
2. **Answer clarifying questions** - don't skip them
3. **Review each artifact** before proceeding to the next role
4. **Use work item IDs** to track related artifacts
5. **Use @workspace** for better project context

## File Locations

GolazoCP creates artifacts in this structure:

```
your-project/
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

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Copilot Chat | `Ctrl+Shift+I` / `Cmd+Shift+I` |
| Inline Chat | `Ctrl+I` / `Cmd+I` |
| Accept Suggestion | `Tab` |
| Dismiss Suggestion | `Esc` |

## Learn More

- [GolazoCP README](README.md)
- [Golazo Methodology](https://microsoft.github.io/golazo/)
- [VS Code Copilot Docs](https://code.visualstudio.com/docs/copilot/overview)
