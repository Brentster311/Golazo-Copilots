# LLM-0012 Documentor Decision Notes

## Documentation Updates

1. **User Story status** — Updated from `BACKLOG` to `IMPLEMENTED`
2. **Architecture-Overview.md** — Added LLM-0012 to:
   - Work Item Landscape table
   - Module Map (discovery.py)
   - Dependency Graph (azure-mgmt-cognitiveservices, azure-mgmt-subscription)
   - Test Coverage table (test_discovery.py)
   - New "What LLM-0012 Added" section describing the feature

## Accuracy Check

- All module references match actual filenames on disk
- Dependency versions in Architecture Overview match pyproject.toml
- Test file listed in coverage table exists and runs (12 pass, 1 live-only)

## No README Update Needed

The README is a high-level project intro. The discovery feature is an optional extra
documented via docstrings in `discovery.py` and the Architecture Overview. No
user-facing README changes required at this time.
