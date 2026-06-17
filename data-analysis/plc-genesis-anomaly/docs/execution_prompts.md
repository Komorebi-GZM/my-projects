# Genesis_Anomaly_Analysis 执行 Prompt 文档

> 版本：v2.0
> 生成日期：2026-06-02
> 基于：execution_prompts 技能模板
> 说明：本文档为纯指令文档，不含代码，供 AI Agent 或人工执行时参考

---

## 全局技能库引用

执行以下 Prompt 时，按需调用以下 Skill：

| Skill ID | 模块名 | 路径 | 核心函数 |
|----------|--------|------|----------|
| Skill-01 | 标准数据加载器 | `src/utils/data_loader.py` | `load_raw_data()`, `load_all_data()`, `split_by_label()`, `load_condition_data()` |
| Skill-02 | 标准可视化出图器 | `src/utils/visualizer.py` | `plot_time_series()`, `plot_distribution()`, `plot_boxplot()`, `plot_heatmap()`, `plot_comparison()`, `plot_state_timeline()` |
| Skill-03 | 标准评估指标计算器 | `src/utils/metrics.py` | `calc_descriptive_stats()`, `perform_ttest()`, `perform_ks_test()`, `calc_cohens_d()`, `extract_time_features()`, `calc_stability_score()`, `calc_correlation_matrix()` |
| Skill-04 | 标准输出产物管理器 | `src/utils/output_manager.py` | `save_dataframe()`, `save_figure()`, `save_markdown()`, `generate_report_md()` |
| Skill-05 | 任务依赖图管理器 | `src/utils/task_graph.py` | `TaskGraph()`, `check_dependencies()`, `update_status()` |

---

# Prompt-01: 数据概览与清洗

## 一、任务概述

### 1.1 本次任务是什么
对 Genesis 数据集的 5 个 CSV 文件进行基础探查，建立 9 路模拟量和 13 路离散量信号的基准统计特征，明确数据质量状况，为后续章节提供统一的数据加载接口和清洗后数据集。

### 1.2 从什么数据出发
- `data/原始数据1/Genesis_AnomalyLabels.csv`（16,220行，含Label 0/1/2，20列，Unix秒时间戳）
- `data/原始数据1/Genesis_StateMachineLabel.csv`（16,220行，含Label 0-8，20列，Unix秒时间戳）
- `data/原始数据1/Genesis_lineardrive.csv`（7,424行，无Label，24列，Unix毫秒时间戳）
- `data/原始数据1/Genesis_normal.csv`（7,040行，无Label，24列，Unix毫秒时间戳）
- `data/原始数据1/Genesis_pressure.csv`（8,476行，无Label，24列，Unix毫秒时间戳）

### 1.3 可以采用什么方法
- 数据读取与结构探查（pandas read_csv）
- 时间戳解析与标准化（pd.to_datetime，区分秒/毫秒格式）
- 缺失值检测与统计（isnull().sum() / isnull().mean()）
- 描述性统计（df.describe()，含均值、标准差、分位数）
- 分布可视化（直方图、箱线图、核密度估计）

---

## 二、执行步骤（六子结构）

### Step 1: 数据加载与结构探查
- **本步骤要做什么**：加载全部 5 个 CSV 文件，记录每个文件的基本信息（行数、列数、列名、时间范围），对比列名差异，建立统一列名映射。
- **本步骤输出产物**：`dataset_info_table.csv`，路径 `outputs/ch01_data_overview_and_cleaning/`，包含 file/rows/columns/time_range 字段。
- **具体操作指引**：
  1. 调用 Skill-01 的 `load_all_data(parse_timestamp=True)` 加载全部数据
  2. 注意区分两种时间戳格式：前两个文件为 Unix 秒，后三个文件为 Unix 毫秒
  3. 对比 5 个文件的列名差异，记录哪些列是共有的、哪些是独有的
  4. 统计每个文件的行数、列数、时间范围
- **本步骤完成后的检查标准**：
  1. 5 个文件全部成功加载，无编码错误
  2. dataset_info_table.csv 已生成，包含 5 行记录
  3. 时间戳已统一转换为 datetime 格式

### Step 2: 缺失值统计
- **本步骤要做什么**：按文件、按列统计缺失值数量和比例，评估数据完整性。
- **本步骤输出产物**：`missing_value_stats.csv`，路径 `outputs/ch01_data_overview_and_cleaning/`，包含 file/total_cells/missing_cells/missing_rate 字段。
- **具体操作指引**：
  1. 对每个 DataFrame 执行 `isnull().sum()` 统计每列缺失值
  2. 计算缺失率 = 缺失单元格数 / 总单元格数
  3. 识别缺失值最严重的列（如有）
- **本步骤完成后的检查标准**：
  1. missing_value_stats.csv 已生成
  2. 所有文件的缺失率计算准确

### Step 3: 描述性统计
- **本步骤要做什么**：对每路模拟量信号计算均值、标准差、最小值、25%/50%/75%分位数、最大值、偏度、峰度，建立正常工况下的信号基准。
- **本步骤输出产物**：`signal_baseline_stats.csv`，路径 `outputs/ch01_data_overview_and_cleaning/`，包含 file/signal/mean/std/min/25%/50%/75%/max/skewness/kurtosis 字段。
- **具体操作指引**：
  1. 调用 Skill-01 的 `get_signal_columns('analog')` 获取模拟量列名
  2. 对每个文件中的每路模拟量信号调用 Skill-03 的 `calc_descriptive_stats()`
  3. 按文件和信号分组汇总
  4. 特别关注 AnomalyLabels 中 Label=0（正常）组的统计特征，作为后续对比基准
