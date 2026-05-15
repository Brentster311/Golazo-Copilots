# TIM-0005 — Program Manager Decision Notes

## Key Decisions

- **12 agents produced in one pass**: No phasing needed. All source files exist. Uniform structure.
- **`.github/agents/` at workspace root**: Consistent with the Golazo Copilot infrastructure already in the repo (`.github/agents/golazo-copilot/`).
- **Single commit**: All 12 agents go in together. Partial delivery would be inconsistent and has no value on its own.

## Risk Log

- **YAML syntax**: Highest single-file risk. Mitigated by quoting all description values.
- **Over-length bodies**: Each body capped at ~400 words to preserve context efficiency.

## Open Questions

None. All inputs available and scope clear.
