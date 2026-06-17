# Prompt-02 产物说明文档

> **章节**: 用电负荷特征挖掘与用电规律分析
> **输入数据**: `outputs/ch01_data_preprocessing/ch01_feature_engineered_data.csv`
> **脚本**: `src/ch02_load_pattern/analysis.py` / `analysis.ipynb`

---

## 产物总览

本章节共产出 **18 个文件**（3 个 CSV 数据表 + 15 张 PNG 可视化图表），涵盖描述性统计、日内负荷规律、工作日/周末差异、周内周期性、跨城市对比、居民/工业负荷分层六大分析维度。

---

## 一、数据表产物

### 1. `ch02_descriptive_stats.csv` — 描述性统计总表

| 项目 | 说明 |
|------|------|
| **是什么** | 每个城市每个 zone 的基本统计指标汇总表 |
| **作用** | 为后续峰值识别（Prompt-03）提供各 zone 的统计基准；为预测建模（Prompt-04）提供特征理解参考 |
| **列结构** | `city`（城市）, `zone`（区域编号）, `count`（样本量）, `mean`（均值）, `median`（中位数）, `std`（标准差）, `min`（最小值）, `max`（最大值）, `skew`（偏度）, `kurtosis`（峰度） |
| **行数** | 28 行（4 城市 × 7 zone） |

---

### 2. `ch02_load_rate_cv.csv` — 负荷率与变异系数表

| 项目 | 说明 |
|------|------|
| **是什么** | 衡量各 zone 用电稳定性的两个核心衍生指标 |
| **作用** | 为配电网优化（Prompt-07）提供负荷率基准；为跨国对比（Prompt-06）提供标准化指标 |
| **列结构** | `city`（城市）, `zone`（区域编号）, `mean_kW`（平均负荷 kW）, `max_kW`（最大负荷 kW）, `std_kW`（标准差 kW）, `load_rate`（负荷率 = mean/max）, `cv`（变异系数 = std/mean） |
| **关键解读** | 负荷率越高说明设备利用率越好；CV 越小说明用电越平稳 |

---

### 3. `ch02_residential_industrial_class.csv` — 居民/工业负荷分类表

| 项目 | 说明 |
|------|------|
| **是什么** | 基于 KMeans 聚类将 28 个 zone 分为居民（Residential）和工业（Industrial）两类 |
| **作用** | 为峰值识别（Prompt-03）提供负荷类型标签；为跨国对比（Prompt-06）提供分层分析依据 |
| **列结构** | `city`（城市）, `zone`（区域编号）, `cv`（变异系数）, `peak_valley_ratio`（峰谷比）, `mean_kW`（平均负荷）, `max_kW`（最大负荷）, `cluster`（聚类编号）, `load_type`（负荷类型：Industrial / Residential） |
| **分类逻辑** | 以 CV（变异系数）和峰谷比作为聚类特征，低 CV 的 zone 归为工业（用电平稳），高 CV 的归为居民（波动大） |

---

## 二、可视化图表产物

### 4. `ch02_daily_load_curve_{city}.png` — 日内 24 小时平均负荷曲线（4 张）

| 城市 | 文件名 |
|------|--------|
| 拉尤恩 | `ch02_daily_load_curve_laayoune.png` |
| 布杰杜尔 | `ch02_daily_load_curve_boujdour.png` |
| 富姆埃卢德 | `ch02_daily_load_curve_foum eloued.png` |
| 马拉喀什 | `ch02_daily_load_curve_marrakech.png` |

| 项目 | 说明 |
|------|------|
| **是什么** | 每个城市各 zone 的 24 小时平均负荷折线图 |
| **作用** | 揭示日内用电节奏，识别早晚高峰时段和午间低谷 |
| **图表类型** | 多系列折线图（每条线代表一个 zone） |
| **横轴（X 轴）** | `Hour` — 小时（0~23），整数刻度 |
| **纵轴（Y 轴）** | `Load (kW)` — 负荷值，单位千瓦 |
| **图例（Legend）** | `zone1` ~ `zone7`，位于图表右侧外部 |
| **标题** | `{城市名} - 24h Average Load Curve` |
| **数据含义** | 每个数据点 = 该小时内所有 10 分钟采样值的算术平均 |

---

### 5. `ch02_weekday_vs_weekend_{city}.png` — 工作日 vs 周末负荷对比（4 张）

| 城市 | 文件名 |
|------|--------|
| 拉尤恩 | `ch02_weekday_vs_weekend_laayoune.png` |
| 布杰杜尔 | `ch02_weekday_vs_weekend_boujdour.png` |
| 富姆埃卢德 | `ch02_weekday_vs_weekend_foum eloued.png` |
| 马拉喀什 | `ch02_weekday_vs_weekend_marrakech.png` |

