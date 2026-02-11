# PO Notes — GCP-0042

## Scope Decision
Code change to `gcp_status.py` + `server.py` formatter. Advisory only — shows hint if registry exists, silent if not. Must not crash on malformed YAML.

## Dependency
Depends on GCP-0038 (tool + `_load_registry` helper). Independent of GCP-0039, GCP-0040, GCP-0041.
