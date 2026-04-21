import os
import logging
from typing import Dict, Tuple, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# 🔑 API ключ
DEFAULT_KEY = "7216cf5ae90f43f5815d50ddcf378c4f"
key = os.getenv("WEATHERBIT_KEY", DEFAULT_KEY)

url = "https://api.weatherbit.io/v2.0/current"

# 📍 (ОПЦИОНАЛЬНО) старые регионы — можно оставить или удалить
coord: Dict[str, Tuple[float, float]] = {
    "gom": (52.4338, 31.1923),
    "minsk": (53.9000, 27.5667),
}

# 🔁 сессия с retry
_session = requests.Session()
_retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
)
_session.mount("https://", HTTPAdapter(max_retries=_retries))

def get_weather_by_coords(lat: float, lon: float) -> dict:
    """Получить погоду по координатам"""

    params = {
        "lat": lat,
        "lon": lon,
        "key": key,
        "lang": "ru",
        "units": "M",
    }

    try:
        resp = _session.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        item = data["data"][0]

        return {
            "city": item.get("city_name", "Неизвестно"),
            "temp": round(float(item.get("temp", 0))),
            "descr": item.get("weather", {}).get("description", "-"),
            "icon": item.get("weather", {}).get("icon", "")
        }

    except Exception as e:
        logger.exception("Ошибка API")
        return {
            "city": "Error",
            "temp": 0,
            "descr": str(e),
            "icon": ""
        }


def data_url(region_id: str) -> dict:
    """Старый метод (region_id или 'lat,lon')"""

    region_id = region_id.strip()

    # 1. если это ключ (gom, minsk)
    if region_id in coord:
        lat, lon = coord[region_id]
        return get_weather_by_coords(lat, lon)

    # 2. если это "lat,lon"
    try:
        lat, lon = map(float, region_id.split(","))
        return get_weather_by_coords(lat, lon)
    except Exception:
        return {
            "city": "Error",
            "temp": 0,
            "descr": "Неверные координаты",
            "icon": ""
        }