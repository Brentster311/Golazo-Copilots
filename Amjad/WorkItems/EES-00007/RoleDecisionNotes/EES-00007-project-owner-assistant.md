# Project Owner Assistant Decision Notes — EES-00007

## Scope Justification
Single user-observable outcome: enter an incident ID and fetch text from Kusto. File-based loading is preserved as an alternative input method.

## Key Decisions
- **Kusto details provided**: Cluster `https://acciafollowercentralus.centralus.kusto.windows.net`, database `IcmDataWarehouse`, table `IncidentDescriptions`. Query will look up by incident ID.
- **Coexistence**: Both file browse and Kusto fetch will be available — no removal of existing functionality.
- **Same auth pattern**: Reuse ChainedTokenCredential for Kusto access, consistent with Azure OpenAI auth.
