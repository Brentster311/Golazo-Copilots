# EES-00008 — Project Owner Assistant Decision Notes

## Decision: Option A + C (Two-tier facts + smarter prompt)

### Context
During live testing of incident 586887556, the LLM extracted ~20 facts. Many were instance-specific identifiers (resource group names, GUIDs, VMSS resource names, activity IDs) that would create rules matching only this single incident — classic overfitting.

### Options Considered
| Option | Description | Verdict |
|--------|-------------|---------|
| A | Add `scope` field to Fact ("rule" vs "context") | **Selected** — safety net for user override |
| B | Ontology property classification (identifier vs categorical) | Deferred — ontology not mature enough yet |
| C | Smarter LLM prompt to avoid extracting junk | **Selected** — reduces noise at source |
| D | Post-extraction regex heuristics | Rejected — brittle, needs constant maintenance |
| E | B + C combined | Deferred (B portion) |

### Rationale
- **C is free** — prompt tuning eliminates most junk with zero code change
- **A is the safety net** — LLM won't be perfect; user needs ability to reclassify facts before they become rules
- **B deferred** — requires accumulated ontology metadata to pay off; can be added later without breaking anything
- **D rejected** — regex patterns for Azure resource names/GUIDs are fragile and need ongoing maintenance

### Scope Decision
Combined A + C into a single work item because they address the same user-observable outcome (preventing overfit rules) and are too small individually to justify separate stories.

### Known from Prior Work Items
- Interface: Tkinter GUI (EES-00005)
- Platform: Windows
- Persistence: YAML files
- User type: Technical (Azure support engineers)
