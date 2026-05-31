import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector



class PrixCarburantsFRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_TRACKER_ENTITY, "Prix Carburants"),
                data={
                    CONF_TRACKER_ENTITY: user_input[CONF_TRACKER_ENTITY],
                    CONF_RAYON_KM: int(user_input.get(CONF_RAYON_KM, 20)),
                    CONF_NB_STATIONS: int(user_input.get(CONF_NB_STATIONS, 5)),
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_TRACKER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="device_tracker")
                ),
                    selector.EntitySelectorConfig(domain="zone")
                ),
                vol.Required(CONF_RAYON_KM, default=20): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
                vol.Required(CONF_NB_STATIONS, default=5): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
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
                    vol.Required(
                        CONF_RAYON_KM,
                        default=self.config_entry.data.get(CONF_RAYON_KM, 20),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
                    vol.Required(
                        CONF_NB_STATIONS,
                        default=self.config_entry.data.get(CONF_NB_STATIONS, 5),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
                }
            ),
        )
