# Technical Best Practices

This file contains accumulated technical knowledge to prevent redesigns and common pitfalls.
It is referenced by Architect, Developer, and Refactor Expert roles.

**Usage:** Review this file before making architectural decisions or implementing solutions.

---

## Azure & Cloud

### Azure Identity - Credential Chaining
**DO NOT** use `DefaultAzureCredential` from Azure Identity library directly.

**Instead**, chain CLI and Managed Identity credentials explicitly:

```python
# ❌ Wrong - DefaultAzureCredential has unpredictable behavior
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()

# ✅ Correct - Explicit chain with known order
from azure.identity import ChainedTokenCredential, AzureCliCredential, ManagedIdentityCredential

credential = ChainedTokenCredential(
    AzureCliCredential(),           # Local dev
    ManagedIdentityCredential()     # Production (Azure)
)
```

**Reason:** `DefaultAzureCredential` tries many methods in an unpredictable order, causing slow timeouts and confusing errors. Explicit chaining gives you control and faster failures.

---

## Python

### Kusto / Azure Data Explorer Queries
**DO NOT** use Kusto libraries directly in Python (`azure-kusto-data`, `azure-kusto-ingest`).

**Instead**, use the `accia-datacollection` package from Azure Artifacts:

```python
# ❌ Wrong - Direct Kusto library usage
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
client = KustoClient(KustoConnectionStringBuilder.with_aad_device_authentication(cluster))
response = client.execute(database, query)

# ✅ Correct - Use accia.datacollection.KustoHandler
from azure.identity import AzureCliCredential, ManagedIdentityCredential
from accia.datacollection import KustoHandler

handler = KustoHandler(
    AlternateAADCredentialsList=[
        AzureCliCredential(),           # Local dev
        ManagedIdentityCredential()     # Production (Azure)
    ],
    UseDefaultCredentials=False
)

df = handler.GetDataFrameFromKustoQuery(
    Cluster="https://your-cluster.kusto.windows.net",
    Database="your_database",
    Query="your_query | take 100",
    CacheExpiryInMin=60
)
```

**Reason:** The `accia-datacollection` package handles caching, retries, and error handling consistently across all ACCIA projects. Using `AlternateAADCredentialsList` with explicit credentials avoids the unpredictable behavior of default credential chains.

---

## Git & Version Control

*(Add Git best practices here)*

---

## Testing

*(Add testing best practices here)*

---

## How to Add New Best Practices

1. Add a clear heading under the appropriate category
2. Show **DO NOT** (wrong way) and **Instead** (correct way)
3. Include code examples when applicable
4. Explain **Reason** so the practice is understood, not just followed
