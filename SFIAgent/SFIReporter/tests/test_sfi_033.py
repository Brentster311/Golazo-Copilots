"""SFI-033: Tests for LLM removal, stub, and Copilot panel integration."""
import importlib
import os
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Root of SFIReporter package
_SFI_ROOT = Path(__file__).resolve().parent.parent / "src" / "sfi_reporter"


# -----------------------------------------------------------------------
# Phase 0 — LLM module deletion
# -----------------------------------------------------------------------

class TestLLMModuleDeletion:
    """Verify old LLM modules and their tests are gone."""

    def test_llm_client_module_deleted(self):
        """llm_client.py must not exist on disk."""
        assert not (_SFI_ROOT / "llm_client.py").exists()

    def test_llm_client_import_fails(self):
        """Importing sfi_reporter.llm_client must raise ModuleNotFoundError."""
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("sfi_reporter.llm_client")

    def test_llm_storage_module_deleted(self):
        """llm_storage.py must not exist on disk."""
        assert not (_SFI_ROOT / "llm_storage.py").exists()

    def test_deleted_test_files_gone(self):
        """Test files for deleted modules must not exist."""
        tests_dir = Path(__file__).resolve().parent
        for name in ("test_llm_client.py", "test_llm_storage.py", "test_sfi_025.py"):
            assert not (tests_dir / name).exists(), f"{name} still exists"

    def test_analyze_with_llm_doc_deleted(self):
        """Documentation for removed LLM feature must be deleted."""
        docs_dir = Path(__file__).resolve().parent.parent / "docs"
        assert not (docs_dir / "analyze-with-llm.md").exists()


# -----------------------------------------------------------------------
# Phase 0 — LLM references cleaned from dialogs.py
# -----------------------------------------------------------------------

class TestDialogsLLMCleanup:
    """Verify LLM classes and helpers are removed from dialogs module."""

    def test_no_configure_llm_dialog(self):
        """ConfigureLLMDialog must not be in dialogs."""
        import sfi_reporter.dialogs as dialogs
        assert "ConfigureLLMDialog" not in dir(dialogs)
        assert "ConfigureLLMDialog" not in getattr(dialogs, "__all__", [])

    def test_no_analysis_modal(self):
        """AnalysisModal must not be in dialogs."""
        import sfi_reporter.dialogs as dialogs
        assert "AnalysisModal" not in dir(dialogs)
        assert "AnalysisModal" not in getattr(dialogs, "__all__", [])

    def test_no_analysis_progress_modal(self):
        """AnalysisProgressModal must not be in dialogs."""
        import sfi_reporter.dialogs as dialogs
        assert "AnalysisProgressModal" not in dir(dialogs)
        assert "AnalysisProgressModal" not in getattr(dialogs, "__all__", [])

    def test_no_on_analysis_complete(self):
        """_on_analysis_complete must not be in dialogs."""
        import sfi_reporter.dialogs as dialogs
        assert "_on_analysis_complete" not in dir(dialogs)

    def test_no_on_analysis_error(self):
        """_on_analysis_error must not be in dialogs."""
        import sfi_reporter.dialogs as dialogs
        assert "_on_analysis_error" not in dir(dialogs)


# -----------------------------------------------------------------------
# Phase 0 — services.py cleanup
# -----------------------------------------------------------------------

class TestServicesLLMCleanup:
    """Verify _load_llm_config is removed from services."""

    def test_no_load_llm_config_in_services(self):
        """_load_llm_config must not be in services.__all__ or callable."""
        import sfi_reporter.services as services
        assert "_load_llm_config" not in getattr(services, "__all__", [])
        assert not hasattr(services, "_load_llm_config")


# -----------------------------------------------------------------------
# Phase 0 — app.py cleanup
# -----------------------------------------------------------------------

class TestAppLLMCleanup:
    """Verify ConfigureLLMDialog references removed from app.py."""

    def test_no_configure_llm_dialog_import_in_app(self):
        """app.py must not import ConfigureLLMDialog."""
        src = (_SFI_ROOT / "app.py").read_text(encoding="utf-8")
        assert "ConfigureLLMDialog" not in src

    def test_no_llm_config_btn_attribute(self):
        """App must not have llm_config_btn attribute."""
        src = (_SFI_ROOT / "app.py").read_text(encoding="utf-8")
        assert "llm_config_btn" not in src


# -----------------------------------------------------------------------
# Phase 0 — _launch_llm_analysis stub
# -----------------------------------------------------------------------

class TestLLMAnalysisStub:
    """_launch_llm_analysis should be a messagebox stub with no LLM imports."""

    def test_analyze_with_llm_shows_not_implemented(self):
        """Calling _launch_llm_analysis should show 'not yet implemented'."""
        with patch("sfi_reporter.dialogs.messagebox") as mock_mb:
            from sfi_reporter.dialogs import _launch_llm_analysis
            parent = MagicMock()
            item = {"id": "AI-123", "title": "Test item"}
            _launch_llm_analysis(parent, item)
            mock_mb.showinfo.assert_called_once()
            call_args = mock_mb.showinfo.call_args
            # Message should contain "not yet implemented" (case-insensitive)
            msg = str(call_args).lower()
            assert "not yet implemented" in msg

    def test_stub_has_no_llm_imports(self):
        """The stub function body must not import llm_client or llm_storage."""
        import inspect
        from sfi_reporter.dialogs import _launch_llm_analysis
        src = inspect.getsource(_launch_llm_analysis)
        assert "llm_client" not in src
        assert "llm_storage" not in src
        assert "_load_llm_config" not in src


