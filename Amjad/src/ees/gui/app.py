"""EES GUI — Desktop application for incident processing and rule management.

Wraps the existing expert system engine with a Tkinter interface.
Uses ttk themed widgets for Windows-native appearance.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from ees.fact_extractor import FactExtractor
from ees.gap_detector import GapDetector
from ees.gui.adapters import (
    eval_result_to_display,
    facts_to_rows,
    filter_rules,
    ontology_to_tree,
    rules_to_rows,
)
from ees.gui.workers import run_in_worker
from ees.gui.settings import SettingsManager
try:
    from ees.gui.kusto_client import KustoClient, KUSTO_AVAILABLE
except ImportError:  # pragma: no cover
    KUSTO_AVAILABLE = False
from ees.models import Fact, Incident, Rule, RootCause
from ees.ontology_manager import OntologyManager
from ees.rule_evaluator import RuleEvaluator
from ees.rule_generator import RuleGenerator
from ees.yaml_store import YamlStore


class EESApp:
    """Main EES GUI application."""

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.store = YamlStore(self.data_dir)
        self.settings_mgr = SettingsManager(self.data_dir)

        self._ensure_data_dirs()

        self.root = tk.Tk()
        self.root.title("Expert System (EES)")
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)

        # State
        self._pending_facts: list[Fact] = []
        self._pending_rules: list[Rule] = []
        self._pending_root_cause: str | None = None
        self._incident_text: str = ""

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the main tabbed interface."""
        # Menu bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Set Data Directory...",
                              command=self._set_data_dir)
        file_menu.add_command(label="Settings...",
                              command=self._open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Process Incident
        self._build_process_tab()

        # Tab 2: Knowledge Base
        self._build_kb_tab()

        # Tab 3: Evaluate
        self._build_eval_tab()

        # Status bar
        self.status_var = tk.StringVar(value=f"Data: {self.data_dir.resolve()}")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)

    # ── Tab 1: Process Incident ───────────────────────────────

    def _build_process_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Process Incident")

        # Top: file selection
        top = ttk.Frame(frame)
        top.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(top, text="Incident file:").pack(side=tk.LEFT)
        self.incident_path_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.incident_path_var, width=60).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(top, text="Browse...",
                   command=self._browse_incident).pack(side=tk.LEFT)
        self.extract_btn = ttk.Button(top, text="Extract Facts",
                                      command=self._extract_facts)
        self.extract_btn.pack(side=tk.LEFT, padx=5)

        # Kusto fetch row
        kusto_row = ttk.Frame(frame)
        kusto_row.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Label(kusto_row, text="Incident ID:").pack(side=tk.LEFT)
        self.incident_id_var = tk.StringVar()
        ttk.Entry(kusto_row, textvariable=self.incident_id_var, width=30).pack(
            side=tk.LEFT, padx=5)
        self.fetch_kusto_btn = ttk.Button(
            kusto_row, text="Fetch from Kusto",
            command=self._fetch_from_kusto,
            state=tk.NORMAL if KUSTO_AVAILABLE else tk.DISABLED,
        )
        self.fetch_kusto_btn.pack(side=tk.LEFT)
        if not KUSTO_AVAILABLE:
            ttk.Label(
                kusto_row, text="(accia-datacollection not installed)",
                foreground="gray",
            ).pack(side=tk.LEFT, padx=5)

        # Paned window: left=text, right=facts/rules
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: incident text
        left = ttk.LabelFrame(paned, text="Incident Text")
        self.incident_text = tk.Text(left, wrap=tk.WORD, state=tk.DISABLED,
                                     width=40)
        self.incident_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        paned.add(left, weight=1)

        # Right: facts and rules
        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        # Facts frame
        facts_frame = ttk.LabelFrame(right, text="Proposed Facts")
        facts_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        cols = ("noun", "instance", "property", "operator", "value", "status")
        self.facts_tree = ttk.Treeview(facts_frame, columns=cols,
                                       show="headings", height=8)
        for col in cols:
            self.facts_tree.heading(col, text=col.title())
            self.facts_tree.column(col, width=100)
        self.facts_tree.pack(fill=tk.BOTH, expand=True)

        fact_btns = ttk.Frame(facts_frame)
        fact_btns.pack(fill=tk.X, pady=2)
        ttk.Button(fact_btns, text="Confirm",
                   command=lambda: self._set_fact_status("confirmed")).pack(
                       side=tk.LEFT, padx=2)
        ttk.Button(fact_btns, text="Reject",
                   command=lambda: self._set_fact_status("rejected")).pack(
                       side=tk.LEFT, padx=2)
        ttk.Button(fact_btns, text="Confirm All",
                   command=self._confirm_all_facts).pack(side=tk.LEFT, padx=2)

        # Rules/save frame
        rules_frame = ttk.LabelFrame(right, text="Proposed Rules")
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        rule_cols = ("rule_id", "type", "conditions", "then")
        self.rules_tree = ttk.Treeview(rules_frame, columns=rule_cols,
                                       show="headings", height=6)
        for col in rule_cols:
            self.rules_tree.heading(col, text=col.title())
        self.rules_tree.column("rule_id", width=80)
        self.rules_tree.column("type", width=80)
        self.rules_tree.column("conditions", width=250)
        self.rules_tree.column("then", width=200)
        self.rules_tree.pack(fill=tk.BOTH, expand=True)

        save_frame = ttk.Frame(rules_frame)
        save_frame.pack(fill=tk.X, pady=2)
        self.save_btn = ttk.Button(save_frame, text="Save All",
                                   command=self._save_all, state=tk.DISABLED)
        self.save_btn.pack(side=tk.RIGHT, padx=5)

        # Progress
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=5, pady=2)

    def _browse_incident(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Incident File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.incident_path_var.set(path)
            self._load_incident_text(path)

    def _load_incident_text(self, path: str) -> None:
        try:
            text = Path(path).read_text(encoding="utf-8")
            self._incident_text = text
            self.incident_text.config(state=tk.NORMAL)
            self.incident_text.delete("1.0", tk.END)
            self.incident_text.insert("1.0", text)
            self.incident_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def _fetch_from_kusto(self) -> None:
        """Fetch incident text from Kusto by incident ID."""
        incident_id = self.incident_id_var.get().strip()
        if not incident_id:
            messagebox.showwarning("Warning", "Enter an Incident ID first.")
            return

        self.fetch_kusto_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set(f"Fetching incident {incident_id} from Kusto...")

        kusto_settings = self.settings_mgr.load_kusto()
        client = KustoClient(
            cluster=kusto_settings["cluster"],
            database=kusto_settings["database"],
        )

        def task():
            return client.fetch_incident(incident_id)

        def on_done(text):
            self.progress.stop()
            self.fetch_kusto_btn.config(state=tk.NORMAL)
            self._incident_text = text
            self.incident_text.config(state=tk.NORMAL)
            self.incident_text.delete("1.0", tk.END)
            self.incident_text.insert("1.0", text)
            self.incident_text.config(state=tk.DISABLED)
            self.status_var.set(
                f"Loaded incident {incident_id} from Kusto "
                f"({len(text)} chars)"
            )

        def on_error(exc):
            self.progress.stop()
            self.fetch_kusto_btn.config(state=tk.NORMAL)
            self.status_var.set("Kusto fetch failed.")
            messagebox.showerror(
                "Kusto Error", str(exc), parent=self.root,
            )

        run_in_worker(task, on_done, on_error)

    def _extract_facts(self) -> None:
        if not self._incident_text:
            messagebox.showwarning("Warning", "Load an incident file first.")
            return

        self.extract_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Extracting facts via LLM...")

        ontology_nouns = self.store.load_ontology()

        def do_extract():
            settings = self.settings_mgr.load()
            extractor = FactExtractor(
                endpoint=settings["endpoint"],
                deployment=settings["deployment"],
                api_version=settings["api_version"],
            )
            return extractor.extract(self._incident_text, ontology_nouns)

        def on_complete(llm_response):
            self.root.after(0, self._on_extraction_complete, llm_response)

        def on_error(exc):
            self.root.after(0, self._on_extraction_error, exc)

        run_in_worker(do_extract, on_complete, on_error)

    def _on_extraction_complete(self, llm_response) -> None:
        self.progress.stop()
        self.extract_btn.config(state=tk.NORMAL)
        self.status_var.set("Extraction complete.")

        self._pending_facts = llm_response.facts
        self._pending_rules = llm_response.rules
        self._pending_root_cause = llm_response.root_cause

        # Populate facts tree
        self.facts_tree.delete(*self.facts_tree.get_children())
        for i, row in enumerate(facts_to_rows(self._pending_facts)):
            self.facts_tree.insert("", tk.END, iid=str(i), values=(
                row["noun"], row["instance"], row["property"],
                row["operator"], row["value"], row["status"],
            ))

        # Populate rules tree
        self.rules_tree.delete(*self.rules_tree.get_children())
        for i, row in enumerate(rules_to_rows(self._pending_rules)):
            self.rules_tree.insert("", tk.END, iid=str(i), values=(
                row["rule_id"], row["type"], row["conditions"], row["then"],
            ))

        self.save_btn.config(state=tk.NORMAL)

    def _on_extraction_error(self, exc) -> None:
        self.progress.stop()
        self.extract_btn.config(state=tk.NORMAL)
        self.status_var.set("Extraction failed.")
        messagebox.showerror("LLM Error", str(exc))

    def _set_fact_status(self, status: str) -> None:
        selected = self.facts_tree.selection()
        for iid in selected:
            idx = int(iid)
            self._pending_facts[idx].status = status
            vals = list(self.facts_tree.item(iid, "values"))
            vals[5] = status
            self.facts_tree.item(iid, values=vals)

    def _confirm_all_facts(self) -> None:
        for i, fact in enumerate(self._pending_facts):
            fact.status = "confirmed"
            vals = list(self.facts_tree.item(str(i), "values"))
            vals[5] = "confirmed"
            self.facts_tree.item(str(i), values=vals)

    def _save_all(self) -> None:
        """Save the processed incident, confirmed rules, and updates."""
        confirmed_facts = [f for f in self._pending_facts
                           if f.status == "confirmed"]
        if not confirmed_facts:
            messagebox.showwarning("Warning", "No confirmed facts to save.")
            return

        # Generate IDs
        incident_id = self.store.next_incident_id()

        # Save incident
        incident = Incident(
            incident_id=incident_id,
            source_text=self._incident_text,
            facts=self._pending_facts,
            root_cause_identified=self._pending_root_cause,
        )
        self.store.save_incident(incident)

        # Filter and save rules
        existing_rules = self.store.list_rules()
        gen = RuleGenerator(existing_rules)
        filtered = gen.filter_rules(self._pending_rules, confirmed_facts)

        for rule in filtered:
            rule.rule_id = self.store.next_rule_id()
            rule.sources = [incident_id]
            self.store.save_rule(rule)

        # GAP detection
        detector = GapDetector(existing_rules)
        gaps = detector.detect_gaps(
            confirmed_facts, filtered, self._pending_root_cause, incident_id)
        for gap in gaps:
            gap.rule_id = self.store.next_rule_id()
            self.store.save_rule(gap)

        # Refinements
        refinements = detector.check_refinements(filtered, incident_id)
        for ref in refinements:
            self.store.save_rule(ref.updated_rule)

        # Ontology
        ontology_nouns = self.store.load_ontology()
        mgr = OntologyManager(ontology_nouns)
        mgr.update_from_facts(confirmed_facts)
        if mgr.has_changes():
            self.store.save_ontology(mgr.get_nouns())

        # Root causes
        if self._pending_root_cause:
            rcs = self.store.load_root_causes()
            rc_names = {rc.name.lower() for rc in rcs}
            if self._pending_root_cause.lower() not in rc_names:
                rcs.append(RootCause(name=self._pending_root_cause))
            self.store.save_root_causes(rcs)

        self.save_btn.config(state=tk.DISABLED)
        self.status_var.set(
            f"Saved: {incident_id}, {len(filtered)} rules, {len(gaps)} GAPs")
        messagebox.showinfo("Saved",
                            f"Incident {incident_id} saved.\n"
                            f"Rules: {len(filtered)}\nGAPs: {len(gaps)}")

    # ── Tab 2: Knowledge Base ─────────────────────────────────

    def _build_kb_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Knowledge Base")

        kb_notebook = ttk.Notebook(frame)
        kb_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Rules sub-tab
        rules_frame = ttk.Frame(kb_notebook)
        kb_notebook.add(rules_frame, text="Rules")

        # Filter bar
        filter_bar = ttk.Frame(rules_frame)
        filter_bar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_bar, text="Status:").pack(side=tk.LEFT)
        self.kb_status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_bar, textvariable=self.kb_status_var,
                                    values=["All", "CONFIRMED", "GAP", "RESOLVED"],
                                    state="readonly", width=12)
        status_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_bar, text="Type:").pack(side=tk.LEFT)
        self.kb_type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(filter_bar, textvariable=self.kb_type_var,
                                  values=["All", "positive", "ruleout"],
                                  state="readonly", width=12)
        type_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_bar, text="Refresh",
                   command=self._refresh_kb_rules).pack(side=tk.LEFT, padx=5)

        # Rules treeview
        cols = ("rule_id", "status", "type", "conditions", "then", "because")
        self.kb_rules_tree = ttk.Treeview(rules_frame, columns=cols,
                                          show="headings", height=15)
        for col in cols:
            self.kb_rules_tree.heading(col, text=col.title())
        self.kb_rules_tree.column("rule_id", width=80)
        self.kb_rules_tree.column("status", width=90)
        self.kb_rules_tree.column("type", width=80)
        self.kb_rules_tree.column("conditions", width=300)
        self.kb_rules_tree.column("then", width=200)
        self.kb_rules_tree.column("because", width=250)
        self.kb_rules_tree.pack(fill=tk.BOTH, expand=True, padx=5)

        # Ontology sub-tab
        ont_frame = ttk.Frame(kb_notebook)
        kb_notebook.add(ont_frame, text="Ontology")

        self.ont_tree = ttk.Treeview(ont_frame, show="tree", height=15)
        self.ont_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(ont_frame, text="Refresh",
                   command=self._refresh_ontology).pack(padx=5, pady=5)

        # Root Causes sub-tab
        rc_frame = ttk.Frame(kb_notebook)
        kb_notebook.add(rc_frame, text="Root Causes")

        self.rc_listbox = tk.Listbox(rc_frame, height=15)
        self.rc_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(rc_frame, text="Refresh",
                   command=self._refresh_root_causes).pack(padx=5, pady=5)

    def _refresh_kb_rules(self) -> None:
        all_rules = self.store.list_rules()
        status_filter = self.kb_status_var.get()
        type_filter = self.kb_type_var.get()

        filtered = filter_rules(
            all_rules,
            status=None if status_filter == "All" else status_filter,
            rule_type=None if type_filter == "All" else type_filter,
        )

        self.kb_rules_tree.delete(*self.kb_rules_tree.get_children())
        for row in rules_to_rows(filtered):
            self.kb_rules_tree.insert("", tk.END, values=(
                row["rule_id"], row["status"], row["type"],
                row["conditions"], row["then"], row["because"],
            ))
        self.status_var.set(f"Rules: {len(filtered)} shown of {len(all_rules)} total")

    def _refresh_ontology(self) -> None:
        nouns = self.store.load_ontology()
        self.ont_tree.delete(*self.ont_tree.get_children())
        for entry in ontology_to_tree(nouns):
            parent = self.ont_tree.insert("", tk.END, text=entry["noun"])
            for prop in entry["properties"]:
                self.ont_tree.insert(parent, tk.END,
                                     text=f"{prop['name']} ({prop['type']})")

    def _refresh_root_causes(self) -> None:
        rcs = self.store.load_root_causes()
        self.rc_listbox.delete(0, tk.END)
        for rc in rcs:
            self.rc_listbox.insert(tk.END, rc.name)

    # ── Tab 3: Evaluate ───────────────────────────────────────

    def _build_eval_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Evaluate")

        # Input area
        input_frame = ttk.LabelFrame(frame, text="Input Facts (one per line)")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.eval_input = tk.Text(input_frame, height=5, wrap=tk.WORD)
        self.eval_input.pack(fill=tk.X, padx=5, pady=5)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(btn_frame, text="Evaluate",
                   command=self._run_evaluation).pack(side=tk.LEFT)

        # Results area
        results_frame = ttk.LabelFrame(frame, text="Evaluation Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.eval_results = tk.Text(results_frame, wrap=tk.WORD,
                                    state=tk.DISABLED)
        scroll = ttk.Scrollbar(results_frame, command=self.eval_results.yview)
        self.eval_results.config(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.eval_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _run_evaluation(self) -> None:
        text = self.eval_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Enter at least one fact.")
            return

        # Parse facts (one per line)
        input_facts = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            fact = Fact.parse(line)
            if fact is None:
                messagebox.showerror("Error", f"Invalid fact: {line}")
                return
            input_facts.append(fact)

        if not input_facts:
            messagebox.showwarning("Warning", "No valid facts entered.")
            return

        # Evaluate
        rules = self.store.list_rules()
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate(input_facts)
        display = eval_result_to_display(result)
        text = _format_eval_display(display, total_rules=len(rules))

        self.eval_results.config(state=tk.NORMAL)
        self.eval_results.delete("1.0", tk.END)
        self.eval_results.insert("1.0", text)
        self.eval_results.config(state=tk.DISABLED)

        self.status_var.set(f"Evaluation: {len(display['fired_rules'])} rules fired")

    # ── Settings ──────────────────────────────────────────────

    def _ensure_data_dirs(self) -> None:
        """Create required subdirectories under data_dir."""
        (self.data_dir / "incidents").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "rules").mkdir(parents=True, exist_ok=True)

    def _set_data_dir(self) -> None:
        path = filedialog.askdirectory(title="Select Data Directory")
        if path:
            self.data_dir = Path(path)
            self.store = YamlStore(self.data_dir)
            self.settings_mgr = SettingsManager(self.data_dir)
            self._ensure_data_dirs()
            self.status_var.set(f"Data: {self.data_dir.resolve()}")

    def _open_settings(self) -> None:
        """Open the Settings dialog."""
        SettingsDialog(self.root, self.settings_mgr)

    # ── Run ───────────────────────────────────────────────────

    def run(self) -> None:
        """Start the GUI event loop."""
        self.root.mainloop()


