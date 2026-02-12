"""Tkinter dialog classes and reusable widgets for SFI Reporter."""
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from sfi_reporter.formatters import (
    clean_html_from_title,
    extract_urls_from_text,
    format_field_label,
    format_field_value,
    group_item_fields,
    parse_resource_uris,
)
from sfi_reporter.models import (
    COLUMN_DISPLAY_NAMES,
    REQUIRED_COLUMNS,
    _resolve_eta_status,
    _resolve_sla_display,
    get_empty_columns,
    validate_visible_columns,
)
from sfi_reporter.services import _load_setting, _save_setting

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SortableTreeview
# ---------------------------------------------------------------------------

class SortableTreeview(ttk.Treeview):
    """Treeview with sortable columns."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._sort_reverse = {}  # Track sort direction per column

    def heading(self, column, **kwargs):
        """Override heading to add sort on click."""
        if 'command' not in kwargs:
            kwargs['command'] = lambda c=column: self._sort_by_column(c)
        return super().heading(column, **kwargs)

    def sort_by_columns(self, columns: list[tuple[str, bool]]):
        """Sort treeview by multiple columns.

        Args:
            columns: List of (column_name, descending) tuples.
                     Applied in order, so last column is primary sort.
        """
        if not columns:
            return

        all_items = list(self.get_children(''))
        if not all_items:
            return

        def get_sort_key(item, col):
            val = self.set(item, col) or ''
            if val.replace(',', '').replace('.', '').replace('-', '').isdigit():
                try:
                    return (0, int(val.replace(',', '')))
                except ValueError:
                    return (1, val.lower())
            return (1, val.lower())

        for col, descending in columns:
            all_items.sort(key=lambda item: get_sort_key(item, col), reverse=descending)

        for index, item in enumerate(all_items):
            self.move(item, '', index)

    def _sort_by_column(self, col):
        """Sort treeview by column."""
        items = [(self.set(item, col), item) for item in self.get_children('')]

        reverse = self._sort_reverse.get(col, False)

        is_numeric = False
        for val, _ in items:
            if val:
                is_numeric = val.replace(',', '').replace('.', '').isdigit()
                break

        if is_numeric:
            def sort_key(x):
                try:
                    return int(x[0].replace(',', '')) if x[0] else 0
                except ValueError:
                    return 0
            items.sort(key=sort_key, reverse=reverse)
        else:
            items.sort(key=lambda x: (x[0] or '').lower(), reverse=reverse)

        for index, (_, item) in enumerate(items):
            self.move(item, '', index)

        self._sort_reverse[col] = not reverse


# ---------------------------------------------------------------------------
# ColumnSelectorDialog
# ---------------------------------------------------------------------------

class ColumnSelectorDialog(tk.Toplevel):
    """Modal dialog for selecting which columns to display in DetailModal."""

    # Class variable to store column visibility across modal instances (session only)
    _visible_columns: list[str] | None = None

    def __init__(self, parent, available_columns: list[str], on_apply: callable = None,
                 empty_columns: set[str] = None):
        super().__init__(parent)
        self.title("Select Columns")
        self.geometry("350x450")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 350) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 450) // 2
        self.geometry(f"+{x}+{y}")

        self.available_columns = available_columns
        self.on_apply = on_apply
        self._empty_columns = empty_columns or set()
        self._checkboxes: dict[str, tk.BooleanVar] = {}

        if ColumnSelectorDialog._visible_columns is None:
            ColumnSelectorDialog._visible_columns = list(available_columns)

        self._create_widgets()

        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()

    def _create_widgets(self):
        """Create the dialog content."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Select columns to display:",
                  font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(btn_frame, text="Select All",
                   command=self._select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear All",
                   command=self._clear_all).pack(side=tk.LEFT)

        list_container = ttk.Frame(main_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(list_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self._canvas.yview)
        scrollable_frame = ttk.Frame(self._canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )

        self._canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._canvas.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

        for col in self.available_columns:
            var = tk.BooleanVar(value=col in ColumnSelectorDialog._visible_columns)
            self._checkboxes[col] = var

            display_name = COLUMN_DISPLAY_NAMES.get(col, col)
            if col in self._empty_columns:
                display_name = f"{display_name} (empty)"

            cb = ttk.Checkbutton(scrollable_frame, text=display_name, variable=var)
            cb.pack(anchor=tk.W, pady=2)

            if col in REQUIRED_COLUMNS:
                var.set(True)
                cb.configure(state='disabled')

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(action_frame, text="Apply",
                   command=self._apply).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(action_frame, text="Cancel",
                   command=self.destroy).pack(side=tk.RIGHT)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _select_all(self):
        for col, var in self._checkboxes.items():
            var.set(True)

    def _clear_all(self):
        for col, var in self._checkboxes.items():
            if col in REQUIRED_COLUMNS:
                var.set(True)
            else:
                var.set(False)

    def _apply(self):
        ColumnSelectorDialog._visible_columns = [
            col for col, var in self._checkboxes.items() if var.get()
        ]
        ColumnSelectorDialog._visible_columns = validate_visible_columns(
            ColumnSelectorDialog._visible_columns
        )
        if self.on_apply:
            self.on_apply()
        self.destroy()

    @classmethod
    def get_visible_columns(cls) -> list[str] | None:
        return cls._visible_columns

    @classmethod
    def reset_visible_columns(cls):
        cls._visible_columns = None


# ---------------------------------------------------------------------------
# DetailModal
# ---------------------------------------------------------------------------

class DetailModal(tk.Toplevel):
    """Modal dialog showing drill-down details for action items."""

    COLUMNS = ("title", "service", "sla", "due_date", "eta_date", "eta_status", "assigned_to", "action_owner")

    def __init__(self, parent, title: str, items: list, service_names: dict = None, on_eta_complete=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("1000x500")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 1000) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.geometry(f"+{x}+{y}")

        self.service_names = service_names or {}
        self._items = items
        self._item_map = {}
        self._on_eta_complete = on_eta_complete
        self._create_widgets(items)

        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()

    def _create_widgets(self, items: list):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._main_frame = main_frame
        if not items:
            ttk.Label(main_frame, text="No items found.", font=("Segoe UI", 12)).pack(pady=20)
        else:
            self._build_tree(main_frame, items)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)

        self.eta_btn = ttk.Button(
            btn_frame, text="\U0001f4cb Update ETAs",
            command=self._on_detail_update_etas,
        )
        self.eta_btn.pack(side=tk.RIGHT, padx=(0, 5))
        if not items:
            self.eta_btn.configure(state="disabled")

        self.selected_eta_btn = ttk.Button(
            btn_frame, text="\U0001f4cb Update ETAs for selected",
            command=self._on_selected_eta_update,
            state="disabled",
        )
        self.selected_eta_btn.pack(side=tk.RIGHT, padx=(0, 5))

        self._count_label = ttk.Label(btn_frame, text=f"{len(items)} item(s)")
        self._count_label.pack(side=tk.LEFT)

    def _build_tree(self, parent_frame, items: list):
        columns = self.COLUMNS
        self.tree = SortableTreeview(parent_frame, columns=columns, show="headings", height=15)
        tree = self.tree

        tree.heading("title", text="Title")
        tree.heading("service", text="Service")
        tree.heading("sla", text="SLA Status")
        tree.heading("due_date", text="Due Date")
        tree.heading("eta_date", text="ETA Date")
        tree.heading("eta_status", text="ETA Status")
        tree.heading("assigned_to", text="Assigned To")
        tree.heading("action_owner", text="Action Owner")

        tree.column("title", width=220, anchor=tk.W)
        tree.column("service", width=130, anchor=tk.W)
        tree.column("sla", width=80, anchor=tk.CENTER)
        tree.column("due_date", width=85, anchor=tk.CENTER)
        tree.column("eta_date", width=85, anchor=tk.CENTER)
        tree.column("eta_status", width=100, anchor=tk.W)
        tree.column("assigned_to", width=90, anchor=tk.W)
        tree.column("action_owner", width=110, anchor=tk.W)

        y_scroll = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=tree.yview)
        x_scroll = ttk.Scrollbar(parent_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._item_map.clear()
        self._populate_rows(items)

        self.tree.sort_by_columns([('due_date', False)])

        tree.bind('<Double-1>', self._on_item_double_click)
        tree.bind('<Button-3>', self._on_item_right_click)
        tree.bind('<<TreeviewSelect>>', self._on_tree_select)

    def _on_tree_select(self, event=None):
        selection = self.tree.selection()
        count = len(selection)
        if count > 0:
            self.selected_eta_btn.configure(
                text=f"\U0001f4cb Update ETAs for {count} selected",
                state="normal",
            )
        else:
            self.selected_eta_btn.configure(
                text="\U0001f4cb Update ETAs for selected",
                state="disabled",
            )

    def _on_selected_eta_update(self):
        selection = self.tree.selection()
        if not selection:
            return
        selected_items = [self._item_map[iid] for iid in selection if iid in self._item_map]
        if not selected_items:
            return
        ManualEtaReviewDialog(
            self, selected_items,
            on_complete=self._on_detail_eta_complete,
        )

    def _on_detail_update_etas(self):
        items = self._items
        if not items:
            return
        ManualEtaReviewDialog(
            self, items,
            on_complete=self._on_detail_eta_complete,
        )

    def _on_detail_eta_complete(self, saved, skipped, failed):
        if not saved:
            return
        for item, eta_str, notes in saved:
            item['EtaDate'] = eta_str
            if notes:
                item['EtaStatus'] = notes
        self._refresh_items()
        if self._on_eta_complete:
            self._on_eta_complete(saved, skipped, failed)

    def _refresh_items(self):
        if hasattr(self, 'tree'):
            for child in self.tree.get_children():
                self.tree.delete(child)
            self._item_map.clear()
            self._populate_rows(self._items)
            self.tree.sort_by_columns([('due_date', False)])

    def _populate_rows(self, items: list):
        for item in items:
            svc_id = item.get('serviceTreeId', '')
            svc_name = self.service_names.get(svc_id, svc_id[:20] + '...' if len(svc_id) > 20 else svc_id)
            raw_title = item.get('title', '')
            clean_title = clean_html_from_title(raw_title)
            iid = self.tree.insert('', tk.END, values=(
                clean_title[:60],
                svc_name,
                _resolve_sla_display(item.get('SlaType')),
                (item.get('DueDate') or item.get('dueDate', ''))[:10],
                (item.get('EtaDate') or '')[:10],
                _resolve_eta_status(item.get('EtaStatus')),
                item.get('S360_AssignedTo') or item.get('assignedTo', ''),
                item.get('ActionOwnerName') or item.get('ActionOwnerAlias', ''),
            ))
            self._item_map[iid] = item

    def _on_item_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        iid = selection[0]
        item = self._item_map.get(iid)
        if not item:
            return
        ItemDetailsModal(self, item)

    def _on_item_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        item = self._item_map.get(iid)
        if not item:
            return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="\U0001f916 Analyze with LLM",
            command=lambda: _launch_llm_analysis(self, item),
        )
        menu.tk_popup(event.x_root, event.y_root)


