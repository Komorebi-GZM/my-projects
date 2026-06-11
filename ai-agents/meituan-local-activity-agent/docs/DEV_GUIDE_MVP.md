# 🎯 本地生活短时活动规划 Agent — MVP 开发者指南

> **文档版本**：V1.0（MVP）
> **配套文档**：[PRD_本地生活AI_Agent_V3_MVP.md](./PRD_本地生活AI_Agent_V3_MVP.md)
> **技术栈**：Python >=3.11 + LangGraph 1.0 + OpenAI-compatible LLM + FastAPI + Streamlit

---

# 一、快速启动

## 1.1 环境要求

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| Python | >= 3.11 | 本地 conda 环境名 `py312` |
| pip | 最新版 | `python3 -m pip install --upgrade pip` |
| Git | 任意版本 | 代码版本管理 |
| conda | 任意版本 | 用于创建 `py312` 环境 |

> **硬件建议**：运行 LLM Mock 时内存 >= 8GB，推荐 16GB

## 1.2 创建 conda 环境并安装

```bash
# 克隆项目
git clone <repo-url>
cd <project-root>

# 创建 conda 环境
conda create -n py312 python=3.12 -y
conda activate py312

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
pip install -r requirements.txt
```

### `backend/requirements.txt`

```txt
# ========== LangGraph 生态 ==========
langgraph==1.0.0

# ========== LLM（OpenAI-compatible Chat Completions）==========
openai>=1.0.0

# ========== FastAPI ==========
fastapi==0.115.0
uvicorn[standard]==0.30.0
pydantic==2.9.0

# ========== 工具库 ==========
httpx==0.27.0
python-dotenv==1.0.0
structlog==24.4.0

# ========== 测试 ==========
pytest==8.3.0
pytest-asyncio==0.24.0
```

### `frontend/requirements.txt`

```txt
streamlit==1.40.0
httpx==0.27.0
python-dotenv==1.0.0
```

## 1.3 环境变量配置

在 `backend/` 和 `frontend/` 目录分别创建 `.env` 文件：

### `backend/.env`

```env
# ========== LLM 配置 ==========
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
LLM_MAX_TOKENS=2048

# ========== 服务配置 ==========
LOG_LEVEL=INFO
TRACE_LEVEL=basic  # basic | advanced

# ========== Mock API 配置 ==========
# Mock 成功率基线
MOCK_SUCCESS_RATE=0.85
# 高优接口成功率（搜索/订座）
MOCK_HIGH_PRIORITY_RATE=0.95
# 低优接口成功率（评价/详情）
MOCK_LOW_PRIORITY_RATE=0.80

# ========== 服务端口 ==========
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### `frontend/.env`

```env
# ========== 后端地址 ==========
BACKEND_URL=http://localhost:8000
```

> ⚠️ **重要**：`LLM_API_KEY` 需要到模型平台申请。团队成员只需要替换 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 三项；任意兼容 OpenAI Chat Completions 的 `/v1` 地址都可用。阿里百炼兼容地址：`https://dashscope.aliyuncs.com/compatible-mode/v1`；Kimi：`https://api.moonshot.cn/v1`；DeepSeek：`https://api.deepseek.com/v1`。

## 1.4 启动服务

```bash
# 终端 1：后端
conda activate py312
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# 终端 2：前端
conda activate py312
cd frontend
streamlit run app.py --server.port 8501
```

> 当前仓库没有 Makefile。不要用 `make start`，也不要把 `cd backend && ...` 合成一条启动命令；先激活 `py312`，再进入对应目录启动服务。

## 1.5 验证启动成功

```bash
# 验证后端健康检查
curl http://localhost:8000/health

# 预期返回：
# {"status": "ok", "version": "1.0.0"}

# 打开浏览器访问
open http://localhost:8501
```

---

# 二、项目结构

## 2.1 目录树

```
<project-root>/
├── PRD_本地生活AI_Agent_V3_MVP.md   # 产品需求文档（PRD）
├── DEV_GUIDE_MVP.md                  # 本文档
│
├── backend/                          # FastAPI 后端
│   ├── main.py                       # 应用入口
│   ├── config.py                     # 配置管理
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── agents/                       # Agent 核心实现
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # 主编排器（LangGraph 驱动）
│   │   ├── intent_agent.py           # IntentAgent
│   │   ├── planner_agent.py          # PlannerAgent
│   │   ├── executor_agent.py         # ExecutorAgent
│   │   │
│   │   └── brainstorm/               # 头脑风暴层
│   │       ├── __init__.py
│   │       ├── experience_agent.py   # 体验 Agent
│   │       ├── safety_agent.py        # 安全 Agent
│   │       ├── efficiency_agent.py    # 效率 Agent
│   │       └── budget_agent.py        # 预算 Agent
│   │
│   ├── graph/                        # LangGraph 状态机
│   │   ├── __init__.py
│   │   ├── state.py                  # BrainstormState 定义
│   │   ├── nodes.py                  # Node 函数
│   │   └── edges.py                  # 条件边路由
│   │
│   ├── tools/                        # 工具层
│   │   ├── __init__.py
│   │   ├── mock_api.py                # Mock API 封装
│   │   ├── search.py                   # 搜索工具
│   │   ├── booking.py                  # 订座工具
│   │   └── weather.py                  # 天气查询（直接调用）
│   │
│   ├── middleware/                   # 中间件
│   │   ├── __init__.py
│   │   └── trace.py                   # Trace 中间件
│   │
│   └── schemas/                      # 数据模型
│       ├── __init__.py
│       ├── intent.py                  # Intent 结构
│       ├── plan.py                    # 方案结构
│       └── review.py                  # 评审结果结构
│
└── frontend/                         # Streamlit 前端
    ├── app.py                         # 主界面
    ├── config.py                      # 配置
    ├── requirements.txt
    ├── .env.example
    │
    ├── pages/                         # 多页面
    │   ├── home.py                    # 首页
    │   ├── chat.py                    # 对话界面
    │   └── history.py                 # 历史记录
    │
    └── components/                    # 组件
        ├── plan_card.py               # 方案卡片
        ├── score_matrix.py             # 评分矩阵
        └── trace_viewer.py             # Trace 查看器
```

## 2.2 核心文件职责

| 文件 | 职责 | 复杂度 |
|------|------|--------|
| `main.py` | FastAPI 应用入口、路由注册 | ⭐⭐ |
| `config.py` | 环境变量读取、配置校验 | ⭐ |
| `orchestrator.py` | 全局状态持有、LangGraph 编排、协商仲裁 | ⭐⭐⭐⭐⭐ |
| `graph/state.py` | BrainstormState 定义、类型注解 | ⭐⭐ |
| `graph/nodes.py` | 各 Node 实现（意图解析→规划→头脑风暴→执行） | ⭐⭐⭐⭐ |
| `graph/edges.py` | 条件边路由（safety_router / replan_router / executor_router） | ⭐⭐⭐ |
| `brainstorm/*.py` | 4 个视角 Agent 的 Prompt + 评分逻辑 | ⭐⭐⭐ |
| `tools/mock_api.py` | Mock 成功率控制、故障注入 | ⭐⭐⭐ |
| `tools/weather.py` | 天气查询（直接调用和风天气等免费 API） | ⭐⭐ |
| `middleware/trace.py` | Trace ID 生成与传播 | ⭐⭐ |

## 2.3 命名规范

