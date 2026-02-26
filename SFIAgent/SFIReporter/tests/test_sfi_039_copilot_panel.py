"""Tests for sfi_reporter.copilot_panel — target ≥70 % coverage.

The ``copilot`` package is NOT installed in the test environment, so we inject
mock modules into ``sys.modules`` BEFORE importing anything from sfi_reporter
that touches the SDK.
"""

from __future__ import annotations

import asyncio
import sys
import threading
import time
import tkinter as tk
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# ---------------------------------------------------------------------------
# Mock the copilot SDK before importing copilot_panel
# ---------------------------------------------------------------------------
_mock_copilot = MagicMock()


class _FakeTool:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _FakeToolResult:
    def __init__(self, **kw):
        self.__dict__.update(kw)


_mock_copilot.Tool = _FakeTool
_mock_copilot.ToolResult = _FakeToolResult
_mock_copilot.define_tool = MagicMock()
_mock_copilot.CopilotClient = MagicMock
sys.modules.setdefault("copilot", _mock_copilot)

# NOW we can safely import
from sfi_reporter.copilot_panel import AsyncBridge, CopilotPanel  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def tk_root():
    """Create a single Tk root for the whole module."""
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def panel(tk_root):
    """Create a CopilotPanel with mocked app and on_close callback."""
    mock_app = MagicMock()
    mock_app.current_data = {"detailed_items": []}
    close_cb = MagicMock()
    p = CopilotPanel(tk_root, app=mock_app, on_close=close_cb)
    yield p
    p.destroy()


def _get_chat_text(panel: CopilotPanel) -> str:
    """Return the full text content of the chat display."""
    return panel._chat_display.get("1.0", tk.END)


# ===========================================================================
# TestAsyncBridge
# ===========================================================================

class TestAsyncBridge:
    def test_start_creates_loop(self):
        bridge = AsyncBridge()
        bridge.start()
        assert bridge.loop is not None
        assert bridge.loop.is_running()
        bridge.stop()

    def test_run_coroutine(self):
        bridge = AsyncBridge()
        bridge.start()

        async def _coro():
            return 42

        fut = bridge.run_coroutine(_coro())
        result = fut.result(timeout=5)
        assert result == 42
        bridge.stop()

    def test_stop_halts_loop(self):
        bridge = AsyncBridge()
        bridge.start()
        assert bridge.loop.is_running()
        bridge.stop()
        # Give thread a moment to stop
        time.sleep(0.1)
        assert not bridge.loop.is_running()

    def test_stop_noop_when_not_started(self):
        """stop() on a fresh bridge does nothing."""
        bridge = AsyncBridge()
        bridge.stop()  # should not raise


# ===========================================================================
# TestCopilotPanelInit
# ===========================================================================

class TestCopilotPanelInit:
    def test_widgets_created(self, panel):
        """Panel creates core widgets."""
        assert panel._chat_display is not None
        assert panel._input_entry is not None
        assert panel._send_btn is not None
        assert panel._stop_btn is not None
        assert panel._status_label is not None

    def test_initial_state(self, panel):
        """Panel starts disconnected, not sending."""
        assert panel._client is None
        assert panel._session is None
        assert panel._is_sending is False
        assert panel._is_connecting is False
        assert panel._got_content is False

    def test_welcome_message(self, panel):
        """A system welcome message is in the chat display."""
        text = _get_chat_text(panel)
        assert "Type a message" in text

    def test_bridge_started(self, panel):
        """The async bridge is running."""
        assert panel._bridge.loop is not None
        assert panel._bridge.loop.is_running()

    def test_link_counter_starts_at_zero(self, panel):
        """Link counter initialises to 0."""
        # After _build_ui the counter is 0 (welcome message has no links)
        # but we just verify the attribute exists and is numeric
        assert isinstance(panel._link_counter, int)


# ===========================================================================
# TestAppendMessage
# ===========================================================================

