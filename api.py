import os
import logging
from typing import Dict, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

DEFAULT_KEY = "92ff3999060421b6afef1bec8d98f3b9"
key = os.getenv("OPENWEATHER_KEY", DEFAULT_KEY)

url = "https://api.openweathermap.org/data/2.5/weather"


_session = requests.Session()
_retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
)
_session.mount("https://", HTTPAdapter(max_retries=_retries))

def weather_score(data: dict) -> int:
    main = data["main"]
    wind = data.get("wind", {})
    clouds = data.get("clouds", {}).get("all", 0)

    temp = main.get("temp", 0)
    humidity = main.get("humidity", 0)
    wind_speed = wind.get("speed", 0)

    temp_score = max(0, 100 - abs(temp - 20) * 5)
    score = (
        temp_score * 0.4 +
        (100 - humidity) * 0.2 +
        (100 - clouds) * 0.2 +
        (100 - wind_speed * 10) * 0.2
    )
    return round(max(0, min(100, score)))


def weather_class(data: dict) -> str:
    rain = data.get("rain", {}).get("1h", 0)
    clouds = data.get("clouds", {}).get("all", 0)
    temp = data["main"].get("temp", 0)
    wind = data.get("wind", {}).get("speed", 0)

    if rain > 0:
        return "rain"
    if wind > 8:
        return "windy"
    if clouds > 70:
        return "cloudy"
    if temp > 25:
        return "hot"
    if temp < 0:
        return "cold"
    return "clear"

def weather_label(score: int) -> str:
    if score >= 80:
        return "Очень хорошая погода"
    elif score >= 60:
        return "Хорошая погода"
    elif score >= 40:
        return "Средняя погода"
    else:
        return "Плохая погода"
    
def humidity_label(humidity: int) -> str:
    if humidity < 30:
        return "Сухо"
    elif humidity < 60:
        return "Комфортно"
    else:
        return "Влажно"
    
def weather_coords(lat: float, lon: float) -> dict:
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
    wind = data.get("wind", {})
    rain = data.get("rain", {})
    clouds = data.get("clouds", {})
    score = weather_score(data)
    result = {
        "city": data.get("name", "Unknown"),
        "temp": round(main.get("temp", 0)),
        "descr": weather.get("description", "-"),
        "icon": weather.get("icon", ""),
        "wind_speed": wind.get("speed", 0),
        "wind_deg": wind.get("deg", 0),
        "wind_gust": wind.get("gust", 0),
        "rain_1h": rain.get("1h", 0),
        "rain_probability": clouds.get("all", 0),
        "weather_score": score,
        "weather_label": weather_label(score)
    }

    result["weather_score"] = weather_score(data)
    result["weather_class"] = weather_class(data)

    return result

def data_url(region_id: str) -> dict:
    try:
        lat, lon = map(float, region_id.split(","))
        return weather_coords(lat, lon)
    except Exception:
        return {
            "city": "Error",
            "temp": 0,
            "descr": "Неверные координаты",
            "icon": "",

            "wind_speed": 0,
            "wind_deg": 0,
            "wind_gust": 0,

            "rain_1h": 0,
            "rain_probability": 0
        }

