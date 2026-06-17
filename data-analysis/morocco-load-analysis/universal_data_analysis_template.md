# Universal Data Analysis Template — Skill 文档 M-0 + M-1

> **版本**: v1.0
> **基于项目**: 摩洛哥电力负荷分析项目实战经验提炼
> **适用范围**: 任何需要结构化、可分发、可并行的数据分析项目

---

# ═══════════════════════════════════════════════════════════════
# M-0: Skill 元信息 + 工作流程总览
# ═══════════════════════════════════════════════════════════════

---

## 0.1 Skill 元信息

| 属性 | 值 |
|------|-----|
| **Skill 名称** | `universal-data-analysis-template` |
| **版本** | v1.0 |
| **类型** | 项目脚手架 + 流程规范 Skill |
| **语言** | 中英双语（文档以中文为主，代码/占位符为英文） |
| **适用场景** | 面向 SOLO Agent 的数据分析项目全生命周期管理。适用于任何需要：多章节/多阶段分析、多人/AI协作分发、并行批次调度、标准化产物输出的数据分析项目 |
| **前置依赖** | SOLO Agent 环境、Python 3.x、conda/venv |
| **产出物** | 完整的项目目录结构、规范文档、任务分发指南、可执行的章节脚本模板 |
| **设计理念** | 文档先行 → 规范驱动 → 批次并行 → 产物可追溯 |

### 适用场景详细描述

本 Skill 适用于以下典型场景：

1. **多维度数据分析项目**：项目需要从多个角度（如预处理、模式挖掘、预测、对比、优化等）对同一数据集进行分析
2. **多人/AI 协作项目**：项目需要分发给多个执行者（人或 AI Agent）并行执行不同章节
3. **长期迭代项目**：项目需要持续维护、扩展新章节、更新分析逻辑
4. **可复现研究**：项目需要严格的文档记录、版本控制、产物追溯
5. **教学/培训场景**：项目需要同时提供批量执行脚本和交互式 Notebook

---

## 0.2 触发条件

### 中文触发关键词

| 类别 | 关键词 |
|------|--------|
| **创建类** | "创建数据分析项目"、"搭建数据分析框架"、"初始化数据分析项目"、"新建分析项目脚手架" |
| **分析类** | "分析数据"、"数据分析"、"数据探索"、"数据挖掘"、"数据建模" |
| **规范类** | "项目规范"、"编写 project convention"、"制定分析流程"、"任务分发指南" |
| **模板类** | "数据分析模板"、"分析项目模板"、"项目模板" |
| **分发类** | "派活"、"任务分发"、"批次划分"、"并行执行"、"多Agent协作" |
| **扩展类** | "给项目加一个新章节"、"修改分析流程"、"复用模板到新项目" |

### 英文触发关键词

| 类别 | 关键词 |
|------|--------|
| **创建类** | "create data analysis project", "set up analysis framework", "initialize analysis project", "scaffold data project" |
| **分析类** | "data analysis", "analyze data", "data exploration", "data mining", "data modeling" |
| **规范类** | "project convention", "analysis workflow", "task dispatch", "coding standards" |
| **模板类** | "data analysis template", "analysis project template", "project scaffold" |
| **分发类** | "task dispatch", "batch execution", "parallel analysis", "multi-agent collaboration" |

### 触发优先级

当用户输入同时匹配多个关键词时，按以下优先级判断：

1. **明确创建意图**（"创建数据分析项目"）→ 直接进入 Phase 1 信息收集
2. **分析需求但无项目**（"帮我分析这份数据"）→ 先确认是否需要创建项目，再进入 Phase 1
3. **仅询问规范**（"数据分析项目应该怎么组织"）→ 展示本 Skill 的规范框架

---

## 0.3 八 Phase 工作流程图

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Universal Data Analysis Template 工作流程                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌─────────────┐                                                             ║
║  │  Phase 1    │  项目初始化 — 信息收集                                       ║
║  │  信息收集    │  收集 10 个核心参数（项目名/描述/数据/章节/环境等）            ║
║  └──────┬──────┘                                                             ║
║         │                                                                    ║
║         ▼                                                                    ║
║  ┌─────────────┐                                                             ║
║  │  Phase 2    │  规范文档生成 — project_convention.md                        ║
║  │  规范先行    │  生成项目唯一规范依据（结构/命名/脚本/环境/派活/检查）         ║
║  └──────┬──────┘                                                             ║
║         │                                                                    ║
║         ▼                                                                    ║
║  ┌─────────────┐                                                             ║
║  │  Phase 3    │  任务分发指南 — task_dispatch_guide.md                       ║
║  │  依赖编排    │  构建全局依赖图 + 批次划分 + 派活模板                        ║
║  └──────┬──────┘                                                             ║
║         │                                                                    ║
║         ▼                                                                    ║
║  ┌─────────────┐                                                             ║
║  │  Phase 4    │  目录结构 + 基础代码脚手架                                    ║
║  │  脚手架搭建  │  创建完整目录树 + utils 工具模块 + 章节脚本骨架              ║
║  └──────┬──────┘                                                             ║
║         │                                                                    ║
║         ▼                                                                    ║
║  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                     ║
║  │  Phase 5    │────▶│  Phase 5    │────▶│  Phase 5    │                     ║
║  │  Batch-0    │     │  Batch-1    │     │  Batch-N    │   批次化执行         ║
║  │  (串行前置)  │     │  (并行执行)  │     │  (串行收束)  │   按依赖图调度       ║
║  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                     ║
║         │                   │                   │                             ║
║         └───────────────────┼───────────────────┘                             ║
║                             │                                                 ║
║                             ▼                                                 ║
║  ┌─────────────┐                                                             ║
║  │  Phase 6    │  产物完整性检查                                              ║
║  │  质量检查    │  逐章节验证产物齐全性 + 脚本可运行性 + 文档一致性             ║
║  └──────┬──────┘                                                             ║
║         │                                                                    ║
║         ▼                                                                    ║
║  ┌─────────────┐                                                             ║
║  │  Phase 7    │  文档更新 + 经验沉淀                                         ║
║  │  收尾归档    │  更新规范文档 + 提炼经验教训 + 归档产物清单                  ║
║  └──────┬──────┘                                                             ║
║         │                                                                    ║
║         ▼                                                                    ║
║  ┌─────────────┐                                                             ║
║  │  Phase 8    │  项目交付 + Skill 库更新                                     ║
║  │  交付复用    │  生成最终报告 + 更新 Skill 模板库 + 归档项目模板              ║
║  └─────────────┘                                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 0.3.1 四份核心文档关系图

```
convention.md（项目宪法，所有文档的上游）
    ├── flow_design.md（研究设计文档：做什么、为什么、用什么方法）
    │       └── 被 dispatch_guide.md 和 execution_prompts.md 引用
    ├── dispatch_guide.md（执行操作手册：怎么做、按什么顺序、怎么派活）
    │       └── 引用 convention + flow_design
    └── execution_prompts.md（执行细节文档：精确到函数、参数、代码级别）
            └── 引用 convention + flow_design
```

**阅读顺序**：convention → flow_design → dispatch_guide → execution_prompts
**修改规则**：修改上游文档后，需检查下游文档是否需要同步更新

## 0.3.2 模块与 Phase 映射关系

| Skill 模块 | 对应 Phase | 产出文档 | 说明 |
|-----------|-----------|---------|------|
| M-0 | — | — | 元信息+流程总览（本模块） |
| M-1 | Phase 1-2 | project_convention.md | 信息收集+规范文档 |
| M-2 | Phase 3 | flow_design.md | 研究设计文档 |
| M-3 | Phase 4 | execution_prompts.md | 执行Prompt文档 |
| M-4 | Phase 5 | task_dispatch_guide.md | 任务分发指南 |
| M-5 | Phase 6 | 代码框架（config/utils/脚本骨架） | 脚手架搭建 |
| M-6 | Phase 7-8 | requirements.txt + 验证报告 | 依赖+验证 |

## 0.3.3 快速启动端到端检查清单

拿到本项目后的完整操作流程：

- [ ] **Step 0**: 阅读本文档 M-0（元信息+流程总览），理解整体架构
- [ ] **Step 1**: 阅读 `docs/project_convention.md`，了解目录结构、命名规则、禁止事项
- [ ] **Step 2**: 配置环境 `{{ENV_TYPE}} activate {{ENV_NAME}}`，安装依赖 `pip install -r requirements.txt`
- [ ] **Step 3**: 阅读 `docs/flow_design.md`，理解研究目标、数据概况、各章节方法
- [ ] **Step 4**: 阅读 `docs/task_dispatch_guide.md`，了解批次划分和依赖关系
- [ ] **Step 5**: 运行 `python src/utils/task_graph.py` 检查当前进度
- [ ] **Step 6**: 按批次执行（参考 dispatch_guide 的派活模板），从 Batch-0 开始
- [ ] **Step 7**: 每完成一个章节，运行 task_graph.py 更新状态，检查产物完整性

---

## 0.4 各 Phase 输入/输出关系表

| Phase | 名称 | 输入 | 输出 | 依赖前置 |
|-------|------|------|------|----------|
| **Phase 1** | 项目初始化 — 信息收集 | 用户需求描述 + 原始数据文件（可选） | 10 个核心参数值（参数化配置表） | 无 |
| **Phase 2** | 规范文档生成 | Phase 1 的 10 个参数 | `docs/project_convention.md`（完整规范文档） | Phase 1 |
| **Phase 3** | 任务分发指南 | Phase 1 的章节列表 + 依赖关系 + Phase 2 规范 | `docs/task_dispatch_guide.md`（依赖图 + 批次 + 派活模板） | Phase 1, Phase 2 |
| **Phase 4** | 脚手架搭建 | Phase 1 参数 + Phase 2 规范 + Phase 3 依赖图 | 完整目录树 + `src/utils/` 工具模块 + 章节脚本骨架 + `requirements.txt` | Phase 1, Phase 2, Phase 3 |
| **Phase 5** | 批次化执行 | Phase 4 脚手架 + Phase 3 批次计划 | 各章节的 `.py` + `.ipynb` 脚本 + `outputs/` 产物 | Phase 4 |
| **Phase 6** | 产物完整性检查 | Phase 5 的全部产物 + Phase 2 规范 | 检查报告（通过/失败 + 缺失项清单） | Phase 5 |
| **Phase 7** | 文档更新 + 经验沉淀 | Phase 5 产物 + Phase 6 检查结果 | 更新后的规范文档 + 经验教训文档 | Phase 6 |
| **Phase 8** | 项目交付 + Skill 库更新 | 全部 Phase 产出 | 最终交付报告 + Skill 模板库更新 | Phase 7 |

### 输入/输出流转示意

```
Phase 1 ──[10参数]──▶ Phase 2 ──[规范文档]──▶ Phase 3 ──[分发指南]──▶ Phase 4
                                                                      │
                                                              [脚手架+骨架]
                                                                      │
                                                                      ▼
Phase 8 ◀──[交付报告]── Phase 7 ◀──[更新文档]── Phase 6 ◀──[检查报告]── Phase 5
[Skill库更新]                  [经验沉淀]      [产物验证]     [各章节产物]
```

---

## 0.5 占位符完整列表

以下占位符贯穿整个 Skill 文档，用于在模板中标记需要根据具体项目替换的变量。

### 项目基本信息类

| 占位符 | 说明 | 示例值 | 使用位置 |
|--------|------|--------|----------|
| `{{PROJECT_NAME}}` | 项目名称（英文，用于目录名） | `Morocco_Load_Analysis` | 目录名、脚本路径、文档标题 |
| `{{PROJECT_DESCRIPTION}}` | 项目描述（中文，一句话） | `电商用户行为分析` | 文档标题、派活话术、报告封面 |
| `{{PROJECT_NAME_CN}}` | 项目中文名称（完整） | `电商用户行为全流程分析` | 文档标题、报告封面 |

### 数据相关类

| 占位符 | 说明 | 示例值 | 使用位置 |
|--------|------|--------|----------|
| `{{RAW_DATA_FILENAME}}` | 原始数据文件名 | `Data Morocco.xlsx` | data/ 目录、脚本引用、派活模板 |
| `{{DATA_FORMAT}}` | 数据格式 | `xlsx` / `csv` / `json` / `parquet` | 数据加载器、依赖说明 |
| `{{DATA_SHEET_NAME}}` | 数据表名（如为多表文件） | `Sheet1` / `RawData` | 数据加载器配置 |

### 分析实体类

| 占位符 | 说明 | 示例值 | 使用位置 |
|--------|------|--------|----------|
| `{{ENTITY_NAME}}` | 分析实体的中文名称 | `城市` / `客户` / `产品` | 文档描述、分析维度说明 |
| `{{ENTITY_NAME_EN}}` | 分析实体的英文名称 | `City` / `Customer` / `Product` | 代码变量名、目录名 |
| `{{ENTITY_CONFIG}}` | 实体配置（JSON 或列表） | `["Casablanca", "Rabat", ...]` | config.py 中的常量定义 |
| `{{ENTITY_COUNT}}` | 实体数量 | `8` | 文档描述、循环范围 |

### 章节结构类

| 占位符 | 说明 | 示例值 | 使用位置 |
|--------|------|--------|----------|
| `{{CHAPTER_LIST}}` | 章节列表（JSON 数组） | `[{"id":1,"name":"预处理",...}, ...]` | 依赖图生成、目录创建、派活模板 |
| `{{CHAPTER_COUNT}}` | 章节总数 | `8` | 文档描述、循环范围 |
| `{{CHAPTER_DEPENDENCIES}}` | 章节依赖关系（JSON） | `{"ch01":[], "ch02":["ch01"], ...}` | 依赖图生成、批次划分 |
| `{{CHAPTER_PREFIX}}` | 章节目录前缀格式 | `ch{NN}` | 目录命名、产物命名 |

### 环境配置类

| 占位符 | 说明 | 示例值 | 使用位置 |
|--------|------|--------|----------|
| `{{PYTHON_VERSION}}` | Python 版本 | `3.10` / `3.11` / `3.12` | conda 环境、kernel 配置、requirements |
| `{{ENV_NAME}}` | conda/venv 环境名 | `py310` | 激活命令、kernel 配置、派活话术 |
| `{{ENV_TYPE}}` | 环境类型 | `conda` / `venv` | 环境配置命令模板 |
| `{{CUSTOM_DEPENDENCIES}}` | 自定义依赖列表 | `pandas>=2.0, scikit-learn, ...` | requirements.txt 生成 |

### 领域配置类

| 占位符 | 说明 | 示例值 | 使用位置 |
|--------|------|--------|----------|
| `{{DOMAIN_CONFIG}}` | 领域特定配置（JSON） | `{"unit":"MW","freq":"hourly",...}` | config.py 领域参数 |
| `{{DOMAIN_KNOWLEDGE_FILE}}` | 领域知识文档 | `电力系统基础知识.md` | docs/ 目录、Prompt 引用 |
| `{{EXTERNAL_DATA_SOURCES}}` | 外部数据源描述 | `世界银行电力数据` | 数据采集章节引用 |

### 批次调度类

| 占位符 | 说明 | 示例值 | 使用位置 |
|--------|------|--------|----------|
| `{{BATCH_COUNT}}` | 批次总数 | `6` | 派活模板、进度检查 |
| `{{BATCH_PLAN}}` | 批次计划（JSON） | `[{"id":0,"tasks":[1],"parallel":false}, ...]` | 依赖图、派活模板 |

### 产物检查类

| 占位符 | 说明 | 示例值 | 使用位置 |
|--------|------|--------|----------|
| `{{DELIVERABLE_CHECKLIST}}` | 各章节产物清单（JSON） | `{"ch01":["cleaned_data.csv",...], ...}` | 产物完整性检查 |
| `{{QUALITY_CRITERIA}}` | 质量检查标准 | `DPI>=150, 无NaN, ...` | Phase 6 检查标准 |

> **注意**：本文档为占位符的权威定义位置。附录 A 中的占位符列表为本表的补充扩展。如有冲突，以本表为准。

---

## 0.6 从摩洛哥项目提炼的 10 条核心经验教训

以下经验均来自「摩洛哥电力负荷分析」项目的实战复盘，每条经验都附有具体的问题场景和改进方案。

### 经验 1：文档先行（Documentation First）

**问题场景**：项目初期直接开始写代码，导致后续多个 Agent 执行时对目录结构、命名规则、产物格式理解不一致，产生了大量返工。

**改进方案**：在任何代码编写之前，必须先完成 `project_convention.md` 和 `task_dispatch_guide.md` 两份核心文档。这两份文档是项目的"宪法"，所有执行者必须先读后做。

**核心原则**：
- 规范文档是项目的唯一真理来源（Single Source of Truth）
- 派活时只需一句话引用文档，无需重复说明规范
- 文档中的每条规则都必须可验证、可执行

> 详细分析见附录 D

### 经验 2：命名规范的重要性（Naming Convention Matters）

**问题场景**：产物文件缺少统一前缀，导致无法快速判断文件归属哪个章节；目录命名风格不统一（有的用下划线，有的用驼峰），增加了查找成本。

**改进方案**：建立严格的分层命名规范：
- 目录命名：`ch{NN}_{英文简称}/`（脚本目录）vs `ch{NN}_{英文全称}/`（输出目录）
- 产物命名：强制 `ch{NN}_` 前缀，确保归属清晰
- 脚本命名：以动作为核心（`preprocess.py`、`analysis.py`、`forecast.py`）

**核心原则**：
- 前缀 `ch{NN}_` 是强制的，不可省略
- 命名规则必须覆盖目录、脚本、产物三个层级
- 命名规范写入规范文档，执行时零歧义

> 详细分析见附录 D

### 经验 3：双格式脚本的价值（Dual-Format Scripts）

**问题场景**：只提供 `.py` 脚本时，调试困难、学习曲线陡峭；只提供 `.ipynb` 时，无法批量执行、版本控制困难。

**改进方案**：每个章节必须同时提供 `.py`（批量执行）和 `.ipynb`（交互学习）两种格式，且逻辑完全一致。`.ipynb` 是 `.py` 的分步展开版。

**核心原则**：
- `.py` 用于 CI/CD、批量执行、生产部署
- `.ipynb` 用于探索性分析、学习理解、逐步调试
- 两者逻辑必须一致，修改一个必须同步修改另一个

> 详细分析见附录 D

### 经验 4：产物前缀的归属清晰度（Deliverable Prefix Ownership）

**问题场景**：多个章节的产物混放在同一目录，无法区分归属；产物文件名缺少章节标识，导致后续章节引用时容易混淆。

**改进方案**：
- 每个章节有独立的 `outputs/chXX_xxx/` 子目录
- 所有产物文件强制以 `ch{NN}_` 开头
- 禁止跨章节写入产物

**核心原则**：
- 一个章节的产物只写入自己的目录
- 文件名前缀 = 章节编号 = 归属标识
- 产物目录结构在规范文档中明确定义

> 详细分析见附录 D

### 经验 5：派活话术的效率（Dispatch Template Efficiency）

**问题场景**：每次派活都需要详细说明项目结构、环境配置、依赖关系，沟通成本极高；不同执行者对任务的理解不一致。

**改进方案**：预定义三种派活模板（完整启动/单批次/检查进度），每次派活只需填充变量即可。派活时一句话引用规范文档，无需重复说明。

**核心原则**：
- 派活模板 = 固定结构 + 变量占位符
- 派活话术必须包含：环境、规范文档引用、输入数据、输出产物、完成标志
- 模板化派活可将单次派活时间从 10 分钟降低到 1 分钟

> 详细分析见附录 D

### 经验 6：质量检查标准（Quality Check Standards）

**问题场景**：章节完成后没有统一的检查标准，导致产物质量参差不齐；有的产物缺少必要文件，有的图片分辨率不足。

**改进方案**：建立通用的 6 项检查标准 + 章节自定义检查项：
1. 产物目录下文件齐全
2. 所有数据文件以 `ch{NN}_` 开头
3. 所有图片 DPI >= 150
4. 脚本可在指定环境下无报错运行
5. `.py` 和 `.ipynb` 逻辑一致
6. 任务进度状态更新为完成

**核心原则**：
- 检查标准必须可自动化（脚本可执行检查）
- 通用检查项 + 章节自定义检查项的组合模式
- 检查结果必须记录，不合格必须返工

> 详细分析见附录 D

### 经验 7：并行批次划分策略（Parallel Batch Strategy）

**问题场景**：所有章节串行执行，总耗时过长；但盲目并行又会导致依赖冲突和数据不一致。

**改进方案**：基于依赖图进行拓扑排序，将章节划分为多个批次：
- Batch-0：串行前置（无依赖的章节，通常是数据预处理）
- Batch-1~N-1：并行执行（无相互依赖的章节可同时进行）
- Batch-N：串行收束（需要所有前置章节完成的汇总章节）

**核心原则**：
- 依赖图是批次划分的唯一依据
- 严禁跳批（必须等前置依赖全部完成）
- 并行度最大化 vs 依赖正确性的平衡

> 详细分析见附录 D

### 经验 8：Skill 库复用模式（Skill Library Reuse Pattern）

**问题场景**：每个新项目都从零开始搭建，重复劳动多；项目间的优秀实践无法有效传递。

**改进方案**：将项目模板抽象为 Skill，形成可复用的模板库：
- 项目规范文档模板（本 Skill 的核心产出）
- 任务分发指南模板
- 脚手架生成脚本
- 通用工具模块（config、data_loader、output_manager、task_graph）

**核心原则**：
- 每个项目完成后，提炼可复用的模式更新到 Skill 库
- Skill 库 = 模板 + 占位符 + 参数化配置
- 新项目 = Skill 实例化（填充参数 → 生成项目）

> 详细分析见附录 D

### 经验 9：Prompt 五段式结构的完整性（Five-Part Prompt Structure）

**问题场景**：执行 Prompt 缺少必要的上下文信息，导致执行者需要反复确认；有的 Prompt 只描述了"做什么"，没有说明"为什么"和"做到什么程度"。

**改进方案**：每个执行 Prompt 必须包含五个部分：
1. **背景与目标**（Why）：为什么需要这个章节，要解决什么问题
2. **输入数据**（Input）：需要哪些数据文件，数据格式是什么
3. **执行步骤**（Steps）：详细的分步执行指令
4. **输出产物**（Output）：期望的产物列表和格式要求
5. **质量标准**（Quality）：产物需要满足的质量标准

**核心原则**：
- 五段式结构缺一不可
- 每个步骤必须可独立验证
- Prompt 中的产物描述必须与规范文档一致

> 详细分析见附录 D

### 经验 10：Step 六子结构的可执行性（Six-Sub-Step Executability）

**问题场景**：步骤描述过于笼统（如"进行数据清洗"），执行者不知道具体该做什么；步骤之间缺少逻辑衔接，执行顺序不明确。

**改进方案**：每个 Step 必须包含六个子结构：
1. **Step 编号**：`Step X.N`，明确层级关系
2. **目标描述**：一句话说明本步骤要达成什么
3. **方法说明**：使用什么方法/算法/工具
4. **输入产物**：本步骤需要读取哪些文件
5. **输出产物**：本步骤产生哪些文件（含命名）
6. **验收标准**：如何判断本步骤完成

**核心原则**：
- 每个子结构都必须有明确的值，不允许"视情况而定"的模糊描述
- 输入产物必须是前面步骤已产出的文件
- 验收标准必须可量化或可程序化检查

> 详细分析见附录 D

---

# ═══════════════════════════════════════════════════════════════
# M-1: Phase 1-2 模板
# ═══════════════════════════════════════════════════════════════

---

# Phase 1: 项目初始化 — 信息收集

> **目标**：收集创建数据分析项目所需的全部核心参数，为后续 Phase 生成规范文档和脚手架提供输入。
> **输出**：10 个核心参数的完整配置表。

---

## 1.1 十参数收集策略表

| # | 参数名 | 占位符 | 说明 | 示例值 | 是否必填 | 推断策略 |
|---|--------|--------|------|--------|----------|----------|
| 1 | **项目名称** | `{{PROJECT_NAME}}` | 英文项目名，用于目录名、代码引用。要求：小写字母+下划线，无空格 | `Morocco_Load_Analysis` | **必填** | 从用户描述中提取核心主题，转为英文 snake_case |
| 2 | **项目描述** | `{{PROJECT_DESCRIPTION}}` | 中文一句话描述，用于文档标题和派活话术 | `电商用户行为分析` | **必填** | 从用户需求描述中提炼核心目标 |
| 3 | **原始数据文件名** | `{{RAW_DATA_FILENAME}}` | 原始数据文件的完整文件名（含扩展名） | `Data Morocco.xlsx` | **必填** | 检查用户上传的文件名，或询问数据来源 |
| 4 | **数据格式** | `{{DATA_FORMAT}}` | 原始数据的文件格式 | `xlsx` | **必填** | 从文件名扩展名自动推断 |
| 5 | **分析实体名称** | `{{ENTITY_NAME}}` | 分析的核心实体中文名（如城市、客户、产品、地区等） | `城市` | **必填** | 从项目描述或数据列名中推断 |
| 6 | **实体配置** | `{{ENTITY_CONFIG}}` | 实体的具体取值列表或配置（JSON 格式） | `["Casablanca","Rabat","Tangier",...]` | 条件必填 | 读取数据文件中的实体列，提取唯一值 |
| 7 | **章节列表** | `{{CHAPTER_LIST}}` | 分析章节的列表（JSON 数组，含 id、名称、简称） | 见下方示例 | **必填** | 根据分析目标规划，或参考同类项目模板 |
| 8 | **章节依赖关系** | `{{CHAPTER_DEPENDENCIES}}` | 章节间的数据依赖关系（JSON 对象） | `{"ch01":[],"ch02":["ch01"],...}` | **必填** | 根据章节间的数据流向自动推断 |
| 9 | **Python 版本** | `{{PYTHON_VERSION}}` | 项目使用的 Python 版本 | `3.10` | **必填** | 默认 `3.10`，除非用户指定 |
| 10 | **环境配置** | `{{ENV_NAME}}` + `{{ENV_TYPE}}` | Python 环境名称和类型 | `py310` / `conda` | **必填** | 默认 conda + `py3{{PYTHON_VERSION_NO_DOT}}` |

### 章节列表示例格式

```json
[
  {"id": 1, "name_cn": "数据预处理", "name_en": "preprocessing", "dir_suffix": "preprocessing"},
  {"id": 2, "name_cn": "用电规律挖掘", "name_en": "load_pattern", "dir_suffix": "load_pattern"},
  {"id": 3, "name_cn": "峰值识别", "name_en": "peak_analysis", "dir_suffix": "peak_analysis"},
  {"id": 4, "name_cn": "短期负荷预测", "name_en": "load_forecasting", "dir_suffix": "load_forecasting"},
  {"id": 5, "name_cn": "中长期趋势分析", "name_en": "midlong_term_trend", "dir_suffix": "midlong_term_trend"},
  {"id": 6, "name_cn": "跨国对比", "name_en": "cross_country", "dir_suffix": "cross_country"},
  {"id": 7, "name_cn": "配电网优化", "name_en": "grid_optimization", "dir_suffix": "grid_optimization"},
  {"id": 8, "name_cn": "总结展望", "name_en": "summary", "dir_suffix": "summary"}
]
```

### 章节依赖关系示例格式

```json
{
  "ch01": [],
  "ch02": ["ch01"],
  "ch03": ["ch01", "ch02"],
  "ch04": ["ch01"],
  "ch05": ["ch01"],
  "ch06": ["ch02", "ch05"],
  "ch07": ["ch02", "ch03", "ch04", "ch05"],
  "ch08": ["ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07"]
}
```

---

## 1.2 快速模式 vs 自定义模式

### 快速模式（Quick Mode）

适用于：用户只想快速启动一个标准数据分析项目，不需要精细配置。

**行为**：
- 使用以下默认值自动填充所有参数：

| 参数 | 默认值 |
|------|--------|
| `{{PROJECT_NAME}}` | 从数据文件名自动生成（去掉扩展名，转 snake_case）（如果自动检测失败，SOLO 应询问用户手动指定） |
| `{{PROJECT_DESCRIPTION}}` | 从数据文件名自动生成中文描述（如果自动检测失败，SOLO 应询问用户手动指定） |
| `{{RAW_DATA_FILENAME}}` | 用户上传的文件名 |
| `{{DATA_FORMAT}}` | 从文件扩展名自动推断（如果自动检测失败，SOLO 应询问用户手动指定） |
| `{{ENTITY_NAME}}` | 自动检测数据中的分类列（如果自动检测失败，SOLO 应询问用户手动指定） |
| `{{ENTITY_CONFIG}}` | 自动提取分类列的唯一值（如果自动检测失败，SOLO 应询问用户手动指定） |
| `{{CHAPTER_LIST}}` | 使用通用 5 章节模板（预处理→探索→建模→评估→总结） |
| `{{CHAPTER_DEPENDENCIES}}` | 使用通用串行依赖（ch01→ch02→ch03→ch04→ch05） |
| `{{PYTHON_VERSION}}` | `3.10` |
| `{{ENV_NAME}}` / `{{ENV_TYPE}}` | `py310` / `conda` |

**触发条件**：用户说"快速创建"、"用默认配置"、"帮我分析这份数据"等。

### 自定义模式（Custom Mode）

适用于：用户有明确的项目规划，需要精细控制每个参数。

**行为**：
- 逐个参数与用户确认，支持修改和调整
- 对于章节列表和依赖关系，提供交互式编辑界面
- 支持从已有项目中导入配置

**触发条件**：用户说"自定义配置"、"我有具体规划"、"按我的要求来"等。

---

## 1.3 信息收集对话模板

以下是 SOLO 与用户进行信息收集的标准交互流程。根据快速模式或自定义模式，可跳过部分步骤。

### Step 1.1: 确认项目基本信息

```
SOLO: 你好！我将帮你创建一个结构化的数据分析项目。请先告诉我以下基本信息：

1. 这个项目叫什么？（中文描述，如"电商用户行为分析"）
2. 你有原始数据文件吗？文件名是什么？（如"Data Morocco.xlsx"）

[如果用户提供了数据文件，SOLO 自动读取并推断数据格式和实体信息]
```

### Step 1.2: 确认分析实体

```
SOLO: 我已经读取了你的数据文件。数据中包含以下分类维度：
  - 列 A: [唯一值列表]
  - 列 B: [唯一值列表]

请问你的分析主要围绕哪个实体展开？（如"城市"、"客户"、"产品"等）

[如果数据中没有明显的分类列，SOLO 询问用户]
```

### Step 1.3: 规划分析章节

```
SOLO: 基于你的项目描述和数据特征，我建议以下分析章节：

  ch01: 数据预处理          — 清洗、缺失值处理、特征工程
  ch02: 探索性数据分析      — 描述统计、分布分析、相关性分析
  ch03: [领域相关分析]      — 根据项目目标定制
  ch04: 建模与预测          — 模型训练、评估、预测
  ch05: 总结与报告          — 结论汇总、可视化报告

你是否同意这个章节规划？需要增加、删除或调整吗？

[如果用户有明确规划，按用户要求调整]
[如果用户说"用默认的"，直接使用建议的章节]
```

### Step 1.4: 确认章节依赖关系

