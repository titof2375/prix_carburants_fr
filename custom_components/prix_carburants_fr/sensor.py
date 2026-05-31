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

    sensor = PrixCarburantsSensor(entry.entry_id, entry.title)
    async_add_entities([sensor], True)


class PrixCarburantsSensor(SensorEntity):
    """Sensor for Prix Carburants France."""

    def __init__(self, entry_id: str, title: str) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{DOMAIN}_{entry_id}"
        self._attr_name = title
        self._attr_state = "Initializing"

    @property
    def state(self) -> str:
        """Return the state."""
        return self._attr_state

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        return {
            "integration": DOMAIN,
        }