# ---------------------------------------------------------------------------
# ItemDetailsModal
# ---------------------------------------------------------------------------

class ItemDetailsModal(tk.Toplevel):
    """Modal dialog showing full details for a single action item."""

    def __init__(self, parent, item: dict):
        super().__init__(parent)

        item_title = clean_html_from_title(item.get('title', 'Action Item Details'))
        window_title = item_title[:60] + '...' if len(item_title) > 60 else item_title
        self.title(window_title)

        self.geometry("800x650")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 800) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 650) // 2
        self.geometry(f"+{x}+{y}")

        self._link_counter = 0
        self._item = item
        self._create_widgets(item)

        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()

    def _open_column_selector(self):
        available = sorted(self._item.keys())
        empty_cols = get_empty_columns(self._item)
        ColumnSelectorDialog(self, available, on_apply=self._on_columns_changed,
                             empty_columns=empty_cols)

    def _open_eta_editor(self):
        SingleEtaEditDialog(self, self._item, on_saved=self._on_eta_saved)

    def _on_eta_saved(self, item: dict, eta_date: str, notes: str):
        item['EtaDate'] = eta_date
        if notes:
            item['EtaStatus'] = notes
        self._on_columns_changed()

    def _on_columns_changed(self):
        for widget in self._main_frame.winfo_children():
            widget.destroy()
        self._link_counter = 0
        self._build_content(self._item)

    def _open_url(self, url: str):
        import html
        webbrowser.open(html.unescape(url))

    def _insert_text_with_links(self, text_widget: tk.Text, content: str, base_tag: str = 'value'):
        """Insert text content, making URLs clickable."""
        if not content:
            return

        stripped = content.strip()

        if (stripped.startswith(('http://', 'https://'))
                and '<a ' not in content.lower()):
            self._link_counter += 1
            link_tag = f'link_{self._link_counter}'
            text_widget.insert(tk.END, stripped, (link_tag, 'hyperlink'))
            text_widget.tag_bind(link_tag, '<Button-1>', lambda e, u=stripped: self._open_url(u))
            text_widget.tag_bind(link_tag, '<Enter>', lambda e: text_widget.configure(cursor='hand2'))
            text_widget.tag_bind(link_tag, '<Leave>', lambda e: text_widget.configure(cursor=''))
            return

        urls = extract_urls_from_text(content)

        if not urls:
            text_widget.insert(tk.END, content, base_tag)
            return

        last_end = 0
        for url, display_text, start, end in urls:
            if start > last_end:
                text_widget.insert(tk.END, content[last_end:start], base_tag)

            if not url:
                if display_text.strip():
                    text_widget.insert(tk.END, display_text, base_tag)
            else:
                self._link_counter += 1
                link_tag = f'link_{self._link_counter}'
                text_widget.insert(tk.END, display_text, (link_tag, 'hyperlink'))
                text_widget.tag_bind(link_tag, '<Button-1>', lambda e, u=url: self._open_url(u))
                text_widget.tag_bind(link_tag, '<Enter>', lambda e: text_widget.configure(cursor='hand2'))
                text_widget.tag_bind(link_tag, '<Leave>', lambda e: text_widget.configure(cursor=''))

            last_end = end

        if last_end < len(content):
            text_widget.insert(tk.END, content[last_end:], base_tag)

    def _insert_resource_uris(self, text_widget: tk.Text, value):
        uris = parse_resource_uris(value)
        if not uris:
            text_widget.insert(tk.END, str(value), 'value')
            return

        text_widget.insert(tk.END, "\n", 'value')
        for uri in uris:
            self._link_counter += 1
            link_tag = f'link_{self._link_counter}'

            text_widget.insert(tk.END, "  \u2022 ", 'value')
            text_widget.insert(tk.END, uri, (link_tag, 'hyperlink'))
            text_widget.insert(tk.END, "\n", 'value')

            text_widget.tag_bind(link_tag, '<Button-1>', lambda e, u=uri: self._open_url(u))
            text_widget.tag_bind(link_tag, '<Enter>', lambda e: text_widget.configure(cursor='hand2'))
            text_widget.tag_bind(link_tag, '<Leave>', lambda e: text_widget.configure(cursor=''))

    def _create_widgets(self, item: dict):
        self._main_frame = ttk.Frame(self, padding=10)
        self._main_frame.pack(fill=tk.BOTH, expand=True)
        self._build_content(item)

    def _build_content(self, item: dict):
        visible = ColumnSelectorDialog.get_visible_columns()

        if visible is not None:
            display_item = {k: v for k, v in item.items() if k in visible}
            for req in REQUIRED_COLUMNS:
                if req in item and req not in display_item:
                    display_item[req] = item[req]
        else:
            display_item = item

        text_frame = ttk.Frame(self._main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10), padx=10, pady=10)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text.tag_configure('header', font=("Segoe UI", 11, "bold"))
        text.tag_configure('separator', foreground='gray')
        text.tag_configure('label', font=("Segoe UI", 10, "bold"))
        text.tag_configure('value', font=("Consolas", 10))
        text.tag_configure('hyperlink', foreground='blue', underline=True, font=("Consolas", 10))

        groups = group_item_fields(display_item)

        group_titles = {
            'identity': '📋 Identity',
            'status': '🔴 Status',           # Red circle indicator
            'dates': '🔵 Dates',             # Blue circle indicator
            'ownership': '🟣 Ownership',     # Purple circle indicator
            'service_program': '⚫ Service & Program',  # Black circle indicator
            'subscription': '☁️ Subscription',
            'resources': '🔗 Resources & Details',
            'other': '📎 Other',
        }

        group_order = ['identity', 'status', 'dates', 'ownership', 'service_program',
                       'subscription', 'resources', 'other']

        for group_name in group_order:
            fields = groups.get(group_name, [])
            if not fields:
                continue

            text.insert(tk.END, f"\n{group_titles.get(group_name, group_name)}\n", 'header')
            text.insert(tk.END, "\u2500" * 50 + "\n", 'separator')

            for field_name, formatted_value in fields:
                label = format_field_label(field_name)
                text.insert(tk.END, f"{label}: ", 'label')

                if field_name == 'ResourceURIs':
                    raw_value = item.get('ResourceURIs', formatted_value)
                    self._insert_resource_uris(text, raw_value)
                elif 'http' in formatted_value.lower() or '<a ' in formatted_value.lower():
                    self._insert_text_with_links(text, formatted_value)
                    text.insert(tk.END, "\n", 'value')
                else:
                    text.insert(tk.END, f"{formatted_value}\n", 'value')

            text.insert(tk.END, "\n")

        text.configure(state=tk.DISABLED)

        btn_frame = ttk.Frame(self._main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Columns", command=self._open_column_selector).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="\U0001f4c5 Update ETA",
                   command=self._open_eta_editor).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)


