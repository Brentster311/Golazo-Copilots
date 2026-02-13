# Architect Decision Notes — EES-00006

## Findings Resolved
- MJ-1: FactExtractor kwargs are additive — CLI unchanged, GUI passes explicit values
- MN-1: Separate defaults for settings.py vs fact_extractor.py — no cross-contamination
- MN-2: Small label next to each field
- MN-3: Basic URL validation on save; connection testing deferred

## Capability Impact
3 capabilities affected (fact-extraction, gui, cli-orchestration). No contract breaks — additive only.

## Architecture
- `SettingsManager` is pure Python, fully testable, no Tkinter dependency
- Resolution order: config → env → default — each layer independent
