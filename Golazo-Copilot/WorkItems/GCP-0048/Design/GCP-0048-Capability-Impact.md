# GCP-0048 Capability Impact

## Impact Analysis Results

### Directly Affected
- **role-loader**: Load role instructions with local-override priority over package defaults
  - Contract: `loader.py` reads raw markdown content and returns it as-is
  - Impact: NONE — front-matter is just part of the markdown string, no parsing changes needed
  - The 10 role files are the key_files of this capability

### Transitively Affected (dependents)
- **tool-create-workitem**: Creates workspace; copies role files via bootstrap
  - Impact: NONE — copies files verbatim
- **tool-transition**: Validates required outputs from role file content
  - Impact: NONE — `output_validator.parse_required_outputs()` uses regex to find `## Required Outputs` section, unaffected by front-matter at top
- **tool-status**: Reads role content for output validation and next-steps
  - Impact: NONE — same parser path as transition
- **tool-bootstrap**: Copies role files from package defaults to `.github/roles/`
  - Impact: NONE — copies files verbatim
- **mcp-server**: Routes calls and formats responses
  - Impact: NONE — passes through role content from loader

### Contract Implications
- No new, changed, or removed public interfaces
- Role files remain markdown strings consumed by LLM and parsed by output_validator
- The YAML front-matter is additive metadata — no existing consumer parses or depends on the file starting with `<!-- ... -->`
