"""Query Builder for SFI Reporter.

Provides a clause-based query builder UI and pure filtering logic
for ad-hoc queries against loaded action item data.
"""
import json
import logging
import re
import tkinter as tk
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import ttk
from typing import Optional

from sfi_reporter.cache import get_cache_dir
from sfi_reporter.data import is_invalid_eta

logger = logging.getLogger(__name__)

CLAUSE_CACHE_FILENAME = "query_clauses.json"

# Date field detection patterns
DATE_FIELD_SUFFIXES = ("Date", "Time", "Eta")
# Explicit date fields that don't match suffix patterns
DATE_FIELD_NAMES = frozenset({
    "dueDate", "DueDate", "EtaDate", "createdDate", "closedDate",
    "OriginalPublishTime", "S360_TwoWayEta",
})

# Operators by field type
STRING_OPERATORS = ["equals", "not equals", "contains", "not contains"]
DATE_OPERATORS = ["on or before", "on or after", "equals"]

# Regex for @Today expressions
TODAY_EXPR_RE = re.compile(r"^@Today\s*-\s*(\d+)$", re.IGNORECASE)

# Display names for fields (reuse from models where possible)
COLUMN_DISPLAY_NAMES = {
    'title': 'Title',
    'dueDate': 'Due Date',
    'SlaType': 'SLA Type',
    'ActionOwnerName': 'Action Owner',
    'ActionOwnerAlias': 'Action Owner Alias',
    'EtaDate': 'ETA Date',
    'EtaStatus': 'ETA Status',
    'S360_ServiceTreeServiceName': 'Service Name',
    'S360_AssignedToName': 'Assigned To',
    'S360_ProgramIds': 'Program',
    'ActionItemStatus': 'Status',
    'S360_ServiceTreeDivisionName': 'Division',
    'S360_ServiceTreeGroupName': 'Group',
    'S360_ServiceTreeOrganizationName': 'Organization',
    'Clouds': 'Clouds',
    'Environments': 'Environments',
    'createdDate': 'Created Date',
    'closedDate': 'Closed Date',
    'Remediation': 'Remediation',
    '_service_owner': 'Service Owner',
    'myExceptionStatus': 'My Exception Status',
}

# Curated filter fields (order matters for UI)
FILTER_FIELDS = [
    'S360_ServiceTreeServiceName',  # Service Name
    'S360_AssignedToName',          # Assigned To
    'S360_ProgramIds',              # Program
    'ActionOwnerName',              # Action Owner
    'dueDate',                      # Due Date
    'EtaDate',                      # ETA Date
    'myExceptionStatus',            # My Exception Status
]

# Additional field shown only for managers
MANAGER_ONLY_FIELDS = [
    '_service_owner',               # Service Owner (virtual field)
]


@dataclass
class QueryClause:
    """A single query clause."""
    connector: str  # "Where", "And", "Or"
    field: str
    operator: str
    value: str


def _get_today() -> datetime:
    """Get today's date. Separate function for test mocking."""
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def get_field_type(field_name: str) -> str:
    """Determine if a field is a date or string type.

    Args:
        field_name: The raw field name.

    Returns:
        "date" or "string".
    """
    if field_name in DATE_FIELD_NAMES:
        return "date"
    if any(field_name.endswith(suffix) for suffix in DATE_FIELD_SUFFIXES):
        return "date"
    return "string"


def resolve_date_expression(expr: str) -> Optional[datetime]:
    """Parse a date expression into a datetime.

    Supports:
    - "@Today - N" expressions (e.g., "@Today - 7")
    - ISO date strings (e.g., "2026-02-10")

    Args:
        expr: The date expression string.

    Returns:
        Parsed datetime or None if unparseable.
    """
    if not expr:
        return None

    expr = expr.strip()

    # Check for @Today expression
    match = TODAY_EXPR_RE.match(expr)
    if match:
        days = int(match.group(1))
        return _get_today() - timedelta(days=days)

    # Try ISO date
    try:
        return datetime.fromisoformat(expr.replace("Z", "+00:00").split("T")[0])
    except (ValueError, TypeError):
        return None


def _parse_item_date(value: Optional[str]) -> Optional[datetime]:
    """Parse a date value from an action item field.

    Args:
        value: Raw date string from S360 data.

    Returns:
        Parsed datetime (date-only) or None.
    """
    if not value or (isinstance(value, str) and not value.strip()):
        return None
    try:
        full = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        # Return date-only for comparison
        return full.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    except (ValueError, TypeError):
        return None


