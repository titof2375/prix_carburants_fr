"""Data coordinator for Prix Carburants France."""
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_URL, API_DATASET, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PrixCarburantsFRCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from Prix Carburants API."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL),
        )
        self.config = config

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            tracker_entity = self.config.get("tracker_entity")
            rayon_km = int(self.config.get("rayon_km", 20))
            nb_stations = int(self.config.get("nb_stations", 5))

            # Get tracker location
            state = self.hass.states.get(tracker_entity)
            if not state:
                return {
                    "error": f"Tracker entity {tracker_entity} not found",
                    "stations": [],
                }

            latitude = state.attributes.get("latitude")
            longitude = state.attributes.get("longitude")

            if not latitude or not longitude:
                return {"error": "No location data", "stations": []}

            # Fetch from API
            async with aiohttp.ClientSession() as session:
                params = {
                    "dataset": API_DATASET,
                    "rows": 500,
                    "geofilter.distance": f"{latitude},{longitude},{rayon_km * 1000}",
                }
                async with session.get(API_URL, params=params) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"API error: {resp.status}")
                    data = await resp.json()

            records = data.get("records", [])[:nb_stations]

            return {
                "latitude": latitude,
                "longitude": longitude,
                "rayon_km": rayon_km,
                "nb_stations": len(records),
                "stations": records,
                "error": None,
            }

        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")
