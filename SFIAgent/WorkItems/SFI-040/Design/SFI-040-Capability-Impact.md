# SFI-040 Capability Impact

## Command
- `golazo_capabilities(action="impact", files=["SFIReporter/src/sfi_reporter/app.py", "SFIReporter/tests/test_sfi_039_app.py"])`

## Result
- Reported affected capabilities: **0**

## Interpretation
- Capability registry currently does not map these UI table paths to a named capability card.
- Proceeding with localized regression tests to validate behavior contract for table presentation.

## Risk
- Low; change remains in UI rendering layer only.
