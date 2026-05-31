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
    coordinator: PrixCarburantsFRCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entity = PrixCarburantsSensor(coordinator, entry.entry_id, entry.title)
    async_add_entities([entity], True)


class PrixCarburantsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: PrixCarburantsFRCoordinator, entry_id: str, title: str) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.title = title
        self._attr_unique_id = f"{DOMAIN}_{entry_id}"

    @property
    def name(self) -> str:
        return self.title

    @property
    def state(self) -> str | None:
        stations = self.coordinator.data.get("stations", [])
        if not stations:
            return "N/A"
        
        min_price = None
        for station in stations:
            for fuel_data in station.get("fuels", {}).values():
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
        attrs = {
            "tracker_entity": self.coordinator.tracker_entity,
            "tracker_lat": self.coordinator.data.get("tracker_lat"),
            "tracker_lon": self.coordinator.data.get("tracker_lon"),
        }

        # Ajouter chaque station en attribut
        stations = self.coordinator.data.get("stations", [])
        for idx, station in enumerate(stations):
            attrs[f"station_{idx+1}_name"] = station.get("name")
            attrs[f"station_{idx+1}_brand"] = station.get("brand")
            attrs[f"station_{idx+1}_address"] = station.get("address")
            attrs[f"station_{idx+1}_distance_km"] = station.get("distance")
            
            # Prix des carburants
            for fuel_key, fuel_data in station.get("fuels", {}).items():
                attrs[f"station_{idx+1}_{fuel_key}_price"] = fuel_data.get("price")
                attrs[f"station_{idx+1}_{fuel_key}_date"] = fuel_data.get("date")

        return attrs

    @property
    def unit_of_measurement(self) -> str:
        return "€/L"

    @property
    def icon(self) -> str:
        return "mdi:gas-cylinder"
