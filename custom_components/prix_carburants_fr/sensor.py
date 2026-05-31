"""Sensor for Prix Carburants France."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.info("Setting up sensor for %s", entry.entry_id)

    name = entry.data.get("name", "Prix Carburants")
    tracker = entry.data.get("tracker_entity", "unknown")

    # Create sensor immediately
    sensor = PrixCarburantsSensor(entry.entry_id, name, tracker, hass)
    async_add_entities([sensor], True)

    _LOGGER.info("Sensor created: %s", sensor.entity_id)

    # Try to fetch data in background (don't block sensor creation)
    hass.async_create_task(sensor.async_update_data())


class PrixCarburantsSensor(SensorEntity):
    """Sensor for Prix Carburants France."""

    def __init__(self, entry_id: str, name: str, tracker: str, hass: HomeAssistant) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{DOMAIN}_sensor_{entry_id}"
        self._attr_name = name
        self._tracker = tracker
        self._hass = hass
        self._state = "initializing"
        self._stations = []

    @property
    def state(self) -> str:
        """Return the state."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes."""
        return {
            "tracker_entity": self._tracker,
            "count": len(self._stations),
            "integration": DOMAIN,
        }

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:gas-cylinder"

    async def async_update_data(self) -> None:
        """Fetch data in background."""
        try:
            _LOGGER.info("Trying to fetch fuel stations...")

            state = self._hass.states.get(self._tracker)
            if not state:
                self._state = "tracker not found"
                return

            lat = state.attributes.get("latitude")
            lon = state.attributes.get("longitude")

            if lat is None or lon is None:
                self._state = "no location"
                return

            # Try to import aiohttp
            try:
                import aiohttp

                API_URL = "https://data.economie.gouv.fr/api/records/1.0/search/"
                API_DATASET = "prix-des-carburants-en-france-flux-instantane-v2"

                rayon_km = int(self._hass.data.get(DOMAIN, {}).get("rayon_km", 20)) if DOMAIN in self._hass.data else 20

                async with aiohttp.ClientSession() as session:
                    params = {
                        "dataset": API_DATASET,
                        "rows": 100,
                        "geofilter.distance": f"{lat},{lon},{rayon_km * 1000}",
                    }
                    async with session.get(API_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self._stations = data.get("records", [])
                            self._state = f"{len(self._stations)} stations"
                            _LOGGER.info("Found %d stations", len(self._stations))
                        else:
                            self._state = f"api error {resp.status}"

            except ImportError:
                self._state = "aiohttp not available"
                _LOGGER.warning("aiohttp not available")

        except Exception as err:
            self._state = "error"
            _LOGGER.error("Error fetching data: %s", err)
