"""Logging configuration and platform fixes for S360Reporter.

Sets up file-based logging to %TEMP%/GUI/s360_reporter.log
with rotation so the log doesn't grow unbounded.

Also patches subprocess on Windows so that child processes
(e.g. ``az account get-access-token`` called by AzureCliCredential)
do not pop up visible console windows when the app is running as a
GUI / PyInstaller bundle.
"""
import logging
import subprocess
import sys
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path(tempfile.gettempdir()) / "S360Reporter"
LOG_FILE = LOG_DIR / "s360_reporter.log"
LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_BYTES = 2 * 1024 * 1024  # 2 MB
BACKUP_COUNT = 3  # Keep 3 rotated logs


def setup_logging(level: int = logging.DEBUG) -> None:
    """Configure logging for the entire s360_reporter package.

    Writes DEBUG+ to a rotating log file and INFO+ to the console.
    Safe to call multiple times (idempotent).

    Args:
        level: Root log level (default DEBUG for file output).
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("s360_reporter")

    # Avoid adding duplicate handlers on repeated calls
    if root.handlers:
        return

    root.setLevel(level)

    # ── File handler (DEBUG+) ──
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root.addHandler(file_handler)

    # ── Console handler (INFO+) ──
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root.addHandler(console_handler)

    root.info("Logging initialised — log file: %s", LOG_FILE)


# ---------------------------------------------------------------------------
# Windows: suppress console windows from subprocess calls
# ---------------------------------------------------------------------------
_original_popen_init = subprocess.Popen.__init__


def _patched_popen_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
    """Wrapper that adds CREATE_NO_WINDOW on Windows for headless subprocess calls."""
    if sys.platform == "win32" and "creationflags" not in kwargs:
        kwargs["creationflags"] = (
            kwargs.get("creationflags", 0) | subprocess.CREATE_NO_WINDOW
        )
    _original_popen_init(self, *args, **kwargs)


def patch_subprocess_windows() -> None:
    """Monkey-patch ``subprocess.Popen`` so child processes are invisible.

    Only applies on Windows.  Safe to call multiple times (idempotent).
    """
    if sys.platform != "win32":
        return
    if getattr(subprocess.Popen.__init__, "_sfi_patched", False):
        return  # already applied
    subprocess.Popen.__init__ = _patched_popen_init  # type: ignore[assignment]
    subprocess.Popen.__init__._sfi_patched = True  # type: ignore[attr-defined]
    logging.getLogger("s360_reporter").debug(
        "Patched subprocess.Popen to suppress console windows"
    )


def get_log_path() -> Path:
    """Return the path to the current log file."""
    return LOG_FILE
