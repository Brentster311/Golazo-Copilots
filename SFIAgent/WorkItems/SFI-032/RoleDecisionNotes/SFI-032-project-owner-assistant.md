# SFI-032 — Project Owner Assistant Decision Notes

## Decisions
1. **Library-internal refactor**: No new UI/CLI/API. Cache moves from SFIReporter layer to accia-s360 SDK layer.
2. **Per-subtree caching**: More granular than SFI-031's whole-tree cache. Each alias gets its own cache entry, populated as the tree is built recursively.
3. **Reuse S360Config.get_cache_dir()**: Already exists at `LOCALAPPDATA/accia_s360/cache/`. No need for `sfi_reporter.cache.get_cache_dir()`.
4. **Respect cache_enabled flag**: S360Config already has `cache_enabled: bool = True`.
5. **Must-ask answers**: Library change, cross-platform, file persistence (existing config), developer audience — all inherited from existing project context.
