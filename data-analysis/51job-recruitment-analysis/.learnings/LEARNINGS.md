# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260504-001] best_practice

**Logged**: 2026-05-04T12:00:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
execution_prompts 文档必须与实际章节脚本的步骤编号、函数名、产物文件名完全一致

### Details
在编写 51job 项目的 execution_prompts.md 时，发现需要逐一核对 5 个章节的 .py 脚本，确保：
1. 步骤编号与脚本中的 print 语句一致（如 Step 1.1 对应 '[Step 1.1]'）
2. 代码框架中引用的函数名与 utils 模块实际导出一致
3. 产物文件名与 task_graph.py 中定义的 key_artifacts 一致
4. config.py 中的参数名（如 DOMAIN_PARAMS['education_order']）在代码框架中正确引用

如果不做逐一核对，执行者按 Prompt 操作时会出现 import 错误或找不到文件的问题。

### Suggested Action
编写 execution_prompts 后，必须执行交叉验证：
- grep 检查所有函数名在对应模块中是否存在
- 检查所有产物文件名是否以 ch{NN}_ 开头
- 检查步骤编号是否与脚本骨架一致

### Metadata
- Source: conversation
- Related Files: docs/51job_recruitment_analysis_Execution_Prompts.md, src/ch01~ch05/*.py, src/utils/*.py
- Tags: execution_prompts, consistency, documentation

---

## [LRN-20260504-002] insight

**Logged**: 2026-05-04T12:00:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
五段式 Prompt 结构中"代码框架"是执行者最依赖的部分，必须完整可运行

### Details
execution_prompts Skill 定义的五段式结构中，"代码框架"虽然是可选子结构，但对于需要实际编码的步骤，它是执行者最直接依赖的参考。如果代码框架包含省略号（...）或伪代码，执行者需要自行推断实现细节，增加了出错概率。

最佳实践：代码框架应该是完整的、可直接复制运行的 Python 代码块，包含 import 语句、关键变量定义、核心逻辑和结果打印。

### Suggested Action
在项目规范中明确：代码框架不允许使用省略号占位，必须是完整可运行的代码

### Metadata
- Source: conversation
- Related Files: docs/51job_recruitment_analysis_Execution_Prompts.md
- Tags: execution_prompts, code_quality, best_practice

---

## [LRN-20260505-001] best_practice

**Logged**: 2026-05-05T10:00:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
task_dispatch_guide.md 的 DAG 图和批次表必须与 task_graph.py 的 TASKS/BATCHES 定义保持严格一致

### Details
在生成 task_dispatch_guide.md 时，所有依赖关系、批次划分、产物名称都必须直接来源于 task_graph.py 中的 TASKS 和 BATCHES 字典，而非手动编写。这样可以确保：
1. DAG 图中的节点和箭头与代码定义一一对应
2. 批次表中的并行度、前置依赖与代码逻辑一致
3. 速查表中的产物文件名与 key_artifacts 完全匹配
4. 派活模板中的路径与 script/notebook/output_dir 字段一致

### Suggested Action
生成 task_dispatch_guide 后，应通过 task_graph.py 的 CLI 入口验证批次划分一致性：`cd src && python -c "from utils.task_graph import TaskGraph; TaskGraph().print_status()"`

### Metadata
- Source: conversation
- Related Files: docs/task_dispatch_guide.md, src/utils/task_graph.py
- Tags: task_dispatch, consistency, dag, documentation

---

## [LRN-20260505-002] best_practice

**Logged**: 2026-05-05T11:00:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
load_preprocessed() 使用 index_col=0，与 index=False 保存的 CSV 不兼容

### Details
data_loader.py 的 load_preprocessed() 固定使用 index_col=0 读取 CSV。当 ch02/ch03/ch04 的 stats.csv 以 index=False 保存时，load_preprocessed 会将第一列数据（如 '维度'、'指标'）误当作索引列，导致 KeyError。

修复方案：对非索引型 CSV（如统计汇总表），直接使用 pd.read_csv() 而非 load_preprocessed()。仅在读取 ch01_cleaned_data.csv（以 index=True 保存）时使用 load_preprocessed()。

### Suggested Action
在项目规范中明确：load_preprocessed() 仅用于读取带索引的清洗后数据集；统计汇总表使用 pd.read_csv() 直接读取。

### Metadata
- Source: conversation
- Related Files: src/ch05_summary_report/summary.py, src/utils/data_loader.py
- Tags: data_loader, index_col, csv_loading, gotcha

---

## [LRN-20260505-003] correction

**Logged**: 2026-05-05T12:00:00Z
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
薪资单位标签与实际数值单位不一致，导致报告数值被低估 10 倍

### Details
ch01 的 _parse_salary_range() 对"万/月"格式直接保留为万/月单位，对"千/月"格式做了 /10 转换（千转万），最终所有 salary 列统一为"万/月"。但 ch02 的图表 X 轴标签和 ch05 的报告文本误写为"千/月"，导致读者误以为薪资中位数为 1.45 千/月（实际为 1.45 万/月 = 14.5 千/月）。涉及文件：config.py 第56行、salary.py 第121/142/176行、summary.py 共19处。

### Resolution
- **Resolved**: 2026-05-05
- **Notes**: 将 config.py salary_unit 改为"万/月"，将 salary.py 和 summary.py 中所有"千/月"替换为"万/月"

### Suggested Action
在 config.py 中定义 SALARY_UNIT = '万/月' 作为单一事实来源，所有图表和报告引用此常量。

### Metadata
- Source: error
- Related Files: src/utils/config.py, src/ch02_salary_analysis/salary.py, src/ch05_summary_report/summary.py
- Tags: salary_unit, data_quality, label_error

---

## [LRN-20260505-004] correction

**Logged**: 2026-05-05T12:00:00Z
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
ch01 质量报告在字段重命名之前生成，导致报告中的字段名与最终数据不一致

### Details
overview.py 的执行顺序为 Step 1.2（质量评估+报告生成）→ Step 1.3（字段重命名），导致报告中引用的是原始字段名（"学历要求"、"工作经验"），而非清洗后的字段名（"工作经验要求"、"附加要求"）。

### Resolution
- **Resolved**: 2026-05-05
- **Notes**: 将质量报告生成代码从 Step 1.2 移到 Step 1.3 之后（新增 Step 1.2b），使用重命名后的列名重新计算缺失值统计

### Suggested Action
质量报告应放在所有清洗步骤之后生成，确保报告反映数据的最终状态。

### Metadata
- Source: error
- Related Files: src/ch01_data_overview/overview.py
- Tags: field_rename, quality_report, execution_order

---

## [LRN-20260505-005] insight

**Logged**: 2026-05-05T12:00:00Z
**Priority**: medium
**Status**: resolved
**Area**: docs

### Summary
flow_design.md 与 task_graph.py 的产物文件名必须统一维护

### Details
两份文档对 ch02/ch03/ch04 的产物文件名定义不同（共16处差异），代码实现以 task_graph.py 为准，导致 flow_design.md 与实际产出不一致。已以 task_graph.py 为准更新 flow_design.md。

### Resolution
- **Resolved**: 2026-05-05
- **Notes**: 以 task_graph.py 为准更新 flow_design.md 中 ch02/ch03/ch04 的产物文件名，并在 ch04 新增 2 个产物

### Suggested Action
flow_design.md 的产物名应直接引用 task_graph.py 中的 key_artifacts，避免手动维护两份清单。

### Metadata
- Source: conversation
- Related Files: docs/flow_design.md, src/utils/task_graph.py
- Tags: documentation, artifact_names, consistency
