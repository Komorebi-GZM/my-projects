# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root — contains domain model, architecture overview, core data flow, key interfaces, tech stack, architecture principles, known issues, and terminology.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in. Current ADRs:
  - 0001: Four-layer agent architecture (English, brief)
  - ADR-001: 四层Agent架构设计 (Chinese, detailed)
  - 0002: Agent interface unification and dependency injection
  - 0003: Dependency injection and module boundary strategy
- **`docs/agents/`** — per-agent documentation with responsibilities, interfaces, prompts, dependencies, and known limitations.

If any of these files don't exist, proceed silently. Don't flag their absence; don't suggest creating them upfront.

## File structure

Single-context repo:

```
/
├── CONTEXT.md              # 领域上下文（主要领域文档）
├── CLAUDE.md               # Agent skills 配置 + 项目概览
├── docs/
│   ├── adr/                # 架构决策记录
│   │   ├── 0001-four-layer-agent-architecture.md
│   │   ├── 0002-agent-interface-unification.md
│   │   ├── 0003-dependency-injection-pattern.md
│   │   └── 0001-four-layer-agent-architecture.md
│   ├── agents/             # 单 Agent 文档
│   │   ├── quick-lesson-prep.md
│   │   ├── wisdom-transfer.md
│   │   ├── classroom-companion.md
│   │   ├── material.md
│   │   ├── meeting-notes.md
│   │   ├── issue-tracker.md
│   │   ├── triage-labels.md
│   │   └── domain.md       # 本文件
│   ├── issues.md           # 完整 Issue 列表（22 个，3 个阶段）
│   ├── label-design.md     # GitHub 标签体系
│   ├── triage-report.md    # 分诊报告
│   └── architecture-deepening.md
├── maitian_agent/          # 主项目包
│   ├── agents/             # Agent 层
│   ├── api/                # FastAPI REST API
│   ├── config/             # pydantic-settings 配置
│   ├── memory/             # 记忆层
│   ├── rag/                # RAG 知识库
│   ├── tools/              # 工具层 (OCR/ASR/File)
│   └── frontend/           # Streamlit 前端
├── demo/                   # Demo 应用（独立模块）
├── tests/                  # pytest 测试
└── docker/                 # Docker 部署配置
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`'s "术语说明" section. Key terms:

- **Agent** = 继承 BaseAgent 的具体 Agent 类，提供标准 `run(Dict) -> Dict` 接口和公开方法
- **Tools/工具层** = BaseOCR、BaseASR 等工具抽象层 + 工厂方法，由 AgentFactory 注入 Agent
- **RAG** = KnowledgeBase 三层架构（universal/school/teacher），通过 `add_document()`/`search()` 接口暴露
- **记忆层** = ConversationMemory（短期对话）+ TeacherProfileManager（长期画像）
- **配置层** = pydantic-settings Settings，入口处加载，通过 BaseAgent 下发

Don't drift to synonyms the glossary explicitly avoids.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _与 ADR-0002（Agent 接口统一）矛盾 — 但值得重新审视，因为……_
