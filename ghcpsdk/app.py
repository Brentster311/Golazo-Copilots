"""
Copilot SDK Tkinter Chat App (ghcp-0001)

A desktop chat application that integrates with the GitHub Copilot SDK
to send prompts and display streamed responses in real-time.

Requirements:
  - Python 3.9+
  - github-copilot-sdk (pip install github-copilot-sdk)
  - GitHub Copilot CLI installed and authenticated (copilot --version)
"""

import asyncio
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from enum import Enum

# ---------------------------------------------------------------------------
# Async bridge: run an asyncio event loop in a background thread so that
# the Tkinter main loop stays responsive.
# ---------------------------------------------------------------------------

class AsyncBridge:
    """Manages an asyncio event loop running on a dedicated daemon thread."""

    def __init__(self):
        self.loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    def start(self):
        self.loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_coroutine(self, coro):
        """Schedule a coroutine on the background loop. Returns a concurrent.futures.Future."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)


# ---------------------------------------------------------------------------
# Copilot Chat Application
# ---------------------------------------------------------------------------

class CopilotChatApp:
    """Tkinter GUI that communicates with GitHub Copilot via the Python SDK."""

    # -- Appearance constants ------------------------------------------------
    BG_COLOR = "#1e1e2e"
    FG_COLOR = "#cdd6f4"
    INPUT_BG = "#313244"
    INPUT_FG = "#cdd6f4"
    USER_COLOR = "#89b4fa"
    ASSISTANT_COLOR = "#a6e3a1"
    ERROR_COLOR = "#f38ba8"
    SYSTEM_COLOR = "#6c7086"
    BUTTON_BG = "#89b4fa"
    BUTTON_FG = "#1e1e2e"
    FONT_FAMILY = "Consolas"

    def __init__(self):
        # Async plumbing
        self._bridge = AsyncBridge()
        self._bridge.start()

        # SDK objects (created lazily on first send)
        self._client = None
        self._session = None
        self._is_connecting = False
        self._is_sending = False

        # Build the UI
        self._build_ui()

    # -- UI construction -----------------------------------------------------

    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("Copilot Chat — GitHub Copilot SDK")
        self.root.geometry("780x620")
        self.root.minsize(500, 400)
        self.root.configure(bg=self.BG_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Try to set a dark title-bar on Windows
        try:
            from ctypes import windll, byref, c_int
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                byref(c_int(1)), 4
            )
        except Exception:
            pass

        # --- Header ---
        header = tk.Frame(self.root, bg=self.BG_COLOR)
        header.pack(fill=tk.X, padx=12, pady=(10, 0))

        tk.Label(
            header, text="🤖 Copilot Chat",
            font=(self.FONT_FAMILY, 16, "bold"),
            bg=self.BG_COLOR, fg=self.FG_COLOR,
        ).pack(side=tk.LEFT)

        self._status_label = tk.Label(
            header, text="● Disconnected",
            font=(self.FONT_FAMILY, 10),
            bg=self.BG_COLOR, fg=self.SYSTEM_COLOR,
        )
        self._status_label.pack(side=tk.RIGHT)

        # --- Model selector ---
        model_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        model_frame.pack(fill=tk.X, padx=12, pady=(6, 0))

        tk.Label(
            model_frame, text="Model:",
            font=(self.FONT_FAMILY, 10),
            bg=self.BG_COLOR, fg=self.SYSTEM_COLOR,
        ).pack(side=tk.LEFT)

        self._model_var = tk.StringVar(value="gpt-4.1")
        model_combo = ttk.Combobox(
            model_frame, textvariable=self._model_var, width=28,
            values=["gpt-4.1", "gpt-5", "claude-sonnet-4.5", "o4-mini"],
            state="readonly",
        )
        model_combo.pack(side=tk.LEFT, padx=(6, 0))

        # --- Chat display ---
        self._chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=(self.FONT_FAMILY, 11),
            bg=self.BG_COLOR,
            fg=self.FG_COLOR,
            insertbackground=self.FG_COLOR,
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10,
        )
        self._chat_display.pack(fill=tk.BOTH, expand=True, padx=12, pady=(8, 0))

        # Tag styles for different message roles
        self._chat_display.tag_configure("user", foreground=self.USER_COLOR, font=(self.FONT_FAMILY, 11, "bold"))
        self._chat_display.tag_configure("assistant", foreground=self.ASSISTANT_COLOR)
        self._chat_display.tag_configure("error", foreground=self.ERROR_COLOR)
        self._chat_display.tag_configure("system", foreground=self.SYSTEM_COLOR, font=(self.FONT_FAMILY, 10, "italic"))

        # --- Input bar ---
        input_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        input_frame.pack(fill=tk.X, padx=12, pady=10)

        self._input_entry = tk.Entry(
            input_frame,
            font=(self.FONT_FAMILY, 12),
            bg=self.INPUT_BG,
            fg=self.INPUT_FG,
            insertbackground=self.INPUT_FG,
            relief=tk.FLAT,
            borderwidth=8,
        )
        self._input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self._input_entry.bind("<Return>", lambda e: self._on_send())
        self._input_entry.focus_set()

        self._send_btn = tk.Button(
            input_frame, text="Send",
            font=(self.FONT_FAMILY, 11, "bold"),
            bg=self.BUTTON_BG, fg=self.BUTTON_FG,
            activebackground="#74c7ec", activeforeground=self.BUTTON_FG,
            relief=tk.FLAT, padx=16, pady=4,
            command=self._on_send,
        )
        self._send_btn.pack(side=tk.RIGHT, padx=(8, 0))

        # Welcome message
        self._append_message(
            "system",
            "Welcome! Type a message and press Send (or Enter) to chat with GitHub Copilot.\n"
            "Make sure the Copilot CLI is installed and authenticated.\n",
        )

    # -- Chat display helpers -----------------------------------------------

    def _append_message(self, role: str, text: str, *, newline: bool = True):
        """Append text to the chat display (must be called from the main thread)."""
        self._chat_display.configure(state=tk.NORMAL)
        prefix = {"user": "You: ", "assistant": "Copilot: ", "error": "Error: ", "system": ""}.get(role, "")
        tag = role
        if prefix:
            self._chat_display.insert(tk.END, prefix, tag)
        self._chat_display.insert(tk.END, text + ("\n\n" if newline else ""), tag if role != "user" else "")
        self._chat_display.configure(state=tk.DISABLED)
        self._chat_display.see(tk.END)

    def _append_delta(self, text: str):
        """Append a streaming delta chunk (no newline, assistant style)."""
        self._chat_display.configure(state=tk.NORMAL)
        self._chat_display.insert(tk.END, text, "assistant")
        self._chat_display.configure(state=tk.DISABLED)
        self._chat_display.see(tk.END)

    def _finish_assistant_message(self):
        """Add trailing newlines after a streamed response completes."""
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

        self.root.after(0, self._set_status, "● Connecting…", "#fab387")
        self._is_connecting = True

        try:
            self._client = CopilotClient()
            await self._client.start()

            self._session = await self._client.create_session({
                "model": self._model_var.get(),
                "streaming": True,
            })

            # Register the event handler for streaming
            self._session.on(self._on_session_event)

            self.root.after(0, self._set_status, "● Connected", self.ASSISTANT_COLOR)
        except Exception as exc:
            self.root.after(0, self._set_status, "● Connection failed", self.ERROR_COLOR)
            self.root.after(0, self._append_message, "error", f"Failed to connect: {exc}")
            self._client = None
            self._session = None
            raise
        finally:
            self._is_connecting = False

    def _on_session_event(self, event):
        """Handle SDK session events — called from the async thread."""
        etype = event.type.value if hasattr(event.type, "value") else str(event.type)

        if etype == "assistant.message_delta":
            delta = event.data.delta_content or ""
            if delta:
                self.root.after(0, self._append_delta, delta)

        elif etype == "assistant.message":
            # Final message arrived — finish the visual block
            self.root.after(0, self._finish_assistant_message)

        elif etype == "session.idle":
            self.root.after(0, self._on_response_complete)

    def _on_response_complete(self):
        """Re-enable input after the response finishes."""
        self._is_sending = False
        self._set_input_enabled(True)
        self._input_entry.focus_set()

    # -- Send message --------------------------------------------------------

    def _on_send(self):
        prompt = self._input_entry.get().strip()
        if not prompt or self._is_sending or self._is_connecting:
            return

        self._input_entry.delete(0, tk.END)
        self._append_message("user", prompt)
        self._is_sending = True
        self._set_input_enabled(False)

        # Show the "Copilot: " prefix before deltas arrive
        self._chat_display.configure(state=tk.NORMAL)
        self._chat_display.insert(tk.END, "Copilot: ", "assistant")
        self._chat_display.configure(state=tk.DISABLED)

        self._bridge.run_coroutine(self._send_prompt(prompt))

    async def _send_prompt(self, prompt: str):
        try:
            await self._ensure_connected()
            await self._session.send({"prompt": prompt})
        except Exception as exc:
            self.root.after(0, self._finish_assistant_message)
            self.root.after(0, self._append_message, "error", str(exc))
            self.root.after(0, self._on_response_complete)

    # -- Shutdown ------------------------------------------------------------

    def _on_close(self):
        """Gracefully shut down the SDK then destroy the window."""
        self._set_status("● Shutting down…", "#fab387")

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
        self.root.destroy()

    # -- Run -----------------------------------------------------------------

    def run(self):
        self.root.mainloop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = CopilotChatApp()
    app.run()