| 类型 | 规范 | 示例 |
|------|------|---------|
| 文件名 | **下划线**（PEP8） | `experience_agent.py` |
| 类名 | **大驼峰** | `ExperienceAgent` |
| 函数名 | **下划线** | `parse_intent()` |
| 常量 | **全大写下划线** | `MOCK_SUCCESS_RATE` |
| LangGraph Node | **动词+名词** | `parse_intent`, `generate_plans`, `brainstorm_round1` |

## 2.4 模块组织原则

1. **Agent 实现** → `agents/` 目录
   - 顶层：Orchestrator / Intent / Planner / Executor
   - 子目录 `brainstorm/`：4 个视角 Agent

2. **LangGraph 状态机** → `graph/` 目录（独立，便于测试）
   - `state.py`：纯数据结构
   - `nodes.py`：Node 函数实现
   - `edges.py`：条件边路由逻辑

3. **工具层** → `tools/` 目录
   - Mock API 封装
   - 实际 API 调用（天气等）

4. **中间件** → `middleware/` 目录
   - Trace 注入
   - 日志格式化

---

# 三、LangGraph 状态机详解

## 3.1 状态定义（`graph/state.py`）

```python
# graph/state.py
\"\"\"LangGraph 状态定义（使用 TypedDict，与 LangGraph 官方示例对齐）\"\"\"

from typing import TypedDict, Optional, List, Dict, Literal
from enum import Enum


class TripState(str, Enum):
    \"\"\"行程状态枚举\"\"\"
    IDLE = "IDLE"
    INTENT_PARSING = "INTENT_PARSING"
    PLANNING = "PLANNING"
    BRAINSTORMING = "BRAINSTORMING"
    REPLANNING = "REPLANNING"
    CONFIRMING = "CONFIRMING"
    BOOKING = "BOOKING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Intent(TypedDict):
    \"\"\"用户意图结构\"\"\"
    time: Dict[str, str]                    # {"range": "14:00-18:00", "flexibility": "±1h"}
    group: Dict                              # {"type": "family", "count": 3, "children": [{"age": 5}]}
    scene: str                               # "parent_child" | "friends" | "couple"
    constraints: Dict                        # {"max_distance_km": 10, "budget": 200}
    preferences: Dict                       # {"food": "healthy", "activity": "indoor"}
    missing_fields: List[str]               # 缺失字段，待补全


class AgentReview(TypedDict):
    \"\"\"单个 Agent 评审结果\"\"\"
    agent: str                               # "体验Agent" | "安全Agent" | "效率Agent" | "预算Agent"
    score: float                             # 0-10 分
    veto: bool                               # 是否否决（仅安全 Agent 使用）
    veto_reason: Optional[str]               # 否决原因
    strengths: List[str]                     # 优点列表
    concerns: List[str]                      # 问题列表
    suggestions: List[str]                   # 建议列表


class RoundReviews(TypedDict):
    \"\"\"单轮评审结果\"\"\"
    round: int                               # 1 或 2
    reviews: Dict[str, AgentReview]          # {"体验Agent": {...}, "安全Agent": {...}, ...}
    summary: str                             # 本轮评审摘要


class BrainstormState(TypedDict):
    \"\"\"LangGraph 全局状态（TypedDict，无 checkpointer）\"\"\"
    # ========== 基础信息 ==========
    session_id: str                          # 会话 ID
    trip_state: str                          # 行程状态（TripState 枚举值）
    user_input: str                          # 用户原始输入

    # ========== 意图解析 ==========
    intent: Optional[Intent]                 # 解析后的结构化意图

    # ========== 方案相关 ==========
    candidates: Optional[List[Dict]]         # 候选方案列表
    round: int                               # 当前头脑风暴轮次（0 / 1 / 2）
    round1_reviews: Optional[RoundReviews]   # Round 1 评审结果
    round2_reviews: Optional[RoundReviews]   # Round 2 评审结果
    final_score: Optional[float]             # 最终聚合分数
    best_plan: Optional[Dict]               # 最终推荐方案

    # ========== 重试与异常 ==========
    replan_count: int                        # 安全否决后重试次数（上限 2）
    error: Optional[str]                     # 错误信息

    # ========== 可观测性 ==========
    trace_id: str                            # 全链路追踪 ID
    parent_trace_id: Optional[str]           # 上游调用方 ID
    latency_ms: Optional[int]                # 本节点耗时
```

## 3.2 Node 函数（`graph/nodes.py`）

> **说明**：Node 函数集中在 `nodes.py`，每个函数接收 `BrainstormState`，返回 `Dict[str, Any]` 增量更新状态。

```python
# graph/nodes.py
from .state import BrainstormState, TripState

def parse_intent(state: BrainstormState) -> Dict[str, Any]:
    # 加载 IntentAgent → 调用 LLM 解析 → 返回 {"intent": Intent, "trip_state": "INTENT_PARSING", ...}

def generate_plans(state: BrainstormState) -> Dict[str, Any]:
    # 加载 PlannerAgent → 规则模板生成候选方案 → 返回 {"candidates": [...], "round": 0, "trip_state": "PLANNING"}

def brainstorm_round1(state: BrainstormState) -> Dict[str, Any]:
    # brainstorm_engine.run_brainstorm_round(round_num=1) → {"round1_reviews": ..., "round": 1, "trip_state": "BRAINSTORMING"}

def brainstorm_round2(state: BrainstormState) -> Dict[str, Any]:
    # PlannerAgent.revise() 修改方案 → run_brainstorm_round(round_num=2) → {"round2_reviews": ..., "round": 2, "candidates": updated}

def aggregate_and_confirm(state: BrainstormState) -> Dict[str, Any]:
    # orchestrator.aggregate_reviews() → {"final_score": float, "best_plan": Dict, "trip_state": "CONFIRMING"}

def replan(state: BrainstormState) -> Dict[str, Any]:
    # replan_count >= 2 → FAILED；否则 PlannerAgent.regenerate() → {"candidates": new, "replan_count": +1, "round": 0, "trip_state": "REPLANNING"}

def execute_plan(state: BrainstormState) -> Dict[str, Any]:
    # ExecutorAgent.execute() → Mock 预订 → {"trip_state": "EXECUTING"|"FAILED"}
```

## 3.3 条件边路由（`graph/edges.py`）

```python
# graph/edges.py
from .state import BrainstormState

def safety_router(state) -> str:
    # 安全Agent否决 → replan_count>=2 ? "FAILED" : "REPLANNING"
    # 否则 round<2 ? "BRAINSTORMING" : "CONFIRMING"

def replan_router(state) -> str:
    # replan_count>=2 ? "FAILED" : "BRAINSTORMING"

def executor_router(state) -> str:
    # error存在 ? "FAILED" : "COMPLETED"

def should_continue_brainstorm(state) -> str:
    # round==1 && 无reviews → "aggregate"（跳过R2）
    # round>=2 → "aggregate"，否则 → "continue"
```

## 3.4 状态机构建（`graph/builder.py`）

```python
# graph/builder.py
from langgraph.graph import StateGraph, END
from .state import BrainstormState
from .nodes import (parse_intent, generate_plans, brainstorm_round1,
                     brainstorm_round2, aggregate_and_confirm, replan, execute_plan)
from .edges import (safety_router, replan_router, executor_router, should_continue_brainstorm)

def build_graph():
    workflow = StateGraph(BrainstormState)
    # 节点: parse_intent / generate_plans / brainstorm_round1 / brainstorm_round2
    #       / aggregate_and_confirm / replan / execute_plan
    # 入口: parse_intent
    # 条件边: brainstorm_round1 → should_continue_brainstorm → R2 | aggregate | END
    #         aggregate → safety_router → replan | execute_plan | END
    #         replan → replan_router → brainstorm_round1 | END
    #         execute_plan → executor_router → COMPLETED | FAILED
    return workflow.compile()  # 无 checkpointer
```

