# Program Manager Decision Notes — EES-00007

## Key Decisions
- **`azure-kusto-data` SDK**: Official Azure package, handles connection pooling and auth. Preferred over raw REST.
- **Fixed query**: Hardcoded KQL query against `IncidentDescriptions` table. No user-editable queries — keeps scope tight.
- **Settings extension**: Kusto cluster/database added to existing `settings.yaml` and `SettingsDialog`. Reuses EES-00006 infrastructure.
- **Coexistence**: File browse and Kusto fetch are independent input methods on the same tab.
