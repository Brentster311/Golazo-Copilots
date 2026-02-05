# SHUB-040: KPI Explainer

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: Natural language explanation of KPI trends
- **As a**: Supportability PM or executive
- **I want**: To ask about KPI changes in plain English and get clear explanations
- **So that**: I can understand what's driving metrics without deep data analysis

## Scope

- **In scope**:
  - Explain KPI trends: "Why did deflection drop last week?"
  - Break down contributing factors with percentages
  - Compare to historical baselines and targets
  - Identify top drivers (products, topics, changes)
  - Support all standard Supportability Hub KPIs
  
- **Out of scope**:
  - Modifying KPI definitions
  - Creating new custom KPIs
  - Forecasting future KPIs

## Acceptance Criteria (bulleted, testable)

- [ ] User can ask: "Why did my CSAT drop 5 points this month?"
- [ ] AI provides contributing factors ranked by impact
- [ ] AI compares to historical baselines
- [ ] AI identifies specific cases/topics driving the change
- [ ] Explanations are verifiable against raw data

## Non-functional Requirements

- Explanation generation: < 15s
- Accuracy: Explanations match analyst findings 90%+

## Telemetry / Metrics Expected

- KPI explanation requests by metric type
- User satisfaction with explanations
- Follow-up question rate (lower = better explanations)
