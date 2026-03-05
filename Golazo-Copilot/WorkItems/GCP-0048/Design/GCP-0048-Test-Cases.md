# GCP-0048 Test Cases

## Test File: `test_role_self_contained.py`

All tests operate on the role files in `golazo_copilot/roles/defaults/`.

---

### TC-1: Every role file has YAML front-matter (AC1)
**Type:** Parametrized across all 10 role files
**Input:** Each role file content
**Steps:**
1. Load role file content
2. Assert content starts with `---\n`
3. Find closing `---\n` delimiter
4. Parse YAML between delimiters
5. Assert parsed YAML contains keys: `inputs`, `outputs`, `tools`
6. Assert `inputs` is a list (may be empty for POA)
7. Assert `outputs` is a list with at least 1 entry
8. Assert `tools` is a list with at least 1 entry

**Expected:** All 10 role files pass
**Failure message:** `{role}.md missing or invalid YAML front-matter: {detail}`

---

### TC-2: No implicit cross-role references (AC2)
**Type:** Parametrized across all 10 role files
**Input:** Each role file content (excluding front-matter section)
**Steps:**
1. Load role file content
2. Strip YAML front-matter block
3. Search for regex patterns: `previous role|from the last|earlier phase|already created|role complete|implementation complete|DoR complete`
4. Assert zero matches

**Expected:** Zero matches across all files
**Failure message:** `{role}.md contains implicit cross-role reference: "{match}" at line {line}`

---

### TC-3: All artifact references use explicit WorkItems paths (AC3)
**Type:** Parametrized across all 10 role files
**Input:** Role file content
**Steps:**
1. Load role file content
2. Find all references matching `{id}-*.md` pattern (artifact refs with {id} placeholder)
3. For each match, verify it's prefixed with `WorkItems/{id}/` or is inside front-matter (which uses relative paths within WorkItems)
4. Exclude HTML comments, code blocks, and the front-matter block itself

**Expected:** All artifact references include full WorkItems path prefix
**Failure message:** `{role}.md has bare artifact reference without WorkItems path: "{match}" at line {line}`

---

### TC-4: output_validator backward compatibility (AC4)
**Type:** Integration test
**Input:** Each updated role file
**Steps:**
1. Load role file content (with front-matter)
2. Call `parse_required_outputs(content, "TEST-001")`
3. Assert returned OutputSpec list matches expected outputs for that role
4. Assert count matches the `## Required Outputs` file lines

**Expected:** Parser returns correct OutputSpec objects despite front-matter
**Failure message:** `output_validator.parse_required_outputs failed for {role}.md: expected {expected} outputs, got {actual}`

---

### TC-5: Front-matter outputs consistent with Required Outputs (AC6)
**Type:** Parametrized across all 10 role files
**Input:** Each role file
**Steps:**
1. Parse YAML front-matter `outputs:` list
2. Parse `## Required Outputs` section (using output_validator parser)
3. Normalize both lists (strip `WorkItems/{id}/` prefix, substitute `{id}` → placeholder)
4. Assert the sets are equivalent

**Expected:** Zero drift between front-matter and Required Outputs
**Failure message:** `{role}.md front-matter/Required Outputs drift: front-matter has {fm_only}, Required Outputs has {ro_only}`

---

### TC-6: YAML front-matter is valid YAML (AC1 edge case)
**Type:** Parametrized across all 10 role files
**Input:** Front-matter block text
**Steps:**
1. Extract text between `---` delimiters
2. Parse with `yaml.safe_load()`
3. Assert no YAMLError raised
4. Assert result is a dict

**Expected:** Valid YAML dict for all files
**Failure message:** `{role}.md has invalid YAML front-matter: {yaml_error}`

---

### TC-7: Front-matter tools list includes gcp_status and gcp_transition (universal tools)
**Type:** Parametrized across all 10 role files
**Input:** Front-matter `tools:` value
**Steps:**
1. Parse front-matter
2. Assert `gcp_status` in tools list
3. Assert `gcp_transition` in tools list

**Expected:** All roles include both universal tools
**Failure message:** `{role}.md missing universal tool in front-matter: {missing_tool}`

---

### TC-8: TechBestPractices.md reference path is correct
**Type:** Parametrized across roles that reference TechBestPractices (architect, developer, refactor-expert, project-owner-assistant)
**Input:** Role file content
**Steps:**
1. Search for "TechBestPractices" references
2. Verify each reference uses `.github/roles/TechBestPractices.md` path

**Expected:** Correct path used
**Failure message:** `{role}.md references TechBestPractices with wrong path: "{found_path}"`
