# SFI-034: Analyze KPI with LLM

**Status**: IMPLEMENTED

## User Story

- **Title**: Analyze KPI with LLM via Copilot Chat
- **As a**: SFI Reporter user viewing my action items
- **I want**: to right-click a KPI row and select "Analyze with LLM" to get a structured analysis that explains what the KPI requires, why, what resources are affected, and step-by-step remediation guidance — streamed into the Copilot Chat panel
- **So that**: I can quickly understand what each KPI is asking me to do and how to address it without manually researching documentation links

- **Out of scope**:
  - Automatic remediation / auto-fixing resources
  - Persisting analyses to disk or database
  - Batch analysis of multiple KPIs at once
  - Editing or improving the analysis after it appears (user can ask follow-up questions in chat)

- **Assumptions**:
  - **Assumption (explicit)**: The Copilot Chat panel and SDK are already wired up and functional (SFI-033 + recent fixes). The analysis will be sent as a prompt to the existing Copilot session.
  - **Assumption (explicit)**: URL fetching will use simple HTTP GET + HTML-to-text extraction. Pages behind auth (e.g., internal wikis requiring AAD login) may return limited content; this is acceptable for v1.
  - **Assumption (explicit)**: The `url`, `ActionWikiLink`, `Remediation`, `AssetTypeLink0/1/2`, and `CustomGroupingLink` fields on each item contain the relevant documentation URLs.
  - **Assumption (explicit)**: All items for the KPI are already loaded in `current_data["detailed_items"]` (filtered by `_kpi_id`).

- **Acceptance Criteria (bulleted, testable)**:
  - [ ] Right-clicking a KPI row in the main Action Items table and selecting "🤖 Analyze with LLM" opens/activates the Copilot Chat panel and sends an analysis prompt scoped to that KPI
  - [ ] Right-clicking an item row in the detail drill-down modal and selecting "🤖 Analyze with LLM" triggers the same analysis flow for that item's KPI
  - [ ] The analysis prompt includes: all items belonging to the KPI (IDs, titles, services, owners, SLA status, ETA, asset types), plus content fetched from any non-empty URL fields (`url`, `ActionWikiLink`, `Remediation`, asset/grouping links)
  - [ ] The LLM response is structured around four questions: (1) What is being asked?, (2) Why?, (3) On what resources should I act?, (4) How — step-by-step remediation
  - [ ] URL fetching has a reasonable timeout (≤10s per URL) and gracefully degrades if a page is unreachable or returns an error
  - [ ] Status indicator in the Copilot panel shows progress during URL fetching and analysis (e.g., "Fetching KPI docs…", "Analyzing…")

- **Non-functional requirements**:
  - URL fetch timeout: ≤10 seconds per URL
  - Total analysis wall time: should be under 30 seconds for a typical KPI with ≤5 URLs
  - Text extracted from URLs should be truncated to avoid token overflow (e.g., first 4,000 chars per page)

- **Telemetry / metrics expected**:
  - Log: KPI ID analyzed, number of items, number of URLs fetched, fetch success/failure count, total analysis time

- **Rollout / rollback notes**:
  - Replaces the current "Not Yet Implemented" stub in `_launch_llm_analysis`
  - No new dependencies expected (uses stdlib `urllib` or existing `httpx`/`requests`)
  - Rollback: revert `_launch_llm_analysis` to the stub
