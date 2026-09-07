#!/usr/bin/env python3
"""
Finance Data Explorer - Tkinter GUI for exploring finance.db
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path
from datetime import datetime
import calendar
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parents[0]
DB_PATH = ROOT / "analysis" / "finance.db"


class FinanceExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Finance Data Explorer")
        self.root.geometry("1200x700")

        self.sort_states = {}
        self.column_heading_text = {}

        # Default date range: 2026-01-01 through today.
        self.start_date_var = tk.StringVar(value="2026-01-01")
        self.end_date_var = tk.StringVar(value=datetime.now().date().isoformat())
        self.exclude_button_text = tk.StringVar(value="None")
        self.exclude_category_vars = {}
        self.exclude_popup = None
        self.item_detail_map = {}
        self._chart_frame = None
        self._chart_mousewheel_bound = False
        
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        
        self.setup_ui()
        self.load_categories()
        self.load_initial_data()
    
    def setup_ui(self):
        # Top filter frame
        filter_frame = ttk.Frame(self.root, padding="10")
        filter_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, width=20)
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        ttk.Label(filter_frame, text="Merchant:").pack(side=tk.LEFT, padx=5)
        self.merchant_var = tk.StringVar()
        self.merchant_entry = ttk.Entry(filter_frame, textvariable=self.merchant_var, width=25)
        self.merchant_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Start Date:").pack(side=tk.LEFT, padx=5)
        self.start_date_entry = ttk.Entry(filter_frame, textvariable=self.start_date_var, width=12)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="End Date:").pack(side=tk.LEFT, padx=5)
        self.end_date_entry = ttk.Entry(filter_frame, textvariable=self.end_date_var, width=12)
        self.end_date_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Exclude Categories:").pack(side=tk.LEFT, padx=5)
        self.exclude_menu_btn = ttk.Button(
            filter_frame,
            textvariable=self.exclude_button_text,
            width=30,
            command=self.toggle_exclude_popup,
        )
        self.exclude_menu_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Search", command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Reset", command=self.reset_filters).pack(side=tk.LEFT, padx=5)
        
        # View selection
        ttk.Label(filter_frame, text="View:").pack(side=tk.LEFT, padx=20)
        self.view_var = tk.StringVar(value="Transactions")
        views = [
            "Transactions",
            "Recurring Candidates",
            "Spend by Category",
            "Top Merchants",
            "Monthly Summary",
            "Monthly by Category",
        ]
        self.view_combo = ttk.Combobox(filter_frame, textvariable=self.view_var, values=views, width=20, state="readonly")
        self.view_combo.pack(side=tk.LEFT, padx=5)
        self.view_combo.bind("<<ComboboxSelected>>", lambda e: self.change_view())
        
        # Data frame with treeview
        data_frame = ttk.Frame(self.root)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(data_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(data_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_row_double_click)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def load_categories(self):
        categories = self.cur.execute("SELECT DISTINCT normalized_category FROM transactions ORDER BY normalized_category").fetchall()
        cat_list = ["All"] + [row[0] for row in categories]
        self.category_combo['values'] = cat_list

        self._refresh_exclude_categories()
        self._update_exclude_button_text()

    def _refresh_exclude_categories(self):
        selected = set(self._get_excluded_categories())
        categories = self.cur.execute(
            """
            SELECT DISTINCT normalized_category
            FROM transactions
            WHERE normalized_category IS NOT NULL
              AND TRIM(normalized_category) != ''
            ORDER BY normalized_category
            """
        ).fetchall()

        refreshed = {}
        for row in categories:
            cat = row[0]
            refreshed[cat] = tk.BooleanVar(value=(cat in selected))
        self.exclude_category_vars = refreshed
    
    def load_initial_data(self):
        self.show_transactions()

    def _normalize_date_input(self, value):
        text = (value or "").strip()
        if not text:
            return ""
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
            try:
                return datetime.strptime(text, fmt).date().isoformat()
            except ValueError:
                pass
        return None

    def _get_date_filter_values(self):
        start_raw = self.start_date_var.get()
        end_raw = self.end_date_var.get()

        start = self._normalize_date_input(start_raw)
        end = self._normalize_date_input(end_raw)

        if start is None:
            messagebox.showerror("Invalid Start Date", "Use YYYY-MM-DD or M/D/YYYY for start date.")
            return None
        if end is None:
            messagebox.showerror("Invalid End Date", "Use YYYY-MM-DD or M/D/YYYY for end date.")
            return None
        if start and end and start > end:
            messagebox.showerror("Invalid Date Range", "Start date must be on or before end date.")
            return None

        # Canonicalize the UI text to YYYY-MM-DD after successful parse.
        if start:
            self.start_date_var.set(start)
        if end:
            self.end_date_var.set(end)

        return start, end

    def _get_excluded_categories(self):
        return [cat for cat, var in self.exclude_category_vars.items() if var.get()]

    def _update_exclude_button_text(self):
        selected = self._get_excluded_categories()
        if not selected:
            self.exclude_button_text.set("None")
            return
        if len(selected) <= 2:
            self.exclude_button_text.set(", ".join(selected))
            return
        self.exclude_button_text.set(f"{len(selected)} selected")

    def _clear_excluded_categories(self):
        for var in self.exclude_category_vars.values():
            var.set(False)
        self._update_exclude_button_text()

    def toggle_exclude_popup(self):
        if self.exclude_popup and self.exclude_popup.winfo_exists():
            self._close_exclude_popup()
            return
        self._show_exclude_popup()

    def _show_exclude_popup(self):
        self._refresh_exclude_categories()
        self._update_exclude_button_text()

        popup = tk.Toplevel(self.root)
        popup.transient(self.root)
        popup.title("Exclude Categories")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        self.exclude_popup = popup

        x = self.exclude_menu_btn.winfo_rootx()
        y = self.exclude_menu_btn.winfo_rooty() + self.exclude_menu_btn.winfo_height()
        popup.geometry(f"420x460+{x}+{y}")

        outer = ttk.Frame(popup, padding=8)
        outer.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        list_frame = ttk.Frame(canvas)

        list_frame.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        window_id = canvas.create_window((0, 0), window=list_frame, anchor="nw")

        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(window_id, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for cat in sorted(self.exclude_category_vars.keys()):
            ttk.Checkbutton(
                list_frame,
                text=cat,
                variable=self.exclude_category_vars[cat],
                command=self._update_exclude_button_text,
            ).pack(anchor=tk.W, fill=tk.X)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        popup.bind("<MouseWheel>", _on_mousewheel)

        actions = ttk.Frame(popup, padding=(8, 0, 8, 8))
        actions.pack(fill=tk.X)
        ttk.Label(actions, text=f"{len(self.exclude_category_vars)} categories").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions, text="Clear", command=self._clear_excluded_categories).pack(side=tk.LEFT)
        ttk.Button(actions, text="Apply", command=self._apply_excluded_categories).pack(side=tk.RIGHT)

        popup.bind("<Escape>", lambda _e: self._close_exclude_popup())
        popup.protocol("WM_DELETE_WINDOW", self._close_exclude_popup)
        popup.focus_set()

    def _apply_excluded_categories(self):
        self._update_exclude_button_text()
        self._close_exclude_popup()
        self.apply_filters()

    def _close_exclude_popup(self):
        if self.exclude_popup and self.exclude_popup.winfo_exists():
            self.exclude_popup.destroy()
        self.exclude_popup = None

    def _store_row_details(self, item_id, detail):
        self.item_detail_map[str(item_id)] = detail

    def on_row_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.focus(item_id)
            self.tree.selection_set(item_id)
        else:
            item_id = self.tree.focus()
        if not item_id:
            return

        detail = self.item_detail_map.get(str(item_id))
        if detail is None:
            detail = {col: self.tree.set(item_id, col) for col in self.tree["columns"]}
            row_label = self.tree.item(item_id, "text")
            if row_label:
                detail["month"] = row_label
            category = self.tree.set(item_id, "Category") if "Category" in self.tree["columns"] else ""
            if category and category != "Total":
                detail["normalized_category"] = category

        if isinstance(detail, sqlite3.Row):
            detail = dict(detail)

        # For aggregate views, open transaction-level drilldown rows.
        if self.view_var.get() != "Transactions":
            if self._open_aggregate_drilldown(detail):
                return

        if isinstance(detail, dict):
            lines = [f"{k}: {v}" for k, v in detail.items()]
        else:
            lines = [str(detail)]

        top = tk.Toplevel(self.root)
        top.title("Row Details")
        top.geometry("900x520")

        txt = tk.Text(top, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", "\n".join(lines))
        txt.config(state=tk.DISABLED)

    def _open_aggregate_drilldown(self, detail):
        if not isinstance(detail, dict):
            return False

        date_values = self._get_date_filter_values()
        if date_values is None:
            return True
        start_date, end_date = date_values

        view = self.view_var.get()
        where_clauses = []
        params = []

        if start_date:
            where_clauses.append("txn_date >= ?")
            params.append(start_date)
        if end_date:
            where_clauses.append("txn_date <= ?")
            params.append(end_date)

        title = "Aggregation Drilldown"
        if view == "Spend by Category":
            category = detail.get("normalized_category")
            if not category:
                return False
            title = f"Transactions for Category: {category}"
            where_clauses.append("normalized_category = ?")
            where_clauses.append("amount < 0")
            params.extend([category])
        elif view == "Top Merchants":
            merchant = detail.get("normalized_merchant")
            if not merchant:
                return False
            title = f"Transactions for Merchant: {merchant}"
            where_clauses.append("normalized_merchant = ?")
            where_clauses.append("amount < 0")
            params.extend([merchant])
        elif view == "Monthly Summary":
            month = detail.get("month")
            if not month:
                return False
            title = f"Monthly Transactions: {month}"
            where_clauses.append("STRFTIME('%Y-%m', DATE(txn_date)) = ?")
            where_clauses.append("amount < 0")
            where_clauses.append("normalized_category != 'Transfers'")
            params.append(month)
            excluded = self._get_excluded_categories()
            if excluded:
                placeholders = ", ".join(["?"] * len(excluded))
                where_clauses.append(f"normalized_category NOT IN ({placeholders})")
                params.extend(excluded)
        elif view == "Monthly by Category":
            month = detail.get("month")
            if not month:
                return False
            category = detail.get("normalized_category")
            title = f"Monthly Transactions: {month}"
            where_clauses.append("STRFTIME('%Y-%m', DATE(txn_date)) = ?")
            where_clauses.append("amount < 0")
            params.append(month)
            excluded = self._get_excluded_categories()
            if excluded:
                placeholders = ", ".join(["?"] * len(excluded))
                where_clauses.append(f"normalized_category NOT IN ({placeholders})")
                params.extend(excluded)
            if category:
                title = f"Monthly Transactions: {month} / {category}"
                where_clauses.append("normalized_category = ?")
                params.append(category)
        elif view == "Recurring Candidates":
            merchant = detail.get("normalized_merchant")
            if not merchant:
                return False
            category = detail.get("normalized_category")
            title = f"Recurring Candidate Rows: {merchant}"
            where_clauses.append("normalized_merchant = ?")
            params.append(merchant)
            if category:
                where_clauses.append("normalized_category = ?")
                params.append(category)
        else:
            return False

        return self._show_transaction_drilldown(title, where_clauses, params)

    def _show_transaction_drilldown(self, title, where_clauses, params):
        query = """
            SELECT txn_date,
                   normalized_merchant,
                   normalized_category,
                   amount,
                   raw_description
            FROM transactions
        """
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " ORDER BY txn_date DESC, ABS(amount) DESC LIMIT 2000"

        rows = self.cur.execute(query, params).fetchall()

        top = tk.Toplevel(self.root)
        top.title(f"{title} ({len(rows)} rows)")
        top.geometry("1100x580")
        top.transient(self.root)
        top.lift()
        top.focus_force()

        frame = ttk.Frame(top, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        tree = ttk.Treeview(frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        tree["columns"] = ("Date", "Merchant", "Category", "Amount", "Description")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.heading("#0", text="")
        tree.column("Date", anchor=tk.W, width=110)
        tree.column("Merchant", anchor=tk.W, width=280)
        tree.column("Category", anchor=tk.W, width=170)
        tree.column("Amount", anchor=tk.E, width=120)
        tree.column("Description", anchor=tk.W, width=360)
        tree.heading("Date", text="Date", anchor=tk.W)
        tree.heading("Merchant", text="Merchant", anchor=tk.W)
        tree.heading("Category", text="Category", anchor=tk.W)
        tree.heading("Amount", text="Amount", anchor=tk.E)
        tree.heading("Description", text="Description", anchor=tk.W)

        for idx, row in enumerate(rows):
            amount = row[3] or 0
            tree.insert(
                "",
                tk.END,
                iid=str(idx),
                text="",
                values=(
                    row[0] or "",
                    (row[1] or "")[:60],
                    row[2] or "",
                    f"${abs(amount):,.2f}",
                    (row[4] or "")[:90],
                ),
            )

        return True

    def _parse_sort_value(self, value):
        text = "" if value is None else str(value).strip()
        if not text:
            return ""

        # Date format used by this app.
        try:
            return datetime.strptime(text, "%Y-%m-%d")
        except ValueError:
            pass

        # Currency/percent and other numeric-looking values.
        cleaned = text.replace("$", "").replace(",", "")
        if "(" in cleaned and cleaned.endswith("%)"):
            cleaned = cleaned.split("(", 1)[0].strip()
        try:
            return float(cleaned)
        except ValueError:
            return text.lower()

    def _set_heading(self, column, text, anchor=tk.W):
        self.column_heading_text[column] = text
        self.tree.heading(column, text=text, anchor=anchor, command=lambda c=column: self.sort_by_column(c))

    def _refresh_heading_arrows(self):
        for col in self.tree['columns']:
            base = self.column_heading_text.get(col, col)
            direction = self.sort_states.get(col)
            suffix = ""
            if direction is not None:
                suffix = " ▲" if not direction else " ▼"
            self.tree.heading(col, text=f"{base}{suffix}")

    def sort_by_column(self, column):
        rows = []
        for item in self.tree.get_children(""):
            rows.append((self._parse_sort_value(self.tree.set(item, column)), item))

        reverse = not self.sort_states.get(column, False)
        self.sort_states = {column: reverse}
        rows.sort(reverse=reverse, key=lambda row: row[0])

        for idx, (_, item) in enumerate(rows):
            self.tree.move(item, "", idx)

        self._refresh_heading_arrows()
    
    def show_transactions(self):
        date_values = self._get_date_filter_values()
        if date_values is None:
            return
        start_date, end_date = date_values

        self.tree.delete(*self.tree.get_children())
        self.item_detail_map = {}
        self.sort_states = {}
        self.column_heading_text = {}
        self.tree['columns'] = ('Date', 'Merchant', 'Category', 'Amount', 'Description')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('Date', anchor=tk.W, width=100)
        self.tree.column('Merchant', anchor=tk.W, width=300)
        self.tree.column('Category', anchor=tk.W, width=150)
        self.tree.column('Amount', anchor=tk.E, width=100)
        self.tree.column('Description', anchor=tk.W, width=300)
        
        self.tree.heading('#0', text='', anchor=tk.W)
        self._set_heading('Date', 'Date', anchor=tk.W)
        self._set_heading('Merchant', 'Merchant', anchor=tk.W)
        self._set_heading('Category', 'Category', anchor=tk.W)
        self._set_heading('Amount', 'Amount', anchor=tk.E)
        self._set_heading('Description', 'Description', anchor=tk.W)
        
        query = "SELECT * FROM transactions"
        params = []
        where_clauses = []

        if start_date:
            where_clauses.append("txn_date >= ?")
            params.append(start_date)
        if end_date:
            where_clauses.append("txn_date <= ?")
            params.append(end_date)
        
        if self.category_var.get() != "All":
            where_clauses.append("normalized_category = ?")
            params.append(self.category_var.get())
        
        if self.merchant_var.get():
            where_clauses.append("normalized_merchant LIKE ?")
            params.append(f"%{self.merchant_var.get()}%")

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY txn_date DESC LIMIT 500"
        
        rows = self.cur.execute(query, params).fetchall()
        for idx, row in enumerate(rows):
            item_id = str(idx)
            merchant = (row[12] or "")[:50]
            category = row[19] or ""
            amount = row[9] or 0
            description = (row[13] or "")[:50]
            self.tree.insert('', tk.END, iid=item_id, text='',
                           values=(row[6], merchant, category, f"${abs(amount):.2f}", description))
            self._store_row_details(item_id, dict(row))
        
        self.status_var.set(f"Showing {len(rows)} transactions")
    
    def show_recurring(self):
        self.tree.delete(*self.tree.get_children())
        self.item_detail_map = {}
        self.sort_states = {}
        self.column_heading_text = {}
        self.tree['columns'] = ('Merchant', 'Category', 'Count', 'Avg Amount', 'Cadence', 'Confidence')
        for col in self.tree['columns']:
            self.tree.column(col, anchor=tk.W, width=150)
            self._set_heading(col, col, anchor=tk.W)
        
        rows = self.cur.execute("SELECT normalized_merchant, normalized_category, txn_count, ROUND(avg_amount, 2), cadence_guess, ROUND(confidence, 2) FROM recurring_candidates ORDER BY confidence DESC LIMIT 100").fetchall()
        for idx, row in enumerate(rows):
            item_id = str(idx)
            self.tree.insert('', tk.END, iid=item_id, text='',
                           values=(row[0][:50], row[1], row[2], f"${row[3]:.2f}", row[4], row[5]))
            self._store_row_details(item_id, {
                "normalized_merchant": row[0],
                "normalized_category": row[1],
                "txn_count": row[2],
                "avg_amount": row[3],
                "cadence_guess": row[4],
                "confidence": row[5],
            })
        
        self.status_var.set(f"Showing {len(rows)} recurring candidates")
    
    def show_spend_by_category(self):
        date_values = self._get_date_filter_values()
        if date_values is None:
            return
        start_date, end_date = date_values

        # Hide the treeview and replace with scrollable chart canvas
        self.tree.pack_forget()
        self._destroy_chart_frame()

        # ── Fetch monthly spend per category ──────────────────────────────
        excluded_categories = self._get_excluded_categories()
        params = []
        where_clauses = ["amount < 0"]
        if start_date:
            where_clauses.append("txn_date >= ?")
            params.append(start_date)
        if end_date:
            where_clauses.append("txn_date <= ?")
            params.append(end_date)
        if excluded_categories:
            placeholders = ", ".join(["?"] * len(excluded_categories))
            where_clauses.append(f"normalized_category NOT IN ({placeholders})")
            params.extend(excluded_categories)

        where_sql = " AND ".join(where_clauses)
        monthly_q = f"""
            SELECT normalized_category,
                   STRFTIME('%Y-%m', DATE(txn_date)) AS month,
                   ROUND(SUM(-amount), 2) AS spend
            FROM transactions
            WHERE {where_sql}
            GROUP BY normalized_category, month
            ORDER BY normalized_category, month
        """
        monthly_rows = self.cur.execute(monthly_q, params).fetchall()

        # Total spend per category for ordering
        total_q = f"""
            SELECT normalized_category,
                   ROUND(SUM(-amount), 2) AS total_spend
            FROM transactions
            WHERE {where_sql}
            GROUP BY normalized_category
            ORDER BY total_spend DESC
        """
        totals = self.cur.execute(total_q, params).fetchall()
        category_order = [r[0] for r in totals if r[1] and r[1] > 0]

        # Build dict: {category: {month: spend}}
        all_months = sorted({r[1] for r in monthly_rows if r[1]})
        cat_data = {}
        for cat, month, spend in monthly_rows:
            cat_data.setdefault(cat, {})[month] = spend or 0

        # Only consider months that are fully covered by the current date range.
        start_bound = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_bound = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        complete_months = []
        for month in all_months:
            month_start = datetime.strptime(f"{month}-01", "%Y-%m-%d").date()
            month_end = month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1])
            start_ok = (start_bound is None) or (start_bound <= month_start)
            end_ok = (end_bound is None) or (end_bound >= month_end)
            if start_ok and end_ok:
                complete_months.append(month)
        complete_month_set = set(complete_months)
        complete_month_count = len(complete_months)

        # ── Build scrollable frame ────────────────────────────────────────
        chart_outer = tk.Frame(self.tree.master)
        chart_outer.pack(fill=tk.BOTH, expand=True)
        self._chart_frame = chart_outer

        vsb = ttk.Scrollbar(chart_outer, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        canvas_scroll = tk.Canvas(chart_outer, yscrollcommand=vsb.set,
                                   highlightthickness=0, bg="white")
        canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=canvas_scroll.yview)

        inner = tk.Frame(canvas_scroll, bg="white")
        win_id = canvas_scroll.create_window((0, 0), window=inner, anchor="nw")

        canvas_scroll.bind(
            "<Configure>",
            lambda e: canvas_scroll.itemconfig(win_id, width=e.width),
        )
        inner.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")),
        )

        def _on_mousewheel(event):
            canvas_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas_scroll.bind_all("<MouseWheel>", _on_mousewheel)
        self._chart_mousewheel_bound = True

        # ── Draw one chart per category ───────────────────────────────────
        CHART_H = 2.4  # inches per chart
        colors = matplotlib.colormaps["tab10"].colors
        x = range(len(all_months))

        # ── Stacked area summary chart at top ─────────────────────────────
        if category_order and all_months:
            stack_h = max(3.2, 0.18 * len(category_order))
            sfig = Figure(figsize=(12, stack_h), dpi=96, facecolor="white")
            sax = sfig.add_subplot(111)
            sax.set_facecolor("#f7f9fc")

            stack_bottom = [0.0] * len(all_months)
            total_by_month = [0.0] * len(all_months)
            for i, cat in enumerate(category_order):
                monthly = cat_data.get(cat, {})
                y_vals = [monthly.get(m, 0) for m in all_months]
                color = colors[i % len(colors)]
                sax.fill_between(x, stack_bottom,
                                 [stack_bottom[j] + y_vals[j] for j in range(len(all_months))],
                                 alpha=0.75, color=color, label=cat)
                stack_bottom = [stack_bottom[j] + y_vals[j] for j in range(len(all_months))]
                total_by_month = [total_by_month[j] + y_vals[j] for j in range(len(all_months))]

            grand_total = sum(total_by_month)
            if complete_month_count:
                complete_total = sum(
                    total_by_month[idx] for idx, month in enumerate(all_months) if month in complete_month_set
                )
                avg_full_month = complete_total / complete_month_count
                avg_text = f" | avg full month ${avg_full_month:,.2f}"
            else:
                avg_text = " | avg full month n/a"
            sax.set_xticks(list(x))
            sax.set_xticklabels(all_months, fontsize=7, rotation=45, ha="right")
            sax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
            sax.tick_params(axis="y", labelsize=7)
            sax.set_title(
                f"All Categories (stacked)   —   total ${grand_total:,.2f}{avg_text}",
                fontsize=9, fontweight="bold", loc="left", pad=4,
            )
            sax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.5)
            sax.legend(loc="upper right", fontsize=6.5, ncol=3,
                       framealpha=0.85, borderpad=0.4, labelspacing=0.3)
            sfig.tight_layout(pad=0.6)

            sfc = FigureCanvasTkAgg(sfig, master=inner)
            sfc.draw()
            sfc.get_tk_widget().pack(fill=tk.X, padx=8, pady=(8, 0))
            sep0 = tk.Frame(inner, height=2, bg="#aaaaaa")
            sep0.pack(fill=tk.X, padx=8, pady=(4, 0))

        for i, cat in enumerate(category_order):
            monthly = cat_data.get(cat, {})
            y_vals = [monthly.get(m, 0) for m in all_months]
            total_spend = sum(y_vals)
            if complete_month_count:
                complete_total = sum(
                    y_vals[idx] for idx, month in enumerate(all_months) if month in complete_month_set
                )
                avg_full_month = complete_total / complete_month_count
                avg_text = f" | avg full month ${avg_full_month:,.2f}"
            else:
                avg_text = " | avg full month n/a"

            fig = Figure(figsize=(12, CHART_H), dpi=96, facecolor="white")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#f7f9fc")

            color = colors[i % len(colors)]
            ax.fill_between(x, y_vals, alpha=0.25, color=color)
            ax.plot(x, y_vals, marker="o", markersize=4,
                    linewidth=1.8, color=color)

            ax.set_xticks(list(x))
            ax.set_xticklabels(all_months, fontsize=7, rotation=45, ha="right")
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda v, _: f"${v:,.0f}"))
            ax.tick_params(axis="y", labelsize=7)
            ax.set_title(
                f"{cat}   —   total ${total_spend:,.2f}{avg_text}",
                fontsize=9, fontweight="bold", loc="left", pad=4,
            )
            ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
            fig.tight_layout(pad=0.6)

            fc = FigureCanvasTkAgg(fig, master=inner)
            fc.draw()
            fc.get_tk_widget().pack(fill=tk.X, padx=8, pady=(6, 0))

            sep = tk.Frame(inner, height=1, bg="#dddddd")
            sep.pack(fill=tk.X, padx=8)

        self.status_var.set(
            f"Spend by Category trend  |  {len(category_order)} categories  |  "
            f"{len(all_months)} month(s)"
        )

    def _destroy_chart_frame(self):
        # Unbind mousewheel if we bound it
        if getattr(self, "_chart_mousewheel_bound", False):
            try:
                self.root.unbind_all("<MouseWheel>")
            except Exception:
                pass
            self._chart_mousewheel_bound = False
        frame = getattr(self, "_chart_frame", None)
        if frame and frame.winfo_exists():
            frame.destroy()
        self._chart_frame = None
    
    def show_top_merchants(self):
        date_values = self._get_date_filter_values()
        if date_values is None:
            return
        start_date, end_date = date_values

        self.tree.delete(*self.tree.get_children())
        self.item_detail_map = {}
        self.sort_states = {}
        self.column_heading_text = {}
        self.tree['columns'] = ('Merchant', 'Spend', 'Transactions', 'Avg Amount')
        for col in self.tree['columns']:
            self.tree.column(col, anchor=tk.W, width=250)
            self._set_heading(col, col, anchor=tk.W)
        
        query = """
            SELECT normalized_merchant,
                   ROUND(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 2) AS spend,
                   COUNT(*) AS txn_count,
                   ROUND(AVG(ABS(amount)), 2) AS avg_amt
            FROM transactions
            WHERE amount < 0
        """
        params = []
        if start_date:
            query += " AND txn_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND txn_date <= ?"
            params.append(end_date)
        query += " GROUP BY normalized_merchant ORDER BY spend DESC LIMIT 100"

        rows = self.cur.execute(query, params).fetchall()
        
        for idx, row in enumerate(rows):
            item_id = str(idx)
            self.tree.insert('', tk.END, iid=item_id, text='',
                           values=(row[0][:60], f"${row[1]:,.2f}", row[2], f"${row[3]:.2f}"))
            self._store_row_details(item_id, {
                "normalized_merchant": row[0],
                "spend": row[1],
                "transactions": row[2],
                "avg_amount": row[3],
            })
        
        self.status_var.set(f"Showing top {len(rows)} merchants by spend")
    
    def show_monthly_summary(self):
        date_values = self._get_date_filter_values()
        if date_values is None:
            return
        start_date, end_date = date_values
        excluded_categories = self._get_excluded_categories()

        self.tree.delete(*self.tree.get_children())
        self.item_detail_map = {}
        self.sort_states = {}
        self.column_heading_text = {}
        self.tree['columns'] = ('Month', 'Spend', 'Transactions', 'Avg Transaction')
        for col in self.tree['columns']:
            self.tree.column(col, anchor=tk.W, width=200)
            self._set_heading(col, col, anchor=tk.W)
        
        query = """
            SELECT SUBSTR(txn_date, 1, 7) AS month,
                   ROUND(SUM(CASE WHEN amount < 0 AND normalized_category != 'Transfers' THEN -amount ELSE 0 END), 2) AS spend,
                   SUM(CASE WHEN amount < 0 AND normalized_category != 'Transfers' THEN 1 ELSE 0 END) AS txn_count,
                   ROUND(
                       SUM(CASE WHEN amount < 0 AND normalized_category != 'Transfers' THEN -amount ELSE 0 END) /
                       NULLIF(SUM(CASE WHEN amount < 0 AND normalized_category != 'Transfers' THEN 1 ELSE 0 END), 0),
                       2
                   ) AS avg_amt
            FROM transactions
        """
        params = []
        where_clauses = []
        if start_date:
            where_clauses.append("txn_date >= ?")
            params.append(start_date)
        if end_date:
            where_clauses.append("txn_date <= ?")
            params.append(end_date)
        if excluded_categories:
            placeholders = ", ".join(["?"] * len(excluded_categories))
            where_clauses.append(f"normalized_category NOT IN ({placeholders})")
            params.extend(excluded_categories)
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " GROUP BY SUBSTR(txn_date, 1, 7) ORDER BY month DESC"

        rows = self.cur.execute(query, params).fetchall()
        
        for idx, row in enumerate(rows):
            item_id = str(idx)
            self.tree.insert('', tk.END, iid=item_id, text='',
                           values=(row[0], f"${row[1]:,.2f}", row[2], f"${row[3]:.2f}"))
            self._store_row_details(item_id, {
                "month": row[0],
                "spend": row[1],
                "transactions": row[2],
                "avg_transaction": row[3],
                "excluded_categories": ", ".join(excluded_categories) if excluded_categories else "",
            })
        
        self.status_var.set(f"Showing {len(rows)} months of data")

    def show_monthly_by_category(self):
        date_values = self._get_date_filter_values()
        if date_values is None:
            return
        start_date, end_date = date_values
        excluded_categories = self._get_excluded_categories()

        self.tree.delete(*self.tree.get_children())
        self.item_detail_map = {}
        self.sort_states = {}
        self.column_heading_text = {}
        self.tree['columns'] = ('Category', 'Spend', 'Transactions', 'Avg Transaction')
        self.tree.column('#0', anchor=tk.W, width=130, stretch=tk.NO)
        self.tree.heading('#0', text='Month', anchor=tk.W)

        self.tree.column('Category', anchor=tk.W, width=260)
        self.tree.column('Spend', anchor=tk.E, width=160)
        self.tree.column('Transactions', anchor=tk.E, width=140)
        self.tree.column('Avg Transaction', anchor=tk.E, width=160)
        self.tree.heading('Category', text='Category', anchor=tk.W)
        self.tree.heading('Spend', text='Spend', anchor=tk.E)
        self.tree.heading('Transactions', text='Transactions', anchor=tk.E)
        self.tree.heading('Avg Transaction', text='Avg Transaction', anchor=tk.E)

        query = """
            SELECT STRFTIME('%Y-%m', DATE(txn_date)) AS month,
                   normalized_category,
                   ROUND(SUM(-amount), 2) AS spend,
                   COUNT(*) AS txn_count,
                   ROUND(AVG(-amount), 2) AS avg_amt
            FROM transactions
        """
        params = []
        where_clauses = ["amount < 0"]
        if start_date:
            where_clauses.append("DATE(txn_date) >= DATE(?)")
            params.append(start_date)
        if end_date:
            where_clauses.append("DATE(txn_date) <= DATE(?)")
            params.append(end_date)
        if excluded_categories:
            placeholders = ", ".join(["?"] * len(excluded_categories))
            where_clauses.append(f"normalized_category NOT IN ({placeholders})")
            params.extend(excluded_categories)
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " GROUP BY STRFTIME('%Y-%m', DATE(txn_date)), normalized_category ORDER BY month DESC, spend DESC"

        rows = self.cur.execute(query, params).fetchall()
        grouped = {}
        month_order = []
        for row in rows:
            month = row[0] or "Unknown"
            if month not in grouped:
                grouped[month] = []
                month_order.append(month)
            grouped[month].append(row)

        row_id = 0
        for month in month_order:
            month_rows = grouped[month]
            month_spend = sum((r[2] or 0) for r in month_rows)
            month_txn = sum((r[3] or 0) for r in month_rows)
            month_avg = (month_spend / month_txn) if month_txn else 0

            parent_id = f"month-{month}"
            self.tree.insert(
                '',
                tk.END,
                iid=parent_id,
                text=month,
                open=True,
                values=("Total", f"${month_spend:,.2f}", month_txn, f"${month_avg:.2f}"),
            )
            self._store_row_details(parent_id, {
                "month": month,
                "total_spend": round(month_spend, 2),
                "total_transactions": month_txn,
                "avg_transaction": round(month_avg, 2),
                "excluded_categories": ", ".join(excluded_categories) if excluded_categories else "",
            })

            for row in month_rows:
                row_id += 1
                item_id = f"row-{row_id}"
                self.tree.insert(
                    parent_id,
                    tk.END,
                    iid=item_id,
                    text='',
                    values=(row[1], f"${(row[2] or 0):,.2f}", row[3] or 0, f"${(row[4] or 0):.2f}"),
                )
                self._store_row_details(item_id, {
                    "month": month,
                    "normalized_category": row[1],
                    "spend": row[2],
                    "transactions": row[3],
                    "avg_transaction": row[4],
                    "excluded_categories": ", ".join(excluded_categories) if excluded_categories else "",
                })

        self.status_var.set(f"Showing {len(month_order)} months and {len(rows)} category rows")
    
    def _ensure_tree_visible(self):
        """Tear down chart frame and restore the treeview when switching views."""
        self._destroy_chart_frame()
        if not self.tree.winfo_ismapped():
            self.tree.pack(fill=tk.BOTH, expand=True)

    def apply_filters(self):
        view = self.view_var.get()
        if view == "Transactions":
            self._ensure_tree_visible()
            self.show_transactions()
        elif view == "Recurring Candidates":
            self._ensure_tree_visible()
            self.show_recurring()
        elif view == "Spend by Category":
            self.show_spend_by_category()
        elif view == "Top Merchants":
            self._ensure_tree_visible()
            self.show_top_merchants()
        elif view == "Monthly Summary":
            self._ensure_tree_visible()
            self.show_monthly_summary()
        elif view == "Monthly by Category":
            self._ensure_tree_visible()
            self.show_monthly_by_category()
    
    def reset_filters(self):
        self.category_var.set("All")
        self.merchant_var.set("")
        self.start_date_var.set("2026-01-01")
        self.end_date_var.set(datetime.now().date().isoformat())
        self._clear_excluded_categories()
        self.view_var.set("Transactions")
        self.show_transactions()
    
    def change_view(self):
        view = self.view_var.get()
        if view == "Transactions":
            self._ensure_tree_visible()
            self.show_transactions()
        elif view == "Recurring Candidates":
            self._ensure_tree_visible()
            self.show_recurring()
        elif view == "Spend by Category":
            self.show_spend_by_category()
        elif view == "Top Merchants":
            self._ensure_tree_visible()
            self.show_top_merchants()
        elif view == "Monthly Summary":
            self._ensure_tree_visible()
            self.show_monthly_summary()
        elif view == "Monthly by Category":
            self._ensure_tree_visible()
            self.show_monthly_by_category()
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceExplorer(root)
    root.mainloop()
