# FogLift·破雾

FogLift·破雾是一个面向求职信息差场景的 Multi-Agent Web App。它帮助求职者解析 JD、理解 HR 黑话、规划岗位学习路径，并进行基础面试模拟。

当前形态是本地 MVP：FastAPI 后端、Streamlit 前端、LangGraph 编排、JSON 文件知识库、三类 LLM Provider 统一调用接口。

## 当前状态

- 主体功能：已实现 3 条子图流程，共 10 个 Agent/节点角色。
- 后端入口：`POST /agent_invoke`。
- 健康检查：`GET /health`、`GET /api/health`。
- 知识库：当前由 `utils/knowledge_loader.py` 加载 JSON，并在 Agent Prompt 中静态注入或由确定性逻辑读取。
- RAG：独立检索层仍是下一阶段工作，设计见 `docs/architecture/rag-hybrid-retrieval.md`。
- 测试基线：当前 `tests/` 为 `17 passed, 1 failed`，失败原因是 `tests/test_resource_retriever.py` 对 SQL 资源数量的旧断言未同步知识库现状。

## 功能

### JD 翻译器

- `JD解析师`：从原始 JD 中提取硬技能、软技能、经验要求、学历要求和 HR 黑话。
- `黑话翻译官`：根据黑话映射表解释 JD 中的招聘术语。
- `差距分析师`：对比 JD 要求和用户背景，输出核心差距与补齐时间估算。

### 阶梯路径 + 技能学习

- `岗位拆解师`：将目标岗位拆成 3-5 个硬技能维度。
- `阶梯规划师`：生成从校园项目到秋招目标岗位的四步路径。
- `技能推荐官`：按优先级推荐技能。
- `资源检索员`：根据技能名从知识库确定性返回学习资源。

### 面试模拟

- `面试官Agent`：根据目标岗位生成或抽取面试题，并写入会话上下文。
- `答案分析师`：按内容、逻辑、岗位匹配三个维度评分。
- `鼓励师Agent`：根据评分生成敢投指数、亮点和建议。

## 技术栈

- Python 3.12
- FastAPI
- LangGraph
- LangChain 相关 Provider 封装
- Streamlit
- JSON 文件知识库
- DashScope Qwen-Plus / Zhipu GLM-4 / OpenAI 兼容模型

## 快速开始

本机已验证的解释器路径：

```bash
/Users/komorebi/miniforge3/envs/py312/bin/python
```

安装依赖：

```bash
pip install -r requirements.txt
```

配置环境变量：

```bash
cp .env.example .env
```

`.env` 示例：

```bash
LLM_PROVIDER=dashscope
DASHSCOPE_API_KEY=sk-xxx
DASHSCOPE_MODEL=qwen-plus
```

运行后端：

```bash
uvicorn main:app --reload
```

运行前端：

```bash
streamlit run app_streamlit.py
```

运行测试：

```bash
/Users/komorebi/miniforge3/envs/py312/bin/python -m pytest tests/
```

端到端测试需要真实 LLM API Key：

```bash
/Users/komorebi/miniforge3/envs/py312/bin/python test_e2e.py
```

## API

### `POST /agent_invoke`

请求：

```json
{
  "intent": "jd_translate",
  "payload": {
    "jd_text": "..."
  }
}
```

响应：

```json
{
  "success": true,
  "result": {}
}
```

支持的 `intent`：

| intent | 用途 | 关键 payload |
|---|---|---|
| `jd_translate` | JD 翻译器 | `jd_text` |
| `path_skill` | 阶梯路径 + 技能学习 | `target_position` |
| `interview_question` | 获取面试题 | `target_position` |
| `interview_answer` | 提交面试回答 | `session_id`、`answer`、可选 `question`、`key_points` |

## 项目结构

```text
.
├── agents/                  # Agent 模块
│   ├── jd_translator/       # JD 翻译器
│   ├── path_skill/          # 阶梯路径 + 技能学习
│   └── interview/           # 面试模拟
├── utils/                   # 工具层
│   ├── graph_builder.py     # LangGraph 图构建
│   ├── knowledge_loader.py  # JSON 知识库加载
│   ├── llm_client.py        # invoke_llm() 统一 LLM seam
│   ├── session_store.py     # 面试会话存储
│   └── supervisor.py        # intent 路由
├── knowledge_base/          # JSON 知识库
├── docs/                    # 项目文档
├── tests/                   # 单元测试
├── main.py                  # FastAPI 入口
├── app_streamlit.py         # Streamlit 前端
└── test_e2e.py              # 真实 LLM 端到端测试
```

## 文档

- `docs/README.md`：文档索引。
- `docs/architecture/architecture.md`：当前架构事实。
- `docs/architecture/rag-hybrid-retrieval.md`：RAG 下一阶段设计。
- `docs/product/product-spec.md`：产品说明。
- `docs/TODO.md`：当前待办。

## 维护约定

- 不改变 `invoke_llm()` seam，所有 LLM Agent 通过它调用模型。
- 不改变 `POST /agent_invoke` 的 JSON API 形状。
- `KnowledgeLoader` 只负责加载原始 JSON；检索和排序逻辑应放到独立 RAG 层。
- 资源 URL、面试题等事实字段必须从知识库确定性读取，不由 LLM 编造。
