# GCP-0043 — Quality Assurance Decision Notes

## Decisions Made

### 1. Design Approved with Minor Comments
The design is well-scoped and addresses the gap between documented convention and code enforcement. No structural changes requested.

### 2. Underscore Removal is an Intentional Breaking Change
The old regex allowed underscores (`^[a-zA-Z0-9_-]+$`) but the new pattern (`^[A-Za-z]{1,4}-\d{3,}$`) does not. This is intentional and correct — no existing work items use underscores. Added explicit rejection test (TC1.4) to document this behavioral change.

### 3. Comprehensive Test ID Mapping
Rather than ad-hoc replacements, provided a complete mapping table for all 17 test cases that need ID updates. This prevents partial updates that would cause test failures.

### 4. Boundary Testing Emphasis
Added specific boundary test cases (1-letter prefix, 4-letter prefix, 5-letter prefix, 2-digit suffix, 3-digit suffix) because regex boundary conditions are a common source of off-by-one errors.

### 5. Error Message Quality as Testable Criterion
Added TC1.8 specifically to verify the error message includes examples. This is a non-functional requirement from the user story and ensures the tool is self-documenting.
