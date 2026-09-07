# GCP-0076 Program Manager Decision Notes

## Decision

Treat registry location as a shared product contract rather than duplicating path literals among tools. Canonical precedence is deterministic and status remains read-only, while capability queries retain the existing one-time legacy move.

## Delivery Sequence

Tests first establish producer/consumer disagreement and stale repository layout. Implementation then centralizes resolution, aligns tools, populates cards, and removes only confirmed same-project duplicates.

## Success Measures

- One active top-level registry.
- All registry-aware tools resolve the same capability count.
- Canonical key-file validation passes.
- Independent AgentLoop and test registries remain present.
