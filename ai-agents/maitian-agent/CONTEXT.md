# 麦田智囊 — 领域上下文

## 项目定位

麦田智囊是一个面向中国乡村教师的 AI 教研搭档系统，致力于通过大模型多智能体技术，解决乡村教育资源匮乏、教师备课负担重、教学经验难以传承等核心问题。

## 领域模型

### 核心概念

| 概念 | 定义 | 关键属性 |
|------|------|---------|
| 乡村教师 (Teacher) | 系统核心用户，拥有教学风格画像 | teacher_id, grade, subject, teaching_style, lesson_count |
| 教案 (LessonPlan) | 备课产出，含教学目标/重难点/教学过程 | subject, grade, topic, rural_context, sections |
| 知识库文档 (KnowledgeDoc) | RAG 知识库中的可检索内容 | content, metadata, embedding, source |
| 教研纪要 (MeetingNotes) | 教研会议的结构化记录 | meeting_info, discussions, decisions, action_items |
| 练习题 (Quiz) | 课堂伴教产出的测试题 | subject, grade, topic, question_list, answers |
| 教师画像 (TeacherProfile) | 教师长期记忆的聚合表达 | teaching_style_tags, preferences, stats, history |
| 教学素材 (Material) | 外部教学资源（视频/3D/图片/教具） | category, title, description, teaching_tips |

### 核心业务流程

```
教师输入备课参数
    → 感知层（可选 OCR/ASR 识别）
    → 规划层（意图路由）
    → 执行层（Agent + RAG 检索 + 记忆注入）
    → 生成教案/出题/报告
    → 记忆层自动保存
```

## 系统架构 — 四层 Agent 架构

```
┌─────────────────────────────┐
│         感知层 (Perception)    │
│  ASR 语音识别 + OCR 手写识别   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│         规划层 (Planning)     │
│     LangChain 意图路由        │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│         执行层 (Execution)    │
│  5 大 Agent + RAG 检索引擎    │
│  QuickLessonPrep             │
│  WisdomTransfer              │
│  ClassroomCompanion          │
│  Material                    │
│  MeetingNotes                │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│         记忆层 (Memory)       │
│  对话记忆 + 教师专属画像      │
└─────────────────────────────┘
```

### Agent 职责

| Agent | 输入 | 输出 | 关键依赖 |
|-------|------|------|---------|
| QuickLessonPrepAgent | subject, grade, topic, rural_context | 结构化教案 | RAG(可选), ASR(可选), TeacherProfile |
| WisdomTransferAgent | image_path(图片) | 结构化教案文本 | OCR, RAG(入库) |
| ClassroomCompanionAgent | subject, grade, topic, knowledge_points | 练习题/经典题 | RAG(检索) |
| MaterialAgent | subject, grade, topic, rural_context | 素材推荐列表 | 无外部依赖(LLM 生成) |
| MeetingNotesAgent | transcript/audio | 结构化教研报告 | ASR(可选), RAG(入库) |
| RouterAgent | user_input | 意图分类结果 | 无外部依赖 |

## 核心数据流

### 完整请求处理路径

```
用户输入 → 感知层 → 规划层 → 执行层 → 记忆层 → 用户输出
```

### 路径 A：文本输入（极速备课）

1. 用户通过 Streamlit/API 输入文本参数
   - 数据: `{"subject": "数学", "grade": "三年级", "topic": "分数", "rural_context": "分苹果"}`
2. **[感知层]** 文本直接透传（无需 ASR/OCR 处理）
3. **[规划层]** `RouterAgent.run({"user_input": "帮我备一节数学课"})`
   - 数据变换: `Dict → {"intent": "quick_lesson_prep", "agent": "RouterAgent", "info": {...}}`
   - 内部流程: router_template → LLM → StrOutputParser → validation_template → LLM → 验证
4. **[执行层]** `QuickLessonPrepAgent.run(input_data)`
   - 数据变换: `Dict → {"success": true, "result": "教案文本...", "agent": "QuickLessonPrepAgent"}`
   - 内部流程: lesson_plan_template + input_data → LLM chain → StrOutputParser → `_format_output()`
   - [未来] RAG 检索: `knowledge_base.search(query)` → 参考材料注入 prompt
   - [未来] 记忆注入: `teacher_profile.teaching_styles` → prompt 增强
