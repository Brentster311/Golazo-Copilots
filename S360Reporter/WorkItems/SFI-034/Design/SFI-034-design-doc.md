# SFI-034 Design Document — Analyze KPI with LLM

## Summary

Replace the "🤖 Analyze with LLM" stub with a working feature that gathers all action items for a KPI, fetches content from their documentation URLs, and sends a structured analysis prompt to the Copilot Chat panel. The LLM responds with: (1) What is being asked, (2) Why, (3) What resources are affected, and (4) Step-by-step remediation.

## Problem Statement

Users right-click a KPI row and see "Analyze with LLM" but get a "Not Yet Implemented" dialog. KPIs are often opaque — users don't know what's required, why, or how to remediate. Answering these questions requires reading multiple documentation pages and correlating data across items. An LLM can synthesize this automatically.

## Business Case

- **Why now**: Copilot Chat is already integrated (SFI-033 + recent fixes). The plumbing exists — this adds the last-mile analysis capability.
- **Impact**: Reduces time-to-understand per KPI from 15–30+ minutes of manual doc reading to ~20 seconds. Directly unblocks remediation work.
- **KPIs**: Feature adoption (% of KPI analyses triggered), user satisfaction (follow-up question rate as proxy for completeness).

## Stakeholders

- **End users**: SFI/QEI action item owners who need remediation guidance
- **Developers**: Maintainers of the S360Reporter app

## Functional Requirements

1. **Right-click trigger**: "🤖 Analyze with LLM" on any KPI row (main table) or item row (detail modal)
2. **Data gathering**: Collect all items for the selected KPI from `current_data["detailed_items"]` filtered by `_kpi_id`
3. **URL fetching**: For each unique URL across items (`url`, `ActionWikiLink`, `Remediation`, `AssetTypeLink0/1/2`, `CustomGroupingLink`), fetch page content via HTTP GET, extract readable text, truncate to 4,000 chars each
4. **Prompt construction**: Build a structured prompt with KPI metadata, item summaries, and fetched docs, asking the four analysis questions
5. **Chat integration**: Auto-open Copilot Chat panel if closed, inject the analysis prompt as if the user typed it, stream the LLM response
6. **Status feedback**: Show fetch/analysis progress in the Copilot panel status indicator

## Non-Functional Requirements

- URL fetch timeout: ≤10s per URL, total ≤30s for typical KPI
- Truncate fetched text to 4,000 chars per URL (avoid token overflow)
- Total prompt size: should not exceed ~32K chars including all item data + fetched content
- Graceful degradation: unreachable URLs produce a note, not a failure

## Proposed Approach

### Architecture

```
Right-click KPI → _launch_llm_analysis(parent, item)
  │
  ├── 1. Extract kpi_id from item
  ├── 2. Gather all items for that kpi_id from app.current_data
  ├── 3. Collect unique URLs from all items
  ├── 4. Fetch URL content (threaded, with timeout)
  ├── 5. Build analysis prompt
  ├── 6. Open/activate Copilot Chat panel
  └── 7. Send prompt to Copilot session
         └── Response streams in chat panel
```

### Key Components

1. **`kpi_analyzer.py`** (new module): Contains `analyze_kpi(app, kpi_id)` which:
   - Gathers items, collects URLs, fetches content
   - Builds the structured prompt
   - Returns the prompt string

2. **`_launch_llm_analysis`** (modified in `dialogs.py`): Instead of showing a stub messagebox:
   - Resolves `kpi_id` from the clicked item
   - Calls `kpi_analyzer.analyze_kpi()` on a background thread (URL fetching)
   - When done, opens Copilot panel and sends the prompt

3. **`copilot_panel.py`** (minor addition): Add a public method `send_analysis_prompt(prompt)` that programmatically sends a message to the session (reusing `_on_send` logic but with a provided prompt instead of entry field text)

4. **URL fetching** (in `kpi_analyzer.py`):
   - Use `urllib.request` (no new dependencies) or `httpx` if already available
   - ThreadPoolExecutor for parallel fetches (max 5 concurrent)
   - 10s timeout per URL
   - HTML → text via simple tag stripping (regex or `html.parser`) — no new dependency
   - Truncate each page to 4,000 chars

### Prompt Template

```
Analyze the following SFI/QEI KPI and its action items.

## KPI: {kpi_name} ({kpi_id})
Items: {count} total, {out_of_sla} out of SLA

## Action Items
{for each item: id, title, service, owner, SLA status, ETA, assets}

## Documentation
{for each URL: source_field, url, extracted_text}

## Questions to Answer
1. **What is being asked?** — Explain what this KPI requires in plain language.
2. **Why?** — Why does this requirement exist? What risk does it mitigate?
3. **On what resources?** — List the specific Azure resources, services, or assets that need action, based on the item data above.
4. **How? (Step by step)** — Provide concrete remediation steps, referencing the documentation above where applicable.
```

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| New Copilot tool (`analyze_kpi` tool) for the LLM to self-invoke | Overly indirect — user triggers analysis, not the LLM. The prompt approach is simpler and more predictable. |
| Modal dialog for results | User chose Copilot Chat panel. Modal prevents follow-up questions. |
| No URL fetching — rely on LLM's training data | Many KPIs have org-specific requirements. Fetched docs provide accurate, current guidance. |
| Use `requests` or `httpx` for HTTP | `urllib.request` is stdlib, avoids adding deps. If `httpx` is already installed, it could be used, but not worth a new dependency. |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Auth-gated URLs return 401/403 | Missing documentation context | Include note in prompt: "Documentation unavailable (access denied)." LLM can still provide general guidance. |
| Large KPIs (50+ items) overflow token limit | Prompt too large, API error or truncated response | Summarize items (key fields only), cap at 30 items, note truncation. |
| Slow URL fetching (many URLs, slow servers) | User waits >30s | Parallel fetches (ThreadPoolExecutor), 10s timeout, show progress. Cap at 10 unique URLs. |
| LLM doesn't follow the 4-question format | Unstructured response | Explicit prompt instructions + system message context. Acceptable for v1. |

## Open Questions

- None currently. All key decisions resolved with user.

## Dependencies

- Copilot Chat panel + SDK (already implemented)
- `current_data` loaded with detailed items (existing data pipeline)
- Network access for URL fetching

## Migration / Rollout / Rollback

- **Migration**: None — replaces a stub function
- **Rollout**: Ship in next build. Feature is behind right-click menu (low discoverability risk).
- **Rollback**: Revert `_launch_llm_analysis` to the stub messagebox

## Observability Plan

- Log at INFO level: KPI ID, item count, URL count, fetch success/fail, total analysis time
- Log at DEBUG: individual URL fetch times, prompt size
- Errors: log at ERROR level with KPI context

## Test Strategy Summary

- **Unit tests**: Prompt construction with mock items/URLs, URL text extraction, truncation logic
- **Integration tests**: End-to-end flow with mocked HTTP responses and mocked Copilot session
- **Manual tests**: Verify right-click → analysis flow in running app, check 4-question format in response