```
SOLO: 基于章节间的数据流向，我推断出以下依赖关系：

  ch01 (数据预处理) → 无依赖，必须最先完成
  ch02 (探索性分析) → 依赖 ch01 的清洗数据
  ch03 (领域分析)   → 依赖 ch01 + ch02
  ch04 (建模预测)   → 依赖 ch01 + ch02
  ch05 (总结报告)   → 依赖全部章节

这个依赖关系是否正确？有需要调整的吗？

[展示依赖图 ASCII art 供用户确认]
```

### Step 1.5: 确认环境配置

```
SOLO: 最后确认环境配置：

  Python 版本: 3.10（默认）
  环境类型: conda（默认）
  环境名称: py310（默认）

需要修改吗？如果不需要，我将使用默认配置。

[如果用户指定了其他版本或环境，按用户要求调整]
```

### Step 1.6: 参数确认汇总

```
SOLO: 以下是你项目的完整配置，请确认：

┌─────┬──────────────────┬──────────────────────────────────┐
│  #  │ 参数              │ 值                               │
├─────┼──────────────────┼──────────────────────────────────┤
│  1  │ 项目名称          │ {{PROJECT_NAME}}                  │
│  2  │ 项目描述          │ {{PROJECT_DESCRIPTION}}           │
│  3  │ 原始数据文件      │ {{RAW_DATA_FILENAME}}             │
│  4  │ 数据格式          │ {{DATA_FORMAT}}                   │
│  5  │ 分析实体          │ {{ENTITY_NAME}}                   │
│  6  │ 实体配置          │ {{ENTITY_CONFIG}}                 │
│  7  │ 章节列表          │ {{CHAPTER_LIST}}                  │
│  8  │ 依赖关系          │ {{CHAPTER_DEPENDENCIES}}          │
│  9  │ Python 版本       │ {{PYTHON_VERSION}}                │
│ 10  │ 环境配置          │ {{ENV_NAME}} ({{ENV_TYPE}})       │
└─────┴──────────────────┴──────────────────────────────────┘

确认无误后，我将进入 Phase 2 生成项目规范文档。

[用户确认后，进入 Phase 2]
[用户要求修改，返回对应步骤重新确认]
```

---

# Phase 2: project_convention.md 完整模板

> **目标**：基于 Phase 1 收集的 10 个参数，生成项目的唯一规范依据文档。
> **输出**：`docs/project_convention.md`（完整规范文档）。
> **使用方式**：将下方模板中的所有 `{{PLACEHOLDER}}` 替换为实际值，写入 `docs/project_convention.md`。

---

## 模板开始

```markdown
# {{PROJECT_DESCRIPTION}} — 项目规范 (Project Convention)

> **本文档是项目唯一规范依据。** 所有执行者（人 / AI）在动手前必须先阅读本文档。
> 派活时只需一句话：**"参考 `docs/project_convention.md`，执行 Prompt-XX。"**

---

## 一、项目结构总览

```
{{PROJECT_NAME}}/
├── data/                              # 原始数据（只读，不可修改）
│   └── {{RAW_DATA_FILENAME}}          #    唯一数据源
│
├── src/                               # 源代码
│   ├── utils/                         #    通用工具模块（全章节共享）
│   │   ├── config.py                  #      全局配置：路径、参数、常量
│   │   ├── data_loader.py             #      Skill-01: 数据加载器
│   │   ├── output_manager.py          #      Skill-04: 输出产物管理器
│   │   └── task_graph.py              #      任务依赖图 + 进度检查
{{CHAPTER_DIR_TREE}}
│
├── outputs/                           # 输出产物（每个章节独立子目录）
{{OUTPUT_DIR_TREE}}
│
├── docs/                              # 项目文档
│   ├── project_convention.md          #    项目规范（本文档）
│   ├── {{FLOW_DESIGN_FILENAME}}       #    流程设计文档
│   ├── task_dispatch_guide.md         #    任务分发指南（依赖图 + 派活模板）
│   └── {{PROJECT_NAME}}_Execution_Prompts.md  #    各 Prompt 执行细节
│
├── requirements.txt                   # Python 依赖清单
└── README.md                          # 项目说明（可选）
```

> **说明**：`{{CHAPTER_DIR_TREE}}` 和 `{{OUTPUT_DIR_TREE}}` 根据章节列表自动生成。
> 每个章节在 `src/` 下有对应的 `ch{NN}_{英文简称}/` 目录，在 `outputs/` 下有对应的 `ch{NN}_{英文全称}/` 目录。

---

## 二、文件分类规则

### 2.1 什么放哪里

| 文件类型 | 存放位置 | 规则 |
|----------|----------|------|
| **原始数据** | `data/` | 只读，唯一数据源，任何脚本不得修改此目录 |
| **脚本代码** | `src/chXX_xxx/` | 每个章节一个子目录，内含 `.py` + `.ipynb` |
| **通用工具** | `src/utils/` | 跨章节复用的模块（config、loader、manager 等） |
| **输出产物** | `outputs/chXX_xxx/` | 每个章节的产物写入对应子目录，互不干扰 |
| **项目文档** | `docs/` | 规范文档、设计文档、执行 Prompt 等 |
| **依赖清单** | 项目根目录 | `requirements.txt` 唯一一份 |

### 2.2 禁止事项

- ❌ 禁止在 `data/` 中写入任何文件
- ❌ 禁止在 `outputs/` 下跨章节写入（ch02 的产物不能写到 ch01 目录）
- ❌ 禁止在项目根目录散落脚本、数据、临时文件
- ❌ 禁止在 `src/` 下直接放 `.py` 文件（必须在 `chXX_xxx/` 或 `utils/` 子目录内）
- ❌ 禁止创建 `venv/` 目录（使用 {{ENV_TYPE}} 环境 `{{ENV_NAME}}`）
- ❌ **禁止在代码中硬编码项目特定参数**（如文件路径、实体名称、领域常量等），所有参数必须通过 `src/utils/config.py` 统一管理

---

## 三、命名规范

### 3.1 目录命名

| 层级 | 格式 | 示例 |
|------|------|------|
| 章节脚本目录 | `src/ch{NN}_{英文简称}/` | `src/ch02_load_pattern/` |
| 章节输出目录 | `outputs/ch{NN}_{英文全称}/` | `outputs/ch02_load_pattern_analysis/` |

### 3.2 脚本命名

| 类型 | 格式 | 说明 |
|------|------|------|
| Python 脚本 | `{{ACTION}}.py` | 如 `preprocess.py`, `analysis.py`, `forecast.py` |
| Jupyter Notebook | `{{ACTION}}.ipynb` | 与 `.py` 同名，内容对应 |

### 3.3 产物命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch02_descriptive_stats.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch02_daily_load_curve.png` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch02_load_pattern_report.md` |
| 模型文件 | `ch{NN}_{模型名}.pkl` | `ch04_lstm_model.pkl` |

**前缀 `ch{NN}_` 是强制的**，确保产物归属清晰。

### 3.4 变量命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 常量 | `UPPER_SNAKE_CASE` | `OUTPUT_BASE`, `MAX_ITERATIONS` |
| 函数 | `snake_case` | `load_preprocessed_data()`, `save_figure()` |
| 类 | `PascalCase` | `DataLoader`, `OutputManager` |
| 私有方法 | `_leading_underscore` | `_validate_input()`, `_parse_config()` |

### 3.5 配置命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 环境变量 | `UPPER_SNAKE_CASE` | `PYTHON_VERSION`, `DATA_DIR` |
| 配置文件键 | `snake_case` | `output_base`, `figure_dpi` |
| 命令行参数 | `--kebab-case` | `--output-dir`, `--figure-dpi` |

---

## 四、脚本编写规范

### 4.1 每个章节必须提供两种格式

```
src/chXX_xxx/
├── analysis.py       # 可直接运行: python src/chXX_xxx/analysis.py
└── analysis.ipynb    # Jupyter 交互式: jupyter notebook src/chXX_xxx/analysis.ipynb
```

- `.py` 和 `.ipynb` 逻辑完全一致，`.ipynb` 是 `.py` 的分步展开版
- `.py` 用于批量执行，`.ipynb` 用于逐步学习和调试

### 4.2 Python 脚本结构模板

每个 `.py` 脚本必须遵循以下结构：

```python
"""
Prompt-XX: {{CHAPTER_NAME}}
{{CHAPTER_DESCRIPTION}}

覆盖步骤:
  - Step X.1: ...
  - Step X.2: ...
  ...

产物输出到: outputs/chXX_xxx/
"""

import sys
import os

# 路径设置（确保能导入 utils）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

# 导入项目工具
from utils.config import OUTPUT_BASE, FIGURE_DPI, ...
from utils.data_loader import load_preprocessed
from utils.output_manager import save_dataframe, save_figure, save_markdown


