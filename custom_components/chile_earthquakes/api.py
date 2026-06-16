from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import aiohttp
from bs4 import BeautifulSoup

from .const import (
    BOOSTR_URL,
    CHILE_MAX_LAT,
    CHILE_MAX_LON,
    CHILE_MIN_LAT,
    CHILE_MIN_LON,
    LOGGER,
    SISMOLOGIA_URL,
    USGS_URL,
)


@dataclass
class EarthquakeData:
    magnitude: float
    depth: float
    place: str
    latitude: float
    longitude: float
    time: datetime
    source: str
    event_id: Optional[str] = None
    image_url: Optional[str] = None
    info_url: Optional[str] = None


class EarthquakeAPI:
    def __init__(self, session: aiohttp.ClientSession, primary_source: str = "auto") -> None:
        self.session = session
        self.primary_source = primary_source

    async def get_latest(self) -> Optional[EarthquakeData]:
        if self.primary_source == "boostr":
            chain = [
                self._fetch_boostr,
                self._fetch_usgs,
                self._fetch_sismologia,
            ]
        elif self.primary_source == "usgs":
            chain = [
                self._fetch_usgs,
                self._fetch_boostr,
                self._fetch_sismologia,
            ]
        else:
            chain = [
                self._fetch_boostr,
                self._fetch_usgs,
                self._fetch_sismologia,
            ]

        for fetcher in chain:
            try:
                data = await fetcher()
                if data is not None:
                    LOGGER.debug("Got data from %s: M%s at %s", data.source, data.magnitude, data.place)
                    return data
            except Exception as exc:
                LOGGER.warning("Fetcher %s failed: %s", fetcher.__name__, exc)
                continue
        return None

    async def _fetch_boostr(self) -> Optional[EarthquakeData]:
        async with self.session.get(BOOSTR_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            data: dict[str, Any] = await resp.json()
        if data.get("status") != "success":
            return None
        d = data["data"]
        try:
            return EarthquakeData(
                magnitude=float(d["magnitude"]),
                depth=float(str(d["depth"]).split()[0]),
                place=str(d["place"]),
                latitude=float(d["latitude"]),
                longitude=float(d["longitude"]),
                time=datetime.fromisoformat(f"{d['date']}T{d['hour']}"),
                source="boostr",
                event_id=d.get("event_id"),
                image_url=d.get("image"),
                info_url=d.get("info"),
            )
        except (KeyError, ValueError, TypeError) as exc:
            LOGGER.warning("Failed to parse boostr response: %s", exc)
            return None

    async def _fetch_usgs(self) -> Optional[EarthquakeData]:
        async with self.session.get(USGS_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            data: dict[str, Any] = await resp.json()
        features = data.get("features", [])
        if not features:
            return None
        chile_events = []
        for f in features:
            props = f.get("properties", {})
            coords = f.get("geometry", {}).get("coordinates", [])
            if len(coords) < 2:
                continue
            lon, lat = coords[0], coords[1]
            if CHILE_MIN_LAT <= lat <= CHILE_MAX_LAT and CHILE_MIN_LON <= lon <= CHILE_MAX_LON:
                chile_events.append(f)
        if not chile_events:
            return None
        chile_events.sort(key=lambda x: x.get("properties", {}).get("time", 0), reverse=True)
        latest = chile_events[0]
        props = latest["properties"]
        coords = latest["geometry"]["coordinates"]
        try:
            return EarthquakeData(
                magnitude=float(props.get("mag", 0)),
                depth=float(coords[2]) if len(coords) > 2 else 0.0,
                place=str(props.get("place", "Unknown")),
                latitude=float(coords[1]),
                longitude=float(coords[0]),
                time=datetime.utcfromtimestamp(props["time"] / 1000) if props.get("time") else datetime.utcnow(),
                source="usgs",
                event_id=str(latest.get("id", "")),
                info_url=str(props.get("url", "")),
            )
        except (KeyError, ValueError, TypeError) as exc:
            LOGGER.warning("Failed to parse USGS response: %s", exc)
            return None

    async def _fetch_sismologia(self) -> Optional[EarthquakeData]:
        headers = {"User-Agent": "ha-chile-earthquakes/0.1.0 (hackwish)"}
        async with self.session.get(
            SISMOLOGIA_URL, timeout=aiohttp.ClientTimeout(total=15), headers=headers
        ) as resp:
            resp.raise_for_status()
            html = await resp.text()
        try:
            soup = BeautifulSoup(html, "html.parser")
            tables = soup.find_all("table")
            quake_table: Any = None
            for tbl in tables:
                header = tbl.find("tr")
                if header and "fecha" in header.get_text(strip=True).lower():
                    quake_table = tbl
                    break
            if quake_table is None:
                LOGGER.warning("Could not find earthquake table on sismologia.cl")
                return None
            rows = quake_table.find_all("tr")
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) < 3:
                    continue
                raw_text = cells[0].get_text(strip=True)
                depth_raw = cells[1].get_text(strip=True)
                mag_raw = cells[2].get_text(strip=True)
                parts = raw_text.split(" ", 2)
                if len(parts) < 3:
                    continue
                date_str = f"{parts[0]}T{parts[1]}"
                place = parts[2]
                dt = datetime.fromisoformat(date_str)
                mag = float(mag_raw.split()[0])
                depth = float(depth_raw.split()[0])
                return EarthquakeData(
                    magnitude=mag,
                    depth=depth,
                    place=place,
                    latitude=0.0,
                    longitude=0.0,
                    time=dt,
                    source="sismologia",
                )
            LOGGER.warning("No earthquake rows found on sismologia.cl table")
            return None
        except Exception as exc:
            LOGGER.warning("Failed to parse sismologia.cl HTML: %s", exc)
            return None