## 3.5 Trace 中间件（`middleware/trace.py`）

```python
# middleware/trace.py
def generate_trace_id() -> str: return str(uuid.uuid4())
def inject_trace_id(state, parent_trace_id=None): ...  # 注入 trace_id + parent_trace_id
def log_with_trace(logger, event, state, **kwargs): ...  # structlog 带 trace 上下文
```

> **关键约束**：State 用 `TypedDict`，无 checkpointer（MVP）；Node 返回增量更新；所有 Node 函数集中在 `nodes.py`。


# 四、各 Agent 实现

## 4.1 Agent 架构概览

```
Orchestrator (LangGraph)
├── IntentAgent      → 解析输入 → Intent（Python Dict）
├── PlannerAgent    → 规则模板 + 轻量 LLM → 候选方案
├── Brainstorm Layer
│   ├── 体验Agent  → 好玩度/放松度/新鲜感
│   ├── 安全Agent  → 评分 + 一票否决（veto）
│   ├── 效率Agent  → 路线耗时/时间利用率
│   └── 预算Agent  → 预算合理性
└── ExecutorAgent  → Mock API 执行预订
```

| Agent | Prompt 路径 | 调用方式 |
|-------|------------|---------|
| IntentAgent | `prompts/intent_agent.txt` | `call_llm_dict()` → Python Dict |
| PlannerAgent | `prompts/planner_agent.txt` | 规则模板填充 |
| 体验/安全/效率/预算Agent | `prompts/*_agent.txt` | `call_llm_dict()` → `AgentReview` |
| ExecutorAgent | 无 | 调用 `mock_book_poi()` |

## 4.2 统一 LLM 客户端（`agents/llm_client.py`）

```python
# agents/llm_config.py
LLM_BASE_URL=...         # 任意兼容 OpenAI Chat Completions 的 /v1 地址

# agents/llm_client.py
LLM_SETTINGS = get_llm_settings()

def call_llm(prompt, system_prompt=None, temperature=0.7, max_retries=2) -> str:
    # 调用 OpenAI-compatible Chat Completions，返回纯文本

def call_llm_dict(prompt, system_prompt=None, temperature=0.7) -> Dict:
    # call_llm() + eval() 解析为 Python Dict（不用 JSON）
```

## 4.3 IntentAgent（`agents/intent_agent.py`）

```python
# Prompt: prompts/intent_agent.txt（输出 Python Dict 格式）
# 方法签名:
class IntentAgent:
    def parse(self, user_input: str, trace_id: str = None) -> Intent:
        # 加载 prompts/intent_agent.txt → call_llm_dict() → _fill_defaults() → Intent
        pass
    def _fill_defaults(self, intent: Dict) -> Dict: pass
```

## 4.4 PlannerAgent（`agents/planner_agent.py`）

```python
# Prompt: prompts/planner_agent.txt
class PlannerAgent:
    def generate(self, intent: Intent, trace_id: str = None) -> List[Dict]:
        # 规则模板填充 → 返回 3 个候选方案
        pass
    def revise(self, candidates: List[Dict], reviews: Dict) -> List[Dict]:
        # 根据 Round1 反馈修改方案（切换室内/室外、调整预算）
        pass
    def regenerate(self, intent: Intent, exclude_options: List[str]) -> List[Dict]:
        # 安全否决后重新生成（排除被否决的 POI）
        pass
```

## 4.5 头脑风暴层（`agents/brainstorm/`）

### 4.5.1 4 个视角 Agent

| Agent | Prompt | 关键字段 |
|-------|--------|---------|
| 体验Agent | `prompts/experience_agent.txt` | score(0-10), veto=False |
| 安全Agent | `prompts/safety_agent.txt` | score, veto=True/False, veto_reason |
| 效率Agent | `prompts/efficiency_agent.txt` | score, concerns, suggestions |
| 预算Agent | `prompts/budget_agent.txt` | score, budget匹配度 |

```python
# 每个 Agent 结构相同:
class XxxAgent:
    def review(self, candidate: Dict, intent: Dict, trace_id: str = None) -> AgentReview:
        # 加载 prompt → call_llm_dict() → 返回 AgentReview
        pass
```

### 4.5.2 头脑风暴引擎（`agents/brainstorm/brainstorm_engine.py`）

```python
def run_brainstorm_round(candidates, round_num, trace_id=None) -> RoundReviews:
    # ThreadPoolExecutor(4 workers) 并行执行 4 个 Agent 评审所有候选
    # 单个 Agent 失败 → 重试 1 次 → 仍失败返回默认分 5.0
    # 返回: {"round": int, "reviews": {AgentName: [Review]}, "summary": str}
```

## 4.6 ExecutorAgent（`agents/executor_agent.py`）

```python
class ExecutorAgent:
    def execute(self, plan: Dict, trace_id: str = None) -> Dict[str, Any]:
        # 遍历 plan["pois"] → mock_book_poi() → 任意一个失败则返回失败
        # mock_get_weather() 查询天气
        pass
```

## 4.7 Orchestrator（`agents/orchestrator.py`）

> **调用边界**：`/api/plan` 通过 `agents/orchestrator.py::run_planning_flow()` 进入规划流程；该函数构造初始 `BrainstormState`，再调用 `graph.builder.build_graph().invoke()`。`orchestrator.py` 负责 API 响应结构、会话存储和顶层错误 fallback；`graph/nodes.py` 与 `graph/edges.py` 负责具体业务步骤。

```python
def aggregate_reviews(round1, round2, candidates) -> Tuple[float, Dict]:
    # 加权平均: 体验30% / 安全25% / 效率20% / 预算25%
    # 安全否决(veto=True) → 该方案 0 分
    # R1+R2 评分取平均，返回 (final_score, best_plan)
```

> **开发约定**：Prompt 外部化到 `prompts/`；Intent 输出 Python Dict（不用 JSON）；Planner 以规则为主、LLM 为辅。


# 五、Mock API 规范

## 5.1 Mock API 设计原则

| 原则 | 说明 |
|------|------|
| **差异化成功率** | 高优接口（搜索/订座）成功率更高，低优接口（评价/详情）成功率更低 |
| **环境变量注入** | 通过 `.env` 文件配置成功率，便于测试 |
| **Fallback 机制** | 调用失败时返回默认值，不中断流程 |
| **可观测** | 所有 Mock 调用记录 trace ID 和耗时 |

## 5.2 Mock API 列表

| API | 功能 | 成功率配置 | Fallback |
|-----|------|------------|----------|
| `mock_search_poi()` | 搜索 POI | `MOCK_HIGH_PRIORITY_RATE` (默认 0.95) | 返回空列表 `[]` |
| `mock_book_poi()` | 预订/订座 | `MOCK_HIGH_PRIORITY_RATE` (默认 0.95) | 返回 `success=False` |
| `mock_get_reviews()` | 获取评价 | `MOCK_LOW_PRIORITY_RATE` (默认 0.80) | 返回空列表 `[]` |
| `mock_get_poi_detail()` | 获取 POI 详情 | `MOCK_LOW_PRIORITY_RATE` (默认 0.80) | 返回基础信息 |
| `mock_get_weather()` | 天气查询 | 直接调用真实 API（不 Mock） | 询问用户 |

## 5.3 Mock API 实现（`tools/mock_api.py`）

