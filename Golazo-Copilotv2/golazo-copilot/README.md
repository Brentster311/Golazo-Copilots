# Golazo Copilot

A Model Context Protocol (MCP) server that brings **programmatic workflow enforcement** to GitHub Copilot. Golazo Copilot transforms the Golazo development methodology from markdown-based guidance into a system with persistent state, automated gates, and auditable artifacts.

## What is Golazo?

Golazo is a structured development methodology that ensures high-quality software delivery through role-based workflows, gates, and auditable artifacts. For a complete explanation of the Golazo methodology, see the [Golazo README](https://github.com/microsoft/golazo/blob/main/README.md).

## Features

- **Persistent state tracking** – Workflow progress is saved to `state.json` files, surviving session restarts
- **Automated role transitions** – Enforce the correct sequence: Project Owner → Program Manager → QA → Architect → Developer → Refactor Expert → Documentor → Builder → Retrospective
- **Role-based output validation** – Each role defines required outputs (files, directories) that are automatically validated on transition
- **Multi-session support** – Switch between work items while preserving context
- **Workflow profiles** – Choose `complete`, `express`, or `spike` modes based on task complexity
- **Deviation recording** – Audit trail when gates are bypassed with justification
- **Role notes enforcement** – Blocks transitions when role decision notes are missing (bypass with consent)
- **Version sync warning** – Alerts when the deployed workspace instructions don't match the running MCP server version
- **Role progress display** – Shows completion progress (X/9 roles) for each work item

### Feature Details

#### Persistent State Tracking
Each work item maintains its own `state.json` file in the `WorkItems/<id>/` directory. This file records the current role, phase, role history with timestamps, and any deviations. State survives VS Code restarts, allowing you to resume exactly where you left off.

#### Automated Role Transitions
The Golazo workflow enforces a structured progression through roles:
1. **Project Owner** – Define the user story and acceptance criteria
2. **Program Manager** – Break down work, create design document
3. **Quality Assurance** – Review design, define test cases
4. **Architect** – Validate architectural alignment, review contracts
5. **Developer** – Implement the solution with TDD
6. **Refactor Expert** – Improve code quality without changing behavior
7. **Documentor** – Update documentation to reflect changes
8. **Builder** – Verify builds pass, handle CI/CD concerns
9. **Retrospective** – Review what worked and what didn't

Transitions are validated—you cannot skip roles or jump directly to Developer without completing earlier phases. Backward transitions to any prior role are always allowed.

#### Role-Based Output Validation
Each role file (in `.github/roles/`) defines a `## Required Outputs` section listing the files or directories that must exist before you can transition away from that role. The system automatically validates these on transition.

For example, the `project-owner-assistant` role requires:
```
## Required Outputs
- file: WorkItems/{id}/{id}-User-Story.md
- file: WorkItems/{id}/RoleDecisionNotes/{id}-project-owner-assistant.md
```

When you call `gcp_transition`, the system:
1. Reads the current role's `## Required Outputs` section
2. Checks that each listed file/directory exists in the workspace
3. Blocks the transition if any output is missing, with a clear error message listing what's needed
4. Allows bypass via `gcp_consent` + `force=True` when justified

This replaces manual checklist marking with automated, file-based validation.

#### Multi-Session Support
Work on multiple features simultaneously. Each work item has independent state, allowing you to:
- Switch between work items without losing progress
- Check status of any work item at any time
- Resume interrupted work days or weeks later

#### Workflow Profiles
Choose the right level of process for the task:

| Profile | Roles | Use Case |
|---------|-------|----------|
| **Complete** | All 9 roles in sequence | Production features, complex changes |
| **Express** | Streamlined subset of roles | Small bug fixes, minor enhancements |
| **Spike** | Minimal roles | Prototypes, research, proof-of-concept |

All profiles use the same output validation mechanism—role files define what's required, and the system enforces it on transition.

#### Deviation Recording
When you need to bypass a gate (e.g., force a transition when outputs are missing), the system:
1. Requires explicit consent via `gcp_consent` tool
2. Records the action, reason, timestamp, and current role
3. Stores deviations in the work item's `state.json`
4. Enables retrospective review of process deviations

#### Role Notes Enforcement
The Golazo workflow requires every role to produce a decision notes document. The system enforces this by:
1. **Blocking on transition** – When you transition away from a role, `gcp_transition` checks if decision notes exist for that role. If missing, the transition **fails** with an error indicating the expected file path.
2. **Force with consent** – If you need to bypass, use `gcp_consent(action='skip_role')` first, then `gcp_transition(..., force=True)`.
3. **Status visibility** – `gcp_status` includes a `missing_notes` list showing which completed roles lack decision notes.
4. **Expected file naming** – Notes should be at `WorkItems/<id>/RoleDecisionNotes/<id>-<role>.md`

This ensures an audit trail of decisions made at each workflow stage.

#### Version Sync Warning
When you call `gcp_status`, the system compares the running MCP server version against the version comment in your workspace's `.github/copilot-instructions.md`. If they differ, a warning is displayed so you know to re-bootstrap or update the package.

#### Role Progress Display
`gcp_status` shows how many of the 9 workflow roles have been completed for a work item (e.g., "Role Progress: 4/9 complete"), giving visibility into overall progress.

#### TechBestPractices Reference
When bootstrapping a workspace, a `.github/roles/TechBestPractices.md` file is deployed alongside the role files. This shared reference document is referenced by the Architect, Developer, and Refactor Expert roles to ensure consistent technical standards.

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

In GitHub Copilot Chat, ask: **"GCP version?"**

It will run `gcp_status` and display the running version (e.g., `v2.103.6`).

## VS Code Configuration

Configure the MCP server in your **VS Code User Settings** so it's available across all workspaces.

### Step 1: Open User MCP Configuration

1. Open Command Palette: `Ctrl+Shift+P`
2. Run: **"MCP: Open User Configuration"**
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
- `gcp_consent` – Record consent for bypassing workflow gates
- `gcp_bootstrap` – Bootstrap Golazo instructions in a workspace

### Step 5: Bootstrap Your Workspace

In GitHub Copilot Chat, say: *"Please bootstrap GCP"*

This will create the Golazo Copilot directory structure and instruction files in your workspace:
- `WorkItems/` – Directory for work item artifacts
- `.github/copilot-instructions.md` – Workflow enforcement rules for Copilot
- `.github/roles/` – Role-specific instruction files (including `TechBestPractices.md`)

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
| `gcp_status` | Get workflow status: current role, required outputs, role progress, version sync |
| `gcp_transition` | Move between workflow roles (validates required outputs and role notes) |
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
   > "Create work item GCP-0042 using complete profile"

2. **Check status:**
   > "What's the status of GCP-0042?"

3. **Work through roles — Copilot follows role instructions to create required outputs:**
   > "Transition GCP-0042 to program-manager"

4. **If outputs are missing, the transition fails with a clear message:**
   > `[FAIL] Missing required outputs for 'project-owner-assistant': WorkItems/GCP-0042/GCP-0042-User-Story.md`

5. **Continue through all roles to completion:**
   > "Transition GCP-0042 to quality-assurance"
   > "Transition GCP-0042 to architect"
   > "Transition GCP-0042 to developer"
   > ... and so on through retrospective

## Updating

To update to the latest version:

```powershell
pip install --upgrade golazo-copilot --index-url https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/
```

Then reload VS Code and re-bootstrap your workspace to pick up the new version:
> "Please bootstrap GCP with force"

## License

MIT