5. **[记忆层]** 自动保存（当前未集成，未来由 BaseAgent 触发）
   - [未来] `conversation_memory.save_context(input, output)`
   - [未来] `teacher_profile.increment_lesson_plans()`
6. 返回给用户: `{"success": true, "result": "教案文本..."}`

### 路径 B：图片输入（智慧传承）

1. 用户上传手写教案图片
   - 数据: `{"image_path": "/data/uploads/xxx.jpg"}`
2. **[感知层]** `WisdomTransferAgent.recognize_handwriting(image_path)`
   - 数据变换: `image_path → OCR 文本字符串`
   - 内部流程: `BaseOCR.recognize(image_path)` → 文本（通过 AgentFactory 注入）
3. **[规划层]** `RouterAgent` 识别意图为 `"wisdom_transfer"`
4. **[执行层]** `WisdomTransferAgent.run(input_data)`
   - 数据变换: `OCR 文本 → structure_template → LLM → 结构化教案`
   - [未来] `knowledge_base.add_document(text, level=TEACHER)` — 结构化结果入库
   - [未来] LLM 分析教学风格 → `teacher_profile.add_teaching_style()`
5. **[记忆层]** 对话记忆 + 教师画像更新

### 路径 C：音频输入（教研纪要，基础设施层待实现）

1. 用户上传教研会议录音
   - 数据: `{"audio_path": "/data/uploads/meeting.mp3"}`
2. **[感知层]** `BaseASR.transcribe(audio_path)` → 转写文本
   - [当前] `LocalWhisperASR` 待实现（`tools/asr.py`），需本地模型支持
3. **[规划层]** `RouterAgent` 识别意图为 `"meeting_notes"`
4. **[执行层]** `MeetingNotesAgent.run(input_data)`
   - 数据变换: `转写文本 → structure_template → LLM → 结构化教研报告`
   - [未来] `knowledge_base.add_document(report, level=SCHOOL)` — 教研成果入库
5. **[记忆层]** 对话记忆自动保存（BaseAgent._save_to_memory 触发）

### 路径 D：通用对话

1. 用户输入无法匹配任何 Agent 意图
2. `RouterAgent` 返回 `intent="general_chat"`
3. [当前] 无对应处理，返回路由结果
4. [未来] 可设计 GeneralChatAgent 或直接由 LLM 回复

### 层间数据契约

| 层间边界 | 输入格式 | 输出格式 | 协议 |
|---------|---------|---------|------|
| 用户 → 感知层 | 原始文件(text/image/audio) | 统一文本 `str` | `BaseOCR.recognize()` / `BaseASR.transcribe()` |
| 感知层 → 规划层 | `str`（用户原始输入） | `Dict{intent, agent, info}` | `RouterAgent.run(Dict)` |
| 规划层 → 执行层 | `Dict`（路由结果 + 原始参数） | `Dict{success, result, agent, metadata}` | 具体 `Agent.run(Dict)` |
| 执行层 → 记忆层 | `Dict`（输入+输出） | `None`（副作用） | `ConversationMemory.save_context()` / `TeacherProfileManager` |
| 执行层 → 用户 | `Dict{success, result, ...}` | JSON response | FastAPI / Streamlit |

## 关键抽象接口

### BaseAgent (`maitian_agent/agents/base.py`)

所有 Agent 的抽象基类，定义统一契约。

```python
class BaseAgent(ABC):
    def __init__(self, llm: Optional[BaseChatModel], name: str, description: str)

    @abstractmethod
    def build_chain(self) -> Any
        """构建 LangChain 处理链"""

    @abstractmethod
    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]
        """执行 Agent，统一入口。返回格式: {success: bool, result: Any, agent: str, metadata: Dict}"""

    def _validate_input(self, input_data: Dict, required_keys: list) -> None
        """验证输入数据完整性，缺少 key 时抛出 ValueError"""

    def _format_output(self, result: Any, metadata: Optional[Dict] = None) -> Dict[str, Any]
        """格式化成功输出为标准 Dict"""

    def _handle_error(self, error: Exception) -> Dict[str, Any]
        """格式化错误输出为标准 Dict"""
```

**契约规则**: 所有子类必须实现 `run()` 和 `build_chain()`；`run()` 签名固定为 `Dict[str, Any] → Dict[str, Any]`；返回 Dict 必须包含 `success` 键；依赖为 None 时退化为纯 LLM 模式。

### BaseOCR (`maitian_agent/tools/ocr.py`)

