import logging
from typing import Any, Dict

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
    """Set up sensors."""
    coordinator: PrixCarburantsFRCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # Phone location sensors
    if coordinator.data.get("stations_phone"):
        for idx, station in enumerate(coordinator.data["stations_phone"]):
            entities.append(
                PrixCarburantsSensor(
                    coordinator,
                    entry.entry_id,
                    station,
                    location="phone",
                    index=idx,
                )
            )

    # Home location sensors
    if coordinator.data.get("stations_maison"):
        for idx, station in enumerate(coordinator.data["stations_maison"]):
            entities.append(
                PrixCarburantsSensor(
                    coordinator,
                    entry.entry_id,
                    station,
                    location="maison",
                    index=idx,
                )
            )

    async_add_entities(entities, True)


class PrixCarburantsSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: PrixCarburantsFRCoordinator,
        entry_id: str,
        station: Dict[str, Any],
        location: str,
        index: int,
    ) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.station = station
        self.location = location
        self.index = index
        self._attr_unique_id = f"{DOMAIN}_{location}_{index}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.station['name']} ({self.location})"

    @property
    def state(self) -> str | None:
        """Return the state."""
        # Get cheapest fuel price
        min_price = None
        for fuel_data in self.station.get("fuels", {}).values():
            price = fuel_data.get("price")
            if price:
                try:
                    price_float = float(price)
                    if min_price is None or price_float < min_price:
                        min_price = price_float
                except (ValueError, TypeError):
                    continue
        return f"{min_price:.3f}" if min_price else "N/A"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return attributes."""
        attrs = {
            "nom_station": self.station.get("name"),
            "marque": self.station.get("brand"),
            "adresse": self.station.get("address"),
            "latitude": self.station.get("latitude"),
            "longitude": self.station.get("longitude"),
            "distance_km": self.station.get("distance"),
            "derniere_maj": self.station.get("updated_at"),
            "location": self.location,
        }

        # Add all fuel prices
        for fuel_name, fuel_data in self.station.get("fuels", {}).items():
            attrs[f"prix_{fuel_name}"] = fuel_data.get("price")
            attrs[f"date_{fuel_name}"] = fuel_data.get("date")

        return attrs

    @property
    def unit_of_measurement(self) -> str:
        """Return unit."""
        return "€/L"

    @property
    def icon(self) -> str:
        """Return icon."""
        return "mdi:gas-cylinder"