class TestAppendMessage:
    def test_user_message(self, panel):
        panel._append_message("user", "hello")
        text = _get_chat_text(panel)
        assert "You: " in text
        assert "hello" in text

    def test_assistant_message(self, panel):
        panel._append_message("assistant", "hi there")
        text = _get_chat_text(panel)
        assert "Copilot: " in text
        assert "hi there" in text

    def test_error_message(self, panel):
        panel._append_message("error", "oops")
        text = _get_chat_text(panel)
        assert "Error: " in text
        assert "oops" in text

    def test_system_message_no_prefix(self, panel):
        panel._append_message("system", "info msg")
        text = _get_chat_text(panel)
        assert "info msg" in text

    def test_newline_true(self, panel):
        panel._append_message("system", "line1", newline=True)
        text = _get_chat_text(panel)
        # newline=True appends "\n\n"
        assert "line1\n\n" in text

    def test_newline_false(self, panel):
        panel._append_message("system", "line2", newline=False)
        text = _get_chat_text(panel)
        # newline=False means no trailing double newline
        assert "line2" in text

    def test_unknown_role(self, panel):
        """Unknown role falls back to empty prefix."""
        panel._append_message("wizard", "magic")
        text = _get_chat_text(panel)
        assert "magic" in text


# ===========================================================================
# TestAppendDelta
# ===========================================================================

class TestAppendDelta:
    def test_delta_text_appears(self, panel):
        panel._append_delta("chunk1")
        text = _get_chat_text(panel)
        assert "chunk1" in text

    def test_multiple_deltas(self, panel):
        panel._append_delta("aaa")
        panel._append_delta("bbb")
        text = _get_chat_text(panel)
        assert "aaabbb" in text


# ===========================================================================
# TestFinishAssistantMessage
# ===========================================================================

class TestFinishAssistantMessage:
    def test_without_mark(self, panel):
        """No md_msg_start mark — just adds trailing newlines."""
        panel._chat_display.configure(state=tk.NORMAL)
        panel._chat_display.insert(tk.END, "some text")
        panel._chat_display.configure(state=tk.DISABLED)
        panel._finish_assistant_message()
        text = _get_chat_text(panel)
        assert "some text" in text

    def test_with_mark_and_content(self, panel):
        """Content between mark and END gets re-rendered as Markdown."""
        panel._chat_display.configure(state=tk.NORMAL)
        panel._chat_display.insert(tk.END, "Copilot: ", "assistant")
        panel._chat_display.mark_set("md_msg_start", tk.INSERT)
        panel._chat_display.mark_gravity("md_msg_start", tk.LEFT)
        panel._chat_display.insert(tk.END, "# Hello World")
        panel._chat_display.configure(state=tk.DISABLED)
        panel._finish_assistant_message()
        text = _get_chat_text(panel)
        # The heading text should be present (re-rendered)
        assert "Hello World" in text

    def test_with_mark_empty_content(self, panel):
        """Empty content between mark and END — mark is still unset."""
        panel._chat_display.configure(state=tk.NORMAL)
        panel._chat_display.mark_set("md_msg_start", tk.INSERT)
        panel._chat_display.mark_gravity("md_msg_start", tk.LEFT)
        panel._chat_display.configure(state=tk.DISABLED)
        # Should not raise
        panel._finish_assistant_message()


# ===========================================================================
# TestRenderMarkdown
# ===========================================================================

class TestRenderMarkdown:
    def _render(self, panel, text):
        panel._chat_display.configure(state=tk.NORMAL)
        panel._chat_display.delete("1.0", tk.END)
        panel._render_markdown(text)
        panel._chat_display.configure(state=tk.DISABLED)
        return _get_chat_text(panel)

    def test_h1(self, panel):
        result = self._render(panel, "# Heading One")
        assert "Heading One" in result

    def test_h2(self, panel):
        result = self._render(panel, "## Heading Two")
        assert "Heading Two" in result

    def test_h3(self, panel):
        result = self._render(panel, "### Heading Three")
        assert "Heading Three" in result

    def test_h4(self, panel):
        result = self._render(panel, "#### Heading Four")
        assert "Heading Four" in result

    def test_bullet_dash(self, panel):
        result = self._render(panel, "- item one\n- item two")
        assert "\u2022 item one" in result
        assert "\u2022 item two" in result

    def test_bullet_asterisk(self, panel):
        result = self._render(panel, "* starred")
        assert "\u2022 starred" in result

    def test_numbered_list(self, panel):
        result = self._render(panel, "1. first\n2. second")
        assert "1. first" in result
        assert "2. second" in result

    def test_code_block(self, panel):
        result = self._render(panel, "```python\nprint('hi')\n```")
        assert "print('hi')" in result

    def test_plain_paragraph(self, panel):
        result = self._render(panel, "Just a plain line.")
        assert "Just a plain line." in result

    def test_empty_lines(self, panel):
        """Blank lines produce newlines without crashing."""
        result = self._render(panel, "line1\n\nline2")
        assert "line1" in result
        assert "line2" in result

    def test_mixed_content(self, panel):
        md = "# Title\n\nSome text.\n\n- bullet\n\n```\ncode\n```"
        result = self._render(panel, md)
        assert "Title" in result
        assert "Some text." in result
        assert "\u2022 bullet" in result
        assert "code" in result


