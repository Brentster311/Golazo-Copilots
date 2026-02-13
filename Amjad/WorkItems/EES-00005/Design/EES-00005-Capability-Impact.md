# EES-00005 — Capability Impact Analysis

## Impact Summary
4 files analyzed → 7 capabilities affected (2 direct, 5 transitive)
No existing contract changes needed.

## Directly Affected Capabilities

### NEW: gui
- **Files:** `src/ees/gui/*.py` (new package)
- **Change:** Entirely new capability
- **Risk:** None — additive

### cli-orchestration
- **File:** `src/ees/main.py`
- **Change:** No code changes. GUI does not modify CLI module.
- **Risk:** None

## Transitively Affected Capabilities

### data-models, yaml-persistence, fact-extraction, rule-generation, rule-evaluation, ontology-management
- **Why:** GUI calls these existing capabilities
- **Contract Changes:** None — GUI uses existing public APIs
- **Risk:** None

## Capability Registry Update Required
Add to `capabilities.yaml`:
```yaml
- name: gui
  description: "Desktop GUI for incident processing and rule management"
  key_files:
    - src/ees/gui/app.py
    - src/ees/gui/adapters.py
    - src/ees/gui/workers.py
  contracts:
    - "main() -> None (launches GUI)"
  depends_on:
    - data-models
    - yaml-persistence
    - fact-extraction
    - rule-generation
    - rule-evaluation
    - ontology-management
```

## Conclusion
All changes are additive. No existing contracts broken. No blast radius.