- **本步骤完成后的检查标准**：
  1. signal_baseline_stats.csv 已生成
  2. 覆盖所有 9 路模拟量信号
  3. 统计量计算无 NaN（除空列外）

### Step 4: 分布可视化
- **本步骤要做什么**：绘制 9 路模拟量信号的分布直方图和箱线图，直观展示信号分布特征和异常值。
- **本步骤输出产物**：
  - `signal_distribution_ch01.png`，路径 `outputs/ch01_data_overview_and_cleaning/figures/`
  - `signal_boxplot_ch01.png`，路径 `outputs/ch01_data_overview_and_cleaning/figures/`
- **具体操作指引**：
  1. 调用 Skill-02 的 `plot_distribution()` 为每路信号绘制直方图
  2. 调用 Skill-02 的 `plot_boxplot()` 为每路信号绘制箱线图
  3. 图表标题清晰标注信号名称和数据来源
  4. 使用合适的分箱数（bins=50）和透明度
- **本步骤完成后的检查标准**：
  1. 至少生成 2 张 PNG 图表
  2. 图表清晰可读，覆盖主要信号
  3. 图例和坐标轴标签完整

### Step 5: 数据质量报告
- **本步骤要做什么**：汇总数据规模、缺失情况、时间范围、信号范围，生成数据质量评估报告。
- **本步骤输出产物**：`data_quality_report.md`，路径 `outputs/ch01_data_overview_and_cleaning/`，Markdown 格式。
- **具体操作指引**：
  1. 汇总前 4 个步骤的关键发现
  2. 评估数据整体质量（完整性、一致性、时效性）
  3. 指出需要注意的数据问题（如时间戳格式不一致、列名差异等）
  4. 为后续章节提出数据使用建议
- **本步骤完成后的检查标准**：
  1. data_quality_report.md 已生成
  2. 报告包含数据概况、缺失分析、质量评估、使用建议四部分

### Step 6: 生成章节报告
- **本步骤要做什么**：按四段框架（背景→分析方法→分析发现→小结）撰写 chapter 执行报告。
- **本步骤输出产物**：`report.md`，路径 `outputs/ch01_data_overview_and_cleaning/`，Markdown 格式。
- **具体操作指引**：
  1. 调用 Skill-04 的 `generate_report_md()` 生成报告框架
  2. 背景段：说明数据来源、规模、本章目标
  3. 分析方法段：列出使用的统计方法和可视化方法
  4. 分析发现段：汇总关键数据（总行数、信号范围、缺失率等）
  5. 小结段：结论和数据质量总体评价
- **本步骤完成后的检查标准**：
  1. report.md 已生成
  2. 包含完整的四段框架
  3. 引用本章生成的所有产物文件

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 数据集基本信息表 | `dataset_info_table.csv` | `outputs/ch01_data_overview_and_cleaning/` | ch02-ch05 参考 |
| 信号基准特征统计表 | `signal_baseline_stats.csv` | `outputs/ch01_data_overview_and_cleaning/` | ch03 异常对比基准 |
| 缺失值统计表 | `missing_value_stats.csv` | `outputs/ch01_data_overview_and_cleaning/` | 参考 |
| 信号分布直方图 | `signal_distribution_ch01.png` | `outputs/ch01_data_overview_and_cleaning/figures/` | 开题 PPT |
| 信号箱线图 | `signal_boxplot_ch01.png` | `outputs/ch01_data_overview_and_cleaning/figures/` | 开题 PPT |
| 数据质量报告 | `data_quality_report.md` | `outputs/ch01_data_overview_and_cleaning/` | 参考 |
| 章节执行报告 | `report.md` | `outputs/ch01_data_overview_and_cleaning/` | 最终交付 |

### 3.2 关键产物结构详解

**signal_baseline_stats.csv** 是本章节最核心的产物，为后续所有章节的对比分析提供基准。每行代表一个文件中的一路信号，包含完整的描述性统计量。

### 3.3 章节执行报告（report.md）

执行完毕后自动生成 `outputs/ch01_data_overview_and_cleaning/report.md`，遵循四段框架。

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 仅对模拟量信号进行了详细统计，离散量信号的分析较浅
- 时间序列的周期性、趋势性分析未涉及
- 异常值检测仅通过箱线图目视识别，未使用统计方法

### 4.2 可进一步优化的方向
- 增加离散量信号的分布统计（取值频率、状态持续时间）
- 增加时间序列分解（趋势、周期、残差）
- 增加基于 3-sigma 或 IQR 的异常值自动检测

### 4.3 其他可选方法
- 使用 pandas-profiling 生成自动化数据探查报告
- 使用 sweetviz 进行交互式数据对比

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- [ ] 时间戳解析是否正确？（秒 vs 毫秒）
- [ ] 列名映射是否需要调整？
- [ ] 是否有额外的数据文件需要纳入分析？

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| 文件编码错误 | 尝试 `encoding='utf-8'`、`'gbk'`、`'latin1'` |
| 时间戳解析失败 | 检查时间戳格式（秒/毫秒/微秒），调整 `unit` 参数 |
| 列名不一致 | 建立列名映射字典，统一列名 |
| 缺失值过多 | 记录缺失率，评估是否影响后续分析 |

