# My Projects

> Komorebi-GZM 的个人项目作品集，涵盖 AI Agent、数据分析、信号处理、Web 应用与设计原型等方向。

---

## 目录结构

```
my-projects/
├── ai-agents/                        # AI Agent 系统
│   ├── foglift-po-wu/                # 🏆 FogLift·破雾 — 智联招聘 AI 大赛作品
│   ├── chess-ai/                     # 中国象棋 AI 对弈工具
│   ├── maitian-agent/                # 麦田智囊 — 乡村教育 Agent 系统
│   └── meituan-local-activity-agent/ # 🏆 本地生活短时活动规划 Agent（美团 Hackathon）
├── data-analysis/                    # 数据分析项目
│   ├── morocco-load-analysis/        # 摩洛哥电力负荷分析
│   ├── ev-market-analysis/           # 全球电动汽车市场分析
│   ├── ab-test-analysis/             # A/B 测试数据分析
│   ├── financial-news-sentiment/     # 财经新闻情感分析与股市预测
│   ├── online-gaming-analysis/       # 在线小游戏平台数据分析
│   ├── gallstone-prediction/         # 胆结石临床预测建模
│   ├── plc-genesis-anomaly/          # PLC 零件分拣系统异常检测
│   ├── product-sales-analysis/       # 产品销量与价格弹性分析
│   └── 51job-recruitment-analysis/   # 前程无忧招聘数据分析
├── signal-processing/                # 信号处理
│   └── fft-spectrum-analyzer/        # 基于 Cooley-Tukey FFT 的实时频谱分析仪
├── web-apps/                         # Web 应用
│   └── campus-storage/               # 校园物品暂存小程序
└── design-concepts/                  # 设计原型与 UI 概念稿
```

---

## 项目速览

### AI Agents

| 项目 | 简介 | 技术栈 |
|------|------|--------|
| [FogLift·破雾](./ai-agents/foglift-po-wu/) | 面向求职信息差的 Multi-Agent Web App，支持 JD 翻译、路径规划、面试模拟 | Python · FastAPI · LangGraph · Streamlit |
| [中国象棋 AI](./ai-agents/chess-ai/) | 桌面端人机象棋，LLM Agent 驱动走子决策，支持多模型 | Python · LangGraph · Pygame |
| [麦田智囊](./ai-agents/maitian-agent/) | 乡村教育 Agent，自进化 RAG，辅助乡村教师备课、传承经验 | Python · LangChain · RAG |
| [本地生活活动规划 Agent](./ai-agents/meituan-local-activity-agent/) | 短时活动方案 AI 生成 Agent，美团 Hackathon 参赛作品 | Python · FastAPI · Streamlit · Docker |

### 数据分析

| 项目 | 简介 | 技术栈 |
|------|------|--------|
| [摩洛哥电力负荷分析](./data-analysis/morocco-load-analysis/) | 电力负荷预测与配电网优化，多模型对比（ARIMA/LSTM/XGBoost） | Python · XGBoost · Prophet · PyTorch · PuLP |
| [电动汽车市场分析](./data-analysis/ev-market-analysis/) | 全球 EV 市场全维度分析，聚类建模与竞品对标 | Python · scikit-learn · matplotlib |
| [A/B 测试分析](./data-analysis/ab-test-analysis/) | 互联网产品 A/B 测试统计推断，假设检验与决策建议 | Python · scipy · statsmodels |
| [财经新闻情感分析](./data-analysis/financial-news-sentiment/) | 14 万条财经新闻 NLP 情感分析，BERTopic 主题建模 + Streamlit 看板 | Python · transformers · BERTopic · Streamlit |
| [在线游戏分析](./data-analysis/online-gaming-analysis/) | 游戏平台热度分析、标签挖掘与跨平台差异检验 | Python · pandas · seaborn |
| [胆结石预测建模](./data-analysis/gallstone-prediction/) | UCI 临床数据 ML 建模，SHAP 可解释性 + ROC 评估 | Python · scikit-learn · SHAP |
| [PLC 异常检测](./data-analysis/plc-genesis-anomaly/) | 工业 PLC 分拣系统传感器数据分析与异常工况检测 | Python · scipy · matplotlib |
| [产品销量分析](./data-analysis/product-sales-analysis/) | 零售销量预测与价格弹性回归分析 | Python · statsmodels |
| [前程无忧招聘分析](./data-analysis/51job-recruitment-analysis/) | 招聘平台薪资分布、供需热力图多维可视化 | Python · jieba · wordcloud |

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
