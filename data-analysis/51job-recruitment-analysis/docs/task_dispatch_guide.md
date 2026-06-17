# 基于51job招聘数据的人才市场全维度分析 — 任务分发指南

> **版本**: v1.1 | **更新日期**: 2026-05-05
> **本文档定义了项目的任务分发规范。每次派活时，将对应批次的「派活模板」直接发给执行者即可。**

---

## 文档说明

本文档是四份核心文档链的最终环节，承接上游的 `flow_design.md`（研究设计）和 `51job_recruitment_analysis_Execution_Prompts.md`（执行细节），为多 Agent 并行执行提供**任务调度与依赖管理**的完整规范。

**四份核心文档关系**：

| 文档 | 定位 | 关键词 |
|------|------|--------|
| `project_convention.md` | 项目宪法 | 命名规范、目录结构、禁止事项 |
| `flow_design.md` | 研究设计 | 六节结构：目标→数据→方法→步骤→产物→标准 |
| `task_dispatch_guide.md`（本文档） | 执行手册 | DAG 依赖图、批次划分、派活模板 |
| `51job_recruitment_analysis_Execution_Prompts.md` | 执行细节 | 五节结构：概述→步骤→产物→优化→异常 |

---

## 一、全局依赖图

### 1.1 ASCII DAG 图

```
                    ┌──────────────────────────────┐
                    │  Prompt-01 (基础数据概览)      │
                    │  ch01: 数据清洗与质量评估       │
                    └──────────────┬───────────────┘
                                   │
                         ch01_cleaned_data.csv
                         ch01_data_quality_report.md
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │ Prompt-02        │ │ Prompt-03        │ │ Prompt-04        │
    │ (薪资维度分析)    │ │ (供需维度分析)    │ │ (企业特征分析)    │
    │ 支线 A           │ │ 支线 B           │ │ 支线 C           │
    └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
             │                    │                    │
             │ ch02_salary_stats  │ ch03_supply_demand │ ch04_enterprise
             │        .csv        │        _stats.csv  │        _stats.csv
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────────┐
                    │  Prompt-05 (总结报告)          │
                    │  ch05: 综合结论与可视化仪表盘   │
                    └──────────────────────────────┘
                                  │
                                  ▼
                         ch05_final_report.md
                         ch05_dashboard.png
```

### 1.2 依赖关系详解

| 上游 Prompt | 下游 Prompt | 传递的关键产物 | 说明 |
|-------------|-------------|---------------|------|
| Prompt-01 | Prompt-02 | `ch01_cleaned_data.csv` | 清洗后数据集是薪资分析的唯一数据源 |
| Prompt-01 | Prompt-03 | `ch01_cleaned_data.csv` | 清洗后数据集是供需分析的唯一数据源 |
| Prompt-01 | Prompt-04 | `ch01_cleaned_data.csv` | 清洗后数据集是企业特征分析的唯一数据源 |
| Prompt-02 | Prompt-05 | `ch02_salary_stats.csv` | 薪资统计结果汇入总结报告 |
| Prompt-03 | Prompt-05 | `ch03_supply_demand_stats.csv` | 供需统计结果汇入总结报告 |
| Prompt-04 | Prompt-05 | `ch04_enterprise_stats.csv` | 企业特征统计结果汇入总结报告 |

### 1.3 拓扑排序验证

```
输入: 5 个任务节点, 6 条依赖边
算法: Kahn 拓扑排序 + 入度归零分层

Step 1: 入度为 0 的节点 → [Prompt-01]  → Batch-1
Step 2: 移除 Prompt-01 后入度为 0 → [Prompt-02, Prompt-03, Prompt-04]  → Batch-2
Step 3: 移除 02/03/04 后入度为 0 → [Prompt-05]  → Batch-3

结果: 无循环依赖 ✓ | 最大并行度 = 3 (Batch-2)
```

---

## 二、批次划分

### 2.1 批次总览表