---
---

# Prompt-02: PLC 状态机与工序分析

## 一、任务概述

### 1.1 本次任务是什么
基于 StateMachineLabel 数据集中的 9 种 PLC 状态标签（0-8），拆解分拣全流程，量化各状态持续时间、状态转移概率、工序协同逻辑，绘制 PLC 状态转移图和分拣全流程信号时序图。

### 1.2 从什么数据出发
- `data/原始数据1/Genesis_StateMachineLabel.csv`（16,220行，含Label 0-8，20列）
- ch01 输出（时间戳已标准化的数据，作为参考）

### 1.3 可以采用什么方法
- 状态边界识别（diff() 定位状态切换点）
- 状态持续时间统计（groupby + agg）
- 状态转移矩阵（pd.crosstab + normalize）
- 工序时序可视化（带状态背景色的时序图）
- 信号联动分析（同一状态下多信号相关性）

---

## 二、执行步骤（六子结构）

### Step 1: 数据加载与验证
- **本步骤要做什么**：加载 StateMachineLabel 数据，验证时间戳和标签完整性，确认 9 种状态标签的分布。
- **本步骤输出产物**：无独立产物，为后续步骤准备数据。
- **具体操作指引**：
  1. 调用 Skill-01 的 `load_state_machine_data()` 加载数据
  2. 确认 Label 列包含 0-8 的所有状态值
  3. 统计每种状态的样本数
  4. 验证时间戳是否连续、无跳变
- **本步骤完成后的检查标准**：
  1. 数据加载成功，无错误
  2. Label 列包含 0-8 的所有值
  3. 时间戳连续无跳变

### Step 2: 状态边界识别
- **本步骤要做什么**：使用 diff() 定位状态切换点，将连续时间序列分割为离散的状态片段。
- **本步骤输出产物**：状态片段列表（内存中），用于后续统计。
- **具体操作指引**：
  1. 对 Label 列执行 `diff().ne(0)` 识别状态变化点
  2. 记录每个状态片段的起始时间、结束时间、状态值
  3. 验证状态片段总数是否合理（约等于状态切换次数）
- **本步骤完成后的检查标准**：
  1. 状态切换点识别准确，无遗漏或重复
  2. 每个状态片段都有明确的起始和结束时间

### Step 3: 状态持续时间统计
- **本步骤要做什么**：计算每个状态片段的持续时间，按状态分组统计平均持续时间、标准差、最小值、最大值。
- **本步骤输出产物**：`state_duration_stats.csv`，路径 `outputs/ch02_plc_state_machine_analysis/`，包含 state/count/mean/std/min/max 字段。
- **具体操作指引**：
  1. 对每个状态片段计算持续时间 = 结束时间 - 起始时间
  2. 按状态值分组，计算 count/mean/std/min/max
  3. 识别持续时间异常的状态片段（如过长或过短）
  4. 将状态编号映射为状态名称（0=Idle, 1=Homing, ...）
- **本步骤完成后的检查标准**：
  1. state_duration_stats.csv 已生成
  2. 覆盖全部 9 种状态
  3. 统计量计算合理（无负数、无极端异常值）

### Step 4: 状态转移矩阵
- **本步骤要做什么**：构建 9×9 状态转移概率矩阵，识别主要转移路径和异常转移。
- **本步骤输出产物**：`state_transition_matrix.csv`，路径 `outputs/ch02_plc_state_machine_analysis/`，9×9 矩阵，行和为 1。
- **具体操作指引**：
  1. 使用 `pd.crosstab(df['Label'], df['Label'].shift(-1), normalize='index')` 构建转移矩阵
  2. 识别概率最高的转移路径（如 Idle→Homing→Pickup→...）
  3. 识别低概率或异常的转移（如直接 Idle→Error）
  4. 验证矩阵每行概率之和为 1
- **本步骤完成后的检查标准**：
  1. state_transition_matrix.csv 已生成
  2. 矩阵为 9×9，每行概率之和为 1
  3. 主要转移路径符合预期工艺流程

### Step 5: 工序时序可视化
- **本步骤要做什么**：绘制 2-3 路关键信号（ActCurrent, ActPosition, ActSpeed）的时序图，按状态分段着色，直观展示分拣全流程。
- **本步骤输出产物**：
  - `plc_state_transition.png`，路径 `outputs/ch02_plc_state_machine_analysis/figures/`
  - `sorting_process_timeseries.png`，路径 `outputs/ch02_plc_state_machine_analysis/figures/`
- **具体操作指引**：
  1. 调用 Skill-02 的 `plot_state_timeline()` 绘制带状态背景色的时序图
  2. 选择代表性时间段（完整分拣周期）进行局部放大展示
  3. 使用不同颜色标注不同状态段
  4. 添加图例说明状态颜色对应关系
  5. 分析 PLC 控制信号（Gripper, MaterialIsMetal）与传感器信号的联动时序
- **本步骤完成后的检查标准**：
  1. 至少生成 2 张 PNG 图表
  2. 时序图清晰展示至少 2-3 路关键信号
  3. 状态分段着色明显，图例完整