def main():
    """主函数：执行本章全部分析步骤。"""
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'chXX_xxx')
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step X.1: {{STEP_DESCRIPTION}}
    # ...

    # Step X.2: {{STEP_DESCRIPTION}}
    # ...

    print(f"章节 XX 完成。产物已输出到: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
```

### 4.3 Notebook 结构模板

每个 `.ipynb` 必须遵循以下结构：

```
Cell 0 [Markdown]: 标题 + 环境说明 + 规范文档引用
Cell 1 [Code]:     导入 + 路径设置 + 配置加载
Cell 2 [Markdown]: Step X.1 说明（目标 + 方法 + 产物）
Cell 3 [Code]:     Step X.1 实现
Cell 4 [Markdown]: Step X.2 说明
Cell 5 [Code]:     Step X.2 实现
...
Cell N [Code]:     总结
```

**Cell 0 Markdown 模板**：

```markdown
# Prompt-XX: {{CHAPTER_NAME}}

> **环境**: {{ENV_NAME}} (Python {{PYTHON_VERSION}})
> **规范**: 参考 `docs/project_convention.md`
> **数据**: {{RAW_DATA_FILENAME}}

## 本章目标
{{CHAPTER_OBJECTIVE}}
```

### 4.4 Kernel 配置

```json
"kernelspec": {
    "display_name": "Python {{PYTHON_VERSION}} ({{ENV_NAME}})",
    "language": "python",
    "name": "{{ENV_NAME}}"
}
```

### 4.5 代码质量规则

所有 Python 代码必须遵守以下质量标准：

#### PEP8 合规

- 行长度不超过 88 字符（使用 Black 格式化器的默认值）
- 缩进使用 4 个空格
- 类和函数定义之间空两行
- 导入顺序：标准库 → 第三方库 → 项目内部模块，每组之间空一行
- 避免使用通配符导入（`from xxx import *`）

#### 类型注解

- 所有公共函数必须有参数类型注解和返回值类型注解
- 复杂数据结构使用 `typing` 模块（`List`, `Dict`, `Optional`, `Tuple` 等）
- 示例：

```python
from typing import List, Dict, Optional
import pandas as pd


def load_preprocessed(
    entity_name: str,
    data_dir: str = "data"
) -> pd.DataFrame:
    """加载预处理后的数据。

    Args:
        entity_name: 分析实体名称。
        data_dir: 数据目录路径。

    Returns:
        预处理后的 DataFrame。
    """
    ...
```

#### Docstring 规范

- 所有公共模块、类、函数必须有 docstring
- 使用 Google 风格 docstring
- docstring 必须包含：简要描述、Args（参数）、Returns（返回值）、Raises（异常，如有）
- 示例：

```python
def calculate_statistics(
    df: pd.DataFrame,
    group_col: str,
    value_col: str
) -> pd.DataFrame:
    """计算分组统计量。

    对 DataFrame 按指定列分组，计算均值、标准差、最大值、最小值等统计量。

    Args:
        df: 输入数据框。
        group_col: 分组列名。
        value_col: 数值列名。

    Returns:
        包含分组统计量的 DataFrame，列包括 mean, std, min, max, median。

    Raises:
        ValueError: 如果 group_col 或 value_col 不在 df 的列中。
    """
    ...
```

### 4.6 文档更新规则

- **修改代码后必须同步更新文档**：如果修改了脚本逻辑、产物格式、依赖关系，必须同步更新以下文档：
  - `docs/project_convention.md`：如果影响了项目结构、命名规范、脚本规范
  - `docs/task_dispatch_guide.md`：如果影响了依赖关系、批次划分、产物清单
  - 脚本内的 docstring：如果修改了函数签名、行为、产物
- **文档更新检查**：每次提交代码时，检查是否有对应的文档更新。如果没有，需要在提交信息中说明原因

---

## 五、禁止事项清单

### 5.1 核心禁止事项（5 条）

| # | 禁止事项 | 原因 | 正确做法 |
|---|----------|------|----------|
| 1 | 禁止修改 `data/` 目录 | 原始数据是唯一数据源，修改后无法恢复 | 所有数据处理结果写入 `outputs/` |
| 2 | 禁止跨章节写入产物 | 产物归属混乱，后续引用困难 | 每个章节只写入自己的 `outputs/chXX_xxx/` |
| 3 | 禁止在根目录散落文件 | 项目结构混乱，难以维护 | 文件必须归入对应目录（data/src/outputs/docs） |
| 4 | 禁止跳过依赖直接执行 | 数据不一致，产物不可靠 | 严格按批次顺序执行 |
| 5 | 禁止在代码中硬编码参数 | 参数分散难以维护，换项目需大量修改 | 所有参数通过 `src/utils/config.py` 管理 |

### 5.2 扩展禁止事项

| # | 禁止事项 | 原因 | 正确做法 |
|---|----------|------|----------|
| 6 | 禁止在**业务逻辑脚本**中使用 `print()` 输出中间调试信息 | 污染标准输出，不利于日志管理 | 使用 `logging` 模块。**工具模块**（utils/）中的 `print()` 用于用户反馈是允许的。 |
| 7 | 禁止提交包含敏感信息的代码 | 安全风险 | 使用环境变量或配置文件管理密钥 |
| 8 | 禁止在 Notebook 中保留大量调试输出 | 文件体积膨胀，影响版本控制 | 清理 Cell 输出后再提交 |
| 9 | 禁止使用绝对路径引用项目文件 | 换环境后路径失效 | 使用 `os.path` 动态构建相对路径 |
| 10 | 禁止忽略 PEP8 和类型注解要求 | 代码质量下降，维护困难 | 使用 linter（flake8/pylint）自动检查 |
| 11 | 禁止创建未经规范的临时文件 | 临时文件堆积，项目混乱 | 临时文件使用 `tempfile` 模块或写入系统临时目录 |
| 12 | 禁止在 `src/` 下直接放 `.py` 文件 | 破坏目录结构规范 | 必须放在 `chXX_xxx/` 或 `utils/` 子目录内 |

---

## 六、环境配置

### 6.1 环境初始化

```bash
# 创建环境（首次）
{{ENV_TYPE}} create -n {{ENV_NAME}} python={{PYTHON_VERSION}}

# 激活环境
{{ENV_TYPE}} activate {{ENV_NAME}}

# 安装依赖（首次）
cd {{PROJECT_NAME}}
pip install -r requirements.txt
```

### 6.2 运行脚本

```bash
# 激活环境
{{ENV_TYPE}} activate {{ENV_NAME}}

# 运行 Python 脚本
python src/chXX_xxx/analysis.py

# 运行 Notebook
jupyter notebook src/chXX_xxx/analysis.ipynb
# → 选择 Kernel: "Python {{PYTHON_VERSION}} ({{ENV_NAME}})"
```

### 6.3 依赖管理

```bash
# 添加新依赖
pip install {{PACKAGE_NAME}}
pip freeze | grep {{PACKAGE_NAME}} >> requirements.txt

# 更新依赖
pip install --upgrade {{PACKAGE_NAME}}
pip freeze > requirements.txt

# 检查依赖冲突
pip check
```

---

## 七、派活标准话术

### 7.1 完整项目启动（从零开始）

```
【{{PROJECT_DESCRIPTION}} — 完整项目启动】

=== 第一步：了解项目 ===
阅读 docs/project_convention.md（目录结构、命名规则、禁止事项）
阅读 docs/flow_design.md 第一章（研究概述、数据概况、整体逻辑）

=== 第二步：配置环境 ===
{{ENV_TYPE}} activate {{ENV_NAME}}
pip install -r requirements.txt

=== 第三步：检查进度 ===
python src/utils/task_graph.py

=== 第四步：按批次执行 ===
参考 docs/task_dispatch_guide.md 的批次划分
从 Batch-0（数据预处理）开始，逐批执行
每个章节使用 §7.2 的精确派活话术

=== 第五步：产物检查 ===
每完成一个章节，运行 python src/utils/task_graph.py 确认状态更新
全部完成后，检查 outputs/ 下所有章节产物齐全
```

### 7.2 派单个章节（最常用）

```
【{{PROJECT_DESCRIPTION}} — Prompt-{{NN}}: {{CHAPTER_NAME}}】

你现在阅读 docs/{{PROJECT_NAME}}_Execution_Prompts.md，概览任务状况，
你的任务是 Prompt-{{NN}}: {{CHAPTER_NAME}}；
执行标准看 docs/{{FLOW_DESIGN_FILENAME}} 第{{N}}章；
产物要求看该文档第{{N}}章 {{N}}.5 节产物表；
项目规范（文件放哪、怎么命名、脚本结构）看 docs/project_convention.md；
执行前从 src/utils/task_graph.py 检查进度。

环境: {{ENV_TYPE}} activate {{ENV_NAME}}
```

**变量说明**：

| 变量 | 含义 | 示例值 |
|------|------|--------|
| `{{PROJECT_DESCRIPTION}}` | 项目中文描述 | `电商用户行为分析` |
| `{{NN}}` | 章节编号（两位数） | `01` / `02` / `03` |
| `{{CHAPTER_NAME}}` | 章节中文名称 | `数据预处理` / `行为特征分析` |
| `{{PROJECT_NAME}}_Execution_Prompts.md` | 执行Prompt文档文件名 | `Ecommerce_User_Behavior_Analysis_Execution_Prompts.md` |
| `{{FLOW_DESIGN_FILENAME}}` | 流程设计文档文件名 | `电商用户行为分析_流程设计.md` |
| `{{N}}` | 流程设计文档中的章节编号 | `2` / `3` / `4`（注意：流程设计文档第一章是研究概述，Prompt-01 对应第二章） |
| `{{ENV_TYPE}}` | 环境类型 | `conda` |
| `{{ENV_NAME}}` | 环境名称 | `py310` |

**首次执行 vs 重试执行**：

首次执行时，在话术末尾追加：
```
首次执行：先阅读 docs/project_convention.md 了解项目规范，再开始。
```

重试/继续执行时，在话术末尾追加：
```
继续执行：检查 outputs/ch{{NN}}_{{CHAPTER_DIR}}/ 已有哪些产物，从未完成的步骤继续。
```

### 7.3 检查进度

```
检查{{PROJECT_DESCRIPTION}}全部进度:
  python src/utils/task_graph.py

检查特定章节:
  python src/utils/task_graph.py --chapter ch{{NN}}

生成检查报告:
  python src/utils/task_graph.py --report outputs/quality_report.md
```

### 7.4 执行前必做清单（Pre-flight Checklist）

每次收到派活后、开始编码前，必须逐项确认：

- [ ] **1. 环境已激活**: `{{ENV_TYPE}} activate {{ENV_NAME}}`，且 `python --version` 输出正确
- [ ] **2. 依赖已安装**: `pip list | grep pandas` 确认核心依赖可用
- [ ] **3. 前置章节产物已存在**: `python src/utils/task_graph.py --check prompt-{{NN}}`
- [ ] **4. 已阅读项目规范**: `docs/project_convention.md`（至少看完目录结构和命名规范）
- [ ] **5. 已阅读本 Prompt 任务概述**: `docs/{{PROJECT_NAME}}_Execution_Prompts.md` 中搜索 `Prompt-{{NN}}`
- [ ] **6. 已阅读流程设计对应章节**: `docs/{{FLOW_DESIGN_FILENAME}}` 第{{N}}章（了解研究目标和方法选择依据）
- [ ] **7. 已确认产物输出目录**: `outputs/ch{{NN}}_{{CHAPTER_DIR}}/` 目录存在或将被自动创建

**如果第3项不通过**：说明前置章节未完成，需要先完成前置章节或与项目负责人确认。
**如果第5项或第6项不通过**：说明对任务理解不充分，可能导致返工，强烈建议先读完再动手。

---

## 八、产物完整性检查

### 8.1 通用检查项（6 项）

每个章节完成后，必须确认以下检查项：

- [ ] `outputs/chXX_xxx/` 目录下产物齐全
- [ ] 所有数据文件以 `ch{NN}_` 开头
- [ ] 所有图片以 `ch{NN}_` 开头，DPI >= 150
- [ ] 脚本可在 `{{ENV_TYPE}} activate {{ENV_NAME}}` 下无报错运行
- [ ] `.py` 和 `.ipynb` 逻辑一致
- [ ] 运行 `python src/utils/task_graph.py` 状态更新为完成

### 8.2 章节自定义检查项

以下为各章节的额外检查项，根据实际项目内容定制：

{{CHAPTER_CHECKLIST}}

> **说明**：`{{CHAPTER_CHECKLIST}}` 根据章节列表自动生成，每个章节可定义 2-5 个领域特定的检查项。
> 示例格式：
>
> #### ch01: 数据预处理
> - [ ] 清洗后数据无 NaN 值
> - [ ] 特征工程数据列数符合预期
> - [ ] 数据类型正确（数值列为 float/int，分类列为 category）
>
> #### ch02: 探索性分析
> - [ ] 描述统计表包含所有 {{ENTITY_NAME}}
> - [ ] 分布图覆盖所有 {{ENTITY_NAME}}
> - [ ] 相关性矩阵热力图已生成

### 8.3 自动化检查脚本

项目提供 `src/utils/task_graph.py` 用于自动化检查：

```bash
# 检查全部章节进度
python src/utils/task_graph.py

# 检查指定章节
python src/utils/task_graph.py --chapter ch02

# 输出检查报告
python src/utils/task_graph.py --report outputs/quality_report.md
```

检查脚本会自动验证：
1. 各章节产物目录是否存在
2. 必需的产物文件是否齐全
3. 产物文件命名是否符合规范（`ch{NN}_` 前缀）
4. 图片文件 DPI 是否达标
5. 依赖关系是否满足（前置章节产物是否存在）
```

## 模板结束

---

> **M-0 + M-1 文档结束**
> 下一部分 M-2 将包含 Phase 3-4（任务分发指南 + 脚手架搭建）模板。

---

# Skill 文档模板 — M-2 + M-4

> 本文档为数据分析项目模板体系的 Phase 3（flow_design.md）和 Phase 5（task_dispatch_guide.md）完整模板。
> 从实际项目中提取结构模式，去除所有领域特定内容，保留通用框架。

---

# ═══════════════════════════════════════════════════════════════════
# M-2: Phase 3 — flow_design.md 完整模板
# ═══════════════════════════════════════════════════════════════════

---

# {{PROJECT_NAME}} — 流程设计文档

> **版本**: {{VERSION}} | **更新日期**: {{DATE}} | **配套执行文档**: `{{EXECUTION_PROMPT_FILENAME}}`

---

## 文档说明

本文档为**全流程标准化数据分析研究框架**，严格遵循{{DOMAIN}}数据分析、{{SUB_DOMAIN_1}}、{{SUB_DOMAIN_2}}、{{SUB_DOMAIN_3}}的学术规范。每一章节明确：**研究目标 → 数据输入 → 技术方法 → 实施步骤 → 阶段产物 → 质量标准**，可直接作为课程论文、实训报告、数据分析结题文档原稿使用。

**与执行Prompt文档的关系**：本文档定义"做什么、为什么、用什么方法"；配套的Prompt文档定义"怎么做——精确到函数、参数、代码级别"。两份文档配合使用：先阅读本文档理解全貌，再参照Prompt文档逐步执行。

**与 task_dispatch_guide.md 的关系**：
- 本文档（flow_design.md）= **研究设计文档**，面向读者/评审者，描述"做什么、为什么、用什么方法"
- task_dispatch_guide.md = **执行操作手册**，面向执行者，描述"怎么做、按什么顺序、怎么派活"
- 修改本文档的章节目标或方法后，需同步检查 execution_prompts.md 和 dispatch_guide.md 是否需要更新

---

## 第一章 研究概述

### 1.1 研究背景

{{RESEARCH_BACKGROUND}}

本次研究采用**{{DATASET_DESCRIPTION}}**，数据覆盖{{ENTITY_LIST}}，具备**{{DATA_CHARACTERISTICS}}**特征，可真实反映{{REAL_WORLD_PHENOMENON}}。

### 1.2 数据集基础概况

| {{DIMENSION_1}} | {{DIMENSION_2}} | {{DIMENSION_3}} | {{DIMENSION_4}} | {{DIMENSION_5}} | {{DIMENSION_6}} | {{DIMENSION_7}} | {{DIMENSION_8}} |
|------|---------|----------|--------|----------|--------|----------|----------|
| {{VALUE_1_1}} | {{VALUE_1_2}} | {{VALUE_1_3}} | {{VALUE_1_4}} | {{VALUE_1_5}} | {{VALUE_1_6}} | {{VALUE_1_7}} | {{VALUE_1_8}} |
| {{VALUE_2_1}} | {{VALUE_2_2}} | {{VALUE_2_3}} | {{VALUE_2_4}} | {{VALUE_2_5}} | {{VALUE_2_6}} | {{VALUE_2_7}} | {{VALUE_2_8}} |
| ... | ... | ... | ... | ... | ... | ... | ... |

> **填写说明**：
> - 维度数量根据实际数据调整，不限于 8 个。不需要的维度行直接删除。
> - `{{DIMENSION_X}}` 示例：`数据量(行)`、`时间范围`、`采样间隔`、`分析实体数`、`数据类型`、`缺失率`、`数值量级`、`特殊说明`
> - 所有维度均为必填，如果某维度不适用，填写"不适用"

**数据特征**：
- {{DATA_FEATURE_1}}
- {{DATA_FEATURE_2}}
- {{DATA_FEATURE_3}}
- {{DATA_FEATURE_4}}

### 1.3 整体研究逻辑

以{{CORE_DATA_SOURCE}}为核心，依次完成{{N}}大分析环节：

```
{{PHASE_1}} → {{PHASE_2}} → {{PHASE_3}} → {{PHASE_4}}
     ↓              ↓              ↓              ↓
  {{PRODUCT_1}}   {{PRODUCT_2}}   {{PRODUCT_3}}   {{PRODUCT_4}}
     ↓              ↓              ↓              ↓
{{PHASE_5}} → {{PHASE_6}} → {{PHASE_7}} → {{PHASE_8}}
```

**章节间数据依赖关系**：
- 第一章（{{CHAPTER_1_NAME}}）是全部后续章节的基础，必须最先完成
- {{DEPENDENCY_RULE_1}}
- {{DEPENDENCY_RULE_2}}
- {{DEPENDENCY_RULE_3}}
- {{DEPENDENCY_RULE_4}}

### 1.4 整体研究产出总览

| 序号 | 产出类别 | 具体内容 | 产出形式 |
|------|----------|----------|----------|
| 1 | {{OUTPUT_CATEGORY_1}} | {{OUTPUT_DETAIL_1}} | {{OUTPUT_FORMAT_1}} |
| 2 | {{OUTPUT_CATEGORY_2}} | {{OUTPUT_DETAIL_2}} | {{OUTPUT_FORMAT_2}} |
| 3 | {{OUTPUT_CATEGORY_3}} | {{OUTPUT_DETAIL_3}} | {{OUTPUT_FORMAT_3}} |
| ... | ... | ... | ... |
| N | {{OUTPUT_CATEGORY_N}} | {{OUTPUT_DETAIL_N}} | {{OUTPUT_FORMAT_N}} |

**预计总产出**：{{TOTAL_FILE_COUNT}}+ 个文件（{{DATA_FILE_COUNT}} 数据 + {{IMAGE_FILE_COUNT}} 图片 + {{MODEL_FILE_COUNT}} 模型 + {{REPORT_FILE_COUNT}} 报告）

### 1.5 技术环境与依赖

- **{{RUNTIME_NAME}}**: {{RUNTIME_VERSION}}（{{ENVIRONMENT_TYPE}} `{{ENV_NAME}}`，路径：`{{ENV_PATH}}`）
- **执行方式**: 每个章节均提供 **{{SCRIPT_FORMAT}}** 脚本，按章节编号命名（如 `{{SCRIPT_EXAMPLE_1}}`、`{{SCRIPT_EXAMPLE_2}}`），支持{{EXECUTION_FEATURES}}
- **环境管理**: 使用{{ENV_MANAGER}} `{{ENV_NAME}}`，激活命令 `{{ACTIVATE_COMMAND}}`，通过 `{{INSTALL_COMMAND}}` 安装全部依赖。**{{ENV_CONSTRAINT}}**
- **核心依赖**: {{CORE_DEPENDENCY_LIST}}
- **完整依赖清单**: 见 `{{REQUIREMENTS_FILE}}`

---

## 第N章 {{CHAPTER_NAME}}（重复模板）

> **使用说明**：以下为通用章节模板。每个分析章节均严格遵循此六节结构。根据章节类型（数据预处理型 / 分析探索型 / 总结报告型），各节内容的具体模式有所不同，详见后文"三种章节原型详细说明"。

### N.1 研究目标

{{CHAPTER_OBJECTIVE}}

### N.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| {{DATA_ITEM_1}} | `{{DATA_SOURCE_1}}` | {{DATA_FORMAT_1}} | {{DATA_DESCRIPTION_1}} |
| {{DATA_ITEM_2}} | `{{DATA_SOURCE_2}}` | {{DATA_FORMAT_2}} | {{DATA_DESCRIPTION_2}} |
| ... | ... | ... | ... |

### N.3 技术方法

| 环节 | 方法 | 公式/参数 | 选择理由 |
|------|------|-----------|----------|
| {{STEP_1}} | {{METHOD_1}} | `{{FORMULA_OR_PARAM_1}}` | {{REASON_1}} |
| {{STEP_2}} | {{METHOD_2}} | `{{FORMULA_OR_PARAM_2}}` | {{REASON_2}} |
| {{STEP_3}} | {{METHOD_3}} | `{{FORMULA_OR_PARAM_3}}` | {{REASON_3}} |
| ... | ... | ... | ... |

**替代方法**：
- {{ALTERNATIVE_TOPIC_1}}：{{ALTERNATIVE_METHOD_1A}}（{{ALTERNATIVE_PROS_1A}}）、{{ALTERNATIVE_METHOD_1B}}（{{ALTERNATIVE_PROS_1B}}）
- {{ALTERNATIVE_TOPIC_2}}：{{ALTERNATIVE_METHOD_2A}}（{{ALTERNATIVE_PROS_2A}}）、{{ALTERNATIVE_METHOD_2B}}（{{ALTERNATIVE_PROS_2B}}）
- {{ALTERNATIVE_TOPIC_3}}：{{ALTERNATIVE_METHOD_3A}}（{{ALTERNATIVE_PROS_3A}}）

### N.4 实施步骤

1. **{{STEP_1_TITLE}}** — {{STEP_1_DESCRIPTION}}
2. **{{STEP_2_TITLE}}** — {{STEP_2_DESCRIPTION}}
3. **{{STEP_3_TITLE}}** — {{STEP_3_DESCRIPTION}}
4. **{{STEP_4_TITLE}}** — {{STEP_4_DESCRIPTION}}
5. **{{STEP_5_TITLE}}** — {{STEP_5_DESCRIPTION}}
6. **{{STEP_6_TITLE}}** — {{STEP_6_DESCRIPTION}}
7. **{{STEP_7_TITLE}}** — {{STEP_7_DESCRIPTION}}
8. **{{STEP_8_TITLE}}** — {{STEP_8_DESCRIPTION}}

### N.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | {{PRODUCT_1_NAME}} | `{{PRODUCT_1_FILENAME}}` | {{PRODUCT_1_FORMAT}} | {{PRODUCT_1_DOWNSTREAM}} |
| 2 | {{PRODUCT_2_NAME}} | `{{PRODUCT_2_FILENAME}}` | {{PRODUCT_2_FORMAT}} | {{PRODUCT_2_DOWNSTREAM}} |
| 3 | {{PRODUCT_3_NAME}} | `{{PRODUCT_3_FILENAME}}` | {{PRODUCT_3_FORMAT}} | {{PRODUCT_3_DOWNSTREAM}} |
| ... | ... | ... | ... | ... |

### N.6 质量验证标准

- [ ] {{QUALITY_CHECK_1}}
- [ ] {{QUALITY_CHECK_2}}
- [ ] {{QUALITY_CHECK_3}}
- [ ] {{QUALITY_CHECK_4}}

---

## 三种章节原型详细说明

> **本节定义的是章节的"设计层面"**（做什么、为什么、用什么方法）。
> **章节的"执行层面"**（怎么做——精确到代码级别）见 M-3 的 Prompt 模板。
> 两者的关系：flow_design.md 回答"为什么要做这个分析"，execution_prompts.md 回答"具体怎么写代码完成这个分析"。

> **使用说明**：以下三种原型覆盖了数据分析项目的典型章节类型。新建章节时，选择最匹配的原型作为起点，替换占位符即可。一个项目通常包含 1 个数据预处理型章节、N 个分析探索型章节、1 个总结报告型章节。

---

### 原型 A：数据预处理型

> **适用场景**：原始数据清洗、格式统一、特征工程、质量报告生成。
> **核心特征**：输入为原始数据，输出为标准化数据集；步骤以"检测→处理→验证"为主线。

#### A.1 研究目标

厘清原始数据基本属性，解决**{{ISSUE_1}}**（如采样频率不统一）、**{{ISSUE_2}}**（如计量单位不一致）、**{{ISSUE_3}}**（如潜在缺失值和异常值）问题，构建统一格式、统一量纲、高质量的标准化分析数据集，为后续所有分析建模提供数据基础。

#### A.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 原始数据 | `{{RAW_DATA_PATH}}` | {{RAW_DATA_FORMAT}} | {{RAW_DATA_DESCRIPTION}} |

#### A.3 技术方法

| 处理环节 | 方法 | 公式/参数 | 选择理由 |
|----------|------|-----------|----------|
| 时序对齐 | {{ALIGNMENT_METHOD}} | `{{ALIGNMENT_CODE}}` | {{ALIGNMENT_REASON}} |
| 量纲统一 | {{UNIT_CONVERSION_METHOD}} | {{UNIT_CONVERSION_FORMULA}} | {{UNIT_CONVERSION_REASON}} |
| 异常检测 | {{OUTLIER_DETECTION_METHOD}} | {{OUTLIER_DETECTION_PARAM}} | {{OUTLIER_DETECTION_REASON}} |
| 异常处理 | {{OUTLIER_HANDLING_METHOD}} | `{{OUTLIER_HANDLING_CODE}}` | {{OUTLIER_HANDLING_REASON}} |
| 特征工程 | {{FEATURE_ENGINEERING_METHOD}} | {{FEATURE_LIST}} | {{FEATURE_ENGINEERING_REASON}} |

**替代方法**：
- 上采样/对齐：{{ALT_ALIGN_METHOD_1}}（{{ALT_ALIGN_PROS_1}}）、{{ALT_ALIGN_METHOD_2}}（{{ALT_ALIGN_PROS_2}}）
- 异常检测：{{ALT_OUTLIER_METHOD_1}}（{{ALT_OUTLIER_PROS_1}}）、{{ALT_OUTLIER_METHOD_2}}（{{ALT_OUTLIER_PROS_2}}）
- 量纲换算：{{ALT_UNIT_METHOD_1}}（{{ALT_UNIT_PROS_1}}）

#### A.4 实施步骤

1. **数据读取与结构探查** — 批量读取{{N_SOURCES}}个数据源，检查行数、列数、数据类型、缺失值、数值范围
2. **缺失值检测与统计** — 计算每列缺失率，缺失率>{{MISSING_THRESHOLD}}需特别报告
3. **时间戳解析与标准化** — 统一为{{DATETIME_TYPE}}类型，设置为索引，按时间升序排列
4. **{{RESAMPLING_STEP_TITLE}}** — {{RESAMPLING_STEP_DESCRIPTION}}
5. **量纲统一** — {{UNIT_CONVERSION_STEP_DESCRIPTION}}
6. **异常值检测（{{OUTLIER_METHOD_NAME}}）** — 按{{GROUPING_KEY}}分别计算阈值，标记但不删除
7. **异常值处理（{{OUTLIER_HANDLING_NAME}}）** — 替换被标记的异常点，确保无NaN残留
8. **时间特征工程** — 衍生{{FEATURE_LIST}}
9. **数据质量报告生成** — 汇总全部处理结果

#### A.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | 数据概况报告 | `ch{{NN}}_data_profile_report.md` | Markdown | 参考 |
| 2 | 缺失值统计表 | `ch{{NN}}_missing_stats.csv` | CSV | 参考 |
| 3 | {{INTERMEDIATE_PRODUCT_3_NAME}} | `ch{{NN}}_{{INTERMEDIATE_3}}.csv` | CSV | 中间产物 |
| 4 | {{INTERMEDIATE_PRODUCT_4_NAME}} | `ch{{NN}}_{{INTERMEDIATE_4}}.csv` | CSV | 中间产物 |
| 5 | 异常值标记表 | `ch{{NN}}_outlier_flags.csv` | CSV | {{DOWNSTREAM_PROMPT_LIST}} |
| 6 | **清洗后统一数据集** | `ch{{NN}}_cleaned_data.csv` | CSV | {{DOWNSTREAM_PROMPT_LIST}} |
| 7 | **含特征工程数据集** | `ch{{NN}}_feature_engineered_data.csv` | CSV | {{DOWNSTREAM_PROMPT_LIST}} |
| 8 | 数据质量报告 | `ch{{NN}}_data_quality_report.md` | Markdown | 参考 |

#### A.6 质量验证标准

- [ ] 全部{{N_ENTITIES}}个数据源对齐至{{TARGET_GRANULARITY}}粒度，无NaN残留
- [ ] 量纲统一后所有字段数据单位为{{TARGET_UNIT}}，数值量级合理
- [ ] 异常值替换后数据分布无突变断裂
- [ ] 特征工程列完整：{{FEATURE_LIST}}

---

### 原型 B：分析探索型

> **适用场景**：统计分析、可视化、模式发现、建模预测、对比研究、优化求解。
> **核心特征**：输入为预处理后的数据集，输出为分析结论和可视化图表；步骤以"维度分析→可视化→结论归纳"为主线。

#### B.1 研究目标

从**{{ANALYSIS_DIMENSIONS}}**多维度挖掘{{TARGET_PHENOMENON}}规律，量化不同{{GROUPING_DIMENSION}}下的{{METRIC_NAME}}分布特征，厘清{{COMPARISON_GROUPS}}的差异化运行模式。

#### B.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| {{INPUT_DATA_1}} | `{{INPUT_SOURCE_1}}` | {{INPUT_FORMAT_1}} | {{INPUT_DESCRIPTION_1}} |
| {{INPUT_DATA_2}} | `{{INPUT_SOURCE_2}}` | {{INPUT_FORMAT_2}} | {{INPUT_DESCRIPTION_2}} |

#### B.3 技术方法

| 分析维度 | 方法 | 关键函数/公式 |
|----------|------|---------------|
| {{DIM_1}} | {{DIM_1_METHOD}} | `{{DIM_1_CODE}}` |
| {{DIM_2}} | {{DIM_2_METHOD}} | `{{DIM_2_CODE}}` |
| {{DIM_3}} | {{DIM_3_METHOD}} | `{{DIM_3_CODE}}` |
| {{DIM_4}} | {{DIM_4_METHOD}} | `{{DIM_4_CODE}}` |
| {{DIM_5}} | {{DIM_5_METHOD}} | `{{DIM_5_CODE}}` |
| {{DIM_6}} | {{DIM_6_METHOD}} | `{{DIM_6_CODE}}` |

**{{ADVANCED_TOPIC_TITLE}}**：
- 优先：{{PREFERRED_STRATEGY}}
- 备选：{{FALLBACK_STRATEGY}}

**替代方法**：{{ALT_METHOD_1}}（{{ALT_PROS_1}}）、{{ALT_METHOD_2}}（{{ALT_PROS_2}}）

#### B.4 实施步骤

1. **{{STEP_1_TITLE}}** — 按{{GROUPING_KEY}}计算{{STATISTICS_LIST}}
2. **{{STEP_2_TITLE}}** — 计算{{DERIVED_METRICS}}，量化{{TARGET_PROPERTY}}
3. **{{STEP_3_TITLE}}** — 分{{GROUPING_KEY}}绘制，识别{{PATTERN_TO_IDENTIFY}}
4. **{{STEP_4_TITLE}}** — 叠加对比图，量化{{COMPARISON_FACTOR}}影响
5. **{{STEP_5_TITLE}}** — {{GROUPING_DIMENSION_1}}×{{GROUPING_DIMENSION_2}}热力图，展示{{PERIODICITY}}规律
6. **{{STEP_6_TITLE}}** — {{N_GROUPS}}组同坐标系对比，分析{{COMPARISON_TARGET}}差异
7. **{{STEP_7_TITLE}}** — {{CLUSTERING_METHOD}}，输出分类结果
8. **{{STEP_8_TITLE}}** — 分层后统计+可视化

#### B.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | {{PRODUCT_1_NAME}} | `ch{{NN}}_{{PRODUCT_1_KEY}}.csv` | CSV | {{DOWNSTREAM_1}} |
| 2 | {{PRODUCT_2_NAME}} | `ch{{NN}}_{{PRODUCT_2_KEY}}.csv` | CSV | {{DOWNSTREAM_2}} |
| 3 | {{PRODUCT_3_NAME}} | `ch{{NN}}_{{PRODUCT_3_KEY}}_{entity}.png` | PNG | 报告配图 |
| 4 | {{PRODUCT_4_NAME}} | `ch{{NN}}_{{PRODUCT_4_KEY}}_{entity}.png` | PNG | 报告配图 |
| 5 | {{PRODUCT_5_NAME}} | `ch{{NN}}_{{PRODUCT_5_KEY}}_{entity}.png` | PNG | 报告配图 |
| 6 | {{PRODUCT_6_NAME}} | `ch{{NN}}_{{PRODUCT_6_KEY}}.png` | PNG | 报告配图 |
| 7 | {{PRODUCT_7_NAME}} | `ch{{NN}}_{{PRODUCT_7_KEY}}.csv` | CSV | {{DOWNSTREAM_7}} |
| 8 | {{PRODUCT_8_NAME}} | `ch{{NN}}_{{PRODUCT_8_KEY}}.png` | PNG | 报告配图 |

#### B.6 质量验证标准

- [ ] {{QUALITY_CHECK_1}}
- [ ] {{QUALITY_CHECK_2}}
- [ ] {{QUALITY_CHECK_3}}
- [ ] {{QUALITY_CHECK_4}}

---

### 原型 C：总结报告型

> **适用场景**：全流程成果汇总、关键指标总览、不足与展望。
> **核心特征**：输入为全部前序章节产物，输出为总结性文档；步骤以"汇总→归纳→展望"为主线。

#### C.1 研究目标

系统完成{{FULL_PIPELINE_SUMMARY}}全链条研究，完整揭示{{CORE_FINDING_TARGET}}，并结合{{COMPARISON_CONTEXT}}形成横向参考。

#### C.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| 全部前序章节产物 | `outputs/ch{{01}}~ch{{NN-1}}/*/` | 混合格式 | 各章节分析结论与数据 |

#### C.3 技术方法

| 环节 | 方法 | 说明 |
|------|------|------|
| 成果汇总 | 结构化整理 | 按章节顺序汇总核心发现与关键指标 |
| 指标总览 | 交叉引用 | 提取各章节核心指标，形成总览表 |
| 不足分析 | 反思归纳 | 系统梳理研究局限性与改进方向 |
| 展望规划 | 前瞻推演 | 提出未来可拓展的研究方向 |

#### C.4 实施步骤

1. **全流程成果梳理** — 按章节顺序，逐章提取核心发现、关键指标、代表性图表
2. **关键指标总览表编制** — 汇总全部量化指标，形成一张可快速查阅的总览表
3. **研究局限性分析** — 从数据、方法、范围三个维度系统梳理不足
4. **未来研究方向展望** — 针对每个局限性提出具体改进方案和预期效果
5. **总结报告撰写** — 整合以上内容，形成完整总结文档

#### C.5 阶段产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用 |
|------|----------|--------|------|----------|
| 1 | 成果汇总报告 | `ch{{NN}}_achievements_summary.md` | Markdown | 最终交付 |
| 2 | 关键指标总览表 | `ch{{NN}}_key_metrics_table.csv` | CSV | 最终交付 |

#### C.6 质量验证标准

- [ ] 全部前序章节的核心发现均已纳入总结
- [ ] 关键指标总览表覆盖所有量化结论
- [ ] 局限性分析覆盖数据、方法、范围三个维度
- [ ] 每个改进方向均有明确的预期效果说明

---

## 附录

### 附录A: 项目文件目录结构

```
{{PROJECT_DIR_NAME}}/
├── data/                              # 原始数据
│   └── {{RAW_DATA_FILENAME}}
├── notebooks/                         # Jupyter Notebook 交互式脚本（使用 {{ENV_NAME}} 内核）
│   ├── ch{{01}}_{{NOTEBOOK_1_NAME}}.ipynb       # {{CHAPTER_1_SHORT_NAME}}
│   ├── ch{{02}}_{{NOTEBOOK_2_NAME}}.ipynb       # {{CHAPTER_2_SHORT_NAME}}
│   ├── ch{{03}}_{{NOTEBOOK_3_NAME}}.ipynb       # {{CHAPTER_3_SHORT_NAME}}
│   ├── ch{{04}}_{{NOTEBOOK_4_NAME}}.ipynb       # {{CHAPTER_4_SHORT_NAME}}
│   ├── ch{{05}}_{{NOTEBOOK_5_NAME}}.ipynb       # {{CHAPTER_5_SHORT_NAME}}
│   ├── ch{{06}}_{{NOTEBOOK_6_NAME}}.ipynb       # {{CHAPTER_6_SHORT_NAME}}
│   ├── ch{{07}}_{{NOTEBOOK_7_NAME}}.ipynb       # {{CHAPTER_7_SHORT_NAME}}
│   └── ch{{08}}_{{NOTEBOOK_8_NAME}}.ipynb       # {{CHAPTER_8_SHORT_NAME}}
├── outputs/                           # 全部输出产物
│   ├── ch{{01}}_{{OUTPUT_DIR_1}}/       # {{FILE_COUNT_1}}个文件
│   ├── ch{{02}}_{{OUTPUT_DIR_2}}/       # {{FILE_COUNT_2}}+个文件
│   ├── ch{{03}}_{{OUTPUT_DIR_3}}/       # {{FILE_COUNT_3}}+个文件
│   ├── ch{{04}}_{{OUTPUT_DIR_4}}/       # {{FILE_COUNT_4}}+个文件
│   ├── ch{{05}}_{{OUTPUT_DIR_5}}/       # {{FILE_COUNT_5}}+个文件
│   ├── ch{{06}}_{{OUTPUT_DIR_6}}/       # {{FILE_COUNT_6}}+个文件
│   ├── ch{{07}}_{{OUTPUT_DIR_7}}/       # {{FILE_COUNT_7}}个文件
│   └── ch{{08}}_{{OUTPUT_DIR_8}}/       # {{FILE_COUNT_8}}个文件
├── src/                               # {{LANGUAGE}}源代码（Notebook可复用模块）
│   ├── ch{{01}}_{{MODULE_1}}.py ~ ch{{07}}_{{MODULE_7}}.py
│   └── utils/ ({{UTILITY_MODULE_LIST}})
├── docs/                              # 文档
│   ├── {{EXECUTION_PROMPT_FILENAME}}  # 执行Prompt文档
│   └── {{FLOW_DESIGN_FILENAME}}       # 本文档
└── requirements.txt                   # 依赖清单
```

### 附录B: 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch{{01}}_cleaned_data.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch{{02}}_{{VIS_NAME}}_{{entity}}.png` |
| 模型文件 | `ch{NN}_{模型名}_model.{ext}` | `ch{{04}}_{{MODEL_NAME}}_model.{{MODEL_EXT}}` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch{{01}}_data_quality_report.md` |
| 配置文件 | `ch{NN}_{描述}.json` | `ch{{04}}_data_split_info.json` |

### 附录C: 全局可复用Skill库

| Skill | 名称 | 适用章节 | 核心功能 |
|-------|------|----------|----------|
| Skill-01 | 标准数据加载器 | 全部{{N}}章 | `load_{{ENTITY}}_data()`, `load_all_{{ENTITY}}()` |
| Skill-02 | 标准可视化出图器 | {{VIS_CHAPTERS}} | `plot_time_series()`, `plot_heatmap()`, `plot_model_forecast()` |
| Skill-03 | 标准评估指标计算器 | {{EVAL_CHAPTERS}} | `calc_{{METRIC_1}}()`, `calc_{{METRIC_2}}()`, `compare_models()` |
| Skill-04 | 标准输出产物管理器 | 全部{{N}}章 | `save_dataframe()`, `save_figure()`, `generate_quality_checklist()` |

### 附录D: 完整依赖清单

```
{{DEPENDENCY_1}}          # {{DEPENDENCY_1_PURPOSE}}
{{DEPENDENCY_2}}           # {{DEPENDENCY_2_PURPOSE}}
{{DEPENDENCY_3}}         # {{DEPENDENCY_3_PURPOSE}}
{{DEPENDENCY_4}}           # {{DEPENDENCY_4_PURPOSE}}
{{DEPENDENCY_5}}        # {{DEPENDENCY_5_PURPOSE}}
{{DEPENDENCY_6}}          # {{DEPENDENCY_6_PURPOSE}}
{{DEPENDENCY_7}}           # {{DEPENDENCY_7_PURPOSE}}
{{DEPENDENCY_8}}      # {{DEPENDENCY_8_PURPOSE}}
{{DEPENDENCY_9}}           # {{DEPENDENCY_9_PURPOSE}}
{{DEPENDENCY_10}}          # {{DEPENDENCY_10_PURPOSE}}
{{DEPENDENCY_11}}       # {{DEPENDENCY_11_PURPOSE}}
{{DEPENDENCY_12}}      # {{DEPENDENCY_12_PURPOSE}}
{{DEPENDENCY_13}}             # {{DEPENDENCY_13_PURPOSE}}
{{DEPENDENCY_14}}              # {{DEPENDENCY_14_PURPOSE}}
{{DEPENDENCY_15}}             # {{DEPENDENCY_15_PURPOSE}}
{{DEPENDENCY_16}}            # {{DEPENDENCY_16_PURPOSE}}
{{DEPENDENCY_17}}             # {{DEPENDENCY_17_PURPOSE}}
{{DEPENDENCY_18}}            # {{DEPENDENCY_18_PURPOSE}}
{{DEPENDENCY_19}}             # {{DEPENDENCY_19_PURPOSE}}
{{DEPENDENCY_20}}          # {{DEPENDENCY_20_PURPOSE}}
```

### 已知版本兼容性约束

| 约束 | 说明 | 推荐处理 |
|------|------|----------|
| torch + numpy | torch 2.x 通常需要 numpy < 2.0 | 先装 numpy 再装 torch |
| prophet | 需要 cmdstanpy 预编译，安装可能失败 | 提供手动安装回退方案 |
| lightgbm | macOS 需要 OpenMP（默认可能不可用） | `brew install libomp` |
| statsmodels | 与 scipy 版本需兼容 | 使用 requirements.txt 锁定版本 |
| plotly + notebook | Jupyter 中需要 `ipywidgets` | `pip install ipywidgets` |

---
---

# ═══════════════════════════════════════════════════════════════════
# M-4: Phase 5 — task_dispatch_guide.md 完整模板
# ═══════════════════════════════════════════════════════════════════

---

# {{PROJECT_NAME}} — 任务分发指南

> 本文档定义了{{PROJECT_NAME}}项目的任务分发规范。
> **每次派活时，将对应批次的「派活模板」直接发给执行者即可。**

---

## 一、全局依赖图

### 1.1 ASCII DAG 图生成规则

依赖图采用**ASCII有向无环图（DAG）**表示，遵循以下规则：

1. **节点命名**：每个节点对应一个 Prompt，格式为 `Prompt-NN (章节简称)`
2. **箭头方向**：`→` 表示数据/产物依赖方向，从上游指向下游
3. **层级排列**：按拓扑层级从上到下排列，同一层级的并行节点水平对齐
4. **并行标记**：同一层级中可并行的节点用 `├─` 和 `└─` 分叉表示
5. **汇聚标记**：多个上游汇聚到一个下游时，用 `└──►` 合并箭头表示
6. **注释标注**：关键依赖关系在箭头旁用 `←` 注释说明

### 1.2 参数化依赖关系模板

```
Prompt-01 ({{CHAPTER_1_NAME}}) ───────────────────────────────────── 必须最先完成
    │
    ├──────────────────┬──────────────────┐
    ▼                  ▼                  ▼
Prompt-02          Prompt-04          Prompt-05        ← {{PARALLEL_NOTE}}
({{CH2_SHORT}})      ({{CH4_SHORT}})      ({{CH5_SHORT}})
    │                  │                  │
    ▼                  │                  │
Prompt-03              │                  │
({{CH3_SHORT}})        │                  │
    │                  │                  │
    ├──────────────────┤                  │
    ▼                  ▼                  ▼
    └──────► Prompt-06 ◄─────────────────┘
            ({{CH6_SHORT}})     ← {{MERGE_NOTE_1}}
                │
                ▼
            Prompt-07
            ({{CH7_SHORT}})     ← {{MERGE_NOTE_2}}
                │
                ▼
            Prompt-08
            ({{CH8_SHORT}})     ← {{MERGE_NOTE_3}}
```

**DAG 参数说明**：

| 参数 | 含义 | 示例 |
|------|------|------|
| `{{CHAPTER_N_NAME}}` | 第N章完整名称 | 数据预处理 |
| `{{CHN_SHORT}}` | 第N章简称 | 预处理 |
| `{{PARALLEL_NOTE}}` | 并行说明 | 三条支线可并行 |
| `{{MERGE_NOTE_N}}` | 汇聚依赖说明 | 需要 02 + 05 完成 |

---

## 二、批次划分

### 2.1 批次划分算法说明

批次划分基于**拓扑排序（Topological Sort）**算法：

1. **构建依赖图**：以每个 Prompt 为节点，以数据依赖关系为有向边
2. **计算入度**：统计每个节点的入度（前置依赖数量）
3. **逐层展开**：
   - 入度为 0 的节点归入当前批次
   - 移除已分配节点及其出边
   - 重复以上过程直到所有节点分配完毕
4. **并行度标注**：同一批次内的节点可并行执行，标注最大并行度
5. **批次编号**：从 Batch-0 开始顺序编号

### 2.2 批次表格模板

| 批次 | 任务 | 并行度 | 前置依赖 | 数据源 |
|------|------|--------|----------|--------|
{{BATCH_TABLE}}

> **填写规则**：行数等于 `{{BATCH_COUNT}}`（通常为 3-6 个批次）。列格式：`| Batch-{{X}} | {{BATCH_NAME}} | {{BATCH_TASKS}} | {{PARALLEL_FLAG}} | {{DEPENDENCY}} | {{DATA_SOURCE}} |`
> **最少 2 个批次**：Batch-0（串行前置，通常是数据预处理）+ Batch-1（串行收束，通常是总结报告）。

**批次参数说明**：

| 参数 | 含义 | 填写规则 |
|------|------|----------|
| `{{PARALLEL_DEGREE}}` | 并行支线数量 | 同一批次内可同时执行的最大任务数 |
| `{{BRANCH_X}}` | 支线标识 | Batch-1 中的并行支线用字母 A/B/C 标识 |
| `{{BATCHN_DATA_SOURCE}}` | 该批次所需数据 | 列出所有前置产物文件路径 |

---

## 三、派活模板

### 模板 A：完整项目启动（从零开始）

```
【{{PROJECT_NAME}} — 任务分发】

项目路径: {{PROJECT_DIR_NAME}}/
环境: {{ACTIVATE_COMMAND}}
规范文档: docs/{{FLOW_DESIGN_FILENAME}}
执行Prompt: docs/{{EXECUTION_PROMPT_FILENAME}}

═══ 阶段 1：串行前置 ═══
▶ Batch-0: Prompt-01 {{CHAPTER_1_NAME}}
  - 脚本: {{SCRIPT_PATH_CH01}}
  - 产物: outputs/{{OUTPUT_DIR_CH01}}/ ({{PRODUCT_COUNT_CH01}}个文件)
  - 完成标志: {{COMPLETION_FLAG_CH01}}

═══ 阶段 2：{{PARALLEL_DEGREE}}路并行 ═══（Batch-0 完成后启动）
▶ 支线 A: Prompt-{{02}} {{CHAPTER_2_NAME}}
  - 依赖: {{DEPENDENCY_CH02}}
  - 产物: outputs/{{OUTPUT_DIR_CH02}}/
▶ 支线 B: Prompt-{{04}} {{CHAPTER_4_NAME}}
  - 依赖: {{DEPENDENCY_CH04}}
  - 产物: outputs/{{OUTPUT_DIR_CH04}}/
▶ 支线 C: Prompt-{{05}} {{CHAPTER_5_NAME}}
  - 依赖: {{DEPENDENCY_CH05}}
  - 产物: outputs/{{OUTPUT_DIR_CH05}}/

═══ 阶段 3：串行收束 ═══
▶ Batch-2: Prompt-{{03}} {{CHAPTER_3_NAME}}（支线A完成后）
▶ Batch-3: Prompt-{{06}} {{CHAPTER_6_NAME}}（支线A+C完成后）
▶ Batch-4: Prompt-{{07}} {{CHAPTER_7_NAME}}（全部支线完成后）
▶ Batch-5: Prompt-{{08}} {{CHAPTER_8_NAME}}（全部章节完成后）
```

### 模板 B：只派某个批次

```
【{{PROJECT_NAME}} — Batch-{{X}} 任务】

项目路径: {{PROJECT_DIR_NAME}}/
环境: {{ACTIVATE_COMMAND}}

本批次: Prompt-{{XX}} [{{CHAPTER_NAME}}]
前置依赖: {{DEPENDENCY_ARTIFACTS}}（例: ch01_cleaned_data.csv, ch01_feature_engineered_data.csv）
输入数据: {{INPUT_DATA_PATHS}}（例: outputs/ch01_data_preprocessing/ch01_feature_engineered_data.csv）
输出产物: outputs/{{OUTPUT_DIR}}/
完成标志: {{COMPLETION_ARTIFACT}}（例: outputs/ch{{NN}}_{{CHAPTER_DIR}}/ch{{NN}}_{{KEY_PRODUCT}}.csv）
```

**使用说明**：
- 将 `Batch-{{X}}` 替换为实际批次编号
- 将 `Prompt-{{XX}}` 替换为实际 Prompt 编号
- `前置依赖` 必须逐项列出该批次所需的全部上游产物文件
- `完成标志` 应为该批次最关键的 1~2 个产物文件名

### 模板 C：检查进度（一句话提醒）

```
检查{{PROJECT_NAME}}进度：
Batch-0({{CH01_NUM}}) → Batch-1({{CH02_NUM}}+{{CH04_NUM}}+{{CH05_NUM}}并行) → Batch-2({{CH03_NUM}}) → Batch-3({{CH06_NUM}}) → Batch-4({{CH07_NUM}}) → Batch-5({{CH08_NUM}})
当前应在哪个批次？哪些产物已产出？
```

---

## 四、每个 Prompt 的关键信息速查

### 4.1 速查表模板

| Prompt | 名称 | 输入 | 核心产物 | 后续依赖方 |
|--------|------|------|----------|-----------|
{{CHAPTER_SPEED_TABLE}}

> **填写规则**：行数等于 `{{CHAPTER_COUNT}}`，每行对应一个 Prompt。列格式：`| Prompt-{{NN}} | {{CHAPTER_NAME}} | {{INPUT_FILES}} | {{KEY_ARTIFACT}} | {{DOWNSTREAM_CHAPTERS}} |`

### 4.2 速查表填写规范

| 列名 | 填写规则 |
|------|----------|
| **Prompt** | 两位数字编号，与流程设计文档章节编号对应 |
| **名称** | 章节简称（3~8字），用于快速识别 |
| **输入** | 该章节所需的全部输入数据文件，用 `+` 连接多个文件 |
| **核心产物** | 该章节最重要的 1~3 个产物文件名，用 `,` 分隔 |
| **后续依赖方** | 依赖该章节产物的下游 Prompt 编号，"全部"表示所有后续章节均依赖 |

---

## 五、注意事项

1. **严禁跳批**：每个批次必须等前置依赖全部完成后再启动
2. **数据不覆盖**：每个章节的产物写入独立的 `outputs/ch{{NN}}_{{dir_name}}/` 目录，互不干扰
3. **脚本双格式**：每个章节提供 `{{SCRIPT_FORMAT_1}}`（批量执行）+ `{{SCRIPT_FORMAT_2}}`（交互学习）
4. **全局配置共享**：所有脚本通过 `{{CONFIG_MODULE_PATH}}` 统一路径和参数
5. **{{ADDITIONAL_NOTE_1}}**：{{ADDITIONAL_NOTE_1_DETAIL}}
6. **{{ADDITIONAL_NOTE_2}}**：{{ADDITIONAL_NOTE_2_DETAIL}}

---

# M-3: Phase 4 — execution_prompts.md 完整模板

> 本模块是整个 Skill 文档体系中**最大的模块**，定义了 `execution_prompts.md` 的完整通用模板。
> 该文件是数据分析项目执行阶段的核心指南，覆盖从数据预处理到总结报告的完整分析链条。

---

## 4.0 文档头部模板

### 4.0.1 文档标题

```markdown
# {{PROJECT_NAME}} — 执行Prompt文档
```

- `{{PROJECT_NAME}}`：项目全称，参数化替换。例如"多城市用电负荷全流程分析"。

### 4.0.2 文档说明

```markdown
## 文档说明

本文档为**全流程标准化数据分析执行指南**，覆盖从原始数据预处理到{{FINAL_CHAPTER_GOAL}}的完整分析链条。每个章节的Prompt均设计为**自包含、可独立执行**的单元，可直接复制到AI助手（如ChatGPT、Claude、Cursor等）中执行，也可由数据分析师参照手动操作。

### 适用环境
- **Python 版本**: {{PYTHON_VERSION}}（本地 conda 环境 `{{CONDA_ENV_NAME}}`，路径：`{{PYTHON_PATH}}`）
- **执行方式**: 每个章节均提供 **Jupyter Notebook (.ipynb)** 脚本，按章节编号命名（如 `ch01_{{CH01_NOTEBOOK_NAME}}.ipynb`、`ch02_{{CH02_NOTEBOOK_NAME}}.ipynb`），支持交互式运行、逐步调试、可视化即时预览，便于学习和复现
- **环境管理**: 使用本地 conda 环境 `{{CONDA_ENV_NAME}}`，激活命令 `conda activate {{CONDA_ENV_NAME}}`，通过 `pip install -r requirements.txt` 安装全部依赖。**禁止创建 venv 目录**
- **依赖库清单**: 见 `requirements.txt`
- **推荐 IDE**: Jupyter Notebook / VS Code（含 Jupyter 插件）
```

**参数说明表**：

| 占位符 | 含义 | 示例值 |
|--------|------|--------|
| `{{PROJECT_NAME}}` | 项目全称 | 多城市用电负荷全流程分析 |
| `{{FINAL_CHAPTER_GOAL}}` | 最终章节目标 | 配电网优化 |
| `{{PYTHON_VERSION}}` | Python版本号 | 3.10 |
| `{{CONDA_ENV_NAME}}` | Conda环境名 | py310 |
| `{{PYTHON_PATH}}` | Python解释器路径 | /Users/xxx/miniforge3/envs/py310/bin/python |
| `{{CH01_NOTEBOOK_NAME}}` | 第一章Notebook文件名 | preprocessing |
| `{{CH02_NOTEBOOK_NAME}}` | 第二章Notebook文件名 | load_pattern |

### 4.0.3 全局路径配置代码块

```python
import os

# === 路径配置 ===
DATA_DIR = "{{DATA_DIR}}"
RAW_DATA_FILE = os.path.join(DATA_DIR, "{{RAW_DATA_FILE}}")
OUTPUT_BASE = "{{OUTPUT_BASE}}"

# === 分析实体配置 ===
ENTITY_CONFIG = {
{{ENTITY_CONFIG_ENTRIES}}
}

# === 量纲转换参数（如需要） ===
{{CONVERSION_PARAMS}}

# === 时间/周期映射 ===
{{PERIOD_MAP}}

# === 可视化全局样式 ===
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = {{FIGURE_DPI}}
plt.rcParams['savefig.dpi'] = {{FIGURE_DPI}}
plt.rcParams['font.size'] = {{FONT_SIZE}}
plt.rcParams['figure.figsize'] = ({{FIGURE_WIDTH}}, {{FIGURE_HEIGHT}})
plt.rcParams['axes.unicode_minus'] = False  # 中文显示支持
```

**参数说明表**：

| 占位符 | 含义 | 示例值 |
|--------|------|--------|
| `{{DATA_DIR}}` | 原始数据目录 | "data/" |
| `{{RAW_DATA_FILE}}` | 原始数据文件名 | "dataset.xlsx" |
| `{{OUTPUT_BASE}}` | 输出根目录 | "outputs/" |
| `{{ENTITY_CONFIG_ENTRIES}}` | 实体配置条目，每行一个实体的字典 | 见下方示例 |
| `{{CONVERSION_PARAMS}}` | 量纲转换参数代码 | VOLTAGE = 220 等 |
| `{{PERIOD_MAP}}` | 周期/季节映射字典 | SEASON_MAP = {...} |
| `{{FIGURE_DPI}}` | 图表分辨率 | 150 |
| `{{FONT_SIZE}}` | 默认字体大小 | 12 |
| `{{FIGURE_WIDTH}}` | 默认图宽 | 14 |
| `{{FIGURE_HEIGHT}}` | 默认图高 | 5 |

**`{{ENTITY_CONFIG_ENTRIES}}` 填写示例**：

```python
    "{{ENTITY_1_NAME}}": {
        "sheet": "{{ENTITY_1_SHEET}}",
        "sampling": "{{ENTITY_1_SAMPLING}}",
        "unit": "{{ENTITY_1_UNIT}}",
        "zones": {{ENTITY_1_ZONE_COUNT}},
        "zone_cols": [{{ENTITY_1_ZONE_COLS}}]
    },
    "{{ENTITY_2_NAME}}": {
        "sheet": "{{ENTITY_2_SHEET}}",
        "sampling": "{{ENTITY_2_SAMPLING}}",
        "unit": "{{ENTITY_2_UNIT}}",
        "zones": {{ENTITY_2_ZONE_COUNT}},
        "zone_cols": [{{ENTITY_2_ZONE_COLS}}]
    },
```

### 4.0.4 数据集概况表

```markdown
### 数据集概况

| {{ENTITY_LABEL}} | {{SHEET_COL}} | {{SAMPLING_COL}} | {{ROWS_COL}} | {{TIME_RANGE_COL}} | {{ZONE_COL}} | {{DTYPE_COL}} | {{UNIT_COL}} |
|------|---------|----------|------|----------|--------|----------|----------|
{{DATASET_OVERVIEW_ROWS}}
```

**参数说明表**：

| 占位符 | 含义 | 示例值 |
|--------|------|--------|
| `{{ENTITY_LABEL}}` | 实体列标题 | 城市 |
| `{{SHEET_COL}}` | Sheet名列标题 | Sheet名 |
| `{{SAMPLING_COL}}` | 采样间隔列标题 | 采样间隔 |
| `{{ROWS_COL}}` | 行数列标题 | 行数 |
| `{{TIME_RANGE_COL}}` | 时间范围列标题 | 时间范围 |
| `{{ZONE_COL}}` | Zone数列标题 | Zone数 |
| `{{DTYPE_COL}}` | 数据类型列标题 | 数据类型 |
| `{{UNIT_COL}}` | 单位列标题 | 推测单位 |
| `{{DATASET_OVERVIEW_ROWS}}` | 各实体数据行，每行用 `|` 分隔 | 见下方示例 |

**`{{DATASET_OVERVIEW_ROWS}}` 填写示例**：

```markdown
| 实体A | SheetA | 10min | 88,890 | 2022-09-14 ~ 2024-05-24 | 5 | float64 | 单位A |
| 实体B | SheetB | 30min | 17,501 | 2023-01-09 ~ 2024-01-08 | 2 | int64 | 单位B |
```

---

## 4.1 全局Skill库（可复用模块）

> **注意**：以下 4 个 Skill 的完整可运行代码见 M-5（代码框架模板）§5.2-§5.5。本节仅提供接口说明和使用示例，避免代码重复维护。

以下4个Skill贯穿全流程，每个章节均可调用。请在执行任何章节前，先将这些Skill代码保存为独立文件或直接嵌入Notebook的首个Cell。

---

### Skill-01: 标准数据加载器 (`src/utils/data_loader.py`)

**完整代码见 M-5 §5.2**

核心函数：
| 函数 | 签名 | 说明 |
|------|------|------|
| `load_raw_data` | `load_raw_data(filepath, entity_name, sheet_name=None, engine='openpyxl', time_col='DateTime', **kwargs) -> pd.DataFrame` | 加载指定实体的原始数据，支持 Excel/CSV/Parquet，自动解析时间列并设为索引 |
| `load_all_entities` | `load_all_entities(filepath, entity_config, time_col='DateTime', engine='openpyxl', **kwargs) -> Dict[str, pd.DataFrame]` | 加载全部分析实体，返回 `{实体名: DataFrame}` 字典 |
| `load_preprocessed` | `load_preprocessed(filepath, time_col='DateTime', **kwargs) -> pd.DataFrame` | 加载预处理后的统一数据集 |
| `get_entity_column_prefix` | `get_entity_column_prefix(df, pattern='zone') -> list` | 获取以指定模式开头的列名列表 |

使用示例：
```python
from utils.data_loader import load_raw_data, load_all_entities, load_preprocessed
df = load_raw_data('data/{{RAW_DATA_FILENAME}}', entity_name='{{ENTITY_1_NAME}}')
all_data = load_all_entities('data/{{RAW_DATA_FILENAME}}', ENTITY_CONFIG)
df_clean = load_preprocessed('outputs/ch01_data_preprocessing/ch01_cleaned_data.csv')
zone_cols = get_entity_column_prefix(df, pattern='zone')
```

---

### Skill-02: 标准可视化出图器 (`src/utils/visualizer.py`)

**完整代码见 M-5 §5.3**

核心函数：
| 函数 | 签名 | 说明 |
|------|------|------|
| `plot_time_series` | `plot_time_series(df, time_col, value_col, title, save_path=None, figsize=(14,5), dpi=150, ...) -> None` | 标准时序曲线图 |
| `plot_multi_comparison` | `plot_multi_comparison(data_dict, value_col, save_path=None, figsize=(16,10), ...) -> None` | 多实体横向对比图（子图布局） |
| `plot_heatmap` | `plot_heatmap(pivot_data, title, save_path=None, figsize=(12,8), cmap='YlOrRd', ...) -> None` | 标准热力图 |
| `plot_model_forecast` | `plot_model_forecast(y_true, y_pred, title, save_path=None, figsize=(14,5), ...) -> None` | 预测结果拟合图（真实值 vs 预测值） |
| `plot_grouped_bar` | `plot_grouped_bar(data, x_col, y_col, group_col=None, title='', save_path=None, ...) -> None` | 分组柱状图 |

使用示例：
```python
from utils.visualizer import plot_time_series, plot_multi_comparison, plot_heatmap, plot_model_forecast
plot_time_series(df, time_col='DateTime', value_col='zone1',
                 title='{{ENTITY_1_NAME}} - zone1时序曲线',
                 save_path='outputs/ch02_analysis/zone1_timeseries.png')
plot_multi_comparison(entities_dict, value_col='total_load',
                      save_path='outputs/ch02_analysis/cross_entity_comparison.png')
plot_heatmap(pivot_df, title='小时 x 星期 负荷热力图',
             save_path='outputs/ch02_analysis/weekly_heatmap.png')
plot_model_forecast(y_test, y_pred, title='XGBoost - 预测结果',
                    save_path='outputs/ch04_forecasting/xgb_forecast.png')
```

---

### Skill-03: 标准评估指标计算器 (`src/utils/metrics.py`)

**完整代码见 M-5 §5.4**

核心函数：
| 函数 | 签名 | 说明 |
|------|------|------|
| `calc_mae` | `calc_mae(y_true, y_pred) -> float` | 平均绝对误差 (MAE) |
| `calc_rmse` | `calc_rmse(y_true, y_pred) -> float` | 均方根误差 (RMSE) |
| `calc_mape` | `calc_mape(y_true, y_pred) -> float` | 平均绝对百分比误差 (MAPE, %)，自动跳过 y_true=0 的样本 |
| `calc_r2` | `calc_r2(y_true, y_pred) -> float` | 决定系数 (R-squared) |
| `evaluate_model` | `evaluate_model(y_true, y_pred, model_name) -> Dict[str, float]` | 综合评估单个模型，返回 MAE/RMSE/MAPE/R2 |
| `compare_models` | `compare_models(results_list, sort_by='MAPE', save_path=None) -> pd.DataFrame` | 多模型评估结果对比表，按指定指标排序 |
| `print_model_comparison` | `print_model_comparison(comparison_df) -> None` | 格式化打印模型对比结果 |

使用示例：
```python
from utils.metrics import evaluate_model, compare_models, print_model_comparison
result = evaluate_model(y_test, y_pred, "XGBoost")
results = [
    evaluate_model(y_test, pred_lr, "LinearRegression"),
    evaluate_model(y_test, pred_xgb, "XGBoost"),
    evaluate_model(y_test, pred_lstm, "LSTM"),
]
comparison = compare_models(results, save_path="outputs/ch04/model_comparison.csv")
print_model_comparison(comparison)
```

---

### Skill-04: 标准输出产物管理器 (`src/utils/output_manager.py`)

**完整代码见 M-5 §5.5**

核心函数：
| 函数 | 签名 | 说明 |
|------|------|------|
| `ensure_dir` | `ensure_dir(dir_path) -> str` | 确保输出目录存在，不存在则创建 |
| `get_chapter_dir` | `get_chapter_dir(chapter_key) -> str` | 获取章节输出目录的完整路径（基于 CHAPTER_DIR_MAP） |
| `save_dataframe` | `save_dataframe(df, filename, output_dir, index=True) -> str` | 保存 DataFrame 为 CSV |
| `save_figure` | `save_figure(fig, filename, output_dir, dpi=150) -> str` | 保存 matplotlib 图表 |
| `save_markdown` | `save_markdown(content, filename, output_dir) -> str` | 保存 Markdown 文本 |
| `generate_quality_checklist` | `generate_quality_checklist(items, chapter_num, title=None) -> None` | 生成并打印质量验证清单 |
| `build_chapter_names` | `build_chapter_names(chapter_list) -> Dict[int, str]` | 从章节列表构建章节名称映射字典 |

使用示例：
```python
from utils.output_manager import get_chapter_dir, save_dataframe, save_figure, save_markdown, generate_quality_checklist
output_dir = get_chapter_dir('ch01')
save_dataframe(df, "ch01_cleaned_data.csv", output_dir)
save_figure(fig, "ch01_distribution.png", output_dir)
save_markdown(report_text, "ch01_report.md", output_dir)
generate_quality_checklist([
    "数据无NaN残留",
    "量纲已统一",
    "时间索引连续",
    "异常值已处理",
], chapter_num=1)
```

---

## 4.2 Prompt 重复模板（核心！固定5段式结构）

每个Prompt必须严格遵循以下5段式结构。本节定义了完整的模板骨架，所有章节的Prompt均基于此骨架填充具体内容。

---

### 4.2.1 五段式结构总览

```
# Prompt-{{NN}}: {{CHAPTER_NAME}}

## 一、任务概述
  ### 1.1 本次任务是什么
  ### 1.2 从什么数据出发
  ### 1.3 可以采用什么方法

## 二、执行步骤
  ### Step 1: {{STEP_NAME}}
  ### Step 2: {{STEP_NAME}}
  ...
  ### Step N: {{STEP_NAME}}

## 三、产物总览与结构说明
  ### 3.1 本章全部输出产物
  ### 3.2 关键产物结构详解

## 四、产物后续优化方向
  ### 4.1 当前方案的局限性
  ### 4.2 可进一步优化的方向
  ### 4.3 其他可选方法

## 五、异常处理与问题反馈机制
  ### 5.1 需要向用户确认的问题清单
  ### 5.2 常见异常场景与处理策略
```

---

### 4.2.2 第一段：任务概述（一、任务概述）

```markdown
# Prompt-{{NN}}: {{CHAPTER_NAME}}

## 一、任务概述

### 1.1 本次任务是什么

{{TASK_OVERVIEW_PARAGRAPH_1}}

{{TASK_OVERVIEW_PARAGRAPH_2}}

{{TASK_POSITION_STATEMENT}}

### 1.2 从什么数据出发

{{DATA_SOURCE_DESCRIPTION}}

{{DATA_FIELD_DETAILS}}

### 1.3 可以采用什么方法

{{CORE_METHOD_DESCRIPTION}}

**替代方法**：{{ALTERNATIVE_METHODS_DESCRIPTION}}
```

**各子段填写规范**：

| 子段 | 填写要求 | 必填/可选 |
|------|----------|-----------|
| `1.1 本次任务是什么` | 第一段：一段话描述核心目标和价值。第二段：详细说明具体要做什么。第三段：说明本章节在整体分析流程中的位置。 | 必填 |
| `1.2 从什么数据出发` | 列出输入数据清单：文件名 + 字段说明 + 数据量级。明确数据来源章节。 | 必填 |
| `1.3 可以采用什么方法` | 核心方法列表（可用表格：方法/类型/关键参数/优势/局限）。替代方法说明。 | 必填 |

---

### 4.2.3 第二段：执行步骤（二、执行步骤）

每个Step必须包含以下6个子结构（其中2个为必选，4个为可选）：

```markdown
### Step {{STEP_NUM}}: {{STEP_NAME}}

**本步骤要做什么**           ← 必选，目标描述
**具体操作指引**             ← 可选，详细说明
**代码框架**: ```python...``` ← 可选，可执行代码模板
**本步骤完成后的检查标准**    ← 可选，验证条件
**如果遇到问题请及时反馈**    ← 可选，异常处理指引
**本步骤输出产物**           ← 必选，文件名+路径+结构说明
```

**各子结构填写规范**：

| 子结构 | 填写要求 | 必填/可选 |
|--------|----------|-----------|
| **本步骤要做什么** | 1-3句话描述本步骤的核心目标。说明"为什么需要做这一步"以及"做完后达到什么效果"。 | 必选 |
| **具体操作指引** | 详细的操作步骤说明，包括使用的函数、参数选择理由、注意事项。当步骤较复杂时必须填写。 | 可选（复杂步骤建议填写） |
| **代码框架** | 完整可运行的Python代码块。代码必须包含导入语句、关键变量定义、核心逻辑、结果打印。不能有省略号占位。 | 可选（有代码实现的步骤建议填写） |
| **本步骤完成后的检查标准** | 编号列表，每条为一个可验证的条件。例如"行数与预期一致"、"无NaN残留"等。 | 可选（关键步骤建议填写） |
| **如果遇到问题请及时反馈** | 编号列表，每条描述一个可能的问题场景及处理策略。 | 可选 |
| **本步骤输出产物** | 产物名称 + 文件名 + 存放路径 + 内容说明（列结构、行数量级、用途）。格式统一为列表或表格。 | 必选 |

---

### 4.2.4 第三段：产物总览与结构说明（三、产物总览与结构说明）

```markdown
## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | {{PRODUCT_1_NAME}} | {{PRODUCT_1_FILENAME}} | {{PRODUCT_1_FORMAT}} | {{PRODUCT_1_PATH}} | {{PRODUCT_1_DOWNSTREAM}} |
| 2 | {{PRODUCT_2_NAME}} | {{PRODUCT_2_FILENAME}} | {{PRODUCT_2_FORMAT}} | {{PRODUCT_2_PATH}} | {{PRODUCT_2_DOWNSTREAM}} |
| ... | ... | ... | ... | ... | ... |

### 3.2 关键产物结构详解

**{{KEY_PRODUCT_FILENAME}}**（最重要的产物）:
- 列结构：{{COLUMN_DESCRIPTION}}
- 行数量级：{{ROW_COUNT_ESTIMATE}}
- 用途说明：{{USAGE_DESCRIPTION}}
```

---

### 4.2.5 第四段：产物后续优化方向（四、产物后续优化方向）

```markdown
## 四、产物后续优化方向

### 4.1 当前方案的局限性
1. {{LIMITATION_1}}
2. {{LIMITATION_2}}
3. {{LIMITATION_3}}

### 4.2 可进一步优化的方向
1. {{IMPROVEMENT_1}}
2. {{IMPROVEMENT_2}}
3. {{IMPROVEMENT_3}}

### 4.3 其他可选方法
1. {{ALT_METHOD_1}}
2. {{ALT_METHOD_2}}
3. {{ALT_METHOD_3}}
```

---

### 4.2.6 第五段：异常处理与问题反馈机制（五、异常处理与问题反馈机制）

```markdown
## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
1. {{CONFIRM_QUESTION_1}}
2. {{CONFIRM_QUESTION_2}}

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| {{SCENARIO_1}} | {{CRITERION_1}} | {{STRATEGY_1}} | {{NEED_CONFIRM_1}} |
| {{SCENARIO_2}} | {{CRITERION_2}} | {{STRATEGY_2}} | {{NEED_CONFIRM_2}} |
| {{SCENARIO_3}} | {{CRITERION_3}} | {{STRATEGY_3}} | {{NEED_CONFIRM_3}} |
```

---

## 4.3 三种 Prompt 原型的完整示例

以下提供三种章节原型的完整Prompt示例，每种原型均包含实质性的Step内容和代码框架。

---

### 4.3.1 原型A：数据预处理型 Prompt 示例

> **适用场景**：数据清洗、格式统一、缺失值处理、特征工程等数据准备阶段。

```markdown
# Prompt-01: 数据预处理

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**基础起点**，目标是读取{{ENTITY_COUNT}}个分析实体（{{ENTITY_LIST}}）的原始数据，解决数据中存在的**采样频率不统一**（{{SAMPLING_A}} vs {{SAMPLING_B}}）、**计量单位不一致**（{{UNIT_A}} vs {{UNIT_B}}）、**潜在缺失值和异常值**等问题，最终输出一份统一时间粒度、统一量纲、高质量的标准数据集，为后续所有分析章节提供可靠的数据基础。

原始数据中，{{ENTITY_GROUP_A}}采用{{SAMPLING_A}}高频采样，数值为{{UNIT_A}}，量级在{{RANGE_A}}之间；{{ENTITY_GROUP_B}}采用{{SAMPLING_B}}采样，数值为{{UNIT_B}}，量级在{{RANGE_B}}之间。这种差异需要在预处理阶段彻底解决。

### 1.2 从什么数据出发

数据文件为 `{{RAW_DATA_FILE}}`，包含{{SHEET_COUNT}}个Sheet，每个Sheet对应一个分析实体。所有Sheet都包含一个 `DateTime` 时间列和若干 `zone` 数值列。

具体结构如下：
{{ENTITY_DATA_DESCRIPTIONS}}

初步探查显示所有时间列无缺失值，zone列的数值分布需要进一步检查。

### 1.3 可以采用什么方法

核心处理方法包括：
1. **线性插值上采样**：将{{ENTITY_GROUP_B}}的{{SAMPLING_B}}数据上采样至{{SAMPLING_A}}，使用 `DataFrame.resample('{{RESAMPLE_FREQ}}').interpolate(method='linear')`。线性插值是时序数据上采样的标准做法，在数据变化平缓的场景中表现良好。
2. **物理公式量纲换算**：将{{UNIT_A}}转换为{{UNIT_B}}，公式为 `{{CONVERSION_FORMULA}}`。
3. **3sigma准则异常检测**：计算每个zone的均值和标准差，将超出 [mu-3*sigma, mu+3*sigma] 范围的值标记为异常。3sigma准则在正态分布假设下覆盖99.7%的正常数据，是工程上常用的异常值判定方法。
4. **线性插值填补**：对标记为异常的值（以及可能的缺失值）使用线性插值替换，保持时序连续性。

替代方法：样条插值（cubic spline，更平滑但可能引入过拟合）、中位数替换（对极端异常更鲁棒但会改变分布形状）、KNN插值（利用相似时段的数据但计算成本高）。

## 二、执行步骤

> **步骤分组说明**：
> - **通用必选步骤**（Step 1-4）：所有数据分析项目都需要执行
> - **可选步骤**（Step 5-9）：根据数据特征按需启用，不需要的步骤直接跳过

### Step 1: 数据读取与结构探查

**本步骤要做什么**
读取数据文件中{{SHEET_COUNT}}个Sheet的数据，查看每个Sheet的基本信息（行数、列数、数据类型、缺失值情况、数值范围），形成对数据的整体认知。

**具体操作指引**
使用 `pd.read_excel()` 或 `pd.read_csv()` 逐个读取Sheet，调用 `.info()`、`.describe()`、`.head()`、`.isnull().sum()` 查看数据概况。特别关注：各zone列的min/max值是否存在负值或极端值、缺失值的数量和分布模式。

**代码框架**:
```python
import pandas as pd
import numpy as np

RAW_FILE = "{{RAW_DATA_FILE}}"
entities = {{ENTITY_NAME_LIST}}

for entity in entities:
    df = pd.read_excel(RAW_FILE, sheet_name=entity, engine='openpyxl')
    print(f"\n{'='*50}")
    print(f"实体: {entity}")
    print(f"{'='*50}")
    print(f"形状: {df.shape}")
    print(f"\n数据类型:\n{df.dtypes}")
    print(f"\n缺失值:\n{df.isnull().sum()}")
    print(f"\n描述统计:\n{df.describe()}")
    print(f"\n前3行:\n{df.head(3)}")
    print(f"\n时间范围: {df['DateTime'].min()} ~ {df['DateTime'].max()}")
```

**本步骤完成后的检查标准**
- {{SHEET_COUNT}}个Sheet全部成功读取，无报错
- 每个Sheet的行数与预期一致
- DateTime列成功解析为datetime类型
- zone列的min值符合业务逻辑（如不应为负值）

**如果遇到问题请及时反馈**
- 如果某个Sheet读取失败，检查Sheet名称是否与预期完全一致（注意大小写和空格）
- 如果DateTime列解析失败，检查原始格式是否为标准datetime格式

**本步骤输出产物**
- `ch01_data_profile_report.md` — 数据概况报告，存放于 `outputs/ch01_data_preprocessing/`

### Step 2: 缺失值检测与统计

**本步骤要做什么**
全面检测所有Sheet中所有列的缺失值情况，统计缺失率，判断是否需要特殊处理。如果缺失率超过5%，需要记录并报告。

**具体操作指引**
对每个实体的DataFrame，计算每列的缺失数量和缺失百分比。将结果汇总为一张统计表。

**代码框架**:
```python
missing_stats = []
for entity in entities:
    df = pd.read_excel(RAW_FILE, sheet_name=entity, engine='openpyxl')
    for col in df.columns:
        missing_stats.append({
            'entity': entity,
            'column': col,
            'missing_count': df[col].isnull().sum(),
            'missing_rate': df[col].isnull().mean() * 100,
            'total_rows': len(df)
        })
missing_df = pd.DataFrame(missing_stats)
print(missing_df.to_string(index=False))
```

**本步骤完成后的检查标准**
- 缺失统计表覆盖全部{{SHEET_COUNT}}个实体、全部列
- 如果存在缺失率>5%的列，需在报告中特别标注

**本步骤输出产物**
- `ch01_missing_stats.csv` — 缺失值统计表

### Step 3: 时间戳解析与标准化

**本步骤要做什么**
将所有实体的DateTime列统一解析为datetime64类型，设置为DataFrame的索引，并确保按时间升序排列。移除时区信息（如有），统一为naive datetime。

**代码框架**:
```python
for entity in entities:
    df = pd.read_excel(RAW_FILE, sheet_name=entity, engine='openpyxl')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.set_index('DateTime').sort_index()
    expected_freq = '{{EXPECTED_FREQ_A}}' if entity in {{ENTITY_GROUP_A_LIST}} else '{{EXPECTED_FREQ_B}}'
    print(f"{entity}: 采样频率={expected_freq}, 时间范围={df.index.min()} ~ {df.index.max()}")
```

**本步骤输出产物**
- 无独立文件（本步骤为中间处理，结果在内存中传递给后续步骤）

### Step 4: 时序对齐（{{ENTITY_GROUP_B}} {{SAMPLING_B}} -> {{SAMPLING_A}} 上采样）

**本步骤要做什么**
将{{ENTITY_GROUP_B}}的{{SAMPLING_B}}采样数据通过线性插值上采样至{{SAMPLING_A}}，使其与其他实体的时间粒度一致。这是后续跨实体对比分析的前提条件。

**具体操作指引**
使用 `df.resample('{{RESAMPLE_FREQ}}').interpolate(method='linear', limit_direction='both')` 进行上采样。注意：上采样后的数据点是基于插值生成的，不是真实测量值，在后续分析中需要标注这一差异。

**代码框架**:
```python
for entity in {{ENTITY_GROUP_B_LIST}}:
    df = pd.read_excel(RAW_FILE, sheet_name=entity, engine='openpyxl')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.set_index('DateTime').sort_index()

    df_resampled = df.resample('{{RESAMPLE_FREQ}}').interpolate(method='linear', limit_direction='both')
    print(f"{entity} 上采样: {len(df)}行 -> {len(df_resampled)}行")
```

**本步骤完成后的检查标准**
- 上采样后行数约为原来的{{UPSAMPLE_RATIO}}倍
- 上采样后的数据无NaN残留
- 插值曲线在原始数据点处精确通过（可通过抽样验证）

**本步骤输出产物**
- `ch01_{{ENTITY_GROUP_B}}_resampled.csv` — 上采样后的数据

### Step 5: [可选] 量纲统一（{{UNIT_A}} -> {{UNIT_B}}）

**本步骤要做什么**
将{{ENTITY_GROUP_A}}的数据从{{UNIT_A}}统一换算为{{UNIT_B}}，使所有实体的计量单位完全一致。

**具体操作指引**
使用物理公式 `{{CONVERSION_FORMULA}}` 进行换算。换算后，所有zone数据的单位统一为{{UNIT_B}}。

**代码框架**:
```python
{{CONVERSION_PARAMS_CODE}}

for entity in {{ENTITY_GROUP_A_LIST}}:
    df = pd.read_excel(RAW_FILE, sheet_name=entity, engine='openpyxl')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.set_index('DateTime').sort_index()

    zone_cols = [c for c in df.columns if c.startswith('zone')]
    for col in zone_cols:
        df[col] = df[col] * {{CONVERSION_FACTOR}}

    print(f"{entity} 换算后范围: {df[zone_cols].min().min():.2f} ~ {df[zone_cols].max().max():.2f} {{UNIT_B}}")
```

**本步骤完成后的检查标准**
- 换算后所有实体的数值量级可比
- 换算后无负值出现

**本步骤输出产物**
- `ch01_unified_all_entities.csv` — 量纲统一后的全实体数据（合并为一个文件，增加entity列标识）

### Step 6: [可选] 异常值检测（3sigma准则）

**本步骤要做什么**
对每个实体的每个zone列，使用3sigma准则检测异常值。标记但不直接删除，生成异常值标记文件供后续审查。

**代码框架**:
```python
outlier_flags = []
for entity in entities:
    df = load_raw_data(RAW_FILE, entity)
    zone_cols = [c for c in df.columns if c.startswith('zone')]
    for col in zone_cols:
        mean = df[col].mean()
        std = df[col].std()
        lower = mean - 3 * std
        upper = mean + 3 * std
        mask = (df[col] < lower) | (df[col] > upper)
        n_outliers = mask.sum()
        outlier_rate = mask.mean() * 100
        outlier_flags.append({
            'entity': entity, 'zone': col,
            'mean': round(mean, 2), 'std': round(std, 2),
            'lower_bound': round(lower, 2), 'upper_bound': round(upper, 2),
            'outlier_count': n_outliers, 'outlier_rate': round(outlier_rate, 4)
        })
        print(f"{entity}/{col}: 均值={mean:.2f}, 标准差={std:.2f}, 异常值={n_outliers}个({outlier_rate:.2f}%)")
outlier_df = pd.DataFrame(outlier_flags)
```

**本步骤完成后的检查标准**
- 异常值比例通常应在0.3%以下（3sigma准则的理论值）
- 如果某个zone的异常率>1%，需要检查是否存在系统性问题

**本步骤输出产物**
- `ch01_outlier_flags.csv` — 异常值检测结果表

### Step 7: [可选] 异常值处理（线性插值替换）

**本步骤要做什么**
将Step 6中标记的异常值替换为线性插值值，同时处理可能的缺失值。处理后的数据即为"清洗后数据"。

**代码框架**:
```python
for entity in entities:
    df = load_raw_data(RAW_FILE, entity)
    zone_cols = [c for c in df.columns if c.startswith('zone')]
    for col in zone_cols:
        mean = df[col].mean()
        std = df[col].std()
        mask = (df[col] < mean - 3*std) | (df[col] > mean + 3*std)
        df.loc[mask, col] = np.nan
        df[col] = df[col].interpolate(method='linear')
    assert df[zone_cols].isnull().sum().sum() == 0, "存在未处理的NaN!"
```

**本步骤完成后的检查标准**
- 全部zone列无NaN残留
- 数据分布无突变断裂（可通过直方图验证）
- 异常值替换后的数值在合理范围内

**本步骤输出产物**
- `ch01_cleaned_data.csv` — 清洗后的全实体统一数据集

### Step 8: [可选] 时间特征工程

**本步骤要做什么**
基于DateTime索引，衍生出一系列时间特征列，支撑后续的周期规律分析、预测建模等任务。

**具体操作指引**
衍生以下特征：hour（小时0-23）、day_of_week（星期0-6）、is_weekend（是否周末）、month（月份1-12）、season（季节）、year（年份）。季节映射遵循{{SEASON_MAPPING_RULE}}。

**代码框架**:
```python
SEASON_MAP = {{SEASON_MAP_DICT}}

df['hour'] = df.index.hour
df['day_of_week'] = df.index.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df['month'] = df.index.month
df['season'] = df['month'].map(SEASON_MAP)
df['year'] = df.index.year
```

**本步骤完成后的检查标准**
- 特征列完整：hour(0-23), day_of_week(0-6), is_weekend(0/1), month(1-12), season({{SEASON_VALUES}}), year
- 无NaN

**本步骤输出产物**
- `ch01_feature_engineered_data.csv` — 含时间特征的全实体数据集（这是后续所有章节的主要输入数据）

### Step 9: [可选] 数据质量报告生成

**本步骤要做什么**
汇总以上所有步骤的处理结果，生成一份完整的数据质量报告，包括：原始数据概况、缺失值统计、异常值统计、量纲换算参数、时间对齐说明、特征工程说明。

**代码框架**:
```python
quality_report = f"""# 数据质量报告

## 1. 原始数据概况
- 数据文件: {RAW_FILE}
- 实体数量: {len(entities)}
- 各实体行数: {entity_row_summary}

## 2. 缺失值统计
{missing_summary}

## 3. 异常值统计
{outlier_summary}

## 4. 量纲换算
- 换算公式: {{CONVERSION_FORMULA}}
- 换算参数: {{CONVERSION_PARAMS}}

## 5. 时间对齐
- 上采样实体: {{ENTITY_GROUP_B_LIST}}
- 上采样方法: 线性插值
- 上采样比例: {{UPSAMPLE_RATIO}}

## 6. 特征工程
- 新增特征: hour, day_of_week, is_weekend, month, season, year
"""

save_markdown(quality_report, "ch01_data_quality_report.md", chapter_num=1)
```

**本步骤输出产物**
- `ch01_data_quality_report.md` — 数据质量报告

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 数据概况报告 | ch01_data_profile_report.md | Markdown | outputs/ch01_data_preprocessing/ | 参考 |
| 2 | 缺失值统计表 | ch01_missing_stats.csv | CSV | outputs/ch01_data_preprocessing/ | 参考 |
| 3 | 上采样数据 | ch01_{{ENTITY_GROUP_B}}_resampled.csv | CSV | outputs/ch01_data_preprocessing/ | 中间产物 |
| 4 | 量纲统一数据 | ch01_unified_all_entities.csv | CSV | outputs/ch01_data_preprocessing/ | 中间产物 |
| 5 | 异常值标记表 | ch01_outlier_flags.csv | CSV | outputs/ch01_data_preprocessing/ | Prompt-03参考 |
| 6 | 清洗后数据集 | ch01_cleaned_data.csv | CSV | outputs/ch01_data_preprocessing/ | Prompt-02,03,05 |
| 7 | 含特征工程数据集 | ch01_feature_engineered_data.csv | CSV | outputs/ch01_data_preprocessing/ | Prompt-02,03,04,05 |
| 8 | 数据质量报告 | ch01_data_quality_report.md | Markdown | outputs/ch01_data_preprocessing/ | 参考 |

### 3.2 关键产物结构详解

**ch01_feature_engineered_data.csv**（最重要的产物）:
- 列结构：DateTime(索引), entity(str), zone1~zoneN(float64, 单位{{UNIT_B}}), hour(int), day_of_week(int), is_weekend(int), month(int), season(str), year(int)
- 行数量级：约{{TOTAL_ROW_ESTIMATE}}行（{{ENTITY_COUNT}}个实体合并）
- 这是后续Prompt-02~05的主要输入数据

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 量纲换算使用固定的转换参数，实际值可能随时间和区域变化
- 上采样引入了非真实测量数据点
- 3sigma准则假设数据近似正态分布，对偏态分布可能不适用

### 4.2 可进一步优化的方向
- 使用样条插值替代线性插值，获得更平滑的上采样曲线
- 使用IQR（四分位距）方法替代3sigma准则，对偏态分布更鲁棒
- 增加节假日特征

### 4.3 其他可选方法
- 孤立森林（Isolation Forest）：无监督异常检测，不依赖分布假设
- DBSCAN聚类异常检测：基于密度，适合局部异常检测
- 移动中位数滤波：对时序数据的平滑去噪效果优于线性插值

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 如果某个zone列存在大量缺失值（>10%），需确认是删除该zone还是使用插值填补
- 如果量纲换算后的数值范围与预期严重不符，需确认转换参数是否合理
- 如果上采样导致数据失真（如出现负值），需确认是否继续

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| DateTime解析失败 | 报TypeError或ValueError | 检查原始格式，尝试指定format参数 | 否 |
| 上采样后出现NaN | resample后isnull()>0 | 使用limit_direction='both'或ffill/bfill | 否 |
| 换算后出现负值 | min(zone)<0 | 检查原始数据，将负值设为0 | 是 |
| 异常率>5% | outlier_rate>5 | 可能存在数据质量问题，需人工审查 | 是 |
| 内存不足 | MemoryError | 分实体处理，避免一次性加载全部数据 | 否 |
```

---

### 4.3.2 原型B：分析探索型 Prompt 示例

> **适用场景**：描述性统计、模式发现、可视化分析、聚类分类等探索性分析阶段。

```markdown
# Prompt-02: {{ANALYSIS_TOPIC}}

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**核心探索阶段**，基于第一章预处理后的标准化数据，从多个维度深入挖掘{{ENTITY_COUNT}}个实体的{{ANALYSIS_TARGET}}规律。核心目标包括：

1. **量化基本统计特征**：计算各实体各zone的均值、中位数、标准差、波动率、{{KEY_RATE}}，建立{{ANALYSIS_TARGET}}特征的量化基准
2. **揭示日内{{ANALYSIS_TARGET}}节奏**：绘制24小时连续曲线，识别早晚高峰和午间低谷的时段分布
3. **对比工作日/周末差异**：分析工作日与周末曲线的形态差异，量化作息对{{ANALYSIS_TARGET}}的影响
4. **分析跨实体区域差异**：对比{{ENTITY_COUNT}}个实体{{ANALYSIS_TARGET}}水平、波动特征，结合背景知识解释差异成因
5. **区分{{CATEGORY_A}}/{{CATEGORY_B}}**：尝试将zone分为{{CATEGORY_A}}和{{CATEGORY_B}}两种类型，对比其差异化特征

本章的输出将为后续的{{DOWNSTREAM_TASK_A}}提供统计基础，为{{DOWNSTREAM_TASK_B}}提供特征理解。

### 1.2 从什么数据出发

输入数据为 `outputs/ch01_data_preprocessing/ch01_feature_engineered_data.csv`，这是第一章预处理后的最终产物。

该数据集包含以下关键字段：
- **DateTime**（索引）：{{TIME_GRANULARITY}}粒度的时间戳
- **entity**：实体标识（{{ENTITY_LIST}}）
- **zone1~zoneN**：各zone的{{VALUE_COL}}（单位{{VALUE_UNIT}}），已统一量纲
- **hour**：小时（0-23）
- **day_of_week**：星期（0=周一, 6=周日）
- **is_weekend**：是否周末（0/1）
- **month**：月份（1-12）
- **season**：季节（{{SEASON_VALUES}}）
- **year**：年份

### 1.3 可以采用什么方法

**描述性统计分析**：使用pandas的groupby+agg进行分组聚合统计，计算均值、中位数、标准差、最小值、最大值、变异系数(CV=std/mean)、{{KEY_RATE}}(mean/max)。

**日内规律分析**：按hour分组取均值，绘制24小时曲线。分实体、分zone、分工作日/周末分别绘制。

**周期性分析**：使用seaborn的heatmap绘制"小时 x 星期"的热力图，直观展示周内周期规律。

**跨实体对比**：使用matplotlib的subplots多子图布局，将{{ENTITY_COUNT}}个实体曲线放在同一画布上对比。

**{{CATEGORY_A}}/{{CATEGORY_B}}分层**：
- 优先策略：检查zone列命名是否含"{{CATEGORY_A_KEYWORD}}"/"{{CATEGORY_B_KEYWORD}}"等关键词
- 备选策略：基于{{KEY_RATE}}波动率(CV)和日内峰谷比进行KMeans二分类

替代方法：DBSCAN密度聚类（对噪声更鲁棒）、GMM高斯混合模型（提供软分类概率）、基于领域知识的规则分类。

## 二、执行步骤

> **说明**：以上可视化步骤为推荐模板，实际项目应根据分析目标选择合适的可视化类型。
> 常见可视化类型：折线图、柱状图、热力图、散点图、箱线图、小提琴图、分布图、相关性矩阵。

### Step 1: 描述性统计总表

**本步骤要做什么**
计算每个实体每个zone的描述性统计指标，形成一张完整的统计总表。

**具体操作指引**
按entity分组，对每个zone列计算：mean, median, std, min, max, skew（偏度）, kurtosis（峰度）。额外计算衍生指标：CV（变异系数=std/mean）、{{KEY_RATE}}（mean/max）。

**代码框架**:
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_feature_engineered_data.csv", parse_dates=['DateTime'])
df = df.set_index('DateTime')

zone_cols = [c for c in df.columns if c.startswith('zone')]
stats = df.groupby('entity')[zone_cols].agg(['mean','median','std','min','max','skew']).round(4)
print(stats.to_string())
```

**本步骤完成后的检查标准**
- 统计表覆盖全部{{ENTITY_COUNT}}个实体、全部zone
- 所有均值符合业务逻辑（如>0）
- 标准差合理（不应大于均值的数倍）
- 无NaN

**本步骤输出产物**
- `ch02_descriptive_stats.csv` — 描述性统计总表

### Step 2: {{KEY_RATE}}与波动率计算

**本步骤要做什么**
计算每个实体每个zone的{{KEY_RATE}}和变异系数，这两个指标是衡量{{ANALYSIS_TARGET}}稳定性的核心指标。

**代码框架**:
```python
metrics = []
for entity in df['entity'].unique():
    entity_df = df[df['entity'] == entity]
    for col in zone_cols:
        if col in entity_df.columns:
            mean_val = entity_df[col].mean()
            max_val = entity_df[col].max()
            std_val = entity_df[col].std()
            metrics.append({
                'entity': entity, 'zone': col,
                'mean': round(mean_val, 2),
                'max': round(max_val, 2),
                'std': round(std_val, 2),
                '{{KEY_RATE}}': round(mean_val/max_val, 4) if max_val > 0 else 0,
                'cv': round(std_val/mean_val, 4) if mean_val > 0 else 0
            })
metrics_df = pd.DataFrame(metrics)
```

**本步骤输出产物**
- `ch02_{{KEY_RATE}}_cv.csv` — {{KEY_RATE}}和变异系数表

### Step 3: {{VISUALIZATION_1_NAME}}（{{VISUALIZATION_1_DESC}}）

**本步骤要做什么**
绘制每个实体每个zone的{{VISUALIZATION_1_DESC}}。

**具体操作指引**
按hour分组取均值，使用折线图绘制。每个实体单独一张图（多zone叠加），同时绘制一张全实体对比图。区分工作日和周末分别绘制。

**代码框架**:
```python
for entity in df['entity'].unique():
    entity_df = df[df['entity'] == entity]
    entity_zone_cols = [c for c in entity_df.columns if c.startswith('zone')]

    hourly = entity_df.groupby('hour')[entity_zone_cols].mean()

    fig, ax = plt.subplots(figsize=(14, 5), dpi=150)
    for col in entity_zone_cols:
        ax.plot(hourly.index, hourly[col], label=col, linewidth=1.5)
    ax.set_title(f'{entity} - 24小时平均曲线', fontsize=14, fontweight='bold')
    ax.set_xlabel('小时', fontsize=12)
    ax.set_ylabel('{{VALUE_UNIT}}', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(0, 24))
    plt.tight_layout()
    plt.savefig(f'outputs/ch02_{{CHAPTER_DIR}}/ch02_daily_curve_{entity.lower()}.png', dpi=150)
    plt.close()
```

**本步骤完成后的检查标准**
- 曲线能清晰识别高峰时段
- 曲线平滑无异常跳变
- X轴为0-23小时

**本步骤输出产物**
- `ch02_daily_curve_{entity}.png` — 各实体日内曲线（{{ENTITY_COUNT}}张）

### Step 4: {{VISUALIZATION_2_NAME}}（{{VISUALIZATION_2_DESC}}）

**本步骤要做什么**
在同一张图上叠加{{VISUALIZATION_2_DESC}}，直观展示差异。

**代码框架**:
```python
for entity in df['entity'].unique():
    entity_df = df[df['entity'] == entity]
    entity_zone_cols = [c for c in entity_df.columns if c.startswith('zone')]
    entity_df['total'] = entity_df[entity_zone_cols].mean(axis=1)

    weekday = entity_df[entity_df['is_weekend'] == 0].groupby('hour')['total'].mean()
    weekend = entity_df[entity_df['is_weekend'] == 1].groupby('hour')['total'].mean()

    fig, ax = plt.subplots(figsize=(14, 5), dpi=150)
    ax.plot(weekday.index, weekday, label='工作日', linewidth=1.5, color='steelblue')
    ax.plot(weekend.index, weekend, label='周末', linewidth=1.5, color='tomato')
    ax.set_title(f'{entity} - 工作日 vs 周末', fontsize=14, fontweight='bold')
    ax.set_xlabel('小时', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(0, 24))
    plt.tight_layout()
    plt.savefig(f'outputs/ch02_{{CHAPTER_DIR}}/ch02_weekday_vs_weekend_{entity.lower()}.png', dpi=150)
    plt.close()
```

**本步骤输出产物**
- `ch02_weekday_vs_weekend_{entity}.png` — 工作日vs周末对比图（{{ENTITY_COUNT}}张）

### Step 5: {{VISUALIZATION_3_NAME}}（{{VISUALIZATION_3_DESC}}）

**本步骤要做什么**
绘制{{VISUALIZATION_3_DESC}}，直观展示{{ANALYSIS_TARGET}}的分布规律。

**代码框架**:
```python
for entity in df['entity'].unique():
    entity_df = df[df['entity'] == entity]
    entity_zone_cols = [c for c in entity_df.columns if c.startswith('zone')]
    entity_df['total'] = entity_df[entity_zone_cols].mean(axis=1)

    pivot = entity_df.pivot_table(values='total', index='hour', columns='day_of_week', aggfunc='mean')
    pivot.columns = ['周一','周二','周三','周四','周五','周六','周日']

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    sns.heatmap(pivot, ax=ax, cmap='YlOrRd', annot=True, fmt='.1f', linewidths=0.5)
    ax.set_title(f'{entity} - 周内热力图 ({{VALUE_UNIT}})', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'outputs/ch02_{{CHAPTER_DIR}}/ch02_weekly_heatmap_{entity.lower()}.png', dpi=150)
    plt.close()
```

**本步骤输出产物**
- `ch02_weekly_heatmap_{entity}.png` — 周内热力图（{{ENTITY_COUNT}}张）

### Step 6: 跨实体横向对比

**本步骤要做什么**
将{{ENTITY_COUNT}}个实体的曲线放在同一坐标系中对比，分析区域差异。

**代码框架**:
```python
fig, axes = plt.subplots(len(entities), 1, figsize=(16, 5*len(entities)), dpi=150, sharex=True)
if len(entities) == 1:
    axes = [axes]

for i, entity in enumerate(entities):
    entity_df = df[df['entity'] == entity]
    entity_zone_cols = [c for c in entity_df.columns if c.startswith('zone')]
    entity_df['total'] = entity_df[entity_zone_cols].mean(axis=1)
    hourly = entity_df.groupby('hour')['total'].mean()
    axes[i].plot(hourly.index, hourly.values, linewidth=1.5)
    axes[i].set_title(f'{entity}', fontsize=12, fontweight='bold')
    axes[i].grid(True, alpha=0.3)

axes[-1].set_xlabel('小时', fontsize=12)
plt.tight_layout()
plt.savefig('outputs/ch02_{{CHAPTER_DIR}}/ch02_cross_entity_comparison.png', dpi=150)
plt.close()
```

**本步骤输出产物**
- `ch02_cross_entity_comparison.png` — 跨实体对比图

### Step 7: {{CATEGORY_A}}/{{CATEGORY_B}}分层

**本步骤要做什么**
基于{{ANALYSIS_TARGET}}特征（波动率CV、日内峰谷比）对zone进行{{CATEGORY_A}}/{{CATEGORY_B}}二分类。

**具体操作指引**
对每个zone计算CV和峰谷比，使用KMeans(n_clusters=2)聚类。通过分析两个簇的中心特征判断哪个簇是{{CATEGORY_B}}、哪个是{{CATEGORY_A}}。

**代码框架**:
```python
from sklearn.cluster import KMeans

cluster_features = []
for entity in df['entity'].unique():
    entity_df = df[df['entity'] == entity]
    for col in zone_cols:
        if col in entity_df.columns:
            hourly = entity_df.groupby('hour')[col].mean()
            cv = entity_df[col].std() / entity_df[col].mean()
            peak_valley_ratio = hourly.max() / hourly.min() if hourly.min() > 0 else 0
            cluster_features.append({'entity': entity, 'zone': col, 'cv': cv, 'peak_valley_ratio': peak_valley_ratio})

cluster_df = pd.DataFrame(cluster_features)
features = cluster_df[['cv', 'peak_valley_ratio']].values
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
cluster_df['cluster'] = kmeans.fit_predict(features)

for c in [0, 1]:
    subset = cluster_df[cluster_df['cluster'] == c]
    print(f"簇{c}: 平均CV={subset['cv'].mean():.4f}, 平均峰谷比={subset['peak_valley_ratio'].mean():.2f}")
```

**本步骤完成后的检查标准**
- 两个簇的特征差异明显
- 分类结果与曲线形态自洽

**本步骤输出产物**
- `ch02_{{CATEGORY_A}}_{{CATEGORY_B}}_class.csv` — 分类结果表

### Step 8: {{CATEGORY_A}} vs {{CATEGORY_B}} 对比分析

**本步骤要做什么**
基于Step 7的分类结果，分别绘制{{CATEGORY_A}}和{{CATEGORY_B}}的日内曲线，量化两类差异。

**代码框架**:
```python
for cluster_id in [0, 1]:
    cluster_zones = cluster_df[cluster_df['cluster'] == cluster_id]['zone'].tolist()
    cluster_entities = cluster_df[cluster_df['cluster'] == cluster_id]['entity'].unique()

    all_hourly = []
    for entity in cluster_entities:
        entity_df = df[df['entity'] == entity]
        for col in cluster_zones:
            if col in entity_df.columns:
                hourly = entity_df.groupby('hour')[col].mean()
                all_hourly.append(hourly)

    if all_hourly:
        avg_hourly = pd.concat(all_hourly, axis=1).mean(axis=1)
        fig, ax = plt.subplots(figsize=(14, 5), dpi=150)
        ax.plot(avg_hourly.index, avg_hourly.values, linewidth=1.5)
        ax.set_title(f'簇{cluster_id} 日内曲线', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(0, 24))
        plt.tight_layout()
        plt.savefig(f'outputs/ch02_{{CHAPTER_DIR}}/ch02_cluster_{cluster_id}_curve.png', dpi=150)
        plt.close()
```

**本步骤输出产物**
- `ch02_{{CATEGORY_A}}_vs_{{CATEGORY_B}}_comparison.png` — 对比图

## 三、产物总览与结构说明

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用章节 |
|------|----------|--------|------|-------------|
| 1 | 描述性统计总表 | ch02_descriptive_stats.csv | CSV | Prompt-03 |
| 2 | {{KEY_RATE}}变异系数表 | ch02_{{KEY_RATE}}_cv.csv | CSV | Prompt-06,07 |
| 3 | 日内曲线 | ch02_daily_curve_{entity}.png | PNG | 报告配图 |
| 4 | 工作日vs周末对比 | ch02_weekday_vs_weekend_{entity}.png | PNG | 报告配图 |
| 5 | 周内热力图 | ch02_weekly_heatmap_{entity}.png | PNG | 报告配图 |
| 6 | 跨实体对比图 | ch02_cross_entity_comparison.png | PNG | 报告配图 |
| 7 | 分类表 | ch02_{{CATEGORY_A}}_{{CATEGORY_B}}_class.csv | CSV | Prompt-03,06 |
| 8 | 分类对比图 | ch02_{{CATEGORY_A}}_vs_{{CATEGORY_B}}_comparison.png | PNG | 报告配图 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 分层依赖无监督聚类，缺乏真实标签验证
- 跨实体对比未考虑规模差异的标准化
- 日内曲线仅使用均值，未展示置信区间或分位数范围

### 4.2 可进一步优化的方向
- 引入分位数带（5%-95%）替代单一均值曲线
- 计算人均/单位化指标消除规模差异
- 增加月度/季节维度的曲线对比
- 使用DTW量化实体间曲线的相似度

### 4.3 其他可选方法
- 小波变换：在时频域分析多尺度周期特征
- 隐马尔可夫模型（HMM）：识别隐含状态
- 自组织映射（SOM）：高维特征的可视化降维

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 如果某zone的CV>1，需单独分析
- 如果KMeans分类结果不理想，需尝试调整特征或使用GMM

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 某zone的CV>1 | 变异系数异常大 | 可能存在大量零值或间歇性数据 | 是 |
| KMeans分类不理想 | 两簇特征差异不明显 | 增加更多维度或使用GMM | 是 |
| 实体间量级差异过大 | 最大值/最小值>100倍 | 检查量纲换算是否正确 | 是 |
| 工作日/周末差异不显著 | 曲线几乎重叠 | 可能以{{CATEGORY_B}}为主 | 否 |
```

---

### 4.3.3 原型C：总结报告型 Prompt 示例

> **适用场景**：成果汇总、指标提炼、局限性分析、未来展望等总结收尾阶段。

```markdown
# Prompt-{{FINAL_NN}}: 总结与展望

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**收尾章节**，承担两项核心任务：一是对前{{PREV_CHAPTER_COUNT}}章的全部研究成果进行系统性汇总，提炼关键发现和核心数据指标，形成一份完整的"研究结论总览"；二是客观评估本次研究的局限性，并提出未来可拓展的研究方向。

汇总工作不是简单的重复罗列，而是需要从"{{ANALYSIS_CHAIN_SUMMARY}}"全链条中，提炼出最具价值的结论。例如："哪个实体的{{ANALYSIS_TARGET}}波动最大"、"最优预测模型是哪个、精度如何"、"{{COMPARISON_RESULT}}"等。这些结论将直接服务于最终的结题报告或学术论文的"结论"章节。

未来展望部分应结合当前研究的不足，提出具体的改进路径——例如引入多维外部指标提升预测精度、拓展多维度对比、完善优化模型等。展望不是空泛的"未来可以做得更好"，而是要有明确的"做什么、怎么做、预期效果"三个层次。

本章与前序章节的关系是"汇总与升华"——它不产生新的分析结果，而是将前{{PREV_CHAPTER_COUNT}}章的碎片化结论整合为一份连贯的、有逻辑深度的研究成果总览。

### 1.2 从什么数据出发

本章的输入不是单一的数据文件，而是全部前序章节的输出产物和分析结论。具体依赖如下：

{{CHAPTER_DEPENDENCIES_LIST}}

### 1.3 可以采用什么方法

本章以**定性总结 + 定量指标提取**为主，不需要复杂的计算方法。核心是信息整合和逻辑提炼。

具体方法包括：
1. **结构化文本撰写**：按照研究逻辑链条组织总结内容，每章提取2-3条最重要的结论
2. **关键指标提取**：从前序章节的CSV产物中读取核心数值指标，汇总为一张"关键指标总览表"
3. **技术路线回顾**：以流程图或文字描述的形式，回顾全流程使用的技术方法和工具链
4. **SWOT分析**（可选）：从优势(Strength)、劣势(Weakness)、机会(Opportunity)、威胁(Threat)四个维度评估

## 二、执行步骤

### Step 1: 全流程成果汇总

**本步骤要做什么**
按照研究逻辑链条，逐章提炼核心发现，形成结构化的成果汇总报告。这份报告是整个研究项目最精炼的"结论摘要"。

具体而言，需要对{{TOTAL_CHAPTERS}}个章节分别提炼核心结论。每条发现必须包含两个要素：（1）定性结论（"发现了什么"）；（2）定量支撑（"具体数据是多少"）。

**具体操作指引**
1. **逐章阅读前序产物**：依次打开各章的输出文件（CSV和Markdown），提取每章的核心数值和结论。
2. **按统一模板撰写每章总结**：每章的总结遵循以下模板：
   - **核心发现1**：[定性结论] + [定量数据]
   - **核心发现2**：[定性结论] + [定量数据]
   - **与前/后章的逻辑关系**：[一句话说明衔接关系]
3. **填充占位符**：使用"XX"作为占位符，实际执行时需替换为真实数据。

**代码框架**:
```python
import os
import pandas as pd

output_dir = "outputs/ch{{FINAL_CHAPTER_NUM}}_summary"
os.makedirs(output_dir, exist_ok=True)

summary = """# {{PROJECT_NAME}} — 成果汇总报告

> 本报告对全流程{{TOTAL_CHAPTERS}}个章节的核心研究成果进行系统性汇总。
> 数据来源：{{ENTITY_COUNT}}个分析实体
> 分析周期：{{TIME_RANGE}}

---

{{CHAPTER_SUMMARY_SECTIONS}}

---

## 技术路线总结

全流程分析采用的技术路线如下：

```
原始数据
    |
    v
[Step 1] 数据预处理 (pandas)
    |   量纲统一、时间对齐、异常检测、特征工程
    v
[Step 2] {{STEP2_DESCRIPTION}}
    |   {{STEP2_METHODS}}
    v
{{TECH_ROUTE_MIDDLE}}
    |
    v
[Step {{FINAL_CHAPTER_NUM}}] 总结与展望
    |   成果汇总、关键指标、不足与局限、未来展望
```

## 不足与局限

### 数据维度局限
1. **缺少外部数据**：{{MISSING_EXTERNAL_DATA_DESCRIPTION}}
2. **时间跨度有限**：{{TIME_SPAN_LIMITATION}}
3. **空间分辨率有限**：{{SPATIAL_RESOLUTION_LIMITATION}}

### 模型精度局限
1. **预测模型未充分利用外部特征**：{{PREDICTION_LIMITATION}}
2. **优化模型简化假设较多**：{{OPTIMIZATION_LIMITATION}}

### 方法论局限
1. **异常检测方法单一**：仅使用{{ANOMALY_METHOD}}，未结合领域知识
2. **分类方法简单**：基于{{CLUSTERING_METHOD}}的二分类较为粗糙

## 未来展望

### 方向1：引入多维外部数据提升预测精度
- **做什么**：将{{EXTERNAL_FEATURES}}纳入预测模型
- **怎么做**：通过{{DATA_SOURCE}}获取数据，与{{ANALYSIS_TARGET}}数据按时间戳合并
- **预期效果**：{{EXPECTED_IMPROVEMENT}}
- **实施难度**：低

### 方向2：拓展多维度对比
- **做什么**：将对比从当前范围拓展到更多维度
- **怎么做**：通过{{EXPANDED_DATA_SOURCE}}获取数据
- **预期效果**：揭示更普适的规律
- **实施难度**：中

### 方向3：升级优化模型
- **做什么**：将优化模型升级为多时间尺度协调调度
- **怎么做**：日前+日内滚动修正框架
- **预期效果**：优化方案可执行性显著提升
- **实施难度**：高

### 方向4：开发交互式数据可视化平台
- **做什么**：将分析结果整合为交互式Web平台
- **怎么做**：使用Plotly Dash或Streamlit框架
- **预期效果**：研究成果可访问性大幅提升
- **实施难度**：中
"""

summary_path = os.path.join(output_dir, 'ch{{FINAL_CHAPTER_NUM}}_achievements_summary.md')
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write(summary)
print(f"成果汇总报告已保存: {summary_path}")
```

**本步骤完成后的检查标准**
- 报告覆盖全部{{TOTAL_CHAPTERS}}章的核心发现，无遗漏章节
- 每条核心发现包含"定性结论 + 定量数据"两个要素
- 章与章之间的逻辑衔接清晰
- 技术路线以流程图形式呈现
- 不足与局限部分客观诚实
- 未来展望每个方向包含"做什么、怎么做、预期效果"三个层次

**本步骤输出产物**
- `ch{{FINAL_CHAPTER_NUM}}_achievements_summary.md` — 成果汇总报告

### Step 2: 关键指标总览表

**本步骤要做什么**
提取各章核心数值指标，形成一张精炼的"关键指标总览表"。指标选取原则：每个分析章节至少1-2个最具代表性的指标；优先选取可直接量化的数值型指标。

**代码框架**:
```python
def safe_read_csv(filepath, **kwargs):
    try:
        return pd.read_csv(filepath, **kwargs)
    except FileNotFoundError:
        print(f"  警告: 文件不存在 - {filepath}")
        return None

# 尝试从前序章节产物中自动读取指标
{{AUTO_READ_SECTION}}

# 构建关键指标总览表
key_metrics = pd.DataFrame([
{{METRIC_ROWS}}
])

metrics_path = os.path.join(output_dir, 'ch{{FINAL_CHAPTER_NUM}}_key_metrics_table.csv')
key_metrics.to_csv(metrics_path, index=False)

print(f"\n{'='*70}")
print(f"  全流程关键指标总览表")
print(f"{'='*70}")
print(key_metrics.to_string(index=False))

pending_count = (key_metrics['value'] == '待填充').sum()
total_count = len(key_metrics)
print(f"\n指标总数: {total_count}, 已填充: {total_count - pending_count}, 待填充: {pending_count}")
```

**本步骤完成后的检查标准**
- 指标覆盖全部{{PREV_CHAPTER_COUNT}}个分析章节，每章至少1个指标
- 指标总数在12-15个之间
- 每个指标有明确的unit和source_file
- 已有CSV产物的指标已自动读取并填充

**本步骤输出产物**
- `ch{{FINAL_CHAPTER_NUM}}_key_metrics_table.csv` — 关键指标总览表

### Step 3: 技术路线总结

**本步骤要做什么**
回顾全流程使用的技术方法和工具链，形成完整的技术路线总结。回答三个问题：（1）每个步骤用了什么方法？（2）为什么选择这个方法？（3）方法之间的输入输出关系是什么？

**代码框架**:
```python
tech_route = """# 技术路线总结

## 1. 方法选择理由

| 步骤 | 核心方法 | 选择理由 | 替代方案 |
|------|----------|----------|----------|
{{METHOD_SELECTION_TABLE}}

## 2. 工具链清单

| 工具/库 | 版本要求 | 用途 | 使用章节 |
|---------|----------|------|----------|
{{TOOLCHAIN_TABLE}}
"""

print("技术路线总结已嵌入 ch{{FINAL_CHAPTER_NUM}}_achievements_summary.md")
```

**本步骤输出产物**
- 技术路线总结文字（嵌入成果汇总报告）

### Step 4: 不足与局限

**本步骤要做什么**
客观评估本次研究的局限性，从数据维度、模型精度、方法论三个层面进行系统性反思。每个局限性应包含三个要素：（1）具体描述不足之处；（2）说明影响程度；（3）指出改进方向。

**代码框架**:
```python
# 本步骤以文本撰写为主，不产生独立文件
# 不足与局限内容已嵌入 Step 1 的成果汇总报告中
# 每条局限性格式：
# - **[局限性标题]**：[具体描述] -> [影响程度] -> [改进方向]

print("不足与局限内容已嵌入 ch{{FINAL_CHAPTER_NUM}}_achievements_summary.md")
```

**本步骤输出产物**
- 不足与局限文字（嵌入成果汇总报告）

### Step 5: 未来展望

**本步骤要做什么**
提出具体的、可操作的未来研究方向，每个方向包含"做什么、怎么做、预期效果"三个层次。展望方向应与Step 4的局限性形成对应关系。

**代码框架**:
```python
# 本步骤以文本撰写为主，不产生独立文件
# 未来展望内容已嵌入 Step 1 的成果汇总报告中
# 每个方向格式：
# - 做什么（研究目标）
# - 怎么做（技术路线）
# - 预期效果（量化成果）
# - 实施难度（低/中/高）

directions = [
    ("方向1", "{{DIRECTION_1_NAME}}", "低"),
    ("方向2", "{{DIRECTION_2_NAME}}", "中"),
    ("方向3", "{{DIRECTION_3_NAME}}", "高"),
    ("方向4", "{{DIRECTION_4_NAME}}", "高"),
    ("方向5", "{{DIRECTION_5_NAME}}", "中"),
]
for d_id, d_name, d_diff in directions:
    print(f"  {d_id}: {d_name} (实施难度: {d_diff})")
```

**本步骤完成后的检查标准**
- 至少提出4个未来研究方向
- 每个方向包含"做什么、怎么做、预期效果、实施难度"四个要素
- 预期效果尽可能量化
- 方向之间有逻辑递进关系

**本步骤输出产物**
- 未来展望文字（嵌入成果汇总报告）

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 成果汇总报告 | ch{{FINAL_CHAPTER_NUM}}_achievements_summary.md | Markdown | outputs/ch{{FINAL_CHAPTER_NUM}}_summary/ | 最终报告结论章节 |
| 2 | 关键指标总览表 | ch{{FINAL_CHAPTER_NUM}}_key_metrics_table.csv | CSV | outputs/ch{{FINAL_CHAPTER_NUM}}_summary/ | 最终报告指标表格 |

### 3.2 关键产物结构详解

**ch{{FINAL_CHAPTER_NUM}}_achievements_summary.md**（最重要的产物）:
- 结构：{{TOTAL_CHAPTERS}}章核心发现汇总 + 技术路线总结 + 不足与局限 + 未来展望
- 每章提炼2-3条核心结论，含定性描述和定量数据
- 技术路线以ASCII流程图呈现
- 不足与局限分3个层面（数据、模型、方法）
- 未来展望4-5个方向，每个含"做什么-怎么做-预期效果-实施难度"

**ch{{FINAL_CHAPTER_NUM}}_key_metrics_table.csv**（数据名片）:
- 列结构：chapter(str), category(str), metric(str), value(str), unit(str), source_file(str)
- 行数：12-15行（覆盖全部分析章节）
- 已有数据的指标自动填充，缺失数据的指标标注"待填充"

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 成果汇总依赖前序章节的产物完整性
- 关键指标表中的"待填充"项需要人工回填
- 技术路线总结以文字为主，缺少可视化流程图

### 4.2 可进一步优化的方向
- 自动化指标回填脚本
- 生成学术格式报告（IEEE/Elsevier论文格式）
- 制作汇报PPT
- 开发交互式Dashboard

### 4.3 其他可选方法
- 文献计量分析
- 敏感性分析
- 用户调研验证

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 如果某章产物文件不存在导致汇总缺失：需确认是否跳过或等待
- 如果不同章节同一指标数值矛盾：需确认以哪个章节为准
- 如果"待填充"项过多：需确认是否先执行前序章节

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 某章产物文件不存在 | FileNotFoundError | 跳过该章，标注原因 | 否 |
| 指标数据不一致 | 不同章节数值矛盾 | 以最新章节数据为准 | 是 |
| 关键指标为"待填充" | value列含"待填充" | 打印清单，提醒回填 | 是 |
| 汇总报告篇幅过长 | 超过5000字 | 精简每章结论 | 是 |
| 未来展望不切实际 | 难度标注与内容不符 | 重新评估实施难度 | 否 |
```

---

## 4.4 产物总览表模板

### 4.4.1 全项目产物汇总表模板

```markdown
## 附录B: 输出产物总览表

| 章节 | 数据文件 | 图片文件 | 模型文件 | 报告/文档 | 合计 |
|------|----------|----------|----------|-----------|------|
{{CHAPTER_PRODUCT_SUMMARY_ROWS}}
| **总计** | **{{TOTAL_DATA}}** | **{{TOTAL_FIGURE}}** | **{{TOTAL_MODEL}}** | **{{TOTAL_REPORT}}** | **{{TOTAL_ALL}}** |
```

**参数说明**：

| 占位符 | 含义 |
|--------|------|
| `{{CHAPTER_PRODUCT_SUMMARY_ROWS}}` | 每章一行，格式为 `\| ch01 xxx \| N \| N \| N \| N \| N \|` |
| `{{TOTAL_DATA}}` | 数据文件总数 |
| `{{TOTAL_FIGURE}}` | 图片文件总数 |
| `{{TOTAL_MODEL}}` | 模型文件总数 |
| `{{TOTAL_REPORT}}` | 报告/文档总数 |
| `{{TOTAL_ALL}}` | 全部产物总数 |

### 4.4.2 按章节分组的产物清单模板

```markdown
## 附录C: 项目文件目录结构

```
{{PROJECT_DIR_NAME}}/
├── data/
│   └── {{RAW_DATA_FILE}}
├── outputs/
│   ├── ch01_{{CH01_DIR_NAME}}/
│   │   ├── ch01_*.csv
│   │   └── ch01_*.md
│   ├── ch02_{{CH02_DIR_NAME}}/
│   │   ├── ch02_*.csv
│   │   └── ch02_*.png
│   ├── ch03_{{CH03_DIR_NAME}}/
│   │   └── ...
│   ├── ch04_{{CH04_DIR_NAME}}/
│   │   └── ...
│   ├── ch05_{{CH05_DIR_NAME}}/
│   │   └── ...
│   ├── ch06_{{CH06_DIR_NAME}}/
│   │   └── ...
│   ├── ch07_{{CH07_DIR_NAME}}/
│   │   └── ...
│   └── ch08_{{CH08_DIR_NAME}}/
│       └── ...
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── data_loader.py
│   │   ├── visualizer.py
│   │   ├── metrics.py
│   │   ├── output_manager.py
│   │   └── task_graph.py
│   ├── ch01_{{CH01_DIR_NAME}}/
│   │   ├── __init__.py
│   │   ├── script.py
│   │   └── script.ipynb
│   ├── ch02_{{CH02_DIR_NAME}}/
│   │   └── ...
│   └── ...（其他章节目录）
├── docs/
│   └── execution_prompts.md
└── requirements.txt
```
```

### 4.4.3 依赖清单模板

```markdown
## 附录A: 完整依赖清单（requirements.txt）

```
pandas=={{PANDAS_VERSION}}
numpy=={{NUMPY_VERSION}}
openpyxl=={{OPENPYXL_VERSION}}
scipy=={{SCIPY_VERSION}}
matplotlib=={{MATPLOTLIB_VERSION}}
seaborn=={{SEABORN_VERSION}}
plotly=={{PLOTLY_VERSION}}
statsmodels=={{STATSMODELS_VERSION}}
prophet=={{PROPHET_VERSION}}
scikit-learn=={{SKLEARN_VERSION}}
xgboost=={{XGBOOST_VERSION}}
lightgbm=={{LIGHTGBM_VERSION}}
torch=={{TORCH_VERSION}}
pulp=={{PULP_VERSION}}
requests=={{REQUESTS_VERSION}}
beautifulsoup4=={{BS4_VERSION}}
tqdm=={{TQDM_VERSION}}
joblib=={{JOBLIB_VERSION}}
pmdarima=={{PMDARIMA_VERSION}}
```
```

---

**M-3 模块结束**

> 本模板定义了 `execution_prompts.md` 的完整结构，包括：
> - **4.0** 文档头部（标题、说明、路径配置、数据集概况）
> - **4.1** 全局Skill库（4个完整可运行Python模块）
> - **4.2** Prompt重复模板（固定5段式结构）
> - **4.3** 三种Prompt原型完整示例（数据预处理型/分析探索型/总结报告型）
> - **4.4** 产物总览表模板（汇总表、目录结构、依赖清单）
>
> 所有占位符格式为 `{{PLACEHOLDER_NAME}}`，实际项目中替换为具体值。

---

# M-5 + M-6: 代码框架模板 + 验证交付与附录

---

# M-5: Phase 6 — 代码框架模板

> **定位**：本章节提供从摩洛哥电力负荷分析项目中提炼出的**通用代码框架模板**。
> 所有模板已去除领域硬编码，使用 `{{PLACEHOLDER}}` 占位符标注需要适配的部分。
> 复制模板后，替换占位符即可快速启动新项目。

---

## 5.1 config.py 模板

**文件路径**：`src/utils/config.py`

**设计要点**：
- 保留 `PROJECT_ROOT` 路径推导逻辑（基于 `__file__` 上溯）
- 去除 `CITIES`、`VOLTAGE`、`POWER_FACTOR` 等领域硬编码
- 添加 `ENTITY_CONFIG`（实体/主体配置）和 `DOMAIN_PARAMS`（领域参数）两个通用配置区
- 保留可视化全局样式 `PLT_STYLE`

```python
"""
全局配置模块 - {{PROJECT_NAME_CN}}
所有章节脚本共享的路径、参数、常量定义

环境要求:
  - Python {{PYTHON_VERSION}}
  - 依赖安装: pip install -r requirements.txt

脚本规范:
  - 每个章节提供两种脚本:
    1. src/chXX_xxx/script.py       — 可直接运行的 .py 脚本
    2. src/chXX_xxx/script.ipynb     — Jupyter Notebook 交互式脚本（学习用）
  - 运行 .py 脚本: cd {{PROJECT_SLUG}} && python src/chXX_xxx/script.py
  - 运行 .ipynb: 在 Jupyter 中打开，确保 kernel 为 {{PYTHON_VERSION}}
"""

import os

# === 项目根目录（config.py 在 src/utils/ 下，需上溯两级） ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === 项目标识 ===
# {{PROJECT_NAME}}: 英文项目名，用于目录名和文件名（如 Morocco_Load_Analysis）
# {{PROJECT_NAME_CN}}: 中文项目名，用于文档标题和报告（如 电商用户行为分析）
PROJECT_NAME = '{{PROJECT_NAME}}'           # 英文，用于目录名
PROJECT_NAME_CN = '{{PROJECT_NAME_CN}}'     # 中文，用于文档标题

# === 虚拟环境配置 ===
VENV_PYTHON = os.path.expanduser('{{VENV_PYTHON_PATH}}')  # 例如: ~/anaconda3/envs/py310/bin/python
PYTHON_VERSION = '{{PYTHON_VERSION}}'  # 例如: '3.10'

# === 路径配置 ===
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_FILE = os.path.join(DATA_DIR, '{{RAW_DATA_FILENAME}}')  # 例如: 'raw_data.xlsx'
OUTPUT_BASE = os.path.join(PROJECT_ROOT, 'outputs')

# === 实体配置（替代原 CITIES 字典） ===
# 格式: {实体名称: {属性字典}}
# 示例: 城市、客户、产品、门店、设备等业务实体
ENTITY_CONFIG = {
    '{{ENTITY_01_NAME}}': {
        'source': '{{ENTITY_01_SOURCE}}',       # 数据来源标识（如 sheet名、表名、文件名）
        'sampling': '{{ENTITY_01_SAMPLING}}',   # 采样间隔（如 '10min', 'daily', None）
        'unit': '{{ENTITY_01_UNIT}}',           # 数据单位（如 'kW', 'CNY', 'count'）
        'zones': {{ENTITY_01_ZONES}},           # 子分区数量（如 5, 0 表示无分区）
        # 可按需添加更多属性...
    },
    '{{ENTITY_02_NAME}}': {
        'source': '{{ENTITY_02_SOURCE}}',
        'sampling': '{{ENTITY_02_SAMPLING}}',
        'unit': '{{ENTITY_02_UNIT}}',
        'zones': {{ENTITY_02_ZONES}},
    },
    # 按需添加更多实体...
}

# === 领域参数（替代原 VOLTAGE/POWER_FACTOR） ===
# 存放项目特有的常量、转换系数、阈值等
DOMAIN_PARAMS = {
    '{{PARAM_01_NAME}}': {{PARAM_01_VALUE}},  # 例如: 'voltage': 220
    '{{PARAM_02_NAME}}': {{PARAM_02_VALUE}},  # 例如: 'power_factor': 0.9
    '{{PARAM_03_NAME}}': {{PARAM_03_VALUE}},  # 例如: 'low_load_threshold': 0.5
    # 按需添加更多领域参数...
}

# === 分类映射（替代原 SEASON_MAP） ===
# 用于将数值编码映射为可读标签
# 示例: 月份→季节、数值→等级、编码→类别
CATEGORY_MAP = {
    # {{CATEGORY_KEY_EXAMPLE}}: '{{CATEGORY_VALUE_EXAMPLE}}',
    # 按需添加映射关系...
}

# === 可视化全局样式 ===
PLT_STYLE = {
    'figure.dpi': {{PLT_DPI}},               # 默认 150
    'savefig.dpi': {{PLT_SAVEFIG_DPI}},      # 默认 150
    'font.size': {{PLT_FONT_SIZE}},          # 默认 12
    'axes.unicode_minus': False,              # 支持中文负号显示
    'figure.figsize': ({{PLT_FIGWIDTH}}, {{PLT_FIGHEIGHT}}),  # 默认 (14, 5)
}
```

**占位符速查**：

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{PROJECT_NAME}}` | 项目中文名 | `电商用户行为分析` | 是 |
| `{{PROJECT_SLUG}}` | 项目目录名 | `Morocco_Load_Analysis` | 是 |
| `{{PYTHON_VERSION}}` | Python 版本 | `3.10` | 是 |
| `{{VENV_PYTHON_PATH}}` | 虚拟环境 Python 路径 | `~/anaconda3/envs/py310/bin/python` | 否 |
| `{{RAW_DATA_FILENAME}}` | 原始数据文件名 | `Data Morocco.xlsx` | 是 |
| `{{ENTITY_XX_NAME}}` | 实体名称 | `Laayoune` | 是 |
| `{{ENTITY_XX_SOURCE}}` | 实体数据来源 | `Laayoune` (sheet名) | 是 |
| `{{ENTITY_XX_SAMPLING}}` | 采样间隔 | `10min` | 视项目 |
| `{{ENTITY_XX_UNIT}}` | 数据单位 | `kW` | 是 |
| `{{ENTITY_XX_ZONES}}` | 子分区数量 | `5` | 视项目 |
| `{{PARAM_XX_NAME}}` | 领域参数名 | `voltage` | 视项目 |
| `{{PARAM_XX_VALUE}}` | 领域参数值 | `220` | 视项目 |
| `{{PLT_DPI}}` | 图表 DPI | `150` | 否 |
| `{{PLT_FIGWIDTH}}` | 图表默认宽度 | `14` | 否 |
| `{{PLT_FIGHEIGHT}}` | 图表默认高度 | `5` | 否 |

---

## 5.2 Skill-01: data_loader.py 模板

**文件路径**：`src/utils/data_loader.py`

**设计要点**：
- 泛化为支持 CSV / Excel / Parquet 三种格式的通用加载器
- 保留 `load_raw_data()`（加载单个实体原始数据）、`load_all_entities()`（加载全部实体）、`load_preprocessed()`（加载预处理后数据）三个核心函数
- 实体配置从 `config.py` 的 `ENTITY_CONFIG` 参数化读取

```python
"""
通用数据加载器 (Skill-01)
支持加载 CSV / Excel / Parquet 格式的原始数据、预处理后数据、全实体合并数据

使用方式:
    from utils.data_loader import load_raw_data, load_all_entities, load_preprocessed

    # 加载单个实体
    df = load_raw_data('entity_name')

    # 加载全部实体
    all_data = load_all_entities()

    # 加载预处理后数据
    df = load_preprocessed('outputs/ch01/cleaned_data.csv')
"""

