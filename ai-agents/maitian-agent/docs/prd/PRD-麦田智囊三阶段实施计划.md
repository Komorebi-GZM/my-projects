# PRD: 麦田智囊 — 乡村教育 Agent 系统三阶段实施计划

## Problem Statement

麦田智囊目前处于 Demo 原型与主项目框架共存阶段。Demo 有 6 个页面但 3 个为占位状态（课堂伴教、素材推荐、教研纪要）；主项目代码框架完整（6 个 Agent + RAG + 记忆 + 工具 + API + 前端）但模块间集成断裂——RAG、记忆、工具层代码完整但未被 Agent 实际调用；Agent `run()` 接口签名与 BaseAgent 基类不统一，导致 router 和工厂模式无法正常工作。

核心问题：模块各自完整但整体割裂，无法端到端演示完整场景。

核心目标：将麦田智囊从碎片化的代码片段状态，推进到可完整演示、模块集成的生产级系统。

## Solution

通过三阶段递进实施：

1. **第一阶段 — Demo 完善与部署**：补齐 Demo 的 3 个占位页面、Docker 部署、冒烟测试
2. **第二阶段 — 主项目核心集成**：统一 Agent 接口、集成配置/工具/RAG/记忆层、AgentFactory 工厂模式、结构化日志
3. **第三阶段 — 高级功能优化**：ASR 完整集成、BM25 混合检索、教师风格匹配、流式响应、教案导出、Swagger 文档

## User Stories

1. 作为一名乡村教师，我可以通过极速备课功能在 10 秒内生成乡土化教案，以减少备课时间
2. 作为一名乡村教师，我可以上传手写教案照片并自动识别结构化，以传承老教师经验
3. 作为一名乡村教师，我可以在课堂上快速生成练习题和检索经典题，以提升教学效率
4. 作为一名乡村教师，我可以获得与教学内容匹配的视频/3D/图片素材推荐，以丰富课堂教学
5. 作为一名乡村教师，我可以将教研会议记录自动转为结构化报告，以规范教研管理
6. 作为一位学校管理者，我可以查看教师的备课记录和教学风格画像，以了解教学情况
7. 作为一名开发者，我可以通过统一的 API 接口调用所有 Agent 功能，以简化集成开发
8. 作为一名开发者，我可以通过 AgentFactory 一站式创建配置好的 Agent，以消除重复初始化代码
9. 作为一名开发者，Agent 应该能够检索和更新知识库，以支持自进化 RAG 能力
10. 作为一名开发者，Agent 应该维护教师专属画像，以支持个性化输出
11. 作为一名运维人员，我可以通过 Docker 一键部署系统，以降低部署成本
12. 作为一名运维人员，我可以通过结构化日志追踪每个请求的执行链路，以便快速排查问题

## 四层 Agent 整体架构

### 架构概览

```
感知层 (Perception)      规划层 (Planning)      执行层 (Execution)       记忆层 (Memory)
┌─────────────┐        ┌──────────────┐      ┌──────────────────┐     ┌──────────────────┐
│ ASR 语音识别 │ ───→   │ LangChain    │ ──→  │ QuickLessonPrep  │ ─→  │ 对话记忆          │
│ (Whisper)   │        │ 意图路由     │       │ WisdomTransfer   │     │ (Conversation)   │
├─────────────┤        │ (RouterAgent)│       │ ClassroomCompan. │     ├──────────────────┤
│ OCR 手写识别 │ ───→   └──────────────┘      │ MaterialAgent    │ ─→  │ 教师画像          │
│ (EasyOCR)   │                               │ MeetingNotes     │     │ (TeacherProfile) │
└─────────────┘                               └────────┬─────────┘     └──────────────────┘
                                                        │
                                                ┌───────┴───────┐
                                                │  RAG 知识库    │
                                                │  (Chroma+BGE)  │
                                                └───────────────┘
```

### 核心数据流

```
用户输入 → 感知层(可选) → 规划层路由 → 执行层(RAG检索 + 记忆注入) → 生成结果 → 记忆层自动保存
```

### 模块职责

