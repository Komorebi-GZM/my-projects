# Genesis_Anomaly_Analysis 研究设计文档

> 版本：v2.0
> 生成日期：2026-06-02
> 基于：flow_design 技能模板

---

## 文档说明

本文档定义每个分析章节的研究目标、数据输入输出、技术方法、实施步骤和阶段产物。回答"做什么、为什么、用什么方法"，与 `execution_prompts.md`（回答"怎么做"）配合使用。

---

## 第一章：数据概览与清洗（ch01）

**原型**：数据预处理型（原型A）

### 1.1 研究目标

回答 RQ-Sub-1：各路传感器信号在正常工况下的基准特征是什么？

- 建立 Genesis 数据集 9 路模拟量和 13 路离散量信号的基准统计特征
- 明确数据质量状况（缺失值、异常值、时间戳一致性）
- 为后续章节提供统一的数据加载接口和清洗后数据集

### 1.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| Genesis_AnomalyLabels.csv | data/原始数据1/ | CSV | 16,220行，含Label(0/1/2)，20列 |
| Genesis_StateMachineLabel.csv | data/原始数据1/ | CSV | 16,220行，含Label(0-8)，20列 |
| Genesis_lineardrive.csv | data/原始数据1/ | CSV | 7,424行，无Label，24列 |
| Genesis_normal.csv | data/原始数据1/ | CSV | 7,040行，无Label，24列 |
| Genesis_pressure.csv | data/原始数据1/ | CSV | 8,476行，无Label，24列 |

### 1.3 技术方法

**数据读取与验证**：
- `pd.read_csv()` 读取全部 5 个文件
- 检查文件编码、分隔符、列名一致性

**时间戳解析与标准化**：
- 前两个文件（AnomalyLabels/StateMachineLabel）使用 Unix 秒格式
- 后三个文件使用 Unix 毫秒格式，需统一转换为 datetime
- `pd.to_datetime(unit='s')` 和 `pd.to_datetime(unit='ms')`

**缺失值检测**：
- `df.isnull().sum()` 统计每列缺失值
- 计算缺失率 `df.isnull().mean()`

**描述性统计**：
- `df.describe()` 生成均值、标准差、最小值、25%/50%/75%分位数、最大值
- 按 Label 分组统计（正常 vs 异常）

**分布可视化**：
- `plt.hist()` / `sns.histplot()` 绘制信号分布直方图
- `sns.boxplot()` 绘制箱线图识别异常值
- `sns.kdeplot()` 绘制核密度估计图

### 1.4 实施步骤

1. **数据读取** — 使用 `pd.read_csv()` 读取 5 个 CSV 文件，记录基本信息
2. **列名对齐** — 对比 5 个文件的列名差异，建立统一列名映射
3. **时间戳解析** — 区分秒/毫秒格式，统一转换为 datetime 索引
4. **缺失值统计** — 按文件、按列统计缺失值数量和比例
5. **描述性统计** — 对每路信号计算均值、标准差、分位数
6. **分布可视化** — 绘制 9 路模拟量信号的分布直方图和箱线图
7. **数据质量报告** — 汇总数据规模、缺失情况、时间范围、信号范围
8. **生成 report.md** — 按四段框架撰写章节报告

### 1.5 阶段产物

| 产物名称 | 文件名 | 格式 | 后续使用 |
|----------|--------|------|----------|
| 数据集基本信息表 | `dataset_info_table.csv` | CSV | ch01 report.md |
| 信号基准特征统计表 | `signal_baseline_stats.csv` | CSV | ch03 异常对比基准 |
| 信号分布直方图 | `signal_distribution_ch01.png` | PNG | ch01 report.md、开题 PPT |
| 信号箱线图 | `signal_boxplot_ch01.png` | PNG | ch01 report.md |
| 数据质量报告 | `data_quality_report.md` | Markdown | 参考 |
| 章节报告 | `report.md` | Markdown | 最终交付 |

**输出目录**：`outputs/ch01_data_overview_and_cleaning/`

### 1.6 质量验证标准

- [ ] 5 个数据文件全部成功读取，无编码错误
- [ ] 时间戳统一转换为 datetime，格式正确
- [ ] 缺失值统计表覆盖所有列，缺失率计算准确
- [ ] 描述性统计表包含所有 9 路模拟量信号
- [ ] 分布图清晰可读，覆盖主要信号
- [ ] report.md 已生成（四段框架：背景、分析方法、分析发现、小结）
- [ ] notebook.ipynb 与 script.py 逻辑一致

