# SHUB-020: Case Summarization

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: AI-powered case summarization
- **As a**: Support engineer or case reviewer
- **I want**: To get an instant summary of a case including problem, investigation steps, and resolution
- **So that**: I can quickly understand case context without reading all communications

## Scope

- **In scope**:
  - Summarize case from Cases_Vnext data (symptom, cause, resolution)
  - Extract key timeline events
  - Identify customer sentiment trend
  - Highlight escalation points or delays
  - Support single case and batch summarization
  - JIT-compliant data access (respect field restrictions)
  
- **Out of scope**:
  - Summarizing case attachments (files, screenshots)
  - Real-time case updates (point-in-time summary)
  - Modifying case data

## Assumptions

- **Assumption (explicit)**: User has JIT access to case details they're summarizing
- **Assumption (explicit)**: Summary will use only data user is authorized to see
- **Assumption (explicit)**: Kusto query latency is acceptable (< 2s)

## Acceptance Criteria (bulleted, testable)

- [ ] User can request summary by case ID: "Summarize case SR12345678"
- [ ] Summary includes: Problem statement, investigation steps, resolution, duration
- [ ] Summary respects JIT restrictions (no unauthorized field exposure)
- [ ] Summary identifies key events: escalations, transfers, long gaps
- [ ] User can request specific aspects: "What was the root cause of SR12345678?"
- [ ] Batch mode: "Summarize my 5 most recent cases"

## Example Output

```
## Case SR12345678 Summary

**Problem**: Customer unable to connect to VM via RDP after NSG rule change

**Timeline**:
- Created: Jan 15, 2025 (Sev B)
- First response: 2 hours (within SLA)
- Escalated to Tier 2: Jan 16 (customer requested)
- Resolved: Jan 17

**Investigation**:
1. Verified VM status (running)
2. Checked NSG rules - found port 3389 blocked
3. Identified recent rule change by customer

**Resolution**: Customer added inbound rule for RDP port. 
Provided documentation on NSG best practices.

**Duration**: 2 days | **Customer Sentiment**: Neutral ? Satisfied
```

## Non-functional Requirements

- Summary generation: < 5s for single case
- Batch summary: < 30s for 10 cases
- Token limit: Summary fits in 500 tokens

## Telemetry / Metrics Expected

- Summaries generated per day
- Summary request by case age (recent vs. old)
- Batch vs. single case ratio
- Time saved estimate (based on case complexity)

## Rollout / Rollback Notes

- Depends on SHUB-010, SHUB-012
- JIT integration required before production
- Rollback: Disable case data access, documentation-only mode

## Security Considerations

- All summarization requests logged with user ID and case ID
- JIT validation before each request
- No case data cached in LLM context beyond session
- PII scrubbing in prompts (customer names ? "customer")
