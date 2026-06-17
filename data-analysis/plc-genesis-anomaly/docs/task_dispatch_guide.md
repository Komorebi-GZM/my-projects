# Genesis_Anomaly_Analysis 任务分发指南

> 版本：v2.0
> 生成日期：2026-06-02
> 基于：task_dispatch 技能模板

---

## 一、全局依赖 DAG 图

```
                    ┌─────────────────────────────────────┐
                    │         Genesis_Anomaly_Analysis       │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │    Batch-1: ch01 数据概览与清洗        │
                    │    （项目入口，无前置依赖）              │
                    └─────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
    ┌───────────────────────────────┐   ┌───────────────────────────────┐
    │ Batch-2a: ch02 PLC状态机分析    │   │ Batch-2b: ch04 传感器性能分析   │
    │ （依赖 ch01，与 ch04 并行）      │   │ （依赖 ch01，与 ch02 并行）     │
    └───────────────────────────────┘   └───────────────────────────────┘
                    │                                   │
                    ▼                                   │
    ┌───────────────────────────────┐                 │
    │ Batch-3: ch03 异常检测分析      │                 │
    │ （依赖 ch02）                   │                 │
    └───────────────────────────────┘                 │
                    │                                   │
                    └───────────────┬───────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │  Batch-4: ch05 运行效能评估           │
                    │  （依赖 ch03 + ch04，汇总章节）        │
                    └─────────────────────────────────────┘
```

### 依赖关系说明

| 章节 | 前置依赖 | 后续被依赖 |
|------|---------|-----------|
| ch01 | 无 | ch02, ch04 |
| ch02 | ch01 | ch03 |
| ch03 | ch02 | ch05 |
| ch04 | ch01 | ch05 |
| ch05 | ch03, ch04 | 无 |

---

## 二、批次划分表格

| 批次 | 章节 | 并行度 | 前置依赖 | 输入数据 | 核心产物 |
|------|------|--------|---------|---------|---------|
| **Batch-1** | ch01 | 1 | 无 | `data/原始数据1/*.csv` | `dataset_info_table.csv`, `signal_baseline_stats.csv`, `report.md` |
| **Batch-2** | ch02, ch04 | 2 | ch01 | ch01 输出 + `Genesis_StateMachineLabel.csv` / `Genesis_{lineardrive,normal,pressure}.csv` | `state_duration_stats.csv`, `correlation_matrix_*.csv`, `report.md` ×2 |
| **Batch-3** | ch03 | 1 | ch02 | ch02 输出 + `Genesis_AnomalyLabels.csv` | `normal_vs_anomaly_stats.csv`, `statistical_test_results.csv`, `report.md` |
| **Batch-4** | ch05 | 1 | ch03, ch04 | ch02 + ch03 + ch04 全部输出 | `efficiency_comparison_table.csv`, `dataset_limitations.md`, `report.md` |

### 执行顺序

```
Batch-1 (ch01) → Batch-2 (ch02 ∥ ch04) → Batch-3 (ch03) → Batch-4 (ch05)
```

> **注意**：Batch-2 中 ch02 和 ch04 可并行执行，互不干扰。ch03 必须等待 ch02 完成后才能启动。ch05 必须等待 ch03 和 ch04 都完成后才能启动。

---

## 三、章节关键信息速查表

### Prompt-01: 数据概览与清洗

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-01 |
| **章节名称** | 数据概览与清洗 |
| **具体话术** | 1. 阅读 `docs/flow_design.md` 的"第一章"部分，理解分析目标<br>2. 调用 **Skill-01** (`data_loader.load_all_data()`) 加载全部 5 个 CSV 文件<br>3. 调用 **Skill-01** (`get_signal_columns()`) 获取信号列名<br>4. 计算每路信号的均值、标准差、分位数（`df.describe()`）<br>5. 统计缺失值（`df.isnull().sum()`）<br>6. 调用 **Skill-02** (`plot_distribution()`) 绘制信号分布直方图<br>7. 调用 **Skill-02** (`plot_boxplot()`) 绘制箱线图<br>8. 调用 **Skill-04** (`save_dataframe()`) 保存统计表到 `outputs/ch01/`<br>9. 调用 **Skill-04** (`save_figure()`) 保存图表到 `outputs/ch01/figures/`<br>10. 调用 **Skill-04** (`save_markdown()`) 生成 `report.md`（四段框架）<br>11. 检查标准：`outputs/ch01/` 目录下已生成 `report.md` + 至少 2 个 CSV + 至少 2 个 PNG |
| **输入数据** | `data/原始数据1/Genesis_AnomalyLabels.csv`<br>`data/原始数据1/Genesis_StateMachineLabel.csv`<br>`data/原始数据1/Genesis_lineardrive.csv`<br>`data/原始数据1/Genesis_normal.csv`<br>`data/原始数据1/Genesis_pressure.csv` |
| **核心产物** | `dataset_info_table.csv`<br>`signal_baseline_stats.csv`<br>`report.md` |
| **后续依赖方** | Prompt-02, Prompt-04 |
| **技能调用** | Skill-01 (data_loader), Skill-02 (visualizer), Skill-04 (output_manager) |
| **预计耗时** | 1-2 小时 |
| **完成时限** | 开题报告提交前（第 12 周） |

