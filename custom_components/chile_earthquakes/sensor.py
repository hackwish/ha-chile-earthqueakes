from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_DEPTH,
    ATTR_EVENT_ID,
    ATTR_IMAGE_URL,
    ATTR_INFO_URL,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_MAGNITUDE,
    ATTR_PLACE,
    ATTR_SOURCE,
    ATTR_TIME,
    DOMAIN,
)
from .coordinator import ChileEarthquakeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ChileEarthquakeCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ChileEarthquakeSensor(coordinator)])


class ChileEarthquakeSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:earthquake"
    _attr_native_unit_of_measurement = "Mw"

    def __init__(self, coordinator: ChileEarthquakeCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._entry_id}_last_earthquake"
        self._attr_name = "Last Earthquake"

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.magnitude

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data
        if data is None:
            return {}
        return {
            ATTR_MAGNITUDE: data.magnitude,
            ATTR_DEPTH: data.depth,
            ATTR_PLACE: data.place,
            ATTR_LATITUDE: data.latitude,
            ATTR_LONGITUDE: data.longitude,
            ATTR_TIME: data.time.isoformat() if data.time else None,
            ATTR_SOURCE: data.source,
            ATTR_EVENT_ID: data.event_id,
            ATTR_IMAGE_URL: data.image_url,
            ATTR_INFO_URL: data.info_url,
        }

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None