```python
# tools/mock_api.py
"""Mock API 封装（含成功率控制、故障注入）"""

import os
import random
import time
from typing import Dict, Any, List


# ========== 配置读取 ==========

def _get_success_rate(api_type: str) -> float:
    """获取指定类型 API 的成功率"""
    if api_type == "high":
        return float(os.getenv("MOCK_HIGH_PRIORITY_RATE", "0.95"))
    elif api_type == "low":
        return float(os.getenv("MOCK_LOW_PRIORITY_RATE", "0.80"))
    else:
        return float(os.getenv("MOCK_SUCCESS_RATE", "0.85"))


# ========== Mock 实现 ==========

def mock_search_poi(
    keyword: str,
    city: str = "上海",
    trace_id: str = None
) -> List[Dict[str, Any]]:
    """
    Mock 搜索 POI。
    高优接口，成功率由 MOCK_HIGH_PRIORITY_RATE 控制。
    """
    start_time = time.time()
    success_rate = _get_success_rate("high")

    if random.random() < success_rate:
        # 成功：返回 Mock 数据
        result = _generate_mock_pois(keyword, city)
        _log_mock_call("search_poi", True, trace_id, start_time)
        return result
    else:
        # 失败：返回空列表（Fallback）
        _log_mock_call("search_poi", False, trace_id, start_time)
        return []


def mock_book_poi(
    poi_name: str,
    time_slot: str = None,
    trace_id: str = None
) -> Dict[str, Any]:
    """
    Mock 预订 POI。
    高优接口，成功率由 MOCK_HIGH_PRIORITY_RATE 控制。
    """
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
        _log_mock_call("book_poi", True, trace_id, start_time)
        return result
    else:
        result = {
            "success": False,
            "poi_name": poi_name,
            "error": f"{poi_name} 预订失败（Mock）",
            "message": "Mock 失败，符合预设成功率"
        }
        _log_mock_call("book_poi", False, trace_id, start_time)
        return result


def mock_get_reviews(
    poi_name: str,
    trace_id: str = None
) -> List[Dict[str, Any]]:
    """
    Mock 获取评价。
    低优接口，成功率由 MOCK_LOW_PRIORITY_RATE 控制。
    """
    start_time = time.time()
    success_rate = _get_success_rate("low")

    if random.random() < success_rate:
        result = _generate_mock_reviews(poi_name)
        _log_mock_call("get_reviews", True, trace_id, start_time)
        return result
    else:
        # 失败：返回空列表（Fallback）
        _log_mock_call("get_reviews", False, trace_id, start_time)
        return []


def mock_get_poi_detail(
    poi_name: str,
    trace_id: str = None
) -> Dict[str, Any]:
    """
    Mock 获取 POI 详情。
    低优接口，成功率由 MOCK_LOW_PRIORITY_RATE 控制。
    """
    start_time = time.time()
    success_rate = _get_success_rate("low")

    if random.random() < success_rate:
        result = _generate_mock_poi_detail(poi_name)
        _log_mock_call("get_poi_detail", True, trace_id, start_time)
        return result
    else:
        # 失败：返回基础信息（Fallback）
        result = {
            "name": poi_name,
            "address": "未知",
            "rating": 0.0,
            "price_range": "未知"
        }
        _log_mock_call("get_poi_detail", False, trace_id, start_time)
        return result


def mock_get_weather(
    city: str,
    date: str = None,
    trace_id: str = None
) -> Dict[str, Any]:
    """
    Mock 天气查询。
    ⚠️ MVP 阶段使用 Mock，未来可替换为真实 API（和风天气等）。
    """
    start_time = time.time()

    # Mock 数据
    result = {
        "city": city,
        "date": date or "today",
        "temperature": "22°C",
        "weather": "晴",
        "wind": "东风 3级",
        "humidity": "60%"
    }

    _log_mock_call("get_weather", True, trace_id, start_time)
    return result


# ========== 辅助函数 ==========

def _generate_mock_pois(keyword: str, city: str) -> List[Dict[str, Any]]:
    """生成 Mock POI 数据"""
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

    # 模糊匹配
    for key, pois in mock_data.items():
        if key in keyword:
            return pois

    # 默认返回
    return mock_data["火锅"]


def _generate_mock_reviews(poi_name: str) -> List[Dict[str, Any]]:
    """生成 Mock 评价数据"""
    return [
        {"user": "匿名用户1", "rating": 5, "content": "体验很好，推荐！"},
        {"user": "匿名用户2", "rating": 4, "content": "整体不错，性价比高"}
    ]


def _generate_mock_poi_detail(poi_name: str) -> Dict[str, Any]:
    """生成 Mock POI 详情"""
    return {
        "name": poi_name,
        "address": "上海市黄浦区南京东路100号",
        "rating": 4.7,
        "price_range": "100-150元/人",
        "opening_hours": "10:00-22:00",
        "phone": "021-12345678",
        "description": f"{poi_name} 是一家受欢迎的店铺"
    }


def _log_mock_call(
    api_name: str,
    success: bool,
    trace_id: str,
    start_time: float
):
    """记录 Mock 调用日志（可观测性）"""
    import structlog
    logger = structlog.get_logger()
    latency_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "mock_api_call",
        api_name=api_name,
        success=success,
        trace_id=trace_id,
        latency_ms=latency_ms
    )
```

## 5.4 Mock API 使用指南

### 5.4.1 在 Agent 中调用 Mock API

```python
# agents/executor_agent.py
from tools.mock_api import mock_book_poi, mock_search_poi

class ExecutorAgent:
    def execute(self, plan: Dict, trace_id: str = None) -> Dict[str, Any]:
        results = []
        for poi in plan.get("pois", []):
            # 调用 Mock API
            result = mock_book_poi(poi_name=poi, trace_id=trace_id)
            results.append(result)

            # 检查是否失败
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "results": results
                }

        return {"success": True, "results": results}
```

### 5.4.2 测试异常处理

```python
# tests/test_mock_failure.py
"""测试 Mock API 失败时的异常处理"""

import os
from tools.mock_api import mock_book_poi


def test_mock_failure():
    """测试 Mock 失败时的 Fallback"""
    # 设置低成功率
    os.environ["MOCK_HIGH_PRIORITY_RATE"] = "0.0"  # 100% 失败

    result = mock_book_poi(poi_name="海底捞", trace_id="test_001")

    # 验证失败处理
    assert result["success"] == False
    assert "error" in result

    print("✅ Mock 失败处理正常")


if __name__ == "__main__":
    test_mock_failure()
```

## 5.5 未来迁移到真实 API

```python
# tools/real_api.py
"""真实 API 调用（未来替换 Mock）"""

import httpx
import os


def search_poi_real(keyword: str, city: str = "上海") -> list:
    """
    真实 POI 搜索（示例：高德地图 API）。
    未来替换 mock_search_poi()。
    """
    api_key = os.getenv("AMAP_API_KEY")
    url = f"https://restapi.amap.com/v3/place/text"
    params = {
        "key": api_key,
        "keywords": keyword,
        "city": city,
        "output": "json"
    }

    response = httpx.get(url, params=params, timeout=5.0)
    data = response.json()

    if data["status"] == "1":
        return data["pois"]
    else:
        raise RuntimeError(f"API 调用失败：{data.get('info')}")


# 迁移策略：
# 1. 保留 mock_api.py 作为 Fallback
# 2. 在 real_api.py 中实现真实调用
# 3. 通过环境变量 USE_REAL_API=true 切换
```

---

# 六、异常处理实现

## 6.1 异常处理总览（对齐 Q1-Q8）

