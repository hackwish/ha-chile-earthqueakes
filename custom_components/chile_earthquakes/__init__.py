from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EarthquakeAPI
from .const import (
    CONF_PRIMARY_SOURCE,
    DEFAULT_PRIMARY_SOURCE,
    DOMAIN,
    LOGGER,
    PLATFORMS,
)
from .coordinator import ChileEarthquakeCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = EarthquakeAPI(
        session=session,
        primary_source=entry.options.get(CONF_PRIMARY_SOURCE, DEFAULT_PRIMARY_SOURCE),
    )
    coordinator = ChileEarthquakeCoordinator(
        hass=hass,
        api=api,
        config_entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    coordinator: ChileEarthquakeCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.api.primary_source = entry.options.get(CONF_PRIMARY_SOURCE, DEFAULT_PRIMARY_SOURCE)
    LOGGER.debug("Options updated for %s", entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
