# AGENTS.md

## 项目概述

本地生活短时活动规划 Agent（MVP）。Python >= 3.11，需要 conda 环境 `py312`。

## 启动命令

需要 **两个独立终端**，都先激活 `py312` 环境：

```bash
# 终端 1：后端
conda activate py312
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# 终端 2：前端  
conda activate py312
cd frontend
streamlit run app.py --server.port 8501

# 健康检查
curl http://localhost:8000/health
```

**注意**：
- 必须先 `conda activate py312`，确保使用 Python 3.12
- 不要在命令前加 `cd backend &&`，会导致环境未激活
- Makefile 尚未创建，不要用 `make start`

## 目录结构

```
backend/           # FastAPI 后端
  agents/         # Agent 实现（Intent/Planner/Executor/Orchestrator）
    brainstorm/   # 4 个视角 Agent（体验/安全/效率/预算）
  graph/          # LangGraph 状态机（state/nodes/edges/builder）
  tools/          # Mock API + 真实 API
  middleware/     # Trace 中间件
  schemas/        # 数据模型（intent/plan/review）
frontend/         # Streamlit 前端
  pages/          # 多页面（home/chat/history）
  components/     # UI 组件（plan_card/score_matrix/trace_viewer）
docs/             # DEV_GUIDE_MVP.md（完整技术文档）
```

## 关键架构事实

- **状态机**：LangGraph + TypedDict（无 checkpointer）
- **LLM 调用**：通过 `agents/llm_client.py` 统一入口；`agents/llm_config.py` 隔离配置，统一使用 OpenAI-compatible Chat Completions 接口
- **Prompt 管理**：外部化到 `prompts/*.txt`
- **Intent 输出**：Python Dict（不用 JSON）
- **Planner 策略**：规则模板为主，轻量 LLM 为辅

## 环境变量

`.env` 文件在 `backend/` 和 `frontend/` 目录分别配置：

```env
# backend/.env
LLM_API_KEY=your_api_key_here  # 必填，模型平台申请
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1  # 任意 OpenAI-compatible /v1 地址
LLM_MODEL=qwen-plus            # 阿里百炼: qwen-plus | Kimi: kimi-k2.6 | DeepSeek: deepseek-chat
LLM_MAX_TOKENS=2048
LOG_LEVEL=INFO
MOCK_HIGH_PRIORITY_RATE=0.95
MOCK_LOW_PRIORITY_RATE=0.80

# frontend/.env
BACKEND_URL=http://localhost:8000
```

## 测试

```bash
cd backend
python -m pytest tests/ -v
python -m pytest tests/test_llm_client.py::test_call_llm_success -v  # 单个测试
```

## 当前状态

MVP 核心功能已实现：Intent 解析、方案生成、双轮头脑风暴评审（4 Agent 并行）、加权汇总、安全否决重规划、Mock API。参考 `docs/DEV_GUIDE_MVP.md` 了解完整技术规范，参考 `.workbuddy/memory/MODIFICATION_DIRECTIONS.md` 查看待优化项。

## 参考文档

- `docs/DEV_GUIDE_MVP.md` — 完整技术文档（含状态机、Agent、Mock API 规范）
- `docs/DEV_README.md` — 文档目录速查
