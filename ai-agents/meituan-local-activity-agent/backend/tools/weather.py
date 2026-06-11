import json
from typing import Optional
from config import config
from tools.mock_api import mock_get_weather

_WEATHER_CODES = {
    0: "晴", 1: "晴", 2: "多云", 3: "多云",
    45: "雾", 48: "雾",
    51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨",
    61: "雨", 63: "雨", 65: "雨",
    71: "雪", 73: "雪", 75: "雪",
    80: "阵雨", 81: "阵雨", 82: "阵雨",
    95: "雷暴", 96: "雷暴", 99: "雷暴",
}

_CITY_COORDS = json.load(open("data/city_coords.json"))


def _weather_code_to_zh(code: int) -> str:
    return _WEATHER_CODES.get(code, "未知")


def get_weather(city: str, date: Optional[str] = None, trace_id: Optional[str] = None) -> dict:
    if config.USE_REAL_APIS:
        try:
            return _real_get_weather(city, date)
        except Exception as e:
            print(f"[weather fallback] {e}")
    return mock_get_weather(city, date, trace_id)


def _city_to_coords(city: str) -> tuple:
    if city in _CITY_COORDS:
        return _CITY_COORDS[city]["lat"], _CITY_COORDS[city]["lng"]
    return None, None


def _real_get_weather(city: str, date: Optional[str] = None) -> dict:
    lat, lng = _city_to_coords(city)
    if lat is None:
        raise ValueError(f"无法获取城市坐标: {city}")
    import httpx
    params = {
        "latitude": lat,
        "longitude": lng,
        "current_weather": "true",
        "timezone": "Asia/Shanghai",
    }
    if date:
        params["daily"] = "temperature_2m_max,temperature_2m_min,weathercode"
        params["start_date"] = date
        params["end_date"] = date
    r = httpx.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=config.REAL_API_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    current = data.get("current_weather", {})
    return {
        "city": city,
        "date": date or "today",
        "temperature": f"{current.get('temperature', '?')}°C",
        "weather": _weather_code_to_zh(current.get("weathercode", 0)),
        "wind": f"{current.get('windspeed', '?')} km/h",
        "humidity": "N/A",
        "_source": "open-meteo",
    }