# ---------------------------------------------------------------------------
# ETA Update Dialogs  (SFI-019)
# ---------------------------------------------------------------------------

class SingleEtaEditDialog(tk.Toplevel):
    """Small dialog for editing a single item's ETA from the detail view (AC-4)."""

    def __init__(self, parent, item: dict, on_saved=None):
        super().__init__(parent)
        self.title("Update ETA")
        self.geometry("420x260")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 420) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 260) // 2
        self.geometry(f"+{x}+{y}")

        self._item = item
        self._on_saved = on_saved
        self._create_widgets()
        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()

    def _create_widgets(self):
        from sfi_reporter.eta_logic import propose_eta

        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        title = clean_html_from_title(self._item.get('title', ''))[:60]
        ttk.Label(frame, text=title, font=("Segoe UI", 10, "bold"),
                  wraplength=380).pack(anchor=tk.W)

        current_eta = (self._item.get('EtaDate') or 'None')[:10]
        ttk.Label(frame, text=f"Current ETA: {current_eta}",
                  foreground="gray").pack(anchor=tk.W, pady=(5, 0))

        proposed = propose_eta(
            self._item.get('dueDate') or self._item.get('DueDate'))

        eta_frame = ttk.Frame(frame)
        eta_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(eta_frame, text="New ETA:").pack(side=tk.LEFT)
        self._eta_var = tk.StringVar(value=proposed)
        self._eta_entry = ttk.Entry(eta_frame, textvariable=self._eta_var, width=15)
        self._eta_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(eta_frame, text="(YYYY-MM-DD)", foreground="gray").pack(side=tk.LEFT, padx=5)

        notes_frame = ttk.Frame(frame)
        notes_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(notes_frame, text="Status:").pack(side=tk.LEFT)
        self._notes_var = tk.StringVar(value=self._item.get('EtaStatus') or '')
        self._notes_entry = ttk.Entry(notes_frame, textvariable=self._notes_var, width=35)
        self._notes_entry.pack(side=tk.LEFT, padx=(5, 0))

        self._error_var = tk.StringVar()
        self._error_label = ttk.Label(frame, textvariable=self._error_var, foreground="red")
        self._error_label.pack(anchor=tk.W, pady=(5, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        self._save_btn = ttk.Button(btn_frame, text="\U0001f4be Save", command=self._on_save)
        self._save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def _on_save(self):
        from sfi_reporter.eta_logic import validate_eta_date, build_eta_update
        from sfi_reporter.data import get_client, get_current_user_alias

        date_str = self._eta_var.get().strip()
        ok, msg = validate_eta_date(date_str)
        if not ok:
            self._error_var.set(msg)
            return

        self._error_var.set("")
        self._save_btn.configure(state=tk.DISABLED)

        update = build_eta_update(
            self._item,
            date_str,
            notes=self._notes_var.get().strip(),
            fallback_alias=get_current_user_alias() or "",
        )

        def _save_bg():
            try:
                client = get_client()
                result = client.save_etas([update])
                self.after(0, lambda: self._on_save_result(result, date_str))
            except Exception as exc:
                self.after(0, lambda: self._on_save_error(str(exc)))

        threading.Thread(target=_save_bg, daemon=True).start()

    def _on_save_result(self, result, date_str: str):
        if result.success:
            logger.info("ETA saved for %s -> %s", self._item.get('id'), date_str)
            if self._on_saved:
                self._on_saved(self._item, date_str, self._notes_var.get().strip())
            self.destroy()
        else:
            self._save_btn.configure(state=tk.NORMAL)
            msg = result.error_message or "Unknown error"
            self._error_var.set(f"Save failed: {msg}")
            logger.warning("ETA save failed for %s: %s", self._item.get('id'), msg)

    def _on_save_error(self, msg: str):
        self._save_btn.configure(state=tk.NORMAL)
        self._error_var.set(f"Error: {msg}")


class EtaModeDialog(tk.Toplevel):
    """Ask user to choose Manual or Bulk mode (AC-1)."""

    def __init__(self, parent, total_count: int, invalid_count: int, on_choice=None):
        super().__init__(parent)
        self.title("Update ETAs")
        self.geometry("400x220")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 220) // 2
        self.geometry(f"+{x}+{y}")

        self._on_choice = on_choice
        self._create_widgets(total_count, invalid_count)
        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()

    def _create_widgets(self, total_count: int, invalid_count: int):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"\U0001f4c5 {total_count} total item(s), {invalid_count} with invalid ETAs",
                  font=("Segoe UI", 11, "bold")).pack(pady=(0, 15))

        ttk.Button(
            frame, text=f"\U0001f4dd Manual \u2014 review all {total_count} item(s)",
            command=lambda: self._choose("manual"),
        ).pack(fill=tk.X, pady=3)

        bulk_btn = ttk.Button(
            frame,
            text=f"\u26a1 Bulk \u2014 auto-fix {invalid_count} invalid ETA(s)" if invalid_count else "\u26a1 Bulk \u2014 no invalid ETAs to fix",
            command=lambda: self._choose("bulk"),
        )
        bulk_btn.pack(fill=tk.X, pady=3)
        if not invalid_count:
            bulk_btn.configure(state="disabled")

        ttk.Button(frame, text="Cancel",
                   command=self.destroy).pack(fill=tk.X, pady=(10, 0))

    def _choose(self, mode: str):
        self._on_choice(mode)
        self.destroy()


