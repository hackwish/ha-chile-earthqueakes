from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ChileEarthquakeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ChileEarthquakeCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ChileEarthquakeAlert(coordinator)])


class ChileEarthquakeAlert(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:alert"
    _attr_device_class = "safety"

    def __init__(self, coordinator: ChileEarthquakeCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator._entry_id}_alert"
        self._attr_name = "Earthquake Alert"

    @property
    def is_on(self) -> bool:
        return self.coordinator.alert_active