| 场景 | 策略 | 对齐 |
|------|------|------|
| Mock API 失败 | 差异化重试（高优2次，低优1次） | Q1 |
| 安全 Agent 否决 | 正常流程，最多重试2次 | Q2 |
| 重试策略 | 先原地 → 后换策略 | Q3 |
| Round 1 失败 | 跳过 R2，直接聚合 | Q4a |
| 单个 Agent 失败 | 重试1次 → 默认5分 | Q4b |
| 天气查询失败 | 询问用户（未来天气/温度） | Q4c |
| 用户中断 | 确认超时（5min→30min→释放）；头脑风暴/执行立即终止 | Q5 |
| 会话恢复 | 架构预留持久化接口（MVP不实现） | Q6 |
| Mock 失败控制 | 差异化成功率 + 环境变量 + Fallback | Q7 |
| 可观测性 | trace ID + 耗时 + 状态流转 | Q8 |

## 6.2 关键函数

### 重试装饰器（差异化重试，Q1）

```python
# agents/retry_manager.py
ERROR_PROBABILITY = {
    "high": ["mock_book_poi", "mock_search_poi"],     # 2次重试
    "low":  ["mock_get_reviews", "mock_get_poi_detail"]  # 1次重试
}

def retry_with_strategy(func, *args, max_retries=None, **kwargs):
    # 根据 func.__name__ 自动判断 max_retries
    # 指数退避（2**attempt）
    # 达到上限 → _fallback_result() 返回 fallback
    pass
```

### 安全否决重试（Q2）

```python
# graph/nodes.py
def replan(state):
    # replan_count >= 2 → FAILED
    # 否则 → PlannerAgent.regenerate(exclude=vetoed) → replan_count+1, round=0
```

### 重试策略：先原地，后换策略（Q3）

```python
# agents/executor_agent.py
def execute_with_retry(self, plan):
    # 第1次失败 → 原地重试
    # 第2次失败 → _modify_plan() 换策略（室内↔室外）
    # 第3次 → 返回失败
    pass
```

### 用户中断处理（Q5）

```python
# 确认状态超时: timeout_count=0 → 5min提醒 → 1 → 30min保留 → 2 → 释放
# 头脑风暴/执行: 立即终止
```

## 6.3 会话恢复（Q6）

> 预留接口（`agents/orchestrator.py` → `SessionManager`），MVP 不实现，Future 接入 Redis。

> 详细 Mock 失败控制见第5章。


# 七、可观测性（trace）

## 7.1 可观测性设计（对齐 Q8）

| 层级 | 内容 | 实现方式 |
|------|------|----------|
| **Trace ID** | 全链路追踪 ID | `uuid.uuid4()` 生成，传播到所有 Agent |
| **耗时追踪** | 每个 Node 的耗时（ms） | `time.time()` 计算，存入 `state["latency_ms"]` |
| **状态流转** | 状态转换记录 | 在 Node 函数中记录 `trip_state` 变化 |
| **LLM 调用** | LLM 输入/输出日志 | 在 `llm_client.py` 中记录 |
| **Mock API 调用** | Mock 成功率、耗时 | 在 `mock_api.py` 中记录 |

## 7.2 Trace ID 生成与传播

```python
# middleware/trace.py
"""Trace ID 生成与传播中间件"""

import uuid
import structlog
from typing import Dict, Any


logger = structlog.get_logger()


def generate_trace_id() -> str:
    """生成全链路追踪 ID"""
    return str(uuid.uuid4())


def inject_trace_id(state: Dict[str, Any], parent_trace_id: str = None) -> Dict[str, Any]:
    """
    向状态中注入 trace ID。
    如果是子调用，记录 parent_trace_id。
    """
    state["trace_id"] = generate_trace_id()
    if parent_trace_id:
        state["parent_trace_id"] = parent_trace_id
    return state


def log_with_trace(
    logger,
    event: str,
    state: Dict[str, Any],
    **kwargs
):
    """
    带 trace ID 的日志记录。
    所有日志都包含 trace_id、session_id、trip_state。
    """
    logger.info(
        event,
        trace_id=state.get("trace_id"),
        parent_trace_id=state.get("parent_trace_id"),
        session_id=state.get("session_id"),
        trip_state=state.get("trip_state"),
        latency_ms=state.get("latency_ms"),
        **kwargs
    )


def extract_trace_from_state(state: Dict[str, Any]) -> Dict[str, str]:
    """从状态中提取 trace 信息（用于日志上下文）"""
    return {
        "trace_id": state.get("trace_id", "unknown"),
        "parent_trace_id": state.get("parent_trace_id"),
        "session_id": state.get("session_id", "unknown")
    }
```

## 7.3 在 Node 函数中集成 Trace

```python
# graph/nodes.py（节选）
"""在所有 Node 函数中集成 trace"""

import time
from middleware.trace import log_with_trace


def parse_intent(state: BrainstormState) -> Dict[str, Any]:
    """IntentAgent：解析用户意图（带 trace）"""
    start_time = time.time()

    # 注入 trace ID（如果尚未注入）
    if not state.get("trace_id"):
        from middleware.trace import inject_trace_id
        state = inject_trace_id(state)

    from agents.intent_agent import IntentAgent

    try:
        agent = IntentAgent()
        intent = agent.parse(
            user_input=state["user_input"],
            trace_id=state["trace_id"]
        )

        # 记录成功日志
        log_with_trace(
            logger,
            "intent_parsing_completed",
            state,
            intent=intent
        )

        return {
            "intent": intent,
            "trip_state": "INTENT_PARSING",
            "latency_ms": int((time.time() - start_time) * 1000)
        }
    except Exception as e:
        # 记录失败日志
        log_with_trace(
            logger,
            "intent_parsing_failed",
            state,
            error=str(e)
        )
        state["error"] = str(e)
        return state
```

## 7.4 LLM 调用日志

```python
# agents/llm_client.py（节选）
"""LLM 调用日志（带 trace）"""

import structlog
from agents.llm_config import get_llm_settings

logger = structlog.get_logger()
LLM_SETTINGS = get_llm_settings()


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_retries: int = 2,
    trace_id: str = None
) -> str:
    """
    统一 LLM 调用接口（带日志）。
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    for attempt in range(max_retries + 1):
        try:
            # 记录请求日志
            logger.info(
                "llm_request",
                trace_id=trace_id,
                model=LLM_SETTINGS.model,
                provider=LLM_SETTINGS.provider,
                temperature=temperature,
                attempt=attempt + 1,
                prompt_length=len(prompt)
            )

            response = _get_openai_client().chat.completions.create(
                model=LLM_SETTINGS.model,
                messages=messages,
                temperature=temperature,
                max_tokens=LLM_SETTINGS.max_tokens,
            )
            content = response.choices[0].message.content

            logger.info(
                "llm_response",
                trace_id=trace_id,
                model=LLM_SETTINGS.model,
                provider=LLM_SETTINGS.provider,
                response_length=len(content),
                attempt=attempt + 1
            )

            return content
        except Exception as e:
            logger.error(
                "llm_error",
                trace_id=trace_id,
                error=str(e),
                attempt=attempt + 1
            )
            if attempt == max_retries:
                raise RuntimeError(f"LLM 调用异常：{e}")
            continue

    raise RuntimeError("LLM 调用达到最大重试次数")
```

## 7.5 Mock API 调用日志

```python
# tools/mock_api.py（节选）
"""Mock API 调用日志（带 trace）"""

import structlog
from middleware.trace import extract_trace_from_state

logger = structlog.get_logger()


def _log_mock_call(
    api_name: str,
    success: bool,
    trace_id: str,
    start_time: float
):
    """记录 Mock 调用日志"""
    import time
    latency_ms = int((time.time() - start_time) * 1000)

    log_data = {
        "api_name": api_name,
        "success": success,
        "trace_id": trace_id,
        "latency_ms": latency_ms
    }

    if success:
        logger.info("mock_api_success", **log_data)
    else:
        logger.warning("mock_api_failure", **log_data)
```