| 模块 | 职责 | 关键文件 |
|------|------|---------|
| `maitian_agent.agents` | 6 个 Agent + BaseAgent + Router + Factory | base.py, factory.py, quick_lesson_prep.py, wisdom_transfer.py, classroom_companion.py, material_agent.py, meeting_notes.py, router.py |
| `maitian_agent.rag` | Chroma 向量检索 + 知识库管理 | knowledge_base.py, vectorstore.py, embeddings.py |
| `maitian_agent.memory` | 对话记忆 + 教师画像 | conversation_memory.py, teacher_profile.py |
| `maitian_agent.tools` | OCR/ASR/File 工具封装 | ocr.py, asr.py, file.py |
| `maitian_agent.api` | FastAPI REST 接口 | routes.py |
| `maitian_agent.frontend` | Streamlit Web 界面 | streamlit_app.py |
| `maitian_agent.config` | pydantic-settings 配置管理 | settings.py |
| `maitian_agent.utils` | 工具函数（logger 等） | logger.py |

## Implementation Decisions

### 第一阶段：Demo 完善与部署 (v0.1.0-demo)

**目标**：补齐 Demo 到完整 6 页面可演示状态，支持 Docker 部署。

| 任务 | 模块 | 主要变更 |
|------|------|---------|
| Task 1: 课堂伴教 Agent | demo/agents | 新建 ClassroomCompanionAgent（练习题生成 + 经典题推荐） |
| Task 2: 素材推荐 Agent | demo/agents | 新建 MaterialAgent（视频/3D/图片/教具推荐） |
| Task 3: 教研纪要 Agent | demo/agents | 新建 MeetingNotesAgent（会议记录 → 结构化报告） |
| Task 4: Docker 部署 | demo/ | Dockerfile + docker-compose + 启动脚本 |
| Task 5: 冒烟测试 | tests/ | 全流程导入/实例化验证 |
| Task 5M: CHANGELOG | CHANGELOG.md | 初始化 v0.1.0-demo |

**验收标准**：
- [ ] 3 个新 Agent 可通过 pytest 单元测试
- [ ] Demo Streamlit 应用 6 页面均可正常工作
- [ ] `docker-compose up` 一键启动
- [ ] 冒烟测试全部 PASS

### 第二阶段：主项目核心集成 (v0.2.0)

**目标**：统一 Agent 接口 → 集成配置/工具/RAG/记忆 → AgentFactory → Docker 部署 → 结构化日志。

| 任务 | 模块 | 主要变更 |
|------|------|---------|
| Task 6: 统一 Agent 接口 | agents/ + api/ + frontend + cli | 修复 run() 签名 Dict→Dict |
| Task 7: 集成配置管理 | config/ + agents/ + api/ | pydantic-settings 统一管理 |
| Task 8: 集成工具层 | tools/ + agents/ + api/ | OCR/ASR 注入 Agent |
| Task 9: 集成 RAG | rag/ + agents/ + api/ | 知识库检索 + 自动入库 |
| Task 10: 集成记忆 | memory/ + agents/ + api/ | 对话记忆 + 教师画像 |
| Task 11: AgentFactory | agents/factory.py | 统一依赖注入工厂 |
| Task 12: Docker 部署 | docker/ | 主项目 Dockerfile + docker-compose |
| Task 12M: 结构化日志 | utils/logger.py | JSON 日志 + request_id 追踪 |

**执行依赖**：Task 6 → Task 7 → Task 11 → Task 8/9/10(并行) → Task 12 → Task 12M

**验收标准**：
- [ ] 所有 Agent `run()` 签名与 BaseAgent 一致
- [ ] 配置从 pydantic-settings 统一获取，无 `os.getenv()` 调用
- [ ] OCR/ASR 工具类可注入 Agent
- [ ] Agent 可检索知识库并自动入库
- [ ] 对话记忆和教师画像在 Agent 执行中自动维护
- [ ] AgentFactory 一站式创建所有 Agent
- [ ] 主项目可通过 Docker 部署
- [ ] JSON 结构化日志记录每个请求

### 第三阶段：高级功能优化 (v0.3.0)

**目标**：语音完整集成、混合检索、教师风格匹配、流式响应、教案导出、Swagger 文档。

| 任务 | 模块 | 主要变更 |
|------|------|---------|
| Task 13: Whisper ASR 完整集成 | tools/ + agents/ + frontend | 音频上传→转写→生成完整流程 |
| Task 14: BM25 混合检索 | rag/knowledge_base.py | 向量 + BM25 RRF 融合 |
| Task 15: 教师风格匹配 | memory/ + agents/ | 风格向量存储+相似度检索 |
| Task 16: 文件上传 API | api/ + tools/ | 统一上传 + 批量上传 |
| Task 17: 流式响应 | agents/ + api/ + frontend | SSE + st.write_stream |
| Task 18: 教案导出 | tools/ + api/ + frontend | Markdown + Word 导出 |
| Task 18M: Swagger 文档 | api/routes.py | 完整 OpenAPI/response_model |

