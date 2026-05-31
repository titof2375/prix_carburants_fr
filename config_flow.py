import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_GPS_MAISON_LAT, CONF_GPS_MAISON_LON, CONF_GPS_PHONE_LAT, CONF_GPS_PHONE_LON, CONF_RAYON_KM, CONF_NB_STATIONS


class PrixCarburantsFRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            # Validate GPS coordinates
            try:
                gps_maison_lat = float(user_input[CONF_GPS_MAISON_LAT])
                gps_maison_lon = float(user_input[CONF_GPS_MAISON_LON])
                gps_phone_lat = float(user_input[CONF_GPS_PHONE_LAT])
                gps_phone_lon = float(user_input[CONF_GPS_PHONE_LON])

                if not (-90 <= gps_maison_lat <= 90) or not (-180 <= gps_maison_lon <= 180):
                    errors["base"] = "invalid_gps_maison"
                elif not (-90 <= gps_phone_lat <= 90) or not (-180 <= gps_phone_lon <= 180):
                    errors["base"] = "invalid_gps_phone"
            except (ValueError, TypeError):
                errors["base"] = "invalid_gps"

            if not errors:
                return self.async_create_entry(
                    title="Prix Carburants France",
                    data={
                        CONF_GPS_MAISON_LAT: float(user_input[CONF_GPS_MAISON_LAT]),
                        CONF_GPS_MAISON_LON: float(user_input[CONF_GPS_MAISON_LON]),
                        CONF_GPS_PHONE_LAT: float(user_input[CONF_GPS_PHONE_LAT]),
                        CONF_GPS_PHONE_LON: float(user_input[CONF_GPS_PHONE_LON]),
                        CONF_RAYON_KM: int(user_input[CONF_RAYON_KM]),
                        CONF_NB_STATIONS: int(user_input[CONF_NB_STATIONS]),
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_GPS_MAISON_LAT, default=46.57): float,
                vol.Required(CONF_GPS_MAISON_LON, default=2.42): float,
                vol.Required(CONF_GPS_PHONE_LAT, default=46.57): float,
                vol.Required(CONF_GPS_PHONE_LON, default=2.42): float,
                vol.Required(CONF_RAYON_KM, default=20): int,
                vol.Required(CONF_NB_STATIONS, default=5): int,
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
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_GPS_MAISON_LAT,
                        default=self.config_entry.data.get(CONF_GPS_MAISON_LAT),
                    ): float,
                    vol.Required(
                        CONF_GPS_MAISON_LON,
                        default=self.config_entry.data.get(CONF_GPS_MAISON_LON),
                    ): float,
                    vol.Required(
                        CONF_GPS_PHONE_LAT,
                        default=self.config_entry.data.get(CONF_GPS_PHONE_LAT),
                    ): float,
                    vol.Required(
                        CONF_GPS_PHONE_LON,
                        default=self.config_entry.data.get(CONF_GPS_PHONE_LON),
                    ): float,
                    vol.Required(
                        CONF_RAYON_KM,
                        default=self.config_entry.data.get(CONF_RAYON_KM, 20),
                    ): int,
                    vol.Required(
                        CONF_NB_STATIONS,
                        default=self.config_entry.data.get(CONF_NB_STATIONS, 5),
                    ): int,
                }
            ),
        )