def _match_clause(item: dict, clause: QueryClause) -> bool:
    """Check if a single item matches a single clause.

    Args:
        item: Action item dict.
        clause: The clause to evaluate.

    Returns:
        True if item matches the clause.
    """
    # For program field, prefer the resolved display name if enriched,
    # otherwise fall back to the raw value so evaluate_clauses() works
    # without requiring _enrich_items() (e.g. in unit tests).
    if clause.field == 'S360_ProgramIds' and '_resolved_program' in item:
        raw_value = item['_resolved_program']
    else:
        raw_value = item.get(clause.field)
    field_type = get_field_type(clause.field)

    if field_type == "date":
        return _match_date_clause(raw_value, clause.operator, clause.value)
    else:
        return _match_string_clause(raw_value, clause.operator, clause.value)


def _match_string_clause(raw_value, operator: str, target: str) -> bool:
    """Evaluate a string clause against a value (which may be str or list)."""
    target_lower = target.lower()

    # Handle list values (e.g., S360_ProgramIds)
    if isinstance(raw_value, list):
        str_values = [str(v).lower() for v in raw_value]
        if operator == "equals":
            return any(v == target_lower for v in str_values)
        elif operator == "not equals":
            return not any(v == target_lower for v in str_values)
        elif operator == "contains":
            return any(target_lower in v for v in str_values)
        elif operator == "not contains":
            return not any(target_lower in v for v in str_values)
        return False

    # Scalar string
    item_str = str(raw_value).lower() if raw_value is not None else ""

    if operator == "equals":
        return item_str == target_lower
    elif operator == "not equals":
        return item_str != target_lower
    elif operator == "contains":
        return target_lower in item_str
    elif operator == "not contains":
        return target_lower not in item_str
    return False


def _match_date_clause(raw_value, operator: str, target_expr: str) -> bool:
    """Evaluate a date clause."""
    item_date = _parse_item_date(raw_value)
    if item_date is None:
        return False  # Can't compare None dates

    target_date = resolve_date_expression(target_expr)
    if target_date is None:
        return False

    # Strip timezone for comparison
    target_date = target_date.replace(tzinfo=None)

    if operator == "on or before":
        return item_date <= target_date
    elif operator == "on or after":
        return item_date >= target_date
    elif operator == "equals":
        return item_date == target_date
    return False


def evaluate_clauses(
    items: list[dict],
    clauses: list[QueryClause],
    include_ussec: bool = True,
) -> list[dict]:
    """Evaluate query clauses against action items.

    Clauses are evaluated left-to-right:
    - "And" narrows the result (item must match current AND previous)
    - "Or" widens (item can match current OR previous)

    Args:
        items: List of action item dicts.
        clauses: List of QueryClause objects.
        include_ussec: Whether to include USSec Shadow Action Items.

    Returns:
        Filtered list of items.
    """
    # Pre-filter USSec if needed
    if not include_ussec:
        items = [
            item for item in items
            if "ussec shadow action item" not in (item.get("title") or "").lower()
        ]

    # Filter out incomplete clauses
    valid_clauses = [
        c for c in clauses
        if c.field and c.operator and c.value
    ]

    if not valid_clauses:
        return list(items)

    result = []
    for item in items:
        matches = False
        for i, clause in enumerate(valid_clauses):
            clause_match = _match_clause(item, clause)
            if i == 0:
                # First clause — "Where"
                matches = clause_match
            elif clause.connector == "Or":
                matches = matches or clause_match
            else:
                # "And" (default)
                matches = matches and clause_match
        if matches:
            result.append(item)

    return result


def aggregate_results_by_program(
    items: list[dict],
    program_names: dict[str, str],
) -> dict[str, dict]:
    """Aggregate filtered items by program.

    An item with multiple programs appears in each program's count.

    Args:
        items: Filtered action items.
        program_names: Dict mapping program ID to display name.

    Returns:
        Dict mapping program name to {count, sla, invalid_eta}.
    """
    program_stats: dict[str, dict] = {}

    for item in items:
        program_ids = item.get("S360_ProgramIds", [])
        if not isinstance(program_ids, list):
            program_ids = [program_ids] if program_ids else []

        if not program_ids:
            program_ids = ["(No Program)"]

        is_out_of_sla = item.get("SlaType") == "OutOfSla"
        has_invalid_eta = is_invalid_eta(item.get("EtaDate"))

        for pid in program_ids:
            name = program_names.get(pid, pid)
            if name not in program_stats:
                program_stats[name] = {"count": 0, "sla": 0, "invalid_eta": 0}
            program_stats[name]["count"] += 1
            if is_out_of_sla:
                program_stats[name]["sla"] += 1
            if has_invalid_eta:
                program_stats[name]["invalid_eta"] += 1

    return program_stats


