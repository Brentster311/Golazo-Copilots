# SFI-025 — Builder Decision Notes

## Work Item
**ID**: SFI-025  
**Title**: Configure LLM — GUI dialog with manual entry and auto-detect

## Build Results

### Tests
- **230/231 passed** (1 pre-existing flaky test unrelated to this work item)
- **13/13 SFI-025 tests passed**

### PyInstaller Build
- **Command**: `python -m PyInstaller --onefile --name SFIReporter --hidden-import sfi_reporter.query_builder --hidden-import sfi_reporter.eta_logic --hidden-import llm_extender --hidden-import llm_extender.exceptions --hidden-import llm_extender.url_fetcher --hidden-import llm_extender.client --hidden-import llm_extender.config --hidden-import llm_extender.auth --hidden-import llm_extender.providers --hidden-import llm_extender.discovery --paths C:\...\LLMExtender src/sfi_reporter/tk_app.py`
- **Note**: Added `--hidden-import llm_extender.discovery` for the new auto-detect feature
- **Result**: Build completed successfully
- **Artifact**: `dist/SFIReporter.exe` (~47 MB)
- **Package**: `dist/SFIReporter.zip` (~47 MB)

### Git
Branch management deferred to user's workflow preference.
