# ADR-001: 四层Agent架构设计

- 状态: 接受
- 日期: 2026-05-03
- 关联: [0001-four-layer-agent-architecture.md](./0001-four-layer-agent-architecture.md)（英文简版）

## 背景

乡村教育场景面临以下核心挑战，需要一种能够良好组织多模态、多 Agent、持久化能力的架构：

1. **多模态输入需求**: 老教师的手写教案（图片）、教研会议录音（音频）、文本备课需求——三种输入格式需要统一处理
2. **多 Agent 协作需求**: 备课、传承、伴教、素材推荐、教研纪要——五种独立业务场景，各有不同的 Prompt 模板、输入格式和性能要求
3. **持久化记忆需求**: 教师画像需要跨会话保持，知识库需要持续积累，对话上下文需要滑动窗口管理
4. **资源约束**: 乡村学校网络条件差，需要支持离线/弱网部署，单体架构优于分布式
5. **可替换性需求**: OCR 引擎（EasyOCR/PaddleOCR）、ASR 引擎（Whisper API/本地模型）、向量存储（ChromaDB/Milvus）可能需要切换

## 决策

采用四层 Agent 架构：**感知层 → 规划层 → 执行层 → 记忆层**。

### 感知层 (Perception Layer)

- **组件**: `BaseOCR` + `BaseASR` + `FileProcessor`
- **职责**: 将多模态输入（语音、手写图片）转换为统一文本格式
- **设计**: 抽象接口 + 工厂模式，支持运行时切换实现
- **规则**: 仅被执行层 Agent 调用（通过注入的依赖），不依赖执行层和记忆层

### 规划层 (Planning Layer)

- **组件**: `RouterAgent`（基于 LLM 的意图分类器）
- **职责**: 意图识别与路由，决定由哪个 Agent 处理用户请求
- **设计**: Few-Shot 意图列表 + 二次校验机制（router_chain → validation_chain）
- **6 种意图**: `quick_lesson_prep`, `wisdom_transfer`, `classroom_companion`, `material_recommend`, `meeting_notes`, `general_chat`
- **规则**: 无外部依赖（纯 LLM 推理），不直接调用执行层 Agent

### 执行层 (Execution Layer)

- **组件**: 5 个业务 Agent，每个继承 `BaseAgent`
- **职责**: 执行具体业务逻辑（教案生成、OCR 识别、出题、素材推荐、报告结构化）
- **设计**: 统一 `run(Dict) -> Dict` 接口，LangChain LCEL 链式调用
- **规则**: 可依赖工具抽象层、RAG 抽象层、记忆抽象层、配置层；通过构造函数注入

| Agent | 核心能力 | Prompt 模板 | 性能要求 | LLM 温度 |
|-------|---------|------------|---------|----------|
| QuickLessonPrepAgent | 乡土化教案生成 | lesson_plan_template | ≤10秒 | 0.7 |
| WisdomTransferAgent | 手写教案 OCR + 结构化 | structure_template | ≤5秒/张 | 0.3 |
| ClassroomCompanionAgent | 练习题生成 + 经典题检索 | quiz_template + retrieval_template | ≤3秒 | 0.5 |
| MaterialAgent | 教学素材推荐 | material_template | 无硬性要求 | 0.7 |
| MeetingNotesAgent | 教研报告结构化 | structure_template | 转写≥95% | 0.3 |

### 记忆层 (Memory Layer)

- **组件**: `ConversationMemory`（短期）+ `TeacherProfileManager`（长期）
- **职责**: 管理短期对话上下文（滑动窗口，默认 5 轮）和长期教师画像（JSON 持久化）
- **设计**: 短期记忆与长期记忆独立管理，教师画像可跨 Agent 共享
- **规则**: 不依赖执行层，被执行层通过注入调用

## 理由

### 为什么不用单一 Agent？

- 5 种业务场景的 Prompt 模板、输入格式、性能要求完全不同
- 单一 Agent 的 Prompt 会过长（>2000 tokens），导致 LLM 注意力分散
- 单一 Agent 无法针对不同场景优化温度参数（备课 0.7、OCR 结构化 0.3、伴教 0.5）
- 单一 Agent 无法独立测试和迭代

### 为什么不用微服务架构？

- 乡村学校网络条件差，分布式服务依赖不可靠
- 项目规模（5 个 Agent + RAG + 记忆）不需要服务间通信的复杂性
- 单体部署通过 Docker 即可满足需求，运维成本低
- 微服务引入的网络延迟对 ≤3 秒的伴教场景不可接受

### 为什么需要独立的感知层？

- OCR 和 ASR 是重资源操作（模型加载、GPU/CPU 计算），需要独立管理生命周期
- 感知层可独立升级（如 EasyOCR → PaddleOCR）而不影响业务逻辑
- 纯文本输入时感知层被跳过，避免不必要的处理开销
- 抽象接口设计（BaseOCR/BaseASR）支持运行时切换实现

### 为什么需要独立的规划层？

- 用户输入可能是语音/图片转写后的文本，需要智能分类
- 二次校验机制防止误路由（如将备课请求误判为通用对话）
- 规划层可独立迭代（如添加 Few-Shot 示例、调整校验策略）
- 新增 Agent 只需在 RouterAgent 的 INTENTS 字典中注册，无需修改其他层

### 为什么需要独立的记忆层？

- 短期记忆（对话上下文）和长期记忆（教师画像）的生命周期不同
- 记忆层可独立演进（如从 JSON 文件迁移到 MongoDB）
- 教师画像需要跨 Agent 共享（备课 Agent 和传承 Agent 都需要访问）
- 记忆层与 RAG 层独立但互补：记忆层存教师偏好，RAG 层存教学知识

