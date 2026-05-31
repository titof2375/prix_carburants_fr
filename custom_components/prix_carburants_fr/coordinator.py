"""Data coordinator for Prix Carburants France."""
import logging
from datetime import timedelta
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PrixCarburantsFRCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from Prix Carburants API."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="prix_carburants_fr",
            update_interval=timedelta(minutes=UPDATE_INTERVAL),
        )
        self.config = config

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            tracker_entity = self.config.get("tracker_entity", "")
            rayon_km = int(self.config.get("rayon_km", 20))
            nb_stations = int(self.config.get("nb_stations", 5))

            # Get tracker location
            state = self.hass.states.get(tracker_entity)
            if not state:
                _LOGGER.warning("Tracker entity %s not found", tracker_entity)
                return {"stations": [], "count": 0, "error": "Tracker not found"}

            latitude = state.attributes.get("latitude")
            longitude = state.attributes.get("longitude")

            if latitude is None or longitude is None:
                _LOGGER.warning("No location data from tracker")
                return {"stations": [], "count": 0, "error": "No location"}

            _LOGGER.info("Fetching stations from %.2f, %.2f (radius: %d km)", latitude, longitude, rayon_km)

            # Mock data for testing - in real scenario, fetch from API
            # For now just return empty to avoid API errors
            return {
                "latitude": latitude,
                "longitude": longitude,
                "rayon_km": rayon_km,
                "stations": [],
                "count": 0,
                "error": None,
            }

        except Exception as err:
            _LOGGER.error("Error updating data: %s", err)
            return {"stations": [], "count": 0, "error": str(err)}