### Step 6: 生成章节报告
- **本步骤要做什么**：按四段框架撰写 chapter 执行报告，总结 PLC 状态机运行规律。
- **本步骤输出产物**：`report.md`，路径 `outputs/ch02_plc_state_machine_analysis/`。
- **具体操作指引**：
  1. 背景段：说明 StateMachineLabel 数据来源和状态定义
  2. 分析方法段：列出状态识别、持续时间统计、转移矩阵方法
  3. 分析发现段：汇总各状态持续时间、主要转移路径、信号联动规律
  4. 小结段：结论（PLC 控制流程合理性验证）
- **本步骤完成后的检查标准**：
  1. report.md 已生成
  2. 包含完整的四段框架
  3. 引用 state_duration_stats.csv 和 state_transition_matrix.csv

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 状态持续时间统计表 | `state_duration_stats.csv` | `outputs/ch02_plc_state_machine_analysis/` | ch05 效能评估 |
| 状态转移矩阵 | `state_transition_matrix.csv` | `outputs/ch02_plc_state_machine_analysis/` | ch05 效能评估 |
| PLC 状态转移图 | `plc_state_transition.png` | `outputs/ch02_plc_state_machine_analysis/figures/` | 论文核心图、开题 PPT |
| 分拣全流程信号时序图 | `sorting_process_timeseries.png` | `outputs/ch02_plc_state_machine_analysis/figures/` | 论文核心图、开题 PPT |
| 章节执行报告 | `report.md` | `outputs/ch02_plc_state_machine_analysis/` | 最终交付 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 状态转移矩阵仅基于频率统计，未考虑时间因素
- 未对状态序列进行模式挖掘（如频繁子序列）
- 信号联动分析较浅，未量化联动延迟

### 4.2 可进一步优化的方向
- 增加时间加权的状态转移矩阵
- 使用序列模式挖掘算法（PrefixSpan）发现频繁状态序列
- 计算控制信号与传感器信号的互相关，量化联动延迟

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- [ ] 状态编号与工序的对应关系是否正确？
- [ ] 是否有未识别的异常状态片段？
- [ ] 时序图展示的时间段是否合适？

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| 状态切换过于频繁 | 检查是否为噪声，考虑平滑处理 |
| 某状态持续时间异常长 | 标记为异常片段，单独分析 |
| 转移矩阵出现未预期的转移 | 核实是否为真实工艺或数据错误 |

---
---

# Prompt-03: 异常检测与抗干扰分析

## 一、任务概述

### 1.1 本次任务是什么
对比正常（Label=0）与异常（Label=1 直线驱动卡滞、Label=2 驱动脱扣校正）工况下传感器信号的差异，量化故障信号的畸变特征，探索性提取故障敏感特征，为故障预警提供特征工程基础。

### 1.2 从什么数据出发
- `data/原始数据1/Genesis_AnomalyLabels.csv`（16,220行，Label 0/1/2）
- ch01 输出（信号基准统计表，作为正常工况基准）
- ch02 输出（状态片段信息，用于定位故障时段）

### 1.3 可以采用什么方法
- 正常 vs 异常描述性统计对比
- 独立样本 t 检验（均值差异显著性）
- Kolmogorov-Smirnov 检验（分布差异显著性）
- Cohen's d 效应量（差异大小评估）
- 时域特征提取（均值、方差、峰度、偏度、峰峰值、均方根）
- 特征区分力评估（箱线图对比、p-value 排序）

---

## 二、执行步骤（六子结构）

### Step 1: 数据加载与分组
- **本步骤要做什么**：加载 AnomalyLabels 数据，按 Label=0/1/2 分为三组，确认各组样本数。
- **本步骤输出产物**：无独立产物，三组 DataFrame（内存中）。
- **具体操作指引**：
  1. 调用 Skill-01 的 `load_anomaly_data()` 加载数据
  2. 调用 Skill-01 的 `split_by_label()` 按 Label 分组
  3. 确认三组样本数：Label=0（约16,170）、Label=1（39）、Label=2（11）
  4. 记录异常样本占比（约 0.3%）
- **本步骤完成后的检查标准**：
  1. 三组数据正确分离
  2. 样本数与预期一致

### Step 2: 描述性统计对比
- **本步骤要做什么**：对关键信号（ActCurrent, ActPosition, ActSpeed）计算三组的均值、标准差、范围，建立对比表。
- **本步骤输出产物**：`normal_vs_anomaly_stats.csv`，路径 `outputs/ch03_anomaly_detection_analysis/`，包含 signal/label/mean/std/count 字段。
- **具体操作指引**：
  1. 选择 3 路关键信号进行对比
  2. 对每组每路信号计算均值、标准差、最小值、最大值
  3. 计算正常组与异常组的相对差异百分比
  4. 识别差异最显著的信号
- **本步骤完成后的检查标准**：
  1. normal_vs_anomaly_stats.csv 已生成
  2. 覆盖 3 路关键信号 × 3 组 = 9 行记录

### Step 3: 统计检验
- **本步骤要做什么**：对每路关键信号执行 t 检验和 KS 检验，评估正常与异常组之间的统计显著性。
- **本步骤输出产物**：`statistical_test_results.csv`，路径 `outputs/ch03_anomaly_detection_analysis/`，包含 signal/anomaly_label/t_pvalue/t_significant/ks_pvalue/ks_significant/cohens_d 字段。
- **具体操作指引**：
  1. 调用 Skill-03 的 `perform_ttest()` 对正常组 vs Label=1 和正常组 vs Label=2 分别检验
  2. 调用 Skill-03 的 `perform_ks_test()` 执行分布差异检验
  3. 调用 Skill-03 的 `calc_cohens_d()` 计算效应量
  4. 显著性水平设为 0.05
  5. 注意异常样本极少（39 和 11），检验结果需谨慎解读
