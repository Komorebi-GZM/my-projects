# 课堂实时伴教Agent (ClassroomCompanionAgent)

## 职责描述

课堂实时伴教工具，支持两种核心能力：快速生成练习题和检索经典题目。核心价值是在课堂上即时响应教学需求，帮助教师在 3 秒内获得适合乡村学生认知水平的练习题。

**源码位置**: `maitian_agent/agents/classroom_companion.py`

## 输入输出接口

### run() 标准接口

**输入** (`Dict[str, Any]`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `action` | str | 是 | 操作类型：`"quiz"`（生成练习题）或 `"retrieve"`（检索经典题） |
| `subject` | str | 是 | 学科名称 |
| `grade` | str | 是 | 年级 |
| `topic` | str | 是 | 课题 |
| `knowledge_points` | str | 否 | 知识点描述，默认"本课主要内容" |
| `question_count` | int | 否 | 题目数量，默认 5 |
| `question_types` | str | 否 | 题目类型，默认"选择题、填空题" |

**输出** (`Dict[str, Any]`):

```python
{
    "success": True,
    "result": "练习题/经典题文本",
    "agent": "ClassroomCompanionAgent",
    "metadata": {}
}
```

错误情况（未知 action）:
```python
{"success": False, "error": "未知操作: {action}"}
```

### 公开方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `generate_quiz()` | `(subject, grade, topic, knowledge_points, question_count, question_types) -> str` | 生成练习题 |
| `retrieve_classic_questions()` | `(subject, grade, topic, knowledge_points) -> str` | 检索经典题目 |
| `build_chain()` | `(chain_type: str) -> Chain` | 构建指定类型的链（`"quiz"` 或 `"retrieval"`） |

## Prompt 模板说明

### quiz_template（练习题生成）

**变量占位符**: `{subject}`, `{grade}`, `{topic}`, `{knowledge_points}`, `{question_count}`, `{question_types}`

**设计意图**: 引导 LLM 扮演"专业的乡村教师"角色，生成紧扣知识点、难度适中、融入乡土元素的练习题。

### retrieval_template（经典题检索）

**变量占位符**: `{subject}`, `{grade}`, `{topic}`, `{knowledge_points}`

**设计意图**: 引导 LLM 检索与教学内容相关的经典题目和教学资源。

**⚠️ 注意**: `retrieval_template` 当前为伪检索——直接让 LLM 生成"检索结果"而非调用 RAG 知识库。这是已知的架构问题，待集成 `KnowledgeBase` 后修复。

**LLM 参数**: `temperature=0.5`（中等，平衡准确性和多样性）

## 依赖关系

### 当前依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| `ChatOpenAI` | 直接依赖 | DeepSeek-V2 API，通过 `os.getenv()` 创建 |

### 未来计划依赖（已设计未集成）

| 依赖 | 接口 | 集成方式 | 用途 |
|------|------|---------|------|
| `KnowledgeBase` | `search(query, level, k) -> List` | 构造函数注入 | 真实检索经典题目（替换伪检索） |
| `ConversationMemory` | `save_context(input, output)` | 构造函数注入 | 保存出题对话上下文 |

## 性能要求

| 指标 | 目标值 | 验证值 |
|------|--------|--------|
| 练习题生成时长 | ≤ 3 秒 | ✅ 2 秒 |

## 已知限制

1. **伪检索问题**: `retrieve_classic_questions()` 当前让 LLM 直接生成"检索结果"，未调用 RAG 知识库，返回内容不可靠
2. **未集成 RAG**: 无法从已有题库中检索真实经典题目
3. **配置未集中**: 直接调用 `os.getenv()` + `load_dotenv()`，未使用 `Settings`
4. **无题目持久化**: 生成的练习题未保存到知识库供后续复用

## 与架构的集成点

```
规划层 RouterAgent
  意图 "classroom_companion"
    ↓
执行层 ClassroomCompanionAgent.run(input_data)
  ├── action="quiz" → generate_quiz() → quiz_template | LLM
  ├── action="retrieve" → retrieve_classic_questions()
  │   └── [当前] retrieval_template | LLM（伪检索）
  │   └── [未来] KnowledgeBase.search()（真实检索）
  ├── [未来] 记忆层: ConversationMemory.save_context()
  └── [未来] RAG层: 生成题目入库
    ↓
返回 Dict{success, result, agent, metadata}
```
