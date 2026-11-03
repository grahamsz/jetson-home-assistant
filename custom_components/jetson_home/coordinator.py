"""Polling and serialized zone commands."""

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import JetsonAuthError, JetsonClient, JetsonError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .devices import sync_devices
from .models import Snapshot, Zone
from .polling import JetsonPoller

_LOGGER = logging.getLogger(__name__)


class JetsonCoordinator(DataUpdateCoordinator[Snapshot]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: JetsonClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(
                seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )
        self.client = client
        self.poller = JetsonPoller(client)
        self.command_lock = asyncio.Lock()
        self.device_infos = {}
        self._registered_revision = 0

    def _sync_configuration(self, snapshot: Snapshot) -> None:
        if self._registered_revision != self.poller.configuration_revision:
            self.device_infos = sync_devices(self.hass, self.config_entry, snapshot)
            self._registered_revision = self.poller.configuration_revision

    async def _async_update_data(self) -> Snapshot:
        try:
            snapshot = await self.poller.refresh()
            self._sync_configuration(snapshot)
            return snapshot
        except JetsonAuthError as err:
            raise ConfigEntryAuthFailed("Sign in to Jetson Home again") from err
        except JetsonError as err:
            raise UpdateFailed(str(err)) from err

    async def async_refresh_configuration(self) -> Snapshot:
        """Rediscover this account and notify entity platforms without a reload."""
        snapshot = await self.poller.refresh(discover=True)
        self._sync_configuration(snapshot)
        self.async_set_updated_data(snapshot)
        return snapshot

    async def command(self, method: str, zone: Zone, value: Any) -> None:
        async with self.command_lock:
            current = self.data.zones.get(zone.key)
            if not self.last_update_success or current is None or not current.online:
                raise HomeAssistantError("Jetson zone is unavailable")
            try:
                await getattr(self.client, method)(zone.zone_id, value)
            except JetsonAuthError as err:
                self.config_entry.async_start_reauth(self.hass)
                raise HomeAssistantError("Sign in to Jetson Home again") from err
            except JetsonError as err:
                raise HomeAssistantError(str(err)) from err
        # Report confirmed API state; cloud propagation may require another poll.
        await self.async_request_refresh()
