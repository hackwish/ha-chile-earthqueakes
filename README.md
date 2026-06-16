# Chile Earthquakes

[![Validate](https://github.com/hackwish/ha-chile-earthquakes/actions/workflows/validate.yaml/badge.svg)](https://github.com/hackwish/ha-chile-earthquakes/actions/workflows/validate.yaml)
[![Release](https://github.com/hackwish/ha-chile-earthquakes/actions/workflows/release.yaml/badge.svg)](https://github.com/hackwish/ha-chile-earthquakes/actions/workflows/release.yaml)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![hassfest](https://img.shields.io/badge/hassfest-passed-41BDF5.svg)](https://developers.home-assistant.io)

Home Assistant integration for monitoring and alerting on the latest earthquakes in Chile. **Verified via HACS Validation and Hassfest Validation** in CI.

**Data sources**: [CSN / Sismologia.cl](https://www.sismologia.cl/) via [Boostr.cl](https://api.boostr.cl) (primary), [USGS](https://earthquake.usgs.gov) (fallback), and direct scraping of [Sismologia.cl](https://www.sismologia.cl/) (last resort).

## Features

- Real-time earthquake monitoring (30s polling by default)
- Configurable alert threshold
- Binary sensor for alert status (`binary_sensor.chile_earthquake_alert`)
- Fire event (`chile_earthquakes_new_event`) for automations
- Automatic fallback between data sources (Boostr → USGS → sismologia.cl)
- Fully configurable via Home Assistant UI

## Installation

### HACS (recommended)

1. Add `https://github.com/hackwish/ha-chile-earthquakes` as a custom repository (category: **Integration**)
2. Find **Chile Earthquakes** in HACS → Integrations and click Install
3. Restart Home Assistant
4. Go to **Settings → Devices & Services → Add Integration** and search for **Chile Earthquakes**

### Manual

Copy `custom_components/chile_earthquakes/` to your Home Assistant `custom_components/` directory and restart.

## Entities

| Entity | Description |
|--------|-------------|
| `sensor.chile_last_earthquake` | Magnitude (Mw) with attributes: place, depth, coordinates, source, time, image URL, info URL |
| `binary_sensor.chile_earthquake_alert` | ON when a new earthquake ≥ threshold is detected |

## Automation Event

Use `chile_earthquakes_new_event` in your automations:

```yaml
alias: "Earthquake Notification"
triggers:
  - trigger: event
    event_type: chile_earthquakes_new_event
actions:
  - service: notify.mobile_app
    data:
      title: "⚠️ M{{ trigger.event.data.magnitude }} - {{ trigger.event.data.place }}"
      message: "Depth: {{ trigger.event.data.depth }}km | Source: {{ trigger.event.data.source }}"
```

## Options (via UI)

| Option | Default | Range |
|--------|---------|-------|
| Primary source | auto | auto / boostr / usgs |
| Alert threshold | 4.5 Mw | 3.0 – 8.0 |
| Polling interval | 30s | 10 – 300s |
| Alert auto-reset | 10 min | 1 – 60 min |

## Validation

This integration passes both **HACS Validation** and **Hassfest Validation** on every PR and push to `main`. The CI pipeline also runs **Ruff** (Python linter) and enforces **Conventional Commits** on PR titles. Semantic releases are automated via `python-semantic-release`.

## License

GPL-3.0
