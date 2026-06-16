from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.core import callback

from .const import (
    CONF_ALERT_RESET_MINUTES,
    CONF_ALERT_THRESHOLD,
    CONF_PRIMARY_SOURCE,
    CONF_SCAN_INTERVAL,
    DEFAULT_ALERT_RESET_MINUTES,
    DEFAULT_ALERT_THRESHOLD,
    DEFAULT_PRIMARY_SOURCE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SOURCE_AUTO,
    SOURCE_BOOSTR,
    SOURCE_USGS,
)


class ChileEarthquakesConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> dict:
        if user_input is not None:
            return self.async_create_entry(title="Chile Earthquakes", data={})

        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ChileEarthquakesOptionsFlow(config_entry)


class ChileEarthquakesOptionsFlow(OptionsFlow):
    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> dict:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PRIMARY_SOURCE,
                        default=self.config_entry.options.get(CONF_PRIMARY_SOURCE, DEFAULT_PRIMARY_SOURCE),
                    ): vol.In([SOURCE_BOOSTR, SOURCE_USGS, SOURCE_AUTO]),
                    vol.Optional(
                        CONF_ALERT_THRESHOLD,
                        default=self.config_entry.options.get(CONF_ALERT_THRESHOLD, DEFAULT_ALERT_THRESHOLD),
                    ): vol.All(vol.Coerce(float), vol.Range(min=3.0, max=8.0)),
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
                    vol.Optional(
                        CONF_ALERT_RESET_MINUTES,
                        default=self.config_entry.options.get(CONF_ALERT_RESET_MINUTES, DEFAULT_ALERT_RESET_MINUTES),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                }
            ),
        )
