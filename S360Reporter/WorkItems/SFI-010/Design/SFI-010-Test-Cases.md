# SFI-010: Test Cases

## Test Coverage Matrix

| Acceptance Criteria | Test Case(s) |
|---------------------|--------------|
| AC1: Cache file location | TC01 |
| AC2: Discovery flow on miss | TC02, TC03, TC04 |
| AC3: Cache hit single-pass | TC05 |
| AC4: S360_ProgramIds always included | TC06 |
| AC5: Clear Cache clears metadata | TC07 |
| AC6: Existing tests pass | TC08 |

---

## Unit Tests

### TC01: Cache File Location
**File**: `test_data.py`
**Function**: `test_column_cache_path`
```python
def test_column_cache_path():
    """Column metadata cache is at $TEMP/GUI/column_metadata.json"""
    from sfi_reporter.data import get_column_cache_path
    import os
    path = get_column_cache_path()
    assert path.endswith("GUI/column_metadata.json") or \
           path.endswith("GUI\\\column_metadata.json")
```

### TC02: Load Empty Cache
**File**: `test_data.py`
**Function**: `test_load_column_cache_when_missing`
```python
def test_load_column_cache_when_missing(tmp_path, monkeypatch):
    """Returns empty dict when cache file doesn't exist"""
    monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", 
                        lambda: str(tmp_path / "nonexistent.json"))
    from sfi_reporter.data import load_column_cache
    cache = load_column_cache()
    assert cache == {"version": 1, "kpis": {}}
```

### TC03: Save and Load Roundtrip
**File**: `test_data.py`
**Function**: `test_save_and_load_column_cache`
```python
def test_save_and_load_column_cache(tmp_path, monkeypatch):
    """Cache roundtrip preserves data"""
    cache_path = str(tmp_path / "column_metadata.json")
    monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", lambda: cache_path)
    
    from sfi_reporter.data import save_column_cache, load_column_cache
    
    test_data = {
        "version": 1,
        "kpis": {
            "kpi-123": {
                "columns": ["id", "title", "dueDate"],
                "discovered_at": "2026-02-04T18:00:00Z"
            }
        }
    }
    save_column_cache(test_data)
    loaded = load_column_cache()
    assert loaded == test_data
```

### TC04: Corrupt Cache Recovery
**File**: `test_data.py`
**Function**: `test_load_column_cache_corrupt_json`
```python
def test_load_column_cache_corrupt_json(tmp_path, monkeypatch):
    """Returns empty cache when file is corrupt"""
    cache_path = tmp_path / "column_metadata.json"
    cache_path.write_text("not valid json {{{")
    monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", 
                        lambda: str(cache_path))
    
    from sfi_reporter.data import load_column_cache
    cache = load_column_cache()
    assert cache == {"version": 1, "kpis": {}}
```

### TC05: Get Cached Columns
**File**: `test_data.py`
**Function**: `test_get_cached_columns_hit`
```python
def test_get_cached_columns_hit(tmp_path, monkeypatch):
    """Returns cached columns for known KPI"""
    cache_path = str(tmp_path / "column_metadata.json")
    monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", lambda: cache_path)
    
    from sfi_reporter.data import save_column_cache, get_cached_columns
    
    save_column_cache({
        "version": 1,
        "kpis": {
            "kpi-123": {"columns": ["id", "title"], "discovered_at": "2026-02-04"}
        }
    })
    
    columns = get_cached_columns("kpi-123")
    assert columns == ["id", "title"]
```

### TC06: Essential Columns Always Included
**File**: `test_data.py`
**Function**: `test_essential_columns_always_included`
```python
def test_essential_columns_always_included():
    """S360_ProgramIds and url are always in column requests"""
    from sfi_reporter.data import ESSENTIAL_COLUMNS, merge_columns_with_essentials
    
    discovered = ["id", "title", "dueDate"]
    result = merge_columns_with_essentials(discovered)
    
    assert "S360_ProgramIds" in result
    assert "url" in result
    # Original columns preserved
    assert "id" in result
    assert "title" in result
```

---

## Integration Tests

### TC07: Clear Cache Clears Metadata
**File**: `test_tk_app.py`
**Function**: `test_clear_cache_clears_column_metadata`
```python
def test_clear_cache_clears_column_metadata(tmp_path, monkeypatch):
    """Clear Cache button removes both data cache and column metadata cache"""
    data_cache = tmp_path / "brentj_cache.json"
    metadata_cache = tmp_path / "column_metadata.json"
    
    data_cache.write_text('{"test": 1}')
    metadata_cache.write_text('{"version": 1, "kpis": {}}')
    
    monkeypatch.setattr("sfi_reporter.data.get_cache_dir", lambda: str(tmp_path))
    
    from sfi_reporter.tk_app import clear_cache
    clear_cache("brentj")
    
    assert not data_cache.exists()
    assert not metadata_cache.exists()
```

### TC08: Existing Tests Pass
**Verification**: Run `pytest tests/ -v` and confirm 46+ tests pass

---

## Manual Test Checklist

- [ ] Fresh start (no cache): Verify discovery logs appear
- [ ] Second refresh: Verify "Using cached columns" logs
- [ ] Clear Cache: Verify column_metadata.json deleted
- [ ] Program Summary: Verify programs appear (S360_ProgramIds working)
- [ ] Hyperlinks: Verify URLs are clickable (url column working)
