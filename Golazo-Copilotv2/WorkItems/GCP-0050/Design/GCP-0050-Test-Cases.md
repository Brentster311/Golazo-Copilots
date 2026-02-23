# GCP-0050 — Test Cases

Since this is a markdown-only change, tests are manual verification against ACs.

## TC1: Orchestrator pattern described (AC1)
- **Verify:** bootstrap-instructions.md contains the sequence: gcp_status → gcp_role_context → runSubagent → collect output → gcp_transition → repeat
- **Method:** grep for key terms in the file

## TC2: Responsibility separation (AC2)
- **Verify:** Separate sections for orchestrator and subagent responsibilities
- **Method:** Check for distinct headings

## TC3: Fallback mode section (AC3)
- **Verify:** Section describing inline execution when subagents unavailable
- **Method:** Search for "fallback" section

## TC4: Subagent prompt template (AC4)
- **Verify:** Template showing runSubagent call with gcp_role_context bundle
- **Method:** Search for template/example block

## TC5: Between-roles summary (AC5)
- **Verify:** Instruction for displaying completed role, artifacts, next role
- **Method:** Search for summary instruction

## TC6: User override mechanism (AC6)
- **Verify:** "work inline" / "no subagents" escape hatch documented
- **Method:** Search for override section

## TC7: Line count (AC7)
- **Verify:** File is ≤ 150 lines
- **Method:** `wc -l bootstrap-instructions.md`

## TC8: Automated regression test
- **Verify:** Existing test suite still passes (no Python code changes expected, but verify)
- **Method:** `pytest tests/`
