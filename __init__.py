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
        # Create coordinator FIRST (before any setdefault that might reset)
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

        # Initialize hass.data[DOMAIN] ONLY if it doesn't exist
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
            _LOGGER.warning("✅ Created hass.data[DOMAIN]")
        else:
            _LOGGER.warning("✅ hass.data[DOMAIN] already exists")

        # Store coordinator
        _LOGGER.warning("💾 Storing coordinator for %s...", entry.entry_id)
        hass.data[DOMAIN][entry.entry_id] = coordinator
        _LOGGER.warning("✅ Coordinator STORED. Keys now: %s", list(hass.data[DOMAIN].keys()))

        # Forward to platforms AFTER storing coordinator
        _LOGGER.warning("⏭️ Forwarding to platforms...")
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.warning("✅ SETUP COMPLETE! Final keys: %s", list(hass.data[DOMAIN].keys()))
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