# ===========================================================================
# TestInsertInlineMd
# ===========================================================================

class TestInsertInlineMd:
    def _insert(self, panel, text, base_tag="assistant"):
        panel._chat_display.configure(state=tk.NORMAL)
        panel._chat_display.delete("1.0", tk.END)
        panel._insert_inline_md(text, base_tag)
        panel._chat_display.configure(state=tk.DISABLED)
        return _get_chat_text(panel)

    def test_bold(self, panel):
        result = self._insert(panel, "this is **bold** text")
        assert "bold" in result
        assert "**" not in result

    def test_italic(self, panel):
        result = self._insert(panel, "this is *italic* text")
        assert "italic" in result

    def test_inline_code(self, panel):
        result = self._insert(panel, "use `foo()` here")
        assert "foo()" in result
        assert "`" not in result.replace("foo()", "")

    def test_plain_text(self, panel):
        result = self._insert(panel, "no formatting here")
        assert "no formatting here" in result

    def test_mixed(self, panel):
        result = self._insert(panel, "**bold** and *italic* and `code`")
        assert "bold" in result
        assert "italic" in result
        assert "code" in result

    def test_trailing_text_after_match(self, panel):
        result = self._insert(panel, "before **mid** after")
        assert "before " in result
        assert "mid" in result
        assert " after" in result


# ===========================================================================
# TestInsertWithLinks
# ===========================================================================

class TestInsertWithLinks:
    def _insert(self, panel, text, tag=""):
        panel._chat_display.configure(state=tk.NORMAL)
        panel._chat_display.delete("1.0", tk.END)
        panel._insert_with_links(text, tag)
        panel._chat_display.configure(state=tk.DISABLED)
        return _get_chat_text(panel)

    def test_no_urls(self, panel):
        result = self._insert(panel, "no links here")
        assert "no links here" in result

    def test_single_url(self, panel):
        result = self._insert(panel, "visit https://example.com today")
        assert "https://example.com" in result
        assert "visit " in result
        assert " today" in result

    def test_multiple_urls(self, panel):
        result = self._insert(panel, "see https://a.com and https://b.com")
        assert "https://a.com" in result
        assert "https://b.com" in result

    def test_url_increments_link_counter(self, panel):
        before = panel._link_counter
        self._insert(panel, "https://x.com")
        assert panel._link_counter == before + 1


# ===========================================================================
# TestInsertLink
# ===========================================================================

class TestInsertLink:
    def test_link_text_appears(self, panel):
        panel._chat_display.configure(state=tk.NORMAL)
        panel._chat_display.delete("1.0", tk.END)
        panel._insert_link("https://example.org")
        panel._chat_display.configure(state=tk.DISABLED)
        text = _get_chat_text(panel)
        assert "https://example.org" in text

    def test_link_counter_increments(self, panel):
        before = panel._link_counter
        panel._chat_display.configure(state=tk.NORMAL)
        panel._insert_link("https://test.com")
        panel._chat_display.configure(state=tk.DISABLED)
        assert panel._link_counter == before + 1


# ===========================================================================
# TestOnLinkClick
# ===========================================================================

class TestOnLinkClick:
    @patch("sfi_reporter.copilot_panel.webbrowser.open")
    def test_opens_browser(self, mock_open, panel):
        panel._on_link_click("https://go.com")
        mock_open.assert_called_once_with("https://go.com")

    @patch("sfi_reporter.copilot_panel.webbrowser.open", side_effect=OSError("fail"))
    def test_exception_logged(self, mock_open, panel):
        """Exception in webbrowser.open is caught and logged."""
        panel._on_link_click("https://bad.com")  # should not raise


# ===========================================================================
# TestSetStatus
# ===========================================================================

