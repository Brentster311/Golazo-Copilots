# SFI-038: Add KPI Score Column to All Tables

**Status**: IN PROGRESS

**User Story**
- **Title**: Add KPI Score column using kpi.csv lookup
- **As a**: SFI Reporter user
- **I want**: Each table (Services, Program Summary, Action Items) to display a "Score" column computed from KPI scores in kpi.csv
- **So that**: I can see the weighted security-debt impact of action items at a glance without manual calculation
- **Out of scope**: Editing KPI scores in the UI; fetching scores from an API; the Scores... dialog (SFI-038/039 work)
- **Assumptions**:
  - **Assumption (explicit)**: `kpi.csv` is shipped alongside the app in `sfi_reporter/` and loaded at startup. It is not user-editable at runtime.
  - **Assumption (explicit)**: The KPI name in the CSV (`KPI` column) matches the `KpiName` from the S360 API used in `kpi_stats['name']`.
  - **Assumption (explicit)**: Score for a KPI row = `KPIScore × Total count`. Score for a service/program = sum of (KPIScore × count) across all KPIs within that service/program.
- **Acceptance Criteria** (bulleted, testable):
  - [ ] A `Score` column appears in the Action Items table showing `KPIScore * count` for each KPI
  - [ ] A `Score` column appears in the Services table showing the sum of per-KPI scores for each service
  - [ ] A `Score` column appears in the Program Summary table showing the sum of per-KPI scores for each program
  - [ ] KPIs not found in kpi.csv default to score 0
  - [ ] The kpi.csv file is loaded once and cached as a lookup dict keyed by KPI name
  - [ ] At least 5 unit tests cover: CSV loading, score computation, missing KPI fallback, per-service aggregation, per-program aggregation
- **Non-functional requirements**: CSV load must be < 50ms; no new external dependencies (use stdlib `csv` module)
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: Feature is additive — removing the Score column is a clean revert
