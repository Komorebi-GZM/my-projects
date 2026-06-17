# Product_Sales_Analysis — 任务派发指南

> 项目：Product_Sales_Analysis  
> 生成日期：2026-05-08  
> 章节数：5 章  
> 批次数：4 批  
> 最大并行度：2  
> 文档版本：v1.0

---

## 一、全局依赖 DAG 图

```
                    ┌──────────────────┐
                    │   Prompt-01      │
                    │   数据清洗        │  Batch 1（串行前置）
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Prompt-02      │
                    │   描述性统计      │  Batch 2（串行）
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──────┐     │      ┌────────▼──────┐
     │  Prompt-03    │     │      │  Prompt-04    │
     │  销售趋势预测  │     │      │  价格弹性分析  │  Batch 3（并行）
     └────────┬──────┘     │      └────────┬──────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                    ┌────────▼─────────┐
                    │   Prompt-05      │
                    │   结论与业务建议  │  Batch 4（串行收束）
                    └──────────────────┘
```

### 依赖关系矩阵

|  | P-01 | P-02 | P-03 | P-04 | P-05 |
|--|------|------|------|------|------|
| **P-01** | — | → | → | → | |
| **P-02** | | — | → | → | → |
| **P-03** | | | — | | → |
| **P-04** | | | | — | → |
| **P-05** | | | | | — |

> **图例**：→ 表示"产物被依赖"

---

## 二、批次划分

### 2.1 批次总览

| 批次 | Prompt | 章节名称 | 执行模式 | 并行度 | 前置依赖 |
|------|--------|---------|---------|--------|---------|
| **Batch 1** | Prompt-01 | 数据清洗 | 串行 | 1 | 无 |
| **Batch 2** | Prompt-02 | 描述性统计与可视化 | 串行 | 1 | Batch 1 |
| **Batch 3** | Prompt-03 + Prompt-04 | 销售趋势预测 + 价格弹性分析 | **并行** | **2** | Batch 1 + Batch 2 |
| **Batch 4** | Prompt-05 | 结论与业务建议 | 串行 | 1 | Batch 2 + Batch 3 |

### 2.2 批次详细说明

#### Batch 1：数据清洗（串行前置）

- **目标**：完成原始数据质量检查和清洗，为全部后续章节提供干净数据
- **执行模式**：串行（必须第一个完成）
- **输入数据**：`data/product_sales_dataset.csv`
- **产出数据**：`outputs/ch01_data_cleaning/ch01_cleaned_data.csv`
- **预计耗时**：~1 分钟
- **完成标志**：`outputs/ch01_data_cleaning/report.md` 已生成

#### Batch 2：描述性统计与可视化（串行）

- **目标**：多维度描述性分析，生成统计表和可视化图表
- **执行模式**：串行（ch03/ch04 依赖其月度趋势数据）
- **输入数据**：`outputs/ch01_data_cleaning/ch01_cleaned_data.csv`
- **产出数据**：`outputs/ch02_descriptive_analysis/` 下 13 个产物
- **预计耗时**：~3 分钟
- **完成标志**：`outputs/ch02_descriptive_analysis/report.md` + 6 张 PNG + 6 个 CSV

#### Batch 3：销售趋势预测 + 价格弹性分析（并行）

- **目标**：同时进行预测分析和弹性分析，两者互不依赖
- **执行模式**：**并行**（两条支线可同时启动）
- **支线 A（Prompt-03）输入**：`ch01_cleaned_data.csv` + `monthly_trend.csv`
- **支线 B（Prompt-04）输入**：`ch01_cleaned_data.csv`
- **预计耗时**：~2 分钟（并行后总耗时取最长）
- **完成标志**：两个章节的 `report.md` 均已生成

#### Batch 4：结论与业务建议（串行收束）

- **目标**：综合全部前序发现，输出结构化业务建议
- **执行模式**：串行（需等待全部前序章节完成）
- **输入数据**：ch02/ch03/ch04 的全部核心产物
- **产出数据**：`outputs/ch05_conclusions_and_recommendations/` 下 5 个产物
- **预计耗时**：~1 分钟
- **完成标志**：`outputs/ch05_conclusions_and_recommendations/report.md` 已生成

### 2.3 执行命令

```bash
cd Product_Sales_Analysis
conda activate py310

# ===== Batch 1 =====
python src/ch01_data_cleaning/script.py

# ===== Batch 2 =====
python src/ch02_descriptive_analysis/script.py

# ===== Batch 3（并行）=====
python src/ch03_sales_forecasting/script.py &
python src/ch04_price_elasticity/script.py &
wait

# ===== Batch 4 =====
python src/ch05_conclusions_and_recommendations/script.py
```

---

## 三、章节关键信息速查表