import pandas as pd
import sys
import os

# 确保可以导入 config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import RAW_DATA_FILE, ENTITY_CONFIG


def _detect_file_type(filepath: str) -> str:
    """根据文件扩展名检测文件类型

    Args:
        filepath: 文件路径

    Returns:
        文件类型字符串: 'csv', 'excel', 'parquet'

    Raises:
        ValueError: 不支持的文件格式
    """
    ext = os.path.splitext(filepath)[1].lower()
    type_map = {
        '.csv': 'csv',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.parquet': 'parquet',
        '.pq': 'parquet',
    }
    if ext not in type_map:
        raise ValueError(
            f"不支持的文件格式: {ext}，"
            f"当前支持: {', '.join(type_map.keys())}"
        )
    return type_map[ext]


def _read_file(filepath: str, **kwargs) -> pd.DataFrame:
    """根据文件类型自动选择读取方式

    Args:
        filepath: 文件路径
        **kwargs: 传递给底层读取函数的额外参数

    Returns:
        DataFrame
    """
    file_type = _detect_file_type(filepath)

    if file_type == 'csv':
        return pd.read_csv(filepath, **kwargs)
    elif file_type == 'excel':
        kwargs.setdefault('engine', 'openpyxl')
        return pd.read_excel(filepath, **kwargs)
    elif file_type == 'parquet':
        return pd.read_parquet(filepath, **kwargs)


