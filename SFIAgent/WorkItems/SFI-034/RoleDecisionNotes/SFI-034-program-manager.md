# SFI-034 — Program Manager Decision Notes

## Key Design Decisions

1. **New module `kpi_analyzer.py`** rather than embedding logic in `dialogs.py` or `copilot_tools.py`. The analysis involves URL fetching, prompt building, and data gathering — distinct from both UI dialog code and Copilot tool definitions. Keeps concerns separated.

2. **Prompt-based approach over Copilot Tool**: Analysis is user-triggered from a specific context (KPI row), not model-initiated. A pre-built prompt with all context is simpler and more predictable than giving the model a tool and hoping it calls it correctly with the right KPI ID.

3. **`urllib.request` for URL fetching**: Avoids new dependencies. `httpx` or `requests` would work but aren't needed for simple GET + text extraction. If already in the environment, could use them, but `urllib` is guaranteed present.

4. **Parallel URL fetching with ThreadPoolExecutor**: URLs are independent, fetching serially would be too slow. 5 concurrent workers, 10s timeout each, max 10 URLs total.

5. **HTML-to-text via stdlib `html.parser`**: No dependency on `beautifulsoup4` or `lxml`. Simple tag stripping is sufficient — we don't need structured parsing, just readable text for LLM context.

6. **Public `send_analysis_prompt` on CopilotPanel**: Avoids reaching into private internals. The panel gets a clean API for programmatic prompt injection.

## Risks Accepted

- Auth-gated URLs will return errors or empty content. Acceptable for v1 — LLM can still provide general guidance based on KPI name and item data.
- Large KPIs may need item truncation. Will cap at 30 items in prompt, summarize with key fields only.

## Sequencing

1. Build `kpi_analyzer.py` (data gathering, URL fetching, prompt construction)
2. Add `send_analysis_prompt` to `CopilotPanel`
3. Replace `_launch_llm_analysis` stub in `dialogs.py`
4. Write tests
