# GCP-0049 — Architect Notes

## Architectural Review
- **Alignment:** Follows established 3-layer tool pattern ✅
- **Boundaries:** New tool is read-only — no state mutations ✅
- **Contracts:** Clear input schema, structured dict output ✅
- **Failure isolation:** Errors in gcp_role_context cannot affect other tools ✅

## Security Review
- No secrets/tokens/PII handled
- No new auth boundaries — uses same workspace_path resolution
- No attack surface expansion — read-only filesystem operations
- No new dependencies added

## Architecture Decisions
1. YAML front-matter parsing: reuse `yaml.safe_load()` on role content — already used in test_role_self_contained.py
2. Role order: import ROLE_ORDER constant from existing codebase (or define locally)
3. File path resolution: use same `resolve_work_items_dir()` pattern as other tools
4. The formatter should produce markdown that is self-documenting (section headers serve as parsing anchors)

## Naming
- Module: `tools/gcp_role_context.py` — matches `tools/gcp_*.py` pattern ✅
- Function: `gcp_role_context()` — matches `gcp_*()` pattern ✅
- Formatter: `format_role_context_result()` — matches existing pattern ✅