---

### Prompt-02: PLC 状态机与工序分析

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-02 |
| **章节名称** | PLC 状态机分析 |
| **具体话术** | 1. 阅读 `docs/flow_design.md` 的"第二章"部分<br>2. 调用 **Skill-01** (`load_state_machine_data()`) 加载 StateMachineLabel 数据<br>3. 使用 `df['Label'].diff().ne(0)` 识别状态边界（状态切换点）<br>4. 计算每个状态片段的持续时间，按状态分组统计（count/mean/std/min/max）<br>5. 使用 `pd.crosstab()` 构建 9×9 状态转移概率矩阵<br>6. 调用 **Skill-02** (`plot_state_timeline()`) 绘制带状态背景色的时序图<br>7. 分析 PLC 控制信号（Gripper, MaterialIsMetal）与传感器信号的联动时序<br>8. 调用 **Skill-04** (`save_dataframe()`) 保存 `state_duration_stats.csv` 和 `state_transition_matrix.csv`<br>9. 调用 **Skill-04** (`save_markdown()`) 生成 `report.md`<br>10. 检查标准：`outputs/ch02/` 下已生成 `report.md` + 2 个 CSV + 至少 1 个 PNG |
| **输入数据** | `data/原始数据1/Genesis_StateMachineLabel.csv`<br>ch01 输出（时间戳标准化后的数据） |
| **核心产物** | `state_duration_stats.csv`<br>`state_transition_matrix.csv`<br>`report.md` |
| **后续依赖方** | Prompt-03 |
| **技能调用** | Skill-01 (data_loader), Skill-02 (visualizer), Skill-04 (output_manager) |
| **预计耗时** | 2-3 小时 |
| **完成时限** | 开题报告提交前（第 12 周） |

---

### Prompt-03: 异常检测与抗干扰分析

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-03 |
| **章节名称** | 异常检测分析 |
| **具体话术** | 1. 阅读 `docs/flow_design.md` 的"第三章"部分<br>2. 调用 **Skill-01** (`load_anomaly_data()`) 加载 AnomalyLabels 数据<br>3. 调用 **Skill-01** (`split_by_label()`) 按 Label=0/1/2 分组<br>4. 计算三组信号（ActCurrent, ActPosition, ActSpeed）的描述性统计对比<br>5. 调用 **Skill-03** (`perform_ttest()`) 执行独立样本 t 检验（正常 vs 异常）<br>6. 调用 **Skill-03** (`perform_ks_test()`) 执行 KS 检验<br>7. 调用 **Skill-03** (`calc_cohens_d()`) 计算效应量<br>8. 调用 **Skill-02** (`plot_comparison()`) 绘制正常 vs 异常波形叠加对比图<br>9. 调用 **Skill-03** (`extract_time_features()`) 提取时域特征（均值、方差、峰度、偏度等）<br>10. 绘制特征箱线图，评估特征区分力（p-value < 0.05 为显著）<br>11. 调用 **Skill-04** (`save_dataframe()`) 保存统计对比表、检验结果表、特征表<br>12. 调用 **Skill-04** (`save_markdown()`) 生成 `report.md`<br>13. 检查标准：`outputs/ch03/` 下已生成 `report.md` + 3 个 CSV + 至少 2 个 PNG |
| **输入数据** | `data/原始数据1/Genesis_AnomalyLabels.csv`<br>ch01 输出（信号基准统计）<br>ch02 输出（状态片段信息，用于定位故障时段） |
| **核心产物** | `normal_vs_anomaly_stats.csv`<br>`statistical_test_results.csv`<br>`distortion_features_table.csv`<br>`report.md` |
| **后续依赖方** | Prompt-05 |
| **技能调用** | Skill-01 (data_loader), Skill-02 (visualizer), Skill-03 (metrics), Skill-04 (output_manager) |
| **预计耗时** | 3-4 小时 |
| **完成时限** | 开题报告提交前（第 12 周） |

---

