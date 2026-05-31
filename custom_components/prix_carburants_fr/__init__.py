"""Carburants Prix integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "prix_carburants_fr"
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up entry."""
    hass.data[DOMAIN][entry.entry_id] = entry.data
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True
