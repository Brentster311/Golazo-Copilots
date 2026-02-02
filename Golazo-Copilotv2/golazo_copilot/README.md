# Golazo Copilot

MCP server for Golazo Copilot workflow management with GitHub Copilot.

## Installation

```bash
pip install golazo-copilot
```

## Usage

Configure your IDE to use the Golazo Copilot MCP server, then use:

- `gcp_init` - Initialize a new work item
- `gcp_status` - Check workflow status
- `gcp_transition` - Move to next role

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
