# [0002] Agent 接口统一与依赖注入策略

- 状态: 接受
- 日期: 2026-05-03

## 背景

代码审查发现以下架构问题：

### 问题 1: run() 接口不一致

| Agent | 当前签名 | 问题 |
|-------|---------|------|
| `BaseAgent` (规范) | `run(input_data: Dict[str, Any]) -> Dict[str, Any]` | 标准契约 |
| `QuickLessonPrepAgent` | `run(subject, grade, topic, rural_context) -> str` | ❌ 返回 str，接受展平参数 |
| `WisdomTransferAgent` | `run(image_path) -> str` | ❌ 同上 |
| `ClassroomCompanionAgent` | `run(input_data: Dict) -> Dict` | ✅ |
| `MaterialAgent` | `run(input_data: Dict) -> Dict` | ✅ |
| `MeetingNotesAgent` | `run(input_data: Dict) -> Dict` | ✅ |
| `RouterAgent` | `run(input_data: Dict) -> Dict` | ✅ |

RouterAgent 依赖统一的 Dict→Dict 接口来调用下游 Agent，QuickLessonPrepAgent 和 WisdomTransferAgent 的不一致直接阻止了 Router 正常工作。

### 问题 2: 直接依赖具体实现而非抽象

- `WisdomTransferAgent` 在内部直接创建 `easyocr.Reader`，而非使用 `tools/ocr.py` 中的 `BaseOCR` 抽象
- 所有 Agent 通过 `os.getenv()` + `load_dotenv()` 读取配置，而非使用 `config/settings.py` 的 `Settings`
- `MeetingNotesAgent.transcribe_audio()` 在自己的类中实现，而非通过 `WhisperASR` 工具类

### 问题 3: 模块割裂

RAG `KnowledgeBase`、记忆 `ConversationMemory`、`TeacherProfileManager` 代码完整但从未被任何 Agent 实际调用：
- `WisdomTransferAgent.save_to_knowledge_base()` → `NotImplementedError`
- `KnowledgeBase` 的 `add_document()` / `search()` → 从未被调用
- `ConversationMemory`/`TeacherProfileManager` → 从未被注入任何 Agent

## 决策

### 1. 修复 run() 签名为统一的 Dict→Dict

`QuickLessonPrepAgent` 和 `WisdomTransferAgent` 的 `run()` 方法改为：
```python
def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    subject = input_data.get("subject")
    ...
    return self._format_output(result)
```

保留原有的参数化公开方法（如 `generate_lesson_plan()`）供直接调用，`run()` 作为标准接口。

### 2. 统一配置注入

- 所有 Agent 通过 `BaseAgent.__init__(settings: Optional[Settings])` 获取配置
- 移除所有 `os.getenv()` 和 `load_dotenv()` 调用
- `BaseAgent` 提供 `_create_default_llm()` 方法

### 3. 抽象依赖注入

- `WisdomTransferAgent` 接受 `ocr_processor: Optional[BaseOCR]` 参数，默认由 `OCRProcessor.create()` 创建
- `QuickLessonPrepAgent` / `MeetingNotesAgent` 接受 `asr: Optional[BaseASR]` 参数
- 所有 Agent 接受 `knowledge_base: Optional[KnowledgeBase]`、`conversation_memory: Optional[ConversationMemory]` 参数
- 依赖为 `None` 时退化为纯 LLM 模式（向后兼容）

### 4. 创建 AgentFactory

集中化 Agent 创建，统一注入所有依赖。

## 理由

- **统一接口是 Router 工作的前提**：如果不解决这个问题，规划和路由无法正常工作
- **抽象依赖**：WisdomTransferAgent 直接硬编码 EasyOCR 给切换 PaddleOCR 造成困难
- **None = 降级模式**：降低了集成风险，可以在集成中断时保持功能可用
- **工厂模式**：避免了服务定位器反模式，创建逻辑集中在一处

## 影响

- 正向：所有 Agent 可被 Router 统一调度
- 正向：测试更容易（注入 mock 依赖）
- 正向：OCR/ASR 可透明切换实现
- 代价：QuickLessonPrepAgent 和 API 调用者需要修改调用方式
- 代价：现有 Streamlit 前端需要适配新签名

## 备选方案

1. **不统一接口**：Router 为每个 Agent 特殊处理——维护成本高，失去多态优势
2. **服务定位器模式**：全局 `ServiceContainer`——隐式依赖，不利于测试