def load_raw_data(entity_name: str) -> pd.DataFrame:
    """加载指定实体的原始数据

    根据 ENTITY_CONFIG 中的配置自动选择:
    - 若 source 为 sheet 名称且 RAW_DATA_FILE 为 Excel，则按 sheet 读取
    - 若 source 为文件路径，则直接读取该文件
    - 读取后自动解析时间戳列并设为索引

    Args:
        entity_name: 实体名称（需在 ENTITY_CONFIG 中定义）

    Returns:
        DataFrame，时间戳为索引，含 entity 列

    Raises:
        ValueError: 实体名称不存在于 ENTITY_CONFIG
    """
    if entity_name not in ENTITY_CONFIG:
        raise ValueError(
            f"未知实体: {entity_name}，"
            f"可选: {list(ENTITY_CONFIG.keys())}"
        )

    config = ENTITY_CONFIG[entity_name]
    source = config['source']

    # 判断 source 是 sheet 名称还是独立文件路径
    if os.path.isfile(source):
        # source 是独立文件路径
        df = _read_file(source)
    else:
        # source 视为 sheet 名称，从 RAW_DATA_FILE 读取
        file_type = _detect_file_type(RAW_DATA_FILE)
        if file_type == 'excel':
            df = pd.read_excel(RAW_DATA_FILE, sheet_name=source, engine='openpyxl')
        else:
            raise ValueError(
                f"RAW_DATA_FILE 不是 Excel 格式，无法按 sheet 读取。"
                f"请将 source 配置为独立文件路径。"
            )

    # 自动解析时间戳列（查找常见的日期列名）
    datetime_candidates = ['DateTime', 'datetime', 'timestamp', 'date',
                           'Date', 'Timestamp', '时间', '日期', '{{DATETIME_COLUMN}}']
    dt_col = None
    for col in datetime_candidates:
        if col in df.columns:
            dt_col = col
            break

    if dt_col is not None:
        df[dt_col] = pd.to_datetime(df[dt_col])
        df = df.set_index(dt_col).sort_index()
    else:
        # 尝试第一列
        df = df.set_index(df.columns[0])
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

    df['entity'] = entity_name
    return df


