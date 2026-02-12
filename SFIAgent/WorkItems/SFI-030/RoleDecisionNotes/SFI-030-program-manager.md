# Program Manager Notes — SFI-030

## Decision: Express Profile

Pure structural refactor with no behavior changes. 7-phase implementation is straightforward extraction with a re-export shim for backward compatibility.

## Key Risk: query_builder.py

`query_builder.py` imports `SortableTreeview` and `DetailModal` from `tk_app`. These will move to `dialogs.py` but the re-export shim handles this. No changes needed in query_builder.py.
