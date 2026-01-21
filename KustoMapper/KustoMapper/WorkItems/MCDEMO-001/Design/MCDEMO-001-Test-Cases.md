# Test Cases: MCDEMO-001 - Kusto Connection & Table Discovery

## Test Matrix

### Acceptance Criteria Coverage

| AC# | Acceptance Criterion | Test Cases |
|-----|---------------------|------------|
| AC1 | User can enter Kusto cluster URL and database name | TC01, TC02, TC03 |
| AC2 | Application displays list of all tables in the database | TC04, TC05, TC06 |
| AC3 | User can select a table to view its schema | TC07, TC08, TC09 |
| AC4 | Errors are displayed clearly | TC10, TC11, TC12, TC13 |
| AC5 | Schema data is cached locally | TC14, TC15, TC16, TC17, TC18 |

---

## Test Cases

### Connection Tests (AC1)

**TC01: Connect with valid cluster and database**
- **Given**: Valid cluster URL and database name
- **When**: `connect(cluster=url, database=db)` is called
- **Then**: Returns `True`, `is_connected` is `True`
- **Status**: ? Implemented in `test_kusto_adapter.py`

**TC02: Connect without cluster raises error**
- **Given**: Missing cluster URL
- **When**: `connect(database=db)` is called
- **Then**: Raises `ConnectionError` with message containing "required"
- **Status**: ? Implemented

**TC03: Connect without database raises error**
- **Given**: Missing database name
- **When**: `connect(cluster=url)` is called
- **Then**: Raises `ConnectionError` with message containing "required"
- **Status**: ? Implemented

### Table Discovery Tests (AC2)

**TC04: Get tables returns list of TableInfo**
- **Given**: Connected adapter
- **When**: `get_tables()` is called
- **Then**: Returns list of `TableInfo` objects with names
- **Status**: ? Implemented

**TC05: Get tables when not connected raises error**
- **Given**: Disconnected adapter
- **When**: `get_tables()` is called
- **Then**: Raises `RuntimeError` with "Not connected"
- **Status**: ? Implemented

**TC06: Get tables handles empty database**
- **Given**: Connected to database with no tables
- **When**: `get_tables()` is called
- **Then**: Returns empty list
- **Status**: ? Implemented

### Schema Discovery Tests (AC3)

**TC07: Get table schema returns columns**
- **Given**: Connected adapter, valid table name
- **When**: `get_table_schema(table_name)` is called
- **Then**: Returns list of `ColumnInfo` with name and type
- **Status**: ? Implemented

**TC08: Get schema when not connected raises error**
- **Given**: Disconnected adapter
- **When**: `get_table_schema(table_name)` is called
- **Then**: Raises `RuntimeError` with "Not connected"
- **Status**: ? Implemented

**TC09: Get schema for non-existent table raises error**
- **Given**: Connected adapter, invalid table name
- **When**: `get_table_schema("NonExistent")` is called
- **Then**: Raises `ValueError` with "Table not found"
- **Status**: ? Implemented

### Error Handling Tests (AC4)

**TC10: Auth failure provides clear message**
- **Given**: Invalid credentials
- **When**: `connect()` fails with auth error
- **Then**: Raises `ConnectionError` mentioning "az login"
- **Status**: ? Implemented

**TC11: Database not found provides clear message**
- **Given**: Non-existent database
- **When**: `connect()` fails
- **Then**: Raises `ConnectionError` with "Database not found"
- **Status**: ? Implemented

**TC12: Missing dependency provides clear message**
- **Given**: `accia-datacollection` not installed
- **When**: `connect()` is called
- **Then**: Raises `ConnectionError` with "not installed"
- **Status**: ? Implemented

**TC13: Network error handled gracefully**
- **Given**: Network connectivity issues
- **When**: `connect()` fails
- **Then**: Raises `ConnectionError` with wrapped details
- **Status**: ? Implemented

### Cache Tests (AC5)

**TC14: Save and load tables from cache**
- **Given**: List of `TableInfo` objects
- **When**: `save_tables()` then `load_tables()`
- **Then**: Returns equivalent list
- **Status**: ? Implemented in `test_schema_cache.py`

**TC15: Save and load schema from cache**
- **Given**: List of `ColumnInfo` objects
- **When**: `save_schema()` then `load_schema()`
- **Then**: Returns equivalent list
- **Status**: ? Implemented

**TC16: Load from non-existent cache returns None**
- **Given**: No cached data
- **When**: `load_tables()` or `load_schema()` called
- **Then**: Returns `None`
- **Status**: ? Implemented

**TC17: Cache invalidation removes files**
- **Given**: Cached data exists
- **When**: `invalidate()` called
- **Then**: Cache directory removed, `is_valid()` returns `False`
- **Status**: ? Implemented

**TC18: Cache directory structure is correct**
- **Given**: Cluster URL and database name
- **When**: Cache is initialized
- **Then**: Directory uses hashed cluster and sanitized database name
- **Status**: ? Implemented

---

## Model Tests

**TC19: ColumnInfo creation and defaults**
- **Status**: ? Implemented in `test_models.py`

**TC20: ColumnInfo to_dict / from_dict roundtrip**
- **Status**: ? Implemented

**TC21: TableInfo creation and defaults**
- **Status**: ? Implemented

**TC22: TableInfo to_dict / from_dict roundtrip**
- **Status**: ? Implemented

---

## Test Execution

```bash
cd KustoMapper
pip install -e .
pytest -v
```

## Expected Results
- **22 tests** should pass
- All acceptance criteria covered
