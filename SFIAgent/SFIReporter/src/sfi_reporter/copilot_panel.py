"""Copilot chat side panel for SFI Reporter.

Provides an AsyncBridge (background asyncio event loop) and a CopilotPanel
(tk.Frame) that integrates with the GitHub Copilot SDK for streaming chat.

The panel matches the system/light theme of SFI Reporter.
"""
import asyncio
import logging
import threading
import tkinter as tk
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
        super().__init__(parent, bg=self.BG_COLOR, width=350)
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
        self._got_content = False

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

        self._model_var = tk.StringVar(value="gpt-4.1")
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

        # Tag styles
        self._chat_display.tag_configure("user", foreground=self.USER_COLOR,
                                         font=("Segoe UI", 10, "bold"))
        self._chat_display.tag_configure("assistant", foreground=self.ASSISTANT_COLOR)
        self._chat_display.tag_configure("error", foreground=self.ERROR_COLOR)
        self._chat_display.tag_configure("system", foreground=self.SYSTEM_COLOR,
                                         font=("Segoe UI", 9, "italic"))

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
        self._chat_display.insert(tk.END, text + ("\n\n" if newline else ""), tag if role != "user" else "")
        self._chat_display.configure(state=tk.DISABLED)
        self._chat_display.see(tk.END)

    def _append_delta(self, text: str):
        """Append a streaming delta chunk."""
        self._chat_display.configure(state=tk.NORMAL)
        self._chat_display.insert(tk.END, text, "assistant")
        self._chat_display.configure(state=tk.DISABLED)
        self._chat_display.see(tk.END)

    def _finish_assistant_message(self):
        """Add trailing newlines after a streamed response."""
        self._chat_display.configure(state=tk.NORMAL)
        self._chat_display.insert(tk.END, "\n\n")
        self._chat_display.configure(state=tk.DISABLED)
        self._chat_display.see(tk.END)

    def _set_status(self, text: str, color: str | None = None):
        self._status_label.configure(text=text, fg=color or self.SYSTEM_COLOR)

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
            self.after(0, self._set_status, "\u25cf Thinking\u2026", "#b5651d")
        elif etype == "assistant.message_delta":
            delta = getattr(event.data, "delta_content", None) or ""
            if delta:
                if not self._got_content:
                    self.after(0, self._set_status, "\u25cf Responding\u2026", self.ASSISTANT_COLOR)
                self._got_content = True
                self.after(0, self._append_delta, delta)
        elif etype == "assistant.message":
            # Full message — if streaming didn't deliver content, show it now
            content = getattr(event.data, "content", None) or ""
            if content and not self._got_content:
                self._got_content = True
                self.after(0, self._append_delta, content)
            # Only close the message block if we actually wrote text;
            # tool-call messages have no content and more turns follow.
            if self._got_content:
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
            self.after(0, self._on_response_complete)
        elif etype == "session.error":
            msg = getattr(event.data, "message", None) or "Unknown session error"
            logger.error("Copilot session error: %s", msg)
            self.after(0, self._finish_assistant_message)
            self.after(0, self._append_message, "error", msg)
            self.after(0, self._on_response_complete)
        else:
            logger.debug("Unhandled Copilot event type: %s", etype)

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
        self._set_status("\u25cf Thinking\u2026", "#b5651d")

        # Show prefix before deltas
        self._chat_display.configure(state=tk.NORMAL)
        self._chat_display.insert(tk.END, "Copilot: ", "assistant")
        self._chat_display.configure(state=tk.DISABLED)

        self._bridge.run_coroutine(self._send_prompt(prompt))

    async def _send_prompt(self, prompt: str):
        """Send a prompt to the Copilot session."""
        try:
            await self._ensure_connected()
            logger.debug("Sending prompt to Copilot session (model=%s)", self._model_var.get())
            await self._session.send({"prompt": prompt})
            logger.debug("Prompt sent, awaiting events")
        except Exception as exc:
            logger.error("Error sending prompt: %s", exc)
            self._got_content = True  # prevent "(no response)" on top of error
            self.after(0, self._finish_assistant_message)
            self.after(0, self._append_message, "error", str(exc))
            self.after(0, self._on_response_complete)

    def send_analysis_prompt(self, prompt: str):
        """Programmatically send a pre-built analysis prompt.

        Handles connection lifecycle and thread marshaling.  Safe to call
        from any thread — internally marshals to the Tk main thread.
        """
        # Marshal to Tk main thread
        self.after(0, self._do_send_analysis, prompt)

    def _do_send_analysis(self, prompt: str):
        """Send analysis prompt on the Tk main thread."""
        if self._is_sending or self._is_connecting:
            self._append_message("system", "Please wait — a request is already in progress.")
            return

        # Show analysis label instead of echoing the full prompt
        self._append_message("user", "\U0001f916 Analyze KPI")
        self._is_sending = True
        self._got_content = False
        self._set_input_enabled(False)
        self._set_status("\u25cf Analyzing\u2026", "#b5651d")

        # Show prefix before deltas
        self._chat_display.configure(state=tk.NORMAL)
        self._chat_display.insert(tk.END, "Copilot: ", "assistant")
        self._chat_display.configure(state=tk.DISABLED)

        self._bridge.run_coroutine(self._send_prompt(prompt))

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