| 项目 | 说明 |
|------|------|
| **是什么** | 同一城市工作日与周末的平均负荷曲线叠加对比 |
| **作用** | 量化作息规律对用电的影响，判断该城市工业/居民负荷占比 |
| **图表类型** | 双系列折线图 + 差异填充区域 |
| **横轴（X 轴）** | `Hour` — 小时（0~23） |
| **纵轴（Y 轴）** | `Average Load (kW)` — 各 zone 平均后的综合负荷 |
| **图例（Legend）** | `Weekday`（蓝色实线 + 圆形标记）, `Weekend`（橙红色实线 + 方形标记） |
| **填充区域** | 灰色半透明区域表示工作日与周末的负荷差值 |
| **标题** | `{城市名} - Weekday vs Weekend Load Comparison` |
| **数据含义** | 工作日 = is_weekend=0 的所有日期；周末 = is_weekend=1 的所有日期 |

---

### 6. `ch02_weekly_heatmap_{city}.png` — 周内负荷热力图（4 张）

| 城市 | 文件名 |
|------|--------|
| 拉尤恩 | `ch02_weekly_heatmap_laayoune.png` |
| 布杰杜尔 | `ch02_weekly_heatmap_boujdour.png` |
| 富姆埃卢德 | `ch02_weekly_heatmap_foum eloued.png` |
| 马拉喀什 | `ch02_weekly_heatmap_marrakech.png` |

| 项目 | 说明 |
|------|------|
| **是什么** | 以热力图形式展示一周 7 天 × 24 小时的负荷分布 |
| **作用** | 直观展示周内周期规律，识别工作日/周末的负荷差异时段 |
| **图表类型** | 热力图（seaborn heatmap），色阶为 YlOrRd（黄-橙-红） |
| **纵轴（Y 轴）** | `Hour` — 小时（0~23），从上到下 |
| **横轴（X 轴）** | `Day of Week` — 星期，列名依次为 `Mon, Tue, Wed, Thu, Fri, Sat, Sun` |
| **色阶条（Colorbar）** | `Load (kW)` — 颜色越深（红）表示负荷越高，越浅（黄）表示负荷越低 |
| **单元格标注** | 每个格子内标注具体数值（保留 1 位小数，单位 kW） |
| **标题** | `{城市名} - Weekly Load Heatmap (kW)` |
| **数据含义** | 每个格子的值 = 对应小时 + 对应星期几的所有 10 分钟采样值的算术平均 |

---

### 7. `ch02_cross_city_comparison.png` — 跨城市横向对比（2×2 子图版）

| 项目 | 说明 |
|------|------|
| **是什么** | 四城市各自独立子图，展示综合平均负荷的 24 小时曲线 |
| **作用** | 对比不同城市的日内负荷形态和量级差异 |
| **图表类型** | 2×2 多子图折线图，每个子图一个城市 |
| **子图布局** | 左上 = Laayoune（蓝色），右上 = Boujdour（绿色），左下 = Foum eloued（橙色），右下 = Marrakech（粉红色） |
| **各子图横轴（X 轴）** | `Hour` — 小时（0~23），间隔 2 小时 |
| **各子图纵轴（Y 轴）** | `Load (kW)` — 该城市所有 zone 的平均综合负荷 |
| **总标题** | `Cross-City 24h Load Curve Comparison` |
| **数据含义** | 每条曲线 = 该城市所有 zone 在每小时的均值再取平均 |

---

### 8. `ch02_cross_city_comparison_overlay.png` — 跨城市叠加对比图

| 项目 | 说明 |
|------|------|
| **是什么** | 四城市综合负荷曲线叠加在同一坐标系中 |
| **作用** | 直接对比城市间负荷水平和日内形态差异 |
| **图表类型** | 多系列折线图 |
| **横轴（X 轴）** | `Hour` — 小时（0~23） |
| **纵轴（Y 轴）** | `Average Load (kW)` — 各城市综合平均负荷 |
| **图例（Legend）** | `Laayoune`（蓝色）, `Boujdour`（绿色）, `Foum eloued`（橙色）, `Marrakech`（粉红色） |
| **标题** | `Cross-City 24h Load Curve - Overlay` |
| **注意** | Marrakech 负荷量级（~200 kW）远高于其他三城市（~10-20 kW），叠加图中量级差异明显 |

---

### 9. `ch02_res_vs_ind_comparison.png` — 居民 vs 工业负荷对比

| 项目 | 说明 |
|------|------|
| **是什么** | 双面板图：左图为两类负荷的 24 小时日内曲线对比，右图为特征指标柱状图对比 |
| **作用** | 量化居民负荷与工业负荷的差异化运行模式 |
| **图表类型** | 左 = 双系列折线图；右 = 分组柱状图 |

