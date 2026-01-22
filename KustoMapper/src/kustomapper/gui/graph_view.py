"""Graph visualization for table relationships using tkinter Canvas."""

import tkinter as tk
import math
from typing import List, Dict, Tuple, Optional
from kustomapper.models.schema import TableInfo, RelationshipInfo


class GraphView:
    """A canvas-based graph visualization for table relationships."""
    
    NODE_RADIUS = 30
    NODE_COLOR = "#4488CC"
    NODE_SELECTED_COLOR = "#FF6644"
    EDGE_COLOR = "#888888"
    EDGE_HIGHLIGHT_COLOR = "#FF6644"
    
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(parent, bg="white", width=600, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.nodes: Dict[str, dict] = {}
        self.edges: List[dict] = []
        self.selected_node: Optional[str] = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self._drag_data = {"x": 0, "y": 0}
        
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B2-Motion>", self._on_pan)
        self.canvas.bind("<Button-2>", self._on_pan_start)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def set_data(self, tables: List[TableInfo], relationships: List[RelationshipInfo]):
        """Set the graph data and render."""
        self.nodes.clear()
        self.edges.clear()
        self.selected_node = None
        
        if not tables:
            self._render()
            return
        
        positions = self._calculate_layout(tables)
        for table in tables:
            x, y = positions[table.name]
            self.nodes[table.name] = {"x": x, "y": y, "table": table}
        
        for rel in relationships:
            if rel.source_table in self.nodes and rel.target_table in self.nodes:
                self.edges.append({"source": rel.source_table, "target": rel.target_table, "rel": rel})
        
        self._render()
    
    def _calculate_layout(self, tables: List[TableInfo]) -> Dict[str, Tuple[float, float]]:
        """Calculate circular layout for nodes."""
        positions = {}
        n = len(tables)
        if n == 0:
            return positions
        
        cx = 300
        cy = 200
        radius = min(150, 50 * n)
        
        for i, table in enumerate(tables):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            positions[table.name] = (x, y)
        
        return positions
    
    def _render(self):
        """Render the graph on the canvas."""
        self.canvas.delete("all")
        
        for edge in self.edges:
            src = self.nodes[edge["source"]]
            tgt = self.nodes[edge["target"]]
            highlight = self.selected_node in (edge["source"], edge["target"])
            color = self.EDGE_HIGHLIGHT_COLOR if highlight else self.EDGE_COLOR
            width = 3 if highlight else 1
            self.canvas.create_line(
                self._tx(src["x"]), self._ty(src["y"]),
                self._tx(tgt["x"]), self._ty(tgt["y"]),
                fill=color, width=width
            )
        
        for name, node in self.nodes.items():
            is_selected = name == self.selected_node
            color = self.NODE_SELECTED_COLOR if is_selected else self.NODE_COLOR
            r = self.NODE_RADIUS * self.scale
            x = self._tx(node["x"])
            y = self._ty(node["y"])
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="#333", width=2)
            self.canvas.create_text(x, y, text=name, fill="white", font=("Arial", 9))
    
    def _tx(self, x):
        """Transform x coordinate with scale and offset."""
        return x * self.scale + self.offset_x
    
    def _ty(self, y):
        """Transform y coordinate with scale and offset."""
        return y * self.scale + self.offset_y
    
    def _on_click(self, event):
        """Handle click to select node."""
        for name, node in self.nodes.items():
            x = self._tx(node["x"])
            y = self._ty(node["y"])
            r = self.NODE_RADIUS * self.scale
            if (event.x - x)**2 + (event.y - y)**2 <= r**2:
                self.select_node(name)
                return
        self.select_node(None)
    
    def select_node(self, name: Optional[str]):
        """Select a node by name or clear selection."""
        self.selected_node = name
        self._render()
    
    def _on_pan_start(self, event):
        """Start panning."""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def _on_pan(self, event):
        """Handle panning."""
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.offset_x += dx
        self.offset_y += dy
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._render()
    
    def _on_mousewheel(self, event):
        """Handle zoom with mouse wheel."""
        factor = 1.1 if event.delta > 0 else 0.9
        self.zoom(factor)
    
    def zoom(self, factor: float):
        """Zoom the graph by a factor."""
        self.scale *= factor
        self._render()
