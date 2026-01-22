import pytest
import sys

# Skip all GUI tests if tkinter is not available or in headless mode
try:
    import tkinter as tk
    _root = tk.Tk()
    _root.withdraw()
    _root.destroy()
    TK_AVAILABLE = True
except:
    TK_AVAILABLE = False

pytestmark = pytest.mark.skipif(not TK_AVAILABLE, reason="tkinter not available")

if TK_AVAILABLE:
    import tkinter as tk
    from kustomapper.models.schema import TableInfo, ColumnInfo, RelationshipInfo, RelationshipType
    from kustomapper.gui.graph_view import GraphView


@pytestmark
class TestGraphViewInitialization:
    def test_creates_canvas(self):
        root = tk.Tk()
        root.withdraw()
        view = GraphView(root)
        assert view.canvas is not None
        assert isinstance(view.canvas, tk.Canvas)
        root.destroy()


@pytestmark
class TestNodeCreation:
    def test_nodes_created_for_tables(self):
        root = tk.Tk()
        root.withdraw()
        view = GraphView(root)
        tables = [TableInfo("Users"), TableInfo("Orders")]
        view.set_data(tables, [])
        assert len(view.nodes) == 2
        root.destroy()


@pytestmark
class TestEdgeCreation:
    def test_edges_created_for_relationships(self):
        root = tk.Tk()
        root.withdraw()
        view = GraphView(root)
        tables = [TableInfo("Users"), TableInfo("Orders")]
        rels = [RelationshipInfo("Users","Id","Orders","UserId",RelationshipType.ID_SUFFIX)]
        view.set_data(tables, rels)
        assert len(view.edges) == 1
        root.destroy()


@pytestmark
class TestNodeSelection:
    def test_select_node_highlights(self):
        root = tk.Tk()
        root.withdraw()
        view = GraphView(root)
        tables = [TableInfo("Users")]
        view.set_data(tables, [])
        view.select_node("Users")
        assert view.selected_node == "Users"
        root.destroy()


@pytestmark
class TestPanZoom:
    def test_zoom_in(self):
        root = tk.Tk()
        root.withdraw()
        view = GraphView(root)
        initial_scale = view.scale
        view.zoom(1.2)
        assert view.scale > initial_scale
        root.destroy()


@pytestmark
class TestEdgeCases:
    def test_empty_graph(self):
        root = tk.Tk()
        root.withdraw()
        view = GraphView(root)
        view.set_data([], [])
        assert len(view.nodes) == 0
        assert len(view.edges) == 0
        root.destroy()
