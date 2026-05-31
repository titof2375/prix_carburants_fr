"""Carburants Prix integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

try:
    from .coordinator import PrixCarburantsFRCoordinator
except ImportError as e:
    import sys
    print(f"❌ IMPORT ERROR: {e}", file=sys.stderr)
    raise

DOMAIN = "prix_carburants_fr"
_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

_LOGGER.warning("⚠️ MODULE LOADED: prix_carburants_fr")


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up component."""
    _LOGGER.warning("⚠️ async_setup CALLED")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up entry."""
    _LOGGER.warning("⚠️⚠️⚠️ async_setup_entry CALLED for %s", entry.entry_id)

    try:
        # Create coordinator
        _LOGGER.warning("📍 Creating coordinator...")
        coordinator = PrixCarburantsFRCoordinator(hass, entry.data)
        _LOGGER.warning("✅ Coordinator created")

        # Do first refresh
        try:
            _LOGGER.warning("🔄 Starting first refresh...")
            await coordinator.async_config_entry_first_refresh()
            _LOGGER.warning("✅ First refresh OK")
        except Exception as err:
            _LOGGER.error("❌ First refresh failed: %s", err)

        # Store coordinator in entry.runtime_data (Home Assistant way!)
        _LOGGER.warning("💾 Storing coordinator in entry.runtime_data...")
        entry.runtime_data = {"coordinator": coordinator}
        _LOGGER.warning("✅ Coordinator STORED in entry.runtime_data")

        # Also store in hass.data for backward compat
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        hass.data[DOMAIN][entry.entry_id] = coordinator

        # Forward to platforms AFTER storing coordinator
        _LOGGER.warning("⏭️ Forwarding to platforms...")
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.warning("✅ SETUP COMPLETE!")
        return True

    except Exception as err:
        _LOGGER.exception("❌❌❌ EXCEPTION IN async_setup_entry: %s", err)
        raise


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