def load_all_entities() -> dict:
    """加载全部实体原始数据

    Returns:
        {实体名称: DataFrame, ...} 字典
    """
    return {
        entity_name: load_raw_data(entity_name)
        for entity_name in ENTITY_CONFIG
    }


def load_preprocessed(filepath: str) -> pd.DataFrame:
    """加载预处理后的统一数据集

    自动根据文件扩展名选择读取方式，并尝试解析时间索引。

    Args:
        filepath: 预处理后的数据文件路径（CSV/Excel/Parquet）

    Returns:
        DataFrame
    """
    file_type = _detect_file_type(filepath)

    if file_type == 'csv':
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    elif file_type == 'excel':
        df = pd.read_excel(filepath, index_col=0, engine='openpyxl')
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            df.index = pd.to_datetime(df.index)
    elif file_type == 'parquet':
        df = pd.read_parquet(filepath)

    return df
```

---

## 5.3 Skill-02: visualizer.py 模板

**文件路径**：`src/utils/visualizer.py`

**设计要点**：
- 保留 `plot_time_series()`、`plot_multi_comparison()`、`plot_heatmap()`、`plot_model_forecast()` 四个核心函数
- 坐标轴标签参数化（不再硬编码 `'Load (kW)'`）
- 保留 DPI、figsize 等样式参数
- 新增 `_apply_style()` 统一管理全局样式

```python
"""
通用可视化出图器 (Skill-02)
提供项目统一的图表风格和常用绘图函数

使用方式:
    from utils.visualizer import plot_model_forecast, plot_time_series

    fig = plot_model_forecast(y_test, y_pred, '模型预测结果',
                              xlabel='时间', ylabel='{{VALUE_UNIT}}',
                              output_path='outputs/ch04/forecast.png')
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 无显示器环境
import matplotlib.pyplot as plt
import seaborn as sns


def _apply_style(dpi: int = 150, font_size: int = 12, figsize: tuple = (14, 5)):
    """应用项目全局样式

    Args:
        dpi: 图表分辨率
        font_size: 全局字体大小
        figsize: 默认图表尺寸 (width, height)
    """
    plt.rcParams.update({
        'figure.dpi': dpi,
        'savefig.dpi': dpi,
        'font.size': font_size,
        'axes.unicode_minus': False,
        'figure.figsize': figsize,
    })


def plot_time_series(
    data,
    title: str,
    xlabel: str = 'Time',
    ylabel: str = 'Value',
    output_path: str = None,
    figsize: tuple = (14, 5),
    dpi: int = 150,
    color: str = '#2196F3',
    linewidth: float = 0.8,
    alpha: float = 0.9,
    grid: bool = True,
) -> 'matplotlib.figure.Figure':
    """绘制单条或多条时间序列曲线

    Args:
        data: 时间序列数据，支持以下格式:
            - pd.Series（单条曲线）
            - pd.DataFrame（每列一条曲线，自动生成图例）
            - np.ndarray（单条曲线，无时间轴标签）
        title: 图表标题
        xlabel: X轴标签（参数化，不再硬编码）
        ylabel: Y轴标签（参数化，不再硬编码）
        output_path: 若非 None，保存图片到指定路径
        figsize: 图表尺寸
        dpi: 分辨率
        color: 曲线颜色（单条时生效）
        linewidth: 线宽
        alpha: 透明度
        grid: 是否显示网格

    Returns:
        matplotlib Figure 对象
    """
    _apply_style(dpi=dpi, figsize=figsize)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    if isinstance(data, pd.DataFrame):
        for col in data.columns:
            ax.plot(data.index, data[col], linewidth=linewidth, alpha=alpha, label=col)
        ax.legend(fontsize=11, loc='upper right')
    elif isinstance(data, pd.Series):
        ax.plot(data.index, data.values, color=color, linewidth=linewidth, alpha=alpha)
    else:
        ax.plot(data, color=color, linewidth=linewidth, alpha=alpha)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    if grid:
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        print(f'  [保存] {output_path}')
    else:
        plt.close(fig)

    return fig


def plot_multi_comparison(
    data_dict: dict,
    title: str,
    xlabel: str = 'Time',
    ylabel: str = 'Value',
    output_path: str = None,
    figsize: tuple = (14, 5),
    dpi: int = 150,
    linewidth: float = 0.8,
    alpha: float = 0.8,
    grid: bool = True,
) -> 'matplotlib.figure.Figure':
    """绘制多组数据对比图（如多实体对比、多模型对比）

    Args:
        data_dict: {名称: 数据} 字典，数据为 pd.Series 或 np.ndarray
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        output_path: 若非 None，保存图片到指定路径
        figsize: 图表尺寸
        dpi: 分辨率
        linewidth: 线宽
        alpha: 透明度
        grid: 是否显示网格

    Returns:
        matplotlib Figure 对象
    """
    _apply_style(dpi=dpi, figsize=figsize)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    for name, data in data_dict.items():
        if isinstance(data, pd.Series):
            ax.plot(data.index, data.values, linewidth=linewidth, alpha=alpha, label=name)
        else:
            ax.plot(np.asarray(data), linewidth=linewidth, alpha=alpha, label=name)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(fontsize=11, loc='upper right')
    if grid:
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        print(f'  [保存] {output_path}')
    else:
        plt.close(fig)

    return fig


def plot_heatmap(
    data: pd.DataFrame,
    title: str,
    xlabel: str = '',
    ylabel: str = '',
    output_path: str = None,
    figsize: tuple = (12, 8),
    dpi: int = 150,
    cmap: str = 'YlOrRd',
    annot: bool = True,
    fmt: str = '.2f',
    linewidths: float = 0.5,
) -> 'matplotlib.figure.Figure':
    """绘制热力图（相关系数矩阵、交叉统计表等）

    Args:
        data: 二维数据（pd.DataFrame）
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        output_path: 若非 None，保存图片到指定路径
        figsize: 图表尺寸
        dpi: 分辨率
        cmap: 颜色映射
        annot: 是否显示数值标注
        fmt: 数值格式
        linewidths: 格线宽度

    Returns:
        matplotlib Figure 对象
    """
    _apply_style(dpi=dpi, figsize=figsize)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    sns.heatmap(
        data, ax=ax, cmap=cmap, annot=annot, fmt=fmt,
        linewidths=linewidths, cbar_kws={'shrink': 0.8}
    )

    ax.set_title(title, fontsize=14, fontweight='bold')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        print(f'  [保存] {output_path}')
    else:
        plt.close(fig)

    return fig


def plot_model_forecast(
    y_true,
    y_pred,
    title: str,
    xlabel: str = 'Time Step',
    ylabel: str = 'Value',
    output_path: str = None,
    figsize: tuple = (14, 5),
    dpi: int = 150,
    show_metrics: bool = True,
    metrics_dict: dict = None,
    metrics_module: str = 'utils.metrics',
) -> 'matplotlib.figure.Figure':
    """绘制模型预测结果对比图（真实值 vs 预测值）

    Args:
        y_true: 真实值序列（pd.Series 或 np.ndarray）
        y_pred: 预测值序列（pd.Series 或 np.ndarray）
        title: 图表标题
        xlabel: X轴标签（参数化，不再硬编码 'Time Step'）
        ylabel: Y轴标签（参数化，不再硬编码 'Load (kW)'）
        output_path: 若非 None，保存图片到指定路径
        figsize: 图表尺寸
        dpi: 分辨率
        show_metrics: 是否在图表上显示 MAE/RMSE/MAPE
        metrics_dict: 若提供，使用其中的指标值；否则自动计算
        metrics_module: 指标计算模块路径（用于动态导入 evaluate_model）

    Returns:
        matplotlib Figure 对象
    """
    _apply_style(dpi=dpi, figsize=figsize)

    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()

    # 对齐长度
    min_len = min(len(y_true), len(y_pred))
    y_true = y_true[:min_len]
    y_pred = y_pred[:min_len]

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # 绘制曲线
    ax.plot(y_true, color='#2196F3', linewidth=0.8, alpha=0.9, label='Actual')
    ax.plot(y_pred, color='#F44336', linewidth=0.8, alpha=0.7, linestyle='--', label='Predicted')

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)

    # 叠加指标文本框
    if show_metrics:
        if metrics_dict is None:
            import importlib
            mod = importlib.import_module(metrics_module)
            metrics_dict = mod.evaluate_model(y_true, y_pred, '')

        text = (f"MAE  = {metrics_dict['MAE']:.4f}\n"
                f"RMSE = {metrics_dict['RMSE']:.4f}\n"
                f"MAPE = {metrics_dict['MAPE']:.2f}%")
        ax.text(0.02, 0.97, text, transform=ax.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat', alpha=0.8))

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        print(f'  [保存] {output_path}')
    else:
        plt.close(fig)

    return fig
```

---

## 5.4 Skill-03: metrics.py 模板

**文件路径**：`src/utils/metrics.py`

**设计要点**：
- 保留 `calc_mae()`、`calc_rmse()`、`calc_mape()`、`evaluate_model()`、`compare_models()` 五个核心函数
- 低负荷过滤阈值参数化（通过 `threshold` 参数传入，不再硬编码 `0.5`）
- 保留质量标签体系（Outstanding / Excellent / Pass / Needs Improvement），阈值可配置

```python
"""
通用评估指标计算器 (Skill-03)
支持预测模型和优化模型的评估

使用方式:
    from utils.metrics import evaluate_model, compare_models

    result = evaluate_model(y_true, y_pred, "ModelA")
    # {'model': 'ModelA', 'MAE': 1.23, 'RMSE': 1.56, 'MAPE': 5.67}

    df = compare_models([result1, result2, ...])
