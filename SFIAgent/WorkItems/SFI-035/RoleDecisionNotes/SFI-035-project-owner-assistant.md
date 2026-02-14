# SFI-035 — Project Owner Assistant Decision Notes

## Context
User reported that when using "Analyze with LLM", they cannot tell:
1. Whether URLs were extracted from the KPI action items
2. Whether those URLs were actually visited/fetched successfully

This makes it hard to trust the LLM summary since there's no transparency into its source material.

## Key Decisions

### Single story vs. decomposition
**Decision**: Single story — this is one user-observable outcome (seeing provenance before the LLM response). The change touches 3 files but is a single vertical slice.

### Must-Ask checklist resolution
- **Interface type**: Existing Tk GUI (Copilot Chat panel) — no ambiguity, the feature already exists
- **Target platform**: Windows — matches current SFIReporter target
- **Data persistence**: None — display-only, same lifecycle as the chat messages
- **User type**: Technical (security/compliance engineers)

### Scope boundary
The user asked "propose a change" — we scoped this to **display-only provenance** (showing what was extracted and fetched). We explicitly excluded:
- Changing LLM prompt content or model behavior
- Retry logic for failed fetches
- Persisting provenance data

This keeps the story small, shippable, and testable.

## Assumptions justification
All assumptions are based on the existing codebase context — the SFIReporter is already a Tk desktop app targeting Windows with no persistence for chat messages. No new architectural decisions were needed.
