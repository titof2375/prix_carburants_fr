"""Constants for Prix Carburants France integration."""

DOMAIN = "carburants_prix_test"

CONF_TRACKER_ENTITY = "tracker_entity"
CONF_RAYON_KM = "rayon_km"
CONF_NB_STATIONS = "nb_stations"

DEFAULT_RAYON_KM = 20
DEFAULT_NB_STATIONS = 5

API_URL = "https://data.economie.gouv.fr/api/records/1.0/search/"
API_DATASET = "prix-des-carburants-en-france-flux-instantane-v2"
UPDATE_INTERVAL = 10
