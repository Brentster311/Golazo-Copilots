# Architect Notes — GCP-0042

## Summary
Approved. Self-contained YAML parse in `_get_registry_hint()` — no coupling to `gcp_capabilities.py`. Use `yaml.safe_load` + `encoding="utf-8"`.
