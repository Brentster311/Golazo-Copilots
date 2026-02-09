# GCP-0027 Review Comments

## Design Review

### Overall Assessment
Design is clear, well-scoped, and correctly identifies the key gap: `required_outputs` data is computed but silently dropped by `server.py`. The 6-step sequencing is logical.

### Findings

#### Finding 1: bootstrap-instructions.md version is 2.17.0
- **Severity**: Medium
- **Details**: The file header says v2.17.0 but the package is at v2.100.8. This should be updated to match during the cleanup.
- **Recommendation**: Update version header in bootstrap-instructions.md to match pyproject.toml version after bump.

#### Finding 2: _generate_next_steps needs validation_result passed in
- **Severity**: Medium
- **Details**: The design says to pass `validation_result` to `_generate_next_steps()` but doesn't specify the function signature change. Currently `_generate_next_steps(state, role_content)` — needs a third parameter.
- **Recommendation**: Add `validation_result: ValidationResult = None` as optional parameter to maintain backward compatibility.

#### Finding 3: Remediation text format needs to be specific
- **Severity**: Medium
- **Details**: AC #5 says "remediation action (what to create/fix)" but the design only shows something like "Create `<path>` — required by <role>". Need to specify the exact format.
- **Recommendation**: Format should be: `"- Create file: <resolved_path>"` for files, `"- Create directory: <resolved_path>"` for dirs, matching the existing `OutputSpec.type`.

#### Finding 4: server.py required_outputs rendering location
- **Severity**: Low
- **Details**: Design says "render required_outputs" in server.py but doesn't specify where in the status output it should appear. Should be after DoR/DoD, before Next Steps.
- **Recommendation**: Add between DoR/DoD block and Next Steps, format as checklist.

### Scope Verification
- AC 1-4: Deletion/cleanup — straightforward verification via grep
- AC 5: Status enhancement — requires code changes to `server.py` and `gcp_status.py`
- AC 6: Regression — test suite run
- AC 7: Version bump — pyproject.toml edit

All within scope. No new user stories needed.

### Risk Review
- Low risk overall — mostly deletions and formatting
- `server.py` formatting change is the highest risk item — test thoroughly

---

## Architect Notes

### Architectural Review Date
(Added during architect role)

### AR-1: Call ordering — _generate_next_steps() is invoked before output validation
- **Severity**: High — this is a sequencing bug the design must address explicitly
- **Details**: In `gcp_status.py`, `_generate_next_steps()` is called at line 53, but `validate_all_outputs()` runs at lines 78-91. If we want remediation in next_steps, we must **move the _generate_next_steps() call after the validation block**, or compute validation first and pass results down.
- **Decision**: Move the output validation block (lines 78-91) above the `_generate_next_steps()` call (line 53). Then pass the validation outputs to `_generate_next_steps()`. This is the minimal-change approach — reorder two blocks rather than restructuring the function.
- **Impact**: Low — the function return value is built at the end, so reordering computation within the function body doesn't affect callers.

### AR-2: _generate_next_steps signature change — backward compatibility
- **Agrees with QA Finding 2**: Add `required_outputs: list[dict] | None = None` as optional parameter. This preserves backward compatibility if the function is called without it.
- **Contract**: The `required_outputs` parameter receives the same list of dicts already built at lines 84-89 (`[{"path": ..., "type": ..., "valid": ...}]`). No new data structure needed.

### AR-3: Remediation text — coupling to OutputSpec.type values
- **Details**: The remediation format depends on `OutputSpec.type` values (`file`, `dir`, `git-branch`, `git-log`). If new types are added, remediation must be updated.
- **Mitigation**: Use a simple mapping: `{"file": "Create file", "dir": "Create directory"}`. For unknown types, fall back to `"Ensure <type>: <path>"`. This is forward-compatible.

### AR-4: server.py required_outputs rendering — placement and format
- **Agrees with QA Finding 4**: Place between DoR/DoD bullets and Next Steps header.
- **Format decision**: Use checklist format consistent with DoR/DoD display:
  ```
  - Required Outputs: [check] 3/4
    [x] WorkItems/{id}/{id}-User-Story.md
    [ ] WorkItems/{id}/RoleDecisionNotes/{id}-architect.md
  ```
- **Boundary**: Only render this section when `required_outputs["outputs"]` is non-empty. Roles with no Required Outputs in their role file should show nothing, not an empty block.

### AR-5: bootstrap-instructions.md — full audit scope
- **Details**: Beyond removing `gcp_mark` references, the version header (currently 2.17.0) must be updated to match the post-bump version from pyproject.toml.
- **Risk**: Other stale content may exist. Limit scope to `gcp_mark` references and version header — don't rewrite the entire file.

### AR-6: No new external dependencies — confirmed
- All changes are within existing modules. No new imports. `output_validator` types are already imported by `gcp_status.py`.

### AR-7: Blast radius and rollback safety
- **Deletions** (evidence.py, test_evidence.py): Already done. Git history preserves them.
- **server.py formatting**: Additive — adds a new section to status output. No existing data removed.
- **gcp_status.py**: Reorder + parameter addition. Backward-compatible.
- **bootstrap-instructions.md**: Text-only change. No code impact.
- **Rollback**: `git revert` of the final commit cleanly undoes all changes.

### Summary
Design is approved with one required adjustment: **move output validation above `_generate_next_steps()` call** (AR-1). No new user stories needed. No scope changes.