class ManualEtaReviewDialog(tk.Toplevel):
    """Step through items one-at-a-time for manual ETA review (AC-2)."""

    def __init__(self, parent, items: list[dict], on_complete=None):
        super().__init__(parent)
        self.title("Manual ETA Review")
        self.geometry("520x340")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 520) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 340) // 2
        self.geometry(f"+{x}+{y}")

        self._items = items
        self._index = 0
        self._saved: list[tuple[dict, str, str]] = []
        self._skipped: list[dict] = []
        self._failed: list[tuple[dict, str]] = []
        self._on_complete = on_complete

        self._frame = ttk.Frame(self, padding=15)
        self._frame.pack(fill=tk.BOTH, expand=True)
        self._show_current()

        self.bind('<Escape>', lambda e: self._cancel())
        self.focus_set()

    def _show_current(self):
        from sfi_reporter.eta_logic import propose_eta

        for w in self._frame.winfo_children():
            w.destroy()

        if self._index >= len(self._items):
            self._show_summary()
            return

        item = self._items[self._index]
        n = self._index + 1
        total = len(self._items)

        ttk.Label(self._frame, text=f"Item {n} of {total}",
                  font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        title = clean_html_from_title(item.get('title', ''))[:80]
        ttk.Label(self._frame, text=title, wraplength=480).pack(anchor=tk.W, pady=(5, 0))

        info_text = (
            f"Service: {item.get('S360_ServiceTreeServiceName', 'N/A')}\n"
            f"Current ETA: {(item.get('EtaDate') or 'None')[:10]}\n"
            f"Due Date: "
            f"{(item.get('dueDate') or item.get('DueDate') or 'N/A')[:10]}"
        )
        ttk.Label(self._frame, text=info_text, foreground="gray").pack(anchor=tk.W, pady=(5, 0))

        proposed = propose_eta(item.get('dueDate') or item.get('DueDate'))

        eta_f = ttk.Frame(self._frame)
        eta_f.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(eta_f, text="New ETA:").pack(side=tk.LEFT)
        self._eta_var = tk.StringVar(value=proposed)
        ttk.Entry(eta_f, textvariable=self._eta_var, width=15).pack(side=tk.LEFT, padx=5)

        notes_f = ttk.Frame(self._frame)
        notes_f.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(notes_f, text="Status:").pack(side=tk.LEFT)
        self._notes_var = tk.StringVar(value=item.get('EtaStatus') or '')
        ttk.Entry(notes_f, textvariable=self._notes_var, width=35).pack(side=tk.LEFT, padx=5)

        self._error_var = tk.StringVar()
        ttk.Label(self._frame, textvariable=self._error_var, foreground="red").pack(anchor=tk.W, pady=(5, 0))

        btn_f = ttk.Frame(self._frame)
        btn_f.pack(fill=tk.X, pady=(10, 0))
        self._accept_btn = ttk.Button(btn_f, text="\u2705 Accept", command=self._accept)
        self._accept_btn.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_f, text="\u23ed\ufe0f Skip", command=self._skip).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_f, text="\U0001f50d View Details", command=self._view_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_f, text="\u274c Cancel", command=self._cancel).pack(side=tk.RIGHT)

    def _view_details(self):
        if self._index < len(self._items):
            item = self._items[self._index]
            ItemDetailsModal(self, item)

    def _accept(self):
        from sfi_reporter.eta_logic import validate_eta_date, build_eta_update
        from sfi_reporter.data import get_client, get_current_user_alias

        date_str = self._eta_var.get().strip()
        ok, msg = validate_eta_date(date_str)
        if not ok:
            self._error_var.set(msg)
            return

        self._accept_btn.configure(state=tk.DISABLED)
        item = self._items[self._index]
        update = build_eta_update(
            item, date_str,
            notes=self._notes_var.get().strip(),
            fallback_alias=get_current_user_alias() or "",
        )

        def _save_bg():
            try:
                client = get_client()
                result = client.save_etas([update])
                self.after(0, lambda: self._on_result(result, item, date_str))
            except Exception as exc:
                self.after(0, lambda: self._on_error(item, str(exc)))

        threading.Thread(target=_save_bg, daemon=True).start()

    def _on_result(self, result, item, date_str):
        if result.success:
            logger.info("Manual ETA saved for %s -> %s", item.get('id'), date_str)
            self._saved.append((item, date_str, self._notes_var.get().strip()))
        else:
            msg = result.error_message or "Unknown"
            logger.warning("Manual ETA failed for %s: %s", item.get('id'), msg)
            self._failed.append((item, msg))
        self._index += 1
        self._show_current()

    def _on_error(self, item, msg):
        logger.warning("Manual ETA error for %s: %s", item.get('id'), msg)
        self._failed.append((item, msg))
        self._index += 1
        self._show_current()

    def _skip(self):
        self._skipped.append(self._items[self._index])
        self._index += 1
        self._show_current()

    def _cancel(self):
        self._skipped.extend(self._items[self._index:])
        self._show_summary()

    def _show_summary(self):
        for w in self._frame.winfo_children():
            w.destroy()

        ttk.Label(self._frame, text="\U0001f4ca Manual Update Summary",
                  font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
        ttk.Label(self._frame, text=f"\u2705 Saved: {len(self._saved)}").pack(anchor=tk.W)
        ttk.Label(self._frame, text=f"\u23ed\ufe0f Skipped: {len(self._skipped)}").pack(anchor=tk.W)
        ttk.Label(self._frame, text=f"\u274c Failed: {len(self._failed)}").pack(anchor=tk.W)

        if self._failed:
            ttk.Label(self._frame, text="\nFailed items:", foreground="red").pack(anchor=tk.W)
            for item, msg in self._failed[:5]:
                ttk.Label(
                    self._frame,
                    text=f"  \u2022 {item.get('id', '?')}: {msg}",
                    foreground="red", wraplength=480,
                ).pack(anchor=tk.W)

        logger.info("Manual ETA update complete: %d saved, %d skipped, %d failed",
                    len(self._saved), len(self._skipped), len(self._failed))

        ttk.Button(self._frame, text="Close", command=self._finish).pack(pady=(15, 0))

    def _finish(self):
        if self._on_complete:
            self._on_complete(self._saved, self._skipped, self._failed)
        self.destroy()


class BulkEtaProgressDialog(tk.Toplevel):
    """Show progress during bulk ETA update (AC-3)."""

    def __init__(self, parent, items: list[dict], on_complete=None):
        super().__init__(parent)
        self.title("Bulk ETA Update")
        self.geometry("450x220")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 450) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 220) // 2
        self.geometry(f"+{x}+{y}")

        self._items = items
        self._on_complete = on_complete
        self._saved: list[tuple[dict, str, str]] = []
        self._failed: list[tuple[dict, str]] = []

        self._frame = ttk.Frame(self, padding=15)
        self._frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self._frame, text=f"\u26a1 Updating {len(items)} item(s)\u2026",
                  font=("Segoe UI", 11, "bold")).pack(pady=(0, 10))

        self._progress_var = tk.IntVar(value=0)
        self._progress = ttk.Progressbar(
            self._frame, maximum=len(items),
            variable=self._progress_var, length=400)
        self._progress.pack(fill=tk.X, pady=5)

        self._status_var = tk.StringVar(value="Starting\u2026")
        ttk.Label(self._frame, textvariable=self._status_var).pack(anchor=tk.W)

        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self.after(100, self._start)

    def _start(self):
        threading.Thread(target=self._run_bulk, daemon=True).start()

    def _run_bulk(self):
        from sfi_reporter.eta_logic import propose_eta, build_eta_update
        from sfi_reporter.data import get_client, get_current_user_alias

        client = get_client()
        alias = get_current_user_alias() or ""

        for i, item in enumerate(self._items):
            eta_str = propose_eta(item.get('dueDate') or item.get('DueDate'))
            update = build_eta_update(item, eta_str, fallback_alias=alias)

            self.after(0, lambda idx=i, it=item: self._status_var.set(
                f"Saving {idx + 1}/{len(self._items)}: {it.get('id', '?')[:30]}"
            ))

            try:
                result = client.save_etas([update])
                if result.success:
                    self._saved.append((item, eta_str, ""))
                    logger.info("Bulk ETA saved for %s -> %s", item.get('id'), eta_str)
                else:
                    msg = result.error_message or "Unknown"
                    self._failed.append((item, msg))
                    logger.warning("Bulk ETA failed for %s: %s", item.get('id'), msg)
            except Exception as exc:
                self._failed.append((item, str(exc)))
                logger.warning("Bulk ETA error for %s: %s", item.get('id'), exc)

            self.after(0, lambda idx=i: self._progress_var.set(idx + 1))

        self.after(0, self._show_summary)

    def _show_summary(self):
        self.protocol("WM_DELETE_WINDOW", self._finish)

        for w in self._frame.winfo_children():
            w.destroy()

        ttk.Label(self._frame, text="\U0001f4ca Bulk Update Summary",
                  font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
        ttk.Label(self._frame, text=f"\u2705 Saved: {len(self._saved)}").pack(anchor=tk.W)
        ttk.Label(self._frame, text=f"\u274c Failed: {len(self._failed)}").pack(anchor=tk.W)

        if self._failed:
            ttk.Label(self._frame, text="\nFailed items:", foreground="red").pack(anchor=tk.W)
            for item, msg in self._failed[:5]:
                ttk.Label(
                    self._frame,
                    text=f"  \u2022 {item.get('id', '?')}: {msg}",
                    foreground="red", wraplength=400,
                ).pack(anchor=tk.W)

        logger.info("Bulk ETA update complete: %d saved, %d failed",
                    len(self._saved), len(self._failed))

        ttk.Button(self._frame, text="Close", command=self._finish).pack(pady=(15, 0))

    def _finish(self):
        if self._on_complete:
            self._on_complete(self._saved, [], self._failed)
        self.destroy()


# ---------------------------------------------------------------------------
# SubscriptionPickerDialog
# ---------------------------------------------------------------------------

class SubscriptionPickerDialog(tk.Toplevel):
    """Modal dialog to pick one Azure subscription from a list."""

    def __init__(self, parent, choices: list[str]):
        super().__init__(parent)
        self.title("Select Subscription")
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        self.result: str | None = None

        rows: list[tuple[str, str, str]] = []
        for c in choices:
            if "(" in c:
                idx = c.rfind("(")
                name = c[:idx].strip()
                sub_id = c[idx + 1:].rstrip(")")
            else:
                name = c
                sub_id = ""
            rows.append((name, sub_id, c))

        rows.sort(key=lambda r: r[0].lower())

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Choose a subscription to scan:").pack(anchor=tk.W, pady=(0, 8))

        tree_frame = ttk.Frame(frm)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self._tree = ttk.Treeview(
            tree_frame,
            columns=("name", "sub_id"),
            show="headings",
            selectmode="browse",
            height=min(len(rows), 15),
        )
        self._tree.heading("name", text="Subscription Name")
        self._tree.heading("sub_id", text="Subscription ID")
        self._tree.column("name", width=280, minwidth=150)
        self._tree.column("sub_id", width=300, minwidth=200)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._iid_to_choice: dict[str, str] = {}
        for i, (name, sub_id, original) in enumerate(rows):
            iid = str(i)
            self._tree.insert("", tk.END, iid=iid, values=(name, sub_id))
            self._iid_to_choice[iid] = original

        if rows:
            self._tree.selection_set("0")
            self._tree.focus("0")

        self._tree.bind("<Double-Button-1>", lambda _: self._on_ok())

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(pady=(10, 0))
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=5)

        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window()

    def _on_ok(self):
        sel = self._tree.selection()
        if sel:
            self.result = self._iid_to_choice[sel[0]]
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()


