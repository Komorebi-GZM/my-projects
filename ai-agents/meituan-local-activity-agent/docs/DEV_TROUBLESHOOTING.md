# 开发问题与解决记录

> 记录 MVP 开发过程中遇到的关键问题、根因分析、解决方案。
> 版本: 1.0 (2026-05-20)

---

## 目录

1. [E2E 运行时错误（SyntaxError / 线程安全 / HTML 渲染 / 超时）](#1-e2e-运行时错误)
2. [Streamlit 线程安全与全局状态桥接](#2-streamlit-线程安全)
3. [双轮头脑风暴架构设计](#3-双轮头脑风暴架构)
4. [真实 API 集成（天气 + POI 搜索）](#4-真实-api-集成)
5. [城市选择器与地理位置字段](#5-城市选择器与地理位置)
6. [Docker 容器化部署](#6-docker-容器化)
7. [LLM 客户端调用稳定性](#7-llm-客户端调用稳定性)
8. [Mock API 成功率控制](#8-mock-api-成功率控制)

---

## 1. E2E 运行时错误

### 1.1 SyntaxError: `global` 声明位于模块级别

**问题**：在 `frontend/app.py` 中，`global` 关键字被用在模块级别的函数外部，导致 SyntaxError。

**根因**：`global` 只能在函数内部使用，用于声明需要修改的全局变量。在模块级别使用会导致解析错误。

**解决方案**：移除模块级别的 `global` 声明，将所有全局状态封装在函数内部通过返回值传递。

```python
# ❌ 错误
global some_var

# ✅ 正确
def update_state():
    global some_var
    some_var = new_value
```

### 1.2 Streamlit 会话状态线程安全问题

**问题**：当 Streamlit 页面使用 `run_every` 定时刷新时，多个线程同时访问 `st.session_state` 导致数据竞争，出现随机键不存在错误。

**根因**：Streamlit 的脚本重执行机制和后台线程同时读写 `st.session_state`，Streamlit 的 session_state 不是线程安全的。

**解决方案**：引入全局桥接模式 + `threading.Lock`。

```python
import threading

_state_lock = threading.Lock()
_bridge: Dict[str, Any] = {}

def _worker():
    """后台线程执行"""
    with _state_lock:
        _bridge["result"] = long_running_task()

def get_bridge_value(key: str, default=None):
    with _state_lock:
        return _bridge.get(key, default)
```

关键文件：`frontend/app.py`

### 1.3 HTML 渲染为代码块

**问题**：Streamlit 将启用了 `unsafe_allow_html=True` 的 f-string 组件中的空格视为代码块，导致 HTML 被渲染为 `<code>` 块，UI 显示异常。

**根因**：Streamlit 的 Markdown 解析器对 f-string 组件中的前导空格敏感，当组件以空格缩进时被识别为代码块。

**解决方案**：添加 `_clean_html()` 函数，在渲染前剥离 f-string 组件的首行前导空格。

```python
def _clean_html(text: str) -> str:
    lines = text.split('\n')
    if lines and lines[0].strip() == '':
        lines = lines[1:]
    return '\n'.join(lines)
```

### 1.4 `st.button()` TypeError

**问题**：`st.button()` 的 `label` 参数被重复传递，导致 TypeError。

**根因**：Streamlit 版本升级后 API 变更，`label` 只能作为位置参数传递一次。

**解决方案**：移除重复的 `label` 参数。

```python
# ❌ 错误
st.button("确认", label="确认")

# ✅ 正确
st.button("确认")
```

### 1.5 Starlette 1.0 `on_startup` 移除

**问题**：FastAPI 升级到 >=0.115.6 后，Starlette 1.0 移除了 `app.on_startup` 事件。

**根因**：Starlette 1.0 使用 `lifespan` 上下文管理器替代 `on_startup`/`on_shutdown`。

**解决方案**：显式依赖 FastAPI >=0.115.6，使用 `@app.on_event("startup")`（FastAPI 0.115+ 兼容）或 `lifespan`。

```python
# backend/requirements.txt
fastapi>=0.115.6
```

### 1.6 LLM 响应截断

**问题**：OpenAI-compatible LLM 调用超时或返回截断的响应，导致 `parse_dict_from_response` 解析失败。

**根因**：默认的 `max_tokens` 参数偏小（2048），长 prompt 或复杂响应被截断。

**解决方案**：
- `call_llm` 增加 `max_tokens=8192` 参数
- `call_llm_dict` 增加解析容错，提取 Dict 完整片段

```env
LLM_MAX_TOKENS=8192
```

### 1.7 请求超时

**问题**：规划流程涉及多次 LLM 调用（Intent + Planner + 4 Brainstorm Agents × 2 rounds），总耗时超过默认 30s 超时。

**根因**：同步串行调用模式下，8-12 次 LLM 调用平均耗时 30-60s。

**解决方案**：
- HTTP 客户端超时从 30s 增加到 180s
- 后端线程池异步执行，Streamlit 前端使用 `@st.fragment(run_every=2s)` 轮询

```python
# frontend/config.py
BACKEND_TIMEOUT = 180
```

---

## 2. Streamlit 线程安全

### 2.1 全局桥接模式

**问题**：后台线程和 Streamlit 主线程通过 `st.session_state` 共享状态时出现数据竞争。

**根因**：Streamlit 的 session_state 使用 Python dict 实现，不是线程安全。`st.rerun()` 触发脚本重执行，与后台写操作并发。

**解决方案**：全局 `_bridge` dict + `threading.Lock`。

```python
# frontend/app.py
import threading
from typing import Any, Dict

_bridge: Dict[str, Any] = {}
_lock = threading.Lock()
```

### 2.2 `@st.fragment` 轮询

**问题**：E2E 流程耗时 30-60s，需要实时反馈进度。

**解决方案**：使用 Streamlit 1.40+ 的 `@st.fragment(run_every=2)` 装饰器实现轮询式进度展示。

```python
@st.fragment(run_every=2)
def show_progress():
    with _lock:
        if _bridge.get("status") == "running":
            st.markdown("⏳ 规划进行中...")
        elif _bridge.get("status") == "done":
            st.markdown("✅ 规划完成")
```

---

## 3. 双轮头脑风暴架构

### 3.1 架构设计

```
Brainstorm 流程：
  Round 1: 4 Agents 并行评审原始方案 → 汇总反馈
  Round 2: Planner 根据反馈修改方案 → 4 Agents 复评
  Aggregate: 加权汇总 → 安全否决检查 → Execute
```

**动机**：单轮评审方案没有机会改进，缺乏"反馈-修改-复评"的迭代质量提升。

### 3.2 Agent 并行执行

**问题**：4 个 Agent 串行执行耗时过长。

**解决方案**：`ThreadPoolExecutor(4)` 并行执行。

```python
# brainstorm_engine.py
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_brainstorm_round(candidates, round_num, intent, trace_id):
    agents = [
        ExperienceAgent(),
        SafetyAgent(),
        EfficiencyAgent(),
        BudgetAgent()
    ]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for candidate in candidates:
            for agent in agents:
                future = executor.submit(agent.review, candidate, intent, trace_id)
                futures.append((agent.name, candidate["id"], future))
        # 收集结果
```

### 3.3 安全否决与重规划

**问题**：安全 Agent 否决某个方案后需要重新规划，但重试不能无限进行。

**解决方案**：
- 安全 Agent 有 `veto: bool` 字段，一旦 veto=True，该方案最终得分为 0
- 所有方案都被否决时触发 `replan`
- `replan_count` 上限为 2，超过则流程失败

关键文件：
- `backend/graph/edges.py` — `safety_router` 条件路由
- `backend/graph/nodes.py` — `replan` 节点

### 3.4 加权评分聚合

**权重分配**：

| Agent | 权重 | 说明 |
|-------|------|------|
| 体验Agent | 0.30 | 用户体验最优先 |
| 安全Agent | 0.25 | 安全有否决权 |
| 效率Agent | 0.20 | 时间利用率 |
| 预算Agent | 0.25 | 预算匹配度 |

**B4 修复**：R2 覆盖 R1 评分，避免两轮重复累加导致权重失衡。

```python
# B4 修复
for round_data in [round1, round2]:
    if not round_data:
        continue
    for agent_name, agent_reviews in round_data.get("reviews", {}).items():
        for candidate_id, review in agent_reviews.items():
            score = review.get("score", 5.0) if not review.get("veto") else 0
            latest_scores[candidate_id][agent_name] = score  # 后轮覆盖前轮
```

---

## 4. 真实 API 集成

### 4.1 天气 API：Open-Meteo（cf83dff）

**选择理由**：Open-Meteo 是免费开源气象 API，无需 API Key，支持全球城市坐标查询。

**实现**：

```python
# tools/weather.py
def get_weather(city: str, date: str = None, trace_id: str = None) -> Dict:
    # 1. 通过 Nomimatin 或本地坐标映射获取城市经纬度
    # 2. 调用 Open-Meteo API: https://api.open-meteo.com/v1/forecast
    # 3. 解析响应，返回 {temperature, weather, humidity, wind}
```

**Fallback 策略**：
1. 优先调用真实 API（Open-Meteo）
2. 真实 API 失败 → 使用 Mock 数据
3. Mock 也失败 → 返回默认天气信息

关键文件：`backend/tools/weather.py`, `backend/data/city_coords.json`

### 4.2 POI 搜索：Nominatim（cf83dff）

**选择理由**：Nominatim 是 OpenStreetMap 的开源地理编码服务，无需 API Key。

**限制**：使用政策要求 ≤1 请求/秒，需要加入 `User-Agent` 标识。

```python
# tools/search.py
headers = {
    "User-Agent": "LocalLifePlanner/1.0 (hackathon)"
}
response = httpx.get(
    "https://nominatim.openstreetmap.org/search",
    params={"q": keyword, "city": city, "format": "json", "limit": 5},
    headers=headers
)
```

**Fallback 策略**：
1. 真实 API → 2. 模块级 Mock 数据池 → 3. 默认数据

### 4.3 城市坐标映射

**问题**：Open-Meteo 需要经纬度查询天气，Nominatim 每次查询有速率限制。

**解决方案**：预置 `city_coords.json` 包含常见城市坐标，减少 Nominatim 调用。

```json
{
  "北京": {"lat": 39.9042, "lon": 116.4074},
  "上海": {"lat": 31.2304, "lon": 121.4737},
  ...
}
```

### 4.4 Mock 预订增强

**问题**：Mock 预订数据不具备城市/时间感知能力。

**解决方案**：
- 6 城市数据池（上海/北京/杭州/深圳/成都/广州）
- 基于时间段的成功率调整（周末 > 工作日）
- Executor 通过 Intent 中的 `location.city` 获取上下文

---

## 5. 城市选择器与地理位置

### 5.1 功能概述（8f4fdcc）

**需求**：用户选择城市后，规划结果基于该城市生成，并显示当地天气。

**改动范围**：16 个文件，涉及前后端全链路。

### 5.2 后端链路

```
Frontend (city param) → FastAPI main.py → orchestrator.run_planning_flow()
  → intent_agent.parse() + city_override → get_weather(city) → intent["weather"] = weather
  → graph.nodes.py passes city → executor_agent.execute(city=city)
```

**关键点**：
- `main.py`: `PlanRequest` 增加 `city` 字段
- `orchestrator.py`: `run_planning_flow` 接受 `city_override` 参数
- `intent_agent.py`: `_fill_defaults` 默认填入 `location.city` = "上海"

### 5.3 前端链路

```
app.py: 侧边栏城市选择器 → API 调用传递 city → 响应中的 weather 信息
  → intent_summary.py: 显示城市 + 天气
  → best_plan.py: 显示城市 + 天气图标
```

### 5.4 嵌套字典合并问题

**问题**：`_fill_defaults` 直接赋值 `intent["location"]["city"]` 时，`location` 可能不存在。

**解决方案**：
```python
if "location" not in intent:
    intent["location"] = {}
intent["location"]["city"] = city_override or intent.get("location", {}).get("city", "上海")
```

---

## 6. Docker 容器化

### 6.1 文件构成

| 文件 | 作用 |
|------|------|
| `backend/Dockerfile` | 基于 `python:3.12-slim`，安装依赖后运行 uvicorn |
| `frontend/Dockerfile` | 基于 `python:3.12-slim`，安装依赖后运行 streamlit |
| `docker-compose.yml` | 定义 backend + frontend 服务、端口映射、环境变量 |
| `.dockerignore` | 排除 `__pycache__`/`.venv`/`.git` 等 |

### 6.2 构建与运行

```bash
docker-compose up --build
```

### 6.3 环境变量传递

通过 `docker-compose.yml` 的 `environment` 字段传递 `.env` 变量，或通过 `env_file` 引用。

---

## 7. LLM 客户端调用稳定性

### 7.1 OpenAI-compatible 集成

**实现**：
```python
# agents/llm_client.py
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)

def call_llm(prompt, system_prompt=None, temperature=0.7, max_retries=2, trace_id=None):
    # 重试逻辑 + 指数退避
    # max_tokens 由 LLM_MAX_TOKENS 控制
    # 返回纯文本
```

### 7.2 `call_llm_dict` 解析

**问题**：LLM 返回格式不稳定，有时是 Python Dict、有时是 JSON、有时被 Markdown 包裹。

**解决方案**：`parse_dict_from_response` 逐层尝试：
1. 移除 Markdown 代码块标记
2. 尝试 `eval()` 解析 Python Dict
3. 尝试 `json.loads()` 解析 JSON
4. 正则提取 `{...}` 片段

### 7.3 重试策略

| 重试次数 | 退避时间 | 说明 |
|----------|----------|------|
| 第 1 次 | 1s | 网络抖动 |
| 第 2 次 | 3s | 服务临时不可用 |
| 第 3 次 | 7s | 稳定降级（仅高优接口） |

---

## 8. Mock API 成功率控制

### 8.1 差异化成功率

| API | 类型 | 默认成功率 |
|-----|------|-----------|
| `mock_search_poi` | 高优 | 0.95 |
| `mock_book_poi` | 高优 | 0.95 |
| `mock_get_reviews` | 低优 | 0.80 |
| `mock_get_poi_detail` | 低优 | 0.80 |

### 8.2 环境变量控制

```env
MOCK_HIGH_PRIORITY_RATE=0.95
MOCK_LOW_PRIORITY_RATE=0.80
MOCK_SUCCESS_RATE=0.85    # 默认
```

### 8.3 Falback 机制

| API | 失败时 Fallback |
|-----|----------------|
| `mock_search_poi` | 返回空列表 `[]` |
| `mock_book_poi` | 返回 `{"success": False, "error": "..."}` |
| `mock_get_reviews` | 返回空列表 `[]` |
| `mock_get_poi_detail` | 返回基础信息（名称地址评分） |

---

## 附录：提交历史速查

| 提交 | 功能 | 关键改动 |
|------|------|----------|
| `fc132d1` | 环境变量 | `.env` + `.env.example` |
| `029a418` | 配置管理 | `config.py` |
| `5ecf4c2` | 日志 | `logging_config.py` + 依赖 |
| `276d6fd` | LLM 客户端 | `llm_client.py` + 测试 |
| `b2ae082` | Mock API | `mock_api.py` + 6 城市数据池 |
| `a9d2b9d` | MVP 核心 | 全套 Agent + Graph + Frontend |
| `9082972` | E2E 修复 | 7 类运行时错误修复 |
| `cf83dff` | 真实 API | Open-Meteo + Nominatim 集成 |
| `8f4fdcc` | 城市选择 | 城市选择器 + 天气 + Docker |
