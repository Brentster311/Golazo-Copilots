# FRC-001 Project Owner Assistant Notes

## Context Used
- Product direction from Product-Vision.md.
- User preferences from brainstorming session:
  - Desktop web app with React.js + Python direction
  - Local-only privacy boundary
  - Connectivity to First Tech Federal Credit Union and Fidelity now
  - Priority on budget drift warning and categorization quality

## Scope Decision
Selected a first vertical slice that is demonstrable and testable:
- Institution connectivity + transaction ingestion
- Assisted categorization feedback loop
- Monthly category-cap budgets with overspend warning

This avoids overloading the first work item with advanced investment, tax, and long-term simulation features.

## Why This Scope
- Directly addresses the two stated failure concerns:
  - Inability to download data
  - High miscategorization rate
- Creates the foundational data and workflow required for future investment and planning intelligence.

## Explicit Assumptions
- Desktop-first web experience is acceptable for initial release.
- Windows-first usage is acceptable while keeping implementation portable.
- Local encrypted persistence is sufficient for MVP security requirements.
- Direct OFX/API support is feasible for at least one account per target institution.

## Risks
- Institution API/OFX variability could block reliable sync.
- Categorization quality may need iterative rule tuning.
- Budget warning trust depends on ingestion and category correctness.

## Open Questions Deferred
- 60-day measurable success targets (exact numeric thresholds).
- Backup/recovery model for encrypted local data.
- Whether additional institution providers are needed if direct OFX/API is insufficient.

## Recommended Follow-on Work Items
- FRC-002: Add unusual transaction and goal drift alerts.
- FRC-003: Add allocation dashboard and recommendation options with pros/cons.
- FRC-004: Add tax-aware planning surfaces and thresholds.
