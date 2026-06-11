# 麦田智囊 Demo

> **[LEGACY] 早期演示版本** — 仅供概念验证，生产环境请使用 `maitian_agent/` 模块。

乡村教育 Agent 系统的交互式演示版本，基于 Streamlit 构建。此目录保留了项目初期的最小可运行代码，用于展示核心产品概念。

## ⚠️ Legacy 说明

本目录中的代码是项目早期的**原型实现**，与主项目 `maitian_agent/` 在架构上有显著差异：

| 维度 | demo/（本目录） | maitian_agent/（主项目） |
|------|-----------------|------------------------|
| 继承体系 | 无继承，独立裸类 | 统一继承 `BaseAgent(ABC)` |
| LLM 类型 | 直接导入 `ChatOpenAI` | 面向 `BaseChatModel` 抽象编程 |
| 调用模式 | 命令式 `format_messages()` + `invoke()` | LCEL 声明式管道 `prompt \| llm \| parser` |
| 依赖注入 | 不支持 | `AgentFactory` 统一注入 7 种依赖 |
| 配置管理 | `os.getenv()` 散落各处 | Pydantic `Settings` 统一管理 |
| RAG 集成 | 无 | `KnowledgeBase` + BM25 混合检索 |
| 对话记忆 | 无 | `ConversationMemory` + 文件锁并发安全 |
| 教师画像 | 无 | `TeacherProfileManager` |
| 接口规范 | 位置参数，返回 `str` | 统一 `Dict → Dict` 输入输出 |
| CI 覆盖 | 不在 CI 范围内 | 346 项测试，81% 覆盖率 |

## 功能演示

### 1. 乡村专属极速备课 ✅
- **输入**：学科、年级、课题、乡村特色情境
- **输出**：详细的乡土化教案
- **特点**：10 秒生成，结合乡村实际案例

### 2. 老教师经验一键传承 ✅
- **输入**：手写教案照片
- **输出**：OCR 识别结果 + 结构化教案
- **特点**：EasyOCR 识别，大模型结构化处理

### 3. 课堂实时伴教 ✅（Demo 基础版）
- 练习题生成（无 RAG 检索）

### 4–5. 素材推荐 / 教研纪要
- 主项目已实现，Demo 中标注为"开发中"

## 快速开始

### 安装依赖

```bash
pip install streamlit langchain-openai langchain-core python-dotenv easyocr
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 API 密钥
```

### 启动演示

```bash
cd demo
streamlit run app.py
```

访问 http://localhost:8501 查看演示。

## 目录结构

```
demo/
├── app.py                          # [LEGACY] Streamlit 主应用
├── agents/
│   ├── __init__.py
│   ├── quick_lesson_prep.py        # [LEGACY] 极速备课 Agent
│   ├── wisdom_transfer.py           # [LEGACY] 智慧传承 Agent
│   └── classroom_companion.py       # [LEGACY] 课堂伴教 Agent
├── .env.example                     # 环境变量示例
└── README.md                        # 本文件
```

## 主项目架构

完整项目框架请参考 `maitian_agent/` 模块和 `docs/reports/status-final.md` 架构状态报告：

- **四层架构**：感知层（OCR/ASR）→ RAG 层 → 记忆层 → 执行层（6 Agent）
- **AgentFactory**：统一依赖注入，7 种依赖 100% 构造函数注入
- **RAG 系统**：BM25 + 向量双路检索，RRF 加权融合
- **对话记忆**：文件锁并发安全，JSON 持久化
- **CI 流水线**：GitHub Actions（ruff + pytest + mypy）
- **测试覆盖**：346 项测试，81% 覆盖率

## License

© 2026 麦田智囊团队
