# GCP-0049 — Domain Expert Notes

## Domain Analysis
This work item is internal MCP tooling. The relevant domain is the MCP server protocol and Golazo Copilot's role file format.

### Domain: MCP Tool Development
- **Pattern:** Tool follows established 3-layer pattern (register → dispatch → logic)
- **YAML front-matter parsing:** Must use `yaml.safe_load()` on content between `---` markers. The front-matter was standardized in GCP-0048.
- **Role file loading:** Use `roles.loader.load_role_instructions()` which handles `.github/roles/` override → package defaults fallback

### Domain: Context Window Management
- LLM context windows range from 8K–200K tokens. 100KB (~25K tokens) is a safe default cap.
- Truncation should preserve the beginning of artifacts (most important context) and append a marker.

## No External Domain Expertise Required
This is internal tooling with no platform dependencies, external APIs, or compliance requirements.
