"""Main SFIReporterApp window and entry point."""
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from sfi_reporter.cache import (
    clear_cache,
    get_cache_age_minutes,
    is_cache_valid,
    read_cache,
    write_cache,
)
from sfi_reporter.data import get_current_user_alias
from sfi_reporter.logging_config import setup_logging, get_log_path, patch_subprocess_windows
from sfi_reporter.models import OrgAncestry
from sfi_reporter.services import (
    _deserialize_org_data_from_cache,
    _load_setting,
    _save_setting,
    _serialize_org_data_for_cache,
    aggregate_by_owner,
    collect_services_for_owner,
    do_refresh,
    filter_items_by_program,
    filter_items_by_service,
)
from sfi_reporter.dialogs import (
    BulkEtaProgressDialog,
    ConfigureLLMDialog,
    DetailModal,
    EtaModeDialog,
    ManualEtaReviewDialog,
    SortableTreeview,
    _launch_llm_analysis,
)

logger = logging.getLogger(__name__)


class SFIReporterApp:
    """Main application class."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SFI Reporter")
        self.root.geometry("1200x750")

        self.current_data: dict = {}
        self._unfiltered_data: dict = {}
        self.detected_alias = get_current_user_alias() or ""

        self._service_id_map: dict = {}
        self._service_name_map: dict = {}
        self._program_id_map: dict = {}
        self._kpi_id_map: dict = {}

        self._last_filter_clauses: list = []
        self._last_filter_ussec: bool = False

        self._build_ui()
        self._load_cached_data()

    def _build_ui(self):
        """Build the UI components."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_label = ttk.Label(main_frame, text="\U0001f4ca SFI Reporter", font=("Segoe UI", 20, "bold"))
        header_label.pack(anchor=tk.W)

        subtitle_label = ttk.Label(main_frame, text="View SFI/QEI action items for your services", foreground="gray")
        subtitle_label.pack(anchor=tk.W, pady=(0, 10))

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)

        ttk.Label(controls_frame, text="User Alias:").pack(side=tk.LEFT)

        self.alias_var = tk.StringVar(value=self.detected_alias)
        self.alias_entry = ttk.Entry(controls_frame, textvariable=self.alias_var, width=30)
        self.alias_entry.pack(side=tk.LEFT, padx=(5, 10))

        self.alias_entry.bind('<Return>', lambda e: self._load_cached_data())
        self.alias_entry.bind('<FocusOut>', lambda e: self._load_cached_data())

        self.refresh_btn = ttk.Button(controls_frame, text="\U0001f504 Refresh Data", command=self._on_refresh)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(controls_frame, text="\U0001f5d1\ufe0f Clear Cache", command=self._on_clear_cache)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.retry_btn = tk.Button(controls_frame, text="\U0001f501 Retry Failed KPIs",
                                   command=self._on_retry_failed,
                                   bg="#d9534f", fg="white", activebackground="#c9302c",
                                   activeforeground="white", font=("Segoe UI", 9, "bold"),
                                   relief=tk.RAISED, padx=8, pady=2)

        self.query_btn = ttk.Button(controls_frame, text="\U0001f50d Filter", command=self._on_query, state="disabled")
        self.query_btn.pack(side=tk.LEFT, padx=5)

        self.eta_btn = ttk.Button(controls_frame, text="\U0001f4cb Update ETAs",
                                  command=self._on_update_etas, state="disabled")
        self.eta_btn.pack(side=tk.LEFT, padx=5)

        self.llm_config_btn = ttk.Button(
            controls_frame, text="\u2699\ufe0f Configure LLM",
            command=lambda: ConfigureLLMDialog(self.root),
        )
        self.llm_config_btn.pack(side=tk.LEFT, padx=5)

        self._reapply_filter_var = tk.BooleanVar(
            value=_load_setting('reapply_filter_after_refresh', False)
        )
        self._reapply_filter_var.trace_add(
            'write',
            lambda *_: _save_setting('reapply_filter_after_refresh',
                                     self._reapply_filter_var.get()),
        )
        self._reapply_cb = ttk.Checkbutton(
            controls_frame,
            text="Re-apply filter after refresh",
            variable=self._reapply_filter_var,
        )
        self._reapply_cb.pack(side=tk.LEFT, padx=(10, 0))

        self._failed_kpis: list[dict] = []
        self._audience_ids: list[str] = []
        self._kpi_names: dict = {}

        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)

        self.cache_age_var = tk.StringVar()
        self.cache_age_label = ttk.Label(status_frame, textvariable=self.cache_age_var, foreground="green")
        self.cache_age_label.pack(side=tk.LEFT)

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Top section: Services (left) and Program Summary (right)
        top_section = ttk.Frame(main_frame)
        top_section.pack(fill=tk.X, pady=5)

        # Services section
        services_container = ttk.Frame(top_section)
        services_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(services_container, text="\U0001f527 Services", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)

        services_frame = ttk.Frame(services_container)
        services_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.services_tree = SortableTreeview(
            services_frame, columns=("name", "count", "sla", "invalid_eta"), show="tree headings", height=6)
        self.services_tree.heading("#0", text="")
        self.services_tree.heading("name", text="Name")
        self.services_tree.heading("count", text="Total")
        self.services_tree.heading("sla", text="Out of SLA")
        self.services_tree.heading("invalid_eta", text="Invalid ETA")
        self.services_tree.column("#0", width=40, stretch=False)
        self.services_tree.column("name", width=180, anchor=tk.W)
        self.services_tree.column("count", width=60, anchor=tk.CENTER)
        self.services_tree.column("sla", width=80, anchor=tk.CENTER)
        self.services_tree.column("invalid_eta", width=80, anchor=tk.CENTER)

        self._group_path_map = {}

        services_scroll = ttk.Scrollbar(services_frame, orient=tk.VERTICAL, command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=services_scroll.set)

        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        services_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.services_tree.bind('<Double-1>', self._on_service_double_click)

        # Program Summary section
        program_container = ttk.Frame(top_section)
        program_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(program_container, text="\U0001f4c8 Program Summary", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)

        program_frame = ttk.Frame(program_container)
        program_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.program_tree = SortableTreeview(
            program_frame, columns=("program", "count", "sla", "invalid_eta"), show="headings", height=6)
        self.program_tree.heading("program", text="Program")
        self.program_tree.heading("count", text="Total")
        self.program_tree.heading("sla", text="Out of SLA")
        self.program_tree.heading("invalid_eta", text="Invalid ETA")
        self.program_tree.column("program", width=230, anchor=tk.W)
        self.program_tree.column("count", width=60, anchor=tk.CENTER)
        self.program_tree.column("sla", width=70, anchor=tk.CENTER)
        self.program_tree.column("invalid_eta", width=70, anchor=tk.CENTER)

        program_scroll = ttk.Scrollbar(program_frame, orient=tk.VERTICAL, command=self.program_tree.yview)
        self.program_tree.configure(yscrollcommand=program_scroll.set)

        self.program_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        program_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.program_tree.bind('<Double-1>', self._on_program_double_click)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Action Items section
        ttk.Label(main_frame, text="\U0001f4cb Action Items", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(5, 0))

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.action_tree = SortableTreeview(
            action_frame, columns=("name", "count", "sla", "invalid_eta"), show="headings")
        self.action_tree.heading("name", text="Action Item (KPI)")
        self.action_tree.heading("count", text="Total")
        self.action_tree.heading("sla", text="Out of SLA")
        self.action_tree.heading("invalid_eta", text="Invalid ETA")
        self.action_tree.column("name", width=450, anchor=tk.W)
        self.action_tree.column("count", width=80, anchor=tk.CENTER)
        self.action_tree.column("sla", width=80, anchor=tk.CENTER)
        self.action_tree.column("invalid_eta", width=80, anchor=tk.CENTER)

        action_scroll = ttk.Scrollbar(action_frame, orient=tk.VERTICAL, command=self.action_tree.yview)
        self.action_tree.configure(yscrollcommand=action_scroll.set)

        self.action_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        action_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.action_tree.bind('<Double-1>', self._on_action_double_click)
        self.action_tree.bind('<Button-3>', self._on_kpi_right_click)

    def _load_cached_data(self, user_alias: str = None):
        alias = user_alias or self.alias_var.get().strip()
        if alias:
            cached = read_cache(alias)
            if cached and is_cache_valid(cached):
                cached = _deserialize_org_data_from_cache(cached)
                self._update_tables(cached)
                age = get_cache_age_minutes(cached)
                if age is not None:
                    self.cache_age_var.set(f"Cache: {age} minutes old")
                    color = "orange" if age > 30 else "green"
                    self.cache_age_label.configure(foreground=color)
                return True
        return False

    def _on_alias_change(self, *args):
        alias = self.alias_var.get().strip()
        if alias:
            self._load_cached_data(alias)

    def _update_tables(self, data: dict, *, is_filtered: bool = False):
        """Update tables with data."""
        self.current_data = data
        if not is_filtered:
            self._unfiltered_data = data

        if data.get('detailed_items'):
            self.query_btn.configure(state="normal")
            self.eta_btn.configure(state="normal")

        for item in self.services_tree.get_children():
            self.services_tree.delete(item)
        for item in self.action_tree.get_children():
            self.action_tree.delete(item)
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)

        self._service_id_map.clear()
        self._service_name_map.clear()
        self._program_id_map.clear()
        self._kpi_id_map.clear()
        self._group_path_map.clear()

        service_stats = data.get('service_stats', {})
        program_stats = data.get('program_stats', {})
        kpi_stats = data.get('kpi_stats', {})
        owner_stats = data.get('owner_stats', {})
        is_manager = data.get('is_manager', False)
        service_owners = data.get('service_owners', {})

        # Update program summary table
        for program_name, stats in sorted(program_stats.items(), key=lambda x: x[1].get('count', 0), reverse=True):
            iid = self.program_tree.insert("", tk.END, values=(
                program_name, stats.get('count', 0), stats.get('sla', 0), stats.get('invalid_eta', 0),
            ))
            program_id = stats.get('id', program_name)
            self._program_id_map[iid] = program_id

        # Update services table
        services = data.get('services', [])

        if is_manager and owner_stats and service_stats:
            org_mapping = data.get('org_mapping', {})

            svc_path_map: dict[str, tuple[str, ...]] = {}
            for svc_id, stats in service_stats.items():
                svc_name = stats.get('name', svc_id)
                owners = service_owners.get(svc_name, None)
                path = ('Unknown Owner',)
                if owners is None:
                    path = ('Unknown Owner',)
                elif len(owners) == 0:
                    path = ('No Owner',)
                elif org_mapping:
                    for owner in owners:
                        mapped = org_mapping.get(owner)
                        if isinstance(mapped, OrgAncestry) and mapped.path and mapped.path[0] != 'Unknown Owner':
                            path = mapped.path
                            break
                else:
                    path = (owners[0],)
                svc_path_map[svc_id] = path

            root_groups: dict[str, dict] = {}

            for svc_id, path in svc_path_map.items():
                stats = service_stats[svc_id]
                svc_name = stats.get('name', svc_id)

                if len(path) <= 1:
                    group_name = path[0]
                    if group_name not in root_groups:
                        root_groups[group_name] = {'children': {}, 'services': []}
                    root_groups[group_name]['services'].append((svc_id, svc_name, stats))
                else:
                    group_name = path[1]
                    if group_name not in root_groups:
                        root_groups[group_name] = {'children': {}, 'services': []}

                    current = root_groups[group_name]
                    for depth in range(2, len(path)):
                        child_name = path[depth]
                        if child_name not in current['children']:
                            current['children'][child_name] = {'children': {}, 'services': []}
                        current = current['children'][child_name]

                    current['services'].append((svc_id, svc_name, stats))

            def _compute_group_stats(group: dict) -> dict:
                total = {'count': 0, 'sla': 0, 'invalid_eta': 0}
                for _, _, s in group['services']:
                    total['count'] += s.get('count', 0)
                    total['sla'] += s.get('sla', 0)
                    total['invalid_eta'] += s.get('invalid_eta', 0)
                for child in group['children'].values():
                    child_stats = _compute_group_stats(child)
                    total['count'] += child_stats['count']
                    total['sla'] += child_stats['sla']
                    total['invalid_eta'] += child_stats['invalid_eta']
                group['_stats'] = total
                return total

            for g in root_groups.values():
                _compute_group_stats(g)

            root_name = None
            for mapped in org_mapping.values():
                if isinstance(mapped, OrgAncestry) and mapped.path and mapped.path[0] != 'Unknown Owner':
                    root_name = mapped.path[0]
                    break

            def _insert_group(parent_iid, name, group, depth, full_path):
                grp_stats = group.get('_stats', {'count': 0, 'sla': 0, 'invalid_eta': 0})
                iid = self.services_tree.insert(parent_iid, tk.END, values=(
                    f"\U0001f464 {name}", grp_stats['count'], grp_stats['sla'], grp_stats['invalid_eta'],
                ), open=(depth == 0))
                self._group_path_map[iid] = full_path

                for child_name in sorted(
                    group['children'],
                    key=lambda n: group['children'][n].get('_stats', {}).get('count', 0),
                    reverse=True
                ):
                    child_full_path = full_path + (child_name,)
                    _insert_group(iid, child_name, group['children'][child_name], depth + 1, child_full_path)

                for svc_id, svc_name, s in sorted(group['services'], key=lambda x: x[2].get('count', 0), reverse=True):
                    child_iid = self.services_tree.insert(iid, tk.END, values=(
                        svc_name, s.get('count', 0), s.get('sla', 0), s.get('invalid_eta', 0),
                    ))
                    self._service_id_map[child_iid] = svc_id
                    self._service_name_map[svc_id] = svc_name

            # Build a wrapper root node so the logged-in manager appears as
            # a single collapsible row containing all direct-report groups.
            if root_name:
                # Compute aggregate stats across all groups (excluding Unknown/No Owner)
                root_stats = {'count': 0, 'sla': 0, 'invalid_eta': 0}
                for n, g in root_groups.items():
                    gs = g.get('_stats', {'count': 0, 'sla': 0, 'invalid_eta': 0})
                    root_stats['count'] += gs['count']
                    root_stats['sla'] += gs['sla']
                    root_stats['invalid_eta'] += gs['invalid_eta']

                root_iid = self.services_tree.insert("", tk.END, values=(
                    f"\U0001f464 {root_name}", root_stats['count'], root_stats['sla'], root_stats['invalid_eta'],
                ), open=True)
                self._group_path_map[root_iid] = (root_name,)
            else:
                root_iid = ""

            for name in sorted(root_groups, key=lambda n: root_groups[n].get('_stats', {}).get('count', 0), reverse=True):
                if root_name and name == root_name:
                    # Fold root-name bucket directly into the root node
                    # instead of creating a duplicate child group.
                    group = root_groups[name]
                    for child_name in sorted(
                        group['children'],
                        key=lambda n: group['children'][n].get('_stats', {}).get('count', 0),
                        reverse=True
                    ):
                        child_full_path = (root_name, child_name)
                        _insert_group(root_iid, child_name, group['children'][child_name], 0, child_full_path)
                    for svc_id, svc_name, s in sorted(group['services'], key=lambda x: x[2].get('count', 0), reverse=True):
                        child_iid = self.services_tree.insert(root_iid, tk.END, values=(
                            svc_name, s.get('count', 0), s.get('sla', 0), s.get('invalid_eta', 0),
                        ))
                        self._service_id_map[child_iid] = svc_id
                        self._service_name_map[svc_id] = svc_name
                    continue
                if root_name and name != 'Unknown Owner' and name != 'No Owner':
                    full_path = (root_name, name)
                else:
                    full_path = (name,)
                _insert_group(root_iid, name, root_groups[name], 0, full_path)
        elif services:
            for s in services:
                svc_id = s.get('Id', '')
                stats = service_stats.get(svc_id, {})
                iid = self.services_tree.insert("", tk.END, values=(
                    s.get('Name', 'Unknown'), stats.get('count', 0), stats.get('sla', 0), stats.get('invalid_eta', 0),
                ))
                self._service_id_map[iid] = svc_id
                self._service_name_map[svc_id] = s.get('Name', 'Unknown')
        elif service_stats:
            for svc_id, stats in sorted(service_stats.items(), key=lambda x: x[1].get('count', 0), reverse=True):
                iid = self.services_tree.insert("", tk.END, values=(
                    stats.get('name', svc_id), stats.get('count', 0), stats.get('sla', 0), stats.get('invalid_eta', 0),
                ))
                self._service_id_map[iid] = svc_id
                self._service_name_map[svc_id] = stats.get('name', svc_id)

        kpi_stats = data.get('kpi_stats', {})

        for kpi_id, stats in sorted(kpi_stats.items(), key=lambda x: x[1].get('count', 0), reverse=True):
            iid = self.action_tree.insert("", tk.END, values=(
                stats.get('name', kpi_id), stats.get('count', 0), stats.get('sla', 0), stats.get('invalid_eta', 0),
            ))
            self._kpi_id_map[iid] = kpi_id

        self.program_tree.sort_by_columns([('program', False), ('count', True), ('sla', True), ('invalid_eta', True)])
        self.action_tree.sort_by_columns([('name', False), ('count', True), ('sla', True), ('invalid_eta', True)])

        age = get_cache_age_minutes(data)
        if age is not None:
            self.cache_age_var.set(f"Cache: {age} minutes old")
            color = "orange" if age > 30 else "green"
            self.cache_age_label.configure(foreground=color)
        else:
            self.cache_age_var.set("")

    def _on_service_double_click(self, event):
        selection = self.services_tree.selection()
        if not selection:
            return

        iid = selection[0]

        group_path = self._group_path_map.get(iid)
        if group_path:
            service_owners_data = self.current_data.get('service_owners', {})
            org_mapping = self.current_data.get('org_mapping', {})

            display_name = group_path[-1]

            if display_name == 'Unknown Owner':
                known_services = set(service_owners_data.keys())
                items = [
                    item for item in self.current_data.get('detailed_items', [])
                    if item.get('S360_ServiceTreeServiceName') not in known_services
                ]
            elif display_name == 'No Owner':
                empty_owner_services = {svc for svc, owners in service_owners_data.items() if not owners}
                items = [
                    item for item in self.current_data.get('detailed_items', [])
                    if item.get('S360_ServiceTreeServiceName') in empty_owner_services
                ]
            else:
                matching_svcs = collect_services_for_owner(
                    group_path, service_owners_data, org_mapping
                )
                items = [
                    item for item in self.current_data.get('detailed_items', [])
                    if item.get('S360_ServiceTreeServiceName') in matching_svcs
                ]

            DetailModal(
                self.root, f"Action Items for {display_name}", items,
                self._service_name_map, on_eta_complete=self._on_eta_update_complete,
            )
            return

        service_id = self._service_id_map.get(iid)
        if not service_id:
            return

        service_name = self._service_name_map.get(service_id, service_id)
        items = filter_items_by_service(
            self.current_data.get('detailed_items', []), service_id
        )

        DetailModal(
            self.root, f"Action Items for {service_name}", items,
            self._service_name_map, on_eta_complete=self._on_eta_update_complete,
        )

    def _on_program_double_click(self, event):
        selection = self.program_tree.selection()
        if not selection:
            return

        iid = selection[0]
        program_id = self._program_id_map.get(iid)
        if not program_id:
            return

        values = self.program_tree.item(iid, 'values')
        program_name = values[0] if values else program_id

        if program_id == 'unassigned':
            items = [
                item for item in self.current_data.get('detailed_items', [])
                if not (item.get('S360_ProgramIds') or [])
            ]
        else:
            items = filter_items_by_program(
                self.current_data.get('detailed_items', []), program_id
            )

        DetailModal(
            self.root, f"Action Items for {program_name}", items,
            self._service_name_map, on_eta_complete=self._on_eta_update_complete,
        )

    def _on_action_double_click(self, event):
        selection = self.action_tree.selection()
        if not selection:
            return

        iid = selection[0]
        kpi_id = self._kpi_id_map.get(iid)
        if not kpi_id:
            return

        values = self.action_tree.item(iid, 'values')
        kpi_name = values[0] if values else kpi_id

        items = [
            item for item in self.current_data.get('detailed_items', [])
            if item.get('_kpi_id') == kpi_id
        ]

        DetailModal(
            self.root, f"Action Items: {kpi_name}", items,
            self._service_name_map, on_eta_complete=self._on_eta_update_complete,
        )

    def _on_kpi_right_click(self, event):
        iid = self.action_tree.identify_row(event.y)
        if not iid:
            return
        self.action_tree.selection_set(iid)
        kpi_id = self._kpi_id_map.get(iid)
        if not kpi_id:
            return

        items = [
            item for item in self.current_data.get('detailed_items', [])
            if item.get('_kpi_id') == kpi_id
        ]
        if not items:
            return

        item = items[0]

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(
            label="\U0001f916 Analyze with LLM",
            command=lambda: _launch_llm_analysis(self.root, item),
        )
        menu.tk_popup(event.x_root, event.y_root)

    def _update_status(self, message: str, color: str = "black"):
        self.root.after(0, lambda: self._do_update_status(message, color))

    def _do_update_status(self, message: str, color: str):
        self.status_var.set(message)
        self.status_label.configure(foreground=color)

    def _on_update_etas(self):
        from sfi_reporter.eta_logic import get_items_needing_eta_update
        from sfi_reporter.data import is_invalid_eta

        items = (self.current_data or {}).get('detailed_items', [])
        if not items:
            return

        invalid = get_items_needing_eta_update(items)

        sorted_all = sorted(items, key=lambda it: (
            0 if is_invalid_eta(it.get('EtaDate')) else 1
        ))

        def on_mode(mode: str):
            if mode == "manual":
                ManualEtaReviewDialog(
                    self.root, sorted_all, on_complete=self._on_eta_update_complete)
            else:
                BulkEtaProgressDialog(
                    self.root, invalid, on_complete=self._on_eta_update_complete)

        EtaModeDialog(self.root, len(items), len(invalid), on_choice=on_mode)

    def _on_eta_update_complete(self, saved, skipped, failed):
        from sfi_reporter.data import is_invalid_eta
        from datetime import datetime

        if not saved:
            return

        for item, eta_str, notes in saved:
            item['EtaDate'] = eta_str
            if notes:
                item['EtaStatus'] = notes

        data = self.current_data
        if data:
            detailed = data.get('detailed_items', [])
            for stats_dict in (data.get('service_stats', {}),
                               data.get('kpi_stats', {}),
                               data.get('program_stats', {})):
                for key in stats_dict:
                    stats_dict[key]['invalid_eta'] = 0

            for row in detailed:
                if is_invalid_eta(row.get('EtaDate')):
                    svc_id = row.get('S360_ServiceId', 'Unknown')
                    kpi_id = row.get('_kpi_id', 'Unknown')
                    if svc_id in data.get('service_stats', {}):
                        data['service_stats'][svc_id]['invalid_eta'] += 1
                    if kpi_id in data.get('kpi_stats', {}):
                        data['kpi_stats'][kpi_id]['invalid_eta'] += 1

                    pid_list = row.get('S360_ProgramIds') or []
                    if pid_list:
                        programs_lookup = data.get('programs_lookup', {})
                        pname = programs_lookup.get(pid_list[0], 'Other Program')
                        if pname in data.get('program_stats', {}):
                            data['program_stats'][pname]['invalid_eta'] += 1

            if data.get('is_manager') and data.get('owner_stats'):
                svc_owners = data.get('service_owners', {})
                org_map = data.get('org_mapping', {})
                data['owner_stats'] = aggregate_by_owner(
                    detailed, svc_owners,
                    org_mapping=org_map if org_map else None,
                )

            self._update_tables(data, is_filtered=bool(
                self._unfiltered_data and
                self._unfiltered_data is not data))

            alias = self.alias_var.get().strip()
            if alias:
                data['timestamp'] = datetime.now().isoformat()
                write_cache(alias, _serialize_org_data_for_cache(data))

        n = len(saved)
        self._update_status(f"\u2705 {n} ETA(s) updated successfully!", "green")

    def _on_refresh(self):
        alias = self.alias_var.get().strip()
        if not alias:
            messagebox.showwarning("Warning", "Please enter a user alias")
            return

        self.refresh_btn.configure(state=tk.DISABLED)
        self.clear_btn.configure(state=tk.DISABLED)
        self._update_status("Starting...", "blue")

        def fetch_in_background():
            def on_status(msg):
                self._update_status(msg, "blue")

            data = do_refresh(alias, on_status=on_status)
            self.root.after(0, lambda: self._on_refresh_complete(data))

        threading.Thread(target=fetch_in_background, daemon=True).start()

    def _on_refresh_complete(self, data: Optional[dict]):
        self.refresh_btn.configure(state=tk.NORMAL)
        self.clear_btn.configure(state=tk.NORMAL)

        if data:
            self._update_tables(data)

            if (self._reapply_filter_var.get()
                    and self._last_filter_clauses):
                self._reapply_last_filter()

            failed = data.get('failed_kpis', [])
            self._failed_kpis = failed
            self._audience_ids = data.get('audience_ids', [])
            self._kpi_names = data.get('kpi_names', {})

            if failed:
                self.retry_btn.pack(side=tk.LEFT, padx=5)
                names = [f['kpi_name'] for f in failed]
                self._update_status(
                    f"\u26a0\ufe0f {len(failed)} KPI(s) failed: {', '.join(names)}", "orange"
                )
            else:
                self.retry_btn.pack_forget()
                services = data.get('services', [])
                detailed_items = data.get('detailed_items', [])
                kpi_stats = data.get('kpi_stats', {})
                has_data = bool(services or detailed_items or kpi_stats)
                if not has_data:
                    self._update_status("\u26a0\ufe0f No action items found for this user", "orange")
                else:
                    self._update_status("\u2705 Data refreshed!", "green")
        else:
            self.retry_btn.pack_forget()
            self._update_status("\u274c Error fetching data", "red")

    def _on_retry_failed(self):
        if not self._failed_kpis or not self._audience_ids:
            return

        failed_ids = [f['kpi_id'] for f in self._failed_kpis]
        logger.info("Retrying %d failed KPIs: %s", len(failed_ids),
                    [f['kpi_name'] for f in self._failed_kpis])

        self.refresh_btn.configure(state=tk.DISABLED)
        self.clear_btn.configure(state=tk.DISABLED)
        self.retry_btn.configure(state=tk.DISABLED)
        self._update_status(f"Retrying {len(failed_ids)} failed KPI(s)...", "blue")

        audience_ids = self._audience_ids
        kpi_names = self._kpi_names
        alias = self.alias_var.get().strip()

        def retry_in_background():
            from sfi_reporter.data import get_detailed_action_items, is_invalid_eta
            from datetime import datetime

            def on_status(msg):
                self._update_status(msg, "blue")

            new_rows, still_failed = get_detailed_action_items(
                audience_ids, failed_ids, on_status, kpi_names
            )

            self.root.after(0, lambda: self._on_retry_complete(new_rows, still_failed, alias))

        threading.Thread(target=retry_in_background, daemon=True).start()

    def _on_retry_complete(self, new_rows: list, still_failed: list, alias: str):
        from sfi_reporter.data import is_invalid_eta
        from datetime import datetime

        self.refresh_btn.configure(state=tk.NORMAL)
        self.clear_btn.configure(state=tk.NORMAL)
        self.retry_btn.configure(state=tk.NORMAL)

        if not new_rows and still_failed:
            self._failed_kpis = still_failed
            names = [f['kpi_name'] for f in still_failed]
            self._update_status(
                f"\u274c Retry failed \u2014 {len(still_failed)} KPI(s) still failing: {', '.join(names)}",
                "red"
            )
            return

        cached = read_cache(alias)
        if cached:
            cached = _deserialize_org_data_from_cache(cached)
        if not cached:
            self._update_status("\u274c Cache missing \u2014 do a full refresh", "red")
            return

        existing_items = cached.get('detailed_items', [])
        existing_items.extend(new_rows)
        cached['detailed_items'] = existing_items

        kpi_stats = cached.get('kpi_stats', {})
        kpi_names = cached.get('kpi_names', self._kpi_names)
        for row in new_rows:
            kpi_id = row.get('_kpi_id', 'Unknown')
            sla_type = row.get('SlaType', '')
            eta_date = row.get('EtaDate')
            if kpi_id not in kpi_stats:
                kpi_stats[kpi_id] = {'name': kpi_names.get(kpi_id, kpi_id), 'count': 0, 'sla': 0, 'invalid_eta': 0}
            kpi_stats[kpi_id]['count'] += 1
            if sla_type == 'OutOfSla':
                kpi_stats[kpi_id]['sla'] += 1
            if is_invalid_eta(eta_date):
                kpi_stats[kpi_id]['invalid_eta'] += 1

        cached['kpi_stats'] = kpi_stats
        cached['failed_kpis'] = still_failed
        cached['timestamp'] = datetime.now().isoformat()

        write_cache(alias, _serialize_org_data_for_cache(cached))
        self._update_tables(cached)

        self._failed_kpis = still_failed
        self._audience_ids = cached.get('audience_ids', self._audience_ids)

        if still_failed:
            self.retry_btn.pack(side=tk.LEFT, padx=5)
            names = [f['kpi_name'] for f in still_failed]
            self._update_status(
                f"\u2705 Recovered {len(new_rows)} items \u2014 \u26a0\ufe0f {len(still_failed)} KPI(s) still failing: {', '.join(names)}",
                "orange"
            )
        else:
            self.retry_btn.pack_forget()
            self._update_status(
                f"\u2705 Retry successful \u2014 recovered {len(new_rows)} items!", "green"
            )

    def _on_clear_cache(self):
        alias = self.alias_var.get().strip()
        if alias and clear_cache(alias):
            for item in self.services_tree.get_children():
                self.services_tree.delete(item)
            for item in self.action_tree.get_children():
                self.action_tree.delete(item)
            for item in self.program_tree.get_children():
                self.program_tree.delete(item)

            self.cache_age_var.set("")
            self._update_status("Cache cleared", "blue")

    def _on_query(self):
        from sfi_reporter.query_builder import QueryBuilder

        source = self._unfiltered_data or self.current_data
        action_items = source.get('detailed_items', [])
        program_names = source.get('programs_lookup', {})
        service_names = {
            s.get('Id', ''): s.get('Name', '')
            for s in source.get('services', [])
        }
        is_manager = source.get('is_manager', False)
        service_owners = source.get('service_owners', {})

        QueryBuilder(
            self.root,
            action_items=action_items,
            program_names=program_names,
            service_names=service_names,
            is_manager=is_manager,
            service_owners=service_owners,
            on_apply=self._on_filter_applied,
        )

    def _reapply_last_filter(self):
        from sfi_reporter.query_builder import evaluate_clauses
        source = self._unfiltered_data or self.current_data
        items = source.get('detailed_items', [])
        if not items:
            return
        filtered = evaluate_clauses(
            items, self._last_filter_clauses,
            include_ussec=self._last_filter_ussec,
        )
        self._on_filter_applied(filtered, self._last_filter_clauses)

    def _on_filter_applied(self, filtered_items: list, clauses: list):
        self._last_filter_clauses = clauses
        from sfi_reporter.query_builder import load_clause_cache
        _, ussec = load_clause_cache()
        self._last_filter_ussec = ussec

        if not clauses:
            original = self._unfiltered_data or self.current_data
            self.query_btn.configure(text="\U0001f50d Filter")
            self._update_tables(original)
            return

        from sfi_reporter.data import is_invalid_eta
        data = dict(self._unfiltered_data or self.current_data)
        data['detailed_items'] = filtered_items

        program_names = data.get('programs_lookup', {})
        service_stats = {}
        kpi_stats = {}
        program_stats = {}
        kpi_names = data.get('kpi_names', {})

        for row in filtered_items:
            svc_id = row.get('S360_ServiceId', 'Unknown')
            svc_name = row.get('S360_ServiceTreeServiceName', 'Unknown')
            kpi_id = row.get('_kpi_id', 'Unknown')
            sla_type = row.get('SlaType', '')
            eta_date = row.get('EtaDate')
            pid_list = row.get('S360_ProgramIds') or []

            is_out_of_sla = sla_type == 'OutOfSla'
            is_invalid = is_invalid_eta(eta_date)

            if svc_id not in service_stats:
                service_stats[svc_id] = {'name': svc_name, 'count': 0, 'sla': 0, 'invalid_eta': 0}
            service_stats[svc_id]['count'] += 1
            if is_out_of_sla:
                service_stats[svc_id]['sla'] += 1
            if is_invalid:
                service_stats[svc_id]['invalid_eta'] += 1

            if kpi_id not in kpi_stats:
                kpi_stats[kpi_id] = {'name': kpi_names.get(kpi_id, kpi_id), 'count': 0, 'sla': 0, 'invalid_eta': 0}
            kpi_stats[kpi_id]['count'] += 1
            if is_out_of_sla:
                kpi_stats[kpi_id]['sla'] += 1
            if is_invalid:
                kpi_stats[kpi_id]['invalid_eta'] += 1

            if pid_list:
                pid = pid_list[0]
                pname = program_names.get(pid, 'Other Program')
                if pname not in program_stats:
                    program_stats[pname] = {'count': 0, 'sla': 0, 'invalid_eta': 0, 'id': pid}
                program_stats[pname]['count'] += 1
                if is_out_of_sla:
                    program_stats[pname]['sla'] += 1
                if is_invalid:
                    program_stats[pname]['invalid_eta'] += 1
            else:
                if 'Unassigned' not in program_stats:
                    program_stats['Unassigned'] = {'count': 0, 'sla': 0, 'invalid_eta': 0, 'id': 'unassigned'}
                program_stats['Unassigned']['count'] += 1
                if is_out_of_sla:
                    program_stats['Unassigned']['sla'] += 1
                if is_invalid:
                    program_stats['Unassigned']['invalid_eta'] += 1

        data['service_stats'] = service_stats
        data['kpi_stats'] = kpi_stats
        data['program_stats'] = program_stats

        if data.get('is_manager') and service_stats:
            svc_owners = data.get('service_owners', {})
            org_map = data.get('org_mapping', {})
            data['owner_stats'] = aggregate_by_owner(
                filtered_items, svc_owners,
                org_mapping=org_map if org_map else None,
            )

        n = len(filtered_items)
        self.query_btn.configure(text=f"\U0001f50d Filter ({n})")

        self._update_tables(data, is_filtered=True)


def main():
    """Main entry point."""
    setup_logging()
    patch_subprocess_windows()
    logger.info("SFI Reporter starting \u2014 log file: %s", get_log_path())

    root = tk.Tk()

    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure('Treeview', indent=10)

    app = SFIReporterApp(root)
    root.mainloop()


__all__ = [
    'SFIReporterApp',
    'main',
]

if __name__ == "__main__":
    main()
