# Program Manager Decision Notes — EES-00006

## Key Decisions

- **SettingsManager as pure Python class**: No Tkinter dependency, fully testable, reusable by CLI if needed later.
- **Three-tier resolution**: settings.yaml → env var → built-in default. User always sees the source in the dialog.
- **FactExtractor kwargs**: Rather than the GUI setting env vars, pass explicit kwargs. Cleaner and doesn't pollute process environment.
- **Built-in defaults match user's deployment**: endpoint=`open-ai-poc`, deployment=`gpt5.2`, api_version=`2025-12-11`.
