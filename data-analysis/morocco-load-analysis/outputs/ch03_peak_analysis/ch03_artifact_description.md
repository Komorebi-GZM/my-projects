# Prompt-03 产物说明文档 — 负荷峰值识别与峰值特征研究

> **章节**: 第三章 | **脚本**: `src/ch03_peak_analysis/peak_detection.py/.ipynb`
> **输入数据**: `ch01_feature_engineered_data.csv` + `ch02_descriptive_stats.csv`
> **产物数量**: 12 个（5 CSV + 7 PNG）

---

## 一、数据产物说明

### 1. `ch03_peak_thresholds.csv`

| 项目 | 内容 |
|------|------|
| **是什么** | 每个城市每个 zone 的峰值判定阈值表 |
| **列说明** | `city`(城市), `zone`(区域), `q90_threshold`(90%分位数), `q95_threshold`(95%分位数，主阈值), `q98_threshold`(98%分位数), `max_value`(最大值), `q95_to_max_ratio`(阈值/最大值比率) |
| **作用** | 定义"什么是峰值"的客观标准。95% 分位数意味着只有排名前 5% 的负荷值被判定为峰值。q90/q98 作为参考区间，ratio 用于评估阈值合理性（正常范围 0.70~0.95） |
| **后续使用** | Prompt-07 配电网优化将参考此阈值设定优化目标 |

### 2. `ch03_peak_events.csv`

| 项目 | 内容 |
|------|------|
| **是什么** | 峰值事件完整明细表（逐行逐条记录） |
| **列说明** | `DateTime`(时间戳, 索引), `city`(城市), `zone`(区域), `peak_load_kw`(峰值负荷, kW), `threshold_kw`(对应阈值, kW), `excess_ratio_pct`(超出幅度百分比) |
| **作用** | 记录所有超过 95% 阈值的负荷时序点。`excess_ratio_pct` 表示实际负荷超出阈值的百分比，值越大说明峰值越严重。是 Step 3.3~3.7 所有分析的数据基础 |
| **数据规模** | 约 71,823 行（全量明细） |

### 3. `ch03_peak_events_summary.csv`

| 项目 | 内容 |
|------|------|
| **是什么** | 峰值事件聚合摘要表（按城市+zone 汇总） |
| **列说明** | `city`, `zone`, `total_data_points`(总数据点数), `total_peak_count`(峰值事件总数), `peak_ratio_pct`(峰值占比%), `avg_excess_ratio_pct`(平均超出幅度%), `max_excess_ratio_pct`(最大超出幅度%), `avg_peak_load_kw`(平均峰值负荷), `max_peak_load_kw`(最大峰值负荷) |
| **作用** | 轻量级参考表，无需加载大体积明细即可快速了解各 zone 的峰值概况。`peak_ratio_pct` 理论值约 5%，偏离过大说明数据分布异常 |

### 4. `ch03_peak_duration_stats.csv`

| 项目 | 内容 |
|------|------|
| **是什么** | 峰值持续时长统计表（双口径） |
| **列说明** | `scope`(统计口径: `city_aggregated`=城市聚合 / `zone_specific`=单Zone精确), `city`, `zone`, `group_id`(片段编号), `start_time`(开始时间), `end_time`(结束时间), `duration_minutes`(持续分钟数), `duration_hours`(持续小时数) |
| **作用** | 将离散的峰值点归并为连续的"峰值事件片段"。**城市聚合口径**反映城市整体电网过载风险时段（任一 zone 超阈即算）；**单 Zone 口径**反映单个馈线/变压器的过载风险。持续时长是评估设备热累积风险的关键指标 |
| **数据规模** | 城市聚合 4,504 个片段 + 单 Zone 7,844 个片段 |

### 5. `ch03_peak_attribution.csv`

| 项目 | 内容 |
|------|------|
| **是什么** | 峰值成因五维交叉归因表 |
| **列说明** | `city`(城市), `year`(年份), `season`(季节: Winter/Spring/Summer/Autumn), `hour`(小时 0~23), `is_weekend`(是否周末: 0=工作日, 1=周末), `peak_count`(该组合下的峰值事件数), `avg_peak_load`(平均峰值负荷, kW), `max_peak_load`(最大峰值负荷, kW) |
| **作用** | 量化不同因素（季节、时段、工作日/周末、年度）对峰值事件的驱动作用。按 `peak_count` 降序排列，排名第一的组合即为"最危险的峰值场景"。可用于回答"什么因素最可能导致峰值" |
| **后续使用** | Prompt-07 配电网优化将参考此归因结论 |

### 6. `ch03_anomaly_peak_flags.csv`

