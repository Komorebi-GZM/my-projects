# Mock → 真实 API 集成设计方案

> 2026-05-20 · MVP 迭代 · 方案 B

## 目标

将 5 个 Mock API 中的 2 个替换为真实开放 API（天气、POI 搜索），保留 1 个增强 Mock（预订），其余 2 个保持不动。每个 domain tool 遵循 **real → fallback → mock** 模式。

## 架构概览

```
before:
  tools/mock_api.py ── 5 个 mock 函数大杂烩

after:
  tools/
    weather.py       real: Open-Meteo            + mock fallback
    search.py        real: Nominatim/OSM         + mock fallback
    booking.py       enhanced mock（按城市/时段）
    mock_api.py      保留，作为 fallback 数据源
    city_coords.json 城市→经纬度映射表
```

## 详细设计

### 1. 统一调用模式

每个 domain tool 的函数签名统一为：

```python
def get_xxx(city: str, ...) -> ResultType:
    if config.USE_REAL_APIS:
        try:
            result = _real_get_xxx(city, ...)
            return result
        except Exception as e:
            logger.warning("[fallback]", api="xxx", error=str(e))
    return _mock_get_xxx(city, ...)
```

### 2. 配置项扩展

```env
# Real API 开关
USE_REAL_APIS=true           # false → 全部走 mock
REAL_API_TIMEOUT=5           # 单次 HTTP 超时（秒）
REAL_API_RETRIES=1           # 失败重试次数
NOMINATIM_USER_AGENT=LocalLifeAgent/1.0
```

### 3. 天气 — Open-Meteo

#### 实时天气端点（MVP 够用）

```
GET https://api.open-meteo.com/v1/forecast?
  latitude={lat}&longitude={lng}
  &current_weather=true
  &daily=temperature_2m_max,temperature_2m_min,weathercode
  &timezone=Asia/Shanghai
```

#### 天气码 → 中文映射

| Code | 英文 | 中文 |
|------|------|------|
| 0 | Clear sky | 晴 |
| 1-3 | Mainly clear / partly cloudy | 多云 |
| 45-48 | Foggy | 雾 |
| 51-57 | Drizzle | 毛毛雨 |
| 61-67 | Rain | 雨 |
| 71-77 | Snow | 雪 |
| 80-82 | Rain showers | 阵雨 |
| 95-99 | Thunderstorm | 雷暴 |

#### 城市坐标

独立文件 `data/city_coords.json`，覆盖国内 15+ 主流城市：

```json
{
  "北京": {"lat": 39.9042, "lng": 116.4074},
  "上海": {"lat": 31.2304, "lng": 121.4737},
  "杭州": {"lat": 30.2741, "lng": 120.1551},
  "成都": {"lat": 30.5728, "lng": 104.0668},
  "广州": {"lat": 23.1291, "lng": 113.2644},
  "深圳": {"lat": 22.5431, "lng": 114.0579},
  ...
}
```

**未匹配城市 fallback：** 调用 Open-Meteo Geocoding API 实时查询：
```
GET https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1
```

### 4. POI 搜索 — Nominatim / OpenStreetMap

#### 搜索端点

```
GET https://nominatim.openstreetmap.org/search?
  q={keyword}+{city}
  &format=json
  &limit=5
  &addressdetails=1
  &accept-language=zh
```

#### 约束

- **必需** 设置 `User-Agent` 头，格式：`LocalLifeAgent/1.0 (your@email.com)`
- **限流** 1 req/sec，函数内置 `time.sleep(1)` 或限流装饰器
- **缓存** 使用 `functools.lru_cache(maxsize=128)` 缓存相同关键词+城市的结果

#### 字段映射

| Nominatim 返回 | 内部模型 |
|----------------|----------|
| `display_name` | `name` |
| `lat`, `lon` | `latitude`, `longitude` |
| `type` (hotel/restaurant/cafe…) | `category` |
| `address.road`, `address.city` | `address` |

### 5. Booking — 增强 Mock（无真实 API 替代）

保留 Mock，但增强数据真实性：

#### 城市坐标池

与 `city_coords.json` 对齐，每个城市预置 5-8 个 Mock POI（餐厅/咖啡馆/景点/影院），返回时根据城市过滤。

#### 时段成功率

| 时段 | 成功率 | 说明 |
|------|--------|------|
| 18:00-20:00 | 0.70 | 晚餐热门时段，容易满座 |
| 12:00-13:30 | 0.80 | 午餐高峰 |
| 其他 | 0.90 | 常规 |

#### booking_id 格式

```
{city_code}_{YYYYMMDD}_{6位随机}
```
示例：`SH_20260520_a3f8c2`

### 6. 包依赖新增

```txt
# backend/requirements.txt 新增
httpx>=0.27.0    # HTTP 客户端（替代 urllib）
```

`httpx` 选择理由：原生支持超时/重试/异步，比 `requests` 更现代。

## 不变部分

- `mock_get_reviews`（死代码，不动）
- `mock_get_poi_detail`（死代码，不动）
- Graph 状态机（graph/）完全不受影响
- Agent 代码（agents/）调用接口不变，只换内部实现
- 测试文件只更新 `test_mock_api.py`，新增 `test_weather.py`、`test_search.py`

## 影响范围

| 模块 | 改动类型 |
|------|----------|
| `tools/mock_api.py` | 删除天气/搜索函数，保留 booking/reviews/detail |
| `tools/weather.py` | 重写：Open-Meteo 调用 + mock fallback |
| `tools/search.py` | 重写：Nominatim 调用 + mock fallback + 缓存 |
| `tools/booking.py` | 重写：增强 Mock + 城市池 + 时段成功率 |
| `tools/__init__.py` | 导出新函数 |
| `data/city_coords.json` | 新增 |
| `backend/requirements.txt` | 新增 `httpx>=0.27.0` |
| `backend/.env.example` | 新增 `USE_REAL_APIS` 等配置项 |
| `config.py` | 读取新环境变量 |

## 调用点变更

agents 中所有 `from tools.mock_api import mock_xxx` 改为 `from tools.xxx import get_xxx`：

| 旧调用 | 新调用 | 涉及文件 |
|--------|--------|----------|
| `from tools.mock_api import mock_book_poi` | `from tools.booking import book_poi` | `agents/executor_agent.py` |

函数签名（参数、返回值）保持不变，只改 import 路径和函数名（去掉 `mock_` 前缀）。

## 未动（零改动）

- `graph/` 全部
- `middleware/` 全部
- `frontend/` 全部
