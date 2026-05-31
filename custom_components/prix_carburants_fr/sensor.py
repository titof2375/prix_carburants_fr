"""Sensor for Prix Carburants France."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PrixCarburantsFRCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.info("Setting up sensor for %s", entry.entry_id)

    coordinator = PrixCarburantsFRCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    name = entry.data.get("name", "Prix Carburants")
    sensor = PrixCarburantsSensor(coordinator, entry.entry_id, name)
    async_add_entities([sensor], True)


class PrixCarburantsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Prix Carburants France."""

    def __init__(self, coordinator: PrixCarburantsFRCoordinator, entry_id: str, name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_sensor_{entry_id}"
        self._attr_name = name

    @property
    def state(self) -> str:
        """Return the state - number of stations."""
        if self.coordinator.last_update_success:
            count = self.coordinator.data.get("count", 0)
            return f"{count} stations"
        return "error"

    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes with station details."""
        if not self.coordinator.last_update_success:
            return {"error": "No data"}

        stations = self.coordinator.data.get("stations", [])
        attrs = {"count": len(stations)}

        # Add each station
        for i, station in enumerate(stations, 1):
            fields = station.get("fields", {})
            attrs[f"station_{i}_name"] = fields.get("nom", "N/A")
            attrs[f"station_{i}_address"] = f"{fields.get('cp', '')} {fields.get('ville', '')}"
            attrs[f"station_{i}_distance"] = f"{fields.get('distance', 0):.0f}m"

        return attrs

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:gas-cylinder"
