# SFI-031 — Program Manager Decision Notes

## Decisions
1. **Separate cache file**: `{alias}_org_tree.json` rather than embedding in the main user cache. Decouples TTLs (1hr main vs 24hr org tree).
2. **Serialization in services.py**: The `OrgTree`→dict→JSON serialization lives in `services.py` (not `cache.py`) because it's domain-specific to the org-tree structure.
3. **No new cache.py functions**: Reuse `get_cache_dir()` only. The org-tree cache read/write is self-contained in two private helpers in `services.py`.
4. **Atomic writes**: Use temp file + rename pattern to prevent corrupt cache files.
