"""Simple async progress spinner for long-running agent tasks."""

import asyncio
import sys
import time


class Spinner:
    """Async context manager that displays a live spinner with elapsed time."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str = "Running agent"):
        self._message = message
        self._task: asyncio.Task | None = None
        self._start: float = 0

    async def _spin(self):
        i = 0
        try:
            while True:
                elapsed = time.time() - self._start
                frame = self.FRAMES[i % len(self.FRAMES)]
                sys.stdout.write(
                    f"\r{frame}  {self._message} ({elapsed:.0f}s elapsed)  "
                )
                sys.stdout.flush()
                i += 1
                await asyncio.sleep(0.12)
        except asyncio.CancelledError:
            elapsed = time.time() - self._start
            sys.stdout.write(f"\r✅ {self._message} — done in {elapsed:.1f}s\n")
            sys.stdout.flush()

    async def __aenter__(self):
        self._start = time.time()
        self._task = asyncio.create_task(self._spin())
        return self

    async def __aexit__(self, *exc):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
