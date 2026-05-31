"""Config flow for prix_carburants_fr."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "prix_carburants_fr"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for prix_carburants_fr."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle a user step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Prix Carburants France",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("tracker_entity"): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="device_tracker")
                    ),
                    vol.Required("name", default="Prix Carburants"): str,
                    vol.Optional("rayon_km", default="20"): str,
                    vol.Optional("nb_stations", default="5"): str,
                }
            ),
        )
