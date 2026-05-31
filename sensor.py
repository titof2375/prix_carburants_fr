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
            sensor = StationSensor(coordinator, entry.entry_id, i)
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
        index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._index = index

        self._attr_unique_id = f"{DOMAIN}_{entry_id}_station_{index}"

    def _get_station(self) -> dict:
        """Get current station data from coordinator."""
        if not self.coordinator.last_update_success:
            return {}

        stations = self.coordinator.data.get("stations", [])
        if self._index > len(stations) or self._index < 1:
            return {}

        return stations[self._index - 1]  # Convert 1-indexed to 0-indexed

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        station = self._get_station()
        fields = station.get("fields", {})
        return fields.get("nom", f"Station {self._index}")

    @property
    def state(self) -> str:
        """Return the state - station address."""
        if not self.coordinator.last_update_success:
            return "error"

        station = self._get_station()
        if not station:
            return "error"

        fields = station.get("fields", {})
        cp = fields.get("cp", "")
        ville = fields.get("ville", "")
        return f"{cp} {ville}".strip()

    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes with full station details."""
        if not self.coordinator.last_update_success:
            return {"error": "No data"}

        station = self._get_station()
        if not station:
            return {"error": "Station not found"}

        fields = station.get("fields", {})

        # Format last update time
        last_updated = "N/A"
        if self.coordinator.last_update_success_time:
            last_updated = self.coordinator.last_update_success_time.strftime("%d/%m/%Y %H:%M:%S")

        attrs = {
            "name": fields.get("nom", "N/A"),
            "address": fields.get("adresse", "N/A"),
            "postal_code": fields.get("cp", "N/A"),
            "city": fields.get("ville", "N/A"),
            "distance_m": f"{fields.get('distance', 0):.0f}",
            "latitude": fields.get("latitude", "N/A"),
            "longitude": fields.get("longitude", "N/A"),
            "last_updated": last_updated,
            "index": self._index,
        }

        return attrs

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:gas-cylinder"
