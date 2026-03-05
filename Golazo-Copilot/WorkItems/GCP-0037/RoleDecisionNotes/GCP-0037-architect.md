# Architect Notes — GCP-0037

## Decision
Approved. Minimal change, well-contained.

## Recommendations
- File mapping as a constant for extensibility
- Consistent `encoding="utf-8"` on all reads
- try/except around source reads to prevent crashes from corrupted installs
