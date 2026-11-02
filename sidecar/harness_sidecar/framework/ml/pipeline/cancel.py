"""Async cancellation techniques.

Three patterns:
1. Cooperative Event (threading) — job checks a flag at safe points
2. asyncio.Task.cancel() — raises CancelledError inside the task
3. Timeout + shield — cancel after a deadline, protect cleanup
"""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any, Callable


# --- 1. Cooperative (threading) ---

class CancelToken:
    """Shared flag a worker checks between steps."""

    def __init__(self):
        self._ev = threading.Event()

    def cancel(self) -> None:
        self._ev.set()

    def cancelled(self) -> bool:
        return self._ev.is_set()

    def raise_if_cancelled(self) -> None:
        if self._ev.is_set():
            raise Cancelled()


class Cancelled(Exception):
    pass


def run_cooperative(steps: int, token: CancelToken, work: Callable[[], Any] | None = None) -> dict:
    done = 0
    for i in range(steps):
        if token.cancelled():
            return {"status": "cancelled", "done": done}
        if work:
            work()
        else:
            time.sleep(0.01)
        done += 1
    return {"status": "done", "done": done}


# --- 2. asyncio.Task.cancel ---

async def _async_work(steps: int) -> int:
    for i in range(steps):
        await asyncio.sleep(0.01)
    return steps


async def run_async_cancel(steps: int, cancel_after: float) -> dict:
    task = asyncio.create_task(_async_work(steps))
    await asyncio.sleep(cancel_after)
    task.cancel()
    try:
        await task
        return {"status": "done"}
    except asyncio.CancelledError:
        return {"status": "cancelled"}


# --- 3. Timeout + shield ---

async def run_with_timeout(steps: int, timeout: float) -> dict:
    try:
        result = await asyncio.wait_for(_async_work(steps), timeout=timeout)
        return {"status": "done", "result": result}
    except asyncio.TimeoutError:
        return {"status": "timeout"}


async def run_shielded(steps: int) -> dict:
    """Cleanup that must finish even if the outer task is cancelled."""
    task = asyncio.create_task(_async_work(steps))
    try:
        return {"status": "done", "result": await asyncio.shield(task)}
    except asyncio.CancelledError:
        # Shield keeps the inner task running; we still observe the cancel
        return {"status": "cancelled-outer", "inner_done": task.done()}