- **本步骤完成后的检查标准**：
  1. statistical_test_results.csv 已生成
  2. t 检验和 KS 检验的 p-value 计算正确
  3. 显著性判断基于 p-value < 0.05

### Step 4: 波形对比可视化
- **本步骤要做什么**：绘制正常 vs 异常信号的时序叠加对比图，直观展示故障信号畸变。
- **本步骤输出产物**：`signal_comparison_normal_anomaly.png`，路径 `outputs/ch03_anomaly_detection_analysis/figures/`。
- **具体操作指引**：
  1. 调用 Skill-02 的 `plot_comparison()` 绘制波形叠加图
  2. 对每路关键信号分别绘制正常组、Label=1 组、Label=2 组的波形
  3. 使用不同颜色和透明度区分
  4. 标注异常发生时段
  5. 分析波形畸变特征（幅值突变、波动增大、相位偏移等）
- **本步骤完成后的检查标准**：
  1. 至少生成 1 张对比图
  2. 图表清晰展示正常与异常信号的波形差异

### Step 5: 特征提取与区分力评估
- **本步骤要做什么**：提取时域统计特征，评估各特征对异常识别的区分力，识别最敏感的故障特征。
- **本步骤输出产物**：
  - `distortion_features_table.csv`，路径 `outputs/ch03_anomaly_detection_analysis/`，包含 signal/label/mean/std/max/min/peak_to_peak/rms/skewness/kurtosis 字段
  - `feature_importance_ranking.csv`，路径 `outputs/ch03_anomaly_detection_analysis/`，特征按区分力排序
- **具体操作指引**：
  1. 调用 Skill-03 的 `extract_time_features()` 为每组每路信号提取时域特征
  2. 绘制特征箱线图，对比三组特征的分布差异
  3. 计算各特征的统计显著性（p-value）
  4. 按 p-value 排序，识别区分力最强的特征
  5. 注意：本步骤为探索性特征分析，不构建复杂分类模型
- **本步骤完成后的检查标准**：
  1. distortion_features_table.csv 已生成
  2. feature_importance_ranking.csv 已生成
  3. 至少识别 3 个显著区分正常与异常的特征

### Step 6: 生成章节报告
- **本步骤要做什么**：按四段框架撰写 chapter 执行报告，总结故障信号畸变规律和关键特征。
- **本步骤输出产物**：`report.md`，路径 `outputs/ch03_anomaly_detection_analysis/`。
- **具体操作指引**：
  1. 背景段：说明异常标签定义（Label=1 卡滞、Label=2 脱扣）
  2. 分析方法段：列出统计检验方法和特征提取方法
  3. 分析发现段：汇总信号畸变特征、统计检验结果、关键特征排序
  4. 小结段：结论（故障对信号的影响规律）
- **本步骤完成后的检查标准**：
  1. report.md 已生成
  2. 引用 normal_vs_anomaly_stats.csv、statistical_test_results.csv、feature_importance_ranking.csv

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 正常 vs 异常统计对比表 | `normal_vs_anomaly_stats.csv` | `outputs/ch03_anomaly_detection_analysis/` | ch03 report.md |
| 统计检验结果表 | `statistical_test_results.csv` | `outputs/ch03_anomaly_detection_analysis/` | ch03 report.md |
| 正常/异常信号对比图 | `signal_comparison_normal_anomaly.png` | `outputs/ch03_anomaly_detection_analysis/figures/` | 论文核心图、开题 PPT |
| 畸变特征量化表 | `distortion_features_table.csv` | `outputs/ch03_anomaly_detection_analysis/` | ch03 report.md、开题报告 |
| 特征重要性排序 | `feature_importance_ranking.csv` | `outputs/ch03_anomaly_detection_analysis/` | 论文附录 |
| 章节执行报告 | `report.md` | `outputs/ch03_anomaly_detection_analysis/` | 最终交付 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 异常样本极少（50 条），统计检验功效有限
- 仅提取时域特征，未涉及频域/时频域特征
- 未构建分类模型，仅做探索性特征分析

### 4.2 可进一步优化的方向
- 使用 SMOTE 等过采样方法扩充异常样本
- 提取频域特征（FFT、功率谱密度）
- 构建简单可解释的分类模型（决策树、逻辑回归）

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- [ ] 异常样本数量极少，统计结论是否足够支撑开题？
- [ ] 是否需要补充其他异常类型数据？
- [ ] 特征分析结果是否符合工程直觉？

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| t 检验 p-value 不显著 | 考虑样本量过小，改用效应量评估 |
| 异常信号与正常信号差异不明显 | 检查是否选择了正确的对比信号 |
| 特征区分力排序与预期不符 | 核实特征计算是否正确 |

---
---

# Prompt-04: 传感器性能关联分析

## 一、任务概述

### 1.1 本次任务是什么
探究多路传感器信号（气压、位移、电流、速度等）之间的耦合关系，对比 normal/lineardrive/pressure 三种工况下的相关性差异，评估传感器在连续运行与工况波动下的可靠性。

