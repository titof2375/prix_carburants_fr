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
    _LOGGER.warning("🎨 sensor.async_setup_entry START for %s", entry.entry_id)

    # Get coordinator from entry.runtime_data (Home Assistant way!)
    if not entry.runtime_data or "coordinator" not in entry.runtime_data:
        _LOGGER.error("❌ Coordinator not in entry.runtime_data!")
        return

    coordinator: PrixCarburantsFRCoordinator = entry.runtime_data["coordinator"]
    _LOGGER.warning("✅ Got coordinator from entry.runtime_data!")

    if coordinator is None:
        _LOGGER.error("❌ Coordinator is None")
        return

    # Create one sensor per station
    sensors = []

    if coordinator.last_update_success:
        stations = coordinator.data.get("stations", [])
        _LOGGER.warning("🎨 Creating %d station sensors...", len(stations))

        for i, station in enumerate(stations, 1):
            sensor = StationSensor(coordinator, entry.entry_id, station, i)
            sensors.append(sensor)
            _LOGGER.warning("🎨 Created sensor for station %d", i)

    if sensors:
        async_add_entities(sensors, True)
        _LOGGER.warning("✅✅✅ %d STATION SENSORS CREATED AND ADDED!", len(sensors))
    else:
        _LOGGER.warning("⚠️ No stations found to create sensors")


class StationSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a single fuel station."""

    def __init__(
        self,
        coordinator: PrixCarburantsFRCoordinator,
        entry_id: str,
        station: dict,
        index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station = station
        self._index = index

        fields = station.get("fields", {})
        station_name = fields.get("nom", f"Station {index}")

        self._attr_unique_id = f"{DOMAIN}_{entry_id}_station_{index}"
        self._attr_name = station_name

    @property
    def state(self) -> str:
        """Return the state - station address."""
        if not self.coordinator.last_update_success:
            return "error"

        fields = self._station.get("fields", {})
        cp = fields.get("cp", "")
        ville = fields.get("ville", "")
        return f"{cp} {ville}".strip()

    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes with full station details."""
        if not self.coordinator.last_update_success:
            return {"error": "No data"}

        fields = self._station.get("fields", {})

        attrs = {
            "name": fields.get("nom", "N/A"),
            "address": fields.get("adresse", "N/A"),
            "postal_code": fields.get("cp", "N/A"),
            "city": fields.get("ville", "N/A"),
            "distance_m": f"{fields.get('distance', 0):.0f}",
            "latitude": fields.get("latitude", "N/A"),
            "longitude": fields.get("longitude", "N/A"),
            "index": self._index,
        }

        return attrs

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:gas-cylinder"
