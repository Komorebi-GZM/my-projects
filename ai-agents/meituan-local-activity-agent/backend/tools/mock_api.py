import random
import time
from typing import Dict, Any, List, Optional

import structlog

from config import config

logger = structlog.get_logger()


def _get_success_rate(api_type: str) -> float:
    """获取 Mock API 成功率（通过 Config 类统一管理）。"""
    if api_type == "high":
        return config.MOCK_HIGH_PRIORITY_RATE
    elif api_type == "low":
        return config.MOCK_LOW_PRIORITY_RATE
    else:
        return 0.85


def mock_search_poi(keyword: str, city: str = "上海", trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    start_time = time.time()
    success_rate = _get_success_rate("high")

    if random.random() < success_rate:
        result = _generate_mock_pois(keyword, city)
        _log_mock_call(trace_id, "search_poi", True, start_time)
        return result
    else:
        _log_mock_call(trace_id, "search_poi", False, start_time)
        return []


def mock_book_poi(poi_name: str, time_slot: Optional[str] = None, trace_id: Optional[str] = None) -> Dict[str, Any]:
    start_time = time.time()
    success_rate = _get_success_rate("high")

    if random.random() < success_rate:
        result = {
            "success": True,
            "poi_name": poi_name,
            "booking_id": f"mock_{random.randint(1000, 9999)}",
            "time_slot": time_slot or "14:00-16:00",
            "message": f"{poi_name} 预订成功"
        }
        _log_mock_call(trace_id, "book_poi", True, start_time)
        return result
    else:
        result = {
            "success": False,
            "poi_name": poi_name,
            "error": f"{poi_name} 预订失败（Mock）",
            "message": "Mock 失败，符合预设成功率"
        }
        _log_mock_call(trace_id, "book_poi", False, start_time)
        return result


def mock_get_reviews(poi_name: str, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    start_time = time.time()
    success_rate = _get_success_rate("low")

    if random.random() < success_rate:
        result = _generate_mock_reviews(poi_name)
        _log_mock_call(trace_id, "get_reviews", True, start_time)
        return result
    else:
        _log_mock_call(trace_id, "get_reviews", False, start_time)
        return []


def mock_get_poi_detail(poi_name: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
    start_time = time.time()
    success_rate = _get_success_rate("low")

    if random.random() < success_rate:
        result = _generate_mock_poi_detail(poi_name)
        _log_mock_call(trace_id, "get_poi_detail", True, start_time)
        return result
    else:
        result = {"name": poi_name, "address": "未知", "rating": 0.0, "price_range": "未知"}
        _log_mock_call(trace_id, "get_poi_detail", False, start_time)
        return result


def mock_get_weather(city: str, date: Optional[str] = None, trace_id: Optional[str] = None) -> Dict[str, Any]:
    start_time = time.time()
    result = {
        "city": city,
        "date": date or "today",
        "temperature": "22°C",
        "weather": "晴",
        "wind": "东风 3级",
        "humidity": "60%"
    }
    _log_mock_call(trace_id, "get_weather", True, start_time)
    return result


def _generate_mock_pois(keyword: str, city: str) -> List[Dict[str, Any]]:
    mock_data = {
        "火锅": [
            {"name": "海底捞", "address": f"{city}万达店", "rating": 4.8, "price_per_person": 120},
            {"name": "呷哺呷哺", "address": f"{city}南京东路店", "rating": 4.5, "price_per_person": 80}
        ],
        "电影": [
            {"name": "万达影城", "address": f"{city}万达广场", "rating": 4.7, "price_per_person": 45},
            {"name": "CGV影城", "address": f"{city}环贸广场", "rating": 4.6, "price_per_person": 50}
        ],
        "亲子": [
            {"name": "万达宝贝王", "address": f"{city}万达广场", "rating": 4.6, "price_per_person": 150},
            {"name": "迪士尼小镇", "address": f"{city}迪士尼度假区", "rating": 4.9, "price_per_person": 300}
        ]
    }
    for key, pois in mock_data.items():
        if key in keyword:
            return pois
    return mock_data["火锅"]


def _generate_mock_reviews(poi_name: str) -> List[Dict[str, Any]]:
    # N4 修复：使用 poi_name 生成差异化评价
    return [
        {"user": "匿名用户1", "rating": 5, "content": f"{poi_name}体验很好，强烈推荐！"},
        {"user": "匿名用户2", "rating": 4, "content": f"{poi_name}整体不错，性价比高，值得再去。"}
    ]


def _generate_mock_poi_detail(poi_name: str) -> Dict[str, Any]:
    return {
        "name": poi_name,
        "address": "上海市黄浦区南京东路100号",
        "rating": 4.7,
        "price_range": "100-150元/人",
        "opening_hours": "10:00-22:00",
        "phone": "021-12345678",
        "description": f"{poi_name} 是一家受欢迎的店铺"
    }


# N3 修复：trace_id 参数前置
def _log_mock_call(trace_id: Optional[str], api_name: str, success: bool, start_time: float):
    latency_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "mock_api_call",
        api_name=api_name,
        success=success,
        trace_id=trace_id,
        latency_ms=latency_ms
    )
