# Genesis_Anomaly_Analysis 项目交付物清单

> **项目名称**: PLC小型零件自动分拣系统——基于Genesis工业数据集的传感器性能、异常检测与运行效能分析
> **验收日期**: 2026-06-03 | **验收标准**: quality_check v2.2
> **综合评分**: 9.8/10
> **补救记录**: ch01/ch02/ch03/ch04 四份 report.md 已按v2.2质量门控标准补救重写

---

## 一、项目根目录结构

```
Genesis_Anomaly_Analysis/
├── data/                          # 原始数据（只读）
│   └── 原始数据1/
│       ├── Genesis_AnomalyLabels.csv          (16,220行)
│       ├── Genesis_StateMachineLabel.csv      (16,220行)
│       ├── Genesis_lineardrive.csv            (7,424行)
│       ├── Genesis_normal.csv                 (7,040行)
│       └── Genesis_pressure.csv               (8,476行)
├── docs/                          # 项目文档
│   ├── analysis_goals.md          # 分析目标与SMART目标
│   ├── project_convention.md      # 项目规范
│   ├── flow_design.md             # 研究设计
│   ├── execution_prompts.md       # 执行指令
│   └── task_dispatch_guide.md     # 任务调度指南
├── src/                           # 源代码
│   ├── utils/                     # 工具模块（6个）
│   │   ├── config.py
│   │   ├── data_loader.py
│   │   ├── visualizer.py
│   │   ├── metrics.py
│   │   ├── output_manager.py
│   │   └── task_graph.py
│   ├── ch01_data_overview_and_cleaning/
│   │   ├── script.py              ✅ exit code 0
│   │   └── notebook.ipynb
│   ├── ch02_plc_state_machine_analysis/
│   │   ├── script.py              ✅ exit code 0
│   │   └── notebook.ipynb
│   ├── ch03_anomaly_detection_analysis/
│   │   ├── script.py              ✅ exit code 0
│   │   └── notebook.ipynb
│   ├── ch04_sensor_performance_analysis/
│   │   ├── script.py              ✅ exit code 0
│   │   └── notebook.ipynb
│   └── ch05_performance_evaluation/
│       ├── script.py              ✅ exit code 0
│       └── notebook.ipynb
├── outputs/                       # 分析产物（按章节归档）
│   ├── ch01_data_overview_and_cleaning/   (17个产物)
│   ├── ch02_plc_state_machine_analysis/   (5个产物)
│   ├── ch03_anomaly_detection_analysis/   (7个产物)
│   ├── ch04_sensor_performance_analysis/  (7个产物)
│   ├── ch05_performance_evaluation/       (6个产物)
│   ├── quality_report.md          # 质量验收报告
│   └── delivery_checklist.md      # 本文件
├── requirements.txt               # Python依赖
└── project_params.json            # 项目参数配置
```

---

## 二、章节交付物明细

### ch01 数据概览与清洗（17个产物）

| 文件名 | 类型 | 说明 | 状态 |
|--------|------|------|:---:|
| dataset_info_table.csv | CSV | 5个数据文件基本信息 | ✅ |
| signal_baseline_stats.csv | CSV | 模拟量信号描述性统计 | ✅ |
| missing_value_stats.csv | CSV | 缺失值统计（全部0.0%） | ✅ |
| signal_distribution_ch01.png | PNG | 信号分布直方图 | ✅ |
| signal_boxplot_ch01.png | PNG | 信号箱线图 | ✅ |
| data_quality_report.md | MD | 数据质量报告 | ✅ |
| report.md | MD | 章节执行报告（65行，含表格+图引用） | ✅ 补救 |
| *(额外)* 12张信号独立分布图 | PNG | 每路信号独立可视化 | ✅ |

### ch02 PLC状态机与工序分析（5个产物）

| 文件名 | 类型 | 说明 | 状态 |
|--------|------|------|:---:|
| state_duration_stats.csv | CSV | 9状态持续时间统计（357个片段） | ✅ |
| state_transition_matrix.csv | CSV | 9×9状态转移概率矩阵 | ✅ |
| plc_state_transition.png | PNG | 状态转移可视化 | ✅ |
| sorting_process_timeseries.png | PNG | 分拣工序时序图 | ✅ |
| report.md | MD | 章节执行报告（86行，含表格+图引用） | ✅ 补救 |

### ch03 异常检测与抗干扰分析（7个产物）

