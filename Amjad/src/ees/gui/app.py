"""EES GUI — Desktop application for incident processing and rule management.

Wraps the existing expert system engine with a Tkinter interface.
Uses ttk themed widgets for Windows-native appearance.
"""
from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from tkhtmlview import HTMLScrolledText

_STYLE_RE = re.compile(r'\s*style\s*=\s*"[^"]*"', re.IGNORECASE)
_STYLE_BLOCK_RE = re.compile(r'<style[^>]*>.*?</style>', re.IGNORECASE | re.DOTALL)


def _sanitize_html_colors(html: str) -> str:
    """Strip inline style attributes and <style> blocks — Tkinter can't handle CSS values."""
    html = _STYLE_BLOCK_RE.sub("", html)
    return _STYLE_RE.sub("", html)


class _ToolTip:
    """Lightweight hover tooltip for any Tkinter widget."""

    def __init__(self, widget: tk.Widget, text: str, *, delay: int = 400) -> None:
        self._widget = widget
        self._text = text
        self._delay = delay
        self._tip_window: tk.Toplevel | None = None
        self._after_id: str | None = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _schedule(self, _event: tk.Event) -> None:
        self._after_id = self._widget.after(self._delay, self._show)

    def _show(self) -> None:
        if self._tip_window:
            return
        x = self._widget.winfo_rootx() + self._widget.winfo_width() // 2
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self._text, background="#ffffe1", relief="solid",
            borderwidth=1, font=("Segoe UI", 9), wraplength=300, justify="left",
        )
        label.pack()
        self._tip_window = tw

    def _hide(self, _event: tk.Event | None = None) -> None:
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None