### 1.2 从什么数据出发
- `data/原始数据1/Genesis_lineardrive.csv`（7,424行，直线驱动工况）
- `data/原始数据1/Genesis_normal.csv`（7,040行，正常工况）
- `data/原始数据1/Genesis_pressure.csv`（8,476行，气压工况）
- ch01 输出（清洗后数据）

### 1.3 可以采用什么方法
- Pearson 相关系数（线性关系）
- Spearman 相关系数（单调关系）
- 相关性热力图可视化
- 工况对比分析（三种工况的相关性差异）
- 滑动窗口标准差（信号稳定性评估）
- 变异系数（CV = 标准差/均值）

---

## 二、执行步骤（六子结构）

### Step 1: 数据加载与对齐
- **本步骤要做什么**：加载三种工况数据，获取共同列，筛选模拟量信号列。
- **本步骤输出产物**：无独立产物，三种工况的 DataFrame（内存中）。
- **具体操作指引**：
  1. 调用 Skill-01 的 `load_condition_data()` 分别加载 lineardrive、normal、pressure
  2. 调用 Skill-01 的 `get_common_columns()` 获取三个文件的共同列
  3. 筛选模拟量信号列（排除 Set* 设定值和离散量）
  4. 确认三种工况的数据行数和时间范围
- **本步骤完成后的检查标准**：
  1. 三种工况数据全部加载成功
  2. 共同列识别准确

### Step 2: 相关性计算
- **本步骤要做什么**：分别计算三种工况的 Pearson 和 Spearman 相关系数矩阵。
- **本步骤输出产物**：
  - `correlation_matrix_normal.csv`
  - `correlation_matrix_lineardrive.csv`
  - `correlation_matrix_pressure.csv`
  路径均为 `outputs/ch04_sensor_performance_analysis/`。
- **具体操作指引**：
  1. 对每种工况的模拟量信号列调用 Skill-03 的 `calc_correlation_matrix(method='pearson')`
  2. 同样计算 Spearman 相关系数矩阵
  3. 检查矩阵对称性，对角线应为 1
  4. 识别相关系数绝对值最高的信号对
- **本步骤完成后的检查标准**：
  1. 三个 CSV 文件已生成
  2. 矩阵为方阵，对角线为 1
  3. 无 NaN（除完全空列外）

### Step 3: 相关性热力图
- **本步骤要做什么**：绘制三种工况的相关性热力图，直观展示信号间的耦合关系。
- **本步骤输出产物**：`sensor_correlation_heatmap.png`，路径 `outputs/ch04_sensor_performance_analysis/figures/`。
- **具体操作指引**：
  1. 调用 Skill-02 的 `plot_heatmap()` 绘制三种工况的热力图
  2. 使用 RdBu_r 颜色映射，中心为 0
  3. 标注相关系数数值（保留两位小数）
  4. 将三张热力图拼接为一张对比图
- **本步骤完成后的检查标准**：
  1. 热力图已生成
  2. 颜色映射正确，数值标注清晰

### Step 4: 工况差异分析
- **本步骤要做什么**：对比三种工况下的相关性矩阵，识别相关性显著变化的信号对。
- **本步骤输出产物**：`correlation_diff_by_condition.csv`，路径 `outputs/ch04_sensor_performance_analysis/`，包含 signal_pair/condition/correlation 字段。
- **具体操作指引**：
  1. 计算三种工况相关性矩阵的差值
  2. 识别相关性变化最大的信号对（差值 > 0.3）
  3. 分析变化原因（如某工况下某传感器失效或异常）
  4. 记录分析结论
- **本步骤完成后的检查标准**：
  1. correlation_diff_by_condition.csv 已生成
  2. 至少识别 3 对显著变化的信号

### Step 5: 信号稳定性评估
- **本步骤要做什么**：计算滑动窗口内的标准差和变异系数，评估各信号在不同工况下的稳定性。
- **本步骤输出产物**：`signal_stability_scores.csv`，路径 `outputs/ch04_sensor_performance_analysis/`，包含 condition/signal/mean_std/max_std/mean_cv/stability_score 字段。
- **具体操作指引**：
  1. 调用 Skill-03 的 `calc_stability_score()` 计算滑动窗口标准差
  2. 窗口大小设为 100（约 5 秒）
  3. 计算变异系数 CV = 标准差 / 均值
  4. 按稳定性评分排序，识别最稳定和最不稳定的信号
  5. 分析电流-速度、力控-位置的联动关系
- **本步骤完成后的检查标准**：
  1. signal_stability_scores.csv 已生成
  2. 覆盖所有模拟量信号
  3. 稳定性评分合理（越高越稳定）

### Step 6: 生成章节报告
- **本步骤要做什么**：按四段框架撰写 chapter 执行报告，总结传感器耦合关系和稳定性评估结果。
- **本步骤输出产物**：`report.md`，路径 `outputs/ch04_sensor_performance_analysis/`。
- **具体操作指引**：
  1. 背景段：说明三种工况的定义和分析目标
  2. 分析方法段：列出相关性分析和稳定性评估方法
  3. 分析发现段：汇总关键信号对的相关性、工况差异、稳定性排序
  4. 小结段：结论（传感器可靠性评估）
