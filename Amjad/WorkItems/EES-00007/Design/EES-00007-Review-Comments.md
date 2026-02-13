# EES-00007 — Review Comments

## Major Findings

**MJ-1: New dependency `azure-kusto-data`**
This is the first external Azure SDK dependency beyond `openai` and `azure-identity`. Architect should confirm the package is appropriate and document the install requirement.

## Minor Findings

**MN-1: Query column name assumption**
The KQL query assumes `IncidentId` and `Description` column names. These should be configurable or at least documented as assumptions.

**MN-2: Incident ID validation**
No mention of validating the incident ID format before querying Kusto. Consider basic sanity check (non-empty, reasonable length).

**MN-3: Multiple results handling**
The query uses `take 1` — what if there are multiple descriptions? Should we concatenate or just take the first? Recommend: take first, document behavior.

---

## Architect Notes

### MJ-1 Resolution
`azure-kusto-data` is the official Azure SDK for Kusto/ADX. It's well-maintained and consistent with our existing Azure SDK usage (`openai`, `azure-identity`). **Approved**. Add to `pyproject.toml` dependencies.

### MN-1 Resolution
Column names `IncidentId` and `Description` are specific to the `IncidentDescriptions` table in the `IcmDataWarehouse` database. They are fixed by the table schema and not user-configurable. **Accepted as-is** — document in code comments.

### MN-2 Resolution
Validate incident ID is non-empty and stripped of whitespace before querying. Raise `ValueError` for empty input. **Agreed** — implement in `KustoClient.fetch_incident()`.

### MN-3 Resolution
`take 1` returns the first matching row. This is correct behavior for a single incident lookup. **Accepted as-is** — document in docstring.

### Architectural Observations

1. **Graceful degradation**: If `azure-kusto-data` is not installed, the Fetch button should be disabled rather than crashing. Use a try/except import guard.
2. **KQL injection**: The incident ID must not be interpolated directly into the KQL string. Use parameterized queries via `azure-kusto-data`'s `KustoConnectionStringBuilder` and query parameters, or at minimum sanitize the input (strip non-alphanumeric/hyphen chars).
3. **Credential reuse**: Auth uses the same `ChainedTokenCredential(AzureCliCredential(), ManagedIdentityCredential())` as Azure OpenAI. Consider extracting a shared credential factory if not already done (low priority).
4. **Capability impact**: Only the `gui` capability is affected (1 of 9). No transitive impacts.

### Contract Summary
- `KustoClient.__init__(cluster: str, database: str)` — creates client with `ChainedTokenCredential`
- `KustoClient.fetch_incident(incident_id: str) -> str` — returns description text, raises `ValueError` (empty ID), `RuntimeError` (not found / connection error)
- `SettingsManager` extended with `kusto` section defaults and env map
- `SettingsDialog` extended with Kusto cluster/database fields
