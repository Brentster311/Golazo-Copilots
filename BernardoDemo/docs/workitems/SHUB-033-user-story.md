# SHUB-033: Solution Gap Analyzer

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: Identify documentation gaps from case topics
- **As a**: Supportability PM or content lead
- **I want**: The AI to identify case topics that lack adequate self-help documentation
- **So that**: I can prioritize content creation for maximum deflection impact

## Scope

- **In scope**:
  - Compare case topic distribution to existing Apollo article coverage
  - Identify high-volume topics with no/weak documentation
  - Estimate deflection potential if documentation created
  - Rank gaps by impact (case volume × deflection likelihood)
  - Track gap closure over time
  
- **Out of scope**:
  - Creating documentation (separate stories)
  - Evaluating article quality (assumes existence = coverage)
  - Cross-product gap analysis

## Acceptance Criteria (bulleted, testable)

- [ ] User can request: "What are my biggest documentation gaps?"
- [ ] Report shows: topic, case volume, existing coverage, estimated impact
- [ ] AI explains gap: "142 cases about X, but only 1 partial article"
- [ ] Results sorted by estimated deflection impact
- [ ] User can drill into specific gaps: "Tell me more about the NSG gap"

## Example Output

```
## Documentation Gap Analysis: Azure Compute (Last 90 days)

| Rank | Topic | Cases | Coverage | Gap Score | Est. Deflection |
|------|-------|-------|----------|-----------|-----------------|
| 1 | NSG rule priority | 142 | 20% | 9.2 | 85 cases/month |
| 2 | VM boot diagnostics | 98 | 40% | 7.1 | 45 cases/month |
| 3 | Disk encryption | 76 | 15% | 6.8 | 50 cases/month |
| 4 | Custom script ext | 54 | 60% | 3.2 | 15 cases/month |

**Recommendation**: Prioritize NSG rule priority article (SHUB-030 draft available)
```

## Non-functional Requirements

- Analysis scope: Up to 10,000 cases vs. 1,000 articles
- Analysis time: < 2 minutes
- Refresh frequency: Weekly

## Telemetry / Metrics Expected

- Gaps identified and tracked
- Time to gap closure
- Actual deflection after gap filled
