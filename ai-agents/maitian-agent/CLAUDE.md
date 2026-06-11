# 麦田智囊 (Wheatfield Braintrust)

面向中国乡村教师的 AI 教研搭档系统。基于大模型多智能体技术，解决乡村教育资源匮乏、教师备课负担重、教学经验难以传承等核心问题。

## Agent skills

### Issue tracker

Issues live as GitHub issues on [Komorebi-GZM/wheatfield_braintrust](https://github.com/Komorebi-GZM/wheatfield_braintrust). Use the `gh` CLI for all operations. See `docs/agents/issue-tracker.md`.

### Triage labels

Uses the default five canonical triage roles. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo. See `docs/agents/domain.md`.

## Project overview

- **四层 Agent 架构**: 感知层 → 规划层 → 执行层 → 记忆层
- **执行层 5 个 Agent**: QuickLessonPrep, WisdomTransfer, ClassroomCompanion, Material, MeetingNotes
- **规划层 1 个 Agent**: Router（意图路由 + 二次校验）
- **技术栈**: Python 3.11+, LangChain 0.2.x, DeepSeek-V2, ChromaDB + BGE-Large-zh, FastAPI, Streamlit
- 详见 `CONTEXT.md`

## Development conventions

- **测试**: pytest，外部 API 一律 mock，Chroma 使用临时目录
- **配置**: pydantic-settings `Settings`（当前 Agent 未集成，待修复）
- **Agent 接口**: `run(Dict[str, Any]) -> Dict[str, Any]` 统一签名
- **依赖注入**: 构造函数注入，禁止内部实例化跨层依赖
- **层间依赖规则**: 执行层可依赖工具/RAG/记忆/配置层；工具/RAG/记忆层不可依赖执行层；配置层不可依赖任何业务层
