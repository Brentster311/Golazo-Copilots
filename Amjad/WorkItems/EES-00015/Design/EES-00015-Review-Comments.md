# EES-00015 — Review Comments

## Design Review
- Design is clear and appropriately scoped.
- No concerns with approach — bold tag on Treeview is standard Tkinter.
- Edge case noted: if no rules are proposed (e.g., extraction produces only facts), no facts should be bolded and the "Confirm Used" button should be a no-op.
- Edge case: facts with same noun but different property should NOT be bolded — match must be (noun, property) pair.
