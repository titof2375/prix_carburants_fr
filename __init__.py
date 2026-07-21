"""Carburants Prix integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
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

        # Store coordinator in entry.runtime_data (Home Assistant way!)
        entry.runtime_data = {"coordinator": coordinator}

        # Also store in hass.data for backward compat
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        hass.data[DOMAIN][entry.entry_id] = coordinator

        # Forward to platforms right away: sensor.py already knows how to
        # create its sensors later via a coordinator listener, so the
        # platform can be set up before any data exists.
        _LOGGER.warning("⏭️ Forwarding to platforms...")
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        # First refresh: at cold boot, device_tracker entities restored by
        # the mobile app integration are not guaranteed to exist yet when
        # this integration loads (they can load after us). Doing the first
        # refresh here would then permanently record "0 stations" until the
        # next scheduled update (10 min later). Instead, if HA hasn't
        # finished starting, wait for EVENT_HOMEASSISTANT_STARTED so every
        # other integration (including device_tracker) is guaranteed to be
        # loaded before we look up the tracked position.
        if hass.is_running:
            # Not a cold boot (e.g. manual integration reload) -> the entry
            # is still in SETUP_IN_PROGRESS here, so first_refresh is valid.
            try:
                _LOGGER.warning("🔄 Starting first refresh...")
                await coordinator.async_config_entry_first_refresh()
                _LOGGER.warning("✅ First refresh OK")
            except Exception as err:
                _LOGGER.error("❌ First refresh failed: %s", err)
        else:
            # Cold boot: by the time EVENT_HOMEASSISTANT_STARTED fires,
            # async_setup_entry has already returned and the entry is
            # LOADED, not SETUP_IN_PROGRESS - async_config_entry_first_refresh
            # would raise in that state, so use a plain refresh instead.
            # It still populates coordinator.data and notifies sensor.py's
            # listener exactly the same way.
            async def _do_refresh(_event=None) -> None:
                try:
                    _LOGGER.warning("🔄 Starting delayed refresh (HA fully started)...")
                    await coordinator.async_refresh()
                    _LOGGER.warning("✅ Delayed refresh OK")
                except Exception as err:
                    _LOGGER.error("❌ Delayed refresh failed: %s", err)

            entry.async_on_unload(
                hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _do_refresh)
            )

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
