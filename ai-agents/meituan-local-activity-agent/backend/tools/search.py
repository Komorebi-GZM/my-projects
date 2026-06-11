import time
import json
import threading
import httpx
from functools import lru_cache
from typing import Optional, List, Dict, Any
from config import config
from tools.mock_api import mock_search_poi

_NOMINATIM_BASE = "https://nominatim.openstreetmap.org/search"
_lock = threading.Lock()


def _rate_limited_call(params: dict) -> list:
    with _lock:
        time.sleep(1.1)
        headers = {"User-Agent": config.NOMINATIM_USER_AGENT}
        r = httpx.get(_NOMINATIM_BASE, params=params, headers=headers, timeout=config.REAL_API_TIMEOUT)
        r.raise_for_status()
        return r.json()


@lru_cache(maxsize=128)
def _cached_search(query: str, city: str) -> str:
    params = {
        "q": f"{query} {city}",
        "format": "json",
        "limit": 5,
        "addressdetails": "1",
        "accept-language": "zh",
    }
    results = _rate_limited_call(params)
    return json.dumps(results, ensure_ascii=False)


def _real_search_poi(keyword: str, city: str) -> List[Dict[str, Any]]:
    raw = _cached_search(keyword, city)
    results = json.loads(raw)
    pois = []
    for item in results:
        pois.append({
            "name": item.get("display_name", "").split(",")[0],
            "address": item.get("display_name", ""),
            "latitude": float(item.get("lat", 0)),
            "longitude": float(item.get("lon", 0)),
            "category": item.get("type", "unknown"),
            "_source": "nominatim",
        })
    return pois


def search_poi(keyword: str, city: str = "上海", trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if config.USE_REAL_APIS:
        try:
            return _real_search_poi(keyword, city)
        except Exception as e:
            print(f"[search fallback] {e}")
    return mock_search_poi(keyword, city, trace_id)
