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

    # NOTE: le premier refresh du coordinateur a lieu tres tot au demarrage
    # de HA, souvent AVANT que l'entite device_tracker suivie ne soit
    # chargee. Dans ce cas coordinator.data['stations'] est vide a cet
    # instant precis. Plutot que de ne creer les capteurs qu'une seule fois
    # ici (ce qui
