# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260505-001] best_practice

**Logged**: 2026-05-05T12:00:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
EV market CSV header count mismatch: expected 25 columns but actual data has 24 columns.

### Details
The CSV file `ev_market_2026.csv` header line contains 25 comma-separated values, but pandas read_csv correctly parses it as 24 columns. This is because the header line's last field may include a trailing comma or the column count in documentation was inaccurate. Always verify actual column count via `df.shape[1]` rather than counting header commas.

### Suggested Action
When documenting data schemas, always verify with actual `df.shape` rather than manual header counting.

### Metadata
- Source: conversation
- Related Files: data/ev_market_2026.csv
- Tags: csv, schema, data-validation
- Pattern-Key: harden.schema_verification

---

## [LRN-20260505-002] insight

**Logged**: 2026-05-05T12:00:00Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
Duplicate key handling strategy: 930 out of 2000 rows (46.5%) are duplicates on (brand, model, year, variant) composite key.

### Details
In EV market data, the same vehicle configuration (brand+model+year+variant) appears multiple times. This could represent different data collection timestamps, regional variations, or data entry errors. The chosen strategy was to keep the first occurrence, reducing the dataset from 2000 to 1070 rows. For future analyses, consider whether aggregation (mean/median) might be more appropriate than deduplication.

### Suggested Action
When encountering high duplicate rates (>40%), investigate business meaning before choosing dedup strategy. Consider adding a `data_source` or `collection_date` column to distinguish legitimate duplicates.

### Metadata
- Source: conversation
- Related Files: src/ch01_data_cleaning/preprocess.py
- Tags: deduplication, data-quality, ev-data
- Pattern-Key: simplify.dedup_strategy

---

## [LRN-20260505-003] best_practice

**Logged**: 2026-05-05T12:00:00Z
**Priority**: low
**Status**: pending
**Area**: backend

### Summary
Winsorize vs IQR-based outlier removal: Winsorize is preferred when data size is moderate and outliers may contain valid information.

### Details
For the EV market dataset (1070 rows after dedup), Winsorize (capping at IQR boundaries) was chosen over outright removal because: (1) extreme values like high warranty_years (7-8 years) may reflect legitimate premium offerings, (2) removal would reduce already-small dataset, (3) Winsorize preserves the rank order while reducing extreme influence on statistical measures.

### Suggested Action
Default to Winsorize for datasets < 5000 rows where business context suggests outliers may be valid. Use removal only when outliers are confirmed errors.

### Metadata
- Source: conversation
- Related Files: src/ch01_data_cleaning/preprocess.py
- Tags: outliers, winsorize, data-cleaning
- Pattern-Key: simplify.outlier_handling

---

## [LRN-20260506-001] best_practice

**Logged**: 2026-05-06T12:00:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
分析目标文档应基于已有业务报告反向推导，而非从零开始收集。

### Details
用户上传了一份完整的《全球EV市场数据集完整分析报告》docx，其中已明确定义了8大核心分析目标、8大分析维度、分析方法论和预期成果。直接从报告中提取和结构化分析目标，比通过问答逐步收集效率高得多。关键是将报告中的自然语言描述转化为SMART目标格式，并映射到具体的数据字段和分析方法。

### Suggested Action
当用户已有业务报告或需求文档时，优先从中提取分析目标，而非重新收集。使用 pandoc 将 docx 转 markdown 后进行结构化提取。

### Metadata
- Source: conversation
- Related Files: docs/analysis_goals.md
- Tags: goal-setting, documentation, workflow
- Pattern-Key: simplify.goal_extraction

---

## [LRN-20260506-002] best_practice

**Logged**: 2026-05-06T14:00:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
多子代理并行生成大型文档时，需在合并后统一Markdown标题层级。

### Details
将execution_prompts.md（9147行）的生成任务拆分为4个并行子代理（Part1:头部+ch02+ch03, Part2:ch04+ch05+ch06, Part3:ch07+ch08, Part4:ch09+附录），大幅缩短生成时间。但合并后发现Part1中的Prompt-02/03使用了`###`/`####`标题层级，而Part2-4使用`##`/`###`，导致全文不一致。需要在合并后用sed按行范围批量修正标题层级。

### Suggested Action
并行生成文档时，在prompt中明确指定统一的Markdown标题层级规范（如：Prompt标题用`#`，五段式标题用`##`，子标题用`###`），避免合并后修复。或在合并步骤中加入自动化的标题层级校验和修正。

### Metadata
- Source: conversation
- Related Files: docs/ev_market_analysis_execution_prompts.md
- Tags: sub-agent, parallel-generation, markdown, heading-level
- Pattern-Key: simplify.parallel_doc_heading_consistency

---

## [LRN-20260506-003] best_practice

**Logged**: 2026-05-06T15:00:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
任务派发指南应包含每章独立话术，支持直接复制派活。

### Details
task_dispatch_guide.md 的核心价值在于"派活即复制"。每个章节的派发话术应包含：任务目标、输入数据、输出产物（含数量）、执行步骤摘要、质量验收标准、详细执行指南引用。这样执行者无需阅读完整execution_prompts.md即可开始工作，也便于多Agent并行派活。

### Suggested Action
派发话术模板：任务目标 + 输入数据 + 输出产物列表 + 执行步骤摘要 + 质量验收清单 + 详细指南引用。确保每个话术可独立使用。

### Metadata
- Source: conversation
- Related Files: docs/task_dispatch_guide.md
- Tags: task-dispatch, template, multi-agent
- Pattern-Key: simplify.dispatch_template

---

## [LRN-20260506-004] best_practice

**Logged**: 2026-05-06T16:00:00Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
代码框架更新应与执行Prompt文档保持一致，测试先行验证。

### Details
更新代码框架时，需要确保：1) 章节脚本骨架与execution_prompts.md中的步骤一致；2) 工具模块函数签名与Prompt中的代码框架一致；3) 测试覆盖关键函数。本次更新增强了visualizer.py（添加plot_model_forecast, plot_grouped_bar, plot_scatter）、metrics.py（添加compare_models, calc_r2）、output_manager.py（添加get_chapter_dir），并创建了test_utils.py覆盖全部工具模块。21个测试全部通过。

### Suggested Action
代码框架更新后立即运行测试验证，确保不引入回归。工具模块新增函数时应同步更新测试文件。

### Metadata
- Source: conversation
- Related Files: src/utils/*.py, tests/test_utils.py
- Tags: code-framework, tdd, testing
- Pattern-Key: simplify.code_framework_update
