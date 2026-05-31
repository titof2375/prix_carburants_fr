"""Config flow for Prix Carburants France."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from typing import Any, Dict, Optional

DOMAIN = "prix_carburants_fr"


class ConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow."""

    VERSION = 1
    domain = DOMAIN

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle user step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Prix Carburants France",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