| 批次 | 名称 | 包含任务 | 并行度 | 前置依赖 | 数据源 |
|------|------|----------|--------|----------|--------|
| Batch-0 | 环境初始化 | （无 Prompt） | — | — | `requirements.txt` |
| Batch-1 | 数据概览（串行前置） | Prompt-01 | 1（串行） | Batch-0 完成 | `data/前程无忧数据集.csv` |
| Batch-2 | 三维度并行分析 | Prompt-02 + Prompt-03 + Prompt-04 | 3（并行） | Prompt-01 全部产物 | `outputs/ch01_data_overview/ch01_cleaned_data.csv` |
| Batch-3 | 总结报告（串行收束） | Prompt-05 | 1（串行） | Prompt-02 + 03 + 04 全部产物 | `outputs/ch02_salary_analysis/ch02_salary_stats.csv` + `outputs/ch03_supply_demand/ch03_supply_demand_stats.csv` + `outputs/ch04_enterprise_features/ch04_enterprise_stats.csv` |

### 2.2 批次详细说明

#### Batch-0: 环境初始化

| 项目 | 内容 |
|------|------|
| **目标** | 确保 Python 环境和依赖就绪 |
| **操作** | `conda activate py310 && pip install -r requirements.txt` |
| **验证** | `cd src && python -c "from utils.data_loader import load_raw_data; print(len(load_raw_data()))"` → 输出 `295` |
| **完成标志** | 无报错退出，打印 295 |

#### Batch-1: 数据概览（串行前置）

| 项目 | 内容 |
|------|------|
| **Prompt** | Prompt-01 基础数据概览 |
| **脚本** | `src/ch01_data_overview/overview.py` |
| **Notebook** | `src/ch01_data_overview/overview.ipynb` |
| **输入** | `data/前程无忧数据集.csv`（297 行，含 1 行重复表头） |
| **输出目录** | `outputs/ch01_data_overview/` |
| **关键产物** | `ch01_cleaned_data.csv`, `ch01_data_quality_report.md`, `ch01_missing_values.png`, `ch01_field_distribution.png` |
| **完成标志** | `ch01_cleaned_data.csv` 存在且行数 = 295 |
| **下游影响** | 所有后续章节（02/03/04/05）均依赖此批次产物 |

#### Batch-2: 三维度并行分析

| 项目 | 支线 A | 支线 B | 支线 C |
|------|--------|--------|--------|
| **Prompt** | Prompt-02 | Prompt-03 | Prompt-04 |
| **名称** | 薪资维度分析 | 供需维度分析 | 企业特征分析 |
| **脚本** | `src/ch02_salary_analysis/salary.py` | `src/ch03_supply_demand/supply_demand.py` | `src/ch04_enterprise_features/enterprise.py` |
| **Notebook** | `salary.ipynb` | `supply_demand.ipynb` | `enterprise.ipynb` |
| **输入** | `ch01_cleaned_data.csv` | `ch01_cleaned_data.csv` | `ch01_cleaned_data.csv` |
| **输出目录** | `outputs/ch02_salary_analysis/` | `outputs/ch03_supply_demand/` | `outputs/ch04_enterprise_features/` |
| **关键产物** | `ch02_salary_distribution.png`, `ch02_salary_by_education.png`, `ch02_salary_by_experience.png`, `ch02_salary_by_industry_boxplot.png`, `ch02_salary_by_company_nature.png`, `ch02_salary_by_company_size.png`, `ch02_salary_stats.csv` | `ch03_job_type_top20.png`, `ch03_city_hiring_ranking.png`, `ch03_industry_demand_pie.png`, `ch03_education_experience_heatmap.png`, `ch03_supply_demand_stats.csv` | `ch04_nature_pie.png`, `ch04_size_bar.png`, `ch04_welfare_top15.png`, `ch04_welfare_by_nature.png`, `ch04_industry_welfare_heatmap.png`, `ch04_edu_by_nature_heatmap.png`, `ch04_benefit_salary_correlation.png`, `ch04_recruitment_preference.png`, `ch04_enterprise_stats.csv` |
| **完成标志** | `ch02_salary_stats.csv` 存在 | `ch03_supply_demand_stats.csv` 存在 | `ch04_enterprise_stats.csv` 存在 |
| **下游影响** | Prompt-05 | Prompt-05 | Prompt-05 |

