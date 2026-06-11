# AI Agents

本目录收录四个独立的 AI Agent 项目，涵盖求职、教育、博弈、本地生活四个垂直场景。

---

## 项目列表

| 目录 | 项目名 | 场景 | 状态 |
|------|--------|------|------|
| [foglift-po-wu/](./foglift-po-wu/) | FogLift·破雾 | 求职信息差 | 已完成，智联 AI 大赛提交版 |
| [chess-ai/](./chess-ai/) | 中国象棋 AI | 博弈娱乐 | 已完成 |
| [maitian-agent/](./maitian-agent/) | 麦田智囊 | 乡村教育 | 已完成 |
| [meituan-local-activity-agent/](./meituan-local-activity-agent/) | 本地生活活动规划 Agent | 本地生活 | MVP 已完成，美团 Hackathon |

---

### FogLift·破雾

面向求职信息差场景的 Multi-Agent Web App，帮助求职者解析 JD、理解 HR 黑话、规划学习路径，并模拟面试。

- **后端**：FastAPI + LangGraph（10 个 Agent 节点，3 条子图流程）
- **前端**：Streamlit
- **模型**：DashScope Qwen-Plus / Zhipu GLM-4 / OpenAI 兼容

### 中国象棋 AI

桌面端人机对弈工具，LLM Agent 编排走子决策，支持 DeepSeek、GPT-4o、本地 Ollama。

- **规则引擎**：完整象棋规则（将军/应将/将死/困毙/长将/和棋）
- **GUI**：Pygame 图形棋盘，选中高亮 + 合法走位提示
- **数据**：SQLite 持久化对局记录，支持棋谱回放

### 麦田智囊

乡村教育 Agent 系统，为乡村教师提供 AI 教研搭档。核心能力：极速备课、手写教案 OCR 传承、课堂伴教、素材推荐、教研纪要生成。

- **架构**：感知层（ASR+OCR）→ 规划层（意图路由）→ 执行层（5 Agent 链）→ 记忆层（RAG）
- **RAG**：自进化知识库，支持教师专属画像

### 本地生活活动规划 Agent

给定用户所在城市与空闲时间，自动规划合适的本地生活短时活动方案，美团 Hackathon 参赛作品。

- **后端**：FastAPI + AI Agent 规划引擎
- **前端**：Streamlit
- **部署**：Docker Compose 一键启动