```python
class BaseOCR(ABC):
    @abstractmethod
    def recognize(self, image_path: str) -> str

    @abstractmethod
    def recognize_batch(self, image_paths: List[str]) -> List[str]
```

**实现**: `EasyOCRProcessor`, `PaddleOCRProcessor`（待实现）
**工厂**: `OCRProcessor.create(ocr_type="easyocr") → BaseOCR`

### BaseASR (`maitian_agent/tools/asr.py`)

```python
class BaseASR(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str
```

**实现**: `WhisperASR`（API）, `LocalWhisperASR`（待实现）

### KnowledgeBase (`maitian_agent/rag/knowledge_base.py`)

三层知识库架构: `universal`（通用教材）/ `school`（校本共享）/ `teacher`（教师专属）

```python
class KnowledgeBase:
    def __init__(self, persist_directory: str, embedding_model_name: str)

    def add_document(self, text: str, level: KnowledgeLevel, metadata: Optional[Dict]) -> List[str]
    def add_documents(self, texts: List[str], level: KnowledgeLevel, metadatas: Optional[List[Dict]]) -> List[str]
    def search(self, query: str, level: Optional[KnowledgeLevel], k: int = 4) -> List[Any]
    def search_with_filter(self, query: str, filter_dict: Dict, k: int = 4) -> List[Any]
    def delete_by_level(self, level: KnowledgeLevel, ids: List[str]) -> None
    def get_collection_info(self, level: KnowledgeLevel) -> Dict[str, Any]
```

### ConversationMemory (`maitian_agent/memory/conversation_memory.py`)

短期对话记忆，滑动窗口机制。

```python
class ConversationMemory:
    def __init__(self, memory_type: str, conversation_window: int, session_id: str, persist_directory: str)

    def save_context(self, input_data: Dict, output_data: Dict) -> None
    def load_memory_variables(self) -> Dict[str, Any]
    def get_conversation_history(self) -> List[Dict[str, str]]
    def clear(self) -> None
```

**持久化**: JSON 文件，路径: `{persist_directory}/chat_history_{session_id}.json`
**窗口机制**: 保留最近 N 轮对话（`N=conversation_window`），超出部分丢弃

### TeacherProfileManager (`maitian_agent/memory/teacher_profile.py`)

长期教师画像管理。

```python
class TeacherProfileManager:
    def __init__(self, persist_directory: str)

    def save_profile(self, profile: TeacherProfile) -> None
    def load_profile(self, teacher_id: str) -> Optional[TeacherProfile]
    def create_profile(self, teacher_id: str, name: str, ...) -> TeacherProfile
    def list_profiles(self) -> List[Dict[str, Any]]
    def delete_profile(self, teacher_id: str) -> bool
```

**TeacherProfile 数据模型**: `teacher_id`, `name`, `school`, `subjects`, `grades`, `teaching_years`, `teaching_styles: List[TeachingStyle]`, `preferences: Dict`, `lesson_plans_count: int`
**持久化**: JSON 文件，路径: `{persist_directory}/profile_{teacher_id}.json`

## 四层架构详细职责

### 感知层 (Perception Layer)

**职责**: 将多模态输入（语音、手写图片）转换为统一文本格式。

**组件**:
- `BaseOCR` / `EasyOCRProcessor` — 手写教案图片 → 文本
- `BaseASR` / `WhisperASR` — 语音录音 → 文本
- `FileProcessor` — 文件上传、保存、管理

**交互规则**: 仅被执行层 Agent 调用（通过注入的依赖）；不依赖执行层、记忆层；纯文本输入时感知层被跳过（透传）。

**当前状态**: OCR 可用（EasyOCR，92% 准确率），ASR 待集成（`LocalWhisperASR` 基础设施层待实现）。

### 规划层 (Planning Layer)

**职责**: 意图识别与路由，决定由哪个 Agent 处理用户请求。

**组件**: `RouterAgent` — 基于 LLM 的意图分类器，6 种意图（`quick_lesson_prep`, `wisdom_transfer`, `classroom_companion`, `material_recommend`, `meeting_notes`, `general_chat`），二次校验机制（router_chain → validation_chain）。

**交互规则**: 接收感知层输出的文本（或用户直接输入的文本）；输出意图分类结果，由 API 层或前端根据意图调用对应 Agent；不直接调用执行层 Agent；无外部依赖（纯 LLM 推理）。