class SettingsDialog:
    """Modal dialog for Azure OpenAI and Kusto configuration."""

    _OPENAI_FIELDS = [
        ("endpoint", "Endpoint URL:"),
        ("deployment", "Deployment:"),
        ("api_version", "API Version:"),
    ]

    _KUSTO_FIELDS = [
        ("cluster", "Kusto Cluster:"),
        ("database", "Kusto Database:"),
    ]

    def __init__(self, parent: tk.Tk, settings_mgr: SettingsManager) -> None:
        self._mgr = settings_mgr

        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Settings")
        self._dialog.resizable(False, False)
        self._dialog.grab_set()
        self._dialog.transient(parent)

        self._entries: dict[str, tk.StringVar] = {}
        self._source_labels: dict[str, ttk.Label] = {}
        self._kusto_entries: dict[str, tk.StringVar] = {}

        frame = ttk.Frame(self._dialog, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        # ── Azure OpenAI section ──
        ttk.Label(frame, text="Azure OpenAI", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        for idx, (key, label) in enumerate(self._OPENAI_FIELDS):
            row = idx + 1
            ttk.Label(frame, text=label).grid(
                row=row, column=0, sticky=tk.W, pady=4)
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var, width=50)
            entry.grid(row=row, column=1, padx=5, pady=4)
            src_label = ttk.Label(frame, text="", width=10)
            src_label.grid(row=row, column=2, padx=5, pady=4)

            value, source = self._mgr.get_effective(key)
            var.set(value)
            src_label.config(text=f"({source})")

            self._entries[key] = var
            self._source_labels[key] = src_label

        # ── Kusto section ──
        kusto_start = len(self._OPENAI_FIELDS) + 1
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(
            row=kusto_start, column=0, columnspan=3, sticky="ew", pady=8)
        ttk.Label(frame, text="Kusto (Azure Data Explorer)",
                  font=("", 10, "bold")).grid(
            row=kusto_start + 1, column=0, columnspan=3,
            sticky=tk.W, pady=(0, 5))

        kusto_settings = self._mgr.load_kusto()
        for idx, (key, label) in enumerate(self._KUSTO_FIELDS):
            row = kusto_start + 2 + idx
            ttk.Label(frame, text=label).grid(
                row=row, column=0, sticky=tk.W, pady=4)
            var = tk.StringVar(value=kusto_settings.get(key, ""))
            entry = ttk.Entry(frame, textvariable=var, width=50)
            entry.grid(row=row, column=1, padx=5, pady=4)
            self._kusto_entries[key] = var

        # Buttons
        btn_row = kusto_start + 2 + len(self._KUSTO_FIELDS)
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=btn_row, column=0, columnspan=3, pady=10)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel",
                   command=self._dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _save(self) -> None:
        openai_settings = {key: var.get() for key, var in self._entries.items()}

        # Basic URL validation
        endpoint = openai_settings.get("endpoint", "")
        if endpoint and not endpoint.startswith("https://"):
            messagebox.showwarning(
                "Warning",
                "Endpoint should start with https://. Saving anyway.",
                parent=self._dialog,
            )

        self._mgr.save(openai_settings)

        # Save Kusto settings
        kusto_settings = {
            key: var.get() for key, var in self._kusto_entries.items()
        }
        self._mgr.save_kusto(kusto_settings)

        # Update source labels
        for key in self._entries:
            self._source_labels[key].config(text="(config)")

        messagebox.showinfo("Settings", "Settings saved.", parent=self._dialog)
        self._dialog.destroy()


def _format_eval_display(display: dict, *, total_rules: int) -> str:
    """Format an eval_result_to_display dict as human-readable text."""
    lines: list[str] = []
    lines.append("=== Evaluation Results ===\n")
    lines.append(f"Input facts ({len(display['input_facts'])}):")
    for f in display["input_facts"]:
        lines.append(f"  \u2022 {f}")

    if display["fired_rules"]:
        lines.append(f"\nFired rules ({len(display['fired_rules'])}):")
        for r in display["fired_rules"]:
            lines.append(f"  {r['rule_id']}: {r['conditions']} \u2192 {r['then']}")

    if display["root_causes"]:
        lines.append(f"\nRoot causes identified ({len(display['root_causes'])}):")
        for rc in display["root_causes"]:
            lines.append(f"  \u2713 {rc}")

    if display["ruled_out"]:
        lines.append(f"\nRoot causes ruled out ({len(display['ruled_out'])}):")
        for ro in display["ruled_out"]:
            lines.append(f"  \u2717 {ro}")

    if display["gap_rules"]:
        lines.append(f"\nGAP rules encountered ({len(display['gap_rules'])}):")
        for g in display["gap_rules"]:
            lines.append(f"  {g['rule_id']}: {g['requires']} \u2014 {g['note']}")

    lines.append(f"\nSummary: {total_rules} rules evaluated, "
                 f"{len(display['fired_rules'])} fired, "
                 f"{len(display['root_causes'])} root causes, "
                 f"{len(display['ruled_out'])} ruled out, "
                 f"{len(display['gap_rules'])} GAPs")
    return "\n".join(lines)


def main() -> None:
    """Entry point for the GUI application."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="ees-gui",
        description="Expert System GUI",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Path to the data directory (default: data)",
    )
    args = parser.parse_args()

    app = EESApp(data_dir=args.data_dir)
    app.run()


if __name__ == "__main__":
    main()
