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

# API v2.1 (Opendatasoft) - remplace l'ancienne API records/1.0 qui est
# en cours de dépréciation. Le paramètre geofilter.distance reste
# supporté pour compatibilité avec les recherches géographiques.
API_URL = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "prix-des-carburants-en-france-flux-instantane-v2/records"
)


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
            try:
                rayon_km = int(self.config.get("rayon_km", 20))
                nb_stations = int(self.config.get("nb_stations", 5))
            except (ValueError, TypeError) as err:
                _LOGGER.error("Invalid rayon_km or nb_stations: %s", err)
                raise UpdateFailed(f"Invalid configuration: {err}") from err

            # Get tracker location
            state = self.hass.states.get(tracker_entity)
            if not state:
                _LOGGER.warning("Entity %s not found", tracker_entity)
                return {"stations": [], "count": 0, "latitude": 0, "longitude": 0}

            lat = state.attributes.get("latitude")
            lon = state.attributes.get("longitude")

            if lat is None or lon is None:
                location = state.attributes.get("location")
                if location and isinstance(location, (list, tuple)) and len(location) >= 2:
                    lat, lon = location[0], location[1]
                    _LOGGER.info("Got location from array: %.4f, %.4f", lat, lon)

            if lat is None or lon is None:
                _LOGGER.warning(
                    "No location data from %s (attributes: %s)",
                    tracker_entity,
                    state.attributes,
                )
                return {"stations": [], "count": 0, "latitude": 0, "longitude": 0}

            _LOGGER.info("Fetching stations from %.4f, %.4f", lat, lon)

            async with aiohttp.ClientSession() as session:
                params = {
                    "geofilter.distance": f"{lat},{lon},{rayon_km * 1000}",
                    "limit": nb_stations,
                }
                async with session.get(
                    API_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"API error: {resp.status}")
                    data = await resp.json()

            # L'API v2.1 renvoie les enregistrements "à plat" sous "results"
            # (contrairement à v1 qui les imbriquait sous record.fields).
            records = data.get("results", [])
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
