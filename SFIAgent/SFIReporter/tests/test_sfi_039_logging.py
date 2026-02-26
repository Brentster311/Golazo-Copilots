"""Tests for sfi_reporter.logging_config — targets ≥70% coverage."""

import logging
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------

class TestSetupLogging:
    """Tests for setup_logging()."""

    def test_creates_log_dir_and_handlers(self, tmp_path):
        """First call creates file + console handlers."""
        log_dir = tmp_path / "sfireporter"
        log_file = log_dir / "sfi_reporter.log"

        with patch("sfi_reporter.logging_config.LOG_DIR", log_dir), \
             patch("sfi_reporter.logging_config.LOG_FILE", log_file):
            from sfi_reporter.logging_config import setup_logging

            # Ensure a fresh logger for this test
            test_logger = logging.getLogger("sfi_reporter")
            test_logger.handlers.clear()

            setup_logging(level=logging.DEBUG)

            assert log_dir.exists()
            assert len(test_logger.handlers) == 2  # file + console
            # Clean up
            test_logger.handlers.clear()

    def test_idempotent_on_second_call(self, tmp_path):
        """Second call is a no-op (handlers already present)."""
        log_dir = tmp_path / "sfireporter"
        log_file = log_dir / "sfi_reporter.log"

        with patch("sfi_reporter.logging_config.LOG_DIR", log_dir), \
             patch("sfi_reporter.logging_config.LOG_FILE", log_file):
            from sfi_reporter.logging_config import setup_logging

            test_logger = logging.getLogger("sfi_reporter")
            test_logger.handlers.clear()

            setup_logging(level=logging.DEBUG)
            handler_count = len(test_logger.handlers)

            setup_logging(level=logging.DEBUG)
            assert len(test_logger.handlers) == handler_count
            # Clean up
            test_logger.handlers.clear()

    def test_file_handler_level_is_debug(self, tmp_path):
        """File handler captures DEBUG+."""
        log_dir = tmp_path / "sfireporter"
        log_file = log_dir / "sfi_reporter.log"

        with patch("sfi_reporter.logging_config.LOG_DIR", log_dir), \
             patch("sfi_reporter.logging_config.LOG_FILE", log_file):
            from sfi_reporter.logging_config import setup_logging

            test_logger = logging.getLogger("sfi_reporter")
            test_logger.handlers.clear()

            setup_logging()

            file_handlers = [h for h in test_logger.handlers
                            if hasattr(h, 'baseFilename')]
            assert len(file_handlers) == 1
            assert file_handlers[0].level == logging.DEBUG
            test_logger.handlers.clear()

    def test_console_handler_level_is_info(self, tmp_path):
        """Console handler only captures INFO+."""
        log_dir = tmp_path / "sfireporter"
        log_file = log_dir / "sfi_reporter.log"

        with patch("sfi_reporter.logging_config.LOG_DIR", log_dir), \
             patch("sfi_reporter.logging_config.LOG_FILE", log_file):
            from sfi_reporter.logging_config import setup_logging

            test_logger = logging.getLogger("sfi_reporter")
            test_logger.handlers.clear()

            setup_logging()

            stream_handlers = [h for h in test_logger.handlers
                              if isinstance(h, logging.StreamHandler)
                              and not hasattr(h, 'baseFilename')]
            assert len(stream_handlers) == 1
            assert stream_handlers[0].level == logging.INFO
            test_logger.handlers.clear()


# ---------------------------------------------------------------------------
# patch_subprocess_windows
# ---------------------------------------------------------------------------

class TestPatchSubprocessWindows:
    """Tests for patch_subprocess_windows() and _patched_popen_init."""

    def setup_method(self):
        """Reset _sfi_patched before each test."""
        if hasattr(subprocess.Popen.__init__, "_sfi_patched"):
            # Restore original
            from sfi_reporter.logging_config import _original_popen_init
            subprocess.Popen.__init__ = _original_popen_init

    def teardown_method(self):
        """Restore original Popen after each test."""
        if hasattr(subprocess.Popen.__init__, "_sfi_patched"):
            from sfi_reporter.logging_config import _original_popen_init
            subprocess.Popen.__init__ = _original_popen_init

    def test_patches_on_windows(self):
        """On win32, Popen.__init__ is replaced."""
        from sfi_reporter.logging_config import patch_subprocess_windows

        with patch("sfi_reporter.logging_config.sys") as mock_sys:
            mock_sys.platform = "win32"
            # Ensure not already patched
            if hasattr(subprocess.Popen.__init__, "_sfi_patched"):
                delattr(subprocess.Popen.__init__, "_sfi_patched")
            patch_subprocess_windows()
            assert getattr(subprocess.Popen.__init__, "_sfi_patched", False) is True

    def test_noop_on_non_windows(self):
        """On non-win32, nothing happens."""
        from sfi_reporter.logging_config import patch_subprocess_windows, _original_popen_init

        with patch("sfi_reporter.logging_config.sys") as mock_sys:
            mock_sys.platform = "linux"
            original = subprocess.Popen.__init__
            patch_subprocess_windows()
            # Should not have the _sfi_patched attribute if it wasn't there
            # (or original is still the same)
            assert subprocess.Popen.__init__ is original or not getattr(
                subprocess.Popen.__init__, "_sfi_patched", False
            )

    def test_idempotent_when_already_patched(self):
        """Calling twice doesn't double-patch."""
        from sfi_reporter.logging_config import patch_subprocess_windows

        with patch("sfi_reporter.logging_config.sys") as mock_sys:
            mock_sys.platform = "win32"
            if hasattr(subprocess.Popen.__init__, "_sfi_patched"):
                delattr(subprocess.Popen.__init__, "_sfi_patched")
            patch_subprocess_windows()
            patched_fn = subprocess.Popen.__init__
            patch_subprocess_windows()
            assert subprocess.Popen.__init__ is patched_fn

    def test_patched_popen_adds_create_no_window(self):
        """_patched_popen_init adds CREATE_NO_WINDOW flag on win32."""
        from sfi_reporter.logging_config import _patched_popen_init, _original_popen_init

        captured_kwargs = {}
        def fake_original(self, *args, **kwargs):
            captured_kwargs.update(kwargs)

        with patch("sfi_reporter.logging_config._original_popen_init", fake_original), \
             patch("sfi_reporter.logging_config.sys") as mock_sys:
            mock_sys.platform = "win32"
            mock_popen = MagicMock()
            _patched_popen_init(mock_popen, "echo", "hello")
            assert "creationflags" in captured_kwargs
            assert captured_kwargs["creationflags"] & subprocess.CREATE_NO_WINDOW


# ---------------------------------------------------------------------------
# get_log_path
# ---------------------------------------------------------------------------

class TestGetLogPath:
    def test_returns_path_object(self):
        from sfi_reporter.logging_config import get_log_path, LOG_FILE
        result = get_log_path()
        assert isinstance(result, Path)
        assert result == LOG_FILE


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_log_format_is_string(self):
        from sfi_reporter.logging_config import LOG_FORMAT
        assert isinstance(LOG_FORMAT, str)
        assert "%(asctime)s" in LOG_FORMAT

    def test_max_log_bytes(self):
        from sfi_reporter.logging_config import MAX_LOG_BYTES
        assert MAX_LOG_BYTES == 2 * 1024 * 1024

    def test_backup_count(self):
        from sfi_reporter.logging_config import BACKUP_COUNT
        assert BACKUP_COUNT == 3
