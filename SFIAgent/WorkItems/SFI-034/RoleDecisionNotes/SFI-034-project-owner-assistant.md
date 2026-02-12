# SFI-034 — Project Owner Assistant Decision Notes

## Decisions Made

1. **UI approach — Copilot Chat panel**: Analysis streams into the existing side panel rather than a separate modal. Rationale: avoids building throwaway UI, reuses the already-working streaming infrastructure, and allows follow-up questions in the same chat context.

2. **Live URL fetching**: The tool will HTTP-fetch KPI documentation URLs and extract text content. This is essential for answering "How?" with step-by-step remediation guidance that's specific to the KPI. Pages behind auth may return errors — this is acceptable; the LLM will note when docs were unavailable.

3. **Scope — both tables**: The right-click "Analyze with LLM" works from both the main KPI table and the detail drill-down modal. Both already have the right-click menu wired to `_launch_llm_analysis`, so the implementation touches the same function.

4. **Single user story**: This is one user-observable outcome (right-click → analysis in chat). URL fetching, prompt construction, and chat integration are implementation details, not separate user stories.

## Clarifications from User

- **Trigger**: Right-click on a KPI row → "Analyze with LLM"
- **Context**: All items belonging to that KPI (not just the one row clicked)
- **Four questions**: What?, Why?, On what?, How (step-by-step)?
- **URL fetching**: Yes — fetch live content from KPI documentation links
- **KPI URLs to visit**: `url`, `ActionWikiLink`, `Remediation`, `AssetTypeLink0/1/2`, `CustomGroupingLink` fields; also similar/common URLs per KPI type

## Assumptions Logged

- Copilot Chat panel + SDK already functional
- HTTP GET sufficient for URL fetching (no JS rendering needed)
- All KPI items already in memory (no additional API calls to load items)
- Auth-gated pages gracefully degrade (empty content, not a crash)