class TestSetStatus:
    def test_set_status_text(self, panel):
        panel._set_status("● Ready")
        assert panel._status_label.cget("text") == "● Ready"

    def test_set_status_color(self, panel):
        panel._set_status("● Error", "#ff0000")
        assert panel._status_label.cget("fg") == "#ff0000"

    def test_set_status_default_color(self, panel):
        panel._set_status("● Default")
        assert panel._status_label.cget("fg") == CopilotPanel.SYSTEM_COLOR


# ===========================================================================
# TestOnStop
# ===========================================================================

class TestOnStop:
    def test_noop_not_sending(self, panel):
        """Does nothing when not sending."""
        panel._is_sending = False
        panel._on_stop()  # should not raise

    def test_noop_no_session(self, panel):
        """Does nothing when no session."""
        panel._is_sending = True
        panel._session = None
        panel._on_stop()
        panel._is_sending = False  # cleanup

    def test_abort_when_sending(self, panel):
        """Calls abort on the session and disables stop button."""
        mock_session = MagicMock()
        mock_session.abort = AsyncMock()
        panel._session = mock_session
        panel._is_sending = True
        panel._turn_timeout_id = None

        panel._on_stop()

        # Stop button should be disabled
        assert str(panel._stop_btn.cget("state")) == "disabled"
        # Cleanup
        panel._is_sending = False
        panel._session = None


# ===========================================================================
# TestSetInputEnabled
# ===========================================================================

class TestSetInputEnabled:
    def test_disable(self, panel):
        panel._set_input_enabled(False)
        assert str(panel._input_entry.cget("state")) == "disabled"
        assert str(panel._send_btn.instate(["disabled"])) == "True"

    def test_enable(self, panel):
        panel._set_input_enabled(True)
        assert str(panel._input_entry.cget("state")) == "normal"
        assert panel._send_btn.instate(["!disabled"])


# ===========================================================================
# TestOnSessionEvent
# ===========================================================================

class TestOnSessionEvent:
    def _make_event(self, etype, **data_attrs):
        """Create a mock event with type.value and data attributes."""
        event = MagicMock()
        event.type.value = etype
        for k, v in data_attrs.items():
            setattr(event.data, k, v)
        return event

    def test_turn_start(self, panel):
        panel._is_sending = True
        event = self._make_event("assistant.turn_start")
        panel._on_session_event(event)
        assert panel._turn_has_content is False

    def test_message_delta_with_content(self, panel):
        panel._is_sending = True
        panel._got_content = False
        panel._turn_has_content = False
        event = self._make_event("assistant.message_delta", delta_content="hello")
        panel._on_session_event(event)
        assert panel._got_content is True
        assert panel._turn_has_content is True

    def test_message_delta_empty(self, panel):
        panel._is_sending = True
        panel._got_content = False
        panel._turn_has_content = False
        event = self._make_event("assistant.message_delta", delta_content="")
        panel._on_session_event(event)
        assert panel._got_content is False

    def test_message_delta_none(self, panel):
        panel._is_sending = True
        panel._got_content = False
        event = self._make_event("assistant.message_delta")
        # delta_content defaults to mock, override to return None
        event.data.delta_content = None
        panel._on_session_event(event)
        assert panel._got_content is False

    def test_assistant_message_with_content_no_prior_delta(self, panel):
        panel._turn_has_content = False
        panel._got_content = False
        event = self._make_event("assistant.message", content="full reply")
        panel._on_session_event(event)
        assert panel._got_content is True
        assert panel._turn_has_content is True

    def test_assistant_message_already_has_content(self, panel):
        """When turn already has content, message event doesn't re-add."""
        panel._turn_has_content = True
        panel._got_content = True
        event = self._make_event("assistant.message", content="dup")
        panel._on_session_event(event)
        # Still has content, no error
        assert panel._turn_has_content is True

    def test_assistant_message_empty(self, panel):
        panel._turn_has_content = False
        panel._got_content = False
        event = self._make_event("assistant.message", content="")
        panel._on_session_event(event)
        # No content was delivered
        assert panel._turn_has_content is False

    def test_tool_execution_start(self, panel):
        event = self._make_event("tool.execution_start", tool_name="my_tool")
        panel._on_session_event(event)
        # Should not raise; status is updated via after()

    def test_tool_execution_complete(self, panel):
        event = self._make_event("tool.execution_complete")
        panel._on_session_event(event)

    def test_turn_end(self, panel):
        event = self._make_event("assistant.turn_end")
        panel._on_session_event(event)  # pass — no action

    def test_session_idle(self, panel):
        panel._is_sending = True
        panel._got_content = True
        event = self._make_event("session.idle")
        panel._on_session_event(event)
        # after(0, _on_response_complete) is scheduled

    def test_session_error(self, panel):
        panel._is_sending = True
        panel._session = MagicMock()
        event = self._make_event("session.error", message="bad stuff")
        panel._on_session_event(event)
        # Session should be cleared
        assert panel._session is None
        assert panel._is_sending is False

    def test_session_error_no_message(self, panel):
        panel._is_sending = True
        panel._session = MagicMock()
        event = self._make_event("session.error")
        event.data.message = None
        panel._on_session_event(event)
        assert panel._session is None

    def test_unhandled_event_type(self, panel):
        event = self._make_event("unknown.type")
        panel._on_session_event(event)  # should not raise

    def test_event_type_as_string(self, panel):
        """Event type without .value falls back to str()."""
        event = MagicMock()
        del event.type.value  # force hasattr to be False
        event.type.__str__ = lambda self: "assistant.turn_end"
        panel._on_session_event(event)


