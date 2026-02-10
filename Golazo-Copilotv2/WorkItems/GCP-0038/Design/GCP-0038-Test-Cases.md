# GCP-0038 — Test Cases

## TC-1: List action (AC1)
- **TC-1.1**: `action="list"` with valid registry returns all capability names + descriptions
- **TC-1.2**: `action="list"` with empty capabilities list returns empty list, no error

## TC-2: Show action (AC2)
- **TC-2.1**: `action="show", capability="X"` returns full card including computed `depended_on_by`
- **TC-2.2**: `action="show", capability="nonexistent"` returns clear "not found" message
- **TC-2.3**: `action="show"` without capability parameter returns error

## TC-3: Impact action (AC3)
- **TC-3.1**: `action="impact", files=["path/to/file.py"]` returns directly affected capabilities
- **TC-3.2**: Impact returns transitive dependents (A depends on B, file in B → returns B and A)
- **TC-3.3**: Diamond dependency (A→B→D, A→C→D) — file in D returns D, B, C, A without duplicates
- **TC-3.4**: Files matching zero capabilities returns empty result, not error
- **TC-3.5**: Suffix matching works (input `status.py` matches key_file `src/tools/gcp_status.py`)
- **TC-3.6**: Exact match takes priority over suffix match

## TC-4: Validate action (AC4)
- **TC-4.1**: All key_files exist → all capabilities pass
- **TC-4.2**: Some key_files missing → those capabilities fail with specific missing files listed
- **TC-4.3**: Validate detects dangling `depends_on` references (bonus)

## TC-5: Missing registry (AC5)
- **TC-5.1**: No `capabilities.yaml` → all actions return "no registry found" message, success=true
- **TC-5.2**: Malformed YAML → clear error message

## TC-6: Depended-on-by computation (AC6)
- **TC-6.1**: Capability A depends on B → B's card shows `depended_on_by: [A]`
- **TC-6.2**: No dependents → `depended_on_by` is empty list
- **TC-6.3**: Circular dependency (A→B→A) → no infinite loop, both show each other

## TC-7: Cycle handling
- **TC-7.1**: Circular `depends_on` does not cause infinite loop in `impact` traversal
