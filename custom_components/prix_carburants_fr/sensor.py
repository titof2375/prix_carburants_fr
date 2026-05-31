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
    coordinator = PrixCarburantsFRCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    sensor = PrixCarburantsSensor(coordinator, entry.entry_id, entry.data.get("name", "Prix Carburants"))
    async_add_entities([sensor], True)


class PrixCarburantsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Prix Carburants France."""

    def __init__(self, coordinator: PrixCarburantsFRCoordinator, entry_id: str, name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{entry_id}"
        self._attr_name = name
        self.entry_id = entry_id

    @property
    def state(self) -> str:
        """Return the state."""
        if self.coordinator.data.get("error"):
            return "error"
        return str(self.coordinator.data.get("nb_stations", 0))

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        data = self.coordinator.data
        stations = data.get("stations", [])

        # Format stations
        stations_list = []
        for i, station in enumerate(stations[:5], 1):
            fields = station.get("fields", {})
            stations_list.append({
                f"station_{i}_name": fields.get("nom", "N/A"),
                f"station_{i}_address": f"{fields.get('cp', '')} {fields.get('ville', '')}",
                f"station_{i}_distance": f"{fields.get('distance', 'N/A')}m",
            })

        # Merge all dicts
        attrs = {}
        for station_dict in stations_list:
            attrs.update(station_dict)

        attrs.update({
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "rayon_km": data.get("rayon_km"),
            "error": data.get("error"),
        })

        return attrs

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:gas-cylinder"
