# PM Notes — GCP-0040

## Summary
Design doc created. Straightforward extension of the existing bootstrap pattern: add a template YAML resource, read it with `importlib.resources`, write with skip/force logic.

## Key Decisions
- Template stored as a package resource (`capabilities-template.yaml`), not inline Python string
- Same skip/force contract as all other bootstrap files
- Template must be valid YAML with `capabilities` key (self-documenting with comments)
