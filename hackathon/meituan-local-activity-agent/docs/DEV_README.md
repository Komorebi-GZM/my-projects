# DEV_README — 开发指南导航

> `DEV_GUIDE_MVP.md` 的目录速查手册。按章节定位内容，避免在无际文档中盲目翻找。

---

## 📖 章节速查表

| 章节 | 标题 | 内容摘要 | 关键文件 |
|------|------|----------|----------|
| **一** | [快速启动](#一快速启动) | conda 环境 / 依赖安装 / 前后端启动 | `backend/requirements.txt`, `frontend/requirements.txt` |
| **二** | [项目结构](#二项目结构) | 完整目录树 / 文件职责表 / 命名规范 | 全项目 |
| **三** | [LangGraph 状态机](#三langgraph-状态机详解) | State 定义 / Node 函数签名 / 条件边 / Trace 中间件 | `graph/state.py`, `graph/nodes.py`, `graph/edges.py`, `graph/builder.py` |
| **四** | [各 Agent 实现](#四各-agent-实现) | Intent/Planner/Executor/Brainstorm 4 Agent / LLM 客户端 | `agents/*.py`, `agents/brainstorm/*.py`, `agents/llm_client.py` |
| **五** | [Mock API 规范](#五mock-api-规范) | 差异化成功率 / Fallback / 迁移真实 API 策略 | `tools/mock_api.py` |
| **六** | [异常处理实现](#六异常处理实现) | Q1-Q8 对齐 / 重试策略 / 安全否决重试 | `agents/retry_manager.py`, `graph/nodes.py` |
| **七** | [可观测性 (trace)](#七可观测性trace) | Trace ID 全链路 / structlog 配置 / 日志示例 | `middleware/trace.py`, `config.py` |
| **八** | [测试策略](#八测试策略) | 单元测试 / 集成测试 / E2E Demo 场景 | `tests/*.py` |
| **九** | [Hackathon Demo 指南](#九hackathon-demo-指南) | Demo 场景设计 / 演示稿 / Q&A 准备 | - |
| **十** | [已知限制 & V1 规划](#十已知限制--v1-规划) | MVP 限制清单 / V1.0~V1.2 演进路线 / 技术债务 | - |
| **附录** | [附录](#附录) | 环境变量列表 / 文件路径速查 / 常见问题排查 | - |

---

## 🔍 按任务查章节

### 我想...

| 任务 | 去章节 |
|------|--------|
| 搭环境 / 启动项目 | [一、快速启动](#一快速启动) |
| 了解文件结构 | [二、项目结构](#二项目结构) |
| 理解状态机怎么跑 | [三、LangGraph 状态机](#三langgraph-状态机详解) |
| 看每个 Agent 怎么写 | [四、各 Agent 实现](#四各-agent-实现) |
| 调 Mock API 成功率 | [五、Mock API 规范](#五mock-api-规范) |
| 处理重试 / 安全否决 | [六、异常处理实现](#六异常处理实现) |
| 接入 Trace / 看日志 | [七、可观测性](#七可观测性trace) |
| 写测试 / 跑 pytest | [八、测试策略](#八测试策略) |
| 准备 Hackathon 演示 | [九、Demo 指南](#九hackathon-demo-指南) |
| 看 V1 规划 | [十、已知限制 & V1 规划](#十已知限制--v1-规划) |
| 查环境变量含义 | [附录 A](#附录) |

---

## 📂 关键文件路径速查

| 功能 | 路径 |
|------|------|
| 状态定义 | `backend/graph/state.py` |
| Node 函数 | `backend/graph/nodes.py` |
| 条件边路由 | `backend/graph/edges.py` |
| 状态机构建 | `backend/graph/builder.py` |
| LLM 客户端 | `backend/agents/llm_client.py` |
| Intent Agent | `backend/agents/intent_agent.py` |
| Planner Agent | `backend/agents/planner_agent.py` |
| Executor Agent | `backend/agents/executor_agent.py` |
| 头脑风暴引擎 | `backend/agents/brainstorm/brainstorm_engine.py` |
| Mock API | `backend/tools/mock_api.py` |
| Trace 中间件 | `backend/middleware/trace.py` |
| Prompt 模板 | `backend/prompts/*.txt` |

---

## ⚡ 常用命令

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

> 当前仓库没有 Makefile。不要用 `make start`，也不要把 `cd backend && ...` 合成一条启动命令；先激活 `py312`，再进入对应目录启动服务。

---

> 详细内容请直接查阅 `DEV_GUIDE_MVP.md` 对应章节。
