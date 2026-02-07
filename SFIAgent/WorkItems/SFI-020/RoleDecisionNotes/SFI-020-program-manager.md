# SFI-020 — Program Manager Decision Notes

## Work Item
**SFI-020**: Right-Click KPI Row → Analyze with LLM (Core)

## Design Decisions

### Module Structure
- Split LLM concerns into two new modules (`llm_client.py`, `llm_storage.py`) rather than adding everything to `tk_app.py`.
- **Rationale**: `tk_app.py` is already ~2900 lines. Keeping API logic and file I/O separate improves testability and maintainability.

### Azure OpenAI SDK Choice
- Chose the `openai` package (official OpenAI Python SDK) which supports Azure OpenAI natively via `AzureOpenAI` client.
- **Alternatives considered**: `azure-ai-openai` (not a real package), `httpx` direct calls (more boilerplate), `langchain` (too heavy for a single call).
- **Decision**: `openai>=1.0.0` is the lightest, most standard option with built-in Azure support.

### Prompt Engineering Strategy
- Structured system prompt with explicit section headers (Mission, Steps to Done, Resources, Risk of Delay).
- Low temperature (0.3) for factual, deterministic output.
- **Rationale**: Fixed section headers enable reliable parsing and consistent UX. The user asked for exactly these four outputs.

### Storage Key Strategy
- Keyed by `action_item_id` (not `kpi_id` or a hash).
- **Rationale**: Action item IDs are unique, human-readable, and stable. One analysis per action item is the natural mental model.

### Extensibility Stub for SFI-021
- `build_prompt()` will accept `url_content: dict[str, str] | None = None` from day one.
- **Rationale**: Adding a parameter later changes the function signature and potentially breaks tests. Adding the stub now is zero-cost.

### AnalysisModal vs. Reusing ItemDetailsModal
- Created a new `AnalysisModal` rather than reusing `ItemDetailsModal`.
- **Rationale**: `ItemDetailsModal` renders structured field-by-field data with specific tags and groupings. The analysis is free-form markdown text with different sections. The two modals share the same *pattern* (Toplevel + scrollable Text) but have different content rendering logic.

## Review Disposition
- All review comments addressed in the design doc.
- Four ⚠️ notes flagged for developer attention (PyInstaller size, token truncation, config error UX, concurrency guard).

## Test Coverage Assessment
- 17 test cases covering: config loading, prompt building, API call + errors, storage CRUD, context menu binding, integration flow, security (key masking).
- Sufficient for the 5 acceptance criteria.
