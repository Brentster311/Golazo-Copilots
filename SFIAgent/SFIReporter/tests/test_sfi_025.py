"""Tests for SFI-025: Configure LLM dialog with manual entry and auto-detect.

Covers TC-01 through TC-13 from SFI-025-Test-Cases.md.
All Azure SDK / discovery calls are mocked.
"""
import json
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from types import SimpleNamespace


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_llm_extender_config(
    *,
    base_url="https://my-openai.openai.azure.com/",
    deployment="gpt-4",
    model="gpt-4o",
    api_version="2024-12-01-preview",
    provider="azure_openai",
):
    """Build a mock llm_extender LLMConfig-like object."""
    cfg = SimpleNamespace()
    cfg.base_url = base_url
    cfg.deployment = deployment
    cfg.model = model
    cfg.api_version = api_version
    cfg.provider = provider
    return cfg


# ===========================================================================
# TC-01: Configure LLM button exists on main screen
# ===========================================================================

class TestConfigureLLMButton:
    def test_tc01_button_exists_on_controls_row(self):
        """TC-01: App main screen has 'Configure LLM' button."""
        from sfi_reporter.tk_app import SFIReporterApp
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        try:
            app = SFIReporterApp(root)
            assert hasattr(app, 'llm_config_btn'), \
                "Expected 'Configure LLM' button (llm_config_btn) in controls row"
            assert "Configure LLM" in str(app.llm_config_btn.cget("text")), \
                "Expected button text to contain 'Configure LLM'"
        finally:
            root.destroy()


# ===========================================================================
# TC-14: Subscription picker dialog
# ===========================================================================

class TestSubscriptionPicker:
    def test_tc14_picker_returns_selected(self):
        """TC-14: SubscriptionPickerDialog returns selected subscription."""
        import tkinter as tk
        from sfi_reporter.tk_app import SubscriptionPickerDialog

        root = tk.Tk()
        root.withdraw()
        try:
            choices = ["Sub B  (sub-id-b)", "Sub A  (sub-id-a)"]
            # Simulate user clicking OK by patching wait_window
            with patch.object(SubscriptionPickerDialog, 'wait_window'):
                dlg = SubscriptionPickerDialog(root, choices)
                # Treeview should be sorted by name: Sub A first, Sub B second
                items = dlg._tree.get_children()
                assert len(items) == 2
                assert dlg._tree.item(items[0], "values")[0] == "Sub A"
                assert dlg._tree.item(items[1], "values")[0] == "Sub B"
                # Select second row (Sub B) and confirm
                dlg._tree.selection_set(items[1])
                dlg._on_ok()
                assert dlg.result == "Sub B  (sub-id-b)", \
                    "Expected picker to return selected subscription"
        finally:
            root.destroy()


# ===========================================================================
# TC-02: Dialog opens with empty fields (no saved config)
# ===========================================================================

class TestDialogDefaultFields:
    def test_tc02_default_values_no_saved_config(self):
        """TC-02: No saved LLM config → dialog fields show defaults."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting", return_value=None):
                dlg = ConfigureLLMDialog(root)
                assert dlg._endpoint_var.get() == "", \
                    "Expected empty endpoint when no config saved"
                assert dlg._deployment_var.get() == "gpt-4o", \
                    "Expected default deployment 'gpt-4o'"
                assert dlg._api_version_var.get() == "2024-10-21", \
                    "Expected default API version '2024-10-21'"
                dlg.destroy()
        finally:
            root.destroy()


# ===========================================================================
# TC-03: Dialog opens with saved config pre-populated
# ===========================================================================

class TestDialogSavedConfig:
    def test_tc03_prepopulated_from_saved_config(self):
        """TC-03: Saved config → dialog fields pre-populated."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        saved = {
            "llm_endpoint": "https://my.openai.azure.com/",
            "llm_deployment": "gpt-35",
            "llm_api_version": "2025-01-01",
        }

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting",
                        side_effect=lambda k, d=None: saved.get(k, d)):
                dlg = ConfigureLLMDialog(root)
                assert dlg._endpoint_var.get() == "https://my.openai.azure.com/", \
                    "Expected dialog fields to match saved config"
                assert dlg._deployment_var.get() == "gpt-35"
                assert dlg._api_version_var.get() == "2025-01-01"
                dlg.destroy()
        finally:
            root.destroy()


# ===========================================================================
# TC-04: Auto-detect happy path — configs discovered
# ===========================================================================