"""

import numpy as np
import pandas as pd


# === 低值过滤阈值（默认值，可通过函数参数覆盖） ===
# 用于 MAPE 计算时跳过 |y_true| < threshold 的点，避免除零导致 MAPE 爆炸
DEFAULT_LOW_VALUE_THRESHOLD = {{DEFAULT_LOW_VALUE_THRESHOLD}}  # 例如: 0.5

# === 质量标签阈值（可按领域调整） ===
QUALITY_THRESHOLDS = {
    'outstanding': {{QUALITY_OUTSTANDING}},   # MAPE < 此值 → Outstanding，例如: 5
    'excellent':   {{QUALITY_EXCELLENT}},     # MAPE < 此值 → Excellent，例如: 10
    'pass':        {{QUALITY_PASS}},          # MAPE < 此值 → Pass，例如: 15
    # MAPE >= pass → Needs Improvement
}


def calc_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """平均绝对误差 (Mean Absolute Error)

    Args:
        y_true: 真实值
        y_pred: 预测值

    Returns:
        MAE 值
    """
    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()
    return float(np.mean(np.abs(y_true - y_pred)))


def calc_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """均方根误差 (Root Mean Square Error)

    Args:
        y_true: 真实值
        y_pred: 预测值

    Returns:
        RMSE 值
    """
    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calc_mape(y_true: np.ndarray, y_pred: np.ndarray,
              threshold: float = None) -> float:
    """平均绝对百分比误差 (Mean Absolute Percentage Error, %)

    跳过 |y_true| < threshold 的点，避免低值时段除零导致 MAPE 爆炸。

    Args:
        y_true: 真实值
        y_pred: 预测值
        threshold: 低值过滤阈值，默认使用 DEFAULT_LOW_VALUE_THRESHOLD

    Returns:
        MAPE 百分比数值（如 5.23 表示 5.23%）
    """
    if threshold is None:
        threshold = DEFAULT_LOW_VALUE_THRESHOLD

    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()

    # 过滤低值点
    mask = np.abs(y_true) >= threshold
    if mask.sum() == 0:
        return float('inf')

    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def evaluate_model(y_true, y_pred, model_name: str,
                   threshold: float = None) -> dict:
    """综合评估单个模型

    Args:
        y_true: 真实值 (np.ndarray 或 pd.Series)
        y_pred: 预测值 (np.ndarray 或 pd.Series)
        model_name: 模型名称
        threshold: MAPE 低值过滤阈值，默认使用 DEFAULT_LOW_VALUE_THRESHOLD

    Returns:
        dict: {'model': str, 'MAE': float, 'RMSE': float, 'MAPE': float}
    """
    y_true = np.asarray(y_true, dtype=np.float64).ravel()
    y_pred = np.asarray(y_pred, dtype=np.float64).ravel()

    return {
        'model': model_name,
        'MAE': round(calc_mae(y_true, y_pred), 4),
        'RMSE': round(calc_rmse(y_true, y_pred), 4),
        'MAPE': round(calc_mape(y_true, y_pred, threshold), 2),
    }


def _quality_label(mape: float) -> str:
    """根据 MAPE 值返回质量标签

    阈值由 QUALITY_THRESHOLDS 配置决定:
    - < outstanding: Outstanding (卓越)
    - < excellent:   Excellent (优秀)
    - < pass:        Pass (合格)
    - >= pass:       Needs Improvement (需改进)
    """
    if mape < QUALITY_THRESHOLDS['outstanding']:
        return 'Outstanding'
    elif mape < QUALITY_THRESHOLDS['excellent']:
        return 'Excellent'
    elif mape < QUALITY_THRESHOLDS['pass']:
        return 'Pass'
    else:
        return 'Needs Improvement'


def compare_models(results: list, output_path: str = None) -> pd.DataFrame:
    """多模型对比，生成排序后的 DataFrame

    Args:
        results: evaluate_model() 返回的 dict 列表
        output_path: 若非 None，保存为 CSV

    Returns:
        DataFrame 按 MAPE 升序排列，含 model/MAE/RMSE/MAPE/quality 列
    """
    df = pd.DataFrame(results)
    df = df.sort_values('MAPE', ascending=True).reset_index(drop=True)
    df.insert(0, 'rank', range(1, len(df) + 1))
    df['quality'] = df['MAPE'].apply(_quality_label)

    if output_path:
        df.to_csv(output_path, index=False)
        print(f'  [保存] {output_path}')

    return df
```

---

## 5.5 Skill-04: output_manager.py 模板

**文件路径**：`src/utils/output_manager.py`

**设计要点**：
- 保留 `ensure_dir()`、`save_dataframe()`、`save_figure()`、`save_markdown()` 四个核心函数
- 新增 `get_chapter_dir()` 参数化章节目录映射
- 所有输出路径基于 `OUTPUT_BASE` + 章节前缀自动推导

```python
"""
通用输出产物管理器 (Skill-04)
确保输出目录存在，统一保存 DataFrame、图片和 Markdown 文本

使用方式:
    from utils.output_manager import get_chapter_dir, save_dataframe, save_figure, save_markdown

    output_dir = get_chapter_dir('ch01')
    save_dataframe(df, 'ch01_cleaned_data.csv', output_dir)
    save_figure(fig, 'ch01_distribution.png', output_dir)
    save_markdown(report, 'ch01_report.md', output_dir)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


def _get_output_base() -> str:
    """获取输出根目录（延迟导入，避免循环依赖）"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.config import OUTPUT_BASE
    return OUTPUT_BASE


# === 章节目录映射（从 config 自动生成，无需手动维护） ===
# 如需自定义目录名，在 config.py 的 CHAPTER_CONFIG 中配置
def get_chapter_dir_map():
    """从 config 获取章节目录映射"""
    try:
        from utils.config import CHAPTER_CONFIG
        return {f'ch{str(k).zfill(2)}': v['dir_name'] for k, v in CHAPTER_CONFIG.items()}
    except ImportError:
        # 回退：使用默认命名规则
        return {
            'ch01': 'ch01_preprocessing',
            'ch02': 'ch02_analysis',
            # ... 按需扩展
        }

CHAPTER_DIR_MAP = get_chapter_dir_map()


def ensure_dir(dirpath: str) -> str:
    """确保目录存在，不存在则创建

    Args:
        dirpath: 目录路径

    Returns:
        目录路径（确认存在）
    """
    os.makedirs(dirpath, exist_ok=True)
    return dirpath


def get_chapter_dir(chapter_key: str) -> str:
    """获取章节输出目录的完整路径

    Args:
        chapter_key: 章节标识（如 'ch01'）

    Returns:
        完整目录路径

    Raises:
        ValueError: 章节标识未在 CHAPTER_DIR_MAP 中注册
    """
    if chapter_key not in CHAPTER_DIR_MAP:
        raise ValueError(
            f"未注册的章节标识: {chapter_key}，"
            f"当前已注册: {list(CHAPTER_DIR_MAP.keys())}。"
            f"请在 CHAPTER_DIR_MAP 中添加映射。"
        )

    output_base = _get_output_base()
    chapter_subdir = CHAPTER_DIR_MAP[chapter_key]
    return ensure_dir(os.path.join(output_base, chapter_subdir))


def save_dataframe(df: pd.DataFrame, filename: str, output_dir: str,
                   index: bool = True) -> str:
    """保存 DataFrame 为 CSV

    Args:
        df: 要保存的 DataFrame
        filename: 文件名（建议使用 chXX_ 前缀，如 ch01_cleaned_data.csv）
        output_dir: 输出目录
        index: 是否保存索引

    Returns:
        完整文件路径
    """
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=index)
    print(f'  [保存] {filepath}')
    return filepath


def save_figure(fig, filename: str, output_dir: str, dpi: int = 150) -> str:
    """保存 matplotlib 图表

    Args:
        fig: matplotlib Figure 对象
        filename: 文件名（建议使用 chXX_ 前缀，如 ch02_distribution.png）
        output_dir: 输出目录
        dpi: 图片分辨率

    Returns:
        完整文件路径
    """
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f'  [保存] {filepath}')
    return filepath


def save_markdown(content: str, filename: str, output_dir: str) -> str:
    """保存 Markdown 文本

    Args:
        content: Markdown 文本内容
        filename: 文件名（建议使用 chXX_ 前缀，如 ch01_report.md）
        output_dir: 输出目录

    Returns:
        完整文件路径
    """
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  [保存] {filepath}')
    return filepath
```

---

## 5.6 task_graph.py 模板

**文件路径**：`src/utils/task_graph.py`

**设计要点**：
- 保留 `TaskGraph` 类完整架构（`check_ready()`、`get_status()`、`get_current_batch()`、`print_status()`）
- `TASKS` 和 `BATCHES` 字典参数化，使用占位符标注
- 保留基于产物存在性推断进度的机制

```python
"""
任务依赖图模块
定义各 Prompt 之间的依赖关系，提供前置条件检查和进度查询功能。

使用方式:
    from utils.task_graph import TaskGraph

    tg = TaskGraph()
    tg.check_ready('prompt-02')   # 检查 Prompt-02 是否可以启动
    tg.get_status()               # 查看全部任务状态
    tg.print_status()             # 打印进度总览
"""

import os
import glob

# === 任务定义 ===
# 格式:
#   'prompt-XX': {
#       'name':         任务中文名,
#       'batch':        所属批次号（int，从0开始）,
#       'depends':      依赖的 prompt 列表,
#       'branch':       支线标识（可选，如 'A', 'B', 'C'）,
#       'script':       .py 脚本相对路径,
#       'notebook':     .ipynb 笔记本相对路径,
#       'output_dir':   输出目录相对路径,
#       'key_artifacts': 关键产物文件名列表,
#   }
TASKS = {
    'prompt-01': {
        'name': '{{TASK_01_NAME}}',           # 例如: '数据预处理'
        'batch': 0,
        'depends': [],
        'script': 'src/{{CHAPTER_01_DIR}}/{{CHAPTER_01_SCRIPT}}',
        'notebook': 'src/{{CHAPTER_01_DIR}}/{{CHAPTER_01_NOTEBOOK}}',
        'output_dir': 'outputs/{{CHAPTER_01_DIR}}',
        'key_artifacts': [
            '{{ARTIFACT_01_01}}',  # 例如: 'ch01_cleaned_data.csv'
            '{{ARTIFACT_01_02}}',  # 例如: 'ch01_feature_engineered_data.csv'
        ],
    },
    'prompt-02': {
        'name': '{{TASK_02_NAME}}',
        'batch': 1,
        'depends': ['prompt-01'],
        'branch': 'A',
        'script': 'src/{{CHAPTER_02_DIR}}/{{CHAPTER_02_SCRIPT}}',
        'notebook': 'src/{{CHAPTER_02_DIR}}/{{CHAPTER_02_NOTEBOOK}}',
        'output_dir': 'outputs/{{CHAPTER_02_DIR}}',
        'key_artifacts': [
            '{{ARTIFACT_02_01}}',
            '{{ARTIFACT_02_02}}',
        ],
    },
    'prompt-03': {
        'name': '{{TASK_03_NAME}}',
        'batch': 2,
        'depends': ['prompt-02'],
        'branch': 'A',
        'script': 'src/{{CHAPTER_03_DIR}}/{{CHAPTER_03_SCRIPT}}',
        'notebook': 'src/{{CHAPTER_03_DIR}}/{{CHAPTER_03_NOTEBOOK}}',
        'output_dir': 'outputs/{{CHAPTER_03_DIR}}',
        'key_artifacts': [
            '{{ARTIFACT_03_01}}',
            '{{ARTIFACT_03_02}}',
        ],
    },
    'prompt-04': {
        'name': '{{TASK_04_NAME}}',
        'batch': 1,
        'depends': ['prompt-01'],
        'branch': 'B',
        'script': 'src/{{CHAPTER_04_DIR}}/{{CHAPTER_04_SCRIPT}}',
        'notebook': 'src/{{CHAPTER_04_DIR}}/{{CHAPTER_04_NOTEBOOK}}',
        'output_dir': 'outputs/{{CHAPTER_04_DIR}}',
        'key_artifacts': [
            '{{ARTIFACT_04_01}}',
        ],
    },
    'prompt-05': {
        'name': '{{TASK_05_NAME}}',
        'batch': 1,
        'depends': ['prompt-01'],
        'branch': 'C',
        'script': 'src/{{CHAPTER_05_DIR}}/{{CHAPTER_05_SCRIPT}}',
        'notebook': 'src/{{CHAPTER_05_DIR}}/{{CHAPTER_05_NOTEBOOK}}',
        'output_dir': 'outputs/{{CHAPTER_05_DIR}}',
        'key_artifacts': [
            '{{ARTIFACT_05_01}}',
            '{{ARTIFACT_05_02}}',
        ],
    },
    'prompt-06': {
        'name': '{{TASK_06_NAME}}',
        'batch': 3,
        'depends': ['prompt-03'],
        'branch': 'A',
        'script': 'src/{{CHAPTER_06_DIR}}/{{CHAPTER_06_SCRIPT}}',
        'notebook': 'src/{{CHAPTER_06_DIR}}/{{CHAPTER_06_NOTEBOOK}}',
        'output_dir': 'outputs/{{CHAPTER_06_DIR}}',
        'key_artifacts': [
            '{{ARTIFACT_06_01}}',
            '{{ARTIFACT_06_02}}',
        ],
    },
    'prompt-07': {
        'name': '{{TASK_07_NAME}}',
        'batch': 3,
        'depends': ['prompt-04'],
        'branch': 'B',
        'script': 'src/{{CHAPTER_07_DIR}}/{{CHAPTER_07_SCRIPT}}',
        'notebook': 'src/{{CHAPTER_07_DIR}}/{{CHAPTER_07_NOTEBOOK}}',
        'output_dir': 'outputs/{{CHAPTER_07_DIR}}',
        'key_artifacts': [
            '{{ARTIFACT_07_01}}',
            '{{ARTIFACT_07_02}}',
        ],
    },
    'prompt-08': {
        'name': '{{TASK_08_NAME}}',
        'batch': 3,
        'depends': ['prompt-05'],
        'branch': 'C',
        'script': 'src/{{CHAPTER_08_DIR}}/{{CHAPTER_08_SCRIPT}}',
        'notebook': 'src/{{CHAPTER_08_DIR}}/{{CHAPTER_08_NOTEBOOK}}',
        'output_dir': 'outputs/{{CHAPTER_08_DIR}}',
        'key_artifacts': [
            '{{ARTIFACT_08_01}}',
            '{{ARTIFACT_08_02}}',
        ],
    },
}

# === 批次定义 ===
# 格式:
#   批次号: {
#       'name':     批次中文名,
#       'tasks':    该批次包含的 prompt 列表,
#       'parallel': 是否可并行执行,
#   }
BATCHES = {
    0: {'name': '{{BATCH_0_NAME}}',    'tasks': ['prompt-01'], 'parallel': False},
    1: {'name': '{{BATCH_1_NAME}}',    'tasks': ['prompt-02', 'prompt-04', 'prompt-05'], 'parallel': True},
    2: {'name': '{{BATCH_2_NAME}}',    'tasks': ['prompt-03'], 'parallel': False},
    3: {'name': '{{BATCH_3_NAME}}',    'tasks': ['prompt-06', 'prompt-07', 'prompt-08'], 'parallel': True},
}


class TaskGraph:
    """任务依赖图，提供前置检查和进度查询"""

    def __init__(self, project_root: str = None):
        if project_root is None:
            from utils.config import PROJECT_ROOT
            project_root = PROJECT_ROOT
        self.project_root = project_root

    def _artifact_exists(self, artifact_name: str, task_key: str) -> bool:
        """检查关键产物是否存在"""
        task = TASKS[task_key]
        output_dir = os.path.join(self.project_root, task['output_dir'])
        return os.path.isfile(os.path.join(output_dir, artifact_name))

    def check_ready(self, task_key: str) -> dict:
        """检查某任务是否可以启动

        Returns:
            {'ready': bool, 'missing_deps': [...], 'missing_artifacts': [...]}
        """
        task = TASKS[task_key]
        missing_deps = []
        missing_artifacts = []

        for dep_key in task['depends']:
            dep = TASKS[dep_key]
            # 检查依赖任务的关键产物是否存在
            for artifact in dep['key_artifacts']:
                if not self._artifact_exists(artifact, dep_key):
                    missing_artifacts.append(
                        f"{dep_key}({dep['name']}): {artifact}"
                    )

        ready = len(missing_artifacts) == 0
        return {
            'ready': ready,
            'task': task_key,
            'name': task['name'],
            'batch': task['batch'],
            'missing_deps': missing_deps,
            'missing_artifacts': missing_artifacts,
        }

    def get_status(self) -> list:
        """查看全部任务状态"""
        results = []
        for task_key in TASKS:
            task = TASKS[task_key]
            if not task['key_artifacts']:
                results.append({
                    'task': task_key, 'name': task['name'],
                    'batch': task['batch'], 'status': '待开发',
                })
                continue

            exists_count = sum(
                1 for a in task['key_artifacts']
                if self._artifact_exists(a, task_key)
            )
            total = len(task['key_artifacts'])

            if exists_count == total:
                status = '已完成'
            elif exists_count > 0:
                status = f'进行中 ({exists_count}/{total})'
            else:
                status = '未开始'

            results.append({
                'task': task_key, 'name': task['name'],
                'batch': task['batch'], 'status': status,
            })
        return results

    def get_current_batch(self) -> int:
        """根据产物存在情况推断当前应执行的批次"""
        for batch_num in sorted(BATCHES.keys()):
            batch = BATCHES[batch_num]
            for task_key in batch['tasks']:
                task = TASKS[task_key]
                all_exist = all(
                    self._artifact_exists(a, task_key)
                    for a in task['key_artifacts']
                )
                if not all_exist:
                    return batch_num
        return max(BATCHES.keys()) + 1  # 全部完成

    def print_status(self):
        """打印进度总览"""
        current = self.get_current_batch()
        print(f'当前应执行批次: Batch-{current}')
        print('=' * 60)

        for batch_num in sorted(BATCHES.keys()):
            batch = BATCHES[batch_num]
            marker = '>>>' if batch_num == current else '   '
            parallel = ' [并行]' if batch['parallel'] else ''
            print(f'{marker} Batch-{batch_num}: {batch["name"]}{parallel}')

            for task_key in batch['tasks']:
                task = TASKS[task_key]
                exists_count = sum(
                    1 for a in task['key_artifacts']
                    if self._artifact_exists(a, task_key)
                )
                total = len(task['key_artifacts'])
                status = '[OK]' if exists_count == total else '[  ]'
                branch = f" (支线{task.get('branch', '')})" if 'branch' in task else ''
                print(f'      {status} {task_key}: {task["name"]}{branch} '
                      f'[{exists_count}/{total}]')

        print('=' * 60)


# === CLI 入口 ===
if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    tg = TaskGraph()
    tg.print_status()
```

---

## 5.7 章节脚本 .py 骨架模板

**文件路径**：`src/chXX_xxx/script.py`

**设计要点**：
- 标准化 docstring 头（参数化项目名、章节号、步骤描述）
- `sys.path` 设置确保可导入 `utils` 模块
- `import` 标准模板（按功能分组）
- `main()` 函数骨架含步骤注释框架
- `if __name__ == '__main__'` 入口

```python
"""
Prompt-{{CHAPTER_NUM}}: {{CHAPTER_TITLE}}
{{PROJECT_NAME}} - {{CHAPTER_DESCRIPTION}}

覆盖{{STEP_COUNT}}个处理步骤:
  {{STEP_LIST}}

