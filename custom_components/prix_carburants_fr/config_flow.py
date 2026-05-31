"""Config flow for prix_carburants_fr."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

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
            data_schema=vol.Schema({}),
        )
