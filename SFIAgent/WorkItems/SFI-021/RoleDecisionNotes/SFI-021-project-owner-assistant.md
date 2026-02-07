# SFI-021 — Project Owner Assistant Decision Notes

## Work Item
**SFI-021**: URL Content Enrichment for LLM Analysis

## Decisions Made

### Why a Separate Story
- URL fetching is an independent enrichment layer with its own complexity: HTTP timeouts, authentication handling, HTML-to-text conversion, token limit management.
- Without this story, SFI-020 still delivers a complete (if less detailed) analysis using the action item's structured data fields.
- This story can be tested independently by comparing analysis quality with and without URL content.

### Scope
- Fetch content from the direct URLs embedded in action item fields only — no recursive crawling.
- Best-effort: skip URLs that are unreachable, auth-gated, or time out.
- Clean fetched HTML to plain text before including in the LLM prompt.

### Interface / Platform / Persistence / User Type
- Same as SFI-020: GUI (tkinter), Windows, no additional persistence (content is ephemeral — used in the prompt then discarded), technical users.

### Key Design Decisions
1. **Per-URL timeout (10s)**: Prevents a single slow URL from blocking the entire analysis.
2. **Parallel fetching**: Multiple URLs fetched concurrently to stay within a 30s total budget.
3. **No credential forwarding**: We don't send user credentials to arbitrary URLs — 401/403 responses are skipped.
4. **Truncation strategy**: Needed to keep total prompt within LLM token limits — details deferred to design phase.

## Risks
- Many enterprise URLs may be SSO-gated → most URLs may be unfetchable. The analysis should still be useful with partial content.
- HTML-to-text conversion quality varies — may need a robust library (e.g., `beautifulsoup4`).
