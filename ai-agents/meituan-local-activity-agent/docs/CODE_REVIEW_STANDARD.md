# 本地生活短时活动规划 Agent — 代码审查标准与流程

> **版本**：V1.0
> **适用范围**：美团 Hackathon MVP 项目全体代码
> **技术栈**：Python 3.12 / LangGraph 1.0 / FastAPI / Streamlit

---

## 一、审查总览

### 1.1 代码审查目标

| 目标 | 说明 |
|------|------|
| **防止缺陷上线** | 拦截安全漏洞、数据丢失、逻辑错误 |
| **统一质量基线** | 确保所有贡献者遵循相同标准 |
| **知识传播** | 通过审查交流，提升团队整体水平 |
| **架构一致性** | 保证代码符合 DEV_GUIDE_MVP.md 设计规范 |

### 1.2 审查范围与优先级

| 层级 | 目录/文件 | 审查严格度 | 说明 |
|------|----------|-----------|------|
| **核心** | `graph/` 状态机 | 最高 | 状态流转、条件路由是系统命脉 |
| **核心** | `agents/` Agent 实现 | 高 | LLM 调用、Prompt 集成 |
| **核心** | `agents/llm_client.py` | 最高 | 统一 LLM 入口，所有调用经过此文件 |
| **重要** | `tools/mock_api.py` | 中高 | Mock 数据质量影响测试和演示 |
| **重要** | `middleware/trace.py` | 中 | 可观测性基础设施 |
| **重要** | `schemas/` 数据模型 | 中 | 类型定义影响全链路 |
| **一般** | `frontend/` Streamlit | 中 | UI 交互与展示层 |
| **一般** | `config.py` | 低 | 配置管理 |

---

## 二、审查流程

### 2.1 提交前自查（作者责任，5 分钟）

在请求审查前，作者**必须**完成以下检查：

```
提交前自查 Checklist
─────────────────────────────────────────────
[x] conda activate py312
[x] cd backend
[x] python -m pytest tests/ -v
[x] 所有测试通过（不允许带失败测试提交）
[x] 无 import 错误（python -c "import graph.state; import agents.llm_client"）
[x] 新增/修改的函数有类型注解
[x] 新增的公共函数有 docstring
[x] 无硬编码的 API Key 或敏感信息
[x] 符合命名规范（PEP8: snake_case 文件名/函数名，CamelCase 类名）
[x] structlog 日志包含 trace_id（涉及 LLM/Mock API 调用时）
```

### 2.2 审查流程图

```
开发者完成代码 → 运行测试 + 提交前自查
                    ↓
           创建审查请求（PR / 代码片段）
                    ↓
           ┌────────────────────────┐
           │  自动化检查（linter）   │  ← 未来接入 ruff/mypy
           └────────────┬───────────┘
                        ↓
                  人工代码审查
                        ↓
           ┌────────────┴───────────┐
           │ 有 Blocker 问题？       │
           └────────────┬───────────┘
                 是 ↙        ↘ 否
           返回修改        标记通过
                ↓                ↓
           作者修复        合并代码
                ↓
           再次提交审查（从自动化检查开始）
```

### 2.3 审查响应时间

| 情况 | 响应时限 | 说明 |
|------|---------|------|
| **Blocker 问题** | 2 小时内 | 安全漏洞、数据丢失等，需立即沟通 |
| **常规审查** | 半天内 | Hackathon 期间可适当缩短 |
| **紧急修复** | 1 小时内 | Demo 前的 P0 bug |

### 2.4 审查轮次控制

| 原则 | 规则 |
|------|------|
| **一次提完整** | 不要"分批提交"，一次性提供完整可审查的代码 |
| **最多 3 轮** | 超过 3 轮未通过的审查，改为面对面讨论 |
| **Blocker 优先** | 每轮先处理 Blocker，Suggestion 可累积到最终轮 |

---

## 三、审查标准（三级分类）

### 3.1 🔴 Blocker — 必须修复，阻塞合并

#### B1: 安全漏洞

| 编号 | 检查项 | 示例 |
|------|--------|------|
| B1.1 | **eval() / exec() 使用** | `llm_client.py:65` — `eval(response)` 解析 LLM 输出，存在任意代码执行风险 |
| B1.2 | API Key / 密钥泄露 | 硬编码 `LLM_API_KEY`，日志中打印敏感信息 |
| B1.3 | 输入注入 | 用户输入未清洗直接拼入 Prompt（Prompt Injection） |

