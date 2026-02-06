# SFI-009 — Test Cases

| ID | Test | Expected |
|----|------|----------|
| TC-01 | `get_detailed_action_items` with valid KPIs | Returns (rows, []) tuple |
| TC-02 | Empty KPI list | Returns ([], []) immediately |
| TC-03 | Individual KPI failure | Other KPIs still return data |
| TC-04 | Status callback receives progress | "Fetching KPIs: X/Y complete" |
| TC-05 | Thread safety of completed_count | No race conditions under load |
