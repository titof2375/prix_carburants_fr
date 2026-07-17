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
    if not entry.runtime_data or "coordinator" not in entry.runtime_data:
        _LOGGER.error("Coordinator not in entry.runtime_data!")
        return

    coordinator: PrixCarburantsFRCoordinator = entry.runtime_data["coordinator"]
    if coordinator is None:
        _LOGGER.error("Coordinator is None")
        return

    sensors = []
    if coordinator.last_update_success:
        stations = coordinator.data.get("stations", [])
        _LOGGER.debug("Creating %d station sensors...", len(stations))
        for i, station in enumerate(stations, 1):
            sensors.append(StationSensor(coordinator, entry.entry_id, i))

    if sensors:
        async_add_entities(sensors, True)
        _LOGGER.info("%d station sensors created", len(sensors))
    else:
        _LOGGER.warning("No stations found to create sensors")


def _extract_fuel_data(record: dict) -> dict:
    """Pull every '<fuel>_prix' / '<fuel>_maj' pair present in the record.

    The government dataset exposes one price column and one update-timestamp
    column per fuel (e.g. gazole_prix / gazole_maj, sp95_prix / sp95_maj).
    Extracting by suffix instead of a hardcoded fuel list makes this robust
    to fuels being added/renamed on the source side.
    """
    prices = {}
    dates = {}
    for key, value in record.items():
        if value in (None, ""):
            continue
        if key.endswith("_prix"):
            fuel = key[: -len("_prix")]
            prices[fuel] = value
        elif key.endswith("_maj"):
            fuel = key[: -len("_maj")]
            dates[fuel] = value
    return {"prices": prices, "dates": dates}


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
        self._attr_name = f"Station {index}"

    def _get_station(self) -> dict:
        """Get current station data from coordinator."""
        if not self.coordinator.last_update_success:
            return {}
        stations = self.coordinator.data.get("stations", [])
        if self._index > len(stations) or self._index < 1:
            return {}
        return stations[self._index - 1]  # Convert 1-indexed to 0-indexed

    @property
    def state(self) -> str:
        """Return the state - station address."""
        if not self.coordinator.last_update_success:
            return "error"
        station = self._get_station()
        if not station:
            return "error"
        cp = station.get("cp", "")
        ville = station.get("ville", "")
        return f"{cp} {ville}".strip()

    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes with full station details, including per-fuel price + date."""
        if not self.coordinator.last_update_success:
            return {"error": "No data"}
        station = self._get_station()
        if not station:
            return {"error": "Station not found"}

        fuel_data = _extract_fuel_data(station)

        attrs = {
            "name": station.get("nom") or station.get("adresse", "N/A"),
            "address": station.get("adresse", "N/A"),
            "postal_code": station.get("cp", "N/A"),
            "city": station.get("ville", "N/A"),
            "latitude": station.get("latitude", "N/A"),
            "longitude": station.get("longitude", "N/A"),
            "index": self._index,
        }

        # prix_gazole, prix_sp95, ... / date_gazole, date_sp95, ...
        for fuel, price in fuel_data["prices"].items():
            attrs[f"prix_{fuel}"] = price
        for fuel, maj in fuel_data["dates"].items():
            attrs[f"date_{fuel}"] = maj

        return attrs

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:gas-station"