> **并行说明**：三条支线（A/B/C）共享同一输入文件 `ch01_cleaned_data.csv`，互不写入对方目录，可安全并行执行。并行度 = 3。

#### Batch-3: 总结报告（串行收束）

| 项目 | 内容 |
|------|------|
| **Prompt** | Prompt-05 总结报告 |
| **脚本** | `src/ch05_summary_report/summary.py` |
| **Notebook** | `src/ch05_summary_report/summary.ipynb` |
| **输入** | `ch02_salary_stats.csv` + `ch03_supply_demand_stats.csv` + `ch04_enterprise_stats.csv` + 各章节全部图表产物 |
| **输出目录** | `outputs/ch05_summary_report/` |
| **关键产物** | `ch05_final_report.md`, `ch05_dashboard.png` |
| **完成标志** | `ch05_final_report.md` 存在且非空 |
| **下游影响** | 无（最终产物） |

---

## 三、派活模板

### 模板 A：完整项目启动（从零开始）

```
【基于51job招聘数据的人才市场全维度分析 — 完整任务分发】

项目路径: 51job_recruitment_analysis/
环境激活: conda activate py310
规范文档: docs/project_convention.md
研究设计: docs/flow_design.md
执行Prompt: docs/51job_recruitment_analysis_Execution_Prompts.md

═══════════════════════════════════════════════════════════
  阶段 0：环境初始化
═══════════════════════════════════════════════════════════
▶ Batch-0: 环境初始化
  - 命令: conda activate py310 && pip install -r requirements.txt
  - 验证: cd src && python -c "from utils.data_loader import load_raw_data; print(len(load_raw_data()))"
  - 完成标志: 输出 295，无报错

═══════════════════════════════════════════════════════════
  阶段 1：串行前置（必须最先完成）
═══════════════════════════════════════════════════════════
▶ Batch-1: Prompt-01 基础数据概览
  - 脚本: src/ch01_data_overview/overview.py
  - Notebook: src/ch01_data_overview/overview.ipynb
  - 产物: outputs/ch01_data_overview/ (4个文件)
  - 完成标志: ch01_cleaned_data.csv 存在且行数 = 295
  - ⚠️ 所有后续章节依赖此批次，必须确认产物完整后再推进

═══════════════════════════════════════════════════════════
  阶段 2：3路并行（Batch-1 完成后启动）
═══════════════════════════════════════════════════════════
▶ 支线 A: Prompt-02 薪资维度分析
  - 依赖: outputs/ch01_data_overview/ch01_cleaned_data.csv
  - 脚本: src/ch02_salary_analysis/salary.py
  - 产物: outputs/ch02_salary_analysis/ (7个文件)
  - 完成标志: ch02_salary_stats.csv 存在

▶ 支线 B: Prompt-03 供需维度分析
  - 依赖: outputs/ch01_data_overview/ch01_cleaned_data.csv
  - 脚本: src/ch03_supply_demand/supply_demand.py
  - 产物: outputs/ch03_supply_demand/ (5个文件)
  - 完成标志: ch03_supply_demand_stats.csv 存在

▶ 支线 C: Prompt-04 企业特征分析
  - 依赖: outputs/ch01_data_overview/ch01_cleaned_data.csv
  - 脚本: src/ch04_enterprise_features/enterprise.py
  - 产物: outputs/ch04_enterprise_features/ (9个文件)
  - 完成标志: ch04_enterprise_stats.csv 存在

  ⚠️ 三条支线共享输入、独立输出，可安全并行。全部完成后进入阶段3。

═══════════════════════════════════════════════════════════
  阶段 3：串行收束（Batch-2 全部完成后启动）
═══════════════════════════════════════════════════════════
▶ Batch-3: Prompt-05 总结报告
  - 依赖:
    ├── outputs/ch02_salary_analysis/ch02_salary_stats.csv
    ├── outputs/ch03_supply_demand/ch03_supply_demand_stats.csv
    └── outputs/ch04_enterprise_features/ch04_enterprise_stats.csv
  - 脚本: src/ch05_summary_report/summary.py
  - 产物: outputs/ch05_summary_report/ (2个文件)
  - 完成标志: ch05_final_report.md 存在且非空

═══════════════════════════════════════════════════════════
  全部完成 ✓
═══════════════════════════════════════════════════════════
```