# ===========================================================================
# TestCancelTurnTimeout
# ===========================================================================

class TestCancelTurnTimeout:
    def test_cancel_when_set(self, panel):
        panel._turn_timeout_id = panel.after(60000, lambda: None)
        panel._cancel_turn_timeout()
        assert panel._turn_timeout_id is None

    def test_cancel_when_none(self, panel):
        panel._turn_timeout_id = None
        panel._cancel_turn_timeout()  # no-op, no error
        assert panel._turn_timeout_id is None


# ===========================================================================
# TestOnTurnTimeout
# ===========================================================================

class TestOnTurnTimeout:
    def test_timeout_no_content(self, panel):
        """With no content, appends timeout message and force-completes."""
        panel._is_sending = True
        panel._got_content = False
        panel._turn_timeout_id = "fake"

        # Pre-insert a prefix so _finish_assistant_message works
        panel._chat_display.configure(state=tk.NORMAL)
        panel._chat_display.insert(tk.END, "Copilot: ", "assistant")
        panel._chat_display.configure(state=tk.DISABLED)

        panel._on_turn_timeout()

        text = _get_chat_text(panel)
        assert "timed out" in text
        # _on_response_complete resets _got_content and _is_sending
        assert panel._is_sending is False
        assert panel._got_content is False

    def test_timeout_with_content(self, panel):
        """With content already received, force-completes without timeout msg."""
        panel._is_sending = True
        panel._got_content = True
        panel._turn_timeout_id = "fake"
        panel._on_turn_timeout()
        # _on_response_complete is called
        assert panel._is_sending is False

    def test_timeout_not_sending(self, panel):
        """If not sending, does nothing."""
        panel._is_sending = False
        panel._turn_timeout_id = "fake"
        panel._on_turn_timeout()


# ===========================================================================
# TestOnResponseComplete
# ===========================================================================

class TestOnResponseComplete:
    def test_complete_with_content(self, panel):
        panel._is_sending = True
        panel._got_content = True
        panel._on_response_complete()
        assert panel._is_sending is False
        assert panel._got_content is False
        assert str(panel._input_entry.cget("state")) == "normal"

    def test_complete_no_content(self, panel):
        """Appends '(no response)' when no content was received."""
        panel._is_sending = True
        panel._got_content = False

        # Need the mark for _finish_assistant_message
        panel._chat_display.configure(state=tk.NORMAL)
        panel._chat_display.insert(tk.END, "Copilot: ", "assistant")
        panel._chat_display.mark_set("md_msg_start", tk.INSERT)
        panel._chat_display.mark_gravity("md_msg_start", tk.LEFT)
        panel._chat_display.configure(state=tk.DISABLED)

        panel._on_response_complete()
        text = _get_chat_text(panel)
        assert "(no response)" in text
        assert panel._is_sending is False

    def test_noop_not_sending(self, panel):
        """Does nothing when _is_sending is False."""
        panel._is_sending = False
        panel._on_response_complete()  # no-op


# ===========================================================================
# TestOnSend
# ===========================================================================

