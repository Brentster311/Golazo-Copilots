# SHUB-042: Scorecard Summarizer

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: AI-generated executive summaries from scorecard data
- **As a**: Executive or senior PM preparing for reviews
- **I want**: An AI-generated summary of scorecard highlights and lowlights
- **So that**: I can quickly prepare for executive reviews without manual data synthesis

## Scope

- **In scope**:
  - Generate narrative summary from scorecard data
  - Highlight: wins, concerns, trends, comparisons to targets
  - Call out items needing attention
  - Support configurable time periods
  - Export-friendly format (email, slides)
  
- **Out of scope**:
  - Generating slides/decks directly
  - Real-time scorecard updates
  - Cross-organization comparisons

## Acceptance Criteria (bulleted, testable)

- [ ] User can request: "Summarize my scorecard for exec review"
- [ ] Summary includes: top 3 wins, top 3 concerns, key trends
- [ ] Summary is 1-page readable (< 500 words)
- [ ] Data points are accurate and verifiable
- [ ] Summary can be copied to email/doc

## Example Output

```
## Azure Compute Supportability Summary - January 2025

### ?? Wins
1. **Deflection up 8%**: New VM connectivity GT driving 2,400 deflections
2. **CSAT at 4.2**: Highest score in 6 months, up from 3.9
3. **Resolution time -12%**: Average now 18 hours (was 20.5)

### ?? Concerns
1. **NSG cases up 34%**: Documentation gap identified (SHUB-023)
2. **Sev A backlog growing**: 12 cases > 48 hours old
3. **Chat abandonment up 5%**: Queue times exceeding 15 min

### ?? Trends to Watch
- Linux VM cases trending up (+15% MoM)
- Self-help engagement down on mobile (-8%)

### Recommended Actions
1. Prioritize NSG documentation (see SHUB-030 draft)
2. Add staffing for Sev A coverage
3. Review chat queue routing rules
```

## Non-functional Requirements

- Summary generation: < 20s
- Accuracy: All data points verifiable

## Telemetry / Metrics Expected

- Summary requests per review cycle
- Export/share rate
- Exec review prep time reduction