# --- Clause cache ---

def save_clause_cache(
    clauses: list[QueryClause],
    include_ussec: bool = False,
    cache_dir: Optional[Path] = None,
) -> None:
    """Save query clauses to cache file.

    Args:
        clauses: List of clauses to save.
        include_ussec: USSec checkbox state.
        cache_dir: Optional cache directory (default: get_cache_dir()).
    """
    if cache_dir is None:
        cache_dir = get_cache_dir()
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "clauses": [asdict(c) for c in clauses],
        "include_ussec": include_ussec,
    }
    path = cache_dir / CLAUSE_CACHE_FILENAME
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.debug("Saved %d clauses to cache", len(clauses))
    except IOError as e:
        logger.error("Error saving clause cache: %s", e)


def load_clause_cache(
    cache_dir: Optional[Path] = None,
) -> tuple[list[QueryClause], bool]:
    """Load query clauses from cache file.

    Args:
        cache_dir: Optional cache directory (default: get_cache_dir()).

    Returns:
        Tuple of (clauses, include_ussec). Empty defaults if file missing/corrupt.
    """
    if cache_dir is None:
        cache_dir = get_cache_dir()
    cache_dir = Path(cache_dir)
    path = cache_dir / CLAUSE_CACHE_FILENAME

    if not path.exists():
        return [], False

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        clauses = [
            QueryClause(**c) for c in data.get("clauses", [])
        ]
        include_ussec = data.get("include_ussec", False)
        logger.debug("Loaded %d clauses from cache", len(clauses))
        return clauses, include_ussec
    except (json.JSONDecodeError, IOError, TypeError, KeyError) as e:
        logger.warning("Could not load clause cache: %s", e)
        return [], False


def clear_clause_cache(cache_dir: Optional[Path] = None) -> None:
    """Delete the clause cache file.

    Args:
        cache_dir: Optional cache directory (default: get_cache_dir()).
    """
    if cache_dir is None:
        cache_dir = get_cache_dir()
    cache_dir = Path(cache_dir)
    path = cache_dir / CLAUSE_CACHE_FILENAME
    if path.exists():
        path.unlink()
        logger.debug("Cleared clause cache")


# --- UI ---

