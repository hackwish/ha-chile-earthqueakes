from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EarthquakeAPI, EarthquakeData
from .const import (
    CONF_ALERT_RESET_MINUTES,
    CONF_ALERT_THRESHOLD,
    CONF_SCAN_INTERVAL,
    DEFAULT_ALERT_RESET_MINUTES,
    DEFAULT_ALERT_THRESHOLD,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_NEW_EARTHQUAKE,
    LOGGER,
)


class ChileEarthquakeCoordinator(DataUpdateCoordinator[Optional[EarthquakeData]]):
    def __init__(
        self,
        hass: HomeAssistant,
        api: EarthquakeAPI,
        config_entry: ConfigEntry,
    ) -> None:
        self.api = api
        self._entry_id = config_entry.entry_id
        self._config_entry = config_entry
        self._previous_event_id: Optional[str] = None
        self._alert_active = False
        self._cancel_reset: Optional[Callable[[], None]] = None

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
        )

    @property
    def alert_active(self) -> bool:
        return self._alert_active

    @property
    def alert_reset_minutes(self) -> int:
        return self._config_entry.options.get(CONF_ALERT_RESET_MINUTES, DEFAULT_ALERT_RESET_MINUTES)

    @property
    def alert_threshold(self) -> float:
        return self._config_entry.options.get(CONF_ALERT_THRESHOLD, DEFAULT_ALERT_THRESHOLD)

    @property
    def scan_interval(self) -> int:
        return self._config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    def _compute_event_id(self, data: EarthquakeData) -> str:
        if data.event_id:
            return data.event_id
        return f"{data.time.isoformat()}_{data.latitude}_{data.longitude}_{data.magnitude}"

    async def _async_update_data(self) -> Optional[EarthquakeData]:
        data = await self.api.get_latest()
        if data is None:
            raise UpdateFailed("No earthquake data available from any source")

        event_id = self._compute_event_id(data)

        if event_id != self._previous_event_id:
            self._previous_event_id = event_id
            if data.magnitude >= self.alert_threshold:
                LOGGER.info("New earthquake alert: M%s at %s", data.magnitude, data.place)
                self._alert_active = True
                self.async_update_listeners()
                self.hass.bus.async_fire(
                    EVENT_NEW_EARTHQUAKE,
                    {
                        "magnitude": data.magnitude,
                        "depth": data.depth,
                        "place": data.place,
                        "latitude": data.latitude,
                        "longitude": data.longitude,
                        "time": data.time.isoformat(),
                        "source": data.source,
                        "event_id": data.event_id,
                        "image_url": data.image_url,
                        "info_url": data.info_url,
                    },
                )
                self._schedule_alert_reset()

        self.update_interval = timedelta(seconds=self.scan_interval)
        return data

    def _schedule_alert_reset(self) -> None:
        if self._cancel_reset:
            self._cancel_reset()
        self._cancel_reset = async_call_later(
            self.hass,
            timedelta(minutes=self.alert_reset_minutes),
            self._async_reset_alert,
        )

    async def _async_reset_alert(self, _now: datetime) -> None:
        self._alert_active = False
        self._cancel_reset = None
        self.async_update_listeners()

    async def async_shutdown(self) -> None:
        if self._cancel_reset:
            self._cancel_reset()
        await super().async_shutdown()
