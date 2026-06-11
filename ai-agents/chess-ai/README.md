# 中国象棋AI对弈工具

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Pygame](https://img.shields.io/badge/Pygame-2.6+-orange.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> 基于 Python 3.12 + LangGraph + Pygame 的桌面端中国象棋人机对弈工具，支持多 LLM 模型（DeepSeek、GPT-4o、本地 Ollama）智能走子。

---

## 功能特性

- 完整的象棋规则引擎（将军/应将/将死/困毙/长将/和棋判定）
- 基于 Pygame 的图形化棋盘界面，支持棋子选中高亮、合法走位提示
- LangGraph Agent 编排 LLM 走子决策，支持非法走子自动重试与降级
- 多模型可插拔架构，支持 DeepSeek、GPT-4o、本地 Ollama 一键切换
- SQLite 持久化存储对局记录，支持棋谱回放与复盘
- 悔棋、重置、音效开关等完整游戏控制功能

---

## 快速开始

### 环境要求

- Python 3.12+
- 支持的操作系统：Windows / macOS / Linux

### 安装步骤

```bash
# 1. 克隆仓库
git clone <repository-url>
cd chess_ai

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp config/.env.example config/.env
# 编辑 config/.env，填入你的 LLM API Key

# 5. 启动游戏
python main.py
```

### 配置 LLM 模型

编辑 `config/config.yaml` 切换模型：

```yaml
model:
  name: deepseek-chat  # 可选: gpt-4o, qwen2.5, llama3.2 等
  temperature: 0.3
  timeout: 15
```

或使用本地 Ollama（无需联网）：

```yaml
model:
  name: qwen2.5
  provider: ollama
  base_url: http://localhost:11434
```

---

## 项目结构

```
chess_ai/
├── assets/                 # 静态资源文件
│   ├── fonts/             # 字体文件
│   ├── icons/             # UI 图标
│   ├── images/            # 图片资源
│   │   └── pieces/        # 棋子图片（14张）
│   └── sounds/            # 音效文件
├── config/                # 配置文件
│   ├── config.yaml        # 主配置文件
│   ├── .env.example       # 环境变量模板
│   └── logging.yaml       # 日志配置
├── docs/                  # 文档目录
│   ├── detailed_design/   # 详细设计文档
│   ├── references/        # 参考资料
│   └── *.md              # 项目级文档
├── src/                   # 源代码（待实现）
│   ├── board/            # 棋盘规则引擎模块
│   ├── gui/              # GUI 模块
│   ├── agent/            # LangGraph Agent 模块
│   ├── llm/              # LLM 接入模块
│   └── infra/            # 基础设施模块
├── tests/                 # 测试代码（待实现）
│   ├── unit/             # 单元测试
│   ├── integration/      # 集成测试
│   └── fixtures/         # 测试数据
├── scripts/               # 工具脚本
│   ├── setup.sh          # 环境初始化
│   └── run_tests.sh      # 运行测试
├── main.py                # 程序入口
├── requirements.txt       # Python 依赖
├── PROJECT_STRUCTURE.md   # 目录结构说明
└── README.md              # 本文件
```

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | 主开发语言 |
| LangGraph | 1.0+ | Agent 状态机编排 |
| LangChain | 1.2+ | LLM 调用框架 |
| Pygame | 2.6+ | 桌面 GUI 框架 |
| Pydantic | 2.x | 数据模型与校验 |
| SQLite | 3 | 本地持久化存储 |

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 系统架构设计 |
| [USER_GUIDE.md](docs/USER_GUIDE.md) | 用户手册 |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | 部署运维指南 |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | 贡献指南 |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | 目录结构说明 |

### 详细设计文档

| 文档 | 说明 |
|------|------|
| [01_board_engine_design.md](docs/detailed_design/01_board_engine_design.md) | 棋盘与规则引擎设计 |
| [02_gui_module_design.md](docs/detailed_design/02_gui_module_design.md) | GUI 模块设计 |
| [03_langgraph_agent_design.md](docs/detailed_design/03_langgraph_agent_design.md) | LangGraph Agent 设计 |
| [04_llm_prompt_design.md](docs/detailed_design/04_llm_prompt_design.md) | LLM 接入与 Prompt 设计 |
| [api_documentation.md](docs/detailed_design/api_documentation.md) | API 接口契约 |
| [database_schema.md](docs/detailed_design/database_schema.md) | 数据库 Schema |
| [test_plan.md](docs/detailed_design/test_plan.md) | 测试计划 |

---

## 游戏操作

| 操作 | 说明 |
|------|------|
| **点击棋子** | 选中己方棋子，显示合法走位 |
| **点击目标位置** | 执行走子 |
| **悔棋** | 撤销上一步走子（双方各退一步） |
| **重置** | 重新开始对局 |
| **设置** | 切换 LLM 模型、调整音效等 |

---

## 开发计划

- [x] 架构设计与技术选型
- [x] 详细设计文档编写
- [x] 资源文件准备（棋子、音效、图标）
- [ ] 棋盘规则引擎实现
- [ ] GUI 模块实现
- [ ] LangGraph Agent 实现
- [ ] LLM 接入模块实现
- [ ] 测试与优化

---

## 许可证

MIT License

---

## 致谢

- 棋子图片资源来自开源社区
- Pygame 提供优秀的图形渲染支持
- LangGraph 提供强大的 Agent 编排能力
