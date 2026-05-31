DOMAIN = "prix_carburants_fr"

CONF_GPS_MAISON_LAT = "gps_maison_lat"
CONF_GPS_MAISON_LON = "gps_maison_lon"
CONF_GPS_PHONE_LAT = "gps_phone_lat"
CONF_GPS_PHONE_LON = "gps_phone_lon"
CONF_RAYON_KM = "rayon_km"
CONF_NB_STATIONS = "nb_stations"

API_URL = "https://data.economie.gouv.fr/api/records/1.0/search/"
API_DATASET = "prix-des-carburants-en-france-flux-instantane-v2"

UPDATE_INTERVAL = 10  # minutes

FUEL_TYPES = {
    "Gazole (B7)": "gazole",
    "SP95": "sp95",
    "SP98": "sp98",
    "E85": "e85",
    "GPLc": "gplc",
    "SP95-E10": "sp95e10"
}
