# Review Comments — SFI-030

## Design Review

Design is clear and feasible. The 7-phase approach with dependency layering prevents circular imports. The re-export shim in `tk_app.py` ensures backward compatibility.

### Observation
No test code changes needed — re-exports handle all existing `from sfi_reporter.tk_app import X` patterns. This is the key design strength.

### Risk: `__all__` pollution
Using `from .module import *` without `__all__` could expose unintended names. Each new module should define `__all__` explicitly.

## Architect Notes

Architecture is sound. Dependency layering is correct — no cycle risk. The re-export shim is the right approach for backward compatibility.

### Approved with one note
- `dialogs.py` will be ~1600 lines. This is acceptable for now since the dialogs are self-contained classes. If it grows further, a `dialogs/` sub-package can be created in a future work item.
