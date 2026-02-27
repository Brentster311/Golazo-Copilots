# SFI-020 — Architect Decision Notes

## Work Item
**SFI-020**: Right-Click KPI Row → Analyze with LLM (Core)

## Architecture Review

### ✅ Module Boundaries — Approved
- `llm_client.py` (API + prompt) and `llm_storage.py` (file I/O) are cleanly separated.
- Neither module imports tkinter — they're pure logic, fully testable without GUI.
- `tk_app.py` orchestrates: binds events → calls `llm_client` → calls `llm_storage` → renders modal.

### ✅ Storage Pattern — Approved
- `%LOCALAPPDATA%/GUI/analyses/<action_item_id>.json` is durable and consistent with `s360_client` cache.
- Atomic write (`tmp` + `os.replace`) matches `data.py` column cache pattern.
- `schema_version: 1` enables forward-compatible migration.

### ✅ Threading — Approved
- Daemon thread + `root.after(0, callback)` is the established pattern in the codebase.
- No shared mutable state between threads (item data is read-only, result is produced and handed off).

### ✅ Dependency Choice — Approved
- `openai>=1.0.0` is minimal and supports Azure natively. No need for heavier frameworks.

### Architecture Decisions

#### AD-1: Dict vs. Typed Model for Action Items
- **Decision**: Keep `dict` for action item data.
- **Rationale**: All existing code passes action items as dicts. Introducing a typed model would require refactoring `data.py`, `cache.py`, and `tk_app.py` — a separate work item.
- **Future**: A typed `ActionItem` dataclass could be introduced when the codebase matures.

#### AD-2: Prompt Builder Extensibility
- **Decision**: `build_prompt(item, url_content=None)` — optional param from day one.
- **Rationale**: SFI-021 will add URL content enrichment. Having the parameter stub avoids a breaking change.

#### AD-3: Analysis Modal as New Class
- **Decision**: New `AnalysisModal` class rather than reusing `ItemDetailsModal`.
- **Rationale**: Different rendering logic (markdown-style sections vs. structured field groups). Shared pattern (Toplevel + Text widget) but divergent content.

#### AD-4: Error Strategy
- **Decision**: Three error classes — `LLMConfigError` (missing env vars), `LLMError` (API failures), and standard `OSError` (storage).
- **Rationale**: Distinct error types enable distinct UX: config errors show setup instructions, API errors show retry guidance, storage errors show "saved failed but here's the analysis."

### Performance Considerations
- LLM call is I/O-bound (network); background thread is appropriate.
- No caching of LLM responses in-memory — each analysis goes to disk. SFI-022 will add re-read.
- Token truncation strategy needed for large items (>3000 tokens input).

### Security Sign-off
- API key: env var only, masked in `__repr__`, never logged ✅
- Data stays in Azure tenant (Azure OpenAI, not public OpenAI) ✅
- No credential forwarding to external URLs (that's SFI-021's concern) ✅

## Sign-off
- **Architecture Status**: ✅ Approved for development
