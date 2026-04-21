import os
import logging
from typing import Dict, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# OpenWeather API KEY
DEFAULT_KEY = "92ff3999060421b6afef1bec8d98f3b9"
key = os.getenv("OPENWEATHER_KEY", DEFAULT_KEY)

# OpenWeather URL
url = "https://api.openweathermap.org/data/2.5/weather"


# retry сессия
_session = requests.Session()
_retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
)
_session.mount("https://", HTTPAdapter(max_retries=_retries))


def get_weather_by_coords(lat: float, lon: float) -> dict:
    """Запрос погоды по координатам"""
    logger.info(f"REQUEST: lat={lat}, lon={lon}")

    params = {
        "lat": lat,
        "lon": lon,
        "appid": key,        
        "units": "metric",
        "lang": "ru",
    }

    resp = _session.get(url, params=params, timeout=10)

    logger.info(f"STATUS CODE: {resp.status_code}")
    logger.info(f"RESPONSE: {resp.text}")

    resp.raise_for_status()
    data = resp.json()

    weather = data["weather"][0]
    main = data["main"]

    return {
        "city": data.get("name", "Unknown"),
        "temp": round(main.get("temp", 0)),
        "descr": weather.get("description", "-"),
        "icon": weather.get("icon", "")
    }


def data_url(region_id: str) -> dict:
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