# -----------------------------------------------------------------------
# Phase 1 — open/LLM toggle buttons
# -----------------------------------------------------------------------

class TestOpenLLMButtons:
    """Verify open/LLM buttons exist in app.py source."""

    def test_app_has_open_and_llm_buttons(self):
        """app.py source must contain open_btn and llm_btn references."""
        src = (_SFI_ROOT / "app.py").read_text(encoding="utf-8")
        # The app should create buttons for toggling the copilot panel
        assert "copilot" in src.lower() or "CopilotPanel" in src


# -----------------------------------------------------------------------
# Phase 2 — AsyncBridge
# -----------------------------------------------------------------------

class TestAsyncBridge:
    """Test the AsyncBridge background event loop."""

    def test_async_bridge_starts_background_loop(self):
        """AsyncBridge.start() creates a running event loop."""
        from sfi_reporter.copilot_panel import AsyncBridge

        bridge = AsyncBridge()
        bridge.start()
        try:
            assert bridge.loop is not None
            assert bridge.loop.is_running()
        finally:
            bridge.stop()

    def test_async_bridge_runs_coroutine(self):
        """AsyncBridge can execute a coroutine on its background loop."""
        import asyncio
        from sfi_reporter.copilot_panel import AsyncBridge

        bridge = AsyncBridge()
        bridge.start()
        try:
            async def answer():
                return 42

            future = bridge.run_coroutine(answer())
            assert future.result(timeout=2) == 42
        finally:
            bridge.stop()


# -----------------------------------------------------------------------
# Phase 2 — CopilotPanel widget tests
# -----------------------------------------------------------------------

class TestCopilotPanel:
    """Test CopilotPanel instantiation and widget presence."""

    @pytest.fixture(autouse=True)
    def _setup_tk(self):
        """Create and destroy a Tk root for the class (one per test to avoid state leaks)."""
        import tkinter as tk
        try:
            self.root = tk.Tk()
        except tk.TclError:
            pytest.skip("Tk not available in this environment")
        self.root.withdraw()
        yield
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def test_copilot_panel_has_required_widgets(self):
        """Panel must have model combo, status label, chat display, input, send button."""
        from sfi_reporter.copilot_panel import CopilotPanel

        panel = CopilotPanel(self.root, on_close=lambda: None)
        assert hasattr(panel, "_model_var")
        assert hasattr(panel, "_status_label")
        assert hasattr(panel, "_chat_display")
        assert hasattr(panel, "_input_entry")
        assert hasattr(panel, "_send_btn")

    def test_copilot_panel_model_selector_default(self):
        """Default model should be gpt-4.1."""
        from sfi_reporter.copilot_panel import CopilotPanel

        panel = CopilotPanel(self.root, on_close=lambda: None)
        assert panel._model_var.get() == "gpt-4.1"

    def test_copilot_panel_close_button(self):
        """Close button must trigger on_close callback."""
        from sfi_reporter.copilot_panel import CopilotPanel

        closed = []
        panel = CopilotPanel(self.root, on_close=lambda: closed.append(True))
        # Simulate clicking the close button
        panel._close_btn.invoke()
        assert closed == [True]

    def test_send_empty_prompt_is_noop(self):
        """Sending empty input should not add messages."""
        from sfi_reporter.copilot_panel import CopilotPanel

        panel = CopilotPanel(self.root, on_close=lambda: None)
        panel._input_entry.delete(0, "end")
        panel._input_entry.insert(0, "")
        initial_content = panel._chat_display.get("1.0", "end-1c")
        panel._on_send()
        after_content = panel._chat_display.get("1.0", "end-1c")
        assert after_content == initial_content

    def test_copilot_panel_missing_sdk_shows_instructions(self):
        """When copilot SDK is not installed, panel should show instructions."""
        from sfi_reporter.copilot_panel import CopilotPanel

        panel = CopilotPanel(self.root, on_close=lambda: None)
        # Simulate send with SDK missing
        with patch.dict(sys.modules, {"copilot": None}):
            with patch("importlib.import_module", side_effect=ImportError("No module named 'copilot'")):
                panel._input_entry.delete(0, "end")
                panel._input_entry.insert(0, "Hello")
                panel._on_send()
                # Should show instructions in chat rather than crash
                content = panel._chat_display.get("1.0", "end-1c")
                assert "install" in content.lower() or "copilot" in content.lower() or "not" in content.lower()


# -----------------------------------------------------------------------
# Phase 0 — pyproject.toml cleanup
# -----------------------------------------------------------------------

class TestPyprojectCleanup:
    """Verify pyproject.toml no longer references removed deps/entrypoints."""

    def test_no_llm_extender_dependency(self):
        """pyproject.toml must not depend on llm-extender."""
        toml_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        content = toml_path.read_text(encoding="utf-8")
        assert "llm-extender" not in content

    def test_no_openai_dependency(self):
        """pyproject.toml must not depend on openai."""
        toml_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        content = toml_path.read_text(encoding="utf-8")
        assert "openai" not in content.lower()

    def test_no_web_entrypoint(self):
        """sfi-reporter-web entry point must be removed."""
        toml_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        content = toml_path.read_text(encoding="utf-8")
        assert "sfi-reporter-web" not in content

    def test_no_streamlit_optional_dep(self):
        """Streamlit optional dependency must be removed."""
        toml_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        content = toml_path.read_text(encoding="utf-8")
        assert "streamlit" not in content.lower()
