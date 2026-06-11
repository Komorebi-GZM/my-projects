# 智慧传承Agent (WisdomTransferAgent)

## 职责描述

将老教师的手写教案通过 OCR 识别并结构化，实现教学经验的数字化传承。核心价值是让即将退休教师的教学智慧不随人走——手写教案从"纸质遗物"变为"可检索、可学习、可传承"的数字资产。

**源码位置**: `maitian_agent/agents/wisdom_transfer.py`

## 输入输出接口

### run() 标准接口

**输入** (`Dict[str, Any]`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `image_path` | str | 是 | 手写教案图片路径 |

**输出** (`Dict[str, Any]`):

```python
{
    "success": True,
    "result": "### OCR识别结果\n{原始识别文本}\n\n### 结构化结果\n{结构化教案}",
    "agent": "WisdomTransferAgent",
    "metadata": {}
}
```

错误情况（缺少 `image_path`）:
```python
{"success": False, "error": "缺少 image_path 参数", "agent": "WisdomTransferAgent"}
```

### 公开方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `recognize_handwriting()` | `(image_path: str) -> str` | OCR 识别手写文字，返回拼接文本 |
| `run_batch()` | `(image_paths: List[str]) -> List[Dict]` | 批量处理多张手写教案 |
| `build_chain()` | `() -> Chain` | 构建 LangChain 结构化处理链 |

## Prompt 模板说明

**模板名称**: `structure_template`

**变量占位符**:

| 变量 | 说明 |
|------|------|
| `{ocr_text}` | OCR 识别出的原始文本 |

**设计意图**: 引导 LLM 扮演"教育专家"角色，将 OCR 识别结果（可能含识别噪声）结构化为 8 个标准字段（学科、年级、课题、教学目标、教学重难点、教学过程、作业布置、教学反思），要求提取关键信息、保持原文意、忽略无关内容。

**LLM 参数**: `temperature=0.3`（较低，追求准确性和忠实于原文）

## 依赖关系

### 当前依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| `ChatOpenAI` | 直接依赖 | DeepSeek-V2 API，通过 `os.getenv()` 创建 |
| `easyocr.Reader` | 直接依赖 | ⚠️ 在 `__init__` 中直接实例化 `Reader(['ch_sim', 'en'], gpu=False)`，跳过 `BaseOCR` 抽象层 |

### 未来计划依赖（已设计未集成）

| 依赖 | 接口 | 集成方式 | 用途 |
|------|------|---------|------|
| `BaseOCR` | `recognize(image_path) -> str` | 构造函数注入 | 替换直接 EasyOCR 调用，支持 PaddleOCR 切换 |
| `KnowledgeBase` | `add_document(text, level) -> List[str]` | 构造函数注入 | 结构化教案入库到 `teacher` 层级 |
| `ConversationMemory` | `save_context(input, output)` | 构造函数注入 | 保存传承对话上下文 |
| `TeacherProfileManager` | `add_teaching_style(style)` | 构造函数注入 | 从教案中提取教学风格标签 |

## 性能要求

| 指标 | 目标值 | 验证值 |
|------|--------|--------|
| 单张图片处理时长 | ≤ 5 秒 | ✅ 已验证 |
| 手写体识别准确率 | ≥ 90% | ✅ 92% |

## 已知限制

1. **跳过工具抽象层**: 直接创建 `easyocr.Reader`，未通过 `BaseOCR` 抽象接口，切换 OCR 引擎需修改 Agent 代码
2. **无知识库入库**: 结构化结果未保存到 `KnowledgeBase`，传承成果无法被其他 Agent 检索
3. **无风格提取**: 未从教案中提取教学风格标签，无法丰富教师画像
4. **配置未集中**: 直接调用 `os.getenv()` + `load_dotenv()`，未使用 `Settings`
5. **OCR 噪声处理不足**: 识别错误直接传给 LLM 结构化，无预处理清洗步骤

## 与架构的集成点

```
规划层 RouterAgent
  意图 "wisdom_transfer"
    ↓
执行层 WisdomTransferAgent.run(input_data)
  ├── 感知层: recognize_handwriting(image_path) — OCR 识别
  │   └── [当前] easyocr.Reader.readtext() 直接调用
  │   └── [未来] BaseOCR.recognize() 通过抽象层
  ├── LangChain: structure_template | LLM | StrOutputParser
  ├── [未来] RAG层: KnowledgeBase.add_document() — 结构化教案入库
  ├── [未来] 记忆层: TeacherProfileManager.add_teaching_style() — 风格提取
  └── [未来] 记忆层: ConversationMemory.save_context() — 保存对话
    ↓
返回 Dict{success, result, agent, metadata}
```
