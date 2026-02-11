# LLM-0012 — Architect Decision Notes

## Decisions

### 1. Module placement
`llm_extender/discovery.py` at package root — not under `auth/` or `providers/` since discovery spans both concerns. Correct isolation.

### 2. No async variant in this story
Discovery is a dev-machine operation, not a hot path. Sync-only is fine. Async can be added later if needed.

### 3. Import guard pattern
The module should guard Azure SDK imports at the top of `discover_azure_configs()`, not at module level. This ensures the module can be imported without the optional deps (for type checking, IDE support, etc.) and only fails when actually called.

### 4. Logging strategy
Use `logging.getLogger("llm_extender.discovery")` — consistent with Python logging best practices. No print statements.

## Architectural Verdict
Approved. Clean boundaries, correct dependency isolation, no security concerns.