# ---------------------------------------------------------------------------
# ConfigureLLMDialog
# ---------------------------------------------------------------------------

class ConfigureLLMDialog(tk.Toplevel):
    """Modal dialog for configuring Azure OpenAI LLM settings."""

    _DEFAULT_DEPLOYMENT = "gpt-4o"
    _DEFAULT_API_VERSION = "2024-10-21"

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configure LLM")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self._discovered_configs: list = []

        self._endpoint_var = tk.StringVar(
            value=_load_setting("llm_endpoint", "") or ""
        )
        self._deployment_var = tk.StringVar(
            value=_load_setting("llm_deployment", self._DEFAULT_DEPLOYMENT) or self._DEFAULT_DEPLOYMENT
        )
        self._api_version_var = tk.StringVar(
            value=_load_setting("llm_api_version", self._DEFAULT_API_VERSION) or self._DEFAULT_API_VERSION
        )

        self._build_ui()

        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        pad = dict(padx=10, pady=4)
        frm = ttk.Frame(self, padding=15)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Endpoint:").grid(row=0, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self._endpoint_var, width=55).grid(
            row=0, column=1, columnspan=2, sticky=tk.EW, **pad)

        ttk.Label(frm, text="Deployment:").grid(row=1, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self._deployment_var, width=30).grid(
            row=1, column=1, columnspan=2, sticky=tk.EW, **pad)

        ttk.Label(frm, text="API Version:").grid(row=2, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self._api_version_var, width=30).grid(
            row=2, column=1, columnspan=2, sticky=tk.EW, **pad)

        detect_frame = ttk.LabelFrame(frm, text="Detect from Azure CLI", padding=8)
        detect_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=(10, 4), padx=10)

        self._detect_btn = ttk.Button(
            detect_frame, text="\U0001f50d Detect", command=self._on_auto_detect)
        self._detect_btn.pack(side=tk.LEFT, padx=(0, 10))

        self._config_combo = ttk.Combobox(detect_frame, state="readonly", width=60)
        self._config_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._config_combo.bind("<<ComboboxSelected>>", self._on_config_selected)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(15, 0))

        ttk.Button(btn_frame, text="Save", command=self._on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=self._on_clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _on_auto_detect(self):
        self._detect_btn.configure(text="Loading subs...", state="disabled")
        root = self.winfo_toplevel()

        def _list_subs():
            try:
                import logging as _log
                for _az in ("azure.core", "azure.identity", "azure.mgmt"):
                    _log.getLogger(_az).setLevel(_log.WARNING)
                from llm_extender.discovery import _ensure_azure_sdk, SubscriptionClient, AzureCliCredential
                _ensure_azure_sdk()
                import llm_extender.discovery as disc
                cred = disc.AzureCliCredential()
                sub_client = disc.SubscriptionClient(cred)
                subs = list(sub_client.subscriptions.list())
                root.after(0, lambda: self._on_subs_loaded(subs))
            except Exception as exc:
                root.after(0, lambda e=exc: self._on_detect_error(e))

        threading.Thread(target=_list_subs, daemon=True).start()

    def _on_subs_loaded(self, subs: list):
        self._detect_btn.configure(text="\U0001f50d Detect", state="normal")
        if not subs:
            messagebox.showinfo(
                "No Subscriptions",
                "No Azure subscriptions found.\n\nEnsure you are logged in with `az login`.",
                parent=self,
            )
            return

        choices = {f"{s.display_name}  ({s.subscription_id})": s.subscription_id for s in subs}

        picked = SubscriptionPickerDialog(self, list(choices.keys()))
        if not picked.result:
            return

        selected_sub_id = choices[picked.result]
        self._scan_subscription(selected_sub_id)

    def _scan_subscription(self, subscription_id: str):
        self._detect_btn.configure(text="Scanning...", state="disabled")
        root = self.winfo_toplevel()

        def _do_scan():
            try:
                import logging as _log
                for _az in ("azure.core", "azure.identity", "azure.mgmt"):
                    _log.getLogger(_az).setLevel(_log.WARNING)
                from llm_extender import discover_azure_configs
                configs = discover_azure_configs(subscription_id=subscription_id)
                root.after(0, lambda: self._on_detect_complete(configs))
            except Exception as exc:
                root.after(0, lambda e=exc: self._on_detect_error(e))

        threading.Thread(target=_do_scan, daemon=True).start()

    def _on_detect_complete(self, configs: list):
        self._detect_btn.configure(text="\U0001f50d Detect", state="normal")
        self._discovered_configs = configs
        if not configs:
            self._config_combo["values"] = []
            messagebox.showinfo(
                "No Results",
                "No Azure OpenAI deployments found in the selected subscription.",
                parent=self,
            )
            return
        labels = [
            f"{c.base_url}  \u2014  {c.deployment} ({c.model})"
            for c in configs
        ]
        self._config_combo["values"] = labels
        self._config_combo.current(0)
        self._on_config_selected(None)

    def _on_detect_error(self, error: Exception):
        self._detect_btn.configure(text="\U0001f50d Detect", state="normal")
        if isinstance(error, ImportError):
            messagebox.showerror(
                "Azure SDK Not Installed",
                "Azure discovery SDK is not available.\n\n"
                "Install with:\n  pip install llm-extender[azure-discover]",
                parent=self,
            )
        else:
            messagebox.showerror("Detection Failed", f"Discovery error: {error}", parent=self)

    def _on_config_selected(self, _event):
        idx = self._config_combo.current()
        if idx < 0 or idx >= len(self._discovered_configs):
            return
        cfg = self._discovered_configs[idx]
        self._endpoint_var.set(cfg.base_url)
        self._deployment_var.set(cfg.deployment)
        self._api_version_var.set(cfg.api_version)

    def _on_save(self):
        endpoint = self._endpoint_var.get().strip()
        deploy = self._deployment_var.get().strip()
        api_ver = self._api_version_var.get().strip()

        if not endpoint.startswith("https://"):
            messagebox.showerror("Invalid Endpoint", "Endpoint must start with https://", parent=self)
            return

        _save_setting("llm_endpoint", endpoint)
        _save_setting("llm_deployment", deploy or self._DEFAULT_DEPLOYMENT)
        _save_setting("llm_api_version", api_ver or self._DEFAULT_API_VERSION)
        logger.info("LLM config saved: endpoint=%s deployment=%s api_version=%s",
                    endpoint, deploy, api_ver)
        self.destroy()

    def _on_clear(self):
        _save_setting("llm_endpoint", "")
        _save_setting("llm_deployment", "")
        _save_setting("llm_api_version", "")
        self._endpoint_var.set("")
        self._deployment_var.set(self._DEFAULT_DEPLOYMENT)
        self._api_version_var.set(self._DEFAULT_API_VERSION)
        logger.info("LLM config cleared.")


# ---------------------------------------------------------------------------
# LLM Analysis UI Components
# ---------------------------------------------------------------------------

class AnalysisProgressModal(tk.Toplevel):
    """Modal progress dialog shown while LLM analysis is in flight."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Analyzing...")
        self.geometry("350x120")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 350) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 120) // 2
        self.geometry(f"+{x}+{y}")

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(frame, text="Preparing analysis...", font=("Segoe UI", 10))
        self.status_label.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(frame, mode="indeterminate", length=280)
        self.progress.pack()
        self.progress.start(15)

    def update_status(self, text: str):
        self.status_label.configure(text=text)

    def close(self):
        self.progress.stop()
        self.grab_release()
        self.destroy()


class AnalysisModal(tk.Toplevel):
    """Modal dialog displaying the LLM analysis result."""

    def __init__(self, parent, result):
        super().__init__(parent)

        title_text = result.title[:60] + "..." if len(result.title) > 60 else result.title
        self.title(f"LLM Analysis: {title_text}")
        self.geometry("800x650")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 800) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 650) // 2
        self.geometry(f"+{x}+{y}")

        self._result = result
        self._create_widgets()

        self.bind("<Escape>", lambda e: self.destroy())
        self.focus_set()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        y_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.text = tk.Text(
            text_frame, wrap=tk.WORD, font=("Segoe UI", 10),
            yscrollcommand=y_scroll.set, padx=12, pady=8,
        )
        y_scroll.configure(command=self.text.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text.tag_configure("header", font=("Segoe UI", 13, "bold"), spacing1=12, spacing3=4)
        self.text.tag_configure("section", font=("Segoe UI", 10), lmargin1=10, lmargin2=10)
        self.text.tag_configure("disclaimer", font=("Segoe UI", 8, "italic"), foreground="#888888")
        self.text.tag_configure("meta", font=("Segoe UI", 8), foreground="#666666")

        r = self._result

        sections = [
            ("\U0001f3af Mission", r.mission or "(No mission section parsed)"),
            ("\u2705 Steps to Done", r.steps_to_done or "(No steps section parsed)"),
            ("\U0001f527 Resources Needing Repair", r.resources or "(No resources section parsed)"),
            ("\u26a0\ufe0f Risk of Delay", r.risk_of_delay or "(No risk section parsed)"),
        ]

        for heading, body in sections:
            self.text.insert(tk.END, f"{heading}\n", "header")
            self.text.insert(tk.END, f"{body}\n\n", "section")

        self.text.insert(tk.END, "\n" + "\u2500" * 60 + "\n\n", "meta")

        ts = r.timestamp[:19].replace("T", " ") if r.timestamp else "unknown"
        meta = f"Model: {r.model}  |  Analyzed: {ts} UTC  |  Tokens: {r.prompt_tokens} in / {r.completion_tokens} out"
        self.text.insert(tk.END, meta + "\n", "meta")
        self.text.insert(tk.END, "\nAI-generated analysis \u2014 verify before acting.\n", "disclaimer")

        self.text.configure(state=tk.DISABLED)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="\U0001f4cb Copy to Clipboard",
                   command=self._copy_to_clipboard).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)

    def _copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self._result.analysis_text)
        original = self.title()
        self.title("Copied to clipboard!")
        self.after(1500, lambda: self.title(original))


# ---------------------------------------------------------------------------
# LLM Analysis launcher (shared by KPI tree and DrillDownModal)
# ---------------------------------------------------------------------------

def _launch_llm_analysis(parent, item: dict):
    """Launch LLM analysis for an action item."""
    from sfi_reporter.llm_client import LLMConfigError, LLMError, analyze_item, fetch_action_item_urls
    from sfi_reporter.llm_storage import save_analysis
    from sfi_reporter.services import _load_llm_config

    try:
        config = _load_llm_config()
    except LLMConfigError as e:
        messagebox.showerror("LLM Configuration Required", str(e), parent=parent)
        return

    root = parent.winfo_toplevel()

    progress = AnalysisProgressModal(parent)

    def do_analysis():
        try:
            root.after(0, lambda: progress.update_status("Fetching URL context..."))
            url_content = fetch_action_item_urls(item)

            root.after(0, lambda: progress.update_status("Calling Azure OpenAI..."))
            result = analyze_item(item, config, url_content=url_content or None)

            root.after(0, lambda: progress.update_status("Saving result..."))
            try:
                save_analysis(result)
            except OSError as e:
                logger.warning("Failed to save analysis: %s", e)

            root.after(0, lambda: _on_analysis_complete(root, progress, result))

        except LLMError as e:
            msg = str(e)
            root.after(0, lambda m=msg: _on_analysis_error(root, progress, m))
        except Exception as e:
            msg = f"Unexpected error: {e}"
            logger.error("Unexpected error during LLM analysis: %s", e)
            root.after(0, lambda m=msg: _on_analysis_error(root, progress, m))

    threading.Thread(target=do_analysis, daemon=True).start()


def _on_analysis_complete(root, progress: AnalysisProgressModal, result):
    progress.close()
    AnalysisModal(root, result)


def _on_analysis_error(root, progress: AnalysisProgressModal, error_msg: str):
    progress.close()
    messagebox.showerror("LLM Analysis Failed", error_msg, parent=root)


__all__ = [
    # Widgets
    'SortableTreeview',
    'ColumnSelectorDialog',
    # Modals
    'DetailModal',
    'ItemDetailsModal',
    'SingleEtaEditDialog',
    'EtaModeDialog',
    'ManualEtaReviewDialog',
    'BulkEtaProgressDialog',
    'SubscriptionPickerDialog',
    'ConfigureLLMDialog',
    # LLM Analysis
    'AnalysisProgressModal',
    'AnalysisModal',
    '_launch_llm_analysis',
    '_on_analysis_complete',
    '_on_analysis_error',
]
