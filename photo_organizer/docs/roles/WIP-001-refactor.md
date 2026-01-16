# Refactor Expert Notes: WIP-001

## Work Item
WIP-001 - Organize Photos by Date/Time

## Refactoring Performed

### Changes Made

1. **`scan_photos()` function - List comprehension**
   - Changed from explicit loop with `append()` to list comprehension
   - More Pythonic and concise
   - No behavior change

2. **Year formatting consistency**
   - Changed `str(photo_date.year)` to `f"{photo_date.year}"`
   - Consistent f-string style with month formatting
   - No behavior change

### Code Before
```python
def scan_photos(source_folder: Path) -> list:
    photos = []
    for file_path in source_folder.rglob('*'):
        if file_path.is_file() and is_supported_photo(file_path):
            photos.append(file_path)
    return photos
```

### Code After
```python
def scan_photos(source_folder: Path) -> list:
    return [
        file_path
        for file_path in source_folder.rglob('*')
        if file_path.is_file() and is_supported_photo(file_path)
    ]
```

## Refactoring NOT Performed

The following were considered but rejected for MVP scope:

| Candidate | Reason Not Changed |
|-----------|-------------------|
| Extract date formatting to constant | Single usage; not worth abstraction |
| Add type hints to return list | `list[Path]` requires Python 3.9+; keep 3.8 compat |
| Extract error handling to separate function | Would add complexity without benefit |
| Move constants to config file | Overkill for single-file tool |

## Verification

**Tests Status**: ? All 23 tests pass

```
Ran 23 tests in 0.065s
OK
```

## Decisions Made

1. **Minimal refactoring**
   - Code is already well-structured for its scope
   - No major structural changes needed

2. **Preserved Python 3.8 compatibility**
   - Did not use newer type hint syntax (e.g., `list[Path]`)

## Known Technical Debt
- None significant for current scope

## New User Stories Created
- **None** - no behavior changes required
