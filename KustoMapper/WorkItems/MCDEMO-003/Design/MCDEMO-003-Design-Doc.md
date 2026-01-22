# Design Doc: MCDEMO-003

## Summary
Add a graph visualization tab to the GUI using tkinter Canvas.

## Approach
- New GraphView class in gui/graph_view.py
- Uses tkinter Canvas for drawing
- Force-directed layout for node positioning
- Integrates with RelationshipDetector from MCDEMO-002