**当前状态**: 已实现，但 API 层未使用路由结果自动调度。

### 执行层 (Execution Layer)

**职责**: 执行具体业务逻辑，生成教案/练习题/报告等。

**组件**: 5 个业务 Agent，每个继承 `BaseAgent`，通过 `run(Dict) -> Dict` 统一接口暴露。

| Agent | 核心能力 | Prompt 模板 | 性能要求 | LLM 温度 |
|-------|---------|------------|---------|----------|
| QuickLessonPrepAgent | 乡土化教案生成 | lesson_plan_template | ≤10秒 | 0.7 |
| WisdomTransferAgent | 手写教案 OCR + 结构化 | structure_template | ≤5秒/张 | 0.3 |
| ClassroomCompanionAgent | 练习题生成 + 经典题检索 | quiz_template + retrieval_template | ≤3秒 | 0.5 |
| MaterialAgent | 教学素材推荐 | material_template | 无硬性要求 | 0.7 |
| MeetingNotesAgent | 教研报告结构化 | structure_template | 转写≥95% | 0.3 |

**交互规则**: 可依赖工具抽象层、RAG 抽象层、记忆抽象层、配置层；通过构造函数注入依赖，禁止内部实例化跨层对象。

**当前状态**: 5 个 Agent 均已实现基本功能，但 RAG/记忆/工具层均未集成。

### 记忆层 (Memory Layer)

**职责**: 管理短期对话上下文和长期教师画像。

**组件**:
- `ConversationMemory` — 短期记忆，滑动窗口（默认 5 轮），JSON 持久化
- `TeacherProfileManager` — 长期画像，`TeacherProfile` Pydantic 数据模型，JSON 持久化
- `TeacherStyleVectorStore` — 风格向量匹配（待实现）

**交互规则**: 不依赖执行层；被执行层通过注入调用；RAG 层（KnowledgeBase）与记忆层（TeacherProfile）独立，但共享持久化目录。

**当前状态**: 代码完整但未被任何 Agent 调用。

### 层间交互序列

```
用户 → [Streamlit/API]
  → RouterAgent.run() → 意图识别
  → QuickLessonPrepAgent.run(input_data)  # 以极速备课为例
    → [可选] ASR.transcribe() / OCR.recognize()     # 感知层
    → [可选] knowledge_base.search()                  # RAG 层
    → [可选] teacher_profile.load_profile()            # 记忆层
    → lesson_plan_template | LLM | StrOutputParser    # LLM 推理
    → _format_output(result)
    → [可选] conversation_memory.save_context()        # 记忆层
  → 返回 Dict{success, result, agent, metadata}
→ [Streamlit/API] → 用户
```

## 技术栈

- **语言/运行时**: Python 3.11+
- **AI 框架**: LangChain 0.2.x（规划升级 1.2）
- **大模型**: DeepSeek-V2（OpenAI 兼容接口）
- **向量数据库**: ChromaDB + BGE-Large-zh
- **OCR**: EasyOCR
- **ASR**: Whisper API
- **后端**: FastAPI
- **前端**: Streamlit
- **部署**: Docker

## 架构原则

1. **依赖倒置**: Agent 通过抽象接口依赖 RAG/记忆/工具层，而非直接耦合
2. **统一接口**: 所有 Agent 的 `run()` 必须采用 `Dict[str, Any] → Dict[str, Any]` 签名
3. **工厂注入**: 通过 AgentFactory 统一管理依赖创建与注入，禁止在 Agent 内部实例化跨层依赖
4. **向下兼容**: RAG/记忆/工具层集成时，参数为 None 则退化为纯 LLM 模式
5. **测试隔离**: 外部 API 一律 mock，Chroma 使用临时目录

### 层间依赖规则

```
执行层 (Agent)  → 可依赖: 工具抽象层、RAG抽象层、记忆抽象层、配置层
工具层          → 不可依赖: 执行层、记忆层
RAG层           → 不可依赖: 执行层、工具层
记忆层          → 不可依赖: 执行层
配置层          → 不可依赖: 任何业务层
```

### 已知架构问题（2026-05-03 审计后）

