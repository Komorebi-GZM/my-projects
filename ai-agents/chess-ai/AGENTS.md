# AGENTS.md - 中国象棋AI对弈工具

## Project State

**v0.1.2 - AI难度系统实现。** 添加 Easy/Medium/Hard 三档难度，通过 LLM temperature 控制，GUI 选择 + YAML 持久化。运行命令：`python main.py`。

### 实现概况
- **board / move / rules**：完整棋盘引擎，7种棋子走法验证，FEN序列化，胜负判定
- **gui**：Pygame棋盘渲染，中文字体支持（NotoSansSC），8个SVG图标，7个WAV音效
- **agent**：LangGraph状态机AI Agent，支持走子生成、检查点恢复、人机交互
- **llm**：多模型客户端（OpenAI兼容/DeepSeek/Ollama），Prompt模板，输出解析器
- **infra**：YAML+环境变量双层配置，dotenv自动加载，SQLite数据库（对局/走子/检查点）

### 测试覆盖
- **已有单元测试**：board(24)、move(18)、rules(48)、fen(15)、termination(10) = 114个单元测试
- **待补充测试**：gui、agent、llm、infra 模块

### 当前LLM配置
- 接口类型：OpenAI兼容接口（内部平台）
- 模型：`SDU-AI/DeepSeek-V4-Flash`

### 已知待办
- 集成测试（agent工作流、AI联动）
- gui/agent/llm/infra 单元测试补充

## Tech Stack (Locked)

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.12 | Required for match syntax, enhanced type hints |
| LangChain | 1.2+ | Use `langchain-openai`, `langchain-community` |
| LangGraph | 0.3+ | Agent state machine, checkpointer |
| Pygame | 2.6 | GUI framework |
| Pydantic | 2.x | Data validation |
| SQLite | 3 | Built-in, no extra dependency |

## Architecture (5 Layers)

```
GUI (Pygame) → Rule Engine → LangGraph Agent → LLM Client → Infrastructure
```

Key modules (planned):
- `src/board/` - Chess rules, move validation, FEN serialization (✅ implemented)
- `src/gui/` - Pygame rendering, coordinate mapping (✅ implemented)
- `src/agent/` - LangGraph state machine, retry logic (✅ implemented)
- `src/llm/` - Multi-model client (DeepSeek/GPT/Ollama) (✅ implemented)
- `src/infra/` - Config, logging, SQLite, checkpoint (✅ implemented)

**Strict rule:** Upper layers must NOT directly call lower layers. GUI ↔ Agent only.

## Code Conventions

- **Formatting:** Ruff (formatter + linter), max line length 120
- **Type hints:** Mandatory on all functions/params/returns (no `Any` unless justified)
- **Naming:** `PascalCase` classes, `snake_case` functions/vars, `UPPER_SNAKE_CASE` constants
- **Docstrings:** Google style, Chinese description with English param names
- **Import sorting:** Ruff isort-style, `known-first-party = ["chess_ai"]`

## Rules (Strict)

- **No lazy imports.** All imports must be at module top-level. Never import inside functions.
- **ClassVar for mutable class attributes.** Any `dict`/`list` class attribute must be annotated with `typing.ClassVar` to avoid shared mutable default.
- **FEN row order.** `row=0` = black back rank, `row=9` = red back rank. `to_fen()` iterates `range(10)` (0→9), FEN string order is row 0 → row 9.
- **Chinese fullwidth punctuation allowed.** RUF001/002/003 are ignored — Chinese docstrings/comments may use `，。！（）：` etc.
- **Layer isolation.** Upper layers must NOT directly call lower layers. GUI ↔ Agent only. Agent ↔ LLM Client only. No skip-layer calls.
- **No `Any` without justification.** If `Any` is used, add a `# reason:` inline comment.
- **ConfigManager masks secrets.** Never log API keys. `ConfigManager` auto-masks values containing `key`/`secret`/`token` in logs.

## Running Tests

```bash
pytest tests/              # all tests
pytest tests/unit/         # unit tests only
pytest tests/integration/  # integration tests
pytest --cov=src           # with coverage
```

Required: ≥85% line coverage, ≥75% branch coverage.

## Pre-commit Hooks

Install via: `pre-commit install`

Runs: Ruff format → Ruff check → mypy → pytest (unit only)

## Config & Environment

| Env Variable | Purpose |
|--------------|---------|
| `CHESS_LLM_API_KEY` | **Required** - LLM API key |
| `CHESS_LLM_MODEL` | Model name (default: `deepseek-chat`) |
| `CHESS_LLM_BASE_URL` | API endpoint |
| `CHESS_LOG_LEVEL` | Logging level (default: `INFO`) |

Config priority: env vars > `config.yaml` > defaults.

**Never log API keys.** ConfigManager masks them (`****1234`).

## Key Design Documents

- [ARCHITECTURE.md](docs/design/ARCHITECTURE.md) - Full technical design
- [CONTRIBUTING.md](docs/guides/CONTRIBUTING.md) - Full coding standards

## Agent skills

### Issue tracker

Local markdown issue tracker. Issues live as files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical roles: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: one `CONTEXT.md` at repo root + `docs/adr/` for past decisions. See `docs/agents/domain.md`.