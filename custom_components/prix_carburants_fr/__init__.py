"""Carburants Prix Test integration."""
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "carburants_prix_test"


async def async_setup(hass, config):
    """Set up the integration from YAML config."""
    _LOGGER.info("Carburants Prix Test integration loaded")
    return True
