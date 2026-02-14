# EES-00015 — Architect Notes

## Decisions
- `facts_used_by_rules()` signature: `(facts: list[Fact], rules: list[Rule]) -> set[int]` — returns indices into the facts list. Pure function in `adapters.py`.
- Chaining nouns constant: reuse `_CHAINING_KINDS` from `models.py` or define locally. Local is simpler since adapters shouldn't import private constants.
- Treeview tag: `"used"` tag with bold font configured at widget creation time via `tag_configure("used", font=...)`.
- No architectural concerns — additive feature, no contract changes.
