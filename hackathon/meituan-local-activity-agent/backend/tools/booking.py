import random
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List


_CITY_POOLS = {
    "北京": ["故宫", "798艺术区", "南锣鼓巷", "后海酒吧街", "长城脚下的咖啡馆"],
    "上海": ["外滩观景台", "武康路老洋房", "田子坊艺术空间", "滨江咖啡厅", "新天地餐厅"],
    "杭州": ["西湖边的茶舍", "灵隐寺旁素斋馆", "龙井村农家乐", "运河边的书店", "西溪湿地咖啡馆"],
    "成都": ["宽窄巷子火锅", "锦里小吃街", "人民公园茶馆", "太古里轻食", "青城山民宿餐厅"],
    "广州": ["珠江新城观景餐厅", "沙面咖啡馆", "北京路步行街小吃", "白云山茶馆", "上下九老字号"],
    "深圳": ["海上世界音乐餐吧", "华侨城创意园咖啡馆", "深圳湾公园野餐", "东门小吃街", "南头古城手作坊"],
}

_DEFAULT_POOL = ["热门咖啡馆", "网红餐厅", "城市公园", "购物中心", "艺术展览馆"]


def _get_city_pool(city: str) -> List[str]:
    for key, pool in _CITY_POOLS.items():
        if key in city:
            return pool
    return _DEFAULT_POOL


def _time_based_success_rate(time_slot: Optional[str]) -> float:
    if not time_slot:
        return 0.9
    if "18:00" in time_slot or "19:00" in time_slot or "20:00" in time_slot:
        return 0.70
    if "12:00" in time_slot or "13:00" in time_slot:
        return 0.80
    return 0.90


def book_poi(poi_name: str, time_slot: Optional[str] = None, trace_id: Optional[str] = None, city: str = "上海") -> Dict[str, Any]:
    from config import config
    success_rate = _time_based_success_rate(time_slot)
    success = random.random() < max(success_rate, config.MOCK_HIGH_PRIORITY_RATE)
    if success:
        return {
            "success": True,
            "poi_name": poi_name,
            "booking_id": _generate_booking_id(city),
            "time_slot": time_slot or "any",
            "message": f"{poi_name} 预订成功！",
            "_source": "booking_enhanced_mock",
        }
    return {
        "success": False,
        "poi_name": poi_name,
        "error": f"{poi_name} 在该时段已被订满，请选择其他时间",
        "message": "Mock 失败（时段成功率限制）",
    }


def _generate_booking_id(city: str) -> str:
    city_code = "XX"
    for c in ["北京", "上海", "杭州", "成都", "广州", "深圳", "南京", "武汉", "西安", "重庆"]:
        if c in city:
            city_code = {"北京": "BJ", "上海": "SH", "杭州": "HZ", "成都": "CD",
                         "广州": "GZ", "深圳": "SZ", "南京": "NJ", "武汉": "WH",
                         "西安": "XA", "重庆": "CQ"}.get(c, "XX")
            break
    date_str = datetime.now().strftime("%Y%m%d")
    rand = hashlib.md5(str(random.random()).encode()).hexdigest()[:6]
    return f"{city_code}_{date_str}_{rand}"