| 问题 | 位置 | 严重程度 | 说明 |
|------|------|---------|------|
| ~~**run() 签名不统一**~~ | QuickLessonPrepAgent, WisdomTransferAgent | ✅ 已修复 | 已统一为 `Dict[str, Any] → Dict[str, Any]` 签名 |
| ~~**跳过配置层**~~ | 所有 Agent + demo | ✅ 已修复 | 已统一通过 `Settings` 注入 + `_create_default_llm()` |
| ~~**跳过工具抽象层**~~ | WisdomTransferAgent | ✅ 已修复 | 已改用 `BaseOCR` 抽象，通过 AgentFactory 注入 |
| ~~**RAG 未集成**~~ | 所有 Agent | ✅ 已修复 | 已通过 `_retrieve_context()` 集成到 Agent 调用链 |
| ~~**记忆未集成**~~ | 所有 Agent | ✅ 已修复 | 已通过 `_save_to_memory()` + `_load_teacher_profile()` 集成 |
| ~~**NotImplementedError**~~ | 4 处 TODO 方法 | ✅ 已清理 | 移除冗余存根，保留基础设施层合理占位（Milvus/LocalWhisper） |
| ~~**API 绕过 AgentFactory**~~ | api/routes.py | ✅ 已修复 | 已改为 `AgentFactory().create_all()` |
| ~~**ConversationMemory logger 缺失**~~ | memory/conversation_memory.py | ✅ 已修复 | 添加 `import logging` + `logger` 定义 |
| ~~**TeacherProfile Pydantic V1**~~ | memory/teacher_profile.py | ✅ 已修复 | `class Config` → `model_config = ConfigDict(...)` |
| MaterialAgent RAG 深度集成 | material_agent.py | 🟡 中等 | RAG 结果仅附加在输出末尾，应深度融入 prompt |
| RouterAgent 记忆保存 | agents/router.py | 🟢 低 | 路由决策未记录到对话记忆 |
| AgentFactory 注入方式统一 | agents/factory.py | 🟢 低 | knowledge_base/memory/teacher_profile 通过属性注入而非构造函数 |

### 术语说明

- **Agent** = 继承 BaseAgent 的具体 Agent 类，提供标准 `run(Dict) → Dict` 接口和公开方法
- **Tools/工具层** = BaseOCR、BaseASR 等工具抽象层 + 工厂方法，由 AgentFactory 注入 Agent
- **RAG** = KnowledgeBase 三层架构（universal/school/teacher），通过 `add_document()`/`search()` 接口暴露
- **记忆层** = ConversationMemory（短期对话）+ TeacherProfileManager（长期画像）
- **配置层** = pydantic-settings Settings，入口处加载，通过 BaseAgent 下发

## 关键路径

- Demo → 主项目代码路径分叉：Demo 保持简洁独立，主项目承担完整集成
- 开发顺序：接口统一 → 配置集成 → 工厂模式 → 工具/RAG/记忆集成 → 功能增强
- 版本管理：v0.1.0-demo → v0.2.0(核心集成) → v0.3.0(功能优化)

## 目录结构规范

```
project_root/
├── CONTEXT.md              # 领域上下文（本文档）
├── CHANGELOG.md            # 版本变更记录
├── README.md               # 项目总览
├── prompts.md              # 任务提示
├── requirements.txt        # 依赖管理
├── .env.example            # 环境变量模板
├── docs/
│   ├── adr/               # 架构决策记录
│   ├── *.md               # 其他文档
│   └── *.docx             # 原始文档
├── demo/                  # Demo 应用（独立模块）
│   ├── agents/            # Demo Agent 实现
│   ├── app.py             # Streamlit 入口
│   ├── assets/            # Demo 静态资源
│   └── utils/             # Demo 工具函数
├── maitian_agent/         # 主项目包
│   ├── agents/            # Agent 层
│   │   ├── base.py        # BaseAgent 抽象基类
│   │   ├── factory.py     # AgentFactory 依赖注入
│   │   └── *.py           # 各 Agent 实现
│   ├── api/               # FastAPI REST 接口
│   ├── cli.py             # 命令行入口
│   ├── config/            # 配置管理 (pydantic-settings)
│   ├── frontend/          # Streamlit 前端
│   ├── memory/            # 记忆层
│   ├── rag/               # RAG 知识库层
│   ├── tools/             # 工具层 (OCR/ASR/File)
│   └── utils/             # 工具函数 (logger 等)
├── docker/                # Docker 部署配置
├── tests/                 # 测试目录
│   ├── conftest.py        # pytest 共享 fixtures
│   ├── fixtures/          # 测试数据
│   └── test_*.py          # 测试用例
└── assets/                # 项目级静态资源
```