产物输出到: outputs/{{CHAPTER_DIR}}/
"""

import sys
import os

# === 确保可以导入项目工具模块 ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

# === 标准库 ===
from datetime import datetime

# === 第三方库 ===
import pandas as pd
import numpy as np

# === 项目工具模块 ===
from utils.config import (
    ENTITY_CONFIG,
    DOMAIN_PARAMS,
    CATEGORY_MAP,
    OUTPUT_BASE,
    PLT_STYLE,
)
from utils.data_loader import load_raw_data, load_all_entities, load_preprocessed
from utils.output_manager import get_chapter_dir, save_dataframe, save_figure, save_markdown, ensure_dir
from utils.visualizer import plot_time_series, plot_multi_comparison, plot_heatmap, plot_model_forecast
from utils.metrics import evaluate_model, compare_models


def main():
    """主函数 - {{CHAPTER_TITLE}}"""

    # === 输出目录 ===
    OUTPUT_DIR = get_chapter_dir('ch{{CHAPTER_NUM}}')

    print('=' * 60)
    print(f'Prompt-{{CHAPTER_NUM}}: {{CHAPTER_TITLE}}')
    print('=' * 60)
    print(f'输出目录: {OUTPUT_DIR}\n')

    # ================================================================
    # Step {{STEP_FIRST_NUM}}.{{STEP_FIRST_SUB}}: {{STEP_FIRST_TITLE}}
    # ================================================================
    print(f'[Step {{STEP_FIRST_NUM}}.{{STEP_FIRST_SUB}}] {{STEP_FIRST_TITLE}}...')
    # TODO: 实现步骤逻辑
    # 示例:
    # data = load_preprocessed('outputs/ch01/cleaned_data.csv')
    # print(f'  数据量: {len(data)} 行')

    # ================================================================
    # Step {{STEP_SECOND_NUM}}.{{STEP_SECOND_SUB}}: {{STEP_SECOND_TITLE}}
    # ================================================================
    print(f'\n[Step {{STEP_SECOND_NUM}}.{{STEP_SECOND_SUB}}] {{STEP_SECOND_TITLE}}...')
    # TODO: 实现步骤逻辑

    # ================================================================
    # Step {{STEP_THIRD_NUM}}.{{STEP_THIRD_SUB}}: {{STEP_THIRD_TITLE}}
    # ================================================================
    print(f'\n[Step {{STEP_THIRD_NUM}}.{{STEP_THIRD_SUB}}] {{STEP_THIRD_TITLE}}...')
    # TODO: 实现步骤逻辑

    # ================================================================
    # 总结
    # ================================================================
    print('\n' + '=' * 60)
    print('{{CHAPTER_TITLE}}完成！')
    print('=' * 60)
    print(f'输出目录: {OUTPUT_DIR}')
    print(f'产物数量: {{ARTIFACT_COUNT}} 个')
    print('=' * 60)


if __name__ == '__main__':
    main()
```

**占位符速查**：

| 占位符 | 含义 | 示例值 |
|--------|------|--------|
| `{{CHAPTER_NUM}}` | 章节编号（两位数） | `01` |
| `{{CHAPTER_TITLE}}` | 章节中文标题 | `数据预处理` |
| `{{CHAPTER_DESCRIPTION}}` | 章节功能描述 | `原始数据清洗与特征工程` |
| `{{CHAPTER_DIR}}` | 章节目录名 | `ch01_data_preprocessing` |
| `{{STEP_COUNT}}` | 步骤总数 | `9` |
| `{{STEP_LIST}}` | 步骤列表文本 | `1.1 数据读取...` |
| `{{STEP_FIRST_NUM}}` | 第一步编号 | `1` |
| `{{STEP_FIRST_SUB}}` | 第一步子编号 | `1` |
| `{{STEP_FIRST_TITLE}}` | 第一步标题 | `数据读取与结构探查` |
| `{{ARTIFACT_COUNT}}` | 产物数量 | `8` |

---

## 5.8 章节脚本 .ipynb 骨架模板

**文件路径**：`src/chXX_xxx/script.ipynb`

**设计要点**：
- Markdown Cell 与 Code Cell 交替排列
- 第一个 Markdown Cell 包含章节标题和说明
- 第一个 Code Cell 包含 import 和路径设置
- 后续按步骤交替排列

```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Prompt-{{CHAPTER_NUM}}: {{CHAPTER_TITLE}}\n",
    "\n",
    "{{PROJECT_NAME}} - {{CHAPTER_DESCRIPTION}}\n",
    "\n",
    "## 步骤概览\n",
    "\n",
    "| 步骤 | 名称 | 说明 |\n",
    "|------|------|------|\n",
    "| {{STEP_FIRST_NUM}}.{{STEP_FIRST_SUB}} | {{STEP_FIRST_TITLE}} | {{STEP_FIRST_DESC}} |\n",
    "| {{STEP_SECOND_NUM}}.{{STEP_SECOND_SUB}} | {{STEP_SECOND_TITLE}} | {{STEP_SECOND_DESC}} |\n",
    "| {{STEP_THIRD_NUM}}.{{STEP_THIRD_SUB}} | {{STEP_THIRD_TITLE}} | {{STEP_THIRD_DESC}} |\n",
    "\n",
    "## 产物清单\n",
    "\n",
    "| 序号 | 产物名称 | 文件名 |\n",
    "|------|----------|--------|\n",
    "| 1 | {{ARTIFACT_01_NAME}} | {{ARTIFACT_01_FILENAME}} |\n",
    "| 2 | {{ARTIFACT_02_NAME}} | {{ARTIFACT_02_FILENAME}} |\n",
    "\n",
    "---"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# === 环境设置 ===\n",
    "import sys\n",
    "import os\n",
    "\n",
    "try:\n",
    "    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))\n",
    "except NameError:\n",
    "    SCRIPT_DIR = os.getcwd()\n",
    "SRC_DIR = os.path.dirname(SCRIPT_DIR)\n",
    "sys.path.insert(0, SRC_DIR)\n",
    "\n",
    "# === 标准库 ===\n",
    "from datetime import datetime\n",
    "\n",
    "# === 第三方库 ===\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "# === 项目工具模块 ===\n",
    "from utils.config import ENTITY_CONFIG, DOMAIN_PARAMS, CATEGORY_MAP, OUTPUT_BASE, PLT_STYLE\n",
    "from utils.data_loader import load_raw_data, load_all_entities, load_preprocessed\n",
    "from utils.output_manager import get_chapter_dir, save_dataframe, save_figure, save_markdown\n",
    "from utils.visualizer import plot_time_series, plot_multi_comparison, plot_heatmap, plot_model_forecast\n",
    "from utils.metrics import evaluate_model, compare_models\n",
    "\n",
    "# === 输出目录 ===\n",
    "OUTPUT_DIR = get_chapter_dir('ch{{CHAPTER_NUM}}')\n",
    "print(f'输出目录: {OUTPUT_DIR}')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Step {{STEP_FIRST_NUM}}.{{STEP_FIRST_SUB}}: {{STEP_FIRST_TITLE}}\n",
    "\n",
    "{{STEP_FIRST_DESC}}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step {{STEP_FIRST_NUM}}.{{STEP_FIRST_SUB}}: {{STEP_FIRST_TITLE}}\n",
    "print('[Step {{STEP_FIRST_NUM}}.{{STEP_FIRST_SUB}}] {{STEP_FIRST_TITLE}}...')\n",
    "\n",
    "# TODO: 实现步骤逻辑"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Step {{STEP_SECOND_NUM}}.{{STEP_SECOND_SUB}}: {{STEP_SECOND_TITLE}}\n",
    "\n",
    "{{STEP_SECOND_DESC}}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step {{STEP_SECOND_NUM}}.{{STEP_SECOND_SUB}}: {{STEP_SECOND_TITLE}}\n",
    "print('[Step {{STEP_SECOND_NUM}}.{{STEP_SECOND_SUB}}] {{STEP_SECOND_TITLE}}...')\n",
    "\n",
    "# TODO: 实现步骤逻辑"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 总结\n",
    "\n",
    "本章完成了 {{CHAPTER_TITLE}}，共生成 {{ARTIFACT_COUNT}} 个产物。"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python {{PYTHON_VERSION}}",
   "language": "python",
   "name": "python{{PYTHON_VERSION_NODOT}}"
  },
  "language_info": {
   "name": "python",
   "version": "{{PYTHON_VERSION}}.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
```

---

## 5.9 \_\_init\_\_.py 模板

**文件路径**：`src/utils/__init__.py` 和 `src/chXX_xxx/__init__.py`

### 5.9.1 utils 包初始化

**文件路径**：`src/utils/__init__.py`

```python
"""
utils - 通用工具模块包
提供数据加载、可视化、指标计算、输出管理等通用功能
"""

from utils.config import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DATA_FILE,
    OUTPUT_BASE,
    ENTITY_CONFIG,
    DOMAIN_PARAMS,
    CATEGORY_MAP,
    PLT_STYLE,
)

__all__ = [
    'PROJECT_ROOT',
    'DATA_DIR',
    'RAW_DATA_FILE',
    'OUTPUT_BASE',
    'ENTITY_CONFIG',
    'DOMAIN_PARAMS',
    'CATEGORY_MAP',
    'PLT_STYLE',
]
```

### 5.9.2 章节包初始化

**文件路径**：`src/chXX_xxx/__init__.py`

```python
"""
ch{{CHAPTER_NUM}}_{{CHAPTER_SLUG}} - {{CHAPTER_TITLE}}
{{CHAPTER_DESCRIPTION}}
"""
```

---

# M-6: Phase 7-8 + 附录

---

## Phase 7: 文档更新与经验沉淀

### 7.1 文档更新检查清单

项目执行过程中，以下文档可能需要同步更新：

| 文档 | 更新时机 | 更新内容 |
|------|----------|----------|
| project_convention.md | 新增章节、修改命名规则 | 章节目录、命名规范、禁止事项 |
| flow_design.md | 修改分析方法、调整研究目标 | 对应章节的方法、步骤、产物 |
| execution_prompts.md | 修改代码实现、调整参数 | 对应 Prompt 的代码框架、参数 |
| task_dispatch_guide.md | 调整依赖关系、修改批次划分 | 依赖图、批次表、速查表 |
| requirements.txt | 新增/删除依赖库 | 依赖列表 |

### 7.2 经验教训提炼模板

项目完成后，从执行过程中提炼可复用经验：

| 经验编号 | 问题场景 | 改进方案 | 适用范围 |
|----------|----------|----------|----------|
| E-01 | {{EXPERIENCE_1_PROBLEM}} | {{EXPERIENCE_1_SOLUTION}} | {{EXPERIENCE_1_SCOPE}} |
| E-02 | {{EXPERIENCE_2_PROBLEM}} | {{EXPERIENCE_2_SOLUTION}} | {{EXPERIENCE_2_SCOPE}} |
| ... | ... | ... | ... |

> **填写规则**：每条经验应包含具体的问题场景（发生了什么）、改进方案（怎么解决）、适用范围（哪些项目会遇到类似问题）。

---

## Phase 8: requirements.txt 模板

**文件路径**：`requirements.txt`

**设计要点**：
- 基础依赖（几乎所有项目都需要）
- 可选依赖按功能分组，用注释分隔
- 每个分组标注适用场景，便于按需启用

```txt
# {{PROJECT_NAME}} - Python {{PYTHON_VERSION}} Dependencies
# Install: pip install -r requirements.txt

# ============================================================
# 基础依赖（必装）
# ============================================================

# === 数据处理 ===
pandas>={{PANDAS_VERSION}}           # 数据表操作核心库
numpy>={{NUMPY_VERSION}}             # 数值计算基础库
openpyxl>={{OPENPYXL_VERSION}}       # Excel 文件读写
scipy>={{SCIPY_VERSION}}             # 科学计算（统计检验、插值、优化）

# === 可视化 ===
matplotlib>={{MATPLOTLIB_VERSION}}   # 基础绑图库
seaborn>={{SEABORN_VERSION}}         # 统计可视化增强

# ============================================================
# 可选依赖（按需取消注释安装）
# ============================================================

# --- 机器学习组 ---
# 适用场景: 分类、回归、聚类等传统机器学习任务
# scikit-learn>={{SKLEARN_VERSION}}    # 经典机器学习算法库
# xgboost>={{XGBOOST_VERSION}}         # 梯度提升树（高效回归/分类）
# lightgbm>={{LIGHTGBM_VERSION}}       # 轻量梯度提升（大数据场景）

# --- 时序分析组 ---
# 适用场景: 时间序列预测、季节性分解、ARIMA 建模
# statsmodels>={{STATSMODELS_VERSION}} # 经典时序模型（ARIMA/ETS/分解）
# prophet>={{PROPHET_VERSION}}         # Facebook 时序预测（需安装编译依赖）
# pmdarima>={{PMDARIMA_VERSION}}       # 自动 ARIMA 参数选择

# --- 深度学习组 ---
# 适用场景: LSTM/Transformer 等神经网络时序预测
# torch>={{TORCH_VERSION}}             # PyTorch 深度学习框架

# --- 优化组 ---
# 适用场景: 运筹优化、线性规划、整数规划
# pulp>={{PULP_VERSION}}               # 线性/整数规划求解器

# --- 爬虫组 ---
# 适用场景: 需要从网页抓取外部数据
# requests>={{REQUESTS_VERSION}}       # HTTP 请求库
# beautifulsoup4>={{BS4_VERSION}}      # HTML 解析库

# --- 交互可视化组 ---
# 适用场景: 需要生成交互式图表（可缩放、悬停提示）
# plotly>={{PLOTLY_VERSION}}           # 交互式可视化

# --- 工具库 ---
# tqdm>={{TQDM_VERSION}}               # 进度条
# joblib>={{JOBLIB_VERSION}}           # 并行计算与缓存
```

### 依赖推断规则表

根据项目特征自动推断需要安装的依赖分组：

| 项目特征 | 推断依赖 | 说明 |
|----------|----------|------|
| 包含 `.xlsx` 原始数据文件 | `openpyxl` | Excel 读写必需 |
| 章节标题含"预测"/"forecast" | `scikit-learn`, `xgboost`, `lightgbm` | 机器学习组 |
| 章节标题含"时序"/"趋势"/"ARIMA" | `statsmodels`, `pmdarima` | 时序分析组 |
| 章节标题含"LSTM"/"深度学习"/"neural" | `torch` | 深度学习组 |
| 章节标题含"优化"/"调度"/"规划" | `pulp` | 优化组 |
| 章节标题含"爬取"/"抓取"/"scraping" | `requests`, `beautifulsoup4` | 爬虫组 |
| 章节标题含"交互"/"dashboard" | `plotly` | 交互可视化组 |
| 数据量 > 100MB | `joblib`, `tqdm` | 并行计算与进度显示 |
| 需要统计检验 | `scipy` | 已在基础依赖中 |
| 需要生成热力图 | `seaborn` | 已在基础依赖中 |

---

## Phase 8: 验证与交付

### 8.1 验证清单（7项）

在项目交付前，逐项检查以下内容：

| 序号 | 检查项 | 验证方法 | 通过标准 |
|------|--------|----------|----------|
| 1 | **目录结构完整性** | `tree` 或 `ls -R` 检查 | `src/utils/` 含4个 Skill 模块；每个章节目录含 `.py` + `.ipynb`；`outputs/` 含各章节子目录 |
| 2 | **config.py 配置正确性** | 运行 `python -c "from utils.config import *; print(ENTITY_CONFIG)"` | 无 ImportError；路径存在；ENTITY_CONFIG 非空 |
| 3 | **数据加载器可用性** | 运行 `python -c "from utils.data_loader import load_all_entities; data = load_all_entities(); print({k: len(v) for k,v in data.items()})"` | 每个实体成功加载，行数 > 0 |
| 4 | **Skill 模块导入正常** | 运行 `python -c "from utils.visualizer import *; from utils.metrics import *; from utils.output_manager import *; from utils.task_graph import TaskGraph"` | 全部导入成功，无报错 |
| 5 | **章节脚本可独立运行** | 逐个运行 `python src/chXX_xxx/script.py` | 每个脚本正常退出（exit code 0），产物文件生成 |
| 6 | **产物文件完整性** | 检查 `task_graph.py` 中定义的 `key_artifacts` 是否全部存在 | `TaskGraph().get_status()` 显示所有任务为"已完成" |
| 7 | **Notebook 可执行** | 在 Jupyter 中打开每个 `.ipynb`，执行全部 Cell | 无报错；输出与 `.py` 脚本一致 |

### 8.2 交付物清单模板

```markdown
# {{PROJECT_NAME}} - 交付物清单

## 项目信息
- 项目名称: {{PROJECT_NAME}}
- 项目目录: {{PROJECT_SLUG}}
- Python 版本: {{PYTHON_VERSION}}
- 交付日期: {{DELIVERY_DATE}}

## 目录结构
```
{{PROJECT_SLUG}}/
├── data/                          # 原始数据
│   └── {{RAW_DATA_FILENAME}}
├── src/
│   ├── utils/                     # 通用工具模块（4个 Skill）
│   │   ├── __init__.py
│   │   ├── config.py              # 全局配置
│   │   ├── data_loader.py         # Skill-01: 数据加载器
│   │   ├── visualizer.py          # Skill-02: 可视化出图器
│   │   ├── metrics.py             # Skill-03: 评估指标计算器
│   │   ├── output_manager.py      # Skill-04: 输出产物管理器
│   │   └── task_graph.py          # 任务依赖图
│   ├── ch01_{{CHAPTER_01_SLUG}}/
│   │   ├── __init__.py
│   │   ├── script.py
│   │   └── script.ipynb
│   ├── ch02_{{CHAPTER_02_SLUG}}/
│   │   └── ...
│   └── ...
├── outputs/                       # 全部章节产物
│   ├── ch01_{{CHAPTER_01_DIR}}/
│   │   ├── ch01_{{ARTIFACT_01_FILENAME}}
│   │   └── ...
│   └── ...
├── requirements.txt
└── README.md
```

## 章节产物汇总

| 章节 | 产物数量 | 关键产物 |
|------|----------|----------|
| ch01 | {{CH01_ARTIFACT_COUNT}} | {{CH01_KEY_ARTIFACTS}} |
| ch02 | {{CH02_ARTIFACT_COUNT}} | {{CH02_KEY_ARTIFACTS}} |
| ch03 | {{CH03_ARTIFACT_COUNT}} | {{CH03_KEY_ARTIFACTS}} |
| ... | ... | ... |

## 验证结果

| 序号 | 检查项 | 结果 |
|------|--------|------|
| 1 | 目录结构完整性 | [ ] 通过 |
| 2 | config.py 配置正确性 | [ ] 通过 |
| 3 | 数据加载器可用性 | [ ] 通过 |
| 4 | Skill 模块导入正常 | [ ] 通过 |
| 5 | 章节脚本可独立运行 | [ ] 通过 |
| 6 | 产物文件完整性 | [ ] 通过 |
| 7 | Notebook 可执行 | [ ] 通过 |
```

---

## 附录 A: 占位符完整列表与说明

以下是本模板体系中所有 `{{PLACEHOLDER}}` 的完整列表。

### A.1 项目级占位符

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{PROJECT_NAME}}` | 项目中文名称 | `电商用户行为分析` | 是 |
| `{{PROJECT_SLUG}}` | 项目目录名（英文/拼音） | `Morocco_Load_Analysis` | 是 |
| `{{PYTHON_VERSION}}` | Python 版本号 | `3.10` | 是 |
| `{{PYTHON_VERSION_NODOT}}` | Python 版本号（无点号，用于 kernel 名） | `310` | 是 |
| `{{VENV_PYTHON_PATH}}` | 虚拟环境 Python 解释器路径 | `~/anaconda3/envs/py310/bin/python` | 否 |
| `{{DELIVERY_DATE}}` | 交付日期 | `2025-01-15` | 是 |

### A.2 数据与路径占位符

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{RAW_DATA_FILENAME}}` | 原始数据文件名 | `Data Morocco.xlsx` | 是 |
| `{{DATETIME_COLUMN}}` | 时间戳列名 | `DateTime` | 视项目 |

### A.3 实体配置占位符

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{ENTITY_XX_NAME}}` | 第 XX 个实体的名称 | `Laayoune` | 是 |
| `{{ENTITY_XX_SOURCE}}` | 第 XX 个实体的数据来源 | `Laayoune` (sheet名) | 是 |
| `{{ENTITY_XX_SAMPLING}}` | 第 XX 个实体的采样间隔 | `10min` | 视项目 |
| `{{ENTITY_XX_UNIT}}` | 第 XX 个实体的数据单位 | `kW` | 是 |
| `{{ENTITY_XX_ZONES}}` | 第 XX 个实体的子分区数量 | `5` | 视项目 |

### A.4 领域参数占位符

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{PARAM_XX_NAME}}` | 第 XX 个领域参数名 | `voltage` | 视项目 |
| `{{PARAM_XX_VALUE}}` | 第 XX 个领域参数值 | `220` | 视项目 |

### A.5 可视化参数占位符

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{PLT_DPI}}` | 图表 DPI | `150` | 否 |
| `{{PLT_SAVEFIG_DPI}}` | 保存图片 DPI | `150` | 否 |
| `{{PLT_FONT_SIZE}}` | 全局字体大小 | `12` | 否 |
| `{{PLT_FIGWIDTH}}` | 默认图表宽度 | `14` | 否 |
| `{{PLT_FIGHEIGHT}}` | 默认图表高度 | `5` | 否 |

### A.6 指标参数占位符

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{DEFAULT_LOW_VALUE_THRESHOLD}}` | MAPE 低值过滤阈值 | `0.5` | 是 |
| `{{QUALITY_OUTSTANDING}}` | Outstanding 质量阈值 | `5` | 是 |
| `{{QUALITY_EXCELLENT}}` | Excellent 质量阈值 | `10` | 是 |
| `{{QUALITY_PASS}}` | Pass 质量阈值 | `15` | 是 |

### A.7 章节配置占位符

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{CHAPTER_XX_DIR}}` | 第 XX 章节目录名 | `ch01_data_preprocessing` | 是 |
| `{{CHAPTER_XX_SLUG}}` | 第 XX 章节英文标识 | `preprocessing` | 是 |
| `{{CHAPTER_XX_SCRIPT}}` | 第 XX 章节 .py 文件名 | `preprocess.py` | 是 |
| `{{CHAPTER_XX_NOTEBOOK}}` | 第 XX 章节 .ipynb 文件名 | `preprocess.ipynb` | 是 |

### A.8 任务图占位符

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{TASK_XX_NAME}}` | 第 XX 个任务的中文名 | `数据预处理` | 是 |
| `{{BATCH_XX_NAME}}` | 第 XX 批次的中文名 | `串行前置` | 是 |
| `{{ARTIFACT_XX_YY}}` | 第 XX 任务的第 YY 个关键产物文件名 | `ch01_cleaned_data.csv` | 是 |

### A.9 依赖版本占位符

| 占位符 | 含义 | 示例值 | 必填 |
|--------|------|--------|------|
| `{{PANDAS_VERSION}}` | pandas 最低版本 | `2.0.3` | 是 |
| `{{NUMPY_VERSION}}` | numpy 最低版本 | `1.24.3` | 是 |
| `{{OPENPYXL_VERSION}}` | openpyxl 最低版本 | `3.1.2` | 是 |
| `{{SCIPY_VERSION}}` | scipy 最低版本 | `1.11.4` | 是 |
| `{{MATPLOTLIB_VERSION}}` | matplotlib 最低版本 | `3.8.0` | 是 |
| `{{SEABORN_VERSION}}` | seaborn 最低版本 | `0.13.0` | 是 |
| `{{SKLEARN_VERSION}}` | scikit-learn 最低版本 | `1.3.2` | 是 |
| `{{XGBOOST_VERSION}}` | xgboost 最低版本 | `2.0.3` | 否 |
| `{{LIGHTGBM_VERSION}}` | lightgbm 最低版本 | `4.1.0` | 否 |
| `{{STATSMODELS_VERSION}}` | statsmodels 最低版本 | `0.14.0` | 否 |
| `{{PROPHET_VERSION}}` | prophet 最低版本 | `1.1.5` | 否 |
| `{{PMDARIMA_VERSION}}` | pmdarima 最低版本 | `2.0.4` | 否 |
| `{{TORCH_VERSION}}` | torch 最低版本 | `2.1.0` | 否 |
| `{{PULP_VERSION}}` | pulp 最低版本 | `2.7.0` | 否 |
| `{{REQUESTS_VERSION}}` | requests 最低版本 | `2.31.0` | 否 |
| `{{BS4_VERSION}}` | beautifulsoup4 最低版本 | `4.12.2` | 否 |
| `{{PLOTLY_VERSION}}` | plotly 最低版本 | `5.17.0` | 否 |
| `{{TQDM_VERSION}}` | tqdm 最低版本 | `4.66.1` | 否 |
| `{{JOBLIB_VERSION}}` | joblib 最低版本 | `1.3.2` | 否 |

---

## 附录 B: 章节原型详细说明

根据数据分析项目的常见工作流，章节可分为三种原型。每种原型有典型的步骤、方法和产物模式。

### B.1 数据预处理型

**适用场景**：原始数据清洗、格式统一、特征工程、数据质量保障

**典型步骤**：
1. 数据读取与结构探查（字段类型、行数、时间范围）
2. 缺失值检测与统计（按列/按实体统计缺失率）
3. 时间戳解析与标准化（统一格式、时区处理）
4. 数据对齐（不同采样频率的上/下采样）
5. 量纲统一（单位转换、标准化/归一化）
6. 异常值检测（3sigma、IQR、孤立森林等）
7. 异常值处理（插值、截断、删除）
8. 特征工程（时间特征、统计特征、交叉特征）
9. 数据质量报告生成

**典型方法**：
- `pd.read_excel()` / `pd.read_csv()` / `pd.read_parquet()`
- `df.isnull().sum()` / `df.isnull().mean()`
- `pd.to_datetime()` / `df.resample()`
- `df.interpolate()` / `df.fillna()`
- `scipy.stats.zscore()` / IQR 方法
- `df.clip()` / `df.dropna()`
- `df.index.hour` / `df.index.dayofweek` / `df.index.month`

**典型产物**：
- `chXX_data_profile_report.md` — 数据概况报告
- `chXX_missing_stats.csv` — 缺失值统计表
- `chXX_cleaned_data.csv` — 清洗后数据集
- `chXX_feature_engineered_data.csv` — 含特征工程数据集
- `chXX_data_quality_report.md` — 数据质量报告

### B.2 分析探索型

**适用场景**：描述性统计、分布分析、相关性分析、模式挖掘、模型训练

**典型步骤**：
1. 数据加载与验证（确认输入数据完整性）
2. 描述性统计（均值、标准差、分位数）
3. 分布分析（直方图、箱线图、核密度估计）
4. 相关性分析（相关系数矩阵、热力图）
5. 分组对比分析（按实体/时间/类别分组）
6. 趋势/模式识别（时间序列分解、周期性分析）
7. 模型训练与评估（如适用）
8. 结果可视化与解读
9. 分析报告生成

**典型方法**：
- `df.describe()` / `df.groupby().agg()`
- `plt.hist()` / `sns.boxplot()` / `sns.kdeplot()`
- `df.corr()` / `sns.heatmap()`
- `sns.lineplot()` / `sns.barplot()`
- `statsmodels.tsa.seasonal_decompose()`
- `sklearn.model_selection.train_test_split()`
- `evaluate_model()` / `compare_models()`

**典型产物**：
- `chXX_descriptive_stats.csv` — 描述性统计表
- `chXX_distribution.png` — 分布图
- `chXX_correlation_heatmap.png` — 相关性热力图
- `chXX_group_comparison.csv` — 分组对比表
- `chXX_model_comparison.csv` — 模型对比表
- `chXX_analysis_report.md` — 分析报告

### B.3 总结报告型

**适用场景**：项目收尾、成果汇总、经验总结、展望建议

**典型步骤**：
1. 全部章节产物加载与验证
2. 关键指标汇总（跨章节提取核心数据）
3. 成果亮点提炼（最佳模型、重要发现、异常洞察）
4. 交叉验证（不同章节结论的一致性检查）
5. 局限性分析（数据局限、方法局限）
6. 建议与展望（后续研究方向、业务建议）
7. 交付物清单整理
8. 最终报告生成

**典型方法**：
- `TaskGraph().get_status()` — 验证全部任务完成
- `pd.concat()` / `pd.merge()` — 跨章节数据整合
- Markdown 长文本生成
- 表格/图表汇总

**典型产物**：
- `chXX_achievements_summary.md` — 成果总结
- `chXX_key_findings.md` — 关键发现
- `chXX_recommendations.md` — 建议与展望
- `chXX_deliverables_checklist.md` — 交付物清单

---

## 附录 C: 领域适配示例（3个简例）

### C.1 金融风控分析项目

**项目名称**：`信贷违约风险分析`

**config.py 适配要点**：
```python
PROJECT_NAME = '信贷违约风险分析'
PROJECT_SLUG = 'Credit_Risk_Analysis'
RAW_DATA_FILE = os.path.join(DATA_DIR, 'loan_data.csv')

ENTITY_CONFIG = {
    'personal_loan': {
        'source': 'loan_data.csv',
        'sampling': None,        # 非时序数据
        'unit': 'CNY',
        'zones': 0,
    },
}

DOMAIN_PARAMS = {
    'default_threshold': 0.05,       # 违约率关注阈值
    'credit_score_range': (300, 850),
    'feature_count': 25,
}

CATEGORY_MAP = {
    0: 'Fully Paid',
    1: 'Charged Off',
}

QUALITY_THRESHOLDS = {
    'outstanding': 3,    # AUC > 0.97 → Outstanding
    'excellent': 5,      # AUC > 0.95 → Excellent
    'pass': 10,          # AUC > 0.90 → Pass
}
```

**章节规划**：
| 章节 | 标题 | 原型 |
|------|------|------|
| ch01 | 数据预处理 | 预处理型 |
| ch02 | 特征工程与选择 | 预处理型 |
| ch03 | 探索性数据分析 | 分析探索型 |
| ch04 | 信用评分模型 | 分析探索型 |
| ch05 | 模型解释与归因 | 分析探索型 |
| ch06 | 风险报告生成 | 总结报告型 |

### C.2 电商用户行为分析项目

**项目名称**：`电商用户行为分析与购买预测`

**config.py 适配要点**：
```python
PROJECT_NAME = '电商用户行为分析与购买预测'
PROJECT_SLUG = 'Ecommerce_User_Behavior'
RAW_DATA_FILE = os.path.join(DATA_DIR, 'user_behavior.parquet')

ENTITY_CONFIG = {
    'app_users': {
        'source': 'user_behavior.parquet',
        'sampling': '1min',
        'unit': 'event',
        'zones': 0,
    },
    'web_users': {
        'source': 'web_behavior.parquet',
        'sampling': '1min',
        'unit': 'event',
        'zones': 0,
    },
}

DOMAIN_PARAMS = {
    'purchase_window_hours': 24,       # 购买转化观察窗口
    'session_timeout_minutes': 30,     # 会话超时时间
    'high_value_threshold': 1000,      # 高价值用户消费阈值(CNY)
}

CATEGORY_MAP = {
    'pv': '浏览',
    'cart': '加购',
    'fav': '收藏',
    'buy': '购买',
}
```

**章节规划**：
| 章节 | 标题 | 原型 |
|------|------|------|
| ch01 | 数据清洗与会话重建 | 预处理型 |
| ch02 | 用户行为模式挖掘 | 分析探索型 |
| ch03 | 购买转化漏斗分析 | 分析探索型 |
| ch04 | 用户分群与画像 | 分析探索型 |
| ch05 | 购买预测模型 | 分析探索型 |
| ch06 | 业务洞察报告 | 总结报告型 |

### C.3 医疗数据挖掘项目

**项目名称**：`住院患者再入院风险预测`

**config.py 适配要点**：
```python
PROJECT_NAME = '住院患者再入院风险预测'
PROJECT_SLUG = 'Hospital_Readmission'
RAW_DATA_FILE = os.path.join(DATA_DIR, 'patient_records.xlsx')

ENTITY_CONFIG = {
    'internal_medicine': {
        'source': 'internal_medicine',
        'sampling': None,
        'unit': 'patient',
        'zones': 0,
    },
    'surgery': {
        'source': 'surgery',
        'sampling': None,
        'unit': 'patient',
        'zones': 0,
    },
}

DOMAIN_PARAMS = {
    'readmission_window_days': 30,     # 30天再入院定义
    'age_groups': [0, 18, 45, 65, 100],
    'los_threshold_days': 7,           # 长住院阈值
    'icd_code_count': 1500,            # ICD编码数量
}

CATEGORY_MAP = {
    0: 'No Readmission',
    1: 'Readmitted within 30 days',
}

QUALITY_THRESHOLDS = {
    'outstanding': 5,    # MAPE < 5% → Outstanding
    'excellent': 10,
    'pass': 15,
}
```

**章节规划**：
| 章节 | 标题 | 原型 |
|------|------|------|
| ch01 | 数据清洗与编码映射 | 预处理型 |
| ch02 | 患者特征分析 | 分析探索型 |
| ch03 | 再入院风险因素挖掘 | 分析探索型 |
| ch04 | 风险预测模型 | 分析探索型 |
| ch05 | 模型公平性评估 | 分析探索型 |
| ch06 | 临床决策支持报告 | 总结报告型 |

---

## 附录 D: 摩洛哥项目经验教训总结（10条）

以下经验全部来自摩洛哥智能电表电力负荷分析项目的实际开发过程。

### 1. 文档先行原则

**教训**：在编写任何代码之前，先完成项目规划文档（目录结构、章节划分、任务依赖图、产物清单）。摩洛哥项目中，先定义了 `task_graph.py` 中的 TASKS 和 BATCHES，再逐章节开发，有效避免了返工和遗漏。

**实践建议**：新项目启动时，第一步不是写代码，而是填写 `config.py` 和 `task_graph.py`，确认所有章节的输入/输出关系。

### 2. 命名规范是团队协作的基石

**教训**：统一的命名规范让产物归属一目了然。摩洛哥项目采用 `ch{NN}_{描述}` 前缀（如 `ch01_cleaned_data.csv`），任何人看到文件名就知道它属于哪个章节、是什么内容。

**实践建议**：在 `config.py` 或独立文档中明确定义命名规范，包括文件名前缀、变量命名、函数命名等。

### 3. 双格式脚本（.py + .ipynb）的互补价值

**教训**：`.py` 脚本适合批量运行和自动化流水线，`.ipynb` 适合交互式探索和学习。摩洛哥项目中两种格式并存，既保证了可复现性，又降低了学习门槛。

**实践建议**：每个章节同时提供 `.py` 和 `.ipynb` 两种格式。`.py` 作为"正式版"，`.ipynb` 作为"学习版"。

### 4. 产物前缀（ch{NN}\_）的归属清晰度

**教训**：产物文件名使用章节前缀（如 `ch01_`、`ch02_`），可以快速定位文件归属。在 `task_graph.py` 的 `key_artifacts` 中定义的产物名也遵循此规范，便于自动化检查。

**实践建议**：所有输出产物必须以 `ch{NN}_` 开头，与 `output_manager.py` 的 `save_dataframe()` / `save_figure()` 配合使用。

### 5. 派活话术标准化提升效率

**教训**：当项目由多人（或 AI 助手）协作完成时，标准化的"派活话术"可以大幅减少沟通成本。摩洛哥项目采用统一的 Prompt 模板，每个章节的开发指令包含：目标、输入、步骤、产物、约束条件。

**实践建议**：定义标准的章节开发 Prompt 模板，包含五段式结构（背景、目标、输入、步骤、产物）。

### 6. 质量检查标准防止返工

**教训**：摩洛哥项目中，`metrics.py` 的质量标签体系（Outstanding/Excellent/Pass/Needs Improvement）为模型评估提供了统一标准。`compare_models()` 自动排序和标注质量等级，避免了主观判断。

**实践建议**：在项目初期就定义质量评估标准，包括指标选择、阈值设定、质量等级划分。

### 7. 并行批次划分策略（拓扑排序）

**教训**：`task_graph.py` 的批次划分基于任务依赖关系的拓扑排序。摩洛哥项目中，Batch-1 的三个任务（用电规律挖掘、短期负荷预测、中长期趋势分析）可以并行执行，因为它们只依赖 Batch-0 的数据预处理。这种并行策略将总开发时间从串行的 8 个任务缩短到 6 个批次。

**实践建议**：在 `task_graph.py` 中明确定义 `depends` 和 `batch`，利用并行批次最大化开发效率。

### 8. Skill 库复用模式（4个通用模块）

**教训**：摩洛哥项目中提炼出4个通用 Skill 模块（data_loader、visualizer、metrics、output_manager），它们不包含任何领域硬编码，可直接复用到其他项目。这4个模块覆盖了数据分析项目约 60% 的通用需求。

**实践建议**：新项目启动时，先复制4个 Skill 模块，只需修改 `config.py` 即可快速搭建框架。

### 9. Prompt 五段式结构保证完整性

**教训**：每个章节的开发 Prompt 采用五段式结构：背景（项目上下文）、目标（本章要做什么）、输入（依赖哪些数据）、步骤（详细执行步骤）、产物（输出文件清单）。这种结构确保了 AI 助手生成的代码完整且可运行。

**实践建议**：制定标准的 Prompt 模板，五段式结构是经过验证的有效模式。

### 10. Step 六子结构保证可执行性

**教训**：每个步骤（Step）内部采用六子结构：步骤编号与标题、目标说明、输入数据、处理逻辑、输出产物、验证条件。这种细粒度的结构确保每个步骤都可以独立验证。

**实践建议**：在章节脚本的注释中，每个 Step 至少包含：标题、输入、处理逻辑、输出四个要素。

---

## 附录 E: 常见问题排查指南

### 问题 1: ModuleNotFoundError: No module named 'utils'

**现象**：运行章节脚本时报 `ModuleNotFoundError`。

**原因**：`sys.path` 未正确设置，Python 找不到 `src` 目录下的 `utils` 包。

**解决方案**：
```python
# 在脚本开头添加:
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)
```

### 问题 2: FileNotFoundError: RAW_DATA_FILE not found

**现象**：数据加载时报文件不存在错误。

**原因**：`config.py` 中的 `PROJECT_ROOT` 推导路径不正确，或原始数据文件名拼写错误。

**解决方案**：
```python
# 在 config.py 中验证路径:
print(f"PROJECT_ROOT = {PROJECT_ROOT}")
print(f"RAW_DATA_FILE = {RAW_DATA_FILE}")
print(f"文件存在: {os.path.isfile(RAW_DATA_FILE)}")
```

### 问题 3: UnicodeEncodeError when saving Markdown

**现象**：`save_markdown()` 保存中文内容时报编码错误。

**原因**：系统默认编码不是 UTF-8。

**解决方案**：`save_markdown()` 已使用 `encoding='utf-8'` 显式指定。若仍报错，检查系统环境变量：
```bash
export PYTHONIOENCODING=utf-8
```

### 问题 4: matplotlib 图表中文显示为方块

**现象**：图表中的中文标签显示为方框。

**原因**：matplotlib 未找到支持中文的字体。

**解决方案**：
```python
# 在 config.py 或脚本开头添加:
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

### 问题 5: MAPE 值为 inf

**现象**：`calc_mape()` 返回 `inf`。

**原因**：真实值中存在接近零的点，导致除零。或者 `threshold` 设置过高，过滤掉了所有数据点。

**解决方案**：
```python
# 检查真实值分布:
print(f"y_true min = {y_true.min()}, max = {y_true.max()}")
print(f"y_true 中 |y| < 0.5 的比例: {(np.abs(y_true) < 0.5).mean():.2%}")

# 调整阈值:
result = evaluate_model(y_true, y_pred, 'Model', threshold=0.1)
```

### 问题 6: TaskGraph 显示所有任务"未开始"

**现象**：`TaskGraph().print_status()` 显示全部任务为"未开始"，即使产物文件已存在。

**原因**：`PROJECT_ROOT` 路径不正确，导致 `_artifact_exists()` 在错误的目录下查找文件。

**解决方案**：
```python
# 验证 PROJECT_ROOT:
from utils.config import PROJECT_ROOT
print(f"PROJECT_ROOT = {PROJECT_ROOT}")

# 手动验证产物路径:
import os
expected = os.path.join(PROJECT_ROOT, 'outputs/ch01_data_preprocessing/ch01_cleaned_data.csv')
print(f"期望路径: {expected}")
print(f"文件存在: {os.path.isfile(expected)}")
```

### 问题 7: Jupyter Notebook kernel 死亡

**现象**：执行 Notebook Cell 时 kernel 意外重启。

**原因**：内存不足（大数据集加载时常见）或 C 扩展库冲突。

**解决方案**：
```python
# 分块读取大数据:
chunk_size = 100000
chunks = pd.read_csv('large_file.csv', chunksize=chunk_size)
df = pd.concat(chunks, ignore_index=True)

# 或使用低内存数据类型:
df = df.astype({col: 'float32' for col in df.select_dtypes('float64').columns})
```

### 问题 8: openpyxl 版本不兼容

**现象**：`pd.read_excel()` 报 `BadZipFile` 或 `InvalidFileException`。

**原因**：`.xlsx` 文件格式与 `openpyxl` 版本不兼容。

**解决方案**：
```bash
pip install --upgrade openpyxl
# 或指定兼容版本:
pip install openpyxl==3.1.2
```

### 问题 9: 产物文件被覆盖

**现象**：重新运行章节脚本后，之前的产物被覆盖。

**原因**：`save_dataframe()` / `save_figure()` 默认覆盖同名文件。

**解决方案**：
```python
# 在文件名中加入时间戳:
from datetime import datetime
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'ch01_cleaned_data_{timestamp}.csv'
save_dataframe(df, filename, OUTPUT_DIR)
```

### 问题 10: 并行批次任务产物冲突

**现象**：Batch-1 的并行任务生成了同名产物文件。

**原因**：不同章节使用了相同的产物文件名（未遵循 `ch{NN}_` 前缀规范）。

**解决方案**：
- 严格执行产物命名规范：所有产物以 `ch{NN}_` 开头
- 在 `task_graph.py` 的 `key_artifacts` 中检查是否有重名
- 运行前检查：
```python
from utils.task_graph import TASKS
all_artifacts = []
for key, task in TASKS.items():
    all_artifacts.extend(task['key_artifacts'])
duplicates = [a for a in all_artifacts if all_artifacts.count(a) > 1]
if duplicates:
    print(f"发现重名产物: {set(duplicates)}")
```

### 数据分析领域常见问题

| 问题 | 诊断方法 | 解决方案 |
|------|----------|----------|
| 数据缺失率过高（>30%） | `df.isnull().mean()` 检查各列缺失率 | 考虑删除高缺失列、使用插值填充、或标记缺失并单独分析 |
| 数据格式不符合预期 | `df.dtypes` + `df.head()` 检查 | 使用 `pd.to_numeric()`、`pd.to_datetime()` 强制转换 |
| 分析结果与预期不符 | 检查数据预处理是否正确、方法参数是否合理 | 回到 flow_design.md 对应章节重新审视方法选择 |
| 并行执行时产物冲突 | 检查 task_graph.py 依赖关系是否正确 | 确保无循环依赖，修改后的产物不覆盖其他章节的输入 |
| 内存不足（大数据集） | `df.memory_usage(deep=True)` 检查 | 分块读取 `chunksize`、降精度 `astype(float32)`、使用 `dask` |