class ClauseRow:
    """A single clause row in the query builder UI."""

    def __init__(
        self,
        parent_frame: ttk.Frame,
        index: int,
        fields: list[str],
        field_display: dict[str, str],
        data_values: dict[str, list[str]],
        on_add: callable,
        on_remove: callable,
        on_field_change: Optional[callable] = None,
    ):
        self.frame = ttk.Frame(parent_frame)
        self.frame.pack(fill=tk.X, pady=2)
        self._fields = fields
        self._field_display = field_display
        self._data_values = data_values
        self._display_to_field = {v: k for k, v in field_display.items()}

        # And/Or
        if index == 0:
            self.connector_label = ttk.Label(self.frame, text="Where", width=6)
            self.connector_label.pack(side=tk.LEFT, padx=(0, 5))
            self.connector_var = tk.StringVar(value="Where")
        else:
            self.connector_var = tk.StringVar(value="And")
            self.connector_combo = ttk.Combobox(
                self.frame,
                textvariable=self.connector_var,
                values=["And", "Or"],
                width=5,
                state="readonly",
            )
            self.connector_combo.pack(side=tk.LEFT, padx=(0, 5))

        # Field
        display_names = [field_display.get(f, f) for f in fields]
        self.field_var = tk.StringVar()
        self.field_combo = ttk.Combobox(
            self.frame,
            textvariable=self.field_var,
            values=display_names,
            width=25,
        )
        self.field_combo.pack(side=tk.LEFT, padx=2)
        self.field_combo.bind("<<ComboboxSelected>>", lambda e: self._on_field_selected())

        # Operator
        self.operator_var = tk.StringVar()
        self.operator_combo = ttk.Combobox(
            self.frame,
            textvariable=self.operator_var,
            values=STRING_OPERATORS,
            width=14,
            state="readonly",
        )
        self.operator_combo.pack(side=tk.LEFT, padx=2)

        # Value
        self.value_var = tk.StringVar()
        self.value_combo = ttk.Combobox(
            self.frame,
            textvariable=self.value_var,
            values=[],
            width=30,
        )
        self.value_combo.pack(side=tk.LEFT, padx=2)

        # Add/Remove buttons
        ttk.Button(self.frame, text="➕", width=3, command=on_add).pack(side=tk.LEFT, padx=1)
        self.remove_btn = ttk.Button(self.frame, text="✕", width=3, command=on_remove)
        self.remove_btn.pack(side=tk.LEFT, padx=1)

    def _on_field_selected(self):
        """Update operator and value options when field changes."""
        display_name = self.field_var.get()
        field_name = self._display_to_field.get(display_name, display_name)

        # Update operators based on field type
        ftype = get_field_type(field_name)
        operators = DATE_OPERATORS if ftype == "date" else STRING_OPERATORS
        self.operator_combo.configure(values=operators)
        if self.operator_var.get() not in operators:
            self.operator_var.set(operators[0])

        # Update value suggestions
        values = self._data_values.get(field_name, [])
        self.value_combo.configure(values=values[:500])

    def get_clause(self) -> QueryClause:
        """Get the clause data from this row."""
        display_name = self.field_var.get()
        field_name = self._display_to_field.get(display_name, display_name)
        return QueryClause(
            connector=self.connector_var.get(),
            field=field_name,
            operator=self.operator_var.get(),
            value=self.value_var.get(),
        )

    def set_clause(self, clause: QueryClause):
        """Restore clause data into the row widgets."""
        display_name = self._field_display.get(clause.field, clause.field)
        self.field_var.set(display_name)
        self._on_field_selected()
        self.operator_var.set(clause.operator)
        self.value_var.set(clause.value)
        if hasattr(self, "connector_combo"):
            self.connector_var.set(clause.connector)

    def destroy(self):
        """Remove the row frame."""
        self.frame.destroy()


