# My Projects

> Komorebi-GZM 的个人项目作品集，涵盖 AI Agent、Hackathon 参赛作品、信号处理、Web 应用与设计原型等方向。

---

## 目录结构

```
my-projects/
├── ai-agents/          # AI Agent 系统
│   ├── foglift-po-wu/  # 🏆 FogLift·破雾 — 智联招聘 AI 大赛作品
│   ├── chess-ai/       # 中国象棋 AI 对弈工具
│   └── maitian-agent/  # 麦田智囊 — 乡村教育 Agent 系统
├── hackathon/          # Hackathon 参赛项目
│   └── meituan-local-activity-agent/  # 🏆 本地生活短时活动规划 Agent（美团 Hackathon）
├── signal-processing/  # 信号处理
│   └── fft-spectrum-analyzer/  # 基于 Cooley-Tukey FFT 的实时频谱分析仪
├── web-apps/           # Web 应用
│   └── campus-storage/ # 校园物品暂存小程序
└── design-concepts/    # 设计原型与 UI 概念稿
```

---

## 项目速览

### AI Agents

| 项目 | 简介 | 技术栈 |
|------|------|--------|
| [FogLift·破雾](./ai-agents/foglift-po-wu/) | 面向求职信息差的 Multi-Agent Web App，支持 JD 翻译、路径规划、面试模拟 | Python · FastAPI · LangGraph · Streamlit |
| [中国象棋 AI](./ai-agents/chess-ai/) | 桌面端人机象棋，LLM Agent 驱动走子决策，支持多模型 | Python · LangGraph · Pygame |
| [麦田智囊](./ai-agents/maitian-agent/) | 乡村教育 Agent，自进化 RAG，辅助乡村教师备课、传承经验 | Python · LangChain · RAG |

### Hackathon

| 项目 | 简介 | 技术栈 |
|------|------|--------|
| [本地生活活动规划 Agent](./hackathon/meituan-local-activity-agent/) | 短时活动方案 AI 生成 Agent，美团 Hackathon 参赛作品 | Python · FastAPI · Streamlit · Docker |

### 信号处理

| 项目 | 简介 | 技术栈 |
|------|------|--------|
| [FFT 频谱分析仪](./signal-processing/fft-spectrum-analyzer/) | 纯 Python 实现 Cooley-Tukey FFT，含 PyQt5 实时 GUI，课程设计 | Python · PyQt5 · NumPy · sounddevice |

### Web 应用

| 项目 | 简介 | 技术栈 |
|------|------|--------|
| [校园物品暂存](./web-apps/campus-storage/) | 校园寄存服务小程序，Python 后端 + 微信小程序前端 + CloudBase 部署 | Python · Flask · 微信小程序 · CloudBase |

### 设计概念

| 项目 | 简介 |
|------|------|
| [设计原型](./design-concepts/) | Lusion 风格设计文档、Rival Protocol 战斗界面 HTML 原型 |

---

## 关于作者

山东大学在读，专注 AI Agent 开发与多 Agent 系统工程。

- 主要方向：LLM Application · Multi-Agent Systems · Full-stack
- 开发环境：macOS ARM64 · Python 3.12 · FastAPI · LangGraph
