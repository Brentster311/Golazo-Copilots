# User Story: MCDEMO-001 - Kusto Connection & Table Discovery

**As a** data engineer,
**I want to** connect to a Kusto cluster and see all available tables,
**So that** I can understand what data is available for analysis.

## Acceptance Criteria

1. User can enter Kusto cluster URL and database name
2. Application displays list of all tables in the database
3. User can select a table to view its schema (columns and types)
4. Errors are displayed clearly (auth failed, network error, etc.)
5. Schema data is cached locally to avoid repeated queries

## Status: ✅ Complete

- Tests: 22 passed
- Implementation: Complete
