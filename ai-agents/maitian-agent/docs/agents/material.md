# 具象化素材Agent (MaterialAgent)

## 职责描述

根据教学内容自动推荐具象化教学素材（科普视频、3D 模型、动画演示、图片素材）。核心价值是帮助乡村教师用生动素材弥补实验设备不足的困境，让抽象知识变得可视可感。

**源码位置**: `maitian_agent/agents/material_agent.py`

## 输入输出接口

### run() 标准接口

**输入** (`Dict[str, Any]`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `subject` | str | 是 | 学科名称 |
| `grade` | str | 是 | 年级 |
| `topic` | str | 是 | 课题 |
| `knowledge_points` | str | 否 | 知识点描述，默认"本课主要内容" |
| `rural_context` | str | 否 | 乡村情境描述，默认"乡村实际情境" |

**输出** (`Dict[str, Any]`):

```python
{
    "success": True,
    "result": "素材推荐文本（含4类素材建议）",
    "agent": "MaterialAgent",
    "metadata": {}
}
```

### 公开方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `recommend_materials()` | `(subject, grade, topic, knowledge_points, rural_context) -> str` | 推荐教学素材 |
| `search_material_library()` | `(keyword, material_type) -> List[Dict]` | 搜索素材库（当前 `NotImplementedError`） |
| `build_chain()` | `() -> Chain` | 构建 LangChain 素材推荐链 |

## Prompt 模板说明

**模板名称**: `material_template`

**变量占位符**:

| 变量 | 说明 |
|------|------|
| `{subject}` | 学科 |
| `{grade}` | 年级 |
| `{topic}` | 课题 |
| `{knowledge_points}` | 知识点 |
| `{rural_context}` | 乡村情境 |

**设计意图**: 引导 LLM 扮演"教育资源专家"角色，推荐 4 类素材：
1. 科普视频 — 简短有趣的知识讲解视频
2. 3D 模型 — 可视化展示抽象概念
3. 动画演示 — 生动有趣的动画说明
4. 图片素材 — 贴近乡村生活的实例图片

要求素材贴近乡村学生生活经验、趣味性强、简短精炼、标注来源和获取方式。

**LLM 参数**: `temperature=0.7`（较高，鼓励多样性和创造性）

## 依赖关系

### 当前依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| `ChatOpenAI` | 直接依赖 | DeepSeek-V2 API，通过 `os.getenv()` 创建 |

**MaterialAgent 是最独立的 Agent** — 当前无任何外部工具依赖，纯 LLM 生成。

### 未来计划依赖

| 依赖 | 接口 | 集成方式 | 用途 |
|------|------|---------|------|
| 外部素材库 API | `search(keyword, type) -> List[Material]` | 构造函数注入 | 真实素材库检索（替换 LLM 生成） |
| `ConversationMemory` | `save_context(input, output)` | 构造函数注入 | 保存推荐对话上下文 |

## 性能要求

无硬性 SLA 指标。素材推荐通常由其他 Agent 联动触发，非实时场景。

## 已知限制

1. **`search_material_library()` 未实现**: 素材库检索功能抛出 `NotImplementedError`
2. **LLM 生成非真实检索**: 推荐的素材为 LLM 幻觉生成，可能不存在或无法获取
3. **无素材来源验证**: 推荐内容未经过真实素材库验证
4. **配置未集中**: 直接调用 `os.getenv()` + `load_dotenv()`，未使用 `Settings`
5. **无联动触发机制**: 当前需手动调用，未实现与其他 Agent 的自动联动

## 与架构的集成点

```
规划层 RouterAgent
  意图 "material_recommend"
    ↓
执行层 MaterialAgent.run(input_data)
  ├── LangChain: material_template | LLM | StrOutputParser
  ├── [未来] 外部素材库: search_material_library() — 真实检索
  └── [未来] 记忆层: ConversationMemory.save_context()
    ↓
返回 Dict{success, result, agent, metadata}

联动场景:
  QuickLessonPrepAgent 生成教案 → 自动触发 MaterialAgent 推荐配套素材
```
