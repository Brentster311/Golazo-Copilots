# GCP-0049 — Test Cases

## Test File: `tests/test_gcp_role_context.py`

### TC1: Bundle sections present (AC2)
- **Given:** Valid work item with state.json and role files
- **When:** `gcp_role_context(work_item_id="TST-001")`
- **Then:** Result contains sections: `## Role Instructions`, `## Current State`, `## Input Artifacts`, `## Previous Role Notes`
- **Failure message:** "Bundle missing expected section: {section}"

### TC2: Input artifacts contain file content (AC3)
- **Given:** Role with front-matter `inputs:` listing 2 artifacts, both exist on disk
- **When:** `gcp_role_context(work_item_id="TST-001", role="program-manager")`
- **Then:** `## Input Artifacts` section contains actual file content for both files
- **Failure message:** "Artifact content not found in bundle for: {path}"

### TC3: Missing artifacts marked (AC3)
- **Given:** Role with front-matter `inputs:` listing an artifact that doesn't exist
- **When:** `gcp_role_context(work_item_id="TST-001", role="program-manager")`
- **Then:** Missing artifact listed as `[not yet created]`
- **Failure message:** "Missing artifact should show [not yet created] marker"

### TC4: Size guard truncation (AC4)
- **Given:** Artifacts that total > max_bundle_size (use small limit, e.g., 1000 bytes)
- **When:** `gcp_role_context(work_item_id="TST-001", max_bundle_size=1000)`
- **Then:** Bundle is ≤ max_bundle_size, truncated artifacts have marker `[truncated — full file at <path>]`
- **Failure message:** "Bundle exceeds max size or missing truncation marker"

### TC5: Default role from state (AC5)
- **Given:** State.json with `current_role: "architect"`
- **When:** `gcp_role_context(work_item_id="TST-001")` (no role param)
- **Then:** Bundle contains architect role instructions
- **Failure message:** "Should default to current_role from state.json"

### TC6: No front-matter backward compat (AC6)
- **Given:** Role file without YAML front-matter
- **When:** `gcp_role_context(work_item_id="TST-001", role="legacy-role")`
- **Then:** Bundle contains role instructions + state, `## Input Artifacts` contains warning about missing front-matter
- **Failure message:** "Should handle missing front-matter gracefully with warning"

### TC7: Role instructions section never truncated (NFR)
- **Given:** Very large artifacts + small max_bundle_size
- **When:** `gcp_role_context(work_item_id="TST-001", max_bundle_size=500)`
- **Then:** `## Role Instructions` section is complete (not truncated)
- **Failure message:** "Role instructions must never be truncated"

### TC8: State summary section present (AC2)
- **Given:** Valid state.json
- **When:** `gcp_role_context(work_item_id="TST-001")`
- **Then:** `## Current State` contains work_item_id, current_role, current_phase
- **Failure message:** "State summary missing key fields"

### TC9: Previous role notes included
- **Given:** Work item with domain-expert notes, current role is quality-assurance
- **When:** `gcp_role_context(work_item_id="TST-001", role="quality-assurance")`
- **Then:** `## Previous Role Notes` contains domain-expert notes content
- **Failure message:** "Should include previous role's decision notes"

### TC10: Previous role notes for first role
- **Given:** Current role is project-owner-assistant (no previous role)
- **When:** `gcp_role_context(work_item_id="TST-001", role="project-owner-assistant")`
- **Then:** `## Previous Role Notes` shows `[no previous role]`
- **Failure message:** "First role should show no previous role marker"

### TC11: Invalid work item ID
- **Given:** Non-existent work item
- **When:** `gcp_role_context(work_item_id="FAKE-999")`
- **Then:** Result has `status: "error"` with descriptive message
- **Failure message:** "Should return error for invalid work item"

### TC12: Invalid role name
- **Given:** Valid work item, invalid role name
- **When:** `gcp_role_context(work_item_id="TST-001", role="nonexistent-role")`
- **Then:** Result has `status: "error"` with descriptive message
- **Failure message:** "Should return error for invalid role name"