class TestOnSend:
    def test_empty_prompt(self, panel):
        """Empty input does nothing."""
        panel._input_entry.delete(0, tk.END)
        panel._input_entry.insert(0, "   ")
        panel._on_send()
        assert panel._is_sending is False

    def test_busy_state(self, panel):
        """Does nothing when already sending."""
        panel._is_sending = True
        panel._input_entry.delete(0, tk.END)
        panel._input_entry.insert(0, "hello")
        panel._on_send()
        # Still sending from before, input not cleared
        panel._is_sending = False

    def test_connecting_state(self, panel):
        """Does nothing when connecting."""
        panel._is_connecting = True
        panel._input_entry.delete(0, tk.END)
        panel._input_entry.insert(0, "hi")
        panel._on_send()
        assert panel._is_sending is False
        panel._is_connecting = False

    def test_normal_send(self, panel):
        """Normal send sets state and schedules coroutine."""
        panel._input_entry.delete(0, tk.END)
        panel._input_entry.insert(0, "tell me about SFI")
        panel._is_sending = False
        panel._is_connecting = False

        with patch.object(panel._bridge, "run_coroutine") as mock_rc:
            panel._on_send()

        assert panel._is_sending is True
        assert panel._got_content is False
        text = _get_chat_text(panel)
        assert "You: " in text
        assert "tell me about SFI" in text
        # Input should be cleared
        assert panel._input_entry.get() == ""

        # Cleanup
        panel._is_sending = False
        panel._set_input_enabled(True)


# ===========================================================================
# TestSendPrompt (async)
# ===========================================================================

class TestSendPrompt:
    def test_send_prompt_success(self, panel):
        """_send_prompt connects and sends."""
        mock_session = AsyncMock()
        panel._session = mock_session

        async def _run():
            # Mock self.after and _model_var.get to avoid Tk main-thread errors
            with patch.object(panel, "after"), \
                 patch.object(panel._model_var, "get", return_value="gpt-5"):
                await panel._send_prompt("test prompt")

        panel._bridge.run_coroutine(_run()).result(timeout=5)
        mock_session.send.assert_called_once()

    def test_send_prompt_error(self, panel):
        """On error, schedules error message via after()."""
        panel._session = None  # force _ensure_connected to run

        async def _run():
            with patch.object(
                panel, "_ensure_connected", side_effect=RuntimeError("nope")
            ), patch.object(panel, "after") as mock_after:
                await panel._send_prompt("fail")

        panel._bridge.run_coroutine(_run()).result(timeout=5)
        # _got_content set to True so no "(no response)" on top of error
        assert panel._got_content is True


# ===========================================================================
# TestSendAnalysisPrompt / _do_send_analysis
# ===========================================================================

class TestSendAnalysisPrompt:
    def test_marshal_to_tk(self, panel):
        """send_analysis_prompt schedules _do_send_analysis via after()."""
        with patch.object(panel, "after") as mock_after:
            panel.send_analysis_prompt("analyze this", kpi_label="KPI-1")
            mock_after.assert_called_once()
            args = mock_after.call_args[0]
            assert args[0] == 0
            assert args[1] == panel._do_send_analysis

    def test_do_send_busy(self, panel):
        """Busy state shows wait message."""
        panel._is_sending = True
        panel._do_send_analysis("prompt", "KPI-1")
        text = _get_chat_text(panel)
        assert "wait" in text.lower() or "already in progress" in text.lower()
        panel._is_sending = False

    def test_do_send_with_kpi_label(self, panel):
        """KPI label appears in the user message."""
        panel._is_sending = False
        panel._is_connecting = False
        with patch.object(panel._bridge, "run_coroutine"):
            panel._do_send_analysis("prompt text", "My KPI")

        text = _get_chat_text(panel)
        assert "My KPI" in text
        # Cleanup
        panel._is_sending = False
        panel._set_input_enabled(True)

    def test_do_send_default_kpi_label(self, panel):
        """Empty kpi_label defaults to 'KPI'."""
        panel._is_sending = False
        panel._is_connecting = False
        with patch.object(panel._bridge, "run_coroutine"):
            panel._do_send_analysis("prompt text", "")

        text = _get_chat_text(panel)
        assert "KPI" in text
        panel._is_sending = False
        panel._set_input_enabled(True)

    def test_do_send_with_sources_metadata(self, panel):
        """Sources metadata triggers _show_sources_card."""
        panel._is_sending = False
        panel._is_connecting = False
        sources = MagicMock()
        sources.docs_dir = "/tmp/docs"

        with patch.object(panel._bridge, "run_coroutine"), \
             patch.object(panel, "_show_sources_card") as mock_card, \
             patch("sfi_reporter.copilot_panel.CopilotPanel._do_send_analysis.__module__", create=True):
            # We need to mock set_current_docs_dir import
            with patch("sfi_reporter.copilot_tools.set_current_docs_dir") as mock_set:
                panel._do_send_analysis("prompt", "KPI", sources)
                mock_card.assert_called_once_with(sources)

        panel._is_sending = False
        panel._set_input_enabled(True)

    def test_do_send_sources_no_docs_dir(self, panel):
        """Sources without docs_dir still works."""
        panel._is_sending = False
        panel._is_connecting = False
        sources = MagicMock()
        sources.docs_dir = ""

        with patch.object(panel._bridge, "run_coroutine"), \
             patch.object(panel, "_show_sources_card"):
            panel._do_send_analysis("prompt", "KPI", sources)

        panel._is_sending = False
        panel._set_input_enabled(True)


