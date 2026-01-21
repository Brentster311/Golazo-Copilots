# Design Document: MCDEMO-001 - Kusto Connection & Table Discovery

## Summary
Implement core functionality for KustoMapper to connect to Azure Data Explorer (Kusto) clusters and discover available tables with their schemas.

## Problem Statement
Data engineers need a way to explore Kusto cluster contents programmatically to understand what data is available for analysis. Currently, this requires manual query execution or using Azure portal tools.

## Business Case

### Why Now
- KustoMapper is a new tool; connection is the foundational feature
- Enables all subsequent features (query building, mapping, etc.)

### Impact
- Reduces time to discover available data sources
- Provides consistent interface for data exploration

### KPIs
- Successful connection rate
- Time to display table list
- Cache hit rate for repeated queries

## Stakeholders
- Data engineers (primary users)
- Development team (maintainers)

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | User can enter Kusto cluster URL |
| FR2 | User can enter database name |
| FR3 | Application displays list of all tables in the database |
| FR4 | User can select a table to view its schema (columns and types) |
| FR5 | Errors are displayed clearly (auth failed, network error, etc.) |
| FR6 | Schema data is cached locally to avoid repeated queries |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | Uses Azure CLI credential for authentication |
| NFR2 | Cache stored in user's home directory |
| NFR3 | Cache organized by cluster and database |
| NFR4 | Supports offline viewing of cached schemas |

## Proposed Approach

### Architecture
```
???????????????????
?   KustoAdapter  ? ? Handles connection & queries
???????????????????
?  SchemaCache    ? ? Local JSON-based caching
???????????????????
? TableInfo/      ? ? Data models
? ColumnInfo      ?
???????????????????
```

### Components

1. **KustoAdapter** (`adapters/kusto_adapter.py`)
   - Implements `DataSourceAdapter` interface
   - Uses `accia-datacollection.KustoHandler` for Kusto queries
   - Methods: `connect()`, `get_tables()`, `get_table_schema()`, `disconnect()`
   - Provides clear error messages for auth/network failures

2. **SchemaCache** (`cache/schema_cache.py`)
   - JSON file-based cache in `~/.kustomapper_cache/`
   - Directory structure: `{cluster_hash}/{database}/tables.json`
   - Schema files: `schema_{table_name}.json`
   - Supports invalidation and validity checking

3. **Data Models** (`models/schema.py`)
   - `ColumnInfo`: name, data_type, nullable
   - `TableInfo`: name, row_count, columns
   - Serialization: `to_dict()` / `from_dict()` methods

### Authentication Flow
1. User runs `az login` before using the tool
2. Application uses `AzureCliCredential` from `azure-identity`
3. Credential passed to KustoHandler

## Alternatives Considered

| Alternative | Reason Not Chosen |
|-------------|-------------------|
| Direct Kusto SDK | accia-datacollection provides simpler interface |
| Token-based auth | AzureCliCredential is more user-friendly |
| Database caching | JSON files are simpler, portable |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Auth failures | Clear error messages with guidance |
| Network timeouts | 5-minute cache for repeated queries |
| Missing dependencies | ImportError handling with clear messages |

## Open Questions
- None at this time

## Dependencies
- `azure-identity` for authentication
- `accia-datacollection` for Kusto queries
- `pandas` for data handling

## Migration / Rollout / Rollback Plan
- N/A - new feature, no migration required

## Observability Plan
- Error messages capture underlying exception details
- Connection state tracked via `is_connected` property

## Test Strategy Summary
- Unit tests for model serialization
- Unit tests for cache operations (file I/O mocked)
- Integration tests for adapter (Kusto mocked)
- Error handling tests for all failure modes
