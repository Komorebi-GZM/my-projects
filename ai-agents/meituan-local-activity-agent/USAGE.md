# 本地生活短时活动规划 Agent — 使用指南

> 美团 Hackathon MVP · AI Agent 自动生成活动方案

## 快速开始（Docker 推荐）

### 前置条件

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- 任意支持 OpenAI Chat Completions 接口的模型平台账号

### 1. 配置团队本地密钥

复制模板并编辑 `backend/.env`。队友只需要替换前三项：

```bash
cp backend/.env.example backend/.env
```

```env
LLM_API_KEY=自己的 API Key
LLM_BASE_URL=模型平台的 /v1 地址
LLM_MODEL=模型名称
```

常见示例：

```env
# 阿里百炼 OpenAI-compatible
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus

# Kimi
LLM_BASE_URL=https://api.moonshot.cn/v1
LLM_MODEL=kimi-k2.6

# DeepSeek
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

### 2. 启动

```bash
docker compose up -d --build
```

### 3. 访问

| 服务 | 地址 |
|------|------|
| 前端 UI | http://localhost:8501 |
| 后端 API | http://localhost:8000 |
| 健康检查 | http://localhost:8000/health |

### 4. 停止

```bash
docker compose down
```

---

## 本地开发（无 Docker）

### 前置条件

- Python >= 3.11, conda 环境 `py312`
- 任意支持 OpenAI Chat Completions 接口的模型平台账号

### 安装

```bash
conda activate py312

# 后端
cd backend
pip install -r requirements.txt
cp .env.example .env   # 编辑 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL

# 前端
cd ../frontend
pip install -r requirements.txt
```

### 启动

```bash
# 终端 1：后端
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2：前端
cd frontend
streamlit run app.py --server.port 8501
```

### 测试

```bash
cd backend
python -m pytest tests/ -v
```

---

## API 接口

### POST /api/plan

生成活动规划方案。

**请求：**

```json
{"user_input": "周末和女朋友去北京玩，预算2000以内，别太累"}
```

**响应字段：**

| 字段 | 说明 |
|------|------|
| `session_id` | 会话 ID |
| `intent` | 意图解析结果（时间/人群/预算/偏好） |
| `candidates` | 3 个候选方案 |
| `round1_reviews` | 第一轮 4 Agent 评审 |
| `round2_reviews` | 第二轮评审 |
| `best_plan` | 最佳方案 |
| `final_score` | 综合评分 |
| `execution_result` | Mock 预订执行结果 |

### GET /api/session/{session_id}

查询历史会话结果。

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_API_KEY` | — | 模型平台 API Key，队友各自填写自己的 |
| `LLM_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | OpenAI-compatible `/v1` 地址 |
| `LLM_MODEL` | `qwen-plus` | 模型名（阿里: qwen-plus / Kimi: kimi-k2.6 / DeepSeek: deepseek-chat） |
| `LLM_MAX_TOKENS` | `2048` | 单次 LLM 响应 token 上限 |
| `LLM_FORCE_TEMPERATURE` | — | 可选；某些模型要求固定温度时填写，如 `1.0` |
| `MOCK_HIGH_PRIORITY_RATE` | `0.95` | 高优 Mock 成功率 |
| `MOCK_LOW_PRIORITY_RATE` | `0.80` | 低优 Mock 成功率 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

---

## 项目结构

```
├── backend/              # FastAPI 后端
│   ├── agents/           # Agent 实现（LLM / Intent / Planner / Brainstorm / Executor）
│   ├── graph/            # LangGraph 状态机（state / nodes / edges / builder）
│   ├── tools/            # Mock API + 工具函数
│   ├── schemas/          # TypedDict 数据模型
│   ├── prompts/          # 外部化 Prompt 文件
│   ├── middleware/       # Trace 中间件
│   └── tests/            # 测试
├── frontend/             # Streamlit 前端
│   ├── pages/            # 多页面（home / chat / history）
│   ├── components/       # UI 组件（plan_card / score_matrix / trace_viewer）
│   └── app.py            # 入口
├── docker-compose.yml    # Docker 编排
├── .dockerignore
└── USAGE.md
```