| 文件名 | 类型 | 说明 | 状态 |
|--------|------|------|:---:|
| normal_vs_anomaly_stats.csv | CSV | 正常/异常样本统计对比 | ✅ |
| statistical_test_results.csv | CSV | t-test/KS-test结果 | ✅ |
| signal_comparison_normal_anomaly.png | PNG | 正常vs异常信号对比图 | ✅ |
| distortion_features_table.csv | CSV | 畸变特征表 | ✅ |
| feature_importance_ranking.csv | CSV | Cohen's d特征排序 | ✅ |
| report.md | MD | 章节执行报告（62行，含表格+图引用） | ✅ 补救 |
| *(额外)* feature_boxplots_by_group.png | PNG | 特征箱线图 | ✅ |

### ch04 传感器性能关联分析（7个产物）

| 文件名 | 类型 | 说明 | 状态 |
|--------|------|------|:---:|
| correlation_matrix_normal.csv | CSV | 正常工况Pearson相关矩阵 | ✅ |
| correlation_matrix_lineardrive.csv | CSV | 线驱工况Pearson相关矩阵 | ✅ |
| correlation_matrix_pressure.csv | CSV | 气压工况Pearson相关矩阵 | ✅ |
| sensor_correlation_heatmap.png | PNG | 传感器相关性热力图 | ✅ |
| correlation_diff_by_condition.csv | CSV | 工况间相关性差异 | ✅ |
| signal_stability_scores.csv | CSV | 信号稳定性评分 | ✅ |
| report.md | MD | 章节执行报告（64行，含表格+图引用） | ✅ 补救 |

### ch05 运行效能评估（6个产物）

| 文件名 | 类型 | 说明 | 状态 |
|--------|------|------|:---:|
| sorting_cycle_stats.csv | CSV | 分拣周期统计（43个周期） | ✅ |
| sorting_cycle_details.csv | CSV | 周期明细数据 | ✅ |
| efficiency_comparison_table.csv | CSV | 效率对比表（正常vs故障） | ✅ |
| system_stability_assessment.csv | CSV | 系统稳定性评估（MTBF=4.2min） | ✅ |
| dataset_limitations.md | MD | 数据集局限性分析 | ✅ |
| report.md | MD | 章节执行报告（173行，含表格） | ✅ |

---

## 三、核心分析结论摘要（可直接用于开题报告）

### 3.1 数据质量
- **5个CSV文件**全部加载成功，总计 **55,380行**数据
- 时间戳格式已统一（秒/毫秒自动识别转换）
- 缺失值比例 **0.0%**，数据完整性优秀

### 3.2 PLC状态机
- 识别出 **357个状态片段**，覆盖 **9个PLC状态**
- Sorting_Metal（5.043s）和 Return（5.799s）是耗时最长的两个状态
- 主要工艺流程：Idle→Homing→Pickup→Inspection→Sorting→Return→Idle

### 3.3 异常检测
- 异常样本共 **50条**（Label=1: 39条卡滞，Label=2: 11条脱扣），占比 **0.31%**
- **ActSpeed** 为最强故障敏感特征（Cohen's d = 5.899，对Label=2）
- **ActCurrent** 对Label=1（卡滞）区分力最强（Cohen's d = 2.871）
- 两种故障影响机制完全不同：卡滞影响电流/力控，脱扣影响速度/加速度

### 3.4 传感器关联
- IsForce-ActCurrent-ActSpeed 构成强耦合三角（r>0.7）
- PLC I/O 信号稳定性（>0.87）远高于模拟量信号（<0.01）
- 气压工况对信号相关性影响最大

### 3.5 运行效能
- 识别出 **43个完整分拣周期**，平均周期 **19.389秒**
- 异常发生率：**0.308%**，MTBF：**4.2分钟**
- 故障导致效率下降：**4.3%**

---

## 四、交付状态总览

| 检查维度 | 通过项 | 问题项 | 评分 |
|---------|:---:|:---:|:---:|
| 产物完整性 | 31/31 | 0 | 10/10 |
| 代码质量 | 5/5脚本可运行 | 0 | 10/10 |
| 文档一致性 | 5/5目录匹配 | 0 | 10/10 |
| 报告质量门控 | 5/5通过（含4章补救） | 0 | 10/10 |
| 数据分析质量 | 结论均有数据支撑 | 2个建议项 | 9/10 |
| **综合** | **12/12项通过** | **0严重/2中等** | **9.8/10** |

---

## 五、使用建议

1. **开题报告引用**: 可直接引用 ch01-ch04 的分析结论（数据质量、PLC状态机、异常特征、传感器关联）
2. **答辩PPT素材**: ch02/ch03/ch04 的PNG图表可直接用于演示
3. **后续扩展**: ch05 的数据集局限性分析为引入同类数据集提供了明确方向
4. **Notebook复现**: 5个 `.ipynb` 文件支持交互式复现全部分析过程

---

> **验收结论**: 本项目全部12项质量检查通过（含v2.2报告质量门控），4份空洞报告已补救重写，交付物完整、代码可运行、文档一致、结论有数据支撑，**已达到开题报告使用标准**。
