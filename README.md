# Chile Earthquakes

Home Assistant integration for monitoring and alerting on the latest earthquakes in Chile.

**Data sources**: [CSN / Sismologia.cl](https://www.sismologia.cl/) via [Boostr.cl](https://api.boostr.cl) (primary), [USGS](https://earthquake.usgs.gov) (fallback), and direct scraping of [Sismologia.cl](https://www.sismologia.cl/) (last resort).

## Features

- Real-time earthquake monitoring (30s polling by default)
- Configurable alert threshold
- Binary sensor for alert status
- Fire event for automations
- Automatic fallback between data sources
- Fully configurable via Home Assistant UI

## Installation

### HACS

1. Add this repository as a custom repository in HACS (Integration category)
2. Install "Chile Earthquakes"
3. Restart HA
4. Add via Settings → Devices & Services

### Manual

Copy `custom_components/chile_earthquakes` to your `custom_components` directory.

## Entities

- `sensor.chile_last_earthquake` — magnitude (Mw) with attributes: place, depth, coordinates, source, time, image URL, info URL
- `binary_sensor.chile_earthquake_alert` — ON when a new earthquake >= threshold is detected

## Automation Event

`chile_earthquakes_new_event` is fired for each new earthquake above the threshold.

## Options (via UI)

| Option | Default | Range |
|--------|---------|-------|
| Primary source | auto | auto / boostr / usgs |
| Alert threshold | 4.5 | 3.0 – 8.0 |
| Polling interval | 30s | 10 – 300s |
| Alert reset | 10 min | 1 – 60 min |

## License

GPL-3.0
