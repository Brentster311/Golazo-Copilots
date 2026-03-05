# GCP-0027 Project Owner Assistant Notes

## Decision: Remove gcp_mark_dor/gcp_mark_dod tools and clean up dead code

### Context
GCP-0025 introduced automatic output validation based on role files (`output_validator.py`), replacing the manual evidence-based marking system (`evidence.py`). GCP-0026 updated all role files with Required Outputs sections. The manual marking tools (`gcp_mark_dor`, `gcp_mark_dod`) and the old evidence module are now redundant.

The original GCP-0027 removed the mark tools but missed deleting `evidence.py` and `test_evidence.py` — dead code that was explicitly slated for removal in the GCP-0025 Phase 3 design. This restarted work item corrects that oversight.

### Scope Decisions
- **In scope**: Remove `gcp_mark_dor`, `gcp_mark_dod`, `gcp_mark.py`, `evidence.py`, `test_evidence.py`, related test files
- **Out of scope**: `checklists.py` — verified it is still actively imported by `gcp_status.py`
- **Out of scope**: `output_validator.py` — this is the *replacement* for `evidence.py`, not dead code

### Verification performed
- `grep` confirmed zero production imports of `evidence.py`
- `grep` confirmed `checklists.py` is imported by `gcp_status.py` (must keep)
- `grep` confirmed zero references to `gcp_mark_dor`/`gcp_mark_dod` in source

### Alternatives Considered
1. **Keep tools as deprecated** — Adds confusion, agents still try to use them
2. **Remove tools entirely + clean up dead code** — Clean break, simplifies workflow ✅ CHOSEN

### Tradeoffs
- Breaking change for any workflows depending on mark tools
- Simplifies the tool surface from 7 to 5 tools
- Removes friction and orphaned code

### Must-Ask Checklist
- **Interface type**: MCP server (Python library) — already established
- **Target platform**: Cross-platform — already established
- **Data persistence**: Files (state.json) — already established
- **User type**: Technical (developers using AI agents) — already established
