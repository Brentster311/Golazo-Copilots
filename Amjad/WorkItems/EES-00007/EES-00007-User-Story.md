# EES-00007 — User Story

**Status**: BACKLOG

## Related Work Items
- **Depends on:** EES-00005 (GUI Application)
- **Part of:** Expert System decomposition

---

## User Story

- **Title:** Retrieve Incident Data from Kusto by Incident ID
- **As a:** technical user (developer/engineer)
- **I want:** to enter an incident ID in the GUI and have the application retrieve the incident text from Kusto (Azure Data Explorer), instead of loading from a local file
- **So that:** I can process real incidents directly from our data source without manually exporting and saving text files

- **Out of scope:**
  - Kusto query authoring/editing in the GUI
  - Batch processing of multiple incidents
  - File-based loading removal (both methods should coexist)
  - Problem Solving phase

- **Assumptions:**
  - **Assumption (explicit):** Kusto cluster: `https://acciafollowercentralus.centralus.kusto.windows.net`, database: `IcmDataWarehouse`, table: `IncidentDescriptions`
  - **Assumption (explicit):** Authentication to Kusto uses the same Azure identity pattern (ChainedTokenCredential)
  - **Assumption (explicit):** The GUI's Process Incident tab will offer both file browse and incident ID entry as input methods

- **Acceptance Criteria (bulleted, testable):**
  - The Process Incident tab has an Incident ID text field and a "Fetch from Kusto" button alongside the existing file browse
  - Entering an incident ID and clicking Fetch retrieves the incident text from Kusto
  - Retrieved text is displayed in the incident text pane, identical to file-loaded text
  - The fetch operation is non-blocking (runs on a background thread with progress indication)
  - Kusto connection settings are configurable (cluster, database)
  - Error messages are shown if the incident ID is not found or Kusto is unreachable

- **Non-functional requirements:**
  - Kusto fetch must not block the GUI (same worker pattern as LLM calls)
  - Kusto connection details persisted alongside Azure OpenAI settings

- **Telemetry / metrics expected:**
  - None

- **Rollout / rollback notes:**
  - Additive change; file-based loading continues to work
  - Kusto cluster/database/table details are known; additive change
