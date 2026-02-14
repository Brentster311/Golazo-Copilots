"""Copilot chat side panel for SFI Reporter.

Provides an AsyncBridge (background asyncio event loop) and a CopilotPanel
(tk.Frame) that integrates with the GitHub Copilot SDK for streaming chat.

The panel matches the system/light theme of SFI Reporter.
"""
import asyncio
import logging
import re
import threading
import tkinter as tk
import webbrowser
from tkinter import scrolledtext, ttk

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# AsyncBridge: run asyncio on a background daemon thread
# ---------------------------------------------------------------------------

class AsyncBridge:
    """Manages an asyncio event loop running on a dedicated daemon thread."""

    def __init__(self):
        self.loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    def start(self):
        """Start the background event loop."""
        self.loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_coroutine(self, coro):
        """Schedule a coroutine on the background loop.

        Returns a concurrent.futures.Future.
        """
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        """Stop the background loop."""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)


# ---------------------------------------------------------------------------
# CopilotPanel: side-panel chat UI
# ---------------------------------------------------------------------------

class CopilotPanel(tk.Frame):
    """Right-side chat panel powered by the GitHub Copilot SDK.

    Args:
        parent: The parent Tk widget.
        app: The SFIReporterApp instance (provides live data access).
        on_close: Callback invoked when the user clicks the X close button.
    """

    # System/light theme colours (matches SFI Reporter)
    BG_COLOR = "#f0f0f0"
    FG_COLOR = "#1e1e1e"
    INPUT_BG = "#ffffff"
    CHAT_BG = "#ffffff"
    USER_COLOR = "#0066cc"
    ASSISTANT_COLOR = "#1a7f37"
    ERROR_COLOR = "#cf222e"
    SYSTEM_COLOR = "#656d76"
    HEADER_BG = "#e1e4e8"

    def __init__(self, parent, *, app=None, on_close):
        super().__init__(parent, bg=self.BG_COLOR)
        self._on_close = on_close
        self._app = app

        # Async plumbing
        self._bridge = AsyncBridge()
        self._bridge.start()

        # SDK objects (created lazily)
        self._client = None
        self._session = None
        self._is_connecting = False
        self._is_sending = False
        self._got_content = False       # session-level: any turn had content
        self._turn_has_content = False   # per-turn: current turn has content
        self._turn_timeout_id = None    # Tk after-id for turn timeout

        self._build_ui()

    # -- UI -----------------------------------------------------------------

    def _build_ui(self):
        # Header bar
        header = tk.Frame(self, bg=self.HEADER_BG)
        header.pack(fill=tk.X)

        tk.Label(
            header, text="\U0001f916 Copilot Chat",
            font=("Segoe UI", 11, "bold"),
            bg=self.HEADER_BG, fg=self.FG_COLOR,
        ).pack(side=tk.LEFT, padx=8, pady=4)

        self._close_btn = tk.Button(
            header, text="\u2715", font=("Segoe UI", 10),
            bg=self.HEADER_BG, fg=self.FG_COLOR,
            relief=tk.FLAT, borderwidth=0,
            command=self._on_close,
        )
        self._close_btn.pack(side=tk.RIGHT, padx=4, pady=2)

        # Status label
        self._status_label = tk.Label(
            self, text="\u25cf Disconnected",
            font=("Segoe UI", 9), bg=self.BG_COLOR, fg=self.SYSTEM_COLOR,
        )
        self._status_label.pack(fill=tk.X, padx=8, pady=(4, 0))

        # Model selector
        model_frame = tk.Frame(self, bg=self.BG_COLOR)
        model_frame.pack(fill=tk.X, padx=8, pady=(4, 0))

        tk.Label(
            model_frame, text="Model:",
            font=("Segoe UI", 9), bg=self.BG_COLOR, fg=self.SYSTEM_COLOR,
        ).pack(side=tk.LEFT)

        self._model_var = tk.StringVar(value="gpt-5")
        model_combo = ttk.Combobox(
            model_frame, textvariable=self._model_var, width=22,
            values=["gpt-4.1", "gpt-5", "claude-sonnet-4.5", "o4-mini"],
            state="readonly",
        )
        model_combo.pack(side=tk.LEFT, padx=(4, 0))

        # Chat display
        self._chat_display = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, state=tk.DISABLED,
            font=("Segoe UI", 10),
            bg=self.CHAT_BG, fg=self.FG_COLOR,
            insertbackground=self.FG_COLOR,
            borderwidth=1, relief=tk.SUNKEN,
            padx=8, pady=6,
        )
        self._chat_display.pack(fill=tk.BOTH, expand=True, padx=8, pady=(6, 0))

        # Tag styles — base roles
        self._chat_display.tag_configure("user", foreground=self.USER_COLOR,
                                         font=("Segoe UI", 10, "bold"))
        self._chat_display.tag_configure("assistant", foreground=self.ASSISTANT_COLOR)
        self._chat_display.tag_configure("error", foreground=self.ERROR_COLOR)
        self._chat_display.tag_configure("system", foreground=self.SYSTEM_COLOR,
                                         font=("Segoe UI", 9, "italic"))

        # Tag styles — Markdown
        self._chat_display.tag_configure("md_h1", foreground=self.ASSISTANT_COLOR,
                                         font=("Segoe UI", 14, "bold"))
        self._chat_display.tag_configure("md_h2", foreground=self.ASSISTANT_COLOR,
                                         font=("Segoe UI", 12, "bold"))
        self._chat_display.tag_configure("md_h3", foreground=self.ASSISTANT_COLOR,
                                         font=("Segoe UI", 11, "bold"))
        self._chat_display.tag_configure("md_h4", foreground=self.ASSISTANT_COLOR,
                                         font=("Segoe UI", 10, "bold"))
        self._chat_display.tag_configure("md_bold", foreground=self.ASSISTANT_COLOR,
                                         font=("Segoe UI", 10, "bold"))
        self._chat_display.tag_configure("md_italic", foreground=self.ASSISTANT_COLOR,
                                         font=("Segoe UI", 10, "italic"))
        self._chat_display.tag_configure("md_code", foreground="#953800",
                                         background="#eff1f3",
                                         font=("Consolas", 9))
        self._chat_display.tag_configure("md_code_block", foreground="#1f2328",
                                         background="#f6f8fa",
                                         font=("Consolas", 9),
                                         lmargin1=20, lmargin2=20, rmargin=10)
        self._chat_display.tag_configure("md_bullet", foreground=self.ASSISTANT_COLOR,
                                         lmargin1=16, lmargin2=28)
        self._chat_display.tag_configure("md_link", foreground="#0969da",
                                         underline=True,
                                         font=("Segoe UI", 10))

        # Track link tag counter for unique click bindings
        self._link_counter = 0

        # Input bar
        input_frame = tk.Frame(self, bg=self.BG_COLOR)
        input_frame.pack(fill=tk.X, padx=8, pady=6)

        self._input_entry = tk.Entry(
            input_frame, font=("Segoe UI", 10),
            bg=self.INPUT_BG, fg=self.FG_COLOR,
            insertbackground=self.FG_COLOR,
            relief=tk.SUNKEN, borderwidth=1,
        )
        self._input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self._input_entry.bind("<Return>", lambda e: self._on_send())

        self._stop_btn = ttk.Button(
            input_frame, text="Stop", command=self._on_stop,
        )
        self._stop_btn.pack(side=tk.RIGHT, padx=(4, 0))
        self._stop_btn.configure(state=tk.DISABLED)

        self._send_btn = ttk.Button(
            input_frame, text="Send", command=self._on_send,
        )
        self._send_btn.pack(side=tk.RIGHT, padx=(4, 0))

        # Welcome message
        self._append_message(
            "system",
            "Type a message and press Send to chat with GitHub Copilot.\n"
            "Ensure the Copilot CLI is installed and authenticated.\n",
        )

    # -- URL regex (used for linkification) ---------------------------------
    _URL_RE = re.compile(r"(https?://[^\s)>\]]+)")

    # -- Chat display helpers -----------------------------------------------

    def _append_message(self, role: str, text: str, *, newline: bool = True):
        """Append text to the chat display (main thread only)."""
        self._chat_display.configure(state=tk.NORMAL)
        prefix = {
            "user": "You: ", "assistant": "Copilot: ",
            "error": "Error: ", "system": "",
        }.get(role, "")
        tag = role
        if prefix:
            self._chat_display.insert(tk.END, prefix, tag)
        # Insert text with URLs linkified
        content = text + ("\n\n" if newline else "")
        display_tag = tag if role != "user" else ""
        self._insert_with_links(content, display_tag)
        self._chat_display.configure(state=tk.DISABLED)
        self._chat_display.see(tk.END)

    def _append_delta(self, text: str):
        """Append a streaming delta chunk."""
        self._chat_display.configure(state=tk.NORMAL)
        self._chat_display.insert(tk.END, text, "assistant")
        self._chat_display.configure(state=tk.DISABLED)
        self._chat_display.see(tk.END)

    def _finish_assistant_message(self):
        """Re-render the streamed response as Markdown, then add trailing newlines."""
        self._chat_display.configure(state=tk.NORMAL)
        # Find the start of the current assistant message content
        try:
            mark_pos = self._chat_display.index("md_msg_start")
        except tk.TclError:
            mark_pos = None

        if mark_pos:
            raw = self._chat_display.get(mark_pos, tk.END).rstrip("\n")
            if raw:
                self._chat_display.delete(mark_pos, tk.END)
                self._render_markdown(raw)
            self._chat_display.mark_unset("md_msg_start")

        self._chat_display.insert(tk.END, "\n\n")
        self._chat_display.configure(state=tk.DISABLED)
        self._chat_display.see(tk.END)

    # -- Markdown renderer ---------------------------------------------------

    def _render_markdown(self, text: str):
        """Insert *text* into the chat display with Markdown formatting.

        Handles: headings, bold, italic, inline code, fenced code blocks,
        bullet / numbered lists.  Runs synchronously on the Tk thread.
        """
        w = self._chat_display  # shorthand

        # Split fenced code blocks from the rest
        parts = re.split(r"(```[^\n]*\n.*?```)", text, flags=re.DOTALL)

        for part in parts:
            # Fenced code block
            if part.startswith("```") and part.endswith("```"):
                # Strip the ``` markers and optional language label
                inner = re.sub(r"^```[^\n]*\n?", "", part)
                inner = re.sub(r"\n?```$", "", inner)
                w.insert(tk.END, inner + "\n", "md_code_block")
                continue

            # Process line-by-line for block-level elements
            for line in part.split("\n"):
                stripped = line.strip()
                if not stripped:
                    w.insert(tk.END, "\n")
                    continue

                # Headings
                hm = re.match(r"^(#{1,4})\s+(.*)", stripped)
                if hm:
                    level = len(hm.group(1))
                    tag = f"md_h{level}"
                    self._insert_inline_md(hm.group(2), tag)
                    w.insert(tk.END, "\n")
                    continue

                # Bullet lists (- or *)
                bm = re.match(r"^[-*]\s+(.*)", stripped)
                if bm:
                    w.insert(tk.END, "\u2022 ", "md_bullet")
                    self._insert_inline_md(bm.group(1), "md_bullet")
                    w.insert(tk.END, "\n")
                    continue

                # Numbered lists
                nm = re.match(r"^(\d+)\.\s+(.*)", stripped)
                if nm:
                    w.insert(tk.END, f"{nm.group(1)}. ", "md_bullet")
                    self._insert_inline_md(nm.group(2), "md_bullet")
                    w.insert(tk.END, "\n")
                    continue

                # Plain paragraph line
                self._insert_inline_md(stripped, "assistant")
                w.insert(tk.END, "\n")

    def _insert_inline_md(self, text: str, base_tag: str):
        """Insert a line of text, rendering **bold**, *italic*, and `code`."""
        w = self._chat_display
        # Pattern: **bold**, *italic*, `code`
        pattern = re.compile(
            r"(\*\*(.+?)\*\*"   # **bold**
            r"|\*(.+?)\*"       # *italic*
            r"|`([^`]+)`)"      # `code`
        )
        last = 0
        for m in pattern.finditer(text):
            # Text before this match
            if m.start() > last:
                w.insert(tk.END, text[last:m.start()], base_tag)
            if m.group(2):      # bold
                w.insert(tk.END, m.group(2), "md_bold")
            elif m.group(3):    # italic
                w.insert(tk.END, m.group(3), "md_italic")
            elif m.group(4):    # inline code
                w.insert(tk.END, m.group(4), "md_code")
            last = m.end()
        # Remaining text after last match
        if last < len(text):
            w.insert(tk.END, text[last:], base_tag)

    def _insert_with_links(self, text: str, tag: str):
        """Insert text, converting any URLs into clickable links."""
        w = self._chat_display
        last = 0
        for m in self._URL_RE.finditer(text):
            if m.start() > last:
                w.insert(tk.END, text[last:m.start()], tag)
            self._insert_link(m.group(1))
            last = m.end()
        if last < len(text):
            w.insert(tk.END, text[last:], tag)

    def _insert_link(self, url: str):
        """Insert a single clickable URL into the chat display."""
        w = self._chat_display
        self._link_counter += 1
        link_tag = f"link_{self._link_counter}"
        w.tag_configure(link_tag, foreground="#0969da", underline=True,
                        font=("Segoe UI", 10))
        w.insert(tk.END, url, link_tag)
        # Bind click to open in browser
        _url = url  # capture for closure
        w.tag_bind(link_tag, "<Button-1>", lambda e, u=_url: self._on_link_click(u))
        w.tag_bind(link_tag, "<Enter>",
                   lambda e: w.configure(cursor="hand2"))
        w.tag_bind(link_tag, "<Leave>",
                   lambda e: w.configure(cursor=""))

    def _on_link_click(self, url: str):
        """Open a URL in the default browser."""
        try:
            webbrowser.open(url)
        except Exception as exc:
            logger.warning("Failed to open URL %s: %s", url, exc)

    def _set_status(self, text: str, color: str | None = None):
        self._status_label.configure(text=text, fg=color or self.SYSTEM_COLOR)

    def _on_stop(self):
        """Abort the current in-flight Copilot request."""
        if not self._is_sending or not self._session:
            return
        logger.info("User requested stop")
        self._cancel_turn_timeout()
        self._stop_btn.configure(state=tk.DISABLED)

        async def _do_abort():
            try:
                await self._session.abort()
            except Exception as exc:
                logger.warning("Abort failed: %s", exc)
            self.after(0, self._on_response_complete)

        self._bridge.run_coroutine(_do_abort())

    def _set_input_enabled(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self._input_entry.configure(state=state)
        self._send_btn.configure(state=state)

    # -- SDK lifecycle -------------------------------------------------------

    async def _ensure_connected(self):
        """Lazily create the CopilotClient and session."""
        if self._session is not None:
            return

        from copilot import CopilotClient

        self.after(0, self._set_status, "\u25cf Connecting\u2026", "#b5651d")
        self._is_connecting = True

        try:
            self._client = CopilotClient()
            await self._client.start()

            # Build session config with tools + system message when app is available
            session_cfg: dict = {
                "model": self._model_var.get(),
                "streaming": True,
            }
            if self._app is not None:
                from sfi_reporter.copilot_tools import build_tools, SYSTEM_MESSAGE
                session_cfg["tools"] = build_tools(self._app)
                session_cfg["system_message"] = SYSTEM_MESSAGE

            self._session = await self._client.create_session(session_cfg)
            self._session.on(self._on_session_event)

            self.after(0, self._set_status, "\u25cf Connected", self.ASSISTANT_COLOR)
        except Exception as exc:
            self.after(0, self._set_status, "\u25cf Connection failed", self.ERROR_COLOR)
            self.after(0, self._append_message, "error", f"Failed to connect: {exc}")
            self._client = None
            self._session = None
            raise
        finally:
            self._is_connecting = False

    def _on_session_event(self, event):
        """Handle SDK session events (called from async thread)."""
        etype = event.type.value if hasattr(event.type, "value") else str(event.type)
        logger.debug("Copilot event: type=%s", etype)

        if etype == "assistant.turn_start":
            self._turn_has_content = False  # reset per-turn flag
            self.after(0, self._set_status, "\u25cf Thinking\u2026", "#b5651d")
            # Start a turn timeout — if no content in 90s, force-complete
            self._cancel_turn_timeout()
            self._turn_timeout_id = self.after(
                90_000, self._on_turn_timeout,
            )
        elif etype == "assistant.message_delta":
            delta = getattr(event.data, "delta_content", None) or ""
            if delta:
                self._cancel_turn_timeout()  # content arriving, no timeout needed
                if not self._got_content:
                    self.after(0, self._set_status, "\u25cf Responding\u2026", self.ASSISTANT_COLOR)
                self._got_content = True
                self._turn_has_content = True
                self.after(0, self._append_delta, delta)
        elif etype == "assistant.message":
            # Full message — if streaming didn't deliver content, show it now
            content = getattr(event.data, "content", None) or ""
            if content and not self._turn_has_content:
                self._got_content = True
                self._turn_has_content = True
                self.after(0, self._append_delta, content)
            # Only close the message block if THIS turn actually wrote text;
            # tool-call-only turns have no content — don't add blank lines.
            if self._turn_has_content:
                self.after(0, self._finish_assistant_message)
        elif etype == "tool.execution_start":
            tool_name = getattr(event.data, "tool_name", None) or ""
            self.after(0, self._set_status, f"\u25cf Running tool: {tool_name}\u2026", "#b5651d")
        elif etype == "tool.execution_complete":
            self.after(0, self._set_status, "\u25cf Thinking\u2026", "#b5651d")
        elif etype == "assistant.turn_end":
            # Don't finalize here — with tool calls there are multiple
            # turns before the model is done.  Wait for session.idle.
            pass
        elif etype == "session.idle":
            self._cancel_turn_timeout()
            self.after(0, self._on_response_complete)
        elif etype == "session.error":
            msg = getattr(event.data, "message", None) or "Unknown session error"
            logger.error("Copilot session error: %s", msg)
            self.after(0, self._finish_assistant_message)
            self.after(0, self._append_message, "error", msg)
            self.after(0, self._on_response_complete)
        else:
            logger.debug("Unhandled Copilot event type: %s", etype)

    def _cancel_turn_timeout(self):
        """Cancel any pending turn-timeout callback."""
        if self._turn_timeout_id is not None:
            self.after_cancel(self._turn_timeout_id)
            self._turn_timeout_id = None

    def _on_turn_timeout(self):
        """Force-complete after 90 s of no content on a turn."""
        self._turn_timeout_id = None
        if not self._is_sending:
            return
        logger.warning("Turn timeout — forcing response completion")
        if not self._got_content:
            self._append_delta("(Response timed out — the model may be unable to answer. Try rephrasing.)")
            self._finish_assistant_message()
            self._got_content = True
        self._on_response_complete()

    def _on_response_complete(self):
        """Re-enable input after a response completes."""
        if not self._is_sending:
            return
        if not self._got_content:
            # No content was received — clean up the dangling "Copilot: " prefix
            self._append_delta("(no response)")
            self._finish_assistant_message()
        self._is_sending = False
        self._got_content = False
        self._stop_btn.configure(state=tk.DISABLED)
        self._set_status("\u25cf Connected", self.ASSISTANT_COLOR)
        self._set_input_enabled(True)
        self._input_entry.focus_set()

    # -- Send ----------------------------------------------------------------

    def _on_send(self):
        """Handle send button / Enter key."""
        prompt = self._input_entry.get().strip()
        if not prompt or self._is_sending or self._is_connecting:
            return

        self._input_entry.delete(0, tk.END)
        self._append_message("user", prompt)
        self._is_sending = True
        self._got_content = False
        self._set_input_enabled(False)
        self._stop_btn.configure(state=tk.NORMAL)
        self._set_status("\u25cf Thinking\u2026", "#b5651d")

        # Show prefix before deltas
        self._chat_display.configure(state=tk.NORMAL)
        self._chat_display.insert(tk.END, "Copilot: ", "assistant")
        self._chat_display.mark_set("md_msg_start", tk.INSERT)
        self._chat_display.mark_gravity("md_msg_start", tk.LEFT)
        self._chat_display.configure(state=tk.DISABLED)

        self._bridge.run_coroutine(self._send_prompt(prompt))

    async def _send_prompt(self, prompt: str):
        """Send a prompt to the Copilot session."""
        try:
            await self._ensure_connected()
            logger.debug("Sending prompt to Copilot session (model=%s):\n%s", self._model_var.get(), prompt)
            await self._session.send({"prompt": prompt})
            logger.debug("Prompt sent, awaiting events")
        except Exception as exc:
            logger.error("Error sending prompt: %s", exc)
            self._got_content = True  # prevent "(no response)" on top of error
            self.after(0, self._finish_assistant_message)
            self.after(0, self._append_message, "error", str(exc))
            self.after(0, self._on_response_complete)

    def send_analysis_prompt(self, prompt: str, *, kpi_label: str = "", sources_metadata=None):
        """Programmatically send a pre-built analysis prompt.

        Handles connection lifecycle and thread marshaling.  Safe to call
        from any thread — internally marshals to the Tk main thread.

        Args:
            prompt: The LLM prompt string.
            kpi_label: Display label for the KPI being analyzed.
            sources_metadata: Optional AnalysisResult with provenance data.
        """
        # Marshal to Tk main thread
        self.after(0, self._do_send_analysis, prompt, kpi_label, sources_metadata)

    def _do_send_analysis(self, prompt: str, kpi_label: str = "", sources_metadata=None):
        """Send analysis prompt on the Tk main thread."""
        if self._is_sending or self._is_connecting:
            self._append_message("system", "Please wait — a request is already in progress.")
            return

        # Show which KPI is being analyzed
        display = kpi_label or "KPI"
        self._append_message("user", f"\U0001f916 Analyze: {display}")

        # Show Sources provenance card before LLM response (SFI-035)
        if sources_metadata is not None:
            self._show_sources_card(sources_metadata)
            # Set docs_dir so read_fetched_doc tool knows where files are
            docs_dir = getattr(sources_metadata, "docs_dir", "")
            if docs_dir:
                from sfi_reporter.copilot_tools import set_current_docs_dir
                set_current_docs_dir(docs_dir)
        self._is_sending = True
        self._got_content = False
        self._set_input_enabled(False)
        self._stop_btn.configure(state=tk.NORMAL)
        self._set_status("\u25cf Analyzing\u2026", "#b5651d")

        # Show prefix before deltas
        self._chat_display.configure(state=tk.NORMAL)
        self._chat_display.insert(tk.END, "Copilot: ", "assistant")
        self._chat_display.mark_set("md_msg_start", tk.INSERT)
        self._chat_display.mark_gravity("md_msg_start", tk.LEFT)
        self._chat_display.configure(state=tk.DISABLED)

        self._bridge.run_coroutine(self._send_prompt(prompt))

    def _show_sources_card(self, result):
        """Render a Sources provenance card in the chat panel.

        Shows which URLs were extracted and their fetch status so the
        user can judge the trustworthiness of the LLM analysis.
        """
        try:
            from sfi_reporter.kpi_analyzer import format_sources_card
            card_text = format_sources_card(result)
            self._append_message("system", card_text)
        except Exception as exc:
            logger.warning("Failed to render sources card: %s", exc)

    # -- Cleanup -------------------------------------------------------------

    def destroy(self):
        """Shut down the SDK and bridge before destroying the widget."""
        async def _shutdown():
            try:
                if self._session:
                    await self._session.destroy()
                if self._client:
                    await self._client.stop()
            except Exception:
                pass

        if self._client:
            future = self._bridge.run_coroutine(_shutdown())
            try:
                future.result(timeout=5)
            except Exception:
                pass

        self._bridge.stop()
        super().destroy()
