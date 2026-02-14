# EES-00014 — Program Manager Notes

## Decisions
1. **Scope**: Pure removal — no new features. The Root Causes tab and manual root cause management remain untouched.
2. **Backward compat approach**: `from_dict` silently drops removed keys rather than raising errors.
3. **Sequential edits**: models.py first, then extractor, then GUI, then tests — each layer depends on the one below.
