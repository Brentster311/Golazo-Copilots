# SFI-034 Design Review Comments

## Overall Assessment

Design is clear, feasible, and well-scoped. The approach of building a `kpi_analyzer.py` module and sending analysis via the existing Copilot Chat panel is sound. A few items to tighten before implementation.

## Comments

### 1. [MINOR] Item count cap should be explicit in prompt builder
The design mentions "cap at 30 items" for large KPIs but this isn't reflected in the prompt template section. The prompt builder should include a clear note to the LLM when items are truncated: "Showing 30 of {total} items."

### 2. [MINOR] URL deduplication
Multiple items in the same KPI will have the same `url` value (it's typically the KPI-level docs link). The design correctly says "unique URLs" but implementation should deduplicate across all URL fields across all items before fetching.

### 3. [IMPORTANT] Graceful handling when Copilot panel is not connected
If `_launch_llm_analysis` opens the panel and sends a prompt but the SDK isn't connected yet, the prompt could be lost. The `send_analysis_prompt` method should handle the connection lifecycle (ensure connected → then send).

### 4. [MINOR] Thread safety for `_launch_llm_analysis`
URL fetching runs on a background thread, then posts the prompt to the Copilot panel. Ensure the cross-thread handoff uses `root.after(0, ...)` to marshal back to the Tk main thread before interacting with the panel.

### 5. [NOTE] HTML text extraction quality
Simple regex/html.parser stripping will work for most docs pages but may produce noisy output (nav bars, footers, script content). For v1 this is acceptable — future improvement could use a content extraction heuristic.

### 6. [MINOR] `_kpi_id` field access 
When clicking in the detail modal, the item always has `_kpi_id`. But in the main KPI table, the click resolves to items grouped by KPI display name. Ensure the right-click handler consistently provides `_kpi_id` to the analyzer.

## Verdict

**Approved with comments** — proceed to Architect. Comments 3 and 4 (connection handling, thread safety) should be addressed in implementation.

---

## Architect Notes

### Architectural Review

Design is architecturally sound. Key observations:

1. **Module boundary — `kpi_analyzer.py`**: Good separation. This module should be a pure function: items in → prompt string out. URL fetching is I/O and should be isolated (passed as a fetcher function or results dict) to keep the module testable without network mocking.

2. **Security — URL fetching**: 
   - URLs come from API data (server-controlled), not user input → SSRF risk is low but present
   - **Mitigation**: Only fetch HTTP/HTTPS schemes, reject `file://`, `ftp://`, localhost, private IPs
   - User-Agent header should identify the app to avoid being blocked
   - No credentials should be sent in URL fetch requests (no cookies, no auth headers)

3. **Contract: `send_analysis_prompt(prompt: str) → None`**:
   - Input: prompt string (already constructed)
   - Side effects: opens panel if closed, connects if needed, sends to session
   - Error handling: displays error in chat panel, does not raise
   - Must marshal to Tk main thread if called from background thread

4. **Contract: `analyze_kpi(app, kpi_id: str) → str`**:
   - Input: app instance + KPI ID
   - Output: fully constructed prompt string
   - Pure function once URL content is provided
   - URL fetching happens inside but is parallelized with timeout

5. **Dependency check**: No new dependencies. `urllib.request`, `html.parser`, `concurrent.futures` are all stdlib.

6. **Failure isolation**: URL fetch failures are isolated per-URL and don't abort the analysis. Session errors are caught by the existing Copilot panel error handler.

7. **Capability registry**: No existing capabilities affected (confirmed via impact analysis).

### Verdict

**Approved** — proceed to Developer.
