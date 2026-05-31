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
    data = hass.data[DOMAIN][entry.entry_id]

    sensor = PrixCarburantsSensor(
        entry.entry_id,
        data.get("name", "Prix Carburants"),
        data.get("tracker_entity", "unknown"),
        data.get("rayon_km", "20"),
        data.get("nb_stations", "5"),
    )
    async_add_entities([sensor], True)


class PrixCarburantsSensor(SensorEntity):
    """Sensor for Prix Carburants France."""

    def __init__(self, entry_id: str, name: str, tracker: str, rayon: str, nb_stations: str) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{DOMAIN}_{entry_id}"
        self._attr_name = name
        self._tracker = tracker
        self._rayon = rayon
        self._nb_stations = nb_stations
        self._state = "waiting"

    @property
    def state(self) -> str:
        """Return the state."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        return {
            "tracker_entity": self._tracker,
            "rayon_km": self._rayon,
            "nb_stations": self._nb_stations,
            "integration": DOMAIN,
        }

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:gas-cylinder"
