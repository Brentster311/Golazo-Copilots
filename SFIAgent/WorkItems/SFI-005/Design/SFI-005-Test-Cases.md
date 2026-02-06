# SFI-005 — Test Cases

| ID | Test | Expected |
|----|------|----------|
| TC-01 | `test_refresh_with_status_callback` | Callback receives ≥2 messages, first contains "Connecting" |
| TC-02 | `do_refresh` with no callback | No crash, returns data normally |
| TC-03 | Status shows KPI progress | Messages include "Fetching KPIs: X/Y complete" |
