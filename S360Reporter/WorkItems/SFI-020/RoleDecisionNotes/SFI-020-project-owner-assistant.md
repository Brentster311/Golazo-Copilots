# SFI-020 — Project Owner Assistant Decision Notes

## Work Item
**SFI-020**: Right-Click KPI Row → Analyze with LLM (Core)

## Decomposition Decision

The original request was decomposed into **three stories** per Project Owner feedback:

1. **SFI-020** — Core: right-click → LLM analysis → display in modal → **save to disk**
2. **SFI-021** — Enhancement: fetch URL content to enrich the LLM prompt
3. **SFI-022** — Enhancement: view/manage previously saved analyses

**Why split?**
- The original story had multiple independent user-observable outcomes: context menu interaction, LLM integration, URL fetching, result persistence, and saved-analysis management.
- Each slice is independently shippable and testable.
- The Project Owner explicitly requested persistent storage ("NOT in memory only. I don't want to lose it."), which changed the scope enough to warrant a dedicated management story (SFI-022).

## Decisions Made

### Scope
- SFI-020 covers the **core end-to-end happy path**: right-click → send data to LLM → show result → save to disk.
- URL content fetching split to SFI-021 because it's an independent enrichment layer with its own complexity (timeouts, auth, truncation).
- Saved analysis management split to SFI-022 because viewing/loading/re-analyzing is a distinct user interaction from the initial analysis.

### Interface Type
- **GUI (tkinter)** — confirmed by the user's request ("right click a KPI row"), which is the existing S360Reporter desktop app.

### Target Platform
- **Windows** — consistent with all prior SFI work items and the existing `.spec` PyInstaller build.

### Data Persistence
- **JSON files on disk** under `%LOCALAPPDATA%/GUI/analyses/`, keyed by action item ID.
- Chose `%LOCALAPPDATA%` over `%TEMP%` because `%TEMP%` is volatile (cleaned on reboot) and the user explicitly wants durability. This is consistent with the `s360_client` cache pattern which also uses `%LOCALAPPDATA%`.

### User Type
- **Technical** — SFI engineers who understand KPI remediation workflows.

### Key Assumptions Justified
1. **Azure OpenAI as LLM provider**: The team operates in a Microsoft/Azure enterprise environment. Using Azure OpenAI aligns with existing auth patterns and compliance requirements.
2. **Env-var configuration**: No config file mechanism exists in the codebase. Environment variables are the lightest-weight approach for API keys/endpoints.
3. **Background thread for LLM call**: The existing app uses `threading.Thread` for data fetching (`_do_refresh`). The same pattern will be used for LLM calls.

## Risks
- LLM token limits could be exceeded if action item data is very large — mitigated by truncation strategies in prompt engineering.
- Azure OpenAI rate limits could impact experience during heavy usage — mitigated by clear error messages.
- `%LOCALAPPDATA%` storage could accumulate stale analyses over time — management/cleanup deferred to future work.
