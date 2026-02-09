# LLM-0011 — Project Owner Assistant Notes

## Origin
The `_summarize_s360.py` script had to import the private function `_build_context_prompt` from `llm_extender.url_fetcher` because `complete_with_url()` bundles fetch + LLM into one call, and the CDP fetch happened outside the library. There was no clean way to:
1. Feed pre-fetched content into the LLM with the standard context format
2. Use the same prompt construction logic without reaching into private internals

## Scope Decisions
- **Two-pronged approach**: Both a `LLMClient.complete_with_context()` method (convenient) and a public `build_context_prompt()` utility (flexible) are provided.
- **DRY refactor**: `complete_with_url` should internally delegate to `complete_with_context` to avoid duplicating the prompt-construction logic.
- **Backward compatible**: `_build_context_prompt` remains as an alias so existing internal imports don't break.
- **Single source only**: Multi-document context (e.g., multiple URLs) is a natural extension but out of scope for this story.

## Must-Ask Checklist
All items established from prior work items:
- **Interface type**: Python library (public API)
- **Target platform**: Cross-platform
- **Data persistence**: In-memory only
- **User type**: Technical (developers)