**当前项目 B1 风险点**：
- `llm_client.py` 的 `eval(response)` 是已知技术债务（PRD 约定 Python Dict 输出），审查时需确认：
  - 是否有 fallback（当前有 `json.loads` fallback ✅）
  - 是否对 response 做了长度/内容限制
  - 是否在隔离环境运行（当前不是，需关注）

#### B2: 数据丢失 / 逻辑错误

| 编号 | 检查项 | 示例 |
|------|--------|------|
| B2.1 | 状态丢失 | LangGraph Node 返回的增量更新遗漏关键字段 |
| B2.2 | 循环条件错误 | `edges.py` 路由函数导致无限循环 |
| B2.3 | 重试上限失效 | `replan_count` 递增逻辑有缺陷 |
| B2.4 | 竞态条件 | `ThreadPoolExecutor` 并行写共享状态 |

**当前项目 B2 关注点**：
- `graph/nodes.py:100-117` — `replan()` 函数 `exclude_options=[]` 空列表，未实际排除被否决 POI
- `orchestrator.py:56-64` — 加权聚合循环中，如果同一 Agent 在 R1 和 R2 都评分，权重会被**双重计算**
- `edges.py:4-13` — `safety_router` 只检查最新一轮 reviews，可能遗漏 R1 的否决

#### B3: 异常处理缺失

| 编号 | 检查项 | 示例 |
|------|--------|------|
| B3.1 | 关键路径无 try-catch | LLM 调用失败未捕获，导致状态机崩溃 |
| B3.2 | 异常信息丢失 | except 块吞掉异常不记录 |
| B3.3 | Fallback 值不合理 | Mock 失败返回 None 导致后续 KeyError |

**当前项目 B3 关注点**：
- `graph/nodes.py` 所有 Node 函数**无 try-except**（`parse_intent` 等会直接抛异常，导致 LangGraph 崩溃）
- `orchestrator.py:79-125` — `run_planning_flow` 无任何错误处理

#### B4: 类型 / 接口不匹配

| 编号 | 检查项 | 示例 |
|------|--------|------|
| B4.1 | TypedDict 字段与实际赋值不一致 | `BrainstormState` 定义 vs Node 返回值 |
| B4.2 | Agent 返回值格式不匹配 | `brainstorm_engine` 返回的 reviews 结构与 `aggregate_reviews` 期望不同 |
| B4.3 | Prompt 输出格式偏移 | LLM 输出与 `AgentReview` 结构不匹配 |

### 3.2 🟡 Suggestion — 应该修复，提升质量

#### S1: 可维护性

| 编号 | 检查项 | 修改建议 |
|------|--------|---------|
| S1.1 | **延迟导入** | `nodes.py` 中每个函数顶部都有 `from agents.xxx import Xxx`，应集中到文件顶部 |
| S1.2 | **重复代码** | 4 个 brainstorm Agent 结构完全相同，应抽取基类 |
| S1.3 | **魔法数字** | `replan_count >= 2` 应定义为常量 `MAX_REPLAN_ATTEMPTS = 2` |
| S1.4 | **日志缺失** | `nodes.py` 的 Node 函数无 structlog 日志（DEV_GUIDE 要求每个 Node 带日志） |
| S1.5 | **config.py 双重存在** | `backend/config.py` 和 `backend/logging_config.py` 职责重叠 |

#### S2: 性能

| 编号 | 检查项 | 修改建议 |
|------|--------|---------|
| S2.1 | LLM 串行调用 | 头脑风暴 4 Agent 应并行（brainstorm_engine 有 ThreadPoolExecutor ✅） |
| S2.2 | Agent 实例化 | `nodes.py` 每个 Node 都 `XxxAgent()` 新建实例，考虑复用或单例 |
| S2.3 | Mock 数据硬编码 | `_generate_mock_pois` 应抽取为配置文件或 fixture |

#### S3: 测试

| 编号 | 检查项 | 修改建议 |
|------|--------|---------|
| S3.1 | 核心路径无测试 | `graph/edges.py` 路由函数无单元测试 |
| S3.2 | 边界值缺失 | `aggregate_reviews` 未测试空 candidates、全否决场景 |
| S3.3 | Mock 测试不稳定 | `test_mock_api.py` 依赖 `random.random()`，应使用 `random.seed()` |
| S3.4 | 测试环境隔离 | 测试修改 `os.environ` 但未在 `teardown` 中恢复 |