- **本步骤完成后的检查标准**：
  1. report.md 已生成
  2. 引用相关性矩阵和稳定性评分表

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 相关性矩阵（normal） | `correlation_matrix_normal.csv` | `outputs/ch04_sensor_performance_analysis/` | ch04 report.md |
| 相关性矩阵（lineardrive） | `correlation_matrix_lineardrive.csv` | `outputs/ch04_sensor_performance_analysis/` | ch04 report.md |
| 相关性矩阵（pressure） | `correlation_matrix_pressure.csv` | `outputs/ch04_sensor_performance_analysis/` | ch04 report.md |
| 传感器相关性热力图 | `sensor_correlation_heatmap.png` | `outputs/ch04_sensor_performance_analysis/figures/` | 论文核心图、开题 PPT |
| 工况对比相关性差异表 | `correlation_diff_by_condition.csv` | `outputs/ch04_sensor_performance_analysis/` | ch04 report.md |
| 信号稳定性评分表 | `signal_stability_scores.csv` | `outputs/ch04_sensor_performance_analysis/` | 开题报告 |
| 章节执行报告 | `report.md` | `outputs/ch04_sensor_performance_analysis/` | 最终交付 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 仅分析了线性相关性，未考虑非线性关系
- 滑动窗口大小固定，未针对不同信号自适应调整
- 未进行时序上的动态相关性分析

### 4.2 可进一步优化的方向
- 增加互信息（Mutual Information）分析非线性关系
- 使用变分模态分解（VMD）分析信号间的时频耦合
- 构建动态相关性网络，分析相关性随时间的变化

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- [ ] 三种工况的定义是否与预期一致？
- [ ] 相关性变化最大的信号对是否符合工程直觉？
- [ ] 稳定性评分结果是否合理？

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| 某信号在某种工况下全为常数 | 排除该信号，记录为传感器失效 |
| 相关性矩阵出现 NaN | 检查是否有零方差信号 |
| 三种工况相关性差异极小 | 可能工况划分不明显，需重新评估 |

---
---

# Prompt-05: 运行效能评估

## 一、任务概述

### 1.1 本次任务是什么
汇总前序章节分析结果，计算正常与故障场景下的分拣效率（周期时间、单位时间分拣件数）、稳定运行时长与异常发生率，分析数据集局限性，为课题性能指标提供工业数据基准。

### 1.2 从什么数据出发
- ch02 输出（`state_duration_stats.csv`、`state_transition_matrix.csv`）
- ch03 输出（异常统计结果、`normal_vs_anomaly_stats.csv`）
- ch04 输出（`signal_stability_scores.csv`）
- `data/原始数据1/Genesis_AnomalyLabels.csv`（原始异常标签数据）
- `data/原始数据1/Genesis_StateMachineLabel.csv`（原始状态标签数据）

### 1.3 可以采用什么方法
- 分拣周期识别（基于状态转移：Idle → ... → Idle）
- 周期时间统计（均值、标准差、范围）
- 效率指标计算（单位时间分拣件数、理论 vs 实际效率）
- 稳定性评估（连续无故障运行时长、异常发生率）
- 正常 vs 故障对比（效率下降幅度量化）
- 局限性分析（数据覆盖范围、样本不平衡、时间范围）

---

## 二、执行步骤（六子结构）

### Step 1: 数据整合
- **本步骤要做什么**：加载前序章节的全部产物数据，整合为效能评估所需的统一数据集。
- **本步骤输出产物**：无独立产物，整合后的数据（内存中）。
- **具体操作指引**：
  1. 加载 ch02 的 state_duration_stats.csv 和 state_transition_matrix.csv
  2. 加载 ch03 的 normal_vs_anomaly_stats.csv 和 statistical_test_results.csv
  3. 加载 ch04 的 signal_stability_scores.csv
  4. 加载原始 AnomalyLabels 和 StateMachineLabel 数据
  5. 确认所有数据的时间范围一致
- **本步骤完成后的检查标准**：
  1. 所有前序产物成功加载
  2. 数据时间范围一致

### Step 2: 分拣周期识别
- **本步骤要做什么**：基于状态转移识别完整的分拣周期（从 Idle 出发回到 Idle），计算每个周期的耗时。
- **本步骤输出产物**：`sorting_cycle_stats.csv`，路径 `outputs/ch05_performance_evaluation/`，包含 cycle_index/cycle_duration/start_time/end_time 字段。
- **具体操作指引**：
  1. 基于 StateMachineLabel 的 Label 列识别 Idle 状态（Label=0）
  2. 从一个 Idle 状态到下一个 Idle 状态为一个完整周期
  3. 计算每个周期的持续时间
  4. 过滤异常短的周期（< 1秒，可能为噪声）
  5. 统计周期总数、平均周期时间、标准差
- **本步骤完成后的检查标准**：
  1. sorting_cycle_stats.csv 已生成
  2. 周期数合理（与数据总时长匹配）
  3. 周期时间分布合理（无负数、无极端异常值）

### Step 3: 效率计算
- **本步骤要做什么**：计算单位时间分拣件数、理论最大效率与实际效率，对比正常与故障工况。
- **本步骤输出产物**：`efficiency_comparison_table.csv`，路径 `outputs/ch05_performance_evaluation/`，包含 metric/normal_value/anomaly_value/difference 字段。
- **具体操作指引**：
  1. 计算总周期数 / 总时长 = 单位时间分拣件数
  2. 计算理论最大效率（基于最短周期时间）
  3. 计算实际效率（基于平均周期时间）
  4. 分别计算正常工况（Label=0 时段）和故障工况（Label≠0 时段）的效率
  5. 量化故障导致的效率下降幅度
