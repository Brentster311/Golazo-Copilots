# MCP Server Dispatch Extension Points

## Where to register a tool
- Add the MCP `Tool(...)` schema in `dispatch/registry.py` via `get_tool_definitions()`.
- Keep tool name and required parameter contract stable unless a new user story approves a contract change.

## Where to route and preflight
- Use `dispatch/router.py` for workflow preflight checks and top-level name-to-handler routing.
- Keep routing deterministic: one tool name maps to one handler path.

## Where to implement tool behavior
- Add tool-specific execution logic in `handlers/tools.py`.
- Keep handlers focused on invoking domain tools and assembling result dicts.

## Where to format responses
- Add or modify response/error formatting in `formatters/results.py`.
- Preserve existing success/error envelope shape and deterministic message intent.

## Minimal extension flow
1. Register schema in `dispatch/registry.py`.
2. Add/route handler in `handlers/tools.py` and `dispatch/router.py`.
3. Add formatter logic in `formatters/results.py` if needed.
4. Add parity/dispatch tests before production changes.