class QueryBuilder(tk.Toplevel):
    """Query builder window with clause-based filtering."""

    def __init__(
        self,
        parent,
        action_items: list[dict],
        program_names: dict[str, str],
        service_names: dict[str, str],
        is_manager: bool = False,
        service_owners: dict[str, list[str]] = None,
        on_apply: Optional[callable] = None,
    ):
        super().__init__(parent)
        self.title("🔍 Filter")
        self.geometry("1050x650")
        self.transient(parent)

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 1050) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 650) // 2
        self.geometry(f"+{x}+{y}")

        self._items = action_items
        self._program_names = program_names
        self._service_names = service_names
        self._is_manager = is_manager
        self._service_owners = service_owners or {}
        self._on_apply = on_apply
        self._clause_rows: list[ClauseRow] = []
        self._filtered_items: list[dict] = []

        # Enrich items with resolved program names and service owner (virtual fields)
        self._enrich_items()

        # Build field list and value lookups
        self._fields, self._field_display, self._data_values = self._build_field_metadata()

        self._build_ui()
        self._load_cached()

        self.bind("<Escape>", lambda e: self.destroy())
        self.focus_set()

    def _enrich_items(self):
        """Add virtual fields to items for filtering.

        - _resolved_program: first program ID resolved to display name
        - _service_owner: service owner name (from service_owners lookup)
        """
        for item in self._items:
            # Resolve program name
            pids = item.get('S360_ProgramIds', [])
            if isinstance(pids, list) and pids:
                item['_resolved_program'] = self._program_names.get(pids[0], pids[0])
            else:
                item['_resolved_program'] = ''

            # Resolve service owner
            if self._service_owners:
                svc_name = item.get('S360_ServiceTreeServiceName', '')
                owners = self._service_owners.get(svc_name, [])
                item['_service_owner'] = owners[0] if owners else ''

    def _build_field_metadata(self):
        """Build curated field list, display name map, and distinct value sets."""
        fields = list(FILTER_FIELDS)
        if self._is_manager:
            fields.extend(MANAGER_ONLY_FIELDS)

        # Display names
        field_display = {}
        for f in fields:
            field_display[f] = COLUMN_DISPLAY_NAMES.get(f, f)

        # Distinct values per field (for combobox suggestions)
        data_values: dict[str, list[str]] = {}
        for f in fields:
            values: set[str] = set()
            for item in self._items:
                # For S360_ProgramIds, use the resolved program name
                if f == 'S360_ProgramIds':
                    v = item.get('_resolved_program', '')
                else:
                    v = item.get(f)
                if v is None:
                    continue
                if isinstance(v, list):
                    for elem in v:
                        s = str(elem).strip()
                        if s:
                            values.add(s)
                else:
                    s = str(v).strip()
                    if s:
                        values.add(s)
            data_values[f] = sorted(values)[:500]

        return fields, field_display, data_values

    def _build_ui(self):
        """Build the query builder UI."""
        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # --- Top: Clause builder ---
        clause_header = ttk.Frame(main)
        clause_header.pack(fill=tk.X)
        ttk.Label(clause_header, text="Query Clauses", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)

        # USSec checkbox
        self._ussec_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            clause_header,
            text="Include USSec Shadow items",
            variable=self._ussec_var,
        ).pack(side=tk.RIGHT)

        # Scrollable clause area
        clause_canvas_frame = ttk.Frame(main)
        clause_canvas_frame.pack(fill=tk.X, pady=5)

        self._clause_canvas = tk.Canvas(clause_canvas_frame, height=200, highlightthickness=0)
        clause_scroll = ttk.Scrollbar(clause_canvas_frame, orient=tk.VERTICAL, command=self._clause_canvas.yview)
        self._clause_inner = ttk.Frame(self._clause_canvas)

        self._clause_inner.bind(
            "<Configure>",
            lambda e: self._clause_canvas.configure(scrollregion=self._clause_canvas.bbox("all")),
        )
        self._clause_canvas.create_window((0, 0), window=self._clause_inner, anchor="nw")
        self._clause_canvas.configure(yscrollcommand=clause_scroll.set)

        self._clause_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        clause_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Add clause link
        add_link = ttk.Label(main, text="➕ Add new clause", foreground="blue", cursor="hand2")
        add_link.pack(anchor=tk.W, pady=2)
        add_link.bind("<Button-1>", lambda e: self._add_clause_row())

        # Action buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="▶ Run Query", command=self._run_query).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✅ Apply", command=self._apply_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Clear All", command=self._clear_all).pack(side=tk.LEFT, padx=5)

        self._result_count_var = tk.StringVar()
        ttk.Label(btn_frame, textvariable=self._result_count_var, foreground="gray").pack(side=tk.RIGHT)

        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # --- Bottom: Results ---
        ttk.Label(main, text="Results by Program", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)

        result_frame = ttk.Frame(main)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Import SortableTreeview here to avoid circular import at module level
        from sfi_reporter.dialogs import SortableTreeview

        self._result_tree = SortableTreeview(
            result_frame,
            columns=("program", "count", "sla", "invalid_eta"),
            show="headings",
        )
        self._result_tree.heading("program", text="Program")
        self._result_tree.heading("count", text="Total")
        self._result_tree.heading("sla", text="Out of SLA")
        self._result_tree.heading("invalid_eta", text="Invalid ETA")
        self._result_tree.column("program", width=350, anchor=tk.W)
        self._result_tree.column("count", width=80, anchor=tk.CENTER)
        self._result_tree.column("sla", width=100, anchor=tk.CENTER)
        self._result_tree.column("invalid_eta", width=100, anchor=tk.CENTER)

        result_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self._result_tree.yview)
        self._result_tree.configure(yscrollcommand=result_scroll.set)
        self._result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Double-click drill-down
        self._result_tree.bind("<Double-1>", self._on_result_double_click)
        self._result_program_items: dict[str, list[dict]] = {}

        # Add first empty clause row
        self._add_clause_row()

    def _add_clause_row(self, after_index: Optional[int] = None):
        """Add a new clause row."""
        index = len(self._clause_rows)
        row = ClauseRow(
            parent_frame=self._clause_inner,
            index=index,
            fields=self._fields,
            field_display=self._field_display,
            data_values=self._data_values,
            on_add=lambda: self._add_clause_row(),
            on_remove=lambda r=index: self._remove_clause_row(r),
        )
        self._clause_rows.append(row)
        self._update_remove_buttons()

    def _remove_clause_row(self, index: int):
        """Remove a clause row."""
        if len(self._clause_rows) <= 1:
            return
        if 0 <= index < len(self._clause_rows):
            self._clause_rows[index].destroy()
            self._clause_rows.pop(index)
            # Re-index remove callbacks
            for i, row in enumerate(self._clause_rows):
                row.remove_btn.configure(command=lambda r=i: self._remove_clause_row(r))
            self._update_remove_buttons()

    def _update_remove_buttons(self):
        """Disable remove button if only 1 clause."""
        for row in self._clause_rows:
            state = "disabled" if len(self._clause_rows) <= 1 else "normal"
            row.remove_btn.configure(state=state)

    def _get_clauses(self) -> list[QueryClause]:
        """Get all clauses from the UI."""
        return [row.get_clause() for row in self._clause_rows]

    def _run_query(self):
        """Execute the query and display results."""
        import time
        start = time.perf_counter()

        clauses = self._get_clauses()
        include_ussec = self._ussec_var.get()

        # Evaluate
        self._filtered_items = evaluate_clauses(self._items, clauses, include_ussec)

        # Aggregate by program
        program_stats = aggregate_results_by_program(self._filtered_items, self._program_names)

        # Build program -> items mapping for drill-down
        self._result_program_items.clear()
        for item in self._filtered_items:
            pids = item.get("S360_ProgramIds", [])
            if not isinstance(pids, list):
                pids = [pids] if pids else []
            if not pids:
                pids = ["(No Program)"]
            for pid in pids:
                name = self._program_names.get(pid, pid)
                if name not in self._result_program_items:
                    self._result_program_items[name] = []
                self._result_program_items[name].append(item)

        # Update results tree
        for child in self._result_tree.get_children():
            self._result_tree.delete(child)

        for program_name in sorted(program_stats.keys()):
            stats = program_stats[program_name]
            self._result_tree.insert("", tk.END, values=(
                program_name,
                stats["count"],
                stats["sla"],
                stats["invalid_eta"],
            ))

        elapsed = time.perf_counter() - start
        total = sum(s["count"] for s in program_stats.values())
        total_sla = sum(s["sla"] for s in program_stats.values())
        self._result_count_var.set(
            f"{len(self._filtered_items)} items across {len(program_stats)} programs  "
            f"(Total: {total} | Out of SLA: {total_sla})  [{elapsed:.0f}ms]"
        )

        # Save clauses to cache
        save_clause_cache(clauses, include_ussec)

        logger.debug(
            "Query executed: %d clauses, %d results in %.1fms",
            len(clauses), len(self._filtered_items), elapsed * 1000,
        )

    def _clear_all(self):
        """Clear all clauses and results."""
        # Remove all clause rows
        for row in self._clause_rows:
            row.destroy()
        self._clause_rows.clear()

        # Add one empty row
        self._add_clause_row()

        # Clear results
        for child in self._result_tree.get_children():
            self._result_tree.delete(child)
        self._result_count_var.set("")
        self._result_program_items.clear()

        # Reset USSec checkbox
        self._ussec_var.set(False)

        # Delete cache
        clear_clause_cache()

    def _load_cached(self):
        """Restore cached clauses on window open."""
        clauses, include_ussec = load_clause_cache()
        if clauses:
            # Remove default empty row
            for row in self._clause_rows:
                row.destroy()
            self._clause_rows.clear()

            for i, clause in enumerate(clauses):
                row = ClauseRow(
                    parent_frame=self._clause_inner,
                    index=i,
                    fields=self._fields,
                    field_display=self._field_display,
                    data_values=self._data_values,
                    on_add=lambda: self._add_clause_row(),
                    on_remove=lambda r=i: self._remove_clause_row(r),
                )
                row.set_clause(clause)
                self._clause_rows.append(row)

            self._update_remove_buttons()
            self._ussec_var.set(include_ussec)

    def _apply_filter(self):
        """Apply the current filter to the whole app and close."""
        clauses = self._get_clauses()
        include_ussec = self._ussec_var.get()

        # Evaluate the filter
        filtered = evaluate_clauses(self._items, clauses, include_ussec)

        # Save to cache
        save_clause_cache(clauses, include_ussec)

        # Call back to the main app with filtered items
        if self._on_apply:
            self._on_apply(filtered, clauses)

        self.destroy()

    def _on_result_double_click(self, event):
        """Drill into filtered items for a program."""
        selection = self._result_tree.selection()
        if not selection:
            return

        values = self._result_tree.item(selection[0], "values")
        if not values:
            return

        program_name = values[0]
        items = self._result_program_items.get(program_name, [])
        if not items:
            return

        from sfi_reporter.dialogs import DetailModal
        DetailModal(self, f"Query Results: {program_name}", items, self._service_names)
