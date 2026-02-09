# GCP-0035 — Test Cases

## Verification Tests (post-rewrite grep checks)

### TC-1: No references to deleted tools
- **Action**: Grep README for `gcp_mark_dor`, `gcp_mark_dod`
- **Expected**: Zero matches

### TC-2: No references to evidence validation
- **Action**: Grep README for `evidence` (case-insensitive, excluding "Evidence" in changelog context)
- **Expected**: Zero matches in feature/usage sections

### TC-3: No stale DoR/DoD item-level references
- **Action**: Grep README for `userStory`, `designDoc`, `reviewComments`, `testCases`, `branchCreated`, `testsWrittenFirst`, `testsPass`, `buildPasses`, `docsUpdated`, `refactorComplete`, `retroComplete`
- **Expected**: Zero matches (these were DoR/DoD item names)

### TC-4: All actual tools listed
- **Action**: Verify README contains `gcp_create_workitem`, `gcp_status`, `gcp_transition`, `gcp_consent`, `gcp_bootstrap`
- **Expected**: All 5 present in tools table

### TC-5: New features documented
- **Action**: Verify README mentions version sync warning, role progress, TechBestPractices, Required Outputs
- **Expected**: All 4 present

### TC-6: Role-Based Output Validation section exists
- **Action**: Verify README contains a section explaining the `## Required Outputs` mechanism
- **Expected**: Section present with explanation of how role files define outputs validated on transition

### TC-7: Example session uses current workflow
- **Action**: Verify example session shows create → status → transition, no mark_dor/mark_dod
- **Expected**: Example reflects actual current workflow
