# GCP-0045 Test Cases

## Test Strategy
All tests are manual acceptance tests since the change is to an AI instruction file (`.github/copilot-instructions.md`). No automated unit tests apply — the "system under test" is the AI's behavior in a chat session.

---

## TC-01: "new workitem" triggers immediate creation
**Maps to AC**: Trigger phrases listed and AI immediately calls `gcp_create_workitem`
**Type**: Happy path
**Steps**:
1. Start a fresh chat session with the updated copilot-instructions.md loaded
2. Send: "new workitem: add a dark mode toggle"
**Expected**: AI calls `gcp_create_workitem` on the FIRST response. Does not ask "Would you like me to create a work item?" or similar confirmation.
**Failure message**: "AI did not call gcp_create_workitem on first response to 'new workitem' trigger"

## TC-02: "new work item" (with space) triggers immediate creation
**Maps to AC**: Trigger phrases listed
**Type**: Happy path (variant)
**Steps**:
1. Start a fresh chat session
2. Send: "new work item: fix the login page"
**Expected**: AI calls `gcp_create_workitem` on the FIRST response.
**Failure message**: "AI did not recognize 'new work item' (with space) as a trigger phrase"

## TC-03: Work-item ID pattern triggers creation
**Maps to AC**: Trigger phrases listed, work-item ID pattern recognized
**Type**: Happy path
**Steps**:
1. Start a fresh chat session
2. Send: "GCP-0099: implement caching layer"
**Expected**: AI calls `gcp_create_workitem(work_item_id="GCP-0099", profile="complete")` using the provided ID.
**Failure message**: "AI did not recognize work-item ID pattern as a trigger"

## TC-04: "complete mode" triggers creation
**Maps to AC**: Trigger phrases listed
**Type**: Happy path
**Steps**:
1. Start a fresh chat session
2. Send: "complete mode — refactor the auth module"
**Expected**: AI calls `gcp_create_workitem` with `profile="complete"` on the FIRST response.
**Failure message**: "AI did not recognize 'complete mode' as a trigger phrase"

## TC-05: "Do not ask for confirmation" is enforced
**Maps to AC**: Section explicitly states "Do not ask for confirmation"
**Type**: Negative test
**Steps**:
1. Start a fresh chat session
2. Send: "new workitem: improve error handling"
**Expected**: AI does NOT respond with any of: "Would you like me to create a work item?", "Shall I start the Golazo workflow?", "Do you want me to call gcp_create_workitem?"
**Failure message**: "AI asked for confirmation instead of immediately acting on trigger phrase"

## TC-06: Section placement is early in file
**Maps to AC**: Section placed in high-visibility location
**Type**: Structural / regression
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Find the trigger-phrase section
**Expected**: Section appears before or immediately adjacent to "## REQUIRED: Before EVERY Response"
**Failure message**: "Trigger-phrase section is buried too deep in the file"

## TC-07: Existing instructions preserved (regression)
**Maps to AC**: No functional regressions to other sections
**Type**: Regression
**Steps**:
1. Open `.github/copilot-instructions.md`
2. Verify all existing sections are intact: FORBIDDEN ACTIONS, REQUIRED: Before EVERY Response, Starting a New Work Item, Role Transitions, File Naming Convention, Gate Enforcement, Capability Registry
**Expected**: All sections present and unchanged.
**Failure message**: "Existing copilot-instructions section was modified or removed"

## TC-08: Existing work-item ID calls gcp_status instead
**Maps to**: Review Comments recommendation #1
**Type**: Edge case
**Steps**:
1. Start a fresh chat session
2. Send: "GCP-0001" (an ID that already exists)
**Expected**: AI calls `gcp_status(work_item_id="GCP-0001")` rather than `gcp_create_workitem`, since the work item exists.
**Failure message**: "AI tried to create a work item that already exists instead of checking status"
