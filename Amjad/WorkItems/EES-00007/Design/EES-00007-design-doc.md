# EES-00007 — Design Doc

## Summary

Add Kusto (Azure Data Explorer) integration to the GUI's Process Incident tab. Users enter an incident ID and the app retrieves incident text from Kusto, eliminating the need to export and save text files locally.

## Problem Statement

Currently, users must manually export incident text from their data source and save it as a `.txt` file before the GUI can process it. This adds friction and a manual step to every incident processing workflow.

## Business Case

- **Why now:** GUI is in place (EES-00005), settings infrastructure exists (EES-00006). Kusto is the source of truth for incident data.
- **Impact:** Eliminates manual export step; users go directly from incident ID to AI-processed facts.

## Stakeholders

- Technical users processing incidents via the EES GUI

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | An Incident ID text field and "Fetch from Kusto" button on the Process Incident tab |
| FR-2 | Fetch retrieves incident description text from the `IncidentDescriptions` table |
| FR-3 | Retrieved text populates the incident text pane (same as file-loaded text) |
| FR-4 | File browse remains available as an alternative input method |
| FR-5 | Kusto connection settings (cluster, database) are configurable via Settings dialog |
| FR-6 | Clear error messages for: incident not found, Kusto unreachable, auth failure |

## Non-Functional Requirements

- Kusto fetch runs on a background thread (non-blocking UI)
- Same worker pattern as LLM calls
- Authentication via `ChainedTokenCredential` (same as Azure OpenAI)

## Proposed Approach

### 1. KustoClient (`src/ees/gui/kusto_client.py`)

A pure-Python class with no Tkinter dependency:
- `KustoClient(cluster, database, credential)` — connects to Kusto
- `fetch_incident(incident_id) -> str` — queries `IncidentDescriptions` table and returns the description text

**Query:**
```kql
IncidentDescriptions
| where IncidentId == "{incident_id}"
| project Description
| take 1
```

**Dependency:** `azure-kusto-data` package (official Azure SDK for Kusto).

### 2. Settings Extension

Add Kusto settings to `settings.yaml` and `SettingsDialog`:
```yaml
azure_openai:
  endpoint: "..."
  deployment: "..."
  api_version: "..."
kusto:
  cluster: "https://acciafollowercentralus.centralus.kusto.windows.net"
  database: "IcmDataWarehouse"
```

Extend `SettingsManager` with Kusto defaults and `SettingsDialog` with a Kusto section.

### 3. GUI Changes

Modify the Process Incident tab's top bar:
- Add "Incident ID:" label + entry field + "Fetch from Kusto" button
- Existing file browse remains alongside
- Fetch button triggers `run_in_worker(kusto_client.fetch_incident, ...)` 
- On success, populates incident text pane and stores text in `self._incident_text`

### 4. Authentication

Reuse `ChainedTokenCredential(AzureCliCredential(), ManagedIdentityCredential())` — same pattern as Azure OpenAI.

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|----------------|
| REST API direct call | `azure-kusto-data` SDK handles auth, retries, and connection pooling |
| Embed Kusto query in settings | Fixed table/query is simpler and safer; advanced queries are out of scope |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| `azure-kusto-data` is a new dependency | Official Azure SDK, well-maintained |
| Kusto cluster unreachable | Clear error dialog with retry guidance |
| Incident ID not found | User-friendly "not found" message |
| Auth failure | Same credential chain as OpenAI; consistent error handling |

## Dependencies

- EES-00005 (GUI), EES-00006 (Settings infrastructure)
- New package: `azure-kusto-data`

## Migration / Rollback

- Additive: file browse unchanged; Kusto is an optional additional input method
- If `azure-kusto-data` not installed, Kusto button could be disabled (graceful degradation)

## Test Strategy

- Unit tests for `KustoClient` (mocked `azure-kusto-data`)
- Unit tests for extended `SettingsManager` (Kusto settings load/save)
- Manual test: enter incident ID, fetch, verify text display
