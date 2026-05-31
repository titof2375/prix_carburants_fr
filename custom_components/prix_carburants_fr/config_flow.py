"""Config flow for Prix Carburants France."""
import voluptuous as vol
from homeassistant import config_entries


class PrixCarburantsFRConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Prix Carburants France."""

    VERSION = 1
    domain = "prix_carburants_fr"

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Prix Carburants France",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
