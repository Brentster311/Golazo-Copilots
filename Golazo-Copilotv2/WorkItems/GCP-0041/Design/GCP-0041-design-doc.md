# Design Doc — GCP-0041: Spine — Mention Capability Registry

## Summary
Add a brief (3-5 line) conditional section to `bootstrap-instructions.md` mentioning `gcp_capabilities` so the LLM knows the tool exists.

## Proposed Approach
Append a new `---` section after "Gate Enforcement" in `bootstrap-instructions.md`:

```markdown
---

## Capability Registry (optional)

If a `capabilities.yaml` exists in the project root, use `gcp_capabilities` for impact analysis:
- `gcp_capabilities(action="list")` — summary of all capabilities
- `gcp_capabilities(action="impact", files=["path/to/file.py"])` — check which capabilities are affected by a change
```

This is content-only — no code changes.

## Test Strategy
1. Assert `bootstrap-instructions.md` source contains `gcp_capabilities`
2. Assert conditional phrasing ("If a `capabilities.yaml` exists")
3. Assert brevity (section < 10 lines)
