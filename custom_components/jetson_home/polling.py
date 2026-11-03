"""Serialize explicit discovery and lightweight polling of the known configuration."""

import asyncio
from collections.abc import Callable
from time import monotonic

from .api import JetsonClient
from .models import Snapshot

CONNECTIVITY_INTERVAL = 300


class JetsonPoller:
    """Keep a last-good configuration until startup or an explicit refresh."""

    def __init__(self, client: JetsonClient, *, clock: Callable[[], float] = monotonic) -> None:
        self.client = client
        self.snapshot: Snapshot | None = None
        self.configuration_revision = 0
        self._clock = clock
        self._next_connectivity_update = 0.0
        self._lock = asyncio.Lock()

    async def refresh(self, *, discover: bool = False) -> Snapshot:
        async with self._lock:
            if self.snapshot is None or discover:
                snapshot = await self.client.get_snapshot()
                self.configuration_revision += 1
                self._next_connectivity_update = self._clock() + CONNECTIVITY_INTERVAL
            else:
                refresh_connectivity = self._clock() >= self._next_connectivity_update
                snapshot = await self.client.get_updates(
                    self.snapshot, refresh_connectivity=refresh_connectivity
                )
                if refresh_connectivity:
                    self._next_connectivity_update = self._clock() + CONNECTIVITY_INTERVAL
            # Failed discovery or status reads leave the previous snapshot intact.
            self.snapshot = snapshot
            return snapshot
