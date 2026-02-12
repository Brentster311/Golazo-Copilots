# SFI-034 — Architect Decision Notes

## Architectural Decisions

1. **`kpi_analyzer.py` as standalone module**: Pure prompt-building logic. URL fetching is internal I/O but isolated with timeouts and error handling per-URL.

2. **Security posture for URL fetching**: Only HTTP/HTTPS schemes allowed. No auth headers or cookies sent. User-Agent identifies the app. No private IP/localhost fetching.

3. **Contracts defined**:
   - `analyze_kpi(app, kpi_id) → str` — gathers items, fetches URLs, returns prompt
   - `send_analysis_prompt(prompt)` — on CopilotPanel, handles connection + send + error display
   - `collect_urls(items) → set[str]` — deduplicates URL fields
   - `fetch_url_content(url, timeout) → dict` — returns `{"url", "content", "error"}`
   - `extract_text(html) → str` — strips HTML to text
   - `build_analysis_prompt(items, fetched_docs) → str` — constructs the 4-question prompt

4. **No new dependencies**: All stdlib (`urllib.request`, `html.parser`, `concurrent.futures`).

5. **Capability impact**: None — confirmed via registry. New module, stub replacement only.

## Items to Watch

- SSRF mitigation (URL scheme validation) should be implemented even though URLs come from server data
- Thread marshaling for `_launch_llm_analysis` → must use `root.after(0, ...)` for panel interaction
