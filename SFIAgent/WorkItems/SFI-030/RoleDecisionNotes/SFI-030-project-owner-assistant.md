# Project Owner Assistant Notes — SFI-030

## Decision: Module Boundaries

Selected 6-module split based on dependency layering (no cycles):

```
models.py → formatters.py → services.py → dialogs.py → app.py
                                                          ↑
                                                      tk_app.py (re-exports)
```

## Rationale

- **models.py**: Zero dependencies on other sfi_reporter modules. OrgAncestry, constants, column config.
- **services.py**: Business logic that imports from `data.py` and `models.py`. No UI code.
- **formatters.py**: Pure functions (format_field_label, extract_urls, etc.) — no state, no imports from services.
- **dialogs.py**: All Tk modal dialogs. Imports from models, formatters, services.
- **app.py**: SFIReporterApp class + main(). Imports everything.
- **tk_app.py**: Backward-compat shim with `from .models import *` etc.

## Express Profile

Using express profile — this is a pure structural refactor with no behavior changes. Design doc not needed; the module boundary diagram above is sufficient.
