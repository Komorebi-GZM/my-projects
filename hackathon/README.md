# Hackathon 参赛项目

本目录收录 Hackathon 参赛作品。

---

## 项目列表

| 目录 | 赛事 | 项目名 | 状态 |
|------|------|--------|------|
| [meituan-local-activity-agent/](./meituan-local-activity-agent/) | 美团 Hackathon | 本地生活短时活动规划 Agent | MVP 已完成 |

---

### 本地生活短时活动规划 Agent

给定用户所在城市与空闲时间，自动规划合适的本地生活短时活动方案，对接美团 POI 数据。

**核心功能**
- AI Agent 自动生成活动方案（含餐饮/娱乐/景点推荐）
- Docker 一键部署，前后端分离
- 支持任意 OpenAI 兼容模型接入

**技术栈**
- Backend：Python · FastAPI
- Frontend：Streamlit
- 部署：Docker Compose
- LLM：OpenAI Compatible API

**快速启动**

```bash
cp backend/.env.example backend/.env
# 编辑 .env 填入 API Key
docker-compose up --build
```

详见 [USAGE.md](./meituan-local-activity-agent/USAGE.md)。
