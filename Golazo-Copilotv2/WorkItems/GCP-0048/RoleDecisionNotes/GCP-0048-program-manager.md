# GCP-0048 — Program Manager Decision Notes

## Design Decisions

1. **YAML front-matter format chosen** over JSON/sidecar files — industry standard for markdown metadata, parseable and human-readable
2. **Front-matter placed before `<!-- Last Updated -->` comment** — standard YAML front-matter goes at absolute top of file between `---` delimiters
3. **`tools:` list includes `gcp_status` and `gcp_transition` for every role** — these are universal; role-specific tools (e.g., `gcp_capabilities`, `gcp_create_workitem`) added per-role
4. **Implicit reference replacement uses explicit paths + tool call syntax** — e.g., "return to Developer" becomes "call `gcp_transition(role='developer')`"
5. **Refactor output filename NOT changed** — `{id}-refactor.md` is used in `transitions.py` (`get_role_notes_path`); changing it would be a code change out of scope. Documented as pre-existing naming convention.

## Risk Assessment
- Low risk: all changes are to markdown files, no Python code modifications
- Output validator backward compat confirmed by reading parser source
- Full test suite validation planned
