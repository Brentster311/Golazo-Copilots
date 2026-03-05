# PO Notes — GCP-0040

## Scope Decision
Single new output from `gcp_bootstrap`: a template `capabilities.yaml`. Follows existing skip/force logic for all other bootstrap outputs.

## Dependency
Depends on GCP-0038 (schema defined). Independent of GCP-0039, GCP-0041, GCP-0042.
