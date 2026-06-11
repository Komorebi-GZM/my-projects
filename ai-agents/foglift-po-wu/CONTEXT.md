# FogLift·破雾 Context

FogLift·破雾是一个求职辅助 Multi-Agent Web App，面向农村/普通本科学生、跨专业求职者和缺少求职信息渠道的用户。产品目标是降低求职信息不对称：让用户读懂 JD、知道怎么补技能、能在面试前练习一次。

## Domain Language

**JD解析师 (JD Analyst)**  
JD 翻译器子图的第一个 Agent。输入原始 JD 文本，输出结构化 JD 字段：硬技能、软技能、经验要求、学历要求、HR 黑话。

**黑话翻译官 (Jargon Translator)**  
JD 翻译器子图的第二个 Agent。输入 JD 解析结果中的 `HR黑话` 字段，根据 `jargon_map.json` 输出黑话到真实含义的映射。

**差距分析师 (Gap Analyst)**  
JD 翻译器子图的第三个 Agent。对比结构化 JD 和用户背景，输出核心差距与补齐时间。未提供用户背景时使用 `user_profile_default.json`。

**岗位拆解师 (Position Resolver)**  
阶梯路径子图的第一个 Agent。输入目标岗位，输出 3-5 个硬技能能力维度。

**阶梯规划师 (Ladder Planner)**  
阶梯路径子图的第二个 Agent。基于目标岗位和能力维度输出四步职业路径：校园项目、实习 title、实习积累关键词、秋招目标岗位。

**技能推荐官 (Skill Recommender)**  
阶梯路径子图的第三个 Agent。根据能力维度推荐 3-6 个技能，并给出高/中/低优先级。

**资源检索员 (Resource Retriever)**  
阶梯路径子图的第四个节点。它不调用 LLM；根据技能名从 `skill_resource_map.json` 确定性读取学习资源。未知技能返回空资源数组。

**面试官Agent (Interviewer)**  
面试子图的第一个 Agent。输入目标岗位，生成或抽取一道面试题，并把 `target_position`、`question`、`key_points` 写入 session。

**答案分析师 (Answer Analyst)**  
面试子图的第二个 Agent。根据题目、回答和 key points 输出内容分、逻辑分、匹配分、总分。

**鼓励师Agent (Cheerleader)**  
面试子图的第三个 Agent。根据评分输出敢投指数、鼓励语、亮点和建议。

**汇总节点 (Coordinator)**  
每个子图末尾的纯函数合并节点，不调用 LLM，不参与讨论，只把前置节点输出整理成 API result。

**invoke_llm() 统一接口**  
所有 LLM Agent 必须通过 `utils/llm_client.py` 中的 `invoke_llm()` 调用模型。该 seam 负责根据 `LLM_PROVIDER` 选择 DashScope、Zhipu 或 OpenAI 兼容模型，并解析 JSON 输出。

## Current Architecture

- 后端：FastAPI，入口文件 `main.py`。
- 前端：Streamlit，入口文件 `app_streamlit.py`。
- 编排：`utils/graph_builder.py` 使用 LangGraph 构建主图和子图。
- 路由：`utils/supervisor.py` 根据 `intent` 路由到 JD、路径或面试子图。
- 知识库：`knowledge_base/*.json`，由 `utils/knowledge_loader.py` 启动时加载到内存。
- 会话：面试 session 使用 `utils/session_store.py` 的内存存储，重启后失效。

## Implemented User Flows

**子图1: JD翻译器**  
`JD解析师 -> 黑话翻译官 -> 差距分析师 -> 汇总节点`

**子图2: 阶梯路径 + 技能学习**  
`岗位拆解师 -> 阶梯规划师 -> 技能推荐官 -> 资源检索员 -> 汇总节点`

**子图3: 面试模拟**  
`interview_question` 只获取题目并返回 session；`interview_answer` 恢复上下文后执行答案分析和鼓励反馈。

## Current Knowledge Handling

当前实现是静态知识库注入与确定性读取：

- LLM Agent 在 Prompt 中引用知识库片段。
- 资源检索员从 `skill_resource_map.json` 直接读资源 URL。
- 面试题通过知识库 getter 或 Agent 逻辑获取。

独立 RAG 层尚未实现。下一阶段目标见 `docs/architecture/rag-hybrid-retrieval.md`。

## Known Baseline

- 本地 Python：`/Users/komorebi/miniforge3/envs/py312/bin/python`。
- 当前单元测试：`17 passed, 1 failed`。
- 已知失败：`tests/test_resource_retriever.py` 仍断言 SQL 资源数为 2；实际知识库中 SQL 资源为 3 条。

## Guardrails

- 不改变 `POST /agent_invoke` 请求/响应 JSON 形状。
- 不改变 `invoke_llm()` seam。
- `KnowledgeLoader` 只做 JSON 原始加载。
- 新增 RAG 时不引入 Chroma、FAISS、embedding 依赖。
- 资源 URL、课程名、面试题等事实字段必须来自知识库，不由 LLM 自由生成。
