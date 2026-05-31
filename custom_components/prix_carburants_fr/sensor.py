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
    _LOGGER.info("Setting up sensor for %s", DOMAIN)

    name = entry.data.get("name", "Prix Carburants")
    tracker = entry.data.get("tracker_entity", "unknown")

    sensor = PrixCarburantsSensor(entry.entry_id, name, tracker)
    async_add_entities([sensor], True)

    _LOGGER.info("Sensor created: %s", sensor.entity_id)


class PrixCarburantsSensor(SensorEntity):
    """Sensor for Prix Carburants France."""

    def __init__(self, entry_id: str, name: str, tracker: str) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = f"{DOMAIN}_sensor_{entry_id}"
        self._attr_name = f"{name} Sensor"
        self._tracker = tracker

    @property
    def state(self) -> str:
        """Return the state."""
        return "0 stations"

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        return {
            "tracker_entity": self._tracker,
            "integration": DOMAIN,
        }

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:gas-cylinder"