### Prompt-04: 传感器性能关联分析

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-04 |
| **章节名称** | 传感器性能分析 |
| **具体话术** | 1. 阅读 `docs/flow_design.md` 的"第四章"部分<br>2. 调用 **Skill-01** (`load_condition_data()`) 分别加载 lineardrive、normal、pressure 三个文件<br>3. 调用 **Skill-01** (`get_common_columns()`) 获取共同列<br>4. 对每种工况计算 Pearson 相关系数矩阵（`df.corr()`）<br>5. 调用 **Skill-02** (`plot_heatmap()`) 绘制三种工况的相关性热力图<br>6. 对比不同工况下相关性显著变化的信号对<br>7. 调用 **Skill-03** (`calc_stability_score()`) 计算滑动窗口标准差和变异系数<br>8. 对各信号进行稳定性排序<br>9. 分析电流-速度、力控-位置的联动关系<br>10. 调用 **Skill-04** (`save_dataframe()`) 保存相关性矩阵和稳定性评分<br>11. 调用 **Skill-04** (`save_markdown()`) 生成 `report.md`<br>12. 检查标准：`outputs/ch04/` 下已生成 `report.md` + 3 个 CSV + 至少 1 个 PNG |
| **输入数据** | `data/原始数据1/Genesis_lineardrive.csv`<br>`data/原始数据1/Genesis_normal.csv`<br>`data/原始数据1/Genesis_pressure.csv`<br>ch01 输出（清洗后数据） |
| **核心产物** | `correlation_matrix_normal.csv`<br>`correlation_matrix_lineardrive.csv`<br>`correlation_matrix_pressure.csv`<br>`signal_stability_scores.csv`<br>`report.md` |
| **后续依赖方** | Prompt-05 |
| **技能调用** | Skill-01 (data_loader), Skill-02 (visualizer), Skill-03 (metrics), Skill-04 (output_manager) |
| **预计耗时** | 2-3 小时 |
| **完成时限** | 开题报告提交前（第 12 周） |

---

### Prompt-05: 运行效能评估

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-05 |
| **章节名称** | 运行效能评估 |
| **具体话术** | 1. 阅读 `docs/flow_design.md` 的"第五章"部分<br>2. 加载 ch02 的 `state_duration_stats.csv` 和 `state_transition_matrix.csv`<br>3. 加载 ch03 的异常统计结果<br>4. 基于状态转移识别完整分拣周期（Idle → ... → Idle）<br>5. 计算单周期平均耗时、标准差、最大/最小值<br>6. 计算单位时间分拣件数、理论 vs 实际效率<br>7. 统计连续无故障运行时长、异常发生率<br>8. 量化正常 vs 故障工况下的效率差异<br>9. 分析数据集局限性（样本不平衡、信号类型有限、时间范围单一等）<br>10. 提出后续补充数据集建议<br>11. 调用 **Skill-04** (`save_dataframe()`) 保存效率对比表和稳定性评估<br>12. 调用 **Skill-04** (`save_markdown()`) 生成 `report.md` 和 `dataset_limitations.md`<br>13. 检查标准：`outputs/ch05/` 下已生成 `report.md` + 3 个 CSV + `dataset_limitations.md` |
| **输入数据** | ch02 输出（`state_duration_stats.csv`, `state_transition_matrix.csv`）<br>ch03 输出（异常统计结果）<br>ch04 输出（稳定性评分） |
| **核心产物** | `sorting_cycle_stats.csv`<br>`efficiency_comparison_table.csv`<br>`system_stability_assessment.csv`<br>`dataset_limitations.md`<br>`report.md` |
| **后续依赖方** | 无（项目收尾章节） |
| **技能调用** | Skill-04 (output_manager) |
| **预计耗时** | 2-3 小时 |
| **完成时限** | 第 16 周课堂展示前 |

---

## 四、执行命令参考

### 单个章节执行

```bash
# Batch-1
python src/ch01_data_overview_and_cleaning/script.py

# Batch-2（并行）
python src/ch02_plc_state_machine_analysis/script.py
python src/ch04_sensor_performance_analysis/script.py

# Batch-3
python src/ch03_anomaly_detection_analysis/script.py

# Batch-4
python src/ch05_performance_evaluation/script.py
```

### 使用 task_graph 检查进度

```python
from src.utils.task_graph import TaskGraph, print_execution_plan

# 打印执行计划
print_execution_plan()

# 检查任务状态
graph = TaskGraph()
graph.print_status()

# 获取可执行任务
ready = graph.get_ready_tasks()
print(f"当前可执行: {ready}")
```

---

## 五、核心规则重申

1. **严禁跳批**：Batch-2 必须等 ch01 完成后启动，Batch-3 必须等 ch02 完成后启动，Batch-4 必须等 ch03 和 ch04 都完成后启动
2. **数据不覆盖**：每个章节的产物写入独立的 `outputs/chXX/` 目录
3. **脚本双格式**：每个章节提供 `.py`（批量执行）+ `.ipynb`（交互学习）
4. **全局配置共享**：所有脚本通过 `src/utils/config.py` 统一路径和参数
5. **章节报告必需**：每个章节执行后必须生成 `outputs/chXXX/report.md`（四段框架）
6. **技能调用明确**：每个 Prompt 必须注明需要调用的 Skill 及具体函数

---

## 六、修订记录

| 版本 | 日期 | 修订内容 |
|------|------|---------|
| v1.0 | 2026-06-02 | 初始版本，基于 task_dispatch v2.0 模板生成，含 5 个 Prompt 完整话术 |
