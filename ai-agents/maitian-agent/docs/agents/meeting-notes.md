# 教研纪要Agent (MeetingNotesAgent)

## 职责描述

将教研会议录音转写为结构化教研报告。核心价值是将非结构化的会议讨论转化为可沉淀的教研成果，支持教研活动的数字化管理和经验积累。

**源码位置**: `maitian_agent/agents/meeting_notes.py`

## 输入输出接口

### run() 标准接口

**输入** (`Dict[str, Any]`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audio_path` | str | 二选一 | 音频文件路径（当前 `NotImplementedError`） |
| `transcript` | str | 二选一 | 手动提供的转写文本 |

**输出** (`Dict[str, Any]`):

```python
{
    "success": True,
    "result": "结构化教研报告（含会议信息/议题/讨论摘要/决议/行动计划/教研成果）",
    "agent": "MeetingNotesAgent",
    "metadata": {}
}
```

错误情况（缺少输入）:
```python
{"success": False, "error": "缺少音频文件或转写文本"}
```

### 公开方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `transcribe_audio()` | `(audio_path: str) -> str` | 音频转写（当前 `NotImplementedError`） |
| `process_meeting_notes()` | `(meeting_transcript: str) -> str` | 处理教研纪要文本 |
| `build_chain()` | `() -> Chain` | 构建 LangChain 结构化处理链 |

## Prompt 模板说明

**模板名称**: `structure_template`

**变量占位符**:

| 变量 | 说明 |
|------|------|
| `{meeting_transcript}` | 教研会议原始记录文本 |

**设计意图**: 引导 LLM 扮演"专业教研秘书"角色，将原始会议记录整理为 6 个标准部分：
1. 会议基本信息（时间、地点、参与人员、主题）
2. 会议议题
3. 讨论内容摘要
4. 决议事项
5. 行动计划（具体可执行）
6. 教研成果（可沉淀的教学经验）

要求语言精炼、保留关键信息和专业术语、行动计划具体可执行。

**LLM 参数**: `temperature=0.3`（较低，追求准确性和忠实于原文）

## 依赖关系

### 当前依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| `ChatOpenAI` | 直接依赖 | DeepSeek-V2 API，通过 `os.getenv()` 创建 |

### 未来计划依赖（已设计未集成）

| 依赖 | 接口 | 集成方式 | 用途 |
|------|------|---------|------|
| `BaseASR` | `transcribe(audio_path) -> str` | 构造函数注入 | 音频转写（替换 `NotImplementedError`） |
| `KnowledgeBase` | `add_document(text, level) -> List[str]` | 构造函数注入 | 教研成果入库到 `school` 层级 |
| `ConversationMemory` | `save_context(input, output)` | 构造函数注入 | 保存教研对话上下文 |

## 性能要求

| 指标 | 目标值 | 验证值 |
|------|--------|--------|
| 音频转写准确率 | ≥ 95% | 待验证（ASR 未集成） |

## 已知限制

1. **`transcribe_audio()` 未实现**: 音频转写功能抛出 `NotImplementedError`，音频输入路径完全不可用
2. **仅支持文本输入**: 当前只能手动粘贴转写内容，无法直接处理录音文件
3. **未集成 ASR**: Whisper API 未接入，感知层断裂
4. **未集成知识库**: 教研成果未自动入库到 `KnowledgeBase`，无法被其他 Agent 检索
5. **配置未集中**: 直接调用 `os.getenv()` + `load_dotenv()`，未使用 `Settings`
6. **无参会人员识别**: 无法自动提取和识别会议参与人员

## 与架构的集成点

```
规划层 RouterAgent
  意图 "meeting_notes"
    ↓
执行层 MeetingNotesAgent.run(input_data)
  ├── [当前] transcript 文本直接传入
  ├── [未来] 感知层: BaseASR.transcribe(audio_path) — 音频转文本
  ├── LangChain: structure_template | LLM | StrOutputParser
  ├── [未来] RAG层: KnowledgeBase.add_document() — 教研成果入库
  └── [未来] 记忆层: ConversationMemory.save_context()
    ↓
返回 Dict{success, result, agent, metadata}
```