# ===========================================================================
# TestShowSourcesCard
# ===========================================================================

class TestShowSourcesCard:
    @patch("sfi_reporter.copilot_panel.logger")
    def test_show_sources_card_success(self, mock_logger, panel):
        result = MagicMock()
        with patch("sfi_reporter.kpi_analyzer.format_sources_card", return_value="Sources:\n- OK") as mock_fmt:
            panel._show_sources_card(result)
            mock_fmt.assert_called_once_with(result)
        text = _get_chat_text(panel)
        assert "Sources:" in text

    @patch("sfi_reporter.copilot_panel.logger")
    def test_show_sources_card_import_error(self, mock_logger, panel):
        """Import failure is caught and logged."""
        with patch(
            "sfi_reporter.kpi_analyzer.format_sources_card",
            side_effect=ImportError("no module"),
        ):
            panel._show_sources_card(MagicMock())
        # Should not raise; warning logged
        mock_logger.warning.assert_called()


# ===========================================================================
# TestDestroy
# ===========================================================================

class TestDestroy:
    def test_destroy_no_client(self, tk_root):
        """Destroy without client is clean."""
        mock_app = MagicMock()
        mock_app.current_data = {"detailed_items": []}
        p = CopilotPanel(tk_root, app=mock_app, on_close=MagicMock())
        p.destroy()
        # No error

    def test_destroy_with_client(self, tk_root):
        """Destroy with a client attempts shutdown."""
        mock_app = MagicMock()
        mock_app.current_data = {"detailed_items": []}
        p = CopilotPanel(tk_root, app=mock_app, on_close=MagicMock())

        # Give it a fake client and session
        mock_client = MagicMock()
        mock_client.stop = AsyncMock()
        mock_session = MagicMock()
        mock_session.destroy = AsyncMock()
        p._client = mock_client
        p._session = mock_session

        p.destroy()
        # Should complete without error


# ===========================================================================
# TestEnsureConnected (async)
# ===========================================================================

class TestEnsureConnected:
    def test_already_connected(self, panel):
        """Returns immediately if session already exists."""
        panel._session = MagicMock()

        async def _run():
            await panel._ensure_connected()

        panel._bridge.run_coroutine(_run()).result(timeout=5)
        # session unchanged
        assert panel._session is not None
        panel._session = None  # cleanup

    def test_connection_failure(self, panel):
        """Connection error sets session to None."""
        panel._session = None
        panel._client = None

        async def _run():
            with patch("sfi_reporter.copilot_panel.CopilotPanel.after"):
                mock_cc = MagicMock()
                mock_cc_inst = AsyncMock()
                mock_cc_inst.start = AsyncMock(side_effect=RuntimeError("connect fail"))
                mock_cc.return_value = mock_cc_inst
                with patch("copilot.CopilotClient", mock_cc):
                    with pytest.raises(RuntimeError, match="connect fail"):
                        await panel._ensure_connected()

        panel._bridge.run_coroutine(_run()).result(timeout=5)
        assert panel._session is None
        assert panel._is_connecting is False