---

## 第二章：PLC 状态机与工序分析（ch02）

**原型**：分析探索型（原型B）

### 2.1 研究目标

回答 RQ-Sub-2：PLC 状态机各状态（0-8）对应哪些分拣工序？各工序的时序规律和信号联动逻辑是什么？

- 基于 StateMachineLabel 的 9 种状态标签，拆解分拣全流程
- 量化各状态持续时间、状态转移概率、工序协同逻辑
- 绘制 PLC 状态转移图和分拣全流程信号时序图

### 2.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| Genesis_StateMachineLabel.csv | data/原始数据1/ | CSV | 16,220行，含Label(0-8) |
| ch01 清洗后数据 | outputs/ch01/ | CSV | 时间戳已标准化 |

### 2.3 技术方法

**状态识别与分割**：
- 基于 `Label` 列识别状态边界（状态变化点）
- `df['Label'].diff() != 0` 定位状态切换时刻

**状态持续时间统计**：
- 计算每个状态片段的持续时间
- `groupby('Label')['duration'].agg(['mean', 'std', 'min', 'max'])`

**状态转移矩阵**：
- 构建 9×9 状态转移概率矩阵
- `pd.crosstab(df['Label'], df['Label'].shift(-1), normalize='index')`

**工序时序可视化**：
- `sns.lineplot()` 绘制关键信号（ActCurrent, ActPosition, ActSpeed）时序图
- 使用不同颜色标注不同状态段
- `plt.axvspan()` 添加状态背景色块

**信号联动分析**：
- 计算同一状态下多路信号的相关系数
- 识别 PLC 控制信号（Gripper, MaterialIsMetal）与传感器信号的联动时序

### 2.4 实施步骤

1. **数据加载** — 读取 StateMachineLabel 数据，验证时间戳和标签完整性
2. **状态边界识别** — 使用 `diff()` 定位状态切换点，分割状态片段
3. **状态持续时间统计** — 计算每个状态的平均/标准差/最小/最大持续时间
4. **状态转移矩阵** — 构建 9×9 转移概率矩阵，识别主要转移路径
5. **工序时序可视化** — 绘制 2-3 路关键信号的时序图，按状态分段着色
6. **信号联动分析** — 分析 PLC 控制信号与传感器信号的时序关联
7. **生成图表** — PLC 状态转移图、分拣全流程信号时序图、工序耗时表
8. **生成 report.md** — 按四段框架撰写章节报告

### 2.5 阶段产物

| 产物名称 | 文件名 | 格式 | 后续使用 |
|----------|--------|------|----------|
| 状态持续时间统计表 | `state_duration_stats.csv` | CSV | ch02 report.md |
| 状态转移矩阵 | `state_transition_matrix.csv` | CSV | ch05 效能评估 |
| PLC 状态转移图 | `plc_state_transition.png` | PNG | 论文核心图、开题 PPT |
| 分拣全流程信号时序图 | `sorting_process_timeseries.png` | PNG | 论文核心图、开题 PPT |
| 工序耗时统计表 | `process_time_stats.csv` | CSV | ch02 report.md、开题报告 |
| 章节报告 | `report.md` | Markdown | 最终交付 |

**输出目录**：`outputs/ch02_plc_state_machine_analysis/`

### 2.6 质量验证标准

- [ ] 状态边界识别准确，无遗漏或重复
- [ ] 状态持续时间统计包含全部 9 种状态
- [ ] 状态转移矩阵 9×9 完整，概率归一化正确
- [ ] 时序图清晰展示至少 2-3 路关键信号
- [ ] 状态分段着色明显，图例完整
- [ ] 工序耗时表包含均值、标准差、范围
- [ ] report.md 已生成（四段框架）
- [ ] notebook.ipynb 与 script.py 逻辑一致

---

## 第三章：异常检测与抗干扰分析（ch03）

**原型**：分析探索型（原型B）

### 3.1 研究目标

回答 RQ-Sub-3 和 RQ-Sub-6：
- 直线驱动卡滞（Label=1）和驱动脱扣校正（Label=2）故障下，传感器信号如何畸变？
- 哪些信号特征对异常识别最具区分力？

