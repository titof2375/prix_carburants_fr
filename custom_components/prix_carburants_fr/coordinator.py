import logging
from datetime import timedelta
from typing import Any, Dict, List
import math

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, API_DATASET, UPDATE_INTERVAL, FUEL_TYPES

_LOGGER = logging.getLogger(__name__)


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


class PrixCarburantsFRCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        super().__init__(
            hass,
            _LOGGER,
            name="Prix Carburants France",
            update_interval=timedelta(minutes=UPDATE_INTERVAL),
        )
        self.config = config
        self.gps_maison = (config.get("gps_maison_lat"), config.get("gps_maison_lon"))
        self.gps_phone = (config.get("gps_phone_lat"), config.get("gps_phone_lon"))
        self.rayon = config.get("rayon_km", 20)
        self.nb_stations = config.get("nb_stations", 5)

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                # Fetch data near phone GPS
                stations_phone = await self._fetch_stations(session, self.gps_phone)

                # Fetch data near home GPS
                stations_maison = await self._fetch_stations(session, self.gps_maison)

                return {
                    "stations_phone": stations_phone,
                    "stations_maison": stations_maison,
                }
        except Exception as err:
            raise UpdateFailed(f"Error updating data: {err}")

    async def _fetch_stations(self, session: aiohttp.ClientSession, gps: tuple) -> List[Dict]:
        """Fetch stations near GPS coordinates."""
        lat, lon = gps

        params = {
            "dataset": API_DATASET,
            "q": "",
            "limit": 100,
        }

        async with session.get(API_URL, params=params) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"API returned {resp.status}")

            data = await resp.json()
            records = data.get("records", [])

            # Filter by radius and sort by price
            filtered = []
            for record in records:
                try:
                    fields = record.get("fields", {})
                    st_lat = fields.get("latitude")
                    st_lon = fields.get("longitude")

                    if not st_lat or not st_lon:
                        continue

                    distance = haversine(lat, lon, st_lat, st_lon)
                    if distance > self.rayon:
                        continue

                    # Extract fuel prices
                    fuels = {}
                    for fuel_name, fuel_key in FUEL_TYPES.items():
                        price_key = f"prix_{fuel_key}"
                        if price_key in fields:
                            fuels[fuel_key] = {
                                "price": fields.get(price_key),
                                "date": fields.get(f"date_{fuel_key}", "N/A"),
                            }

                    filtered.append({
                        "name": fields.get("nom_station", "Unknown"),
                        "brand": fields.get("marque", ""),
                        "address": fields.get("adresse", ""),
                        "latitude": st_lat,
                        "longitude": st_lon,
                        "distance": round(distance, 2),
                        "fuels": fuels,
                        "updated_at": fields.get("date_maj", "N/A"),
                    })
                except Exception as e:
                    _LOGGER.warning(f"Error processing station: {e}")
                    continue

            # Sort by average price of Gazole
            filtered.sort(key=lambda x: float(x["fuels"].get("gazole", {}).get("price", 999)))

            return filtered[:self.nb_stations]
