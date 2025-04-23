import time
import threading
import pytest

from fxmoney.updater import (
    enable_background_update,
    disable_background_update,
)

def test_thread_updater_starts_and_stops():
    # Start the updater with a short interval
    enable_background_update(interval_hours=0.0001)  # ~0.36s
    # Give it a moment to spin up
    time.sleep(0.1)
    # There should be at least one alive thread named "fxmoney-rate-updater"
    threads = [t for t in threading.enumerate() if t.name == "fxmoney-rate-updater"]
    assert threads and threads[0].is_alive()

    # Now stop it
    disable_background_update()
    # Wait to ensure the thread has time to exit
    time.sleep(0.1)
    # After stopping, no thread of that name should be alive
    threads = [t for t in threading.enumerate() if t.name == "fxmoney-rate-updater"]
    assert not threads