from ees.fact_extractor import FactExtractor
from ees.gap_detector import GapDetector
from ees.gui.adapters import (
    eval_result_to_display,
    facts_to_rows,
    facts_used_by_rules,
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
from ees.models import Fact, Incident, Rule
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

        # Left: incident text (HTML rendered)
        left = ttk.LabelFrame(paned, text="Incident Text")
        self.incident_text = HTMLScrolledText(left, html="<i>No incident loaded.</i>")
        self.incident_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        paned.add(left, weight=1)

        # Right: facts and rules
        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        # Facts frame
        facts_frame = ttk.LabelFrame(right, text="Proposed Facts")
        facts_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        cols = ("noun", "instance", "property", "operator", "value", "status", "scope")
        self.facts_tree = ttk.Treeview(facts_frame, columns=cols,
                                       show="headings", height=8)
        for col in cols:
            self.facts_tree.heading(col, text=col.title())
            self.facts_tree.column(col, width=100)
        self.facts_tree.pack(fill=tk.BOTH, expand=True)
        self.facts_tree.bind("<Double-1>", self._on_facts_double_click)

        # Bold tag for facts used by rules
        import tkinter.font as tkfont
        default_font = tkfont.nametofont("TkDefaultFont")
        bold_font = tkfont.Font(family=default_font.cget("family"),
                                size=default_font.cget("size"),
                                weight="bold")
        self.facts_tree.tag_configure("used", font=bold_font)

        fact_btns = ttk.Frame(facts_frame)
        fact_btns.pack(fill=tk.X, pady=2)
        btn = ttk.Button(fact_btns, text="Confirm",
                         command=lambda: self._set_fact_status("confirmed"))
        btn.pack(side=tk.LEFT, padx=2)
        _ToolTip(btn, "Mark the selected fact as confirmed.\n"
                 "Only confirmed facts are saved to the knowledge base.")

        btn = ttk.Button(fact_btns, text="Reject",
                         command=lambda: self._set_fact_status("rejected"))
        btn.pack(side=tk.LEFT, padx=2)
        _ToolTip(btn, "Mark the selected fact as rejected.\n"
                 "Rejected facts are discarded and won't be saved.")

        btn = ttk.Button(fact_btns, text="Confirm All",
                         command=self._confirm_all_facts)
        btn.pack(side=tk.LEFT, padx=2)
        _ToolTip(btn, "Confirm every proposed fact at once.")

        btn = ttk.Button(fact_btns, text="Set Rule",
                         command=lambda: self._set_fact_scope("rule"))
        btn.pack(side=tk.LEFT, padx=2)
        _ToolTip(btn, "Change scope to 'rule'. Rule-scoped facts are\n"
                 "generalizable and used to build troubleshooting rules.")

        btn = ttk.Button(fact_btns, text="Set Context",
                         command=lambda: self._set_fact_scope("context"))
        btn.pack(side=tk.LEFT, padx=2)
        _ToolTip(btn, "Change scope to 'context'. Context-scoped facts are\n"
                 "instance-specific and stored for documentation only.")

        btn = ttk.Button(fact_btns, text="Confirm Used",
                         command=self._confirm_used_facts)
        btn.pack(side=tk.LEFT, padx=2)
        _ToolTip(btn, "Confirm only facts that are referenced by at least\n"
                 "one proposed rule condition (shown in bold).")

        # Rules/save frame
        rules_frame = ttk.LabelFrame(right, text="Proposed Rules")
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        rule_cols = ("rule_id", "type", "conditions", "then", "else")
        self.rules_tree = ttk.Treeview(rules_frame, columns=rule_cols,
                                       show="headings", height=6)
        for col in rule_cols:
            self.rules_tree.heading(col, text=col.title())
        self.rules_tree.column("rule_id", width=80)
        self.rules_tree.column("type", width=80)
        self.rules_tree.column("conditions", width=250)
        self.rules_tree.column("then", width=200)
        self.rules_tree.column("else", width=200)
        self.rules_tree.pack(fill=tk.BOTH, expand=True)
        self.rules_tree.bind("<Double-1>", self._on_rules_double_click)

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
            self.incident_text.set_html(_sanitize_html_colors(text))
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
            self.root.after(0, self._on_kusto_complete, incident_id, text)

        def on_error(exc):
            self.root.after(0, self._on_kusto_error, exc)

        run_in_worker(task, on_done, on_error)

    def _on_kusto_complete(self, incident_id: str, text: str) -> None:
        self.progress.stop()
        self.fetch_kusto_btn.config(state=tk.NORMAL)
        self._incident_text = text
        self.incident_text.set_html(_sanitize_html_colors(text))
        self.status_var.set(
            f"Loaded incident {incident_id} from Kusto "
            f"({len(text)} chars)"
        )

    def _on_kusto_error(self, exc: Exception) -> None:
        self.progress.stop()
        self.fetch_kusto_btn.config(state=tk.NORMAL)
        self.status_var.set("Kusto fetch failed.")
        messagebox.showerror(
            "Kusto Error", str(exc), parent=self.root,
        )

    def _extract_facts(self) -> None:
        if not self._incident_text:
            messagebox.showwarning("Warning", "Load an incident file first.")
            return

        self.extract_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Extracting facts via LLM...")

        ontology_nouns = self.store.load_ontology()

        def _update_status(msg: str) -> None:
            self.root.after(0, self.status_var.set, msg)

        def do_extract():
            settings = self.settings_mgr.load()
            extractor = FactExtractor(
                endpoint=settings["endpoint"],
                deployment=settings["deployment"],
                api_version=settings["api_version"],
            )
            return extractor.extract(
                self._incident_text, ontology_nouns, on_status=_update_status,
            )

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

        # Compute which facts are used by rule conditions
        self._used_fact_indices = facts_used_by_rules(
            self._pending_facts, self._pending_rules)

        # Populate facts tree
        self.facts_tree.delete(*self.facts_tree.get_children())
        for i, row in enumerate(facts_to_rows(self._pending_facts)):
            tags = ("used",) if i in self._used_fact_indices else ()
            self.facts_tree.insert("", tk.END, iid=str(i), values=(
                row["noun"], row["instance"], row["property"],
                row["operator"], row["value"], row["status"],
                row["scope"],
            ), tags=tags)

        # Populate rules tree
        self.rules_tree.delete(*self.rules_tree.get_children())
        for i, row in enumerate(rules_to_rows(self._pending_rules)):
            self.rules_tree.insert("", tk.END, iid=str(i), values=(
                row["rule_id"], row["type"], row["conditions"],
                row["then"], row["else"],
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

    def _confirm_used_facts(self) -> None:
        """Confirm only facts that are referenced by rule conditions (bold)."""
        used = getattr(self, "_used_fact_indices", set())
        for idx in used:
            self._pending_facts[idx].status = "confirmed"
            vals = list(self.facts_tree.item(str(idx), "values"))
            vals[5] = "confirmed"
            self.facts_tree.item(str(idx), values=vals)

    def _set_fact_scope(self, scope: str) -> None:
        """Set the scope ('rule' or 'context') for selected facts."""
        selected = self.facts_tree.selection()
        for iid in selected:
            idx = int(iid)
            self._pending_facts[idx].scope = scope
            vals = list(self.facts_tree.item(iid, "values"))
            vals[6] = scope
            self.facts_tree.item(iid, values=vals)

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
        )
        self.store.save_incident(incident)

        # Filter and save rules — only "rule" scope facts drive rule matching
        rule_facts = [f for f in confirmed_facts if f.scope == "rule"]
        existing_rules = self.store.list_rules()
        gen = RuleGenerator(existing_rules)
        filtered = gen.filter_rules(self._pending_rules, rule_facts)

        for rule in filtered:
            rule.rule_id = self.store.next_rule_id()
            rule.sources = [incident_id]
            self.store.save_rule(rule)

        # GAP detection
        detector = GapDetector(existing_rules)
        gaps = detector.detect_gaps(
            confirmed_facts, filtered, None, incident_id)
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
        cols = ("rule_id", "status", "type", "conditions", "then", "else")
        self.kb_rules_tree = ttk.Treeview(rules_frame, columns=cols,
                                          show="headings", height=15)
        for col in cols:
            self.kb_rules_tree.heading(col, text=col.title())
        self.kb_rules_tree.column("rule_id", width=80)
        self.kb_rules_tree.column("status", width=90)
        self.kb_rules_tree.column("type", width=80)
        self.kb_rules_tree.column("conditions", width=300)
        self.kb_rules_tree.column("then", width=200)
        self.kb_rules_tree.column("else", width=200)
        self.kb_rules_tree.pack(fill=tk.BOTH, expand=True, padx=5)
        self.kb_rules_tree.bind("<Double-1>", self._on_kb_rules_double_click)

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
                row["conditions"], row["then"], row["else"],
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

    # ── Double-click detail views ─────────────────────────────

    def _on_facts_double_click(self, event) -> None:
        iid = self.facts_tree.identify_row(event.y)
        if not iid:
            return
        idx = int(iid)
        if 0 <= idx < len(self._pending_facts):
            fact = self._pending_facts[idx]
            detail = (
                f"Noun:      {fact.noun}\n"
                f"Instance:  {fact.instance}\n"
                f"Property:  {fact.property}\n"
                f"Operator:  {fact.operator}\n"
                f"Value:     {fact.value}\n"
                f"Status:    {fact.status}\n"
                f"Scope:     {fact.scope}"
            )
            _show_detail_dialog(self.root, "Fact Detail", detail)

    def _on_rules_double_click(self, event) -> None:
        iid = self.rules_tree.identify_row(event.y)
        if not iid:
            return
        idx = int(iid)
        if 0 <= idx < len(self._pending_rules):
            rule = self._pending_rules[idx]
            _show_rule_detail(self.root, rule)

    def _on_kb_rules_double_click(self, event) -> None:
        iid = self.kb_rules_tree.identify_row(event.y)
        if not iid:
            return
        vals = self.kb_rules_tree.item(iid, "values")
        if not vals:
            return
        detail = (
            f"Rule ID:     {vals[0]}\n"
            f"Status:      {vals[1]}\n"
            f"Type:        {vals[2]}\n"
            f"Conditions:  {vals[3]}\n"
            f"Then:        {vals[4]}\n"
            f"Else:        {vals[5]}"
        )
        _show_detail_dialog(self.root, f"Rule {vals[0]}", detail)

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


def _show_detail_dialog(parent: tk.Tk, title: str, text: str) -> None:
    """Show a read-only detail dialog centered over the parent window."""
    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.transient(parent)

    dlg_w, dlg_h = 600, 400
    parent.update_idletasks()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    x = px + (pw - dlg_w) // 2
    y = py + (ph - dlg_h) // 2
    dlg.geometry(f"{dlg_w}x{dlg_h}+{x}+{y}")

    txt = tk.Text(dlg, wrap=tk.WORD, padx=10, pady=10)
    scroll = ttk.Scrollbar(dlg, command=txt.yview)
    txt.config(yscrollcommand=scroll.set)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    txt.pack(fill=tk.BOTH, expand=True)
    txt.insert("1.0", text)
    txt.config(state=tk.DISABLED)

    ttk.Button(dlg, text="Close", command=dlg.destroy).pack(pady=5)
    dlg.focus_set()


def _show_rule_detail(parent: tk.Tk, rule) -> None:
    """Show full rule details in a dialog."""
    from ees.gui.adapters import _then_display

    cond_parts = []
    for item in rule.conditions.items:
        cond_parts.append(
            f"  {item.noun}({item.instance}).{item.property} "
            f"{item.operator} {item.value}"
        )
    cond_str = f" {rule.conditions.logic}\n".join(cond_parts) or "(none)"

    then_str = _then_display(rule.then)

    detail = (
        f"Rule ID:     {rule.rule_id}\n"
        f"Status:      {rule.status}\n"
        f"Sources:     {', '.join(rule.sources) if rule.sources else '(none)'}\n"
        f"\nConditions ({rule.conditions.logic}):\n{cond_str}\n"
        f"\nThen:        {then_str}\n"
    )
    if rule.else_:
        detail += f"Else:        {_then_display(rule.else_)}\n"

    _show_detail_dialog(parent, f"Rule {rule.rule_id}", detail)


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

    # v2: Group outputs by kind with branch info
    outputs = display.get("outputs", [])
    cs = [o for o in outputs if o["kind"] == "CHANGE_STATE"]
    ro = [o for o in outputs if o["kind"] == "RULED_OUT"]
    gaps = [o for o in outputs if o["kind"] == "GAP"]

    if cs:
        lines.append(f"\nCHANGE_STATE ({len(cs)}):")
        for o in cs:
            branch = f" ({o['branch'].upper()})" if o["branch"] != "then" else ""
            lines.append(f"  \u2713 {o['rule_id']}: {o['description']}{branch}")

    if ro:
        lines.append(f"\nRULED_OUT ({len(ro)}):")
        for o in ro:
            branch = f" ({o['branch'].upper()})" if o["branch"] != "then" else ""
            lines.append(f"  \u2717 {o['rule_id']}: {o['description']}{branch}")

    if gaps:
        lines.append(f"\nGAP ({len(gaps)}):")
        for o in gaps:
            branch = f" ({o['branch'].upper()})" if o["branch"] != "then" else ""
            lines.append(f"  ? {o['rule_id']}: {o['description']}{branch}")

    lines.append(f"\nSummary: {total_rules} rules evaluated, "
                 f"{len(display['fired_rules'])} fired, "
                 f"{len(cs)} change_state, "
                 f"{len(ro)} ruled_out, "
                 f"{len(gaps)} gaps")
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
