# GCP-0038: Design Doc — Capability Registry Tool

## Summary
Add a new `gcp_capabilities` MCP tool that reads a `capabilities.yaml` file from the project root and provides four actions: `list`, `show`, `impact`, and `validate`. This enables impact analysis when changing shared contracts/files.

## Problem Statement
GCP-0036 demonstrated that changing a shared contract (version comment format) led to a downstream miss (stale detection algorithm not updated). There was no structured way for roles to discover what capabilities depend on a given file or contract. The capability registry fills this gap.

## Business Case
- **Why now**: Direct outcome of GCP-0036 retro — the miss is fresh and the fix is clear
- **Impact**: Prevents future downstream misses in any project using GCP
- **KPIs**: Zero downstream misses on work items where capabilities registry is maintained and impact analysis is run

## Stakeholders
- GCP users (primary consumers)
- QA/Architect roles (primary beneficiaries of impact analysis)

## Functional Requirements

### Data Model
```yaml
# capabilities.yaml (user-maintained at project root)
capabilities:
  - name: string           # unique identifier
    description: string     # one-line summary
    key_files:              # files implementing this capability (relative paths)
      - path/to/file.py
    contracts:              # shared formats/interfaces/conventions
      - "Description of contract"
    depends_on:             # other capability names this depends on
      - capability-name
```

### Actions

**`list`** — Returns summary of all capabilities (name + description).

**`show(capability)`** — Returns full card for one capability:
- description, key_files, contracts, depends_on
- `depended_on_by` (computed from inverse of all `depends_on`)

**`impact(files)`** — Given a list of file paths:
1. Find all capabilities whose `key_files` match any input file (using suffix/basename matching for robustness)
2. Compute transitive dependents (capabilities that depend on the matched ones, recursively)
3. Return: directly affected capabilities + transitively affected capabilities

**`validate`** — For each capability, check that all `key_files` exist on disk. Return pass/fail per capability.

### YAML Parsing
Use Python's `yaml` module from PyYAML. Add `PyYAML>=6.0` to `pyproject.toml` dependencies.

**Alternative considered**: Hand-parse the simple YAML subset. Rejected — PyYAML is battle-tested, widely available, and the YAML schema may grow.

## Non-Functional Requirements
- No new dependencies beyond PyYAML
- Validate action <100ms for up to 50 capabilities
- Graceful handling when `capabilities.yaml` missing (not an error)

## Proposed Approach

### New files
1. `tools/gcp_capabilities.py` — Tool implementation
2. `tests/test_gcp_capabilities.py` — Tests

### Modified files
3. `server.py` — Import, Tool schema, call_tool handler
4. `tools/__init__.py` — Export
5. `pyproject.toml` — Add PyYAML dependency

### Implementation Detail

```python
# tools/gcp_capabilities.py

async def gcp_capabilities(
    action: str,                    # "list" | "show" | "impact" | "validate"
    capability: str | None = None,  # for "show"
    files: list[str] | None = None, # for "impact"
    workspace_path: Path | str | None = None,
) -> dict:
```

**File matching strategy for `impact`**: Match input files against `key_files` using path suffix matching. If the input is `tools/gcp_status.py`, it matches a key_file entry of `src/golazo_copilot/tools/gcp_status.py` (suffix match). This handles the common case where the user provides a relative path from their working directory.

**Transitive dependents**: BFS from directly-affected capabilities through the `depended_on_by` graph.

**Cycle detection**: The `depends_on` graph could theoretically have cycles. Use a visited set during BFS to prevent infinite loops.

### Server integration
Follow existing pattern (6th tool):
- Import at top of `server.py`
- Add `Tool(name="gcp_capabilities", ...)` to `list_tools()`
- Add `elif name == "gcp_capabilities":` handler in `call_tool()`
- Resolve workspace_path to find `capabilities.yaml`

### Output format (call_tool)
```
# For action="list":
**Capability Registry** (N capabilities)
- **name1**: description1
- **name2**: description2

# For action="show":
**Capability: name**
- Description: ...
- Key Files: file1, file2
- Contracts: contract1, contract2
- Depends On: cap1, cap2
- Depended On By: cap3, cap4

# For action="impact":
**Impact Analysis** (N files → M capabilities affected)

Directly Affected:
- **cap1**: description (key_files: file1)

Transitively Affected (dependents):
- **cap3**: description (depends on: cap1)

# For action="validate":
**Registry Validation**
[OK] cap1: all 3 key_files exist
[FAIL] cap2: missing src/foo.py
```

## Risks & Mitigations
| Risk | Mitigation |
|---|---|
| Registry goes stale | `validate` action detects missing files; future role integration prompts updates |
| Users don't adopt | Tool is opt-in; zero impact on projects without `capabilities.yaml` |
| Circular dependencies | BFS with visited set prevents infinite loops |
| PyYAML not installed | Add to `pyproject.toml` dependencies; clear error message if import fails |

## Dependencies
- PyYAML >= 6.0 (new dependency)

## Test Strategy
- One test class per action (AC1-AC6)
- Fixture creates temp workspace with sample `capabilities.yaml`
- Test impact traversal with diamond dependency pattern
- Test cycle handling
- Test missing `capabilities.yaml`
- Test file matching (exact, suffix, basename)