### Prompt-01：数据清洗

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-01 |
| **章节名称** | 数据清洗 |
| **输入数据** | `data/product_sales_dataset.csv` |
| **核心产物** | `ch01_cleaned_data.csv`, `report.md` |
| **后续依赖方** | Prompt-02, Prompt-03, Prompt-04 |
| **技能调用** | Skill-01 (data_loader), Skill-04 (output_manager) |

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-01 部分，理解清洗目标
2. 调用 Skill-01 的 `load_raw_data()` 加载 `data/product_sales_dataset.csv`
3. 执行缺失值检测（`df.isnull().sum()`）、重复值检测（`df.duplicated().sum()`）
4. 将 `Order_Date` 转换为 datetime 类型（`pd.to_datetime()`）
5. 验证数值字段类型为 int64，Category 有 6 个唯一值，Customer_City 有 5 个唯一值
6. 调用 Skill-04 的 `save_dataframe()` 保存清洗后数据到 `outputs/ch01_data_cleaning/ch01_cleaned_data.csv`
7. 调用 Skill-04 的 `save_markdown()` 生成 `outputs/ch01_data_cleaning/report.md`（四段框架）
8. **检查标准**：`outputs/ch01_data_cleaning/` 下有 `ch01_cleaned_data.csv` + `report.md`

---

### Prompt-02：描述性统计与可视化

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-02 |
| **章节名称** | 描述性统计与可视化 |
| **输入数据** | `outputs/ch01_data_cleaning/ch01_cleaned_data.csv` |
| **核心产物** | `category_summary.csv`, `city_summary.csv`, `monthly_trend.csv`, 6 张 PNG |
| **后续依赖方** | Prompt-03, Prompt-04, Prompt-05 |
| **技能调用** | Skill-01 (data_loader), Skill-02 (visualizer), Skill-04 (output_manager) |

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-02 部分，理解分析目标
2. 调用 Skill-01 的 `load_preprocessed('ch01')` 加载清洗后数据
3. 使用 `df.describe()` 计算整体描述统计，调用 Skill-04 的 `save_dataframe()` 保存到 `outputs/ch02_descriptive_analysis/descriptive_stats.csv`
4. 按 Category 分组聚合（`df.groupby('Category').agg(...)`），保存到 `category_summary.csv`，绘制柱状图和饼图
5. 按 Customer_City 分组聚合，保存到 `city_summary.csv`，绘制城市对比柱状图
6. 创建城市×品类透视表（`df.pivot_table()`），调用 Skill-02 的 `plot_heatmap()` 绘制热力图
7. 按 Product_Name 分组，输出 Top 10 排名到 `product_ranking.csv`，绘制排名图
8. 按月聚合销售额（`df.resample('M')`），保存到 `monthly_trend.csv`，绘制月度趋势折线图
9. 绘制价格/销量分布箱线图
10. 调用 Skill-04 的 `save_markdown()` 生成 `outputs/ch02_descriptive_analysis/report.md`（四段框架）
11. **检查标准**：`outputs/ch02_descriptive_analysis/` 下有 6 个 CSV + 6 个 PNG + `report.md`

---

### Prompt-03：销售趋势预测

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-03 |
| **章节名称** | 销售趋势预测 |
| **输入数据** | `outputs/ch01_data_cleaning/ch01_cleaned_data.csv`, `outputs/ch02_descriptive_analysis/monthly_trend.csv` |
| **核心产物** | `forecast_results.csv`, `error_metrics.csv`, `forecast_chart.png` |
| **后续依赖方** | Prompt-05 |
| **技能调用** | Skill-01 (data_loader), Skill-03 (metrics), Skill-04 (output_manager) |

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-03 部分，理解预测目标
2. 调用 Skill-01 的 `load_preprocessed('ch01')` 加载清洗后数据
3. 按月聚合 Total_Sales_USD（`df.resample('M').sum()`），保存到 `outputs/ch03_sales_forecasting/monthly_sales.csv`
4. 绘制历史趋势折线图，保存到 `historical_trend.png`
5. 计算 SMA(3) 和 SMA(6) 移动平均，保存到 `moving_average.csv`，绘制对比图
6. 使用 `statsmodels.tsa.holtwinters.SimpleExpSmoothing`（α=0.3）拟合模型，预测未来 3 个月（2026-06 至 2026-08）
7. 使用留一法交叉验证计算 MAE 和 RMSE，调用 Skill-03 的 `calc_mae()` 和 `calc_rmse()`
8. 绘制历史趋势 + 预测曲线 + 95% 置信区间图，保存到 `forecast_chart.png`
9. 保存预测结果到 `forecast_results.csv`，误差指标到 `error_metrics.csv`
10. 调用 Skill-04 的 `save_markdown()` 生成 `outputs/ch03_sales_forecasting/report.md`（四段框架）
11. **检查标准**：`outputs/ch03_sales_forecasting/` 下有 4 个 CSV + 3 个 PNG + `report.md`；MAE ≤ 月均销售额 20%

---