### 模板 B：只派某个批次

```
【基于51job招聘数据的人才市场全维度分析 — Batch-{X} 任务】

项目路径: 51job_recruitment_analysis/
环境激活: conda activate py310
规范文档: docs/project_convention.md
执行Prompt: docs/51job_recruitment_analysis_Execution_Prompts.md（对应 Prompt-{NN} 章节）

本批次: Prompt-{NN} [{章节名称}]
前置依赖: {列出全部上游产物文件路径}
输入数据: {列出全部输入文件路径}
输出产物: outputs/{输出目录}/
完成标志: {最关键的1~2个产物文件名}

执行步骤:
1. 激活环境: conda activate py310
2. 检查前置: 确认上述「前置依赖」文件全部存在
3. 执行脚本: python {脚本路径}
   或交互执行: jupyter lab {notebook路径}
4. 验证产物: 确认「完成标志」文件存在且内容正确
```

**各批次具体参数**：

| 批次 | Prompt | 章节名称 | 前置依赖 | 输入数据 | 输出目录 | 完成标志 |
|------|--------|----------|----------|----------|----------|----------|
| Batch-1 | Prompt-01 | 基础数据概览 | 无（仅环境就绪） | `data/前程无忧数据集.csv` | `outputs/ch01_data_overview/` | `ch01_cleaned_data.csv` (295行) |
| Batch-2A | Prompt-02 | 薪资维度分析 | `ch01_cleaned_data.csv` | `outputs/ch01_data_overview/ch01_cleaned_data.csv` | `outputs/ch02_salary_analysis/` | `ch02_salary_stats.csv` |
| Batch-2B | Prompt-03 | 供需维度分析 | `ch01_cleaned_data.csv` | `outputs/ch01_data_overview/ch01_cleaned_data.csv` | `outputs/ch03_supply_demand/` | `ch03_supply_demand_stats.csv` |
| Batch-2C | Prompt-04 | 企业特征分析 | `ch01_cleaned_data.csv` | `outputs/ch01_data_overview/ch01_cleaned_data.csv` | `outputs/ch04_enterprise_features/` | `ch04_enterprise_stats.csv` |
| Batch-3 | Prompt-05 | 总结报告 | `ch02_salary_stats.csv` + `ch03_supply_demand_stats.csv` + `ch04_enterprise_stats.csv` | 三个 stats.csv + 各章节图表 | `outputs/ch05_summary_report/` | `ch05_final_report.md` (非空) |

### 模板 C：检查进度（一句话提醒）

```
检查「基于51job招聘数据的人才市场全维度分析」进度：

Batch-0(环境) → Batch-1(01串行) → Batch-2(02+03+04并行) → Batch-3(05串行)

快速检查命令:
  cd 51job_recruitment_analysis/src && python -c "from utils.task_graph import TaskGraph; TaskGraph().print_status()"

当前应在哪个批次？哪些产物已产出？
```

---

## 四、每个 Prompt 的关键信息速查

### 4.1 速查表

