# Product Vision: Personal Financial Planner

## Mission
Help me organize my complete financial life so I can make better spending, saving, and investing decisions with confidence.

## Vision
A private, local-first financial planning workspace that connects to my real accounts, turns raw transactions into clear patterns, warns me early when I drift from plan, and offers practical options with pros and cons for better outcomes.

## Product Goals
- Consolidate key financial accounts into one trusted view.
- Provide reliable transaction categorization with user-guided correction.
- Make monthly budgeting, quarterly planning, and long-term planning visible in one workflow.
- Surface meaningful warnings early (budget drift, unusual transactions, goal drift, portfolio drift).
- Support investment decision support without direct trade execution recommendations.

## Planning Cadence
- Primary: monthly budgeting
- Secondary: quarterly planning
- Strategic: long-term and retirement planning

## In-Scope Themes (MVP Direction)
- Account connectivity now (not deferred):
  - First Tech Federal Credit Union
  - Fidelity
  - Direct OFX/API integration where possible
- Transaction intelligence:
  - Download and normalize transactions
  - Assisted categorization with user confirmation/correction loop
  - Track categorization quality over time
- Budget management:
  - Default budgeting model: category caps by month
  - Overspend warning by category
- Investment planning support:
  - Allocation visibility by account and asset class
  - Rebalancing suggestions
  - Contribution suggestions
  - Tax-aware suggestions
  - No direct trade recommendations
- Goal tracking:
  - Savings and long-term goal progress (including retirement-oriented planning)

## Out-of-Scope Themes (Initial)
- Multi-user collaboration and household sharing
- Full tax filing workflow
- Trade execution or brokerage order placement
- Complex financial advisor workflows

## Design Direction
- Make trends and tradeoffs obvious first; details second.
- Keep recommendations actionable and transparent (always include pros/cons).
- Favor user control over automation for categorization corrections.
- Optimize for confidence and clarity, not financial jargon.

## Architecture Direction (High Level)
- Client:
  - Desktop-first web app built with React.js
- Application services:
  - Python backend for integrations, normalization, planning logic, and rule evaluation
- Data layer:
  - Local-only encrypted data store as the default security boundary
- Integration layer:
  - Institution connector abstraction with direct OFX/API providers first
  - Scheduled sync and retry model for reliability
- Intelligence layer:
  - Rule-based budgeting and alert engine
  - Recommendation engine that generates options with pros/cons
- Privacy and security:
  - Local-first operation
  - Encrypted persistence

## Quality Signals and Early Failure Conditions
- Hard failure condition: inability to download data from target institutions.
- Hard failure condition: high miscategorization rate that remains unresolved by user feedback.
- Health indicator: warning signals are timely enough to influence behavior before month end.

## Key Assumptions
- Local-only model is acceptable for day-to-day use.
- Direct institution connections are feasible for the initial target institutions.
- User is willing to guide categorization to improve model quality.

## Risks
- Institution connectivity reliability may vary by API/OFX support.
- Local-only architecture raises backup and recovery considerations.
- Categorization quality may require iterative tuning before trust is high.

## Open Questions
- Final measurable success metrics for 60-day evaluation.
- Backup and recovery strategy for local encrypted data.
- Whether any additional institution providers are required for stability.

## POA Handoff Seeds
- Story 1: Connect First Tech and Fidelity and ingest transactions.
- Story 2: Build user-assisted categorization and correction workflow.
- Story 3: Implement monthly category-cap budgets with overspend alerts.
- Story 4: Add unusual transaction and savings-goal drift alerts.
- Story 5: Add investment allocation dashboard with recommendation options.