#### S4: 文档

| 编号 | 检查项 | 修改建议 |
|------|--------|---------|
| S4.1 | 复杂函数无 docstring | `aggregate_reviews` 逻辑复杂，缺少算法说明 |
| S4.2 | Prompt 文件无注释 | `prompts/*.txt` 缺少输出格式说明 |
| S4.3 | `__init__.py` 为空 | 应导出公共接口 |

### 3.3 💭 Nit — 建议改进，不阻塞

| 编号 | 检查项 |
|------|--------|
| N1 | `trace_id: str = None` 应改为 `Optional[str] = None` |
| N2 | `TripState` 枚举有 `BOOKING` 但代码流程中未使用 |
| N3 | `mock_api.py` 中 `_log_mock_call` 参数顺序可改为 `trace_id` 在前 |
| N4 | `_generate_mock_reviews` 返回固定数据，`poi_name` 参数未使用 |
| N5 | 前端 `frontend/` 文件多为空存根，但已有部分实现，应统一状态 |
| N6 | `orchestrator.py` 中 `SessionManager` 存储在内存字典中，无过期机制 |

---

## 四、各层专项审查清单

### 4.1 LangGraph 状态机（`graph/`）

```
graph/ 审查 Checklist
─────────────────────────────────────────────
🔴 Blocker:
  [ ] state.py: TypedDict 字段完整，与所有 Node 返回值对齐
  [ ] nodes.py: 每个 Node 函数有 try-except，失败时设置 error 字段
  [ ] nodes.py: 返回值只包含 BrainstormState 中已定义的字段
  [ ] edges.py: 所有路由路径无死循环（最大重试次数守卫）
  [ ] edges.py: safety_router 检查所有轮次的否决（不限于最新轮）
  [ ] builder.py: 状态机拓扑正确，无孤立节点

🟡 Suggestion:
  [ ] nodes.py: Node 内部导入集中到文件顶部
  [ ] nodes.py: 每个关键操作有 structlog 日志（含 trace_id）
  [ ] nodes.py: replan() 传入实际被否决的 POI 列表
  [ ] edges.py: 路由函数有单元测试
```

### 4.2 Agent 实现（`agents/`）

```
agents/ 审查 Checklist
─────────────────────────────────────────────
🔴 Blocker:
  [ ] llm_client.py: eval() 使用有安全边界
  [ ] llm_client.py: API Key 不出现在日志中
  [ ] 所有 Agent.parse() / .review() 返回类型与 schemas/ 一致
  [ ] brainstorm_engine: 并行执行失败时单个 Agent 有 fallback

🟡 Suggestion:
  [ ] 4 个 brainstorm Agent 抽取基类 BaseReviewAgent
  [ ] Prompt 文件（prompts/*.txt）有明确的输出格式说明
  [ ] orchestrator.py: aggregate_reviews 加权逻辑正确（R1+R2 不重复计算权重）
  [ ] 新增 Agent 有对应单元测试
```

### 4.3 Mock API（`tools/mock_api.py`）

```
tools/mock_api.py 审查 Checklist
─────────────────────────────────────────────
🔴 Blocker:
  [ ] 成功率从环境变量读取，无硬编码
  [ ] 失败时返回结构化 Fallback（不返回 None）
  [ ] trace_id 正确传播到日志

🟡 Suggestion:
  [ ] Mock 数据可配置化（当前硬编码在函数中）
  [ ] 测试中使用 random.seed() 确保可重复
```

### 4.4 前端（`frontend/`）

```
frontend/ 审查 Checklist
─────────────────────────────────────────────
🔴 Blocker:
  [ ] 无硬编码后端 URL（使用 config.py / .env）
  [ ] API 调用有超时和错误处理
  [ ] 用户输入有基本校验（非空、长度限制）

🟡 Suggestion:
  [ ] 组件职责单一，无巨型文件（>200 行）
  [ ] 空存根文件应有 TODO 注释标明待实现范围
```

---

## 五、审查评论模板

### 5.1 评论格式

```
[优先级] **类别: 简要标题**
文件:行号: 具体代码位置。

**原因**: 为什么这是一个问题。

**建议**: 修改方案（给出代码示例）。
```

