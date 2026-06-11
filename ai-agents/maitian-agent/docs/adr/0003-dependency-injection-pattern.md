# [0003] 依赖注入与模块边界策略

- 状态: 接受
- 日期: 2026-05-03

## 背景

当前代码各层（感知/规划/执行/记忆）虽然目录划分清晰，但存在跨层直接依赖问题：

```
WisdomTransferAgent
  ├── 直接实例化 easyocr.Reader  ← 跳过 tools.ocr 抽象层
  ├── 调用 os.getenv()           ← 跳过 config.settings
  └── save_to_knowledge_base()   ← NotImplementedError
```

此外，工具层存在 `BaseOCR`/`BaseASR` 抽象，但 Agent 层并没有通过这些抽象来依赖。

## 决策

### 1. 层间依赖规则

```
执行层 (Agent)  → 可依赖: 工具抽象层、RAG抽象层、记忆抽象层、配置层
工具层          → 不可依赖: 执行层、记忆层
RAG层           → 不可依赖: 执行层、工具层
记忆层          → 不可依赖: 执行层
配置层          → 不可依赖: 任何业务层
```

### 2. 注入方式

所有跨层依赖通过构造函数注入，不在内部 `import` 或实例化：

```python
# 正确
class WisdomTransferAgent(BaseAgent):
    def __init__(self, ocr_processor: Optional[BaseOCR] = None, ...):
        self.ocr = ocr_processor or OCRProcessor.create(...)

# 错误 — 跳过抽象层
class WisdomTransferAgent(BaseAgent):
    def __init__(self, ...):
        from easyocr import Reader
        self.ocr = Reader(['ch_sim', 'en'])
```

### 3. 配置获取规则

- 所有模块从 `BaseAgent.settings` 获取配置
- `BaseAgent.__init__()` 统一接收 `settings` 参数
- 禁止直接调用 `os.getenv()`（单元测试中除外）
- 配置只在 `api/routes.py` 和 `cli.py` 等入口处加载一次

### 4. 各 Agent 的依赖矩阵

| Agent | OCR | ASR | RAG | 对话记忆 | 教师画像 |
|-------|-----|-----|-----|---------|---------|
| QuickLessonPrepAgent | - | ✅ | ✅ | ✅ | ✅ |
| WisdomTransferAgent | ✅ | - | ✅ | ✅ | ✅ |
| ClassroomCompanionAgent | - | - | ✅ | ✅ | - |
| MaterialAgent | - | - | - | ✅ | - |
| MeetingNotesAgent | - | ✅ | ✅ | ✅ | - |

### 5. 三层 RAG 归属

`KnowledgeBase` 的三个层级（universal/school/teacher）统一通过 `KnowledgeBase` 接口访问，Agent 不直接访问向量存储：

```python
# 检索示例（Agent 内）
results = self.knowledge_base.search(query, level=KnowledgeLevel.UNIVERSAL)

# 入库示例
self.knowledge_base.add_document(text, level=KnowledgeLevel.TEACHER, metadata={...})
```

## 理由

- **层间解耦**：WisdomTransferAgent 不再直接依赖 EasyOCR，可无缝切换 PaddleOCR
- **可测试性**：通过构造函数注入 mock，不需要猴子补丁（monkey-patching）
- **配置中心化**：一处修改，全局生效，避免 Agent 间配置不一致
- **ABC 抽象层复用**：tools/ 的 `BaseOCR`/`BaseASR` 抽象设计合理，应被利用

## 影响

- 正向：模块边界清晰，依赖关系可追踪
- 正向：AgentFactory 集中管理创建逻辑，消除重复
- 正向：新增 Agent 时明确需要哪些依赖
- 代价：Agent 构造函数参数增多（通过 AgentFactory 减轻）
- 代价：现有直接调用的测试需要重构为注入模式

## 备选方案

1. **属性注入（setter）**：创建空 Agent 后 set 依赖——可能遗漏依赖，运行时 NPE
2. **接口注入**：Agent 实现特定接口——Java 风格，Python 中过于繁琐
