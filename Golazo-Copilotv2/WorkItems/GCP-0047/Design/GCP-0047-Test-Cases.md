# GCP-0047 Test Cases

## TC-1: Documenter — No Build Check (AC1)
**Verify:** Documenter role file does not contain "build" in First Action or Entry Conditions.
**Type:** Content assertion on role file text.
**Expected:** No match for "build" in the First Action or Entry Conditions sections.

## TC-2: Developer — Branch Creation Present (AC2)
**Verify:** Developer role file First Action includes branch creation instructions.
**Type:** Content assertion on role file text.
**Expected:** Developer First Action contains "feature branch" or "git checkout -b".

## TC-3: Builder — No Branch Creation Section (AC2)
**Verify:** Builder role file does not contain "Before Developer role" or branch creation instructions.
**Type:** Content assertion on role file text.
**Expected:** No match for "Before Developer" in Builder role file.

## TC-4: Retrospective → POA Transition Valid (AC3)
**Verify:** `transitions.py` TRANSITIONS dict has "project-owner-assistant" in retrospective's forward list.
**Type:** Unit test — import TRANSITIONS, check value.
**Expected:** `"project-owner-assistant" in TRANSITIONS["retrospective"]`

## TC-5: POA Closure Section Exists (AC3)
**Verify:** POA role file contains a "Closure" section with final commit, AC validation, and pending work items.
**Type:** Content assertion on role file text.
**Expected:** POA file contains "## Closure" and "acceptance criteria" and "pending" or "future work".

## TC-6: POA Closure — No Forward Transition Instruction (Edge Case)
**Verify:** POA Closure section explicitly states this is the end of the workflow.
**Type:** Content assertion.
**Expected:** POA Closure section contains "Do NOT transition" or equivalent terminal instruction.

## TC-7: POA Closure Required Output (AC3)
**Verify:** POA role file Required Outputs includes `{id}-closure.md`.
**Type:** Content assertion on role file text.
**Expected:** "closure.md" appears in Required Outputs section.

## TC-8: QA — Design Quality Bullets Removed (AC4)
**Verify:** QA role file Design Review section does not contain: "Risk coverage", "Operability", "cost / performance", "Naming clarity", "Folder/directory structure".
**Type:** Content assertion on role file text.
**Expected:** None of those phrases appear in QA Design Review.

## TC-9: Architect — Design Quality Bullets Added (AC4)
**Verify:** Architect role file contains the design-quality bullets moved from QA.
**Type:** Content assertion.
**Expected:** Architect contains "risk coverage" or "operability" and "naming clarity" or "folder structure".

## TC-10: PM — Has Governance Sections (AC5)
**Verify:** PM role file contains Decision rules, Escalation rules, and Success criteria sections.
**Type:** Content assertion.
**Expected:** PM file contains "## Decision rules", "## Escalation rules", "## Success criteria".

## TC-11: Architect — Security Review Checklist
**Verify:** Architect role file contains a "Security Review" subsection with checklist items.
**Type:** Content assertion.
**Expected:** Architect contains "Security Review" and "data exposure" and "auth" and "attack surface".

## TC-12: Domain Expert — Boundary Statement
**Verify:** Domain Expert role file contains explicit boundary distinguishing domain knowledge from architectural decisions.
**Type:** Content assertion.
**Expected:** Domain Expert contains "not structural" or "not architectural decisions".

## TC-13: Domain Expert — No Capability Registry Section
**Verify:** Domain Expert role file does not contain `gcp_capabilities` instructions.
**Type:** Content assertion.
**Expected:** No match for "gcp_capabilities" in domain-expert.md.

## TC-14: QA — No Capability Registry Section
**Verify:** QA role file does not contain `gcp_capabilities` instructions.
**Type:** Content assertion.
**Expected:** No match for "gcp_capabilities" in quality-assurance.md.

## TC-15: Regression — All Existing Tests Still Pass
**Verify:** Full test suite passes after all changes.
**Type:** pytest run.
**Expected:** 252+ passed, 6 skipped, 0 failed.

## TC-16: Regression — Role File Exists in All 3 Locations
**Verify:** Every modified role file exists in source defaults, `.github/roles/`, and `golazo-copilot/.github/roles/`.
**Type:** File existence check.
**Expected:** All 3 copies exist for each modified role.

## TC-17: Documenter — "IMPLEMENTED" Responsibility Removed
**Verify:** Documenter role file no longer contains "Update User Story status to IMPLEMENTED".
**Type:** Content assertion.
**Expected:** No match for "IMPLEMENTED" in Documenter responsibilities.
