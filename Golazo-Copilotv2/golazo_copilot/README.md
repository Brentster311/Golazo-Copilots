# Golazo Copilot

MCP server for Golazo Copilot workflow management with GitHub Copilot.

## Installation

```bash
pip install golazo-copilot
```

Or for development:
```bash
cd golazo_copilot
pip install -e .
```

## VS Code Integration

### Step 1: Add MCP Configuration to User Settings

**Important:** The MCP config must be in **User Settings** (not just workspace settings).

1. Open VS Code Settings: `Ctrl+,`
2. Search for "mcp"
3. Click "Edit in settings.json"
4. Add the following configuration:

```json
{
  "mcp": {
    "servers": {
      "golazo-copilot": {
        "type": "stdio",
        "command": "python",
        "args": ["-m", "golazo_copilot.server"]
      }
    }
  },
  "chat.mcp.access": "all"
}
```

**If using a virtual environment**, use the full path to the Python interpreter:

```json
{
  "mcp": {
    "servers": {
      "golazo-copilot": {
        "type": "stdio",
        "command": "C:/path/to/your/project/.venv/Scripts/python.exe",
        "args": ["-m", "golazo_copilot.server"]
      }
    }
  },
  "chat.mcp.access": "all"
}
```

### Step 2: Start the MCP Server

After adding the configuration:

1. Open Command Palette: `Ctrl+Shift+P`
2. Run: **"MCP: Start Server"**
3. Select: **golazo-copilot**

Alternatively, run **"Chat: Restart MCP Servers"** to restart all servers.

### Step 3: Verify Tools Are Available

In GitHub Copilot Chat, ask: "What MCP tools do you have?"

You should see:
- `gcp_init` - Initialize a new work item
- `gcp_status` - Check workflow status
- `gcp_transition` - Move between roles
- `gcp_mark_dor` - Mark DoR items complete
- `gcp_mark_dod` - Mark DoD items complete

### Troubleshooting

**Server not showing in MCP picker:**
- Ensure the config is in **User Settings**, not just workspace settings
- Run "Developer: Reload Window" to reload VS Code

**Tools not appearing:**
- Check VS Code Output panel for MCP logs
- Verify the Python path is correct
- Ensure golazo-copilot is installed in the Python environment

**Test the server manually:**
```bash
python -m golazo_copilot.server
```
If it starts without errors, the server is working.

## Usage

### Available Tools

| Tool | Description |
|------|-------------|
| `gcp_init` | Initialize a new work item with state tracking |
| `gcp_status` | Get comprehensive workflow status |
| `gcp_transition` | Move between workflow roles with DoR gate |
| `gcp_mark_dor` | Mark Definition of Ready items |
| `gcp_mark_dod` | Mark Definition of Done items |

### Example Workflow

1. **Start a work item:**
   ```
   "Start work item feature-123"
   ? calls gcp_init(work_item_id="feature-123")
   ```

2. **Check status:**
   ```
   "Check status for feature-123"
   ? calls gcp_status(work_item_id="feature-123")
   ```

3. **Mark progress:**
   ```
   "Mark userStory complete for feature-123"
   ? calls gcp_mark_dor(work_item_id="feature-123", item="userStory", complete=true)
   ```

4. **Transition roles:**
   ```
   "Move to program-manager for feature-123"
   ? calls gcp_transition(work_item_id="feature-123", role="program-manager")
   ```

### Bootstrap Instructions

For automatic workflow enforcement, add `.github/copilot-instructions.md` to your repository. See `bootstrap-instructions.md` for a complete template.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run tests with coverage
pytest --cov=golazo_copilot
```

## License

MIT
