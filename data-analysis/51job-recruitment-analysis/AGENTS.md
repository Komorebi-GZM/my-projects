# Agent 协作规范

## 1. 角色定义

### 1.1 执行者 (Executor)
- **职责**：负责按 Execution Prompts 实现具体章节
- **工作内容**：
  - 阅读并理解分配章节的 Execution Prompt
  - 按照规范完成数据获取、清洗、分析、可视化等任务
  - 生成符合质量标准的产物（脚本、图表、报告等）
  - 确保代码可运行、文档完整、结果正确

### 1.2 审查者 (Reviewer)
- **职责**：负责验证产物完整性和数据正确性
- **工作内容**：
  - 检查产物是否符合章节要求
  - 验证数据计算和逻辑正确性
  - 确保代码风格和命名规范一致
  - 审核可视化图表的准确性和美观性
  - 确认文档完整性（注释、说明、引用）

### 1.3 协调者 (Coordinator)
- **职责**：负责任务分发和依赖管理
- **工作内容**：
  - 维护任务依赖图（task_graph.py）
  - 监控各章节进度和阻塞情况
  - 分配任务给执行者
  - 协调跨章节依赖和接口
  - 处理异常情况和资源冲突

## 2. 工作流规范

### 2.1 执行前准备

1. **阅读项目规范**
   - 执行前必须阅读 `docs/project_convention.md`
   - 了解目录结构、命名规范、代码风格要求
   - 熟悉产物检查清单和质量标准

2. **检查前置依赖**
   ```bash
   python task_graph.py --check-deps <chapter_id>
   ```
   - 确认所有前置依赖章节已完成
   - 验证依赖产物是否存在且有效
   - 如有缺失，联系协调者处理

### 2.2 执行过程

1. **创建 Issue 记录**
   - 在 `.issues/in-progress/` 创建当前任务记录
   - 更新任务状态和开始时间

2. **按 Execution Prompt 执行**
   - 严格遵循步骤要求
   - 记录执行过程中的问题和决策

3. **自测验证**
   - 运行所有生成的脚本确保无错误
   - 检查输出产物完整性

### 2.3 完成后验证

1. **运行产物验证**
   ```bash
   python task_graph.py --validate <chapter_id>
   ```
   - 验证所有产物文件存在
   - 检查文件格式和内容正确性
   - 确认依赖关系已更新

2. **更新 Issue 状态**
   - 将任务移至 `.issues/done/`
   - 记录完成时间和关键产出

### 2.4 问题记录

发现问题时，记录到 `.learnings/LEARNINGS.md`：

```markdown
## YYYY-MM-DD

### 问题描述
[简要描述遇到的问题]

### 影响范围
[受影响的章节或产物]

### 解决方案
[采取的解决措施]

### 预防措施
[如何避免类似问题]
```

## 3. Issue Tracker 配置

项目无 GitHub remote，使用 `.issues/` 目录本地管理 issues。

### 3.1 目录结构

```
.issues/
├── open/           # 待处理 issues
├── in-progress/    # 进行中 issues
└── done/           # 已完成 issues
```

### 3.2 Issue 文件格式

每个 issue 为一个 Markdown 文件，命名格式：`{chapter_id}-{brief-description}.md`

**示例**：`ch3-salary-analysis-data-missing.md`

**内容模板**：

```markdown
---
id: ISSUE-001
title: [Issue 标题]
chapter: [相关章节，如 ch3_salary_analysis]
status: [open | in-progress | done]
priority: [high | medium | low]
created: [YYYY-MM-DD]
assignee: [执行者/审查者/协调者]
---

## 描述
[详细描述问题或任务]

## 复现步骤（如适用）
1. ...
2. ...

## 预期结果
[期望的行为或产物]

## 实际结果
[实际发生的情况]

## 备注
[其他相关信息]
```

### 3.3 状态流转

```
open → in-progress → done
  ↓       ↓
 wontfix  blocked
```

- **open**: 待分配或待处理
- **in-progress**: 正在处理中
- **done**: 已完成并验证
- **blocked**: 因依赖阻塞暂停
- **wontfix**: 决定不处理

## 4. Triage Labels

用于标记和分类 issues 的标签：

| Label | 含义 | 使用场景 |
|-------|------|----------|
| `needs-triage` | 需要分类评估 | 新创建的 issue，尚未评估优先级和分配 |
| `needs-info` | 需要更多信息 | 信息不足，需要补充上下文或数据 |
| `ready-for-agent` | 准备好分配给 Agent | 已明确需求，可开始执行 |
| `ready-for-human` | 需要人工介入 | 需要人工决策或复杂判断 |
| `wontfix` | 不修复 | 经评估决定不处理的问题 |

### 4.1 Label 使用规范

- 每个 issue 至少有一个 label
- `needs-triage` 仅用于新创建的 issue，评估后应替换
- `ready-for-agent` 和 `ready-for-human` 互斥
- 关闭 issue 时，如未解决应标记 `wontfix`

## 5. 协作流程图

```
┌─────────────┐
│  创建 Issue  │
│ needs-triage│
└──────┬──────┘
       ↓
┌─────────────┐     ┌──────────────┐
│  协调者评估  │────→│ needs-info   │
│  分配角色   │     │ （信息不足）  │
└──────┬──────┘     └──────────────┘
       ↓
┌─────────────┐
│ready-for-   │
│agent        │
└──────┬──────┘
       ↓
┌─────────────┐     ┌──────────────┐
│  执行者执行  │────→│ready-for-    │
│  按规范开发  │     │human         │
└──────┬──────┘     │（需人工决策） │
       ↓            └──────────────┘
┌─────────────┐
│  审查者验证  │
│  产物审核   │
└──────┬──────┘
       ↓
┌─────────────┐
│   完成      │
│   done      │
└─────────────┘
```

## 6. 沟通规范

1. **异步优先**：所有决策和讨论记录在 issue 或文档中
2. **明确指派**：使用 `@角色` 明确责任人
3. **进度更新**：每日更新 in-progress 任务状态
4. **阻塞上报**：遇到阻塞立即通知协调者

---

*本文档由协调者维护，所有 Agent 执行前必须阅读*
