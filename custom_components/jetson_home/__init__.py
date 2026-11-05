"""Experimental Jetson Home cloud integration."""

from uuid import uuid4

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JetsonClient, Tokens
from .const import CONF_INSTALL_ID
from .coordinator import JetsonCoordinator

PLATFORMS = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.HUMIDIFIER,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.BUTTON,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    install_id = entry.data.get(CONF_INSTALL_ID) or str(uuid4())
    if CONF_INSTALL_ID not in entry.data:
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_INSTALL_ID: install_id}
        )

    def save_tokens(tokens: Tokens) -> None:
        hass.config_entries.async_update_entry(entry, data={**entry.data, **tokens.as_dict()})

    client = JetsonClient(
        async_get_clientsession(hass),
        Tokens(
            entry.data["access_token"],
            entry.data["refresh_token"],
            entry.data.get("expires_at", 0),
            entry.data.get("user_id", ""),
        ),
        install_id=install_id,
        on_tokens=save_tokens,
    )
    coordinator = JetsonCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # OptionsFlowWithReload handles options; token rotation must not cause reloads.
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