- 对比正常（Label=0）与异常（Label=1/2）工况下传感器信号的差异
- 量化故障信号的畸变特征（幅值、波动、时域统计量）
- 探索性提取故障敏感特征，为故障预警提供特征工程基础

### 3.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| Genesis_AnomalyLabels.csv | data/原始数据1/ | CSV | 16,220行，Label(0/1/2) |
| ch01 信号基准统计 | outputs/ch01/ | CSV | 正常工况基准值 |
| ch02 状态片段信息 | outputs/ch02/ | CSV | 状态边界（用于定位故障时段） |

### 3.3 技术方法

**正常 vs 异常对比**：
- 按 Label 分组提取信号片段
- 计算各组信号的均值、标准差、最大值、最小值、峰度、偏度

**统计检验**：
- 独立样本 t 检验：`scipy.stats.ttest_ind()` 检验正常 vs 异常信号均值差异
- KS 检验：`scipy.stats.ks_2samp()` 检验分布差异

**波形对比可视化**：
- 同一信号正常 vs 异常波形叠加对比
- `plt.plot()` 绘制时序对比图
- 使用透明度和不同颜色区分

**特征提取**：
- 时域特征：均值、标准差、最大值、最小值、峰峰值、均方根、峭度、偏度
- 窗口统计：滑动窗口内的统计特征

**特征区分力评估**：
- 箱线图对比：`sns.boxplot()` 展示正常 vs 异常的特征分布
- 统计显著性：p-value < 0.05 认为有显著差异
- 效应量：Cohen's d 评估差异大小

### 3.4 实施步骤

1. **数据加载** — 读取 AnomalyLabels 数据，分离 Label=0/1/2 三组
2. **信号分组提取** — 提取各 Label 组的关键信号（ActCurrent, ActPosition, ActSpeed）
3. **描述性统计对比** — 计算三组信号的均值、标准差、范围
4. **统计检验** — 对每路信号进行 t 检验和 KS 检验
5. **波形对比可视化** — 绘制正常 vs 异常信号的时序叠加图
6. **特征提取** — 计算时域统计特征（均值、方差、峰度、偏度等）
7. **特征区分力评估** — 绘制特征箱线图，计算统计显著性和效应量
8. **生成图表** — 正常/异常信号对比图、畸变特征量化表、特征重要性排序
9. **生成 report.md** — 按四段框架撰写章节报告

### 3.5 阶段产物

| 产物名称 | 文件名 | 格式 | 后续使用 |
|----------|--------|------|----------|
| 正常 vs 异常统计对比表 | `normal_vs_anomaly_stats.csv` | CSV | ch03 report.md |
| 统计检验结果表 | `statistical_test_results.csv` | CSV | ch03 report.md |
| 正常/异常信号对比图 | `signal_comparison_normal_anomaly.png` | PNG | 论文核心图、开题 PPT |
| 畸变特征量化表 | `distortion_features_table.csv` | CSV | ch03 report.md、开题报告 |
| 特征箱线图 | `feature_boxplot_comparison.png` | PNG | ch03 report.md |
| 特征重要性排序 | `feature_importance_ranking.csv` | CSV | ch03 report.md、论文附录 |
| 章节报告 | `report.md` | Markdown | 最终交付 |

**输出目录**：`outputs/ch03_anomaly_detection_analysis/`

### 3.6 质量验证标准

- [ ] 三组数据（Label=0/1/2）正确分离，样本数准确
- [ ] 统计对比表覆盖所有关键信号
- [ ] t 检验和 KS 检验 p-value 计算正确
- [ ] 波形对比图清晰展示异常信号畸变
- [ ] 特征箱线图展示至少 5 个最具区分力的特征
- [ ] 特征重要性排序基于统计显著性
- [ ] report.md 已生成（四段框架）
- [ ] notebook.ipynb 与 script.py 逻辑一致

---

## 第四章：传感器性能关联分析（ch04）

**原型**：分析探索型（原型B）

### 4.1 研究目标

回答 RQ-Sub-4：多路传感器信号之间存在怎样的耦合关系？工况波动对传感器可靠性有何影响？

- 探究气压、位移、检测信号间的耦合关系
- 评估传感器在连续运行与工况波动下的可靠性
- 分析不同工况（normal/lineardrive/pressure）下信号稳定性差异

