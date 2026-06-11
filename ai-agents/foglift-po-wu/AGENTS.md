# FogLift·破雾 Multi-Agent Web App

## 技术栈
- Python 3.12
- FastAPI (后端框架)
- LangGraph 1.0+ + LangChain Provider 集成 (Multi-Agent框架)
- Streamlit (前端框架)
- 阿里百炼 Qwen-Plus (默认LLM) / 智谱GLM-4 / GPT-4o-mini
- JSON文件 (知识库存储，MVP阶段)

## 核心功能
1. **JD翻译器**：JD解析师 → 黑话翻译官 → 差距分析师 (3-Agent协作)
2. **阶梯路径+技能学习**：岗位拆解师 → 阶梯规划师 → 技能推荐官 → 资源检索员 (4-Agent协作)
3. **面试模拟**：面试官Agent → 答案分析师 → 鼓励师Agent (3-Agent协作)

## 开发要求
- 每个Agent必须调用对应知识库内容作为输出依据
- 主控Agent（Supervisor）负责用户意图识别和子图路由
- 前端通过FastAPI端点与LangGraph编译图对接
- `invoke_llm()` 统一接口：所有Agent通过此seam调用LLM

## 知识库检索/RAG约定
- `KnowledgeLoader` 只负责加载 JSON 原始知识库，RAG 逻辑放在独立检索层。
- MVP 使用混合检索：结构化/关键词匹配优先，预留语义向量后端接口，不引入 Chroma/FAISS/embedding 依赖。
- 检索结果必须保留结构化证据：`id`、`domain`、`title`、`content`、`metadata`、`score`、`match_reasons`。
- Agent Prompt 应引用格式化证据块，资源 URL 仍从知识库确定性读取，不由 LLM 编造。
- 不改变 FastAPI/Streamlit JSON API 形状；不改变 `invoke_llm()` seam。

## 知识库要求（JSON格式）
- 岗位JD库：产品、测试、AI Agent、数据相关岗位JD
- 黑话映射表：HR黑话及对应真实含义
- 技能-资源映射表：技能与免费学习资源对应关系
- 面试题库：各岗位基础面试题
- 阶梯路径模板：不同岗位的基础路径框架
- 默认用户画像：基础用户背景信息

## 开发命令
```bash
# 环境准备（本地 py312）
conda activate py312
pip install -r requirements.txt

# 配置LLM（复制.env.example → .env，填入API Key）
cp .env.example .env

# 运行后端
uvicorn main:app --reload

# 运行前端
streamlit run app_streamlit.py

# 运行单元测试
pytest tests/

# 当前本机更稳的显式解释器路径
/Users/komorebi/miniforge3/envs/py312/bin/python -m pytest tests/

# 运行端到端测试（需真实LLM API Key）
python test_e2e.py
```

## LLM配置
```bash
# .env
LLM_PROVIDER=dashscope        # dashscope | openai | zhipu
DASHSCOPE_API_KEY=sk-xxx      # 阿里百炼 API Key
DASHSCOPE_MODEL=qwen-plus     # 默认模型
```

## 项目结构
```
.
├── agents/                  # Agent模块
│   ├── jd_translator/       # JD翻译器 (3 Agent)
│   ├── path_skill/          # 阶梯路径 (4 Agent)
│   └── interview/           # 面试模拟 (3 Agent)
├── utils/                   # 工具层
│   ├── knowledge_loader.py  # 知识库加载 (单例)
│   ├── llm_client.py        # LLM客户端 + invoke_llm()
│   ├── supervisor.py        # Supervisor意图路由
│   ├── graph_builder.py     # LangGraph图构建
│   └── session_store.py     # 会话存储
├── knowledge_base/          # 知识库JSON文件
├── docs/                    # 项目文档
│   ├── architecture/        # 当前架构与RAG设计
│   ├── product/             # 产品、参赛、合规说明
│   ├── deliverables/        # 参赛交付物
│   ├── reference/           # 原始参考资料
│   ├── adr/                 # 架构决策记录
│   └── TODO.md              # 当前待办
├── tests/                   # 单元测试
├── main.py                  # FastAPI入口
├── app_streamlit.py         # Streamlit前端
├── test_e2e.py              # 端到端测试
└── .env                     # 环境变量配置
```

## 注意事项
- 子图Agent采用顺序执行（无讨论轮次），避免响应缓慢
- Supervisor 只负责 intent 路由；各子图使用独立 coordinator 汇总结果
- 每个Agent的Prompt中引用知识库具体内容
- 前端与后端API统一JSON格式