## 7.6 日志配置（`config.py`）

```python
# config.py
"""日志配置（使用 structlog）"""

import structlog
import sys


def configure_logging(log_level: str = "INFO"):
    """配置 structlog"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer()  # 开发环境：彩色输出
            # structlog.processors.JSONRenderer()  # 生产环境：JSON 格式
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level)
        ),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=False,
    )


# 在应用启动时调用
configure_logging(os.getenv("LOG_LEVEL", "INFO"))
```

## 7.7 日志示例

### 正常流程日志

```
2026-05-19T23:30:00.123456Z [info] intent_parsing_completed
    trace_id=7a3b2c1d-4e5f-6a7b-8c9d-0e1f2a3b4c5d
    session_id=sess_001
    trip_state=INTENT_PARSING
    latency_ms=123
    intent={"time": {...}, ...}

2026-05-19T23:30:00.456789Z [info] llm_request
    trace_id=7a3b2c1d-4e5f-6a7b-8c9d-0e1f2a3b4c5d
    model=qwen-plus
    temperature=0.3
    attempt=1
    prompt_length=256

2026-05-19T23:30:02.123456Z [info] llm_response
    trace_id=7a3b2c1d-4e5f-6a7b-8c9d-0e1f2a3b4c5d
    model=qwen-plus
    response_length=128
    attempt=1

2026-05-19T23:30:03.456789Z [info] mock_api_success
    api_name=search_poi
    success=True
    trace_id=7a3b2c1d-4e5f-6a7b-8c9d-0e1f2a3b4c5d
    latency_ms=45
```

### 异常流程日志

```
2026-05-19T23:35:00.123456Z [warning] mock_api_failure
    api_name=book_poi
    success=False
    trace_id=9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d
    latency_ms=120

2026-05-19T23:35:00.456789Z [error] execution_failed
    trace_id=9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d
    error=预订失败（Mock）
    trip_state=EXECUTING
```

---

# 八、测试策略

## 8.1 测试金字塔

```
        /‾‾\
       / E2E  \    E2E 测试（Streamlit 前端 + FastAPI 后端）
      /__________\
     /            \   集成测试（LangGraph 状态机）
    /  集成测试    \
   /______________\
  /                \  单元测试（LLM Client, Mock API, Agent）
 /   单元测试      \
/__________________\
```

| 测试类型 | 工具 | 覆盖率目标 |
|----------|------|------------|
| 单元测试 | `pytest` | 核心函数 >= 70% |
| 集成测试 | `pytest` + LangGraph | 状态机流程 100% |
| E2E 测试 | Manual | Hackathon 演示场景 100% |

## 8.2 单元测试

### 8.2.1 测试 `llm_client.py`

```python
# tests/test_llm_client.py
"""测试 LLM 客户端"""

import pytest
from unittest.mock import patch, MagicMock
from agents.llm_client import call_llm, parse_dict_from_response


def test_call_llm_success():
    """测试 LLM 调用成功"""
    # Mock OpenAI-compatible Chat Completions
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "测试响应"

    with patch("agents.llm_client._get_openai_client") as mock_get_client:
        mock_get_client.return_value.chat.completions.create.return_value = mock_response
        result = call_llm(prompt="测试提示")
        assert result == "测试响应"


def test_call_llm_failure_with_retry():
    """测试 LLM 调用失败并重试"""
    # Mock 第一次失败，第二次成功
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "成功"
    mock_responses = [
        ValueError("Internal Server Error"),
        mock_response,
    ]

    with patch("agents.llm_client._get_openai_client") as mock_get_client:
        mock_get_client.return_value.chat.completions.create.side_effect = mock_responses
        result = call_llm(prompt="测试提示", max_retries=1)
        assert result == "成功"


def test_parse_dict_from_response():
    """测试解析 LLM 输出为 Dict"""
    # 测试直接输出 Dict
    response = "{'key': 'value', 'num': 123}"
    result = parse_dict_from_response(response)
    assert result == {"key": "value", "num": 123}

    # 测试被 ```python ``` 包裹
    response = "```python\n{'key': 'value'}\n```"
    result = parse_dict_from_response(response)
    assert result == {"key": "value"}

    # 测试 JSON 格式
    response = '{"key": "value", "num": 123}'
    result = parse_dict_from_response(response)
    assert result == {"key": "value", "num": 123}
```

### 8.2.2 测试 `mock_api.py`

```python
# tests/test_mock_api.py
"""测试 Mock API"""

import os
import random
from tools.mock_api import mock_book_poi, mock_search_poi


def test_mock_book_poi_success():
    """测试 Mock 预订成功"""
    # 设置高成功率
    os.environ["MOCK_HIGH_PRIORITY_RATE"] = "1.0"  # 100% 成功

    result = mock_book_poi(poi_name="海底捞", trace_id="test_001")
    assert result["success"] == True
    assert "booking_id" in result


def test_mock_book_poi_failure():
    """测试 Mock 预订失败"""
    # 设置低成功率
    os.environ["MOCK_HIGH_PRIORITY_RATE"] = "0.0"  # 100% 失败

    result = mock_book_poi(poi_name="海底捞", trace_id="test_001")
    assert result["success"] == False
    assert "error" in result


def test_mock_search_poi_failure_fallback():
    """测试搜索失败时的 Fallback（返回空列表）"""
    os.environ["MOCK_HIGH_PRIORITY_RATE"] = "0.0"  # 100% 失败

    result = mock_search_poi(keyword="火锅", trace_id="test_001")
    assert result == []  # Fallback：返回空列表
```

### 8.2.3 测试 `BrainstormState` 转换

```python
# tests/test_state.py
"""测试 LangGraph 状态转换"""

from graph.state import BrainstormState, TripState, Intent, AgentReview, RoundReviews


def test_state_initialization():
    """测试状态初始化"""
    state = BrainstormState(
        session_id="sess_001",
        trip_state=TripState.IDLE,
        user_input="测试输入",
        intent=None,
        candidates=None,
        round=0,
        round1_reviews=None,
        round2_reviews=None,
        final_score=None,
        best_plan=None,
        replan_count=0,
        error=None,
        trace_id="trace_001",
        parent_trace_id=None,
        latency_ms=None
    )

    assert state["session_id"] == "sess_001"
    assert state["trip_state"] == TripState.IDLE
    assert state["round"] == 0


def test_intent_structure():
    """测试 Intent 结构"""
    intent = Intent(
        time={"range": "14:00-18:00", "flexibility": "±1h"},
        group={"type": "family", "count": 3, "children": []},
        scene="parent_child",
        constraints={"max_distance_km": 10, "budget": 200},
        preferences={"food": "healthy"},
        missing_fields=[]
    )

    assert intent["time"]["range"] == "14:00-18:00"
    assert intent["constraints"]["budget"] == 200
```

## 8.3 集成测试

### 8.3.1 测试 LangGraph 状态机完整流程

