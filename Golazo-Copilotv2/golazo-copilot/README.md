# Golazo Copilot

A Model Context Protocol (MCP) server that brings **programmatic workflow enforcement** to GitHub Copilot. Golazo Copilot transforms the Golazo development methodology from markdown-based guidance into a system with:

## What is Golazo?

Golazo is a structured development methodology that ensures high-quality software delivery through role-based workflows, gates, and auditable artifacts. For a complete explanation of the Golazo methodology, see the [Golazo README](https://github.com/microsoft/golazo/blob/main/README.md).

## Features

- **Persistent state tracking** – Workflow progress is saved to `state.json` files, surviving session restarts
- **Automated role transitions** – Enforce the correct sequence: Project Owner → Program Manager → QA → Architect → Developer → Refactor Expert → Builder → Documentor → Retrospective
- **Definition of Ready (DoR) gates** – Block development work until user story, design doc, review comments, and test cases are complete
- **Definition of Done (DoD) tracking** – Track branch creation, tests, builds, docs, and commits
- **Multi-session support** – Switch between work items while preserving context
- **Workflow profiles** – Choose `complete`, `express`, or `spike` modes based on task complexity
- **Deviation recording** – Audit trail when gates are bypassed with justification
- **Role notes enforcement** – Blocks transitions when role decision notes are missing (bypass with consent)

### Feature Details

#### Persistent State Tracking
Each work item maintains its own `state.json` file in the `WorkItems/<id>/` directory. This file records the current role, phase, DoR/DoD checklist status, role history with timestamps, and any deviations. State survives VS Code restarts, allowing you to resume exactly where you left off.

#### Automated Role Transitions
The Golazo workflow enforces a structured progression through roles:
1. **Project Owner** – Define the user story and acceptance criteria
2. **Program Manager** – Break down work, identify dependencies
3. **Quality Assurance** – Define test cases before development
4. **Architect** – Create design document, make technical decisions
5. **Developer** – Implement the solution (requires DoR complete)
6. **Refactor Expert** – Improve code quality without changing behavior
7. **Builder** – Verify builds pass, handle CI/CD concerns
8. **Documentor** – Update documentation to reflect changes
9. **Retrospective** – Review what worked and what didn't

Transitions are validated—you cannot skip roles or jump directly to Developer without completing earlier phases.

#### Definition of Ready (DoR) Gates
Before entering the Development phase, all DoR items must be complete:
- **User Story** – Clear description of what and why
- **Design Doc** – Technical approach documented
- **Review Comments** – Design reviewed and feedback addressed
- **Test Cases** – How success will be verified

The `gcp_transition` tool blocks transitions to Developer until DoR is satisfied (unless consent is recorded).

#### Definition of Done (DoD) Tracking
Track completion of development work:
- **Branch Created** – Feature branch exists
- **Tests Written First** – TDD approach followed
- **Tests Pass** – All tests green
- **Build Passes** – CI/CD pipeline succeeds
- **Docs Updated** – Documentation reflects changes
- **Refactor Complete** – Code quality improvements done
- **Committed** – Changes committed to source control

#### Multi-Session Support
Work on multiple features simultaneously. Each work item has independent state, allowing you to:
- Switch between work items without losing progress
- Check status of any work item at any time
- Resume interrupted work days or weeks later

#### Workflow Profiles
Choose the right level of process for the task:

**Complete** – Full workflow with all gates enforced
- All 9 roles in sequence
- Full DoR required: userStory, designDoc, reviewComments, testCases
- Full DoD tracked: branchCreated, testsWrittenFirst, testsPass, buildPasses, docsUpdated, refactorComplete, committed

**Express** – Reduced gates for faster iteration
- Streamlined roles: Project Owner → Architect → Developer → Builder
- Reduced DoR: userStory, designDoc, testCases (reviewComments optional)
- Reduced DoD: testsPass, buildPasses, committed

**Spike** – Minimal process for exploration
- Minimal roles: Developer → Builder
- No DoR gate (start coding immediately)
- Minimal DoD: buildPasses only

#### Deviation Recording
When you need to bypass a gate (e.g., skip DoR to explore a spike), the system:
1. Requires explicit consent via `gcp_consent` tool
2. Records the action, reason, timestamp, and current role
3. Stores deviations in the work item's `state.json`
4. Enables retrospective review of process deviations

#### Role Notes Enforcement
The Golazo workflow requires every role to produce a decision notes document. The system enforces this by:
1. **Blocking on transition** – When you transition away from a role, `gcp_transition` checks if decision notes exist for that role. If missing, the transition **fails** with an error indicating the expected file path.
2. **Force with consent** – If you need to bypass, use `gcp_consent(action='skip_role')` first, then `gcp_transition(..., force_without_notes=True)`.
3. **Status visibility** – `gcp_status` includes a `missing_notes` list showing which completed roles lack decision notes.
4. **Expected file naming** – Notes should be at `WorkItems/<id>/RoleDecisionNotes/<id>-<role>.md`

This ensures an audit trail of decisions made at each workflow stage.

## Prerequisites

- **Python 3.10 or later** installed and available in your system PATH
- **Visual Studio Code** with GitHub Copilot extension
- Access to the Azure Artifacts feed (for installation)

### Verify Python Installation

```powershell
python --version
```

You should see `Python 3.10.x` or later. If Python is not found, download and install from [python.org](https://www.python.org/downloads/). During installation, ensure you check **"Add python.exe to PATH"**.

## Installation

Install the Azure Artifacts credential provider first, then install `golazo-copilot` into your **global Python environment**:

```bash
# Install credential providers for Azure Artifacts authentication
pip install keyring artifacts-keyring

# Install golazo-copilot from Azure Artifacts
pip install golazo-copilot --index-url https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/
```

> **Note:** The first time you install from Azure Artifacts, you may be prompted to authenticate via browser, or you may need to run `az login` first.

### Verify Installation

```powershell
python -c "import golazo_copilot; print(f'golazo-copilot version: {golazo_copilot.__version__}')"
```

## VS Code Configuration

Configure the MCP server in your **VS Code User Settings** so it's available across all workspaces.

### Step 1: Open User MCP Configuration

1. Open Command Palette: `Ctrl+Shift+P`
2. Run: **"Preferences: Open User Settings (JSON)"**
3. Add the MCP server configuration, or
4. Create/edit the file directly at:
   - **Windows**: `%APPDATA%\Code\User\mcp.json`
   - **macOS**: `~/Library/Application Support/Code/User/mcp.json`
   - **Linux**: `~/.config/Code/User/mcp.json`

### Step 2: Add MCP Server Configuration

Add the following to your `mcp.json` file:

```json
{
    "servers": {
        "golazo-copilot": {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "golazo_copilot.server"]
        }
    }
}
```

### Step 3: Reload VS Code

After saving the configuration:

1. Open Command Palette: `Ctrl+Shift+P`
2. Run: **"Developer: Reload Window"**

### Step 4: Verify MCP Server is Running

In GitHub Copilot Chat, ask: *"What MCP tools do you have?"*

You should see the Golazo Copilot tools listed:
- `gcp_create_workitem` – Initialize a new work item
- `gcp_status` – Check workflow status  
- `gcp_transition` – Move between roles
- `gcp_mark_dor` – Mark Definition of Ready items complete
- `gcp_mark_dod` – Mark Definition of Done items complete
- `gcp_consent` – Record consent for bypassing workflow gates
- `gcp_bootstrap` – Bootstrap Golazo instructions in a workspace

### Step 5: Bootstrap Your Workspace

In GitHub Copilot Chat, say: *"Please bootstrap GCP"*

This will create the Golazo Copilot directory structure and instruction files in your workspace:
- `WorkItems/` – Directory for work item artifacts
- `.github/copilot-instructions.md` – Workflow enforcement rules for Copilot
- `.github/roles/` – Role-specific instruction files

## Troubleshooting

### Server not starting

**"python is not recognized"** – Python is not in your PATH. Either:
- Reinstall Python and check "Add python.exe to PATH"
- Use the full path to Python in your mcp.json:
  ```json
  "command": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
  ```

**"spawn EPERM" error** – This occurs with Windows Store Python. Uninstall Windows Store Python and install from [python.org](https://www.python.org/downloads/) instead.

**"No module named golazo_copilot"** – The package isn't installed in the Python environment VS Code is using. Run:
```powershell
pip install golazo-copilot --index-url https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/
```

### Tools not appearing in Copilot Chat

1. Check the VS Code Output panel → select "MCP" from the dropdown
2. Verify the server started without errors
3. Try reloading: `Ctrl+Shift+P` → "Developer: Reload Window"

### Test the server manually

```powershell
python -m golazo_copilot.server
```

If it starts without errors (no output, waiting for input), the server is working correctly. Press `Ctrl+C` to exit.

## Usage

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `gcp_create_workitem` | Initialize a new work item with persistent state tracking |
| `gcp_status` | Get comprehensive workflow status, including missing role notes |
| `gcp_transition` | Move between workflow roles (enforces DoR gate, warns on missing notes) |
| `gcp_mark_dor` | Mark Definition of Ready items as complete |
| `gcp_mark_dod` | Mark Definition of Done items as complete |
| `gcp_consent` | Record consent for bypassing workflow gates |
| `gcp_bootstrap` | Bootstrap Golazo instructions and directories in a workspace |

### Workflow Profiles

| Profile | Description | Use Case |
|---------|-------------|----------|
| `complete` | Full Golazo workflow with all gates enforced | Production features, complex changes |
| `express` | Reduced gates for faster iteration | Small bug fixes, minor enhancements |
| `spike` | Minimal process for exploration | Prototypes, research, proof-of-concept |

### Example Session

1. **Create a work item:**
   > "Create work item GCP-0015 using complete profile"

2. **Check status:**
   > "What's the status of GCP-0015?"

3. **Mark DoR progress:**
   > "Mark userStory and designDoc complete for GCP-0015"

4. **Transition to next role:**
   > "Transition GCP-0015 to program-manager"

5. **When all DoR items are complete, move to development:**
   > "Transition GCP-0015 to developer"

## Updating

To update to the latest version:

```powershell
pip install --upgrade golazo-copilot --index-url https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/
```

Then reload VS Code to pick up the new version.

## License

MIT
