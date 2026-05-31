"""Carburants Prix integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import PrixCarburantsFRCoordinator

DOMAIN = "prix_carburants_fr"
_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up component."""
    _LOGGER.debug("async_setup called")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up entry."""
    _LOGGER.info("🔧 async_setup_entry START for %s", entry.entry_id)

    # Ensure hass.data[DOMAIN] exists
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.debug("✅ hass.data[DOMAIN] initialized")

    # Create coordinator
    _LOGGER.info("📍 Creating coordinator...")
    coordinator = PrixCarburantsFRCoordinator(hass, entry.data)
    _LOGGER.info("✅ Coordinator created: %s", coordinator)

    # Do first refresh (this is where it can fail)
    try:
        _LOGGER.info("🔄 Starting first refresh...")
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.info("✅ First refresh complete")
    except Exception as err:
        _LOGGER.error("❌ Failed to fetch initial data: %s", err)
        # Continue anyway - sensor will show error state

    # Store coordinator for platform to use
    _LOGGER.info("💾 Storing coordinator in hass.data[%s][%s]", DOMAIN, entry.entry_id)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    _LOGGER.info("✅ Coordinator stored. Keys in hass.data[DOMAIN]: %s", list(hass.data[DOMAIN].keys()))

    # Forward to platforms
    _LOGGER.info("⏭️ Forwarding to platforms: %s", PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("✅ async_setup_entry COMPLETE for %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
