"""Email magic-link setup, reauthentication, and polling options."""

from typing import Any
from uuid import uuid4

import probatio
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig, NumberSelectorMode

from .api import JetsonAuthError, JetsonClient, JetsonError, JetsonHTTPError, token_from_link
from .const import (
    CONF_INSTALL_ID,
    CONF_MAGIC_LINK,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class JetsonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._email = ""
        self._install_id = str(uuid4())
        self._client: JetsonClient | None = None

    def _get_client(self) -> JetsonClient:
        if self._client is None:
            self._client = JetsonClient(
                async_get_clientsession(self.hass), install_id=self._install_id
            )
        return self._client

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            self._email = user_input[CONF_EMAIL].strip()
            if "@" not in self._email or any(char.isspace() for char in self._email):
                errors[CONF_EMAIL] = "invalid_email"
            else:
                await self.async_set_unique_id(self._email.casefold())
                self._abort_if_unique_id_configured()
                try:
                    await self._get_client().request_magic_link(self._email)
                except JetsonError:
                    errors["base"] = "cannot_connect"
                else:
                    return await self.async_step_magic_link()
        return self.async_show_form(
            step_id="user",
            data_schema=probatio.Schema({probatio.Required(CONF_EMAIL): str}),
            errors=errors,
        )

    async def async_step_magic_link(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            try:
                token = token_from_link(user_input[CONF_MAGIC_LINK], self._email)
                tokens = await self._get_client().verify_magic_link(self._email, token)
                if not tokens.user_id:
                    raise JetsonError("Sign-in response is missing its user ID")
            except (ValueError, JetsonAuthError):
                errors["base"] = "invalid_auth"
            except JetsonHTTPError as err:
                errors["base"] = (
                    "invalid_auth" if err.status in (400, 403, 410, 422) else "cannot_connect"
                )
            except JetsonError:
                errors["base"] = "cannot_connect"
            else:
                data = {
                    CONF_EMAIL: self._email,
                    CONF_INSTALL_ID: self._install_id,
                    **tokens.as_dict(),
                }
                if self.source == config_entries.SOURCE_REAUTH:
                    entry = self._get_reauth_entry()
                    if entry.data.get("user_id") and entry.data["user_id"] != tokens.user_id:
                        return self.async_abort(reason="wrong_account")
                    return self.async_update_reload_and_abort(entry, data_updates=data)
                return self.async_create_entry(title=f"Jetson Home ({self._email})", data=data)
        return self.async_show_form(
            step_id="magic_link",
            data_schema=probatio.Schema({probatio.Required(CONF_MAGIC_LINK): str}),
            errors=errors,
            description_placeholders={"email": self._email},
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]):
        self._email = entry_data[CONF_EMAIL]
        self._install_id = entry_data.get(CONF_INSTALL_ID, self._install_id)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            try:
                await self._get_client().request_magic_link(self._email)
            except JetsonError:
                errors["base"] = "cannot_connect"
            else:
                return await self.async_step_magic_link()
        return self.async_show_form(
            step_id="reauth_confirm",
            errors=errors,
            description_placeholders={"email": self._email},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return JetsonOptionsFlow()


class JetsonOptionsFlow(config_entries.OptionsFlowWithReload):
    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            value = user_input.get(CONF_SCAN_INTERVAL)
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and 30 <= value <= 900
                and value == int(value)
            ):
                return self.async_create_entry(title="", data={CONF_SCAN_INTERVAL: int(value)})
            errors["base"] = "invalid_interval"
        return self.async_show_form(
            step_id="init",
            errors=errors,
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(min=30, max=900, step=1, mode=NumberSelectorMode.BOX)
                    ),
                }
            ),
        )