- **本步骤完成后的检查标准**：
  1. efficiency_comparison_table.csv 已生成
  2. 效率计算合理（单位时间件数 > 0）
  3. 正常工况效率高于故障工况

### Step 4: 稳定性统计
- **本步骤要做什么**：统计连续无故障运行时长分布、异常发生率、平均故障间隔时间。
- **本步骤输出产物**：`system_stability_assessment.csv`，路径 `outputs/ch05_performance_evaluation/`，包含 metric/value 字段。
- **具体操作指引**：
  1. 基于 AnomalyLabels 的 Label 列统计异常发生率
  2. 计算连续正常运行的最长时长、平均时长
  3. 估算平均故障间隔时间（MTBF）
  4. 统计异常持续时间分布
- **本步骤完成后的检查标准**：
  1. system_stability_assessment.csv 已生成
  2. 异常发生率与 ch03 统计一致

### Step 5: 数据集局限性分析
- **本步骤要做什么**：系统分析 Genesis 数据集的覆盖边界和局限性，为后续补充数据集提供方向。
- **本步骤输出产物**：`dataset_limitations.md`，路径 `outputs/ch05_performance_evaluation/`，Markdown 格式。
- **具体操作指引**：
  1. 数据覆盖范围：信号类型（仅电机+PLC I/O，缺视觉/温度）、物料种类（单一）、故障场景（仅2种）
  2. 样本不平衡：异常样本仅占 0.3%，统计代表性有限
  3. 时间范围：单一时间段数据，缺季节性/长期趋势
  4. 提出后续补充数据集建议（同类数据集、更多故障类型、多时间段数据）
- **本步骤完成后的检查标准**：
  1. dataset_limitations.md 已生成
  2. 局限性分析覆盖数据、方法、范围三个维度
  3. 后续建议具体可操作

### Step 6: 生成章节报告
- **本步骤要做什么**：按四段框架撰写 chapter 执行报告，汇总系统效能评估结果。
- **本步骤输出产物**：`report.md`，路径 `outputs/ch05_performance_evaluation/`。
- **具体操作指引**：
  1. 背景段：说明本章为汇总章节，整合前序分析结果
  2. 分析方法段：列出周期识别、效率计算、稳定性评估方法
  3. 分析发现段：汇总分拣效率、稳定性指标、正常 vs 故障对比
  4. 小结段：结论（系统效能总体评估）+ 数据集局限性 + 后续建议
- **本步骤完成后的检查标准**：
  1. report.md 已生成
  2. 引用 efficiency_comparison_table.csv、system_stability_assessment.csv
  3. 包含完整的四段框架

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 分拣周期统计表 | `sorting_cycle_stats.csv` | `outputs/ch05_performance_evaluation/` | ch05 report.md |
| 效率对比表 | `efficiency_comparison_table.csv` | `outputs/ch05_performance_evaluation/` | 开题报告 |
| 系统稳定性评估 | `system_stability_assessment.csv` | `outputs/ch05_performance_evaluation/` | ch05 report.md |
| 数据集局限性清单 | `dataset_limitations.md` | `outputs/ch05_performance_evaluation/` | 开题报告 |
| 章节执行报告 | `report.md` | `outputs/ch05_performance_evaluation/` | 最终交付 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 周期识别基于简单规则（Idle→Idle），可能遗漏复杂周期结构
- 效率计算未考虑物料类型、批次大小等因素
- 稳定性评估基于单一数据源，缺乏横向对比

### 4.2 可进一步优化的方向
- 使用隐马尔可夫模型（HMM）识别更复杂的周期结构
- 引入物料类型、批次大小等协变量进行效率回归分析
- 收集多组同类数据集进行横向对比

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- [ ] 分拣周期识别规则是否合理？
- [ ] 效率指标是否符合开题中的性能目标？
- [ ] 数据集局限性分析是否全面？

### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| 周期识别结果异常（周期数过少/过多） | 调整周期识别规则，检查 Idle 状态定义 |
| 效率计算结果与预期差距大 | 检查时间单位（秒/分钟/小时）是否统一 |
| 稳定性指标与 ch03 不一致 | 核实数据来源和统计口径 |

---

## 附录：执行顺序总览

```
Prompt-01 (ch01) → Prompt-02 (ch02) ∥ Prompt-04 (ch04) → Prompt-03 (ch03) → Prompt-05 (ch05)
```

| Prompt | 章节 | 预计耗时 | 完成时限 | 前置依赖 |
|--------|------|---------|---------|---------|
| Prompt-01 | ch01 数据概览 | 1-2 小时 | 第 12 周 | 无 |
| Prompt-02 | ch02 状态机分析 | 2-3 小时 | 第 12 周 | Prompt-01 |
| Prompt-03 | ch03 异常检测 | 3-4 小时 | 第 12 周 | Prompt-02 |
| Prompt-04 | ch04 传感器性能 | 2-3 小时 | 第 12 周 | Prompt-01 |
| Prompt-05 | ch05 效能评估 | 2-3 小时 | 第 16 周 | Prompt-03 + Prompt-04 |