| Prompt | 名称 | 输入 | 核心产物 | 后续依赖方 |
|--------|------|------|----------|-----------|
| Prompt-01 | 基础数据概览 | `data/前程无忧数据集.csv` | `ch01_cleaned_data.csv`, `ch01_data_quality_report.md`, `ch01_missing_values.png`, `ch01_field_distribution.png` | Prompt-02, Prompt-03, Prompt-04, Prompt-05（全部） |
| Prompt-02 | 薪资维度分析 | `ch01_cleaned_data.csv` | `ch02_salary_distribution.png`, `ch02_salary_by_education.png`, `ch02_salary_by_experience.png`, `ch02_salary_by_industry_boxplot.png`, `ch02_salary_by_company_nature.png`, `ch02_salary_by_company_size.png`, `ch02_salary_stats.csv` | Prompt-05 |
| Prompt-03 | 供需维度分析 | `ch01_cleaned_data.csv` | `ch03_job_type_top20.png`, `ch03_city_hiring_ranking.png`, `ch03_industry_demand_pie.png`, `ch03_education_experience_heatmap.png`, `ch03_supply_demand_stats.csv` | Prompt-05 |
| Prompt-04 | 企业特征分析 | `ch01_cleaned_data.csv` | `ch04_nature_pie.png`, `ch04_size_bar.png`, `ch04_welfare_top15.png`, `ch04_welfare_by_nature.png`, `ch04_industry_welfare_heatmap.png`, `ch04_edu_by_nature_heatmap.png`, `ch04_benefit_salary_correlation.png`, `ch04_recruitment_preference.png`, `ch04_enterprise_stats.csv` | Prompt-05 |
| Prompt-05 | 总结报告 | `ch02_salary_stats.csv` + `ch03_supply_demand_stats.csv` + `ch04_enterprise_stats.csv` + 各章节图表 | `ch05_final_report.md`, `ch05_dashboard.png` | 无（最终产物） |

### 4.2 产物文件完整清单

| 章节 | 输出目录 | 产物文件 | 类型 |
|------|----------|----------|------|
| ch01 | `outputs/ch01_data_overview/` | `ch01_cleaned_data.csv` | 数据 |
| ch01 | `outputs/ch01_data_overview/` | `ch01_data_quality_report.md` | 报告 |
| ch01 | `outputs/ch01_data_overview/` | `ch01_missing_values.png` | 图表 |
| ch01 | `outputs/ch01_data_overview/` | `ch01_field_distribution.png` | 图表 |
| ch02 | `outputs/ch02_salary_analysis/` | `ch02_salary_distribution.png` | 图表 |
| ch02 | `outputs/ch02_salary_analysis/` | `ch02_salary_by_education.png` | 图表 |
| ch02 | `outputs/ch02_salary_analysis/` | `ch02_salary_by_experience.png` | 图表 |
| ch02 | `outputs/ch02_salary_analysis/` | `ch02_salary_by_industry_boxplot.png` | 图表 |
| ch02 | `outputs/ch02_salary_analysis/` | `ch02_salary_by_company_nature.png` | 图表 |
| ch02 | `outputs/ch02_salary_analysis/` | `ch02_salary_by_company_size.png` | 图表 |
| ch02 | `outputs/ch02_salary_analysis/` | `ch02_salary_stats.csv` | 数据 |
| ch03 | `outputs/ch03_supply_demand/` | `ch03_job_type_top20.png` | 图表 |
| ch03 | `outputs/ch03_supply_demand/` | `ch03_city_hiring_ranking.png` | 图表 |
| ch03 | `outputs/ch03_supply_demand/` | `ch03_industry_demand_pie.png` | 图表 |
| ch03 | `outputs/ch03_supply_demand/` | `ch03_education_experience_heatmap.png` | 图表 |
| ch03 | `outputs/ch03_supply_demand/` | `ch03_supply_demand_stats.csv` | 数据 |
| ch04 | `outputs/ch04_enterprise_features/` | `ch04_nature_pie.png` | 图表 |
| ch04 | `outputs/ch04_enterprise_features/` | `ch04_size_bar.png` | 图表 |
| ch04 | `outputs/ch04_enterprise_features/` | `ch04_welfare_top15.png` | 图表 |
| ch04 | `outputs/ch04_enterprise_features/` | `ch04_welfare_by_nature.png` | 图表 |
| ch04 | `outputs/ch04_enterprise_features/` | `ch04_industry_welfare_heatmap.png` | 图表 |
| ch04 | `outputs/ch04_enterprise_features/` | `ch04_edu_by_nature_heatmap.png` | 图表 |
| ch04 | `outputs/ch04_enterprise_features/` | `ch04_benefit_salary_correlation.png` | 图表 |
| ch04 | `outputs/ch04_enterprise_features/` | `ch04_recruitment_preference.png` | 图表 |
| ch04 | `outputs/ch04_enterprise_features/` | `ch04_enterprise_stats.csv` | 数据 |
| ch05 | `outputs/ch05_summary_report/` | `ch05_final_report.md` | 报告 |
| ch05 | `outputs/ch05_summary_report/` | `ch05_dashboard.png` | 图表 |