class TestAutoDetectHappy:
    def test_tc04_discovered_configs_in_dropdown(self):
        """TC-04: Detect returns 2 configs → combobox has 2 items."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        configs = [
            _make_llm_extender_config(
                base_url="https://res-1.openai.azure.com/",
                deployment="gpt-4",
                model="gpt-4o",
            ),
            _make_llm_extender_config(
                base_url="https://res-2.openai.azure.com/",
                deployment="gpt-35",
                model="gpt-35-turbo",
            ),
        ]

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting", return_value=None):
                dlg = ConfigureLLMDialog(root)
                # Simulate successful detection callback (phase 2 complete)
                dlg._on_detect_complete(configs)
                values = list(dlg._config_combo["values"])
                assert len(values) == 2, \
                    "Expected discovered configs in selection dropdown"
                dlg.destroy()
        finally:
            root.destroy()


# ===========================================================================
# TC-05: Auto-detect selection populates fields
# ===========================================================================

class TestAutoDetectSelection:
    def test_tc05_selection_populates_fields(self):
        """TC-05: Selecting a discovered config → fields populated."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        configs = [
            _make_llm_extender_config(
                base_url="https://res-1.openai.azure.com/",
                deployment="gpt-4",
                model="gpt-4o",
                api_version="2024-12-01-preview",
            ),
        ]

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting", return_value=None):
                dlg = ConfigureLLMDialog(root)
                dlg._on_detect_complete(configs)
                # Simulate selecting the first item
                dlg._config_combo.current(0)
                dlg._on_config_selected(None)
                assert dlg._endpoint_var.get() == "https://res-1.openai.azure.com/", \
                    "Expected fields to populate from selected discovered config"
                assert dlg._deployment_var.get() == "gpt-4"
                assert dlg._api_version_var.get() == "2024-12-01-preview"
                dlg.destroy()
        finally:
            root.destroy()


# ===========================================================================
# TC-06: Auto-detect — no configs found
# ===========================================================================

class TestAutoDetectEmpty:
    def test_tc06_no_configs_shows_info(self):
        """TC-06: Auto-detect returns [] → info message shown."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting", return_value=None):
                dlg = ConfigureLLMDialog(root)
                with patch("sfi_reporter.tk_app.messagebox.showinfo") as mock_info:
                    dlg._on_detect_complete([])
                    mock_info.assert_called_once()
                    assert "No Azure OpenAI" in str(mock_info.call_args), \
                        "Expected info message when no configs discovered"
                dlg.destroy()
        finally:
            root.destroy()


# ===========================================================================
# TC-07: Auto-detect — ImportError (missing SDK)
# ===========================================================================

class TestAutoDetectImportError:
    def test_tc07_import_error_shows_sdk_message(self):
        """TC-07: ImportError from discovery → error with install instructions."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting", return_value=None):
                dlg = ConfigureLLMDialog(root)
                with patch("sfi_reporter.tk_app.messagebox.showerror") as mock_err:
                    dlg._on_detect_error(ImportError("pip install llm-extender[azure-discover]"))
                    mock_err.assert_called_once()
                    assert "SDK" in str(mock_err.call_args) or "pip install" in str(mock_err.call_args), \
                        "Expected ImportError to show SDK install instructions"
                dlg.destroy()
        finally:
            root.destroy()


# ===========================================================================
# TC-08: Auto-detect — other error
# ===========================================================================

class TestAutoDetectGenericError:
    def test_tc08_generic_error_shows_message(self):
        """TC-08: Generic exception from discovery → error message."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting", return_value=None):
                dlg = ConfigureLLMDialog(root)
                with patch("sfi_reporter.tk_app.messagebox.showerror") as mock_err:
                    dlg._on_detect_error(Exception("Connection timed out"))
                    mock_err.assert_called_once()
                    assert "Connection timed out" in str(mock_err.call_args), \
                        "Expected error message for discovery failure"
                dlg.destroy()
        finally:
            root.destroy()


# ===========================================================================
# TC-09: Save persists config to settings.json
# ===========================================================================

class TestSaveConfig:
    def test_tc09_save_persists_to_settings(self):
        """TC-09: Save writes config to settings.json."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        saved = {}

        def mock_save(key, value):
            saved[key] = value

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting", return_value=None):
                dlg = ConfigureLLMDialog(root)
                dlg._endpoint_var.set("https://test.openai.azure.com/")
                dlg._deployment_var.set("gpt-4o")
                dlg._api_version_var.set("2024-10-21")
                with patch("sfi_reporter.tk_app._save_setting", side_effect=mock_save):
                    dlg._on_save()
                assert saved.get("llm_endpoint") == "https://test.openai.azure.com/", \
                    "Expected config to persist to settings.json after Save"
                assert saved.get("llm_deployment") == "gpt-4o"
                assert saved.get("llm_api_version") == "2024-10-21"
                # Dialog should be destroyed after save
        finally:
            root.destroy()


