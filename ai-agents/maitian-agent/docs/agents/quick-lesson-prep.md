# 极速备课Agent (QuickLessonPrepAgent)

## 职责描述

面向乡村教师的极速备课工具。根据学科、年级、课题和乡村情境，生成融入乡土元素的结构化教案。核心价值是将备课时间从数小时压缩到 10 秒以内，同时确保教案贴近农村学生的生活经验。

**源码位置**: `maitian_agent/agents/quick_lesson_prep.py`

## 输入输出接口

### run() 标准接口

**输入** (`Dict[str, Any]`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `subject` | str | 是 | 学科名称（如"数学"、"语文"） |
| `grade` | str | 是 | 年级（如"三年级"） |
| `topic` | str | 是 | 课题名称 |
| `rural_context` | str | 否 | 乡村特色情境描述，默认"结合乡村实际教学" |

**输出** (`Dict[str, Any]`):

```python
{
    "success": True,
    "result": "教案文本（含教学目标/重难点/教学过程/作业/板书设计）",
    "agent": "QuickLessonPrepAgent",
    "metadata": {}
}
```

### 公开方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `run_with_voice()` | `(audio_path: str) -> str` | 语音备课（当前 `NotImplementedError`） |
| `build_chain()` | `() -> Chain` | 构建 LangChain 备课链 |

## Prompt 模板说明

**模板名称**: `lesson_plan_template`

**变量占位符**:

| 变量 | 说明 |
|------|------|
| `{subject}` | 学科 |
| `{grade}` | 年级 |
| `{topic}` | 课题 |
| `{rural_context}` | 乡村特色情境 |

**设计意图**: 引导 LLM 扮演"经验丰富的乡村教师"角色，生成包含 6 个标准部分的教案（教学目标、教学重难点、教学准备、教学过程、作业布置、板书设计），并强制要求融入乡土元素、语言通俗易懂。

**LLM 参数**: `temperature=0.7`（较高，鼓励创造性生成）

## 依赖关系

### 当前依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| `ChatOpenAI` | 直接依赖 | DeepSeek-V2 API，直接在 `__init__` 中通过 `os.getenv()` 创建 |

### 未来计划依赖（已设计未集成）

| 依赖 | 接口 | 集成方式 | 用途 |
|------|------|---------|------|
| `BaseASR` | `transcribe(audio_path) -> str` | 构造函数注入 | 支持语音备课输入 |
| `KnowledgeBase` | `search(query, level, k) -> List` | 构造函数注入 | 检索已有教案作为参考素材 |
| `ConversationMemory` | `save_context(input, output)` | 构造函数注入 | 保存备课对话上下文 |
| `TeacherProfileManager` | `load_profile(teacher_id) -> TeacherProfile` | 构造函数注入 | 注入教师教学风格，个性化教案 |

## 性能要求

| 指标 | 目标值 | 验证值 |
|------|--------|--------|
| 端到端响应时长 | ≤ 10 秒 | ✅ 8 秒 |

## 已知限制

1. **`run_with_voice()` 未实现**: 语音备课功能抛出 `NotImplementedError`
2. **未集成 RAG**: 无法参考已有教案和教材内容，纯靠 LLM 生成
3. **未集成教师画像**: 无法根据教师个人风格个性化教案
4. **配置未集中**: 直接调用 `os.getenv()` + `load_dotenv()`，未使用 `Settings`
5. **无教案版本管理**: 生成的教案未持久化到知识库

## 与架构的集成点

```
规划层 RouterAgent
  意图 "quick_lesson_prep"
    ↓
执行层 QuickLessonPrepAgent.run(input_data)
  ├── [未来] 感知层: BaseASR.transcribe() — 语音输入转文本
  ├── [未来] RAG层: KnowledgeBase.search() — 检索参考教案
  ├── [未来] 记忆层: TeacherProfileManager.load_profile() — 教师风格注入
  ├── LangChain: lesson_plan_template | LLM | StrOutputParser
  └── [未来] 记忆层: ConversationMemory.save_context() — 保存对话
    ↓
返回 Dict{success, result, agent, metadata}
```
