"""Background worker utilities for GUI.

Runs engine operations in a background thread to keep the UI responsive.
Workers use callbacks for result/error delivery — never touch widgets directly.
"""
from __future__ import annotations

import threading
from typing import Callable


def run_in_worker(
    func: Callable,
    on_complete: Callable,
    on_error: Callable,
) -> threading.Thread:
    """Run func() in a background thread.

    Args:
        func: Callable that performs the work (e.g., LLM extraction).
        on_complete: Called with func's return value on success.
        on_error: Called with the exception on failure.

    Returns:
        The started Thread object.
    """
    def _worker():
        try:
            result = func()
            on_complete(result)
        except Exception as e:
            on_error(e)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return thread
