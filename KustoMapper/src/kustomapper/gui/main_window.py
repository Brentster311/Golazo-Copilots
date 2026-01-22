import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
import threading
from kustomapper.adapters.kusto_adapter import KustoAdapter
from kustomapper.cache.schema_cache import SchemaCache
from kustomapper.models.schema import TableInfo
from kustomapper.gui.graph_view import GraphView
from kustomapper.analysis.relationship_detector import RelationshipDetector

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KustoMapper - Table Discovery")
        self.root.geometry("900x600")
        self.adapter = None
        self.cache = None
        self.tables = []
        self._setup_ui()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        self._setup_connection_panel(main_frame)
        self._setup_content_area(main_frame)
        self._setup_status_bar(main_frame)
    
    def _setup_connection_panel(self, parent):
        conn_frame = ttk.LabelFrame(parent, text="Connection", padding="5")
        conn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        conn_frame.columnconfigure(3, weight=1)
        ttk.Label(conn_frame, text="Cluster URL:").grid(row=0, column=0, sticky="w")
        self.cluster_var = tk.StringVar(value="https://help.kusto.windows.net")
        self.cluster_entry = ttk.Entry(conn_frame, textvariable=self.cluster_var, width=40)
        self.cluster_entry.grid(row=0, column=1, sticky="ew", padx=(0, 15))
        ttk.Label(conn_frame, text="Database:").grid(row=0, column=2, sticky="w")
        self.database_var = tk.StringVar(value="Samples")
        self.database_entry = ttk.Entry(conn_frame, textvariable=self.database_var, width=30)
        self.database_entry.grid(row=0, column=3, sticky="ew", padx=(0, 15))
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.grid(row=0, column=4, sticky="e")
        self.connect_btn = ttk.Button(btn_frame, text="Connect", command=self._on_connect)
        self.connect_btn.pack(side="left", padx=2)
        self.refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self._on_refresh, state="disabled")
        self.refresh_btn.pack(side="left", padx=2)
        self.disconnect_btn = ttk.Button(btn_frame, text="Disconnect", command=self._on_disconnect, state="disabled")
        self.disconnect_btn.pack(side="left", padx=2)
        self.graph_btn = ttk.Button(btn_frame, text="Show Graph", command=self._on_show_graph, state="disabled")
        self.graph_btn.pack(side="left", padx=2)
    
    def _setup_content_area(self, parent):
        content_frame = ttk.Frame(parent)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)
        table_frame = ttk.LabelFrame(content_frame, text="Tables", padding="5")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        table_scroll = ttk.Scrollbar(table_frame)
        table_scroll.grid(row=0, column=1, sticky="ns")
        self.table_listbox = tk.Listbox(table_frame, yscrollcommand=table_scroll.set, font=("Consolas", 10))
        self.table_listbox.grid(row=0, column=0, sticky="nsew")
        table_scroll.config(command=self.table_listbox.yview)
        self.table_listbox.bind("<<ListboxSelect>>", self._on_table_select)
        schema_frame = ttk.LabelFrame(content_frame, text="Schema", padding="5")
        schema_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        schema_frame.columnconfigure(0, weight=1)
        schema_frame.rowconfigure(0, weight=1)
        columns = ("Column Name", "Data Type", "Nullable")
        self.schema_tree = ttk.Treeview(schema_frame, columns=columns, show="headings")
        for col in columns:
            self.schema_tree.heading(col, text=col)
            self.schema_tree.column(col, width=150)
        schema_scroll = ttk.Scrollbar(schema_frame, orient="vertical", command=self.schema_tree.yview)
        self.schema_tree.configure(yscrollcommand=schema_scroll.set)
        self.schema_tree.grid(row=0, column=0, sticky="nsew")
        schema_scroll.grid(row=0, column=1, sticky="ns")
    
    def _setup_status_bar(self, parent):
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.status_var = tk.StringVar(value="Ready. Enter cluster and database, then click Connect.")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief="sunken", anchor="w")
        status_label.grid(row=0, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
    
    def _on_connect(self):
        cluster = self.cluster_var.get().strip()
        database = self.database_var.get().strip()
        if not cluster or not database:
            messagebox.showerror("Error", "Please enter both Cluster URL and Database name.")
            return
        self.status_var.set(f"Connecting to {cluster}...")
        self.connect_btn.config(state="disabled")
        self.root.update()
        def connect_task():
            try:
                self.adapter = KustoAdapter()
                self.adapter.connect(cluster=cluster, database=database)
                self.cache = SchemaCache(cluster=cluster, database=database)
                cached = self.cache.load_tables()
                if cached:
                    self.tables = cached
                    self.root.after(0, lambda: self._update_table_list(True))
                else:
                    self.tables = self.adapter.get_tables()
                    self.cache.save_tables(self.tables)
                    self.root.after(0, lambda: self._update_table_list(False))
                self.root.after(0, self._on_connect_success)
            except Exception as e:
                self.root.after(0, lambda: self._on_connect_error(str(e)))
        threading.Thread(target=connect_task, daemon=True).start()
    
    def _on_connect_success(self):
        self.connect_btn.config(state="disabled")
        self.refresh_btn.config(state="normal")
        self.disconnect_btn.config(state="normal")
        self.graph_btn.config(state="normal")
        self.cluster_entry.config(state="disabled")
        self.database_entry.config(state="disabled")
    
    def _on_connect_error(self, error_msg: str):
        self.connect_btn.config(state="normal")
        self.status_var.set("Connection failed.")
        messagebox.showerror("Connection Error", error_msg)
    
    def _update_table_list(self, from_cache: bool = False):
        self.table_listbox.delete(0, tk.END)
        if not self.tables:
            self.status_var.set("No tables found in database.")
            return
        for table in self.tables:
            self.table_listbox.insert(tk.END, table.name)
        src = "cache" if from_cache else "Kusto"
        self.status_var.set(f"Connected. Found {len(self.tables)} tables (from {src}).")
    
    def _on_table_select(self, event):
        selection = self.table_listbox.curselection()
        if not selection: return
        table_name = self.table_listbox.get(selection[0])
        self.status_var.set(f"Loading schema for {table_name}...")
        self.root.update()
        def load_schema():
            try:
                cached = self.cache.load_schema(table_name) if self.cache else None
                if cached:
                    columns = cached
                else:
                    columns = self.adapter.get_table_schema(table_name)
                    if self.cache: self.cache.save_schema(table_name, columns)
                self.root.after(0, lambda: self._update_schema_view(table_name, columns))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
        threading.Thread(target=load_schema, daemon=True).start()
    
    def _update_schema_view(self, table_name: str, columns):
        for item in self.schema_tree.get_children(): self.schema_tree.delete(item)
        if not columns:
            self.status_var.set(f"No columns found for {table_name}.")
            return
        for col in columns:
            self.schema_tree.insert("", tk.END, values=(col.name, col.data_type, "Yes" if col.nullable else "No"))
        self.status_var.set(f"Schema loaded for {table_name}: {len(columns)} columns.")
    
    def _on_refresh(self):
        if self.cache: self.cache.invalidate()
        self._on_disconnect()
        self._on_connect()
    
    def _on_disconnect(self):
        if self.adapter: self.adapter.disconnect()
        self.adapter = None
        self.tables = []
        self.table_listbox.delete(0, tk.END)
        for item in self.schema_tree.get_children(): self.schema_tree.delete(item)
        self.connect_btn.config(state="normal")
        self.refresh_btn.config(state="disabled")
        self.disconnect_btn.config(state="disabled")
        self.graph_btn.config(state="disabled")
        self.cluster_entry.config(state="normal")
        self.database_entry.config(state="normal")
        self.status_var.set("Disconnected.")
    
    def _on_show_graph(self):
        """Open a new window showing the relationship graph."""
        if not self.tables:
            messagebox.showinfo("No Data", "No tables loaded. Connect to a database first.")
            return
        
        self.status_var.set("Detecting relationships...")
        self.root.update()
        
        # Detect relationships
        detector = RelationshipDetector(self.tables)
        relationships = detector.detect_all()
        
        # Create graph window
        graph_window = tk.Toplevel(self.root)
        graph_window.title(f"Relationship Graph - {len(self.tables)} tables, {len(relationships)} relationships")
        graph_window.geometry("800x600")
        
        # Create GraphView
        graph_view = GraphView(graph_window)
        graph_view.set_data(self.tables, relationships)
        
        self.status_var.set(f"Graph opened: {len(self.tables)} tables, {len(relationships)} relationships detected.")
    
    def run(self): self.root.mainloop()
