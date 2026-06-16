# HA Chile Earthquakes — Agent Guide

## Architecture

Single HA custom component at `custom_components/chile_earthquakes/`. Polling coordinator with sensor + binary_sensor + fire_event.

### Data-source chain (api.py)

1. **Boostr.cl** (`api.boostr.cl/earthquake.json`) — primary, wraps CSN
2. **USGS** GeoJSON `all_hour.geojson` — filtered by Chile bbox
3. **Sismologia.cl** — HTML scrape via BeautifulSoup

### HA entrypoints

- `__init__.py` — `async_setup_entry`, creates `EarthquakeAPI` + `ChileEarthquakeCoordinator`
- `config_flow.py` — `ConfigFlow` + `OptionsFlow` for UI config
- `coordinator.py` — `DataUpdateCoordinator`, polls every 30s, fires `chile_earthquakes_new_event`
- `sensor.py` — magnitude as `native_value`, attributes in `extra_state_attributes`
- `binary_sensor.py` — safety device_class, reflects `coordinator.alert_active`

## CI / Validation

Workflows in `.github/workflows/`:

| File | Trigger | Jobs |
|------|---------|------|
| `validate.yaml` | PR + push to `main` | semantic PR title, hassfest, HACS action, ruff lint |
| `release.yaml` | push to `main` | `python-semantic-release@v10` → bumps version in `manifest.json:version`, creates tag + GH release |

## Commands

```bash
ruff check custom_components/chile_earthquakes/
ruff format --check custom_components/chile_earthquakes/
```

No test framework is set up. No dev server.

## HACS & publishing gotchas

- **manifest.json** keys must be ordered: `domain`, `name`, then **alphabetical** (hassfest enforces this)
- **hacs.json** — no extra keys beyond standard fields (`name`, `content_in_root`, `country`, `render_readme`, `hide_default_branch`, `homeassistant`, `iot_class`)
- **Brand assets** — `icon.png` + `logo.png` (256x256) **must exist in repo root** or HACS validation fails
- **GitHub topics** — must be set manually in repo settings (`hacs`, `home-assistant`, `chile`, `earthquake`, `custom-component`)
- **`beautifulsoup4>=4.12.0`** is declared in `manifest.json` requirements
- **Version** is managed by `python-semantic-release`, not edited manually. Bumped automatically via `pyproject.toml` config targeting `manifest.json:version`
- **Semantic-release config** lives in `pyproject.toml` under `[tool.semantic_release]`

## Translations

- `translations/en.json` — English
- `translations/es.json` — Spanish
- `strings.json` — source of truth mirroring en.json

## Config Flow options

| Key | Type | Default |
|-----|------|---------|
| `primary_source` | auto/boostr/usgs | auto |
| `alert_threshold` | float 3.0–8.0 | 4.5 |
| `scan_interval` | int 10–300s | 30 |
| `alert_reset_minutes` | int 1–60 | 10 |