```python
# tests/test_graph_integration.py
"""测试 LangGraph 状态机集成"""

import pytest
from graph.builder import graph
from graph.state import BrainstormState, TripState


def test_full_flow_success():
    """测试完整流程（成功）"""
    initial_state = BrainstormState(
        session_id="test_sess_001",
        trip_state=TripState.IDLE,
        user_input="周末想带父母和孩子去玩，预算 300 左右",
        intent=None,
        candidates=None,
        round=0,
        round1_reviews=None,
        round2_reviews=None,
        final_score=None,
        best_plan=None,
        replan_count=0,
        error=None,
        trace_id="test_trace_001",
        parent_trace_id=None,
        latency_ms=None
    )

    # 运行状态机
    final_state = graph.invoke(initial_state)

    # 验证：最终状态应该是 COMPLETED 或 FAILED
    assert final_state["trip_state"] in [TripState.COMPLETED, TripState.FAILED]

    # 如果成功，应该有 best_plan 和 final_score
    if final_state["trip_state"] == TripState.COMPLETED:
        assert final_state["best_plan"] is not None
        assert final_state["final_score"] is not None
        assert final_state["final_score"] > 0


def test_safety_veto_triggers_replan():
    """测试安全否决触发重规划"""
    # 构造一个被安全 Agent 否决的状态
    initial_state = BrainstormState(
        session_id="test_sess_002",
        trip_state=TripState.BRAINSTORMING,
        user_input="测试输入",
        intent=None,
        candidates=[{"id": "plan_1", "name": "测试方案"}],
        round=1,
        round1_reviews={
            "round": 1,
            "reviews": {
                "安全Agent": [{
                    "candidate_id": "plan_1",
                    "review": {
                        "agent": "安全Agent",
                        "score": 2.0,
                        "veto": True,
                        "veto_reason": "存在安全隐患"
                    }
                }]
            },
            "summary": "安全否决"
        },
        round2_reviews=None,
        final_score=None,
        best_plan=None,
        replan_count=0,
        error=None,
        trace_id="test_trace_002",
        parent_trace_id=None,
        latency_ms=None
    )

    # 运行状态机
    final_state = graph.invoke(initial_state)

    # 验证：应该触发重规划（replan_count > 0）或失败
    assert final_state["replan_count"] > 0 or final_state["trip_state"] == TripState.FAILED
```

## 8.4 E2E 测试（Hackathon 演示场景）

### 8.4.1 演示场景测试用例

| 场景 | 用户输入 | 预期结果 |
|------|----------|----------|
| **场景 1：亲子半日游** | "周末想带父母和孩子去玩，想要轻松一点的活动，预算 300 左右" | 推荐室内亲子活动（如万达宝贝王） |
| **场景 2：朋友聚会** | "今晚和朋友们聚餐，想吃火锅，人均 100 左右" | 推荐火锅店（如海底捞） |
| **场景 3：情侣约会** | "明天和女朋友约会，想看电影，然后去吃西餐" | 推荐影院 + 西餐厅组合方案 |
| **场景 4：安全否决** | "想去野外游泳"（模拟安全风险） | 安全 Agent 否决，触发重规划 |
| **场景 5：预算超限** | "想去迪士尼，预算 100"（预算不足） | 预算 Agent 低分，推荐替代方案 |

### 8.4.2 手动测试 Checklist

```
E2E 测试 Checklist（Hackathon 演示前必做）

前端（Streamlit）：
- [ ] 打开 http://localhost:8501 能正常加载
- [ ] 输入场景 1，能正常输出推荐方案
- [ ] 点击"确认"按钮，能正常执行预订
- [ ] 显示评分矩阵（4 个 Agent 评分）
- [ ] 显示 trace ID（可观测性）

后端（FastAPI）：
- [ ] 访问 http://localhost:8000/docs 能打开 Swagger UI
- [ ] 调用 /api/parse_intent 能正常解析意图
- [ ] 调用 /api/generate_plans 能生成候选方案
- [ ] 调用 /api/execute_plan 能执行预订（Mock）

LangGraph 状态机：
- [ ] 完整流程能跑通（从用户输入到预订完成）
- [ ] 安全否决能触发重规划
- [ ] Mock API 失败时能正确处理（不中断流程）

日志：
- [ ] 所有关键操作都有 trace ID
- [ ] LLM 调用有输入/输出日志
- [ ] Mock API 调用有成功/失败日志
```

## 8.5 运行测试

```bash
# 激活 conda 环境
conda activate py312

# 运行所有测试
cd backend
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_llm_client.py -v

# 运行特定测试函数
python -m pytest tests/test_llm_client.py::test_call_llm_success -v

# 查看覆盖率
python -m pytest tests/ --cov=agents --cov-report=html
# 打开 htmlcov/index.html 查看覆盖率报告
```

---

# 九、Hackathon Demo 指南

## 9.1 Demo 准备 Checklist

### 9.1.1 演示前必做

```bash
# 1. 启动服务
# 终端 1：后端
conda activate py312
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# 终端 2：前端
conda activate py312
cd frontend
streamlit run app.py --server.port 8501

# 2. 验证后端
curl http://localhost:8000/health
# 预期返回：{"status": "ok", "version": "1.0.0"}

# 3. 验证前端
open http://localhost:8501

# 4. 验证 LLM 配置
python -c "from agents.llm_client import call_llm; print(call_llm('你好'))"
# 预期输出：LLM 响应
```

### 9.1.2 技术检查

| 检查项 | 验证方式 | 通过标准 |
|--------|----------|----------|
| 后端启动 | `curl localhost:8000/health` | 返回 `{"status": "ok"}` |
| 前端启动 | 浏览器打开 localhost:8501 | 页面正常加载 |
| LLM 调用 | 测试 `call_llm` | 返回正常响应 |
| Mock API | 测试 `mock_book_poi` | 返回成功/失败结果 |
| LangGraph 流程 | 运行完整流程测试 | 无异常抛出 |

## 9.2 Demo 场景设计

### 场景 1：亲子半日游（核心演示）

**用户输入**：
> "周末想带父母和孩子（5 岁）去玩，想要轻松一点的活动，预算 300 左右"

**演示要点**：
1. 展示意图解析结果（Intent 输出）
2. 展示候选方案生成（3 个候选）
3. 展示 Round 1 评审（4 个 Agent 并行）
4. 展示 Round 2 复评（修改后的方案）
5. 展示最终推荐（评分 + 方案详情）
6. 展示执行预订（Mock 成功）

**预期流程**：
```
用户输入 → 意图解析 → 生成方案 → Round 1 → Round 2 → 确认 → 预订
```

### 场景 2：安全否决演示

**用户输入**：
> "想去游泳馆玩"

**演示要点**：
1. 展示安全 Agent 否决（veto=True）
2. 展示触发重规划（replan_count +1）
3. 展示新方案生成
4. 展示最大重试次数（2 次）

**预期流程**：
```
安全否决 → 重规划（R1） → 安全否决 → 重规划（R2） → 失败或通过
```

### 场景 3：异常处理演示

**用户输入**：
> "今晚和朋友吃饭，预算 500"

**演示要点**（通过 Mock 失败）：
1. 展示 Mock API 失败日志
2. 展示重试机制
3. 展示 Fallback 结果
4. 展示流程不中断

**演示方式**：
```bash
# 设置低成功率，演示失败场景
export MOCK_HIGH_PRIORITY_RATE=0.0
conda activate py312
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 9.3 Demo 演示稿

### 9.3.1 开场介绍（1 分钟）

```
大家好，我们今天演示的是一个本地生活短时活动规划 AI Agent。

核心能力：
1. 自然语言理解 → 结构化意图
2. 多 Agent 头脑风暴 → 方案评审
3. 智能推荐 → 个性化方案
4. 一键预订 → 实际落地

技术亮点：
- 基于 LangGraph 状态机
- 4 个视角 Agent 并行评审
- 安全否决机制保障体验
- Mock API 支持快速验证
```

### 9.3.2 核心演示（3 分钟）

```
现在演示核心功能...

