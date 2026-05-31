"""Data coordinator for Prix Carburants France."""
import logging
from datetime import timedelta

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

API_URL = "https://data.economie.gouv.fr/api/records/1.0/search/"
API_DATASET = "prix-des-carburants-en-france-flux-instantane-v2"


class PrixCarburantsFRCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from API."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="prix_carburants_fr",
            update_interval=timedelta(minutes=10),
        )
        self.config = config

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            if not AIOHTTP_AVAILABLE:
                _LOGGER.warning("aiohttp not available, returning mock data")
                return {
                    "stations": [],
                    "count": 0,
                    "latitude": 0,
                    "longitude": 0,
                }

            tracker_entity = self.config.get("tracker_entity", "")
            rayon_km = int(self.config.get("rayon_km", 20))
            nb_stations = int(self.config.get("nb_stations", 5))

            # Get tracker location
            state = self.hass.states.get(tracker_entity)
            if not state:
                _LOGGER.warning("Tracker %s not found", tracker_entity)
                return {"stations": [], "count": 0, "latitude": 0, "longitude": 0}

            lat = state.attributes.get("latitude")
            lon = state.attributes.get("longitude")
            if lat is None or lon is None:
                _LOGGER.warning("No location data from tracker")
                return {"stations": [], "count": 0, "latitude": 0, "longitude": 0}

            _LOGGER.info("Fetching stations from %.2f, %.2f", lat, lon)

            # Fetch from API
            async with aiohttp.ClientSession() as session:
                params = {
                    "dataset": API_DATASET,
                    "rows": 100,
                    "geofilter.distance": f"{lat},{lon},{rayon_km * 1000}",
                }
                async with session.get(API_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"API error: {resp.status}")
                    data = await resp.json()

            records = data.get("records", [])[:nb_stations]
            _LOGGER.info("Found %d stations", len(records))

            return {
                "stations": records,
                "count": len(records),
                "latitude": lat,
                "longitude": lon,
            }

        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            return {"stations": [], "count": 0, "latitude": 0, "longitude": 0}