### 4.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| Genesis_lineardrive.csv | data/原始数据1/ | CSV | 7,424行，直线驱动工况 |
| Genesis_normal.csv | data/原始数据1/ | CSV | 7,040行，正常工况 |
| Genesis_pressure.csv | data/原始数据1/ | CSV | 8,476行，气压工况 |
| ch01 清洗后数据 | outputs/ch01/ | CSV | 时间戳已标准化 |

### 4.3 技术方法

**相关性分析**：
- Pearson 相关系数：`df.corr(method='pearson')` — 线性关系
- Spearman 相关系数：`df.corr(method='spearman')` — 单调关系
- 相关性热力图：`sns.heatmap()`

**工况对比分析**：
- 分别计算 normal、lineardrive、pressure 三种工况的相关性矩阵
- 对比不同工况下相关性的变化

**信号稳定性评估**：
- 计算滑动窗口内的标准差：`df.rolling(window=100).std()`
- 稳定性评分：标准差的倒数（标准差越小越稳定）
- 变异系数 CV = 标准差 / 均值

**多传感器联动分析**：
- 分析 ActCurrent（电流）与 ActSpeed（速度）的联动关系
- 分析 IsForce（力控）与 ActPosition（位置）的响应关系

### 4.4 实施步骤

1. **数据加载** — 读取 lineardrive、normal、pressure 三个文件
2. **相关性计算** — 分别计算三种工况的 Pearson 和 Spearman 相关矩阵
3. **相关性热力图** — 绘制三种工况的相关性热力图对比
4. **工况差异分析** — 识别不同工况下相关性显著变化的信号对
5. **信号稳定性计算** — 计算滑动窗口标准差和变异系数
6. **稳定性评分** — 对各信号进行稳定性排序
7. **多传感器联动分析** — 分析电流-速度、力控-位置的联动关系
8. **生成图表** — 传感器相关性热力图、信号稳定性评分表
9. **生成 report.md** — 按四段框架撰写章节报告

### 4.5 阶段产物

| 产物名称 | 文件名 | 格式 | 后续使用 |
|----------|--------|------|----------|
| 相关性矩阵（三种工况） | `correlation_matrix_{工况}.csv` | CSV | ch04 report.md |
| 传感器相关性热力图 | `sensor_correlation_heatmap.png` | PNG | 论文核心图、开题 PPT |
| 工况对比相关性差异表 | `correlation_diff_by_condition.csv` | CSV | ch04 report.md |
| 信号稳定性评分表 | `signal_stability_scores.csv` | CSV | ch04 report.md、开题报告 |
| 稳定性趋势图 | `stability_trend_analysis.png` | PNG | ch04 report.md |
| 章节报告 | `report.md` | Markdown | 最终交付 |

**输出目录**：`outputs/ch04_sensor_performance_analysis/`

### 4.6 质量验证标准

- [ ] 三种工况的相关性矩阵完整，无 NaN
- [ ] 热力图清晰展示所有信号对的相关性
- [ ] 工况差异表识别至少 3 对显著变化的信号
- [ ] 稳定性评分基于滑动窗口统计
- [ ] 稳定性评分表包含均值、标准差、变异系数
- [ ] report.md 已生成（四段框架）
- [ ] notebook.ipynb 与 script.py 逻辑一致

---

## 第五章：运行效能评估（ch05）

**原型**：总结报告型（原型C）

### 5.1 研究目标

回答 RQ-Sub-5：正常工况与故障工况下的分拣效率和系统稳定性差异有多大？

- 计算正常与故障场景下的分拣效率（周期时间、单位时间分拣件数）
- 统计稳定运行时长与异常发生率
- 为课题"分拣精度 ≥99%"目标提供工业数据基准
- 分析数据集局限性，为后续补充提供方向

### 5.2 数据输入

| 数据项 | 来源 | 格式 | 说明 |
|--------|------|------|------|
| ch02 状态持续时间 | outputs/ch02/ | CSV | 各状态持续时间统计 |
| ch02 状态转移矩阵 | outputs/ch02/ | CSV | 状态转移概率 |
| ch03 异常统计 | outputs/ch03/ | CSV | Label=1/2 的样本数和比例 |
| ch01 数据概况 | outputs/ch01/ | CSV | 总样本数、时间范围 |

### 5.3 技术方法

**分拣周期计算**：
- 基于状态转移识别完整分拣周期（如：Idle → ... → Idle）
- 计算单周期平均耗时、标准差、最大/最小值

