import asyncio
import pytest
from fxmoney.updater import async_background_update

@pytest.mark.asyncio
async def test_async_updater_stops_on_event():
    # Create an asyncio.Event and set it after a short delay
    stop_evt = asyncio.Event()

    async def stopper():
        await asyncio.sleep(0.1)
        stop_evt.set()

    # Run both tasks concurrently
    task = asyncio.create_task(async_background_update(0.5, stop_evt))
    stopper_task = asyncio.create_task(stopper())

    # Wait for both to finish
    await asyncio.gather(task, stopper_task)
    # If we reach here without timeout, the updater respected the stop event
    assert stop_evt.is_set()
