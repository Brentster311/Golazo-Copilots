# SHUB-023: Improvement Item Generator

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: AI-powered improvement item identification from case patterns
- **As a**: Supportability PM or team lead
- **I want**: The AI to analyze cases and automatically suggest improvement items
- **So that**: I can proactively address recurring issues before they become major problems

## Scope

- **In scope**:
  - Analyze cases over configurable time period
  - Identify recurring themes/patterns
  - Generate improvement item drafts with evidence (case IDs)
  - Classify by type: documentation gap, tooling need, process issue, training need
  - Estimate impact (cases affected, time saved if fixed)
  - Integration with ADO for item creation
  
- **Out of scope**:
  - Auto-creating items without approval
  - Cross-product pattern analysis (single scope only)
  - Prioritization against existing backlog

## Acceptance Criteria (bulleted, testable)

- [ ] User can request: "What improvement items should I create for last month's cases?"
- [ ] AI identifies top 5 patterns with case count and examples
- [ ] Each suggestion includes: title, description, type, affected cases, estimated impact
- [ ] User can create ADO work item directly from suggestion
- [ ] Suggestions don't duplicate existing improvement items

## Example Output

```
## Suggested Improvement Items for Azure Compute (Jan 2025)

### 1. Documentation Gap: NSG Troubleshooting
- **Cases affected**: 34 (12% of total)
- **Pattern**: Customers repeatedly confused about NSG rule priority
- **Suggestion**: Create Apollo article on NSG rule evaluation order
- **Estimated deflection**: 20+ cases/month
- [Create ADO Item]

### 2. Tooling Need: RDP Diagnostic Enhancement  
- **Cases affected**: 28 (10% of total)
- **Pattern**: Manual steps to check Windows Firewall + NSG together
- **Suggestion**: Add combined RDP connectivity diagnostic
- **Estimated time saved**: 15 min/case
- [Create ADO Item]
```

## Non-functional Requirements

- Analysis scope: Up to 10,000 cases
- Pattern detection latency: < 60s for month of data
- Minimum pattern threshold: 5 cases

## Telemetry / Metrics Expected

- Suggestions generated per scope per month
- ADO items created from suggestions
- Deflection rate for implemented suggestions