| 项目 | 内容 |
|------|------|
| **是什么** | 异常峰值与规律峰值的分类标记表 |
| **列说明** | `city`, `zone`, `total_peaks`(总峰值数), `anomaly_peaks`(异常峰值数), `regular_peaks`(规律峰值数), `anomaly_ratio`(异常占比%) |
| **作用** | 区分"规律性正常高峰"（渐进上升，如每日晚高峰）与"突发型异常峰值"（瞬间跳变，如设备故障）。异常检测方法：30 分钟滚动平滑 + 1 小时差分 + 3σ 阈值。`anomaly_ratio` 正常应 < 10% |

---

## 二、图表产物说明

### 7. `ch03_peak_hourly_distribution.png`

| 项目 | 内容 |
|------|------|
| **是什么** | 四城市峰值事件 24 小时分布柱状图 |
| **布局** | 2×2 子图，每个子图对应一个城市 |
| **横轴 (X)** | **Hour** — 小时（0~23），每 2 小时一个刻度 |
| **纵轴 (Y)** | **Peak Event Count** — 峰值事件数量（次） |
| **标注** | 每个子图标注峰值频次最高的 3 个小时 |
| **颜色** | 每个城市独立配色：Laayoune(蓝), Boujdour(绿), Foum eloued(橙), Marrakech(粉红) |
| **作用** | 识别一天中哪些时段最容易出现负荷峰值。通常可见早高峰（8~10 时）和晚高峰（18~21 时）两个高发时段 |

### 8. `ch03_peak_seasonal_distribution.png`

| 项目 | 内容 |
|------|------|
| **是什么** | 四城市峰值事件季节分布柱状图（含年度分组） |
| **布局** | 2×2 子图，每个子图对应一个城市 |
| **横轴 (X)** | **Season** — 季节（Winter 冬季 / Spring 春季 / Summer 夏季 / Autumn 秋季） |
| **纵轴 (Y)** | **Peak Event Count** — 峰值事件数量（次） |
| **分组** | 按年度分组（图例标注年份），不同颜色的柱子代表不同年份 |
| **标注** | 每个柱子上方标注具体数值 |
| **颜色** | 季节配色：冬(浅蓝 #4FC3F7) / 春(浅绿 #81C784) / 夏(浅橙 #FFB74D) / 秋(浅红 #E57373) |
| **作用** | 分析季节对峰值的影响，判断是否存在夏季制冷负荷驱动的峰值增长趋势，以及年度间的变化 |

### 9. `ch03_peak_spacetime_heatmap_{city}.png`（4 张）

| 项目 | 内容 |
|------|------|
| **是什么** | 每城市峰值事件"小时×月份"二维热力图 |
| **文件名** | `laayoune` / `boujdour` / `foum_eloued` / `marrakech` |
| **横轴 (X)** | **Month** — 月份（1~12） |
| **纵轴 (Y)** | **Hour** — 小时（0~23，从上到下） |
| **色值含义** | 每个格子的数字 = 该月份该小时区间内发生的峰值事件次数（次）。颜色越深（红）表示峰值越密集 |
| **色带 (Colorbar)** | **Peak Event Count** — 峰值事件计数 |
| **作用** | 同时展示峰值的时间（日内）和季节（月度）分布特征，是识别"何时最危险"的最直观工具。可清晰看到夏季傍晚等高风险聚集区域 |

---

## 三、产物间依赖关系

```
Step 3.1 阈值计算 ──→ ch03_peak_thresholds.csv
        │
        ▼
Step 3.2 事件提取 ──→ ch03_peak_events.csv (明细)
        │              ch03_peak_events_summary.csv (摘要)
        │
        ├──→ Step 3.3 持续时长 ──→ ch03_peak_duration_stats.csv
        ├──→ Step 3.4 小时分布 ──→ ch03_peak_hourly_distribution.png
        ├──→ Step 3.5 季节分布 ──→ ch03_peak_seasonal_distribution.png
        ├──→ Step 3.6 时空热力图 ──→ ch03_peak_spacetime_heatmap_*.png (×4)
        └──→ Step 3.7 成因归因 ──→ ch03_peak_attribution.csv

Step 3.1 + 原始数据 ──→ Step 3.8 异常研判 ──→ ch03_anomaly_peak_flags.csv
```

---

## 四、后续章节引用

| 产物 | 被引用章节 | 用途 |
|------|-----------|------|
| `ch03_peak_thresholds.csv` | Prompt-07 配电网优化 | 设定优化目标基准 |
| `ch03_peak_attribution.csv` | Prompt-07 配电网优化 | 提供峰值成因分析结论 |
| `ch03_anomaly_peak_flags.csv` | 报告撰写 | 异常峰值比例与风险评估 |
| `ch03_peak_duration_stats.csv` | 报告撰写 | 电网过载风险时段统计 |
| 全部图表 | 报告配图 | 各章节报告的插图素材 |