> **产物总计**: 27 个文件（4 数据 + 2 报告 + 21 图表）

---

## 五、注意事项

1. **严禁跳批**：每个批次必须等前置依赖全部完成后再启动。Batch-2 的三条支线必须在 Batch-1 的 `ch01_cleaned_data.csv` 产出后才能启动；Batch-3 必须在 Batch-2 三条支线的 stats.csv 全部产出后才能启动。
2. **数据不覆盖**：每个章节的产物写入独立的 `outputs/ch{NN}_{dir_name}/` 目录，互不干扰。`data/` 目录为只读，禁止任何脚本修改原始数据。
3. **脚本双格式**：每个章节提供 `.py`（批量执行）+ `.ipynb`（交互学习）两种格式，内容一致。批量执行优先使用 `.py`，调试和学习时使用 `.ipynb`。
4. **全局配置共享**：所有脚本通过 `src/utils/config.py` 统一路径和参数，修改配置只需改一处。运行 `.py` 脚本时需从项目根目录执行：`python src/chXX_xxx/script.py`。
5. **进度检查**：随时可通过 `cd src && python -c "from utils.task_graph import TaskGraph; TaskGraph().print_status()"` 查看当前进度和产物完成情况。
6. **字段语义错位**：原始数据存在字段语义错位（"学历要求"列实际存储工作经验信息，"工作经验"列实际存储附加要求），ch01 数据清洗时已做字段重命名处理，后续章节使用清洗后数据无需关注此问题。

---

## 附录 A：拓扑排序算法实现

项目已内置拓扑排序和进度检查功能，位于 `src/utils/task_graph.py`：

```python
from utils.task_graph import TaskGraph

# 初始化（自动检测项目根目录）
tg = TaskGraph()

# 检查某任务是否可以启动
result = tg.check_ready('prompt-02')
# → {'ready': True/False, 'missing_artifacts': [...]}

# 查看全部任务状态
status = tg.get_status()
# → [{'task': 'prompt-01', 'name': '基础数据概览', 'batch': 1, 'status': '已完成'}, ...]

# 推断当前应执行批次
current = tg.get_current_batch()
# → 1, 2, 3, 或 4（全部完成）

# 打印进度总览（推荐）
tg.print_status()
```

## 附录 B：批次执行时间估算

| 批次 | 任务数 | 预估单次执行时间 | 说明 |
|------|--------|-----------------|------|
| Batch-0 | — | ~2 分钟 | 依赖安装（首次），后续跳过 |
| Batch-1 | 1 | ~1 分钟 | 数据加载+清洗+质量评估 |
| Batch-2 | 3（并行） | ~1-2 分钟/支线 | 三支线并行，总耗时取决于最慢支线 |
| Batch-3 | 1 | ~1 分钟 | 汇总统计+生成报告+仪表盘 |
| **总计** | **5** | **~5-8 分钟** | 并行执行时约 5 分钟 |

## 附录 C：异常处理速查

| 异常场景 | 排查步骤 |
|----------|----------|
| `ModuleNotFoundError: No module named 'utils'` | 确认从项目根目录运行，或 `cd src` 后运行 |
| `FileNotFoundError: 前程无忧数据集.csv` | 确认 `data/前程无忧数据集.csv` 存在 |
| `ch01_cleaned_data.csv` 行数 ≠ 295 | 检查原始数据是否有新增的重复表头行 |
| Batch-2 支线报错 | 确认 `ch01_cleaned_data.csv` 已正确生成且路径正确 |
| Batch-3 报错缺少 stats.csv | 确认 Batch-2 三条支线的 stats.csv 全部存在 |
| 图表中文乱码 | 确认系统已安装 SimHei 或 WenQuanYi Micro Hei 字体 |
