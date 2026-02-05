# SHUB-041: Anomaly Narrator

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: Natural language narration of detected anomalies
- **As a**: Supportability PM monitoring my service
- **I want**: Detected anomalies explained in plain language with suggested actions
- **So that**: I can quickly understand and respond to unusual patterns

## Scope

- **In scope**:
  - Convert anomaly detection alerts into natural language
  - Explain: what changed, by how much, compared to what baseline
  - Suggest investigation steps
  - Link to related cases/data
  - Integrate with existing anomaly detection (anomaly.md, Anomaly_investigate.md)
  
- **Out of scope**:
  - New anomaly detection algorithms
  - Auto-remediation
  - Cross-service correlation

## Acceptance Criteria (bulleted, testable)

- [ ] When anomaly detected, AI generates narrative explanation
- [ ] Narrative includes: metric, change magnitude, baseline comparison
- [ ] AI suggests: "Check these 15 cases for common thread"
- [ ] User can ask follow-up: "What's different about today's cases?"
- [ ] Explanations are actionable within 30 seconds of reading

## Example Output

```
?? Anomaly Detected: Case Volume Spike

**What happened**: Azure Compute received 340 cases today, 
which is 2.3x the typical Tuesday volume (148 cases).

**When it started**: Spike began at 2:15 PM UTC

**Likely cause**: 89% of excess cases mention "disk encryption" 
following today's service update announcement.

**Suggested actions**:
1. Review the 180 disk encryption cases for common pattern
2. Check if self-help article covers the new encryption flow
3. Consider proactive communication if known issue

[View Cases] [View Update Announcement] [Dismiss Alert]
```

## Non-functional Requirements

- Narrative generation: < 5s from anomaly detection
- Explanation clarity: Understandable by non-technical PM

## Telemetry / Metrics Expected

- Time from anomaly to user acknowledgment
- Action taken rate (did narrative drive action?)
- Anomaly resolution time with vs. without narrator
