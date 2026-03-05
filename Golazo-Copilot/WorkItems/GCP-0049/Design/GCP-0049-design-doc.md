# GCP-0049 Design Document — Role Context Bundler MCP Tool

## Summary
Add a new MCP tool `gcp_role_context` to the Golazo Copilot server that assembles a self-contained context package for a specific role in a work item workflow. This enables orchestrator agents to delegate role work to subagents without passing full conversation history.

## Problem Statement
When an orchestrator agent delegates a role to a subagent, the subagent needs: (a) role instructions, (b) current work item state, (c) input artifacts from prior roles, and (d) previous role notes. Currently there is no single tool call that bundles all this context. Each piece must be separately loaded, requiring multiple tool calls and knowledge of the file layout.

## Business Case
- **Why now:** This is a prerequisite for GCP-0050 (orchestration spine) and GCP-0052 (integration tests). Without it, subagent delegation cannot work.
- **Impact:** Reduces orchestrator complexity from ~5 tool calls per role delegation to 1.
- **KPIs:** Bundle correctness (all required artifacts included), response time (<500ms).

## Stakeholders
- Golazo Copilot users (orchestrator agents, IDE users)
- Downstream: GCP-0050, GCP-0052

## Functional Requirements
1. New tool `gcp_role_context(work_item_id, role?, workspace_path?)` registered in server.py
2. Returns structured markdown with 4 sections:
   - `## Role Instructions` — full role markdown
   - `## Current State` — role, phase, deviation count, recent history
   - `## Input Artifacts` — file contents for each `inputs:` entry in role YAML front-matter
   - `## Previous Role Notes` — decision notes from the immediately preceding role
3. If `role` is omitted, reads `current_role` from state.json
4. Eagerly reads file contents (not just paths)
5. Missing artifacts listed with `[not yet created]`
6. Backward compatibility: roles without front-matter return instructions + state + warning

## Non-functional Requirements
- Response time < 500ms for typical work items (5-10 artifacts)
- Total bundle capped at configurable max (default 100KB)
- Truncation marker: `[truncated — full file at <path>]`
- Plain markdown output parseable by LLMs

## Proposed Approach

### Architecture
Follow the existing 3-layer pattern:
1. **Registration** (`server.py` → `list_tools()`): Add `Tool(name="gcp_role_context", ...)` with inputSchema
2. **Dispatch** (`server.py` → `_dispatch_tool()`): Add elif branch routing to `gcp_role_context()`
3. **Logic** (`tools/gcp_role_context.py`): New module with async function
4. **Formatter** (`server.py` → `format_role_context_result()`): Markdown assembly
5. **Export** (`tools/__init__.py`): Add to imports and `__all__`

### Tool Implementation (`tools/gcp_role_context.py`)
```python
async def gcp_role_context(
    work_item_id: str,
    role: str | None = None,
    workspace_path: str | None = None,
    max_bundle_size: int = 100_000,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
) -> dict
```

**Steps:**
1. Load state.json → resolve `role` (use current_role if None)
2. Load role instructions via `roles.loader.load_role_instructions()`
3. Parse YAML front-matter to extract `inputs:` list
4. For each input artifact, resolve path pattern with `{id}` substitution, read file content
5. Find previous role's decision notes (from ROLE_ORDER list)
6. Assemble dict with all sections
7. Apply size guard: if total > max_bundle_size, truncate largest artifacts first

### Size Guard Algorithm
1. Measure total bundle size
2. While total > max_bundle_size:
   - Find largest artifact section
   - Truncate to (remaining budget / artifact count)
   - Insert truncation marker with full file path
3. Always preserve: role instructions and state summary (never truncated)

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "work_item_id": {"type": "string", "description": "Work item ID"},
    "role": {"type": "string", "description": "Role name (defaults to current role)"},
    "workspace_path": {"type": "string", "description": "Workspace root path"}
  },
  "required": ["work_item_id"]
}
```

## Alternatives Considered
1. **Return file paths instead of contents** — Rejected: subagents may not have filesystem access
2. **Lazy loading via tool callbacks** — Rejected: adds complexity, subagents can't reliably call back
3. **Separate tools per section** — Rejected: multiplies tool calls, defeats purpose of bundling

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Large artifacts blow context window | Size guard with 100KB default cap |
| Role files missing front-matter | Backward-compat fallback with warning |
| File I/O latency | All reads are local filesystem, async where possible |

## Dependencies
- GCP-0048 (completed): YAML front-matter on role files
- `roles.loader.load_role_instructions()`: existing function
- `core.types.WorkItemState`: existing Pydantic model

## Migration / Rollout / Rollback
- **Rollout:** Bump version, rebuild package. Tool appears automatically in MCP tool list.
- **Rollback:** Remove tool registration from server.py, remove import, rebuild.
- **No data migration needed** — read-only tool.

## Observability
- Tool returns `status: "ok"` or `status: "error"` in result dict
- Includes `artifact_count`, `total_size`, `truncated` fields in result metadata

## Test Strategy
- Unit tests in `test_gcp_role_context.py`
- Test AC2-AC6 with mock filesystem (tmp_path fixtures)
- Test size guard with artificially large artifacts
- Test backward compat with role files missing front-matter