**左图 — 日内曲线对比：**

| 元素 | 说明 |
|------|------|
| 横轴（X 轴） | `Hour` — 小时（0~23） |
| 纵轴（Y 轴） | `Average Load (kW)` — 同类型所有 zone 的平均负荷 |
| 图例 | `Residential`（粉红色 + 圆形标记）, `Industrial`（蓝色 + 菱形标记） |
| 标题 | `Residential vs Industrial - 24h Load Curve` |

**右图 — 特征指标对比：**

| 元素 | 说明 |
|------|------|
| 横轴（X 轴） | `Load Type` — 负荷类型（Industrial / Residential） |
| 纵轴（Y 轴） | `Value` — 指标数值 |
| 柱状系列 | `CV`（橙色）— 变异系数均值；`Peak/Valley Ratio`（绿色）— 峰谷比均值；`Mean Load (normalized)`（紫色）— 平均负荷（归一化到 0~1） |
| 数值标注 | 每根柱子顶部标注具体数值 |
| 标题 | `Residential vs Industrial - Feature Comparison` |

---

## 三、英文-中文标注对照表

由于运行环境未配置中文字体，图表中所有文字标注均使用英文。以下为完整的英文-中文对照关系，供报告撰写时参考：

### 通用标注

| 英文（图中实际） | 中文（规范要求） |
|------------------|------------------|
| Hour | 小时 |
| Load (kW) | 负荷 (kW) |
| Average Load (kW) | 平均负荷 (kW) |
| Day of Week | 星期 |
| Load Type | 负荷类型 |
| Value | 数值 |

### 星期对照

| 英文（图中实际） | 中文（规范要求） |
|------------------|------------------|
| Mon | 周一 |
| Tue | 周二 |
| Wed | 周三 |
| Thu | 周四 |
| Fri | 周五 |
| Sat | 周六 |
| Sun | 周日 |

### 图例对照

| 英文（图中实际） | 中文（规范要求） |
|------------------|------------------|
| Weekday | 工作日 |
| Weekend | 周末 |
| Residential | 居民负荷 |
| Industrial | 工业负荷 |
| CV | 变异系数 |
| Peak/Valley Ratio | 峰谷比 |
| Mean Load (normalized) | 平均负荷（归一化） |

### 标题对照

| 图表文件 | 英文标题（图中实际） | 中文标题（规范要求） |
|----------|---------------------|---------------------|
| `ch02_daily_load_curve_{city}.png` | `{城市} - 24h Average Load Curve` | `{城市} - 24小时平均负荷曲线` |
| `ch02_weekday_vs_weekend_{city}.png` | `{城市} - Weekday vs Weekend Load Comparison` | `{城市} - 工作日与周末负荷对比` |
| `ch02_weekly_heatmap_{city}.png` | `{城市} - Weekly Load Heatmap (kW)` | `{城市} - 周内负荷热力图 (kW)` |
| `ch02_cross_city_comparison.png` | `Cross-City 24h Load Curve Comparison` | 跨城市24小时负荷曲线对比 |
| `ch02_cross_city_comparison_overlay.png` | `Cross-City 24h Load Curve - Overlay` | 跨城市24小时负荷曲线 - 叠加对比 |
| `ch02_res_vs_ind_comparison.png`（左图） | `Residential vs Industrial - 24h Load Curve` | 居民与工业 - 24小时负荷曲线对比 |
| `ch02_res_vs_ind_comparison.png`（右图） | `Residential vs Industrial - Feature Comparison` | 居民与工业 - 特征指标对比 |

### CSV 列名对照

| 英文列名 | 中文含义 |
|----------|----------|
| city | 城市 |
| zone | 区域编号 |
| count | 样本量 |
| mean / mean_kW | 均值 (kW) |
| median | 中位数 |
| std / std_kW | 标准差 (kW) |
| min | 最小值 |
| max / max_kW | 最大值 (kW) |
| skew | 偏度 |
| kurtosis | 峰度 |
| load_rate | 负荷率（= 均值 / 最大值） |
| cv | 变异系数（= 标准差 / 均值） |
| peak_valley_ratio | 峰谷比（= 日内最大值 / 日内最小值） |
| cluster | 聚类编号 |
| load_type | 负荷类型（Industrial / Residential） |

---

## 四、产物后续流向

| 产物 | 后续使用章节 |
|------|-------------|
| `ch02_descriptive_stats.csv` | Prompt-03（峰值识别） |
| `ch02_load_rate_cv.csv` | Prompt-06（跨国对比）, Prompt-07（配电网优化） |
| `ch02_residential_industrial_class.csv` | Prompt-03（峰值识别）, Prompt-06（跨国对比） |
| 所有 PNG 图表 | 最终报告配图 |