### Prompt-04：价格弹性分析

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-04 |
| **章节名称** | 价格弹性分析 |
| **输入数据** | `outputs/ch01_data_cleaning/ch01_cleaned_data.csv` |
| **核心产物** | `price_elasticity.csv`, `category_elasticity.png`, `category_price_quantity.png` |
| **后续依赖方** | Prompt-05 |
| **技能调用** | Skill-01 (data_loader), Skill-04 (output_manager) |

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-04 部分，理解弹性分析目标
2. 调用 Skill-01 的 `load_preprocessed('ch01')` 加载清洗后数据
3. 绘制整体价格-销量散点图（含趋势线），保存到 `outputs/ch04_price_elasticity/price_quantity_scatter.png`
4. 按 Category 分组，对 Price_USD 和 Quantity_Sold 取自然对数
5. 使用 `numpy.polynomial.polynomial.polyfit` 进行对数-对数线性回归，斜率即为弹性系数
6. 计算各品类皮尔逊相关系数，按弹性分类标准（弹性 |E|>1、刚性 |E|<0.5、单位弹性 0.5≤|E|≤1）分类
7. 保存弹性系数表到 `price_elasticity.csv`
8. 绘制品类弹性系数柱状图（含阈值线）和品类散点图集
9. 调用 Skill-04 的 `save_markdown()` 生成 `outputs/ch04_price_elasticity/report.md`（四段框架）
10. **检查标准**：`outputs/ch04_price_elasticity/` 下有 1 个 CSV + 3 个 PNG + `report.md`；弹性分析覆盖 6 个品类

---

### Prompt-05：结论与业务建议

| 字段 | 内容 |
|------|------|
| **Prompt 编号** | Prompt-05 |
| **章节名称** | 结论与业务建议 |
| **输入数据** | ch01 清洗数据 + ch02 全部产物 + ch03 forecast_results.csv + ch04 price_elasticity.csv |
| **核心产物** | `key_metrics_summary.csv`, `category_recommendations.csv`, `region_recommendations.csv`, `pricing_recommendations.csv` |
| **后续依赖方** | 无（最终交付） |
| **技能调用** | Skill-01 (data_loader), Skill-04 (output_manager), Skill-05 (task_graph) |

**具体话术**：
1. 阅读 `docs/execution_prompts.md` 的 Prompt-05 部分，理解综合建议目标
2. 调用 Skill-05 的 `TaskGraph().get_status()` 验证全部前序任务已完成
3. 调用 Skill-01 的 `load_preprocessed('ch01')` 加载清洗后数据
4. 读取 ch02 的 `category_summary.csv`、`city_summary.csv`、`product_ranking.csv`、`monthly_trend.csv`
5. 读取 ch03 的 `forecast_results.csv` 和 ch04 的 `price_elasticity.csv`
6. 计算核心指标（总销售额、总销量、平均客单价、产品种类、城市数量），保存到 `key_metrics_summary.csv`
7. 基于品类表现 + 弹性系数，生成品类策略建议表 `category_recommendations.csv`（含优先级）
8. 基于城市表现，生成区域策略建议表 `region_recommendations.csv`（含优先级）
9. 基于弹性分类，生成定价策略建议表 `pricing_recommendations.csv`
10. 调用 Skill-04 的 `save_markdown()` 生成 `outputs/ch05_conclusions_and_recommendations/report.md`（四段框架，含品类/区域/定价三维度建议 + 局限性分析）
11. **检查标准**：`outputs/ch05_conclusions_and_recommendations/` 下有 4 个 CSV + `report.md`；建议覆盖 6 品类 + 5 城市

---

## 四、核心规则

| # | 规则 | 说明 |
|---|------|------|
| 1 | **严禁跳批** | 每个批次必须等前置依赖全部完成后再启动 |
| 2 | **数据不覆盖** | 每个章节产物写入独立的 `outputs/chXXX_*/` 目录 |
| 3 | **脚本双格式** | 每章提供 `.py` + `.ipynb`，逻辑一致 |
| 4 | **全局配置共享** | 所有脚本通过 `config.py` 统一路径和参数 |
| 5 | **章节报告必需** | 每章执行后必须生成 `outputs/chXXX/report.md` |
| 6 | **输出统一归档** | 所有产物统一放到 `outputs/chXXX/` 目录下 |

---

## 五、产物流转图

```
data/product_sales_dataset.csv
    │
    ▼ [Prompt-01]
outputs/ch01_data_cleaning/ch01_cleaned_data.csv
    │
    ├──────────────────────────────┐
    ▼ [Prompt-02]                  │
category_summary.csv              │
city_summary.csv                  │
product_ranking.csv               │
monthly_trend.csv ────────────────┤
    │                              │
    ├──────────────┐               │
    ▼ [Prompt-03]  │               │
forecast_results │               │
error_metrics    │               │
    │              │               │
    │     ┌────────┘               │
    │     ▼ [Prompt-04]            │
    │  price_elasticity.csv        │
    │     │                        │
    ├─────┼────────────────────────┘
    ▼ [Prompt-05]
key_metrics_summary.csv
category_recommendations.csv
region_recommendations.csv
pricing_recommendations.csv
report.md（最终交付）
```

---

## 六、进度检查

使用 Skill-05（task_graph）检查整体进度：

```python
from utils.task_graph import TaskGraph

tg = TaskGraph()
tg.print_status()

# 检查特定章节是否可执行
if tg.check_dependencies('ch03'):
    print("ch03 可以开始执行")
else:
    print("ch03 前置依赖未满足")
```

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-05-08 | 初始版本，4 批次 5 章节 |