# ===========================================================================
# TC-10: LLM analysis uses saved config over env vars
# ===========================================================================

class TestConfigResolutionOrder:
    def test_tc10_saved_config_takes_priority(self):
        """TC-10: Saved config → analysis uses saved endpoint, not env var."""
        from sfi_reporter.tk_app import _load_llm_config

        saved = {
            "llm_endpoint": "https://saved.openai.azure.com/",
            "llm_deployment": "gpt-4-saved",
            "llm_api_version": "2025-01-01",
        }

        with patch("sfi_reporter.tk_app._load_setting",
                    side_effect=lambda k, d=None: saved.get(k, d)):
                config = _load_llm_config()
                assert config.endpoint == "https://saved.openai.azure.com/", \
                    "Expected saved config to take priority over env vars"
                assert config.deployment == "gpt-4-saved"


# ===========================================================================
# TC-11: LLM analysis falls back to env vars when no saved config
# ===========================================================================

class TestConfigFallback:
    def test_tc11_falls_back_to_env_vars(self):
        """TC-11: No saved config → uses LLMConfig.from_env()."""
        from sfi_reporter.tk_app import _load_llm_config

        with patch("sfi_reporter.tk_app._load_setting", return_value=None):
            with patch.dict("os.environ", {
                "AZURE_OPENAI_ENDPOINT": "https://env.openai.azure.com/",
                "AZURE_OPENAI_DEPLOYMENT": "gpt-env",
            }):
                config = _load_llm_config()
                assert config.endpoint == "https://env.openai.azure.com/", \
                    "Expected fallback to env vars when no saved config"
                assert config.deployment == "gpt-env"


# ===========================================================================
# TC-12: Clear button removes saved config
# ===========================================================================

class TestClearConfig:
    def test_tc12_clear_removes_saved_config(self):
        """TC-12: Clear → saved config removed, fields reset to defaults."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        saved = {
            "llm_endpoint": "https://saved.openai.azure.com/",
            "llm_deployment": "gpt-35",
            "llm_api_version": "2025-01-01",
        }
        cleared_keys = []

        def mock_save(key, value):
            if value is None or value == "":
                cleared_keys.append(key)
            saved[key] = value

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting",
                        side_effect=lambda k, d=None: saved.get(k, d)):
                dlg = ConfigureLLMDialog(root)

            with patch("sfi_reporter.tk_app._save_setting", side_effect=mock_save):
                dlg._on_clear()

            assert dlg._endpoint_var.get() == "", \
                "Expected Clear to remove saved config and reset fields"
            assert dlg._deployment_var.get() == "gpt-4o"
            assert dlg._api_version_var.get() == "2024-10-21"
            assert "llm_endpoint" in cleared_keys, \
                "Expected llm_endpoint to be cleared in settings"
            dlg.destroy()
        finally:
            root.destroy()


# ===========================================================================
# TC-13: Save validates endpoint format
# ===========================================================================

class TestSaveValidation:
    def test_tc13_rejects_invalid_endpoint(self):
        """TC-13: Endpoint without https:// → validation error, not saved."""
        import tkinter as tk
        from sfi_reporter.tk_app import ConfigureLLMDialog

        root = tk.Tk()
        root.withdraw()
        try:
            with patch("sfi_reporter.tk_app._load_setting", return_value=None):
                dlg = ConfigureLLMDialog(root)
                dlg._endpoint_var.set("not-a-url")
                with patch("sfi_reporter.tk_app._save_setting") as mock_save:
                    with patch("sfi_reporter.tk_app.messagebox.showerror") as mock_err:
                        dlg._on_save()
                        mock_err.assert_called_once()
                        mock_save.assert_not_called()
                        assert "https://" in str(mock_err.call_args), \
                            "Expected validation error for invalid endpoint URL"
                dlg.destroy()
        finally:
            root.destroy()
