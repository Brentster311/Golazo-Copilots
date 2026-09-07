# GCP-0075 Test Cases

| ID | Scenario | Expected Result | AC |
|---|---|---|---|
| TC-01 | Inspect packaged Documenter role | Reviews non-release documentation and has no version, changelog, or future Builder dependency | AC1 |
| TC-02 | Inspect packaged Builder role | Explicitly owns classification, version update, monotonic PEP 440 validation, changelog, build, commit, and push | AC1 |
| TC-03 | Scan both roles for future-role prerequisites and backward-transition phrases | No circular phrases found | AC2 |
| TC-04 | Compare profile role orders | Complete places Documenter before Builder; Express contains Builder without Documenter; policy remains executable | AC2 |
| TC-05 | Force bootstrap roles to a temporary workspace | Generated Documenter and Builder files equal packaged defaults | AC3 |
| TC-06 | Inspect README workflow guidance | Role order and ownership match packaged instructions | AC3 |
| TC-07 | Reintroduce old phrases in policy fixtures | Assertions identify Builder-note dependency or return-to-Documenter instruction | AC4 |
| TC-08 | Run existing role self-contained and bootstrap suites | No regression | Regression |

## Execution

Write focused policy tests before editing role files, verify red failures, implement instruction changes, then run focused tests, full coverage, Ruff, build, and capability validation.