## 影响

### 正向影响

- **架构清晰**: 四层职责分明，新人可通过 CONTEXT.md 快速理解系统
- **可测试性**: 每层可独立 mock 测试（如注入 mock OCR 测试 WisdomTransferAgent）
- **可替换性**: OCR/ASR/向量存储均可透明切换，无需修改 Agent 业务逻辑
- **渐进集成**: 各层可独立开发测试，通过依赖注入组装（依赖为 None 时退化为纯 LLM 模式）

### 代价

- **前期投入**: 需要定义层间接口契约（BaseAgent、BaseOCR、BaseASR、KnowledgeBase 等）
- **简单场景开销**: 纯文本备课仍需经过完整架构路径（感知层跳过，但仍经规划层路由）
- **接口维护成本**: 接口变更可能影响多层代码（如 BaseAgent.run() 签名变更需同步所有 Agent）
- **构造函数参数增多**: Agent 需要接收多个可选依赖（通过 AgentFactory 减轻）

### 已知风险

- **RouterAgent 意图分类准确率**: 依赖 LLM 能力，可能误路由；二次校验可缓解但无法完全消除
- **感知层 OCR 准确率**: 受手写质量影响（当前 EasyOCR 92% 准确率，复杂手写可能更低）
- **记忆层并发安全**: JSON 文件持久化在并发场景下可能有竞争条件（落地阶段迁移到 MongoDB 解决）

## 备选方案

### 1. 单一 Agent + 工具调用（LangChain Tool Calling）

- **优点**: 实现简单，一个 Agent 通过工具调用完成所有任务
- **缺点**: Prompt 过长导致注意力分散；无法针对不同场景优化温度参数；工具调用增加延迟；难以独立测试
- **否决原因**: 5 种业务场景差异太大，单一 Prompt 无法兼顾

### 2. 微服务架构（每个 Agent 独立部署）

- **优点**: 独立扩展、独立部署、故障隔离
- **缺点**: 乡村网络条件差，服务间通信不可靠；运维成本高；网络延迟对实时场景不可接受
- **否决原因**: 目标用户（乡村学校）的网络条件不支持

### 3. 管道架构（固定顺序处理）

- **优点**: 简单直接，数据流清晰
- **缺点**: 无法根据意图动态路由；所有输入都经过所有步骤，浪费资源；无法针对不同场景优化
- **否决原因**: 5 种业务场景不需要固定顺序处理，按意图路由更高效

## 实施状态

### 已完成（2026-05-03 架构审计确认）

- [x] 四层目录结构已建立
- [x] BaseAgent 抽象基类已实现（`run(Dict) -> Dict` + `build_chain()`）
- [x] 5 个业务 Agent + RouterAgent 已实现基本功能
- [x] BaseOCR / BaseASR 抽象接口已定义
- [x] KnowledgeBase 三层架构已实现（universal / school / teacher）
- [x] ConversationMemory / TeacherProfileManager 已实现
- [x] 3 个 ADR 已记录架构决策（0001-0003）
- [x] **AgentFactory 依赖注入** — 统一管理 LLM、Settings、KnowledgeBase、ConversationMemory、TeacherProfile、OCR、ASR 共 7 种依赖
- [x] **RAG 层集成到 Agent** — `_retrieve_context()` 已集成到 QuickLessonPrepAgent、ClassroomCompanionAgent、MaterialAgent
- [x] **记忆层集成到 Agent** — `_save_to_memory()` 已集成到所有 5 个业务 Agent；`_load_teacher_profile()` 已集成到 QuickLessonPrepAgent
- [x] **工具层集成到 Agent** — WisdomTransferAgent 通过 BaseOCR 抽象 + AgentFactory 注入，已移除直接 easyocr.Reader 耦合
- [x] **配置层集成到 Agent** — 所有 Agent 通过 Settings 注入 + `_create_default_llm()` 创建 LLM，已移除 os.getenv() 直接调用
- [x] **API 层使用 AgentFactory** — `api/routes.py` 通过 `AgentFactory().create_all()` 初始化所有 Agent
- [x] **代码清理** — 移除 3 个冗余 NotImplementedError 存根方法，清理 TODO 项，bare except 添加日志
- [x] **诊断修复** — 修复 4 个 Critical 问题（tools 导入、ConversationMemory 初始化、Pydantic V2、transcribe_audio 缺失）

### 架构合规审计结果（2026-05-03）

| 层 | 文件数 | PASS | FAIL | 合规率 |
|----|--------|------|------|--------|
| 感知层 (tools/) | 4 | 4 | 0 | 100% |
| 规划层 (router) | 1 | 1 | 0 | 100% |
| 执行层 (agents/) | 7 | 6 | 1 | 86% |
| 记忆层 (memory/) | 2 | 2 | 0 | 100% |
| RAG 层 (rag/) | 4 | 4 | 0 | 100% |
| Config 层 (config/) | 2 | 2 | 0 | 100% |
| 跨切面 (api/) | 1 | 1 | 0 | 100% |
| **合计** | **21** | **20** | **1** | **95%** |

### 待后续优化

- [ ] MaterialAgent RAG 检索结果应深度融入 prompt（当前仅附加在输出末尾）
- [ ] RouterAgent 路由决策记录到对话记忆（`_save_to_memory`）
- [ ] AgentFactory 注入方式统一（knowledge_base/memory/teacher_profile 统一走构造函数 kwargs）
- [ ] HybridRetriever BM25 关键词检索实现（当前降级为向量检索）
- [ ] LocalWhisperASR 本地 Whisper 模型集成
- [ ] 子类 Agent 类型注解统一为 `Optional[BaseChatModel]`，移除直接 ChatOpenAI 导入