### 5.2 审查总结模板

```markdown
## Code Review Summary

**分支/PR**: [名称]
**审查人**: [姓名]
**审查日期**: [日期]

### 总体评估
[1-2 句话总结代码质量和主要发现]

### 统计
- 🔴 Blocker: X 个
- 🟡 Suggestion: X 个
- 💭 Nit: X 个

### Blocker 清单
| # | 文件 | 问题 | 说明 |
|---|------|------|------|
| 1 | | | |

### 亮点
[值得表扬的设计和实现]

### 结论
[ ] 需要修改后重新审查
[ ] 修改 Blocker 后可合并
[ ] 通过，可合并
```

---

## 六、当前项目已知问题（审查发现）

基于对现有代码的审查，以下为已识别的问题优先级排序：

### 🔴 Blocker（需优先修复）

| # | 文件 | 问题 | 风险 |
|---|------|------|------|
| 1 | `llm_client.py:65` | `eval(response)` 执行 LLM 输出 | 任意代码执行 |
| 2 | `graph/nodes.py` | 所有 Node 函数无 try-except | 状态机崩溃无恢复 |
| 3 | `nodes.py:108` | `replan()` 的 `exclude_options=[]` 硬编码 | 否决后重规划重复生成相同 POI |
| 4 | `orchestrator.py:56-64` | R1+R2 评分权重可能双重计算 | 最终分数失真 |
| 5 | `edges.py:4-13` | `safety_router` 可能遗漏 R1 否决 | 安全否决失效 |

### 🟡 Suggestion（提升代码质量）

| # | 文件 | 问题 |
|---|------|------|
| 1 | `graph/nodes.py` | 延迟导入，每次调用都 import |
| 2 | `agents/brainstorm/*.py` | 4 个 Agent 结构完全相同，应抽取基类 |
| 3 | `graph/nodes.py` | 缺少 structlog 日志 |
| 4 | `graph/edges.py` | 路由函数无单元测试 |
| 5 | `tests/test_mock_api.py` | 未设置 `random.seed()`，测试不稳定 |
| 6 | `config.py` + `logging_config.py` | 职责重叠 |

---

## 七、Hackathon 期间审查策略

考虑到 Hackathon 时间紧迫，审查策略需调整：

### 7.1 优先级调整

| 阶段 | 审查重点 | 可暂缓 |
|------|---------|--------|
| **开发阶段** | B1（安全）、B2（逻辑）、B3（异常） | S1-S4、N1-N6 |
| **Demo 前 2h** | 仅 Blocker | 全部 Suggestion |
| **Demo 前 30min** | 仅数据丢失 / 崩溃 | 其他全部跳过 |

### 7.2 快速审查模式

当时间极度紧张时，使用简化流程：

```
快速审查模式（≤10 分钟）
─────────────────────────────────────────────
1. 跑一遍测试 → 全部通过？
2. grep -rn "eval\|exec\|__import__" → 无风险调用？
3. 检查 Node 函数有无 try-except → 覆盖核心路径？
4. 检查 edges.py 路由 → 无死循环？
5. 通过 → 合并
```

### 7.3 结对编程替代

对于核心模块（`graph/`、`agents/`），推荐使用结对编程替代异步审查：
- 一人写代码，一人实时审查
- 每完成一个函数，交换角色
- 适合 Hackathon 时间压力下的质量保证

---

## 八、工具与自动化（建议接入）

### 8.1 推荐工具链

| 工具 | 用途 | 优先级 |
|------|------|--------|
| **ruff** | Linter + Formatter（替代 flake8 + black） | P0 — 立即接入 |
| **mypy** | 静态类型检查 | P1 — 接入 |
| **pytest-cov** | 测试覆盖率 | P1 — 已在 requirements.txt |
| **pre-commit** | Git 提交钩子 | P2 — 时间允许 |

### 8.2 ruff 配置建议

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "W", "UP", "B", "SIM"]
ignore = ["E501"]  # 行长度由 formatter 处理

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # 允许未使用的导入
"tests/*" = ["S101"]       # 测试中允许 assert
```

### 8.3 GitHub Actions（可选）

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements.txt
      - run: cd backend && ruff check .
      - run: cd backend && python -m pytest tests/ -v
```

---

**文档终**
