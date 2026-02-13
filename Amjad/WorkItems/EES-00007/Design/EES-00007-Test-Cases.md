# EES-00007 — Test Cases

## Unit Tests: KustoClient

### TC-1: Fetch incident returns description text
- **Input:** `fetch_incident("INC-12345")` with mocked Kusto response containing description text
- **Expected:** Returns the description string

### TC-2: Fetch incident not found returns empty/raises
- **Input:** `fetch_incident("INC-99999")` with mocked empty response
- **Expected:** Raises `IncidentNotFoundError` or returns meaningful error

### TC-3: Kusto connection failure
- **Input:** `fetch_incident("INC-12345")` with mocked connection error
- **Expected:** Raises exception with clear message

### TC-4: Empty incident ID rejected
- **Input:** `fetch_incident("")`
- **Expected:** Raises `ValueError`

## Unit Tests: Settings Extension

### TC-5: Load Kusto settings from YAML
- **Input:** `settings.yaml` with `kusto.cluster` and `kusto.database`
- **Expected:** `load_kusto()` returns correct values

### TC-6: Load Kusto defaults when no config
- **Input:** No `settings.yaml`
- **Expected:** Returns defaults (cluster=`https://acciafollowercentralus.centralus.kusto.windows.net`, database=`IcmDataWarehouse`)

### TC-7: Save and reload Kusto settings round-trip
- **Input:** Save kusto settings, reload
- **Expected:** Values match

## Manual Tests

### TC-8: Fetch from Kusto button visible
- **Steps:** Launch GUI, Process Incident tab
- **Expected:** Incident ID field and "Fetch from Kusto" button visible alongside file browse

### TC-9: Fetch populates text pane
- **Steps:** Enter valid incident ID, click Fetch from Kusto
- **Expected:** Incident text appears in text pane, progress bar runs during fetch

### TC-10: Fetch error shows dialog
- **Steps:** Enter invalid incident ID, click Fetch
- **Expected:** Error dialog shown with clear message

### TC-11: Kusto settings in Settings dialog
- **Steps:** File → Settings
- **Expected:** Kusto cluster and database fields visible with defaults
