# Changelog

## Unreleased

### Documentation

- Reorganized `docs/` into architecture, product, deliverables, reference, ADR, and TODO sections.
- Rewrote README, architecture, product, RAG, competition, compliance, ADR, and context documentation to reflect the current implementation state.
- Updated the RAG document from proposed design to foundation-implemented status.
- Recorded the current unit-test baseline: `28 passed`.
- Removed intermediate planning and UI deconstruction drafts from the long-term docs tree.

### Added

- Added MVP RAG foundation modules for knowledge document types, JSON indexing, hybrid keyword retrieval, and evidence-block formatting.
- Added focused tests for the RAG foundation.

### Fixed

- Updated resource retriever tests to validate current knowledge-base resources instead of stale fixed counts.
- Migrated the deterministic resource retriever onto the new knowledge retrieval foundation while preserving its response shape.
- Migrated Path Skill LLM agents to prompt evidence blocks while preserving `invoke_llm()` usage and output contracts.
- Migrated JD Translator agents to evidence blocks for JD parsing, jargon translation, and default profile gap analysis.
- Migrated interview question selection to the knowledge retrieval foundation and made KB-backed selection deterministic.
- Verified FastAPI health routes and all four `/agent_invoke` intents with in-process smoke tests using mocked LLM responses.

## v0.0.2 (2026-05-18)

### Bug修复与体验优化

#### 关键Bug修复
- **面试模拟数据丢失**：修复切换页面后题目和评估结果消失的问题
  - 题目保存到`st.session_state.question`并持久显示
  - 评估结果保存到`st.session_state.last_evaluation`
  - 使用`st.rerun()`优化页面刷新
- **KnowledgeLoader.get()参数错误**：修复`interviewer.py`中调用`knowledge.get()`传入多余参数
- **Streamlit组件ID冲突**：为所有`text_input`、`text_area`、`radio`组件添加唯一`key`参数

#### 用户体验优化
- 面试题始终显示在页面顶部，切换模式不丢失
- 评估结果持久保留，可随时查看
- 页面分隔线区分题目和操作区域
- 获取题目和提交回答后自动刷新显示

#### 依赖补充
- 添加`langchain-openai>=0.1.0`
- 添加`pytest>=7.0.0`

## v0.0.1 (2026-05-18)

### 首次发布 — MVP 端到端可用

#### 架构
- **LangGraph 多Agent编排**：Supervisor意图路由 + 3个子图 (JD翻译器/阶梯路径/面试模拟)
- **invoke_llm() 统一接口**：10个Agent复用同一LLM调用seam，消除80行重复代码
- **纯函数汇总节点**：Coordinator无LLM调用，直接merge子Agent输出

#### 功能模块
1. **JD翻译器** (3-Agent)
   - JD解析师：提取硬技能/软技能/经验/学历/HR黑话
   - 黑话翻译官：映射HR术语到真实工作描述
   - 差距分析师：对比用户背景与JD要求，输出差距项+弥补时间

2. **阶梯路径+技能学习** (4-Agent)
   - 岗位拆解师：目标岗位→能力维度
   - 阶梯规划师：4步职业阶梯 (校园项目→实习→秋招)
   - 技能推荐官：优先级排序技能列表
   - 资源检索员：技能→免费学习资源映射

3. **面试模拟** (3-Agent)
   - 面试官：生成/抽取面试题
   - 答案分析师：三维评分 (内容40%+逻辑30%+匹配30%)
   - 鼓励师：敢投指数+鼓励语+亮点+建议

#### 知识库
- 6个JSON文件：jd_library, jargon_map, skill_resource_map, interview_questions, ladder_templates, user_profile_default

#### LLM集成
- 支持阿里百炼 (DashScope/qwen-plus) — OpenAI兼容协议
- 支持智谱GLM-4 (ChatZhipuAI)
- 支持OpenAI (gpt-4o-mini等)
- 环境变量配置：`LLM_PROVIDER=dashscope|openai|zhipu`

#### API & 前端
- FastAPI后端：`/agent_invoke` 统一入口
- Streamlit前端：`app_streamlit.py`

#### 测试
- 13个单元测试 (mock LLM)
- 7个端到端测试 (真实LLM)
- 覆盖率：全部Agent函数 + Supervisor路由 + 图构建

#### 修复
- 移除死代码 `_build_jd_subgraph` / `_build_path_skill_subgraph`
- 修复 `coordinator_jd_node` 中未使用的 `__end__` key
- 添加 `tests/conftest.py` 自动PYTHONPATH配置
- 清理所有 `__pycache__` / `.pytest_cache`
