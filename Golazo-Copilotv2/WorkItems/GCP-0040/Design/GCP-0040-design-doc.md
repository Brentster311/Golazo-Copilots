# Design Doc — GCP-0040: Bootstrap — Scaffold capabilities.yaml Template

## Summary
Add a `capabilities-template.yaml` resource to the golazo_copilot package and have `gcp_bootstrap` copy it to the workspace root as `capabilities.yaml` (respecting skip/force logic).

## Problem Statement
Users who want to use the capability registry (GCP-0038) must write `capabilities.yaml` from scratch with no schema reference. Bootstrap should scaffold a starter file.

## Proposed Approach

### 1. New package resource
Create `golazo-copilot/src/golazo_copilot/capabilities-template.yaml` containing:
- A YAML comment header explaining the schema
- One fully commented example capability with all fields (`name`, `description`, `key_files`, `contracts`, `depends_on`)
- A second stub capability to demonstrate the list structure

### 2. Bootstrap logic change
In `gcp_bootstrap.py`:
- After the existing `.gitkeep` block, add a new block that:
  1. Reads `capabilities-template.yaml` from package resources (same pattern as `bootstrap-instructions.md`)
  2. Writes it to `{workspace_root}/capabilities.yaml`
  3. Follows the same skip/force logic:
     - If `capabilities.yaml` exists and `force=False` → append to `files_skipped`
     - If `capabilities.yaml` exists and `force=True` → overwrite, append to `files_created`
     - If `capabilities.yaml` doesn't exist → write, append to `files_created`

### 3. No changes to `gcp_capabilities.py`
The template must pass `gcp_capabilities(action="validate")` as-is.

## Alternatives Considered
- **Inline the template as a Python string**: Rejected — harder to maintain, loses YAML syntax highlighting
- **Generate from schema**: Over-engineered for a static template

## Risks & Mitigations
- **Risk**: Template drifts from schema → **Mitigation**: Add a test that validates the template with `gcp_capabilities`
- **Risk**: Package resource not included in wheel → **Mitigation**: Hatchling auto-includes all files in `src/`; test confirms resource loads

## Test Strategy
1. Bootstrap creates `capabilities.yaml` when it doesn't exist
2. Bootstrap skips `capabilities.yaml` when it exists and `force=False`
3. Bootstrap overwrites `capabilities.yaml` when `force=True`
4. Template content includes comment header and example capability
5. Template passes `gcp_capabilities(action="validate")` (key_files may be missing, that's expected — validate checks file existence)
6. Template is parseable YAML with `capabilities` key

## Dependencies
- GCP-0038 (capability registry tool) — already shipped