[演示场景 1：亲子半日游]

1. 用户输入自然语言需求
2. 系统解析意图（显示解析结果）
3. 生成 3 个候选方案
4. 4 个 Agent 并行评审（体验/安全/效率/预算）
5. Round 2 复评（根据反馈修改）
6. 聚合评分，输出最佳方案
7. 一键预订（Mock）

[切换到后端日志，展示 trace ID 和耗时]
```

### 9.3.3 异常处理演示（1 分钟）

```
接下来演示异常处理...

[演示场景 2：安全否决]

1. 用户输入"想去游泳馆玩"
2. 安全 Agent 发现隐患，否决方案
3. 系统自动触发重规划
4. 生成新方案
5. 重复直到通过或达到上限

[切换到日志，展示否决和重规划过程]
```

### 9.3.4 技术架构（1 分钟）

```
最后介绍一下技术架构...

系统分为三层：
1. Agent 层：Intent / Planner / Brainstorm / Executor
2. 状态机层：LangGraph 状态图
3. 工具层：Mock API / 天气查询

关键设计：
- 状态用 TypedDict，无 checkpointer（MVP）
- Prompt 外部化，便于迭代
- Mock 差异化成功率控制
- Trace ID 全链路追踪
```

## 9.4 现场 Q&A 准备

### 常见问题

| 问题 | 回答要点 |
|------|----------|
| 为什么用 LangGraph？ | 状态机适合多轮对话 + 条件分支，易于调试和扩展 |
| 4 个 Agent 如何协作？ | 并行评审，结果聚合，支持否决和重规划 |
| Mock API 如何保证真实性？ | 差异化成功率 + 环境变量控制，可模拟各种场景 |
| 为什么不调用真实 API？ | MVP 阶段专注核心逻辑，架构预留接口 |
| 如何扩展到真实预订？ | 替换 `tools/mock_api.py` 为 `tools/real_api.py` |

---

# 十、已知限制 & V1 规划

## 10.1 MVP 已知限制

| 限制项 | 说明 | 解决方案（V1） |
|--------|------|---------------|
| **无会话持久化** | 刷新页面丢失会话 | 接入 Redis + 数据库 |
| **无用户认证** | 任何人可访问 | 接入 OAuth / JWT |
| **Mock API** | 不调用真实服务 | V1 接入高德/美团 API |
| **单轮对话** | 不支持多轮澄清 | V1 支持意图补全询问 |
| **无知识库** | 依赖 LLM 泛化能力 | V1 接入本地知识库（RAG） |
| **无性能优化** | LLM 调用耗时 | V1 接入缓存 + 异步 |
| **无流式输出** | 等待 LLM 完成 | V1 接入 SSE 流式 |

## 10.2 V1 规划

### V1.0（MVP）：核心能力闭环

| 功能 | 状态 | 说明 |
|------|------|------|
| 自然语言意图解析 | ✅ MVP | LLM 解析 |
| 候选方案生成 | ✅ MVP | 规则模板 |
| 多 Agent 头脑风暴 | ✅ MVP | 4 Agent 并行 |
| 安全否决机制 | ✅ MVP | 重规划 2 次 |
| Mock API | ✅ MVP | 可配置成功率 |
| **会话持久化** | 📋 V1 | Redis + PostgreSQL |
| **用户认证** | 📋 V1 | JWT |
| **真实 API** | 📋 V1 | 高德/美团 |

### V1.1：智能化提升

| 功能 | 说明 |
|------|------|
| **RAG 知识库** | 接入本地知识库，提升推荐准确性 |
| **流式输出** | SSE 流式输出，减少等待感 |
| **多轮对话** | 支持意图补全、方案修改 |
| **历史记录** | 查看历史规划记录 |

### V1.2：商业化准备

| 功能 | 说明 |
|------|------|
| **真实预订** | 接入美团/高德真实 API |
| **支付闭环** | 微信/支付宝支付 |
| **评价系统** | 真实用户评价接入 |
| **性能优化** | LLM 缓存、异步调用 |

## 10.3 技术债务

| 债务项 | 优先级 | 说明 |
|--------|--------|------|
| **Prompt 迭代** | 高 | 当前 Prompt 较简单，需持续优化 |
| **Agent 评分校准** | 高 | 4 个 Agent 评分标准需对齐 |
| **异常场景覆盖** | 中 | Mock 失败场景需全面测试 |
| **性能监控** | 中 | 接入 APM（如 Sentry） |
| **代码测试覆盖** | 中 | 当前测试较简单，需补充 |

## 10.4 架构演进路线

```
MVP (现在)              V1.0                 V1.1                 V1.2
─────────────────────────────────────────────────────────────
LangGraph              LangGraph            LangGraph            LangGraph
+ TypedDict            + Checkpointer       + RAG                + Real APIs
                        + Redis              + SSE                + Payment
                                             + Multi-turn         + Eval
```

---

# 附录

## A. 环境变量完整列表

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `LLM_API_KEY` | - | 模型平台 API Key（必填） |
| `LLM_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | OpenAI-compatible `/v1` 地址 |
| `LLM_MODEL` | `qwen-plus` | LLM 模型 |
| `LLM_MAX_TOKENS` | `2048` | 单次 LLM 响应 token 上限 |
| `LLM_FORCE_TEMPERATURE` | - | 可选；强制覆盖调用温度，兼容有固定温度要求的模型 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `TRACE_LEVEL` | `basic` | Trace 级别 |
| `MOCK_HIGH_PRIORITY_RATE` | `0.95` | 高优接口成功率 |
| `MOCK_LOW_PRIORITY_RATE` | `0.80` | 低优接口成功率 |
| `BACKEND_HOST` | `0.0.0.0` | 后端监听地址 |
| `BACKEND_PORT` | `8000` | 后端端口 |
| `USE_REAL_APIS` | `true` | 是否优先调用真实 API，失败后 fallback 到 Mock |
| `REAL_API_TIMEOUT` | `5` | 真实 API 超时时间（秒） |
| `BACKEND_URL` | `http://localhost:8000` | 前端调用后端地址 |

## B. 文件路径速查

| 功能 | 文件路径 |
|------|----------|
| 状态定义 | `backend/graph/state.py` |
| Node 函数 | `backend/graph/nodes.py` |
| 条件边 | `backend/graph/edges.py` |
| 状态机构建 | `backend/graph/builder.py` |
| LLM 客户端 | `backend/agents/llm_client.py` |
| Intent Agent | `backend/agents/intent_agent.py` |
| Planner Agent | `backend/agents/planner_agent.py` |
| Executor Agent | `backend/agents/executor_agent.py` |
| 头脑风暴引擎 | `backend/agents/brainstorm/brainstorm_engine.py` |
| Mock API | `backend/tools/mock_api.py` |
| Trace 中间件 | `backend/middleware/trace.py` |
| Prompt 模板 | `backend/prompts/*.txt` |

## C. 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| `LLM_API_KEY` 错误 | Key 过期或无效 | 到模型平台重新申请 |
| LLM 调用超时 | 网络问题或模型负载高 | 检查网络，增加超时重试 |
| Mock API 100% 失败 | `MOCK_HIGH_PRIORITY_RATE=0.0` | 重置环境变量 |
| 前端无法连接后端 | CORS 问题或后端未启动 | 检查后端日志，检查 CORS 配置 |
| 状态机卡住 | 条件边逻辑错误 | 检查 `edges.py` 中的路由函数 |

---

**文档终**
