# GCP-0027 Project Owner Assistant Notes

## Decision: Remove gcp_mark_dor and gcp_mark_dod

### Context
GCP-0025 introduced automatic output validation based on role files. GCP-0026 updated all role files with Required Outputs sections. The manual marking tools are now redundant.

### Alternatives Considered
1. **Keep tools as deprecated** - Adds confusion, agents still try to use them
2. **Remove tools entirely** - Clean break, simplifies workflow ✅ CHOSEN

### Tradeoffs
- Breaking change for any workflows depending on these tools
- Simplifies the tool surface from 7 to 5 tools
- Removes friction in the workflow

### Known Limitations
- state.json still contains dor/dod sections (harmless, not used)
- Future work could clean up state.json schema (not in scope)
