# Test Cases — GCP-0040

## TC1: Bootstrap creates capabilities.yaml when absent
- **Setup**: Temp workspace with `pyproject.toml`, no `capabilities.yaml`
- **Action**: `gcp_bootstrap(workspace_path=tmp)`
- **Assert**: `capabilities.yaml` exists in workspace root; `"capabilities.yaml"` in `files_created`

## TC2: Bootstrap skips capabilities.yaml when exists and force=False
- **Setup**: Temp workspace with pre-existing `capabilities.yaml` containing custom content
- **Action**: `gcp_bootstrap(workspace_path=tmp, force=False)`
- **Assert**: `"capabilities.yaml"` in `files_skipped`; file content unchanged

## TC3: Bootstrap overwrites capabilities.yaml when force=True
- **Setup**: Temp workspace with pre-existing `capabilities.yaml` containing custom content
- **Action**: `gcp_bootstrap(workspace_path=tmp, force=True)`
- **Assert**: `"capabilities.yaml"` in `files_created`; file content matches template

## TC4: Template is valid YAML with capabilities key
- **Action**: Load `capabilities-template.yaml` from package resources, `yaml.safe_load`
- **Assert**: Result is a dict with `"capabilities"` key; value is a non-empty list

## TC5: Template example capability has all expected fields
- **Action**: Parse template, inspect first capability
- **Assert**: Has keys `name`, `description`, `key_files`; `name` is a non-empty string

## TC6: Template contains YAML comment header
- **Action**: Read raw text of template
- **Assert**: First line starts with `#`

## TC7: Bootstrap with include_roles=False still creates capabilities.yaml
- **Setup**: Temp workspace
- **Action**: `gcp_bootstrap(workspace_path=tmp, include_roles=False)`
- **Assert**: `capabilities.yaml` exists; `"capabilities.yaml"` in `files_created`
