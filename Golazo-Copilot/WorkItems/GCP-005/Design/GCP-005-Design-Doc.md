# Design Document: GCP-005 - Distribution Package Creator

## Business Case

### Problem Statement
Currently, distributing GolazoCP requires users to clone the git repository. This creates friction for:
- Users who want to try GolazoCP without git
- Distribution via file shares, email, or download portals
- Offline installations

### Proposed Solution
Add a `--package` CLI flag that creates a self-contained zip file with all necessary files for manual GolazoCP setup.

### Business Value
- **Lower barrier to entry**: Users can download a single zip and extract
- **Flexible distribution**: Share via any file transfer method
- **Offline support**: No internet required after download

## Technical Design

### Architecture Overview

```
Golazo_Copilot.py
??? main() - Entry point, handles CLI args
??? create_package() - NEW: Creates distribution zip
?   ??? Gathers files from .github/
?   ??? Includes README.md
?   ??? Includes USAGE-VisualStudio.md
?   ??? Includes USAGE-VSCode.md
??? install_golazo() - Existing install function
```

### CLI Interface

```bash
# Existing behavior (unchanged)
python Golazo_Copilot.py

# New packaging behavior
python Golazo_Copilot.py --package
```

### Implementation Approach

1. **Argument Parsing**: Use `argparse` from standard library to handle `--package` flag
2. **Zip Creation**: Use `zipfile` module to create the archive
3. **File Collection**: Gather files relative to script directory:
   - `.github/copilot-instructions.md`
   - `.github/roles/*.md`
   - `README.md`
   - `USAGE-VisualStudio.md` (new file)
   - `USAGE-VSCode.md` (new file)

### New Function: `create_package()`

```python
def create_package(output_path: Path) -> bool:
    """
    Create a distribution zip file containing GolazoCP files.
    
    Args:
        output_path: Path where zip file will be created
        
    Returns:
        True if successful, False otherwise
    """
```

### Zip Structure

```
GolazoCP-dist.zip
??? .github/
?   ??? copilot-instructions.md
?   ??? roles/
?       ??? architect.md
?       ??? builder.md
?       ??? developer.md
?       ??? documentor.md
?       ??? program-manager.md
?       ??? project-owner-assistant.md
?       ??? refactor-expert.md
?       ??? retrospective.md
?       ??? reviewer.md
?       ??? tester.md
??? README.md
??? USAGE-VisualStudio.md
??? USAGE-VSCode.md
```

### Error Handling

| Scenario | Behavior |
|----------|----------|
| `.github/` missing | Exit 1 with error message |
| Role files missing | Exit 1 with error message |
| README.md missing | Exit 1 with error message |
| USAGE files missing | Exit 1 with error message |
| Zip already exists | Overwrite with warning |
| Write permission denied | Exit 1 with error message |

### Dependencies

- **No new dependencies** - Uses only Python standard library:
  - `argparse` - CLI argument parsing
  - `zipfile` - Zip creation
  - `pathlib` - Path handling (already used)
  - `sys` - Exit codes (already used)

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `Golazo_Copilot.py` | Modify | Add `--package` flag and `create_package()` function |
| `USAGE-VisualStudio.md` | Create | Visual Studio setup instructions |
| `USAGE-VSCode.md` | Create | VS Code setup instructions |
| `tests/test_golazo_copilot.py` | Modify | Add tests for packaging feature |

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Large zip files | Only include necessary .md files, not WorkItems or tests |
| Path handling differences (Windows/Unix) | Use `zipfile.write()` with explicit `arcname` |
| Missing source files at package time | Validate all files exist before creating zip |
