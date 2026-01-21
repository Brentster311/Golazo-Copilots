# GCP-002: Architect Decision Document

## Work Item
GCP-002 — Golazo CLI Tool and README Documentation

## Decisions Made

### 1. Single-File Architecture
All CLI logic in `Golazo_Copilot.py` — no modules, no packages.

**Rationale**: Scope is small (~150 lines). Single file is easier to distribute and understand.

### 2. Functional Design (No Classes)
Use functions, not OOP.

**Rationale**: No state to encapsulate. Functions are simpler and more testable for this scope.

### 3. `pathlib` for Path Operations
Use `pathlib.Path` throughout instead of `os.path`.

**Rationale**: 
- Modern Python 3 idiom
- Better Windows/Unix compatibility
- Cleaner, more readable code

### 4. `shutil` for File Operations
Use `shutil.copy2()` for copying files.

**Rationale**: Preserves file metadata; standard library; handles cross-platform differences.

### 5. Standard Entry Point Pattern
```python
if __name__ == "__main__":
    sys.exit(main())
```

**Rationale**: Enables importing for unit tests while supporting direct CLI execution.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Click/Typer for CLI | External dependency; overkill for simple args |
| Class-based design | No state; unnecessary complexity |
| Multiple modules | Not enough code to warrant splitting |
| async I/O | File ops are fast; sync is simpler |

## Tradeoffs Accepted

- No plugin architecture (monolithic but simple)
- No dependency injection (direct function calls)
- No logging framework (print statements sufficient)

## Known Limitations or Risks

1. **Testing requires filesystem mocking** — Acceptable; use `tempfile` module
2. **No type hints in v1** — Can add later; Python doesn't require them

## Architectural Diagram

```
???????????????????????????????????????????????????????????
?                    Golazo_Copilot.py                    ?
???????????????????????????????????????????????????????????
?  main()                                                 ?
?    ??? find_repo_root(start_path) ? Path | None        ?
?    ??? get_script_directory() ? Path                   ?
?    ??? ensure_directory(path) ? None                   ?
?    ??? copy_file(src, dst) ? bool                      ?
?    ??? install_golazo(target_root) ? bool              ?
???????????????????????????????????????????????????????????
                          ?
                          ?
              ?????????????????????????
              ?   Target Repository   ?
              ?????????????????????????
              ? .github/              ?
              ?   copilot-instruct... ?
              ?   roles/              ?
              ?     *.md (10 files)   ?
              ?????????????????????????
```

## Security Considerations

- **No network access**: All operations are local filesystem
- **No elevated permissions**: Runs as current user
- **No secrets handling**: No credentials involved
- **File overwrite**: Intentional behavior, documented
