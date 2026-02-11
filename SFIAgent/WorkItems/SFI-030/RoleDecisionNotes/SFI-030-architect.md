# Architect Notes — SFI-030

Approved. Dependency layering prevents circular imports. Re-export shim maintains backward compat. `dialogs.py` at ~1600 lines is acceptable — classes are self-contained.
