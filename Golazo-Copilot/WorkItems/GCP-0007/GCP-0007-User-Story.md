# GCP-0007: CLI Commands

**Status**: IMPLEMENTED

## User Story

**As a** developer who prefers terminal workflows,  
**I want to** use command-line tools for Golazo Copilot operations,  
**So that** I can manage workflow state without relying on the IDE.

---

## Acceptance Criteria

### AC1: `gcp init` Creates Work Item
- [ ] `gcp init feature-x` creates:
  - `WorkItems/feature-x/state.json` with initial state
  - Outputs confirmation and initial status
- [ ] `gcp init feature-x --profile=express` sets profile
- [ ] Error if work item already exists

### AC2: `gcp status` Shows Current State
- [ ] `gcp status` outputs formatted status:
  ```
  Work Item: feature-x
  Profile: complete
  Phase: definition
  Role: quality-assurance
  
  Definition of Ready:
    [x] userStory
    [x] designDoc
    [ ] reviewComments
    [ ] testCases
  
  Definition of Done:
    [ ] branchCreated
    [ ] testsWrittenFirst
    ...
  
  Next: Complete reviewComments, testCases
  ```
- [ ] `gcp status --json` outputs raw JSON

### AC3: `gcp transition <role>` Changes Role
- [ ] `gcp transition program-manager` transitions role
- [ ] Shows new role instructions after transition
- [ ] `gcp transition developer --force` with prior consent

### AC4: `gcp dor` and `gcp dod` Show Checklists
- [ ] `gcp dor` shows DoR checklist with status
- [ ] `gcp dod` shows DoD checklist with status
- [ ] `gcp dor mark userStory` marks item complete
- [ ] `gcp dor unmark userStory` unmarks item

### AC5: `gcp consent` Records Deviation
- [ ] `gcp consent skip_dor "exploring spike"` records consent
- [ ] Outputs consent ID for reference

### AC6: `gcp switch` and `gcp list` for Multi-Session
- [ ] `gcp list` shows all work items with status summary
- [ ] `gcp switch feature-b` switches active work item

### AC7: `gcp help` Shows Available Commands
- [ ] `gcp help` lists all commands with descriptions
- [ ] `gcp help init` shows detailed help for specific command

### AC8: Error Handling and Exit Codes
- [ ] Success: exit code 0
- [ ] User error (invalid args): exit code 1
- [ ] System error (file not found): exit code 2
- [ ] Clear error messages with suggestions

### AC9: Color and Formatting
- [ ] Uses colors for status (green=complete, red=missing)
- [ ] `--no-color` flag for CI/script use
- [ ] Respects `NO_COLOR` environment variable

### AC10: Working Directory Detection
- [ ] Finds `WorkItems/` directory by walking up from cwd
- [ ] `--workdir` flag to specify explicitly
- [ ] Error if no WorkItems directory found

---

## Technical Notes

### Command Structure
```
gcp <command> [subcommand] [args] [--flags]

Commands:
  init <id> [--profile=<p>]     Create new work item
  status [--json]               Show current workflow status
  transition <role> [--force]   Transition to role
  dor [mark|unmark <item>]      DoR checklist operations
  dod [mark|unmark <item>]      DoD checklist operations
  consent <action> "<reason>"   Record deviation consent
  list [--filter=<f>]           List all work items
  switch <id>                   Switch to work item
  complete ["<summary>"]        Mark work item complete
  help [command]                Show help
  version                       Show version

Global Flags:
  --workdir=<path>    Working directory
  --json              Output as JSON
  --no-color          Disable color output
  --verbose           Verbose output
```

### Implementation Approach
```typescript
// Using commander.js for CLI parsing
import { Command } from "commander";

const program = new Command();

program
  .name("gcp")
  .description("Golazo Copilot CLI - Workflow management for GitHub Copilot")
  .version("1.0.0");

program
  .command("init <workItemId>")
  .option("-p, --profile <profile>", "Workflow profile", "complete")
  .description("Initialize a new work item")
  .action(async (workItemId, options) => {
    // Reuse same logic as MCP gcp_init
  });
```

### Shared Core Logic
```typescript
// CLI and MCP share the same core modules
import { initWorkItem } from "../core/init";
import { transition } from "../core/transition";
import { markDoR, markDoD } from "../core/checklist";

// CLI is just a different interface to the same operations
```

### Package Binary
```json
// package.json
{
  "bin": {
    "gcp": "./dist/cli/index.js"
  }
}
```

---

## Dependencies

- **GCP-0001 through GCP-0006**: CLI wraps all core functionality

---

## Out of Scope

- Interactive mode / TUI (Future)
- Shell completions (Future)
- Config file for defaults (Future)

---

## Definition of Ready Checklist

- [ ] User Story document exists (this file)
- [ ] Design Doc exists
- [ ] Review Comments from QA and Architect exist
- [ ] Test Cases document exists

## Definition of Done Checklist

- [ ] Feature branch created
- [ ] Test code written before production code
- [ ] All automated tests pass
- [ ] Build passes
- [ ] Docs updated
- [ ] Refactor pass complete
- [ ] Changes committed
