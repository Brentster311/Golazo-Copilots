# SFI-020: Right-Click KPI Row → Analyze with LLM (Core)

**Status**: IMPLEMENTED

---

## Decomposition Rationale

The original request ("right-click a KPI row and analyze with LLM") was too large — it contained multiple user-observable outcomes (context menu, LLM integration, URL content fetching, result display, persistent storage, and saved-analysis management). It has been decomposed into three independent vertical slices:

| Story | Title | Independently Deliverable? |
|-------|-------|---------------------------|
| **SFI-020** | Right-click → Analyze with LLM + save result | ✅ Core happy path |
| **SFI-021** | URL content enrichment for LLM analysis | ✅ Enhances analysis quality |
| **SFI-022** | View & manage saved LLM analyses | ✅ Leverages saved results |

---

## User Story

**Title**: Right-click KPI row → Analyze with LLM and save result to disk

**As a**: SFI engineer using the SFIReporter desktop app  
**I want**: To right-click a KPI row, select "Analyze with LLM," see a structured analysis in a modal, and have the result automatically saved to disk  
**So that**: I can quickly understand what is being asked, the steps to remediate, which resources need repair, and the risk of delay — and I don't lose the analysis when I close the app

---

## Out of Scope

- Following/fetching embedded URLs for richer LLM context (SFI-021)
- Viewing or managing previously saved analyses (SFI-022)
- Batch/bulk LLM analysis of multiple rows at once
- LLM-based auto-remediation or auto-updating of ETAs
- Customizable LLM prompts from the UI
- Right-click menus on Service or Program treeviews (KPI/Action Items only)
- Streaming/token-by-token display of LLM output

---

## Assumptions

- **Assumption (explicit)**: The right-click context menu will be added to the Action Items treeview (`self.tree_kpis`) and the drill-down treeview in `DrillDownModal`, since both display KPI-level rows
- **Assumption (explicit)**: The LLM provider will be Azure OpenAI (GPT-4o or equivalent), consistent with enterprise Microsoft tooling. Configuration (endpoint, API key, deployment name) will come from environment variables, following the existing config pattern in `s360_client`
- **Assumption (explicit)**: The LLM prompt will use the action item's existing data fields (title, status, SLA, dates, ownership, service tree, remediation text, etc.) — URL content fetching is deferred to SFI-021
- **Assumption (explicit)**: The analysis result will be displayed in a new modal dialog with sections: Mission, Steps to Done, Resources Needing Repair, and Risk of Delay
- **Assumption (explicit)**: Results will be persisted as JSON files under `%LOCALAPPDATA%/sfireporter/analyses/` keyed by action item ID — consistent with the durable `s360_client` cache in `%LOCALAPPDATA%`, not the volatile `%TEMP%` user-data cache
- **Assumption (explicit)**: The analysis runs on a background thread so the UI stays responsive, with a progress/spinner indicator (consistent with existing `_do_refresh` threading pattern)

---

## Acceptance Criteria

- [ ] Right-clicking a KPI row in the Action Items treeview or DrillDownModal treeview shows a context menu with "Analyze with LLM"
- [ ] Selecting "Analyze with LLM" sends action item data to Azure OpenAI and displays a structured response in a modal with labeled sections (Mission, Steps to Done, Resources Needing Repair, Risk of Delay)
- [ ] The LLM analysis result is automatically saved to a JSON file on disk under `%LOCALAPPDATA%/sfireporter/analyses/` keyed by action item ID
- [ ] The UI remains responsive during analysis (background thread + progress indicator)
- [ ] If the LLM API is unreachable or misconfigured, a clear error message is shown to the user

---

## Non-Functional Requirements

- LLM call should complete within 30 seconds under normal conditions
- API key / endpoint must never be logged or displayed in the UI
- Saved analysis files must be valid JSON and include a timestamp
- Should work on Windows (primary platform)

---

## Telemetry / Metrics Expected

- Count of "Analyze with LLM" invocations per session
- Average LLM response time
- Error rate (LLM unavailable / misconfigured)

---

## Rollout / Rollback Notes

- Feature is additive — no existing functionality is modified
- If LLM provider is unavailable, the context menu can show an informative error
- Rollback: remove context menu binding + analysis module; saved JSON files are inert
