# Chile Earthquakes

Monitor and get alerts for the latest earthquakes in Chile.

## Data Sources

1. **[Boostr.cl](https://api.boostr.cl)** — Primary source. Wraps CSN (Centro Sismológico Nacional) data in a clean JSON API.
2. **[USGS](https://earthquake.usgs.gov)** — Fallback. USGS real-time GeoJSON feed filtered for the Chile region.
3. **[Sismologia.cl](https://www.sismologia.cl)** — Last resort. Official CSN website (HTML scraping).

## Installation

### Via HACS (recommended)

1. Go to **HACS → Integrations → Three-dot menu → Custom repositories**
2. Add this repository URL
3. Select category **Integration**
4. Click **Install**
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Add Integration**
7. Search for **Chile Earthquakes**

### Manual

Copy `custom_components/chile_earthquakes/` into your Home Assistant `custom_components/` directory and restart.

## Configuration

- **Primary data source**: auto (try boostr → USGS → sismologia.cl), boostr, or usgs
- **Alert magnitude threshold**: minimum magnitude to trigger the binary sensor (default: 4.5)
- **Polling interval**: how often to check for new data (default: 30s, range: 10-300s)
- **Alert auto-reset**: minutes before the alert binary sensor turns off automatically (default: 10min)

## Entities

| Entity | Description |
|--------|-------------|
| `sensor.chile_last_earthquake` | Latest earthquake magnitude with attributes (place, depth, coordinates, source, etc.) |
| `binary_sensor.chile_earthquake_alert` | On when a new earthquake above threshold is detected |

## Automation Event

The integration fires `chile_earthquakes_new_event` with the full earthquake payload. Use it in your automations:

```yaml
alias: "Earthquake Notification"
triggers:
  - trigger: event
    event_type: chile_earthquakes_new_event
actions:
  - action: notify.mobile_app
    data:
      title: "⚠️ Earthquake detected!"
      message: "M{{ trigger.event.data.magnitude }} - {{ trigger.event.data.place }}"
```

## License

GPL-3.0
