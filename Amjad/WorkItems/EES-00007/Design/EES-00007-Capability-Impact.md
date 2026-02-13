# EES-00007 — Capability Impact

## Affected Capabilities

| Capability | Impact | Notes |
|-----------|--------|-------|
| gui | Direct | New KustoClient class, Settings extension, GUI tab changes |

## Unaffected Capabilities
All other 8 capabilities remain unaffected. KustoClient is scoped entirely within `ees.gui` package.

## Contract Compatibility
- SettingsManager: Additive changes only (new `kusto` section). Existing `azure_openai` section unchanged.
- GUI: Additive (new button/field alongside existing file browse). Existing workflows unchanged.
- No breaking changes to any existing capability contracts.
