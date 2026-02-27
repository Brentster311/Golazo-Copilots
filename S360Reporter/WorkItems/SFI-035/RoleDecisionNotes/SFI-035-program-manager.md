# SFI-035 — Program Manager Decision Notes

## Design decisions

### Structured return type vs. tuple
Chose a `dataclass` (`AnalysisResult`) over a raw tuple or multiple return values. This is self-documenting, extensible (can add fields later without breaking callers), and supports `__str__` for backward compatibility.

### Sources card placement
Decided to show the provenance card as a "system" message in the chat panel rather than a popup dialog or inline in the LLM response. This keeps it non-disruptive and in-context where the user is already reading.

### No new network requests
The design explicitly avoids any additional fetching. All provenance data is captured during the existing `fetch_all_urls` call — we just surface what was already collected.

### Backward compatibility
Added `__str__` to `AnalysisResult` that returns `.prompt`, so any code that accidentally treats the result as a string still works. The `send_analysis_prompt` method gets an optional `sources_metadata` parameter to avoid breaking existing callers.

## Risks assessed
- Low risk — change is isolated to 3 files with no architectural impact
- No new dependencies, no new I/O, no new state
