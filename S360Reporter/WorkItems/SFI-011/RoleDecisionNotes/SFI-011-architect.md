# SFI-011: Architect Notes

## Architectural Review

### Alignment
The column toggle UI follows existing patterns:
- Modal dialogs (ItemDetailsModal pattern)
- Class variables for session state
- Helper functions for logic

### Key Contracts Defined

1. **REQUIRED_COLUMNS**: List of columns that can't be hidden
2. **COLUMN_DISPLAY_NAMES**: Human-readable names for columns
3. **Helper functions**: 5 functions for column management
4. **Class methods**: 3 methods for session state

### Tkinter Implementation Notes

**Scrollable Checkbox List**:
```python
# Create scrollable frame
canvas = tk.Canvas(parent)
scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
scrollable_frame.bind("<Configure>", 
    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
```

**Required Column Protection**:
```python
cb = ttk.Checkbutton(frame, text=display_name, variable=var)
if column in REQUIRED_COLUMNS:
    cb.state(['disabled'])  # Can't uncheck
```

### Integration Points

1. **DrillDownModal.__init__**: Add Columns button to header
2. **DrillDownModal._build_table**: Use visible columns only
3. **New ColumnSelectorDialog class**: Toplevel dialog

### Dependencies
- Reuse `format_field_label()` for column display names
- No new external dependencies

## Approved for Development
Architecture is sound and aligns with existing patterns.
