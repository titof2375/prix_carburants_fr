import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_TRACKER_ENTITY, CONF_RAYON_KM, CONF_NB_STATIONS


class PrixCarburantsFRConfigFlow(config_entries.ConfigFlow):
    VERSION = 1
    domain = DOMAIN

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Prix Carburants France",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TRACKER_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="device_tracker")
                    ),
                    vol.Optional(CONF_RAYON_KM, default=20): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=100)
                    ),
                    vol.Optional(CONF_NB_STATIONS, default=5): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=20)
                    ),
                }
            ),
        )

    async def async_step_import(self, import_data):
        return await self.async_step_user(import_data)

    def async_get_options_flow(self, config_entry):
        return PrixCarburantsFROptionsFlow(config_entry)


class PrixCarburantsFROptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_RAYON_KM,
                        default=self.config_entry.data.get(CONF_RAYON_KM, 20),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
                    vol.Optional(
                        CONF_NB_STATIONS,
                        default=self.config_entry.data.get(CONF_NB_STATIONS, 5),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
                }
            ),
        )
