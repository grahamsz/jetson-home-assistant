"""Localized errors shown by Home Assistant controls."""

from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN


def user_error(key: str, **placeholders: str) -> HomeAssistantError:
    return HomeAssistantError(
        translation_domain=DOMAIN,
        translation_key=key,
        translation_placeholders=placeholders,
    )