**验收标准**：
- [ ] 音频文件上传→转写→生成报告完整流程可工作
- [ ] BM25 + 向量 RRF 融合检索结果优于单路检索
- [ ] 风格向量匹配可找到相似教师并推荐教案
- [ ] 文件上传支持类型验证和批量上传
- [ ] 流式响应在 Streamlit 中逐步渲染
- [ ] 教案可导出为 Markdown 和 Word 格式
- [ ] 所有 API 端点在 Swagger UI 中有完整文档

## 技术约束

1. **Python 版本**：统一使用 Python 3.11+
2. **大模型**：DeepSeek-V2（OpenAI 兼容接口），通过 `init_chat_model()` 统一管理
3. **向量数据库**：Chroma（轻量级嵌入式），生产环境可升级 Milvus
4. **OCR**：EasyOCR（已验证），PaddleOCR 备选
5. **ASR**：Whisper API（OpenAI）
6. **Demo 定位**：保持独立简洁，不引入 RAG/记忆 等复杂依赖
7. **主项目定位**：承担完整功能，通过 AgentFactory 管理依赖注入
8. **外部 API 测试一律 mock**：确保测试可离线运行、快速稳定
9. **版本管理**：每阶段完成更新 CHANGELOG.md

## Testing Decisions

### 测试原则
- 外部 API 调用一律 mock（大模型、OCR、ASR）
- Agent 内部逻辑（prompt 构建、参数处理）真实执行
- RAG 使用真实 Chroma + `tmp_path`，不 mock
- 每个测试独立，使用 pytest fixture 隔离
- 验证外部行为，不验证内部实现细节

### Mock 策略

| 依赖 | Mock 方式 |
|------|----------|
| ChatOpenAI / 大模型 | `unittest.mock.patch` 替换 `invoke()` |
| EasyOCR | `unittest.mock.patch` 替换 `readtext()` |
| Whisper ASR | `unittest.mock.patch` 替换 `transcriptions.create()` |
| Chroma | 真实 Chroma + `tmp_path` |
| 文件系统 | `tmp_path` |

### 测试覆盖模块

- 所有 Agent 单元测试（含正常路径、错误路径、边界条件）
- API 端点测试（mock Agent 层 + TestClient）
- RAG 集成测试（知识库 CRUD + 检索）
- 记忆系统测试（对话保存/查询、教师画像 CRUD）
- 配置管理测试
- 日志功能测试
- 全流程冒烟测试

## Out of Scope

- 用户认证与权限管理（生产版本支持 API Key 认证）
- 多租户与数据隔离
- 性能基准测试与压力测试
- 自动化 CI/CD 流水线
- 移动端适配
- 离线/低网络版本
- RAG 知识库的数据回滚与版本管理

## Further Notes

- 第一阶段（Demo）和第二、三阶段（主项目）代码路径分叉，Demo 保持独立
- 前置任务 Task 0（LangChain 0.2 → 1.2 升级）应在第二阶段开始前完成
- 每阶段结束时需更新 CONTEXT.md 和 ADR 记录
- 建议在每个 Task 完成时执行 `pytest` 确保不引入回归

## 交付物清单

### 代码交付物
- [ ] Demo 完整 6 Agent 实现 + Streamlit 6 页面
- [ ] Demo Dockerfile + docker-compose.yml
- [ ] 主项目 6 Agent 接口统一实现
- [ ] AgentFactory 工厂类
- [ ] RAG 知识库集成代码（含 BM25 混合检索）
- [ ] 记忆系统集成代码（含教师风格匹配）
- [ ] 工具层集成代码（OCR + ASR）
- [ ] FastAPI 完整路由（含流式/文件上传/导出）
- [ ] Streamlit 主项目前端完整页面
- [ ] 结构化日志封装
- [ ] Docker 主项目部署配置

### 测试交付物
- [ ] Demo 冒烟测试
- [ ] Agent 接口一致性测试
- [ ] 配置集成测试
- [ ] RAG 集成测试
- [ ] 记忆系统集成测试
- [ ] 工具层集成测试
- [ ] API 端点测试（含 mock）
- [ ] 日志功能测试

### 文档交付物
- [ ] CHANGELOG.md (v0.1.0 / v0.2.0 / v0.3.0)
- [ ] CONTEXT.md 持续更新
- [ ] ADR 架构决策记录
- [ ] Swagger / OpenAPI 接口文档
- [ ] Docker .env.example
