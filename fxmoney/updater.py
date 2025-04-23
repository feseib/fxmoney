# fxmoney/updater.py

"""
Background rate updater for fxmoney.

Contains:
- Thread-based updater: enable_background_update(), disable_background_update()
- AsyncIO-based updater: async_background_update(interval_seconds, stop_event=None)
"""

import threading
import asyncio
import time
from typing import Optional

from .rates.ecb import ECBBackend

# ─── Thread-based updater ──────────────────────────────────────────────────

# Event and thread handle at module level
_stop_event: threading.Event = threading.Event()
_thread: Optional[threading.Thread] = None

def enable_background_update(interval_hours: float = 4.0) -> None:
    """
    Start a daemon thread that refreshes ECB rates every `interval_hours`.
    If already running, does nothing.
    """
    global _thread, _stop_event
    # If a thread is already alive, skip
    if _thread is not None and _thread.is_alive():
        return

    # Clear any previous stop flag
    _stop_event.clear()

    def _worker():
        # Loop until stop_event is set; sleep interval_hours each iteration
        while not _stop_event.wait(interval_hours * 3600):
            try:
                ECBBackend()  # constructor forces cache refresh if stale
            except Exception:
                # ignore errors in background
                pass

    t = threading.Thread(
        target=_worker,
        name="fxmoney-rate-updater",
        daemon=True
    )
    _thread = t
    t.start()


def disable_background_update() -> None:
    """
    Signal the background updater thread to stop and wait briefly for it.
    """
    global _thread, _stop_event
    _stop_event.set()
    if _thread is not None:
        _thread.join(timeout=1)
        _thread = None


# ─── AsyncIO-based updater ─────────────────────────────────────────────────

async def async_background_update(
    interval_seconds: float,
    stop_event: Optional[asyncio.Event] = None
) -> None:
    """
    AsyncIO-based updater that refreshes ECB rates every `interval_seconds`.
    If `stop_event` (asyncio.Event) is provided, it stops when `stop_event.is_set()`.
    """
    evt = stop_event or asyncio.Event()
    while not evt.is_set():
        try:
            ECBBackend()
        except Exception:
            pass
        # wait for either the event or the timeout
        try:
            await asyncio.wait_for(evt.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue
