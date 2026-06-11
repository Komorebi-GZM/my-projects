# 中国象棋AI对弈工具 - 项目目录结构

本文记录仓库的规范目录。运行时生成物、缓存、日志、数据库和本地密钥不进入版本控制。

## 目录总览

```text
chess_ai/
├── assets/                 # 静态资源：字体、图标、棋盘高亮、音效
├── config/                 # 配置模板与默认配置
├── docs/                   # 项目文档中心
├── scripts/                # 本地辅助脚本
├── src/chess_ai/           # 应用源码包
├── tests/                  # 单元测试、集成测试、测试夹具
├── AGENTS.md               # 智能体协作与代码规则
├── CONTEXT.md              # 领域上下文与核心术语
├── main.py                 # Pygame 应用入口
├── pyproject.toml          # Python 工具链配置
└── requirements.txt        # 运行依赖
```

## 版本控制内目录

### assets/

| 目录 | 用途 |
|------|------|
| `assets/fonts/` | 中文字体 |
| `assets/icons/` | 工具栏 SVG 图标 |
| `assets/images/` | 棋盘高亮等图片资源 |
| `assets/sounds/` | 走子、吃子、将军、胜负音效 |

### config/

| 文件 | 用途 |
|------|------|
| `config/config.yaml` | 默认应用配置 |
| `config/logging.yaml` | 日志配置 |
| `config/.env.example` | 环境变量模板 |

本地密钥写入 `config/.env` 或 `.env`，不进入版本控制。

### docs/

| 目录 | 用途 |
|------|------|
| `docs/agents/` | 智能体协作约定 |
| `docs/adr/` | 架构决策记录 |
| `docs/design/` | 架构设计与 Prompt 调优记录 |
| `docs/guides/` | 用户、部署、贡献指南 |
| `docs/planning/` | PRD、变更记录、任务跟踪 |
| `docs/references/` | 外部规则、协议、框架资料 |
| `docs/releases/` | 版本发布总结 |

文档入口见 [docs/README.md](docs/README.md)。

### src/chess_ai/

| 模块 | 职责 |
|------|------|
| `board/` | 棋盘状态、棋子类型、棋盘异常 |
| `move/` | 走子值对象、中文走法解析 |
| `rules/` | 走法验证、FEN 序列化、胜负判定 |
| `gui/` | Pygame 渲染、交互控制、主题、对局记录 |
| `agent/` | LangGraph Agent 状态机与 GUI 侧编排门面 |
| `llm/` | LLM 客户端、Prompt、解析器、模型配置 |
| `infra/` | 配置、日志、数据库、难度映射 |

层边界遵循 `AGENTS.md`：GUI 只通过 Agent 门面协作，Agent 只通过 LLM 客户端协作。

### tests/

| 目录 | 用途 |
|------|------|
| `tests/unit/` | 模块级单元测试 |
| `tests/integration/` | Agent、LLM、GUI 工作流集成测试 |
| `tests/fixtures/` | 棋局和场景夹具 |

## 本地生成目录

以下内容可随时重新生成，保持忽略：

| 路径 | 来源 |
|------|------|
| `data/` | SQLite 数据库 |
| `logs/` | 应用日志 |
| `saves/` | 本地对局存档 |
| `src/*.egg-info/` | Python 打包元数据 |
| `.codegraph/` | 代码图谱分析缓存 |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `__pycache__/` | 工具缓存 |

## 文件命名规范

| 类型 | 规范 |
|------|------|
| Python 模块 | `snake_case.py` |
| 测试文件 | `test_<module_or_flow>.py` |
| 文档文件 | 小写英文或既有中文标题，单词用 `_` 连接 |
| 发布总结 | `docs/releases/v<version>_summary.md` |
| ADR | `docs/adr/NNNN-short-title.md` |

## 最近整理

| 日期 | 内容 |
|------|------|
| 2026-05-27 | 对齐真实目录结构；清理本地生成目录；明确运行态目录不入库 |