**效率指标计算**：
- 单位时间分拣件数 = 总周期数 / 总时长
- 理论最大效率 vs 实际效率对比

**稳定性评估**：
- 连续无故障运行时长统计
- 异常发生率 = 异常样本数 / 总样本数
- 平均故障间隔时间（MTBF）估算

**正常 vs 故障对比**：
- 正常工况（Label=0）的效率基准
- 故障工况（Label=1/2）的效率下降幅度

**局限性分析**：
- 数据覆盖范围：信号类型、物料种类、故障场景
- 样本不平衡问题：异常样本仅占 0.3%
- 时间范围限制：单一时间段数据

### 5.4 实施步骤

1. **数据整合** — 加载 ch02 和 ch03 的产物数据
2. **分拣周期识别** — 基于状态转移识别完整分拣周期
3. **周期时间统计** — 计算单周期平均耗时、标准差、范围
4. **效率计算** — 计算单位时间分拣件数、理论 vs 实际效率
5. **稳定性统计** — 计算异常发生率、连续运行时长分布
6. **正常 vs 故障对比** — 量化故障对效率的影响
7. **局限性分析** — 总结数据覆盖边界和样本限制
8. **生成图表** — 效率对比表、异常率统计、局限性清单
9. **生成 report.md** — 按四段框架撰写章节报告

### 5.5 阶段产物

| 产物名称 | 文件名 | 格式 | 后续使用 |
|----------|--------|------|----------|
| 分拣周期统计表 | `sorting_cycle_stats.csv` | CSV | ch05 report.md |
| 效率对比表 | `efficiency_comparison_table.csv` | CSV | ch05 report.md、开题报告 |
| 异常率统计表 | `anomaly_rate_stats.csv` | CSV | ch05 report.md |
| 系统稳定性评估 | `system_stability_assessment.csv` | CSV | ch05 report.md |
| 数据集局限性清单 | `dataset_limitations.md` | Markdown | ch05 report.md、开题报告 |
| 后续补充建议 | `future_data_recommendations.md` | Markdown | 后续规划参考 |
| 章节报告 | `report.md` | Markdown | 最终交付 |

**输出目录**：`outputs/ch05_performance_evaluation/`

### 5.6 质量验证标准

- [ ] 分拣周期识别逻辑清晰，周期数合理
- [ ] 效率计算包含理论值和实际值
- [ ] 异常发生率计算准确（Label=1/2 占比）
- [ ] 正常 vs 故障对比量化差异
- [ ] 局限性分析覆盖数据、方法、范围三个维度
- [ ] 后续建议具体可操作
- [ ] report.md 已生成（四段框架）
- [ ] notebook.ipynb 与 script.py 逻辑一致

---

## 附录：章节依赖与执行批次

### 依赖关系图

```
ch01（数据概览与清洗）
 ├── ch02（PLC 状态机与工序分析）
 │    └── ch03（异常检测与抗干扰分析）
 │         └── ch05（运行效能评估）
 └── ch04（传感器性能关联分析）
      └── ch05（运行效能评估）
```

### 执行批次

| 批次 | 章节 | 说明 | 预计完成时间 |
|------|------|------|-------------|
| Batch 1 | ch01 | 基础数据准备 | 第 12 周前 |
| Batch 2 | ch02, ch04 | 并行执行（均依赖 ch01） | 第 12 周前 |
| Batch 3 | ch03 | 依赖 ch02 | 第 12 周前 |
| Batch 4 | ch05 | 汇总（依赖 ch03, ch04） | 第 16 周前 |

### 数据流向

| 章节 | 输入数据 | 输出产物（被后续使用） |
|------|---------|----------------------|
| ch01 | 5 个原始 CSV | 清洗后数据、基准统计表 |
| ch02 | ch01 输出 + StateMachineLabel | 状态持续时间、转移矩阵 |
| ch03 | ch01 输出 + AnomalyLabels | 异常对比统计、特征重要性 |
| ch04 | ch01 输出 + 3 个无标签文件 | 相关性矩阵、稳定性评分 |
| ch05 | ch02 + ch03 + ch04 输出 | 效率对比、局限性清单 |

---

## 修订记录

| 版本 | 日期 | 修订内容 |
|------|------|---------|
| v1.0 | 2026-06-02 | 初始版本，基于 flow_design v2.0 模板生成，包含 5 章完整设计 |
