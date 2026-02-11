# SFI-032 — Program Manager Decision Notes

## Decisions
1. Cache methods are instance methods on `GraphEndpoint` (not module-level) since they need `self.config`.
2. File naming: `org_tree_{alias}.json` in `config.get_cache_dir()` to avoid collision with other cache files.
3. Tests split: graph-level cache tests in accia-s360, integration tests in SFIReporter.
