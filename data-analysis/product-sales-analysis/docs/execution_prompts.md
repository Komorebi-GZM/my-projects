# Product_Sales_Analysis — 执行 Prompt 文档

> 项目：Product_Sales_Analysis  
> 生成日期：2026-05-08  
> 章节数：5 章  
> 文档版本：v1.0  
> 配套文档：flow_design.md（研究设计）、project_convention.md（项目规范）

---

## 全局 Skill 库引用

以下 4 个 Skill 模块贯穿全流程，执行时必须调用：

| Skill ID | 模块名 | 路径 | 核心函数 | 调用时机 |
|----------|--------|------|----------|----------|
| Skill-01 | 标准数据加载器 | `src/utils/data_loader.py` | `load_raw_data()`, `load_preprocessed()` | 读取输入数据时 |
| Skill-02 | 标准可视化出图器 | `src/utils/visualizer.py` | `plot_time_series()`, `plot_heatmap()`, `plot_category_sales()` | 生成图表时 |
| Skill-03 | 标准评估指标计算器 | `src/utils/metrics.py` | `calc_mae()`, `calc_rmse()`, `calc_category_summary()` | 模型评估时 |
| Skill-04 | 标准输出产物管理器 | `src/utils/output_manager.py` | `ensure_dir()`, `save_dataframe()`, `save_figure()`, `save_markdown()` | 保存产物时 |

---

## Prompt-01: 数据清洗

### 一、任务概述

#### 1.1 本次任务是什么
对原始销售数据 `product_sales_dataset.csv`（1000 条记录、8 个字段）进行全面的数据质量检查和清洗，输出可直接用于下游分析的高质量数据集。

#### 1.2 从什么数据出发
- 原始数据：`data/product_sales_dataset.csv`（CSV 格式，1000 行 × 8 列）
- 字段：Product_ID, Product_Name, Category, Price_USD, Quantity_Sold, Total_Sales_USD, Order_Date, Customer_City

#### 1.3 可以采用什么方法
缺失值检测（`df.isnull().sum()`）、重复值检测（`df.duplicated().sum()`）、时间戳解析（`pd.to_datetime()`）、数据类型验证（`df.dtypes`）、描述性统计（`df.describe()`）

### 二、执行步骤（六子结构）

#### Step 1: 数据读取与结构探查
- **本步骤要做什么**：读取 CSV 原始数据，检查行列数、字段名、数据类型，建立数据基本认知
- **本步骤输出产物**：无独立产物（信息记录在 report.md 中）
- **具体操作指引**：
  1. 调用 Skill-01 的 `load_raw_data()` 加载数据
  2. 打印 `df.shape`、`df.columns`、`df.dtypes`
  3. 打印前 5 行 `df.head()`
- **代码框架**：
```python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config import *
from utils.data_loader import load_raw_data
from utils.output_manager import ensure_dir, save_dataframe, save_markdown

output_dir = os.path.join(OUTPUT_BASE, 'ch01_data_cleaning')
ensure_dir(output_dir)

df = load_raw_data()
print(f"数据形状: {df.shape}")
print(f"字段类型:\n{df.dtypes}")
print(f"前5行:\n{df.head()}")
```
- **本步骤完成后的检查标准**：
  1. 数据成功加载，shape 为 (1000, 8)
  2. 8 个字段名与预期一致

#### Step 2: 缺失值检测与统计
- **本步骤要做什么**：逐列检查缺失值数量和比例，判断是否需要处理
- **本步骤输出产物**：缺失值统计信息（记录在 report.md 中）
- **具体操作指引**：
  1. 使用 `df.isnull().sum()` 统计每列缺失值数量
  2. 使用 `df.isnull().mean()` 计算缺失比例
  3. 打印缺失值汇总表
- **代码框架**：
```python
missing = df.isnull().sum()
missing_pct = (df.isnull().mean() * 100).round(2)
missing_df = pd.DataFrame({'缺失数量': missing, '缺失比例(%)': missing_pct})
print(f"缺失值统计:\n{missing_df}")
```
- **本步骤完成后的检查标准**：
  1. 缺失值统计覆盖全部 8 个字段
  2. 如有缺失值，记录具体数量和比例

#### Step 3: 重复值检测
- **本步骤要做什么**：检查是否存在完全重复的记录行
- **本步骤输出产物**：重复值统计信息（记录在 report.md 中）
- **代码框架**：
```python
duplicates = df.duplicated().sum()
print(f"重复记录数: {duplicates}")
if duplicates > 0:
    df = df.drop_duplicates()
    print(f"去重后数据形状: {df.shape}")
```
- **本步骤完成后的检查标准**：
  1. 重复值数量已统计
  2. 如有重复值，已执行去重操作

#### Step 4: 时间戳解析与标准化
- **本步骤要做什么**：将 Order_Date 字段转换为 datetime 类型，提取日期范围
- **本步骤输出产物**：日期范围信息（记录在 report.md 中）
- **代码框架**：
```python
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
print(f"日期范围: {df['Order_Date'].min()} 至 {df['Order_Date'].max()}")
print(f"日期类型: {df['Order_Date'].dtype}")
```
- **本步骤完成后的检查标准**：
  1. Order_Date 类型为 datetime64
  2. 日期范围合理（2025-01 至 2026-05）

#### Step 5: 数据类型验证与描述统计
- **本步骤要做什么**：验证数值字段类型正确性，输出描述性统计
- **本步骤输出产物**：描述统计信息（记录在 report.md 中）
- **代码框架**：
```python
print(f"数据类型:\n{df.dtypes}")
print(f"\n描述统计:\n{df.describe()}")
print(f"\n唯一值统计:")
for col in ['Category', 'Customer_City', 'Product_Name']:
    print(f"  {col}: {df[col].nunique()} 个唯一值")
```
- **本步骤完成后的检查标准**：
  1. 数值字段为 int64 类型
  2. Category 有 6 个唯一值，Customer_City 有 5 个唯一值

#### Step 6: 清洗后数据保存与报告生成
- **本步骤要做什么**：保存清洗后数据集，生成四段框架 report.md
- **本步骤输出产物**：`ch01_cleaned_data.csv`、`report.md`
- **代码框架**：
```python
# 保存清洗后数据
save_dataframe(df, 'ch01_cleaned_data.csv', output_dir)

# 生成 report.md
report = f"""# ch01 数据清洗

## 背景
本章对原始销售数据 product_sales_dataset.csv 进行全面的数据质量检查和清洗。
数据包含 {df.shape[0]} 条记录、{df.shape[1]} 个字段，时间跨度 {df['Order_Date'].min().date()} 至 {df['Order_Date'].max().date()}。

## 分析方法
- 缺失值检测：逐列统计缺失数量和比例
- 重复值检测：检查完全重复的记录行
- 时间戳解析：将 Order_Date 转换为 datetime 类型
- 数据类型验证：确保数值字段为 int64，分类字段为 str

## 分析发现
- 数据形状：{df.shape[0]} 行 × {df.shape[1]} 列
- 缺失值：全部字段无缺失
- 重复值：无重复记录
- 日期范围：{df['Order_Date'].min().date()} 至 {df['Order_Date'].max().date()}
- 品类数量：{df['Category'].nunique()} 个（{', '.join(sorted(df['Category'].unique()))}）
- 城市数量：{df['Customer_City'].nunique()} 个（{', '.join(sorted(df['Customer_City'].unique()))}）
- 产品种类：{df['Product_Name'].nunique()} 种
- 总销售额：${df['Total_Sales_USD'].sum():,.0f}

## 小结
- 数据质量良好，无需额外清洗处理
- 产物清单：ch01_cleaned_data.csv
- 清洗后数据可供 ch02/ch03/ch04 直接使用
"""
save_markdown(report, 'report.md', output_dir)
print(f"[ch01] 数据清洗完成，产物保存至 {output_dir}")
```
- **本步骤完成后的检查标准**：
  1. `ch01_cleaned_data.csv` 已生成，行数 ≥ 990
  2. `report.md` 已生成，包含四段框架

### 三、产物总览与结构说明

#### 3.1 本章全部输出产物

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 清洗后数据集 | `ch01_cleaned_data.csv` | `outputs/ch01_data_cleaning/` | ch02/ch03/ch04 输入 |
| 章节执行报告 | `report.md` | `outputs/ch01_data_cleaning/` | 项目验收 |

#### 3.2 关键产物结构详解

**ch01_cleaned_data.csv**：
```
Product_ID(int), Product_Name(str), Category(str), Price_USD(int),
Quantity_Sold(int), Total_Sales_USD(int), Order_Date(datetime64), Customer_City(str)
```

### 四、产物后续优化方向

#### 4.1 当前方案的局限性
- 仅做了基础质量检查，未进行异常值深度检测（如 3σ、IQR）
- 未进行特征工程（如月份、星期等时间特征提取）

#### 4.2 可进一步优化的方向
- 增加 IQR 异常值检测，标记极端价格或销量记录
- 增加时间特征工程（年、月、季度、星期几）

### 五、异常处理与问题反馈机制

#### 5.1 需要向用户确认的问题清单
- 如发现缺失值比例 > 5%，需确认处理策略（删除/填充/标记）
- 如发现重复值，需确认是否直接去重

#### 5.2 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| CSV 编码错误 | 尝试 `encoding='latin-1'` 或 `'gbk'` |
| 日期解析失败 | 检查日期格式，使用 `format` 参数指定 |
| 数据行数不符 | 检查是否有空行或分隔符问题 |

---

## Prompt-02: 描述性统计与可视化

### 一、任务概述

#### 1.1 本次任务是什么
对清洗后的 1000 条销售记录进行多维度描述性统计分析，覆盖品类、城市、产品、时间四个维度，输出完整的统计表和可视化图表。

#### 1.2 从什么数据出发
- 清洗后数据：`outputs/ch01_data_cleaning/ch01_cleaned_data.csv`（1000 行 × 8 列）

#### 1.3 可以采用什么方法
分组聚合（`df.groupby().agg()`）、频数统计（`df.value_counts()`）、柱状图（`plt.bar()`）、饼图（`plt.pie()`）、热力图（`sns.heatmap()`）、折线图（`plt.plot()`）、箱线图（`sns.boxplot()`）

### 二、执行步骤（六子结构）

#### Step 1: 数据加载与验证
- **本步骤要做什么**：加载 ch01 清洗后的数据，验证完整性
- **本步骤输出产物**：无独立产物
- **代码框架**：
```python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from utils.config import *
from utils.data_loader import load_preprocessed
from utils.output_manager import ensure_dir, save_dataframe, save_figure, save_markdown

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

output_dir = os.path.join(OUTPUT_BASE, 'ch02_descriptive_analysis')
ensure_dir(output_dir)

df = load_preprocessed('ch01')
print(f"数据加载成功: {df.shape}")
assert df.shape[0] >= 990, "数据行数异常"
```

#### Step 2: 整体描述性统计
- **本步骤要做什么**：计算销售额、销量、价格的均值、中位数、标准差等统计量
- **本步骤输出产物**：`descriptive_stats.csv`
- **代码框架**：
```python
desc_stats = df[['Price_USD', 'Quantity_Sold', 'Total_Sales_USD']].describe()
desc_stats.loc['sum'] = df[['Price_USD', 'Quantity_Sold', 'Total_Sales_USD']].sum()
desc_stats.loc['cv'] = (desc_stats.loc['std'] / desc_stats.loc['mean'] * 100).round(2)
save_dataframe(desc_stats, 'descriptive_stats.csv', output_dir)
```

#### Step 3: 品类维度分析
- **本步骤要做什么**：按 Category 分组计算销售额/销量/订单数，绘制品类对比图和饼图
- **本步骤输出产物**：`category_summary.csv`、`category_sales_bar.png`、`category_sales_pie.png`
- **代码框架**：
```python
cat_summary = df.groupby('Category').agg(
    Total_Sales=('Total_Sales_USD', 'sum'),
    Avg_Price=('Price_USD', 'mean'),
    Total_Quantity=('Quantity_Sold', 'sum'),
    Order_Count=('Product_ID', 'count'),
    Avg_Order_Value=('Total_Sales_USD', 'mean')
).sort_values('Total_Sales', ascending=False).round(2)
save_dataframe(cat_summary, 'category_summary.csv', output_dir)

# 品类销售额柱状图
fig, ax = plt.subplots(figsize=PLT_CONFIG['figsize'])
cat_summary['Total_Sales'].plot(kind='bar', ax=ax, color=sns.color_palette('husl', 6))
ax.set_title('各品类总销售额', fontsize=PLT_CONFIG['font_size'])
ax.set_xlabel('品类')
ax.set_ylabel('销售额 (USD)')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
for i, v in enumerate(cat_summary['Total_Sales']):
    ax.text(i, v + 500, f'${v:,.0f}', ha='center', fontsize=9)
plt.tight_layout()
save_figure(fig, 'category_sales_bar.png', output_dir, PLT_CONFIG['dpi'])
plt.close()

# 品类占比饼图
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(cat_summary['Total_Sales'], labels=cat_summary.index, autopct='%1.1f%%',
       colors=sns.color_palette('husl', 6), startangle=90)
ax.set_title('品类销售额占比', fontsize=PLT_CONFIG['font_size'])
plt.tight_layout()
save_figure(fig, 'category_sales_pie.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 4: 城市维度分析
- **本步骤要做什么**：按 Customer_City 分组计算销售额/销量/订单数，绘制城市对比图
- **本步骤输出产物**：`city_summary.csv`、`city_sales_bar.png`
- **代码框架**：
```python
city_summary = df.groupby('Customer_City').agg(
    Total_Sales=('Total_Sales_USD', 'sum'),
    Avg_Price=('Price_USD', 'mean'),
    Total_Quantity=('Quantity_Sold', 'sum'),
    Order_Count=('Product_ID', 'count')
).sort_values('Total_Sales', ascending=False).round(2)
save_dataframe(city_summary, 'city_summary.csv', output_dir)

fig, ax = plt.subplots(figsize=PLT_CONFIG['figsize'])
city_summary['Total_Sales'].plot(kind='bar', ax=ax, color=sns.color_palette('Set2', 5))
ax.set_title('各城市总销售额', fontsize=PLT_CONFIG['font_size'])
ax.set_xlabel('城市')
ax.set_ylabel('销售额 (USD)')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
for i, v in enumerate(city_summary['Total_Sales']):
    ax.text(i, v + 500, f'${v:,.0f}', ha='center', fontsize=9)
plt.tight_layout()
save_figure(fig, 'city_sales_bar.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 5: 城市-品类交叉分析
- **本步骤要做什么**：创建城市×品类透视表，绘制热力图
- **本步骤输出产物**：`city_category_heatmap.png`
- **代码框架**：
```python
pivot = df.pivot_table(values='Total_Sales_USD', index='Customer_City',
                       columns='Category', aggfunc='sum').fillna(0)
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(pivot, annot=True, fmt=',.0f', cmap='YlOrRd', ax=ax)
ax.set_title('城市-品类销售额热力图', fontsize=PLT_CONFIG['font_size'])
plt.tight_layout()
save_figure(fig, 'city_category_heatmap.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 6: 产品维度分析
- **本步骤要做什么**：按 Product_Name 分组计算销售额/销量，输出 Top 10 和 Bottom 10 排名
- **本步骤输出产物**：`product_ranking.csv`、`product_ranking.png`
- **代码框架**：
```python
prod_rank = df.groupby('Product_Name').agg(
    Total_Sales=('Total_Sales_USD', 'sum'),
    Total_Quantity=('Quantity_Sold', 'sum'),
    Avg_Price=('Price_USD', 'mean'),
    Order_Count=('Product_ID', 'count')
).sort_values('Total_Sales', ascending=False).round(2)
save_dataframe(prod_rank, 'product_ranking.csv', output_dir)

# Top 10 产品柱状图
fig, ax = plt.subplots(figsize=(12, 6))
top10 = prod_rank.head(10)
top10['Total_Sales'].plot(kind='barh', ax=ax, color=sns.color_palette('viridis', 10))
ax.set_title('产品销售额 Top 10', fontsize=PLT_CONFIG['font_size'])
ax.set_xlabel('销售额 (USD)')
ax.invert_yaxis()
plt.tight_layout()
save_figure(fig, 'product_ranking.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 7: 时间维度分析
- **本步骤要做什么**：按月聚合销售额，绘制月度趋势图
- **本步骤输出产物**：`monthly_trend.csv`、`monthly_trend.png`
- **代码框架**：
```python
df['Month'] = df['Order_Date'].dt.to_period('M')
monthly = df.groupby('Month').agg(
    Total_Sales=('Total_Sales_USD', 'sum'),
    Total_Quantity=('Quantity_Sold', 'sum'),
    Order_Count=('Product_ID', 'count')
).reset_index()
monthly['Month'] = monthly['Month'].astype(str)
save_dataframe(monthly, 'monthly_trend.csv', output_dir)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly['Month'], monthly['Total_Sales'], marker='o', linewidth=2, markersize=6)
ax.set_title('月度销售额趋势', fontsize=PLT_CONFIG['font_size'])
ax.set_xlabel('月份')
ax.set_ylabel('销售额 (USD)')
plt.xticks(rotation=45)
plt.tight_layout()
save_figure(fig, 'monthly_trend.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 8: 价格-销量分布分析
- **本步骤要做什么**：绘制价格和销量的箱线图，展示分布特征
- **本步骤输出产物**：`price_boxplot.png`
- **代码框架**：
```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.boxplot(y=df['Price_USD'], ax=axes[0], color='steelblue')
axes[0].set_title('价格分布', fontsize=PLT_CONFIG['font_size'])
sns.boxplot(y=df['Quantity_Sold'], ax=axes[1], color='coral')
axes[1].set_title('销量分布', fontsize=PLT_CONFIG['font_size'])
plt.tight_layout()
save_figure(fig, 'price_boxplot.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 9: 综合分析报告生成
- **本步骤要做什么**：汇总所有发现，生成四段框架 report.md
- **本步骤输出产物**：`report.md`
- **本步骤完成后的检查标准**：
  1. report.md 包含背景、分析方法、分析发现、小结四段
  2. 关键数据点（总销售额、品类排名、城市排名）已写入报告

### 三、产物总览与结构说明

#### 3.1 本章全部输出产物

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 描述性统计表 | `descriptive_stats.csv` | `outputs/ch02_descriptive_analysis/` | 报告表格 |
| 品类销售汇总表 | `category_summary.csv` | `outputs/ch02_descriptive_analysis/` | ch05 输入 |
| 城市销售汇总表 | `city_summary.csv` | `outputs/ch02_descriptive_analysis/` | ch05 输入 |
| 产品销售排名表 | `product_ranking.csv` | `outputs/ch02_descriptive_analysis/` | ch05 输入 |
| 月度趋势数据 | `monthly_trend.csv` | `outputs/ch02_descriptive_analysis/` | ch03 输入 |
| 品类销售额柱状图 | `category_sales_bar.png` | `outputs/ch02_descriptive_analysis/` | 报告配图 |
| 品类占比饼图 | `category_sales_pie.png` | `outputs/ch02_descriptive_analysis/` | 报告配图 |
| 城市销售额柱状图 | `city_sales_bar.png` | `outputs/ch02_descriptive_analysis/` | 报告配图 |
| 城市-品类热力图 | `city_category_heatmap.png` | `outputs/ch02_descriptive_analysis/` | 报告配图 |
| 产品销售排名图 | `product_ranking.png` | `outputs/ch02_descriptive_analysis/` | 报告配图 |
| 月度趋势图 | `monthly_trend.png` | `outputs/ch02_descriptive_analysis/` | ch03 参考 |
| 价格分布箱线图 | `price_boxplot.png` | `outputs/ch02_descriptive_analysis/` | 报告配图 |
| 章节执行报告 | `report.md` | `outputs/ch02_descriptive_analysis/` | 项目验收 |

### 四、产物后续优化方向

#### 4.1 当前方案的局限性
- 描述性统计仅覆盖单维度分析，未进行多变量交叉深度分析
- 可视化为静态图表，不支持交互式探索

#### 4.2 可进一步优化的方向
- 增加交互式 Plotly 图表
- 增加帕累托分析（80/20 法则）
- 增加同比/环比增长率计算

### 五、异常处理与问题反馈机制

#### 5.1 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| 中文字体显示为方块 | 安装 SimHei 字体或使用 `Noto Sans CJK SC` |
| 图表保存空白 | 确认使用 `matplotlib.use('Agg')` 后端 |
| 聚合结果为空 | 检查分组字段是否有 NaN |

---

## Prompt-03: 销售趋势预测

### 一、任务概述

#### 1.1 本次任务是什么
基于月度销售额数据，使用统计方法（移动平均、指数平滑）预测未来 3 个月（2026-06 至 2026-08）的销售趋势，并评估预测准确性。

#### 1.2 从什么数据出发
- 清洗后数据：`outputs/ch01_data_cleaning/ch01_cleaned_data.csv`
- 月度趋势数据：`outputs/ch02_descriptive_analysis/monthly_trend.csv`

#### 1.3 可以采用什么方法
简单移动平均 SMA（窗口 3/6）、指数平滑 SES（α=0.3）、MAE/RMSE 误差评估、交叉验证

### 二、执行步骤（六子结构）

#### Step 1: 数据加载与月度聚合
- **本步骤要做什么**：加载清洗数据，按月聚合 Total_Sales_USD，生成时序数据
- **本步骤输出产物**：`monthly_sales.csv`
- **代码框架**：
```python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils.config import *
from utils.data_loader import load_preprocessed
from utils.output_manager import ensure_dir, save_dataframe, save_figure, save_markdown

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

output_dir = os.path.join(OUTPUT_BASE, 'ch03_sales_forecasting')
ensure_dir(output_dir)

df = load_preprocessed('ch01')
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
monthly = df.set_index('Order_Date').resample('M')['Total_Sales_USD'].sum()
monthly.index = monthly.index.to_period('M')
monthly_df = monthly.reset_index()
monthly_df.columns = ['Month', 'Total_Sales']
monthly_df['Month'] = monthly_df['Month'].astype(str)
save_dataframe(monthly_df, 'monthly_sales.csv', output_dir)
print(f"月度数据: {len(monthly_df)} 个月")
```

#### Step 2: 历史趋势可视化
- **本步骤要做什么**：绘制月度销售额折线图，展示历史趋势
- **本步骤输出产物**：`historical_trend.png`
- **代码框架**：
```python
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly_df['Month'], monthly_df['Total_Sales'], marker='o', linewidth=2)
ax.set_title('月度销售额历史趋势', fontsize=PLT_CONFIG['font_size'])
ax.set_xlabel('月份')
ax.set_ylabel('销售额 (USD)')
ax.axhline(y=monthly_df['Total_Sales'].mean(), color='red', linestyle='--', alpha=0.5, label=f'均值 ${monthly_df["Total_Sales"].mean():,.0f}')
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
save_figure(fig, 'historical_trend.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 3: 移动平均计算与可视化
- **本步骤要做什么**：计算 SMA(3) 和 SMA(6)，绘制对比图
- **本步骤输出产物**：`moving_average.csv`、`moving_average_comparison.png`
- **代码框架**：
```python
monthly_df['SMA_3'] = monthly_df['Total_Sales'].rolling(window=3).mean().round(0)
monthly_df['SMA_6'] = monthly_df['Total_Sales'].rolling(window=6).mean().round(0)
save_dataframe(monthly_df, 'moving_average.csv', output_dir)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly_df['Month'], monthly_df['Total_Sales'], marker='o', label='实际销售额', linewidth=2)
ax.plot(monthly_df['Month'], monthly_df['SMA_3'], label='SMA(3)', linewidth=1.5)
ax.plot(monthly_df['Month'], monthly_df['SMA_6'], label='SMA(6)', linewidth=1.5)
ax.set_title('移动平均对比', fontsize=PLT_CONFIG['font_size'])
ax.set_xlabel('月份')
ax.set_ylabel('销售额 (USD)')
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
save_figure(fig, 'moving_average_comparison.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 4: 指数平滑预测
- **本步骤要做什么**：使用 SimpleExpSmoothing 进行未来 3 个月预测
- **本步骤输出产物**：预测值（保存到 forecast_results.csv）
- **代码框架**：
```python
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

# 拟合 SES 模型
values = monthly_df['Total_Sales'].values
model = SimpleExpSmoothing(values, initialization_method='estimated')
fit = model.fit(smoothing_level=0.3, optimized=False)

# 预测未来 3 个月
forecast = fit.forecast(3)
forecast_months = ['2026-06', '2026-07', '2026-08']

# 计算历史误差（留一法交叉验证）
errors = []
for i in range(3, len(values)):
    train = values[:i]
    m = SimpleExpSmoothing(train, initialization_method='estimated')
    f = m.fit(smoothing_level=0.3, optimized=False)
    pred = f.forecast(1)[0]
    errors.append(abs(pred - values[i]))

mae = np.mean(errors)
rmse = np.sqrt(np.mean([e**2 for e in errors]))
mean_sales = np.mean(values)

print(f"MAE: ${mae:,.0f} ({mae/mean_sales*100:.1f}% of mean)")
print(f"RMSE: ${rmse:,.0f}")
print(f"预测值: {forecast}")
```

#### Step 5: 预测结果可视化
- **本步骤要做什么**：绘制历史趋势 + 预测曲线图，含置信区间
- **本步骤输出产物**：`forecast_chart.png`、`forecast_results.csv`、`error_metrics.csv`
- **代码框架**：
```python
# 保存预测结果
forecast_df = pd.DataFrame({
    'Month': forecast_months,
    'Predicted_Sales': forecast.round(0),
    'Lower_Bound': (forecast - 1.96 * rmse).round(0),
    'Upper_Bound': (forecast + 1.96 * rmse).round(0)
})
save_dataframe(forecast_df, 'forecast_results.csv', output_dir)

# 保存误差指标
error_df = pd.DataFrame({
    'Metric': ['MAE', 'RMSE', 'MAE_Pct', 'Mean_Sales'],
    'Value': [round(mae, 0), round(rmse, 0), round(mae/mean_sales*100, 1), round(mean_sales, 0)]
})
save_dataframe(error_df, 'error_metrics.csv', output_dir)

# 绘制预测图
all_months = list(monthly_df['Month']) + forecast_months
all_values = list(monthly_df['Total_Sales']) + list(forecast)
all_lower = list(monthly_df['Total_Sales']) + list(forecast - 1.96 * rmse)
all_upper = list(monthly_df['Total_Sales']) + list(forecast + 1.96 * rmse)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(all_months[:len(monthly_df)], all_values[:len(monthly_df)], marker='o', label='历史数据', linewidth=2)
ax.plot(all_months[len(monthly_df):], all_values[len(monthly_df):], marker='s', label='预测值', linewidth=2, color='red', linestyle='--')
ax.fill_between(all_months[len(monthly_df)-1:], all_lower[len(monthly_df)-1:], all_upper[len(monthly_df)-1:], alpha=0.2, color='red', label='95% 置信区间')
ax.axvline(x='2026-05', color='gray', linestyle=':', alpha=0.7)
ax.set_title('销售额预测（未来 3 个月）', fontsize=PLT_CONFIG['font_size'])
ax.set_xlabel('月份')
ax.set_ylabel('销售额 (USD)')
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
save_figure(fig, 'forecast_chart.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 6: 分析报告生成
- **本步骤要做什么**：生成四段框架 report.md，汇总预测结果
- **本步骤输出产物**：`report.md`
- **本步骤完成后的检查标准**：
  1. report.md 包含预测值和误差指标
  2. MAE ≤ 月均销售额的 20%

### 三、产物总览与结构说明

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 月度销售额数据 | `monthly_sales.csv` | `outputs/ch03_sales_forecasting/` | 分析基础 |
| 移动平均数据 | `moving_average.csv` | `outputs/ch03_sales_forecasting/` | 参考 |
| 预测结果表 | `forecast_results.csv` | `outputs/ch03_sales_forecasting/` | ch05 输入 |
| 误差评估表 | `error_metrics.csv` | `outputs/ch03_sales_forecasting/` | 模型评估 |
| 历史趋势图 | `historical_trend.png` | `outputs/ch03_sales_forecasting/` | 报告配图 |
| 移动平均对比图 | `moving_average_comparison.png` | `outputs/ch03_sales_forecasting/` | 报告配图 |
| 预测结果图 | `forecast_chart.png` | `outputs/ch03_sales_forecasting/` | 报告配图 |
| 章节执行报告 | `report.md` | `outputs/ch03_sales_forecasting/` | 项目验收 |

### 四、产物后续优化方向

#### 4.1 当前方案的局限性
- 数据量仅 17 个月，统计方法可能不够稳健
- SES 假设趋势平稳，无法捕捉增长/下降趋势

#### 4.2 可进一步优化的方向
- 使用 Holt 线性趋势法捕捉趋势
- 使用 Prophet 自动检测季节性
- 增加多步滚动验证提升评估可靠性

### 五、异常处理与问题反馈机制

#### 5.1 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| statsmodels 未安装 | `pip install statsmodels` |
| MAE 超过 20% 阈值 | 尝试调整 α 值或使用 Holt 方法 |
| 预测值为负 | 截断为 0 |

---

## Prompt-04: 价格弹性分析

### 一、任务概述

#### 1.1 本次任务是什么
分析同一产品在不同价格水平下的销量变化，通过对数回归计算各品类的价格弹性系数，为定价策略提供量化依据。

#### 1.2 从什么数据出发
- 清洗后数据：`outputs/ch01_data_cleaning/ch01_cleaned_data.csv`

#### 1.3 可以采用什么方法
散点图分析、对数-对数线性回归、皮尔逊相关系数、品类分组分析

### 二、执行步骤（六子结构）

#### Step 1: 数据加载与验证
- **本步骤要做什么**：加载清洗数据，确认 Price_USD 和 Quantity_Sold 字段完整
- **本步骤输出产物**：无独立产物
- **代码框架**：
```python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from utils.config import *
from utils.data_loader import load_preprocessed
from utils.output_manager import ensure_dir, save_dataframe, save_figure, save_markdown

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

output_dir = os.path.join(OUTPUT_BASE, 'ch04_price_elasticity')
ensure_dir(output_dir)

df = load_preprocessed('ch01')
print(f"数据加载成功: {df.shape}")
print(f"价格范围: ${df['Price_USD'].min()} - ${df['Price_USD'].max()}")
print(f"销量范围: {df['Quantity_Sold'].min()} - {df['Quantity_Sold'].max()}")
```

#### Step 2: 整体价格-销量散点图
- **本步骤要做什么**：绘制所有数据的价格-销量散点图，观察整体关系
- **本步骤输出产物**：`price_quantity_scatter.png`
- **代码框架**：
```python
fig, ax = plt.subplots(figsize=PLT_CONFIG['figsize'])
ax.scatter(df['Price_USD'], df['Quantity_Sold'], alpha=0.5, s=30, c='steelblue')
ax.set_xlabel('价格 (USD)', fontsize=PLT_CONFIG['font_size'])
ax.set_ylabel('销量', fontsize=PLT_CONFIG['font_size'])
ax.set_title('价格-销量散点图（整体）', fontsize=PLT_CONFIG['font_size'])
# 添加趋势线
z = np.polyfit(df['Price_USD'], df['Quantity_Sold'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['Price_USD'].min(), df['Price_USD'].max(), 100)
ax.plot(x_line, p(x_line), 'r--', alpha=0.8, label=f'趋势线 (斜率={z[0]:.4f})')
ax.legend()
plt.tight_layout()
save_figure(fig, 'price_quantity_scatter.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 3: 品类分组弹性系数计算
- **本步骤要做什么**：按品类分组，对价格和销量取对数后进行线性回归，斜率即为弹性系数
- **本步骤输出产物**：`price_elasticity.csv`
- **代码框架**：
```python
from numpy.polynomial.polynomial import polyfit

elasticity_results = []
for cat in CATEGORY_LIST:
    cat_df = df[df['Category'] == cat].copy()
    if len(cat_df) < 10:
        continue
    # 对数转换
    cat_df = cat_df[cat_df['Price_USD'] > 0]
    cat_df = cat_df[cat_df['Quantity_Sold'] > 0]
    cat_df['log_price'] = np.log(cat_df['Price_USD'])
    cat_df['log_qty'] = np.log(cat_df['Quantity_Sold'])
    
    if len(cat_df) > 5:
        corr = cat_df['log_price'].corr(cat_df['log_qty'])
        try:
            # 对数-对数线性回归
            b, a = polyfit(cat_df['log_price'], cat_df['log_qty'], 1)
            elasticity = b  # 斜率即为弹性系数
            etype = '弹性' if elasticity < -1 else ('刚性' if elasticity > -0.5 else '单位弹性')
            elasticity_results.append({
                'Category': cat,
                'Elasticity': round(elasticity, 4),
                'Correlation': round(corr, 4),
                'N': len(cat_df),
                'Type': etype
            })
        except Exception as e:
            print(f"[警告] {cat} 回归失败: {e}")

elasticity_df = pd.DataFrame(elasticity_results)
save_dataframe(elasticity_df, 'price_elasticity.csv', output_dir)
print(f"\n弹性系数表:\n{elasticity_df.to_string(index=False)}")
```

#### Step 4: 品类弹性可视化
- **本步骤要做什么**：绘制各品类弹性系数柱状图和品类散点图集
- **本步骤输出产物**：`category_elasticity.png`、`category_price_quantity.png`
- **代码框架**：
```python
# 弹性系数柱状图
valid_df = elasticity_df.dropna(subset=['Elasticity'])
fig, ax = plt.subplots(figsize=PLT_CONFIG['figsize'])
colors = ['#e74c3c' if e < -1 else '#f39c12' if e < -0.5 else '#27ae60' for e in valid_df['Elasticity']]
bars = ax.barh(valid_df['Category'], valid_df['Elasticity'], color=colors)
ax.set_xlabel('价格弹性系数', fontsize=PLT_CONFIG['font_size'])
ax.set_title('各品类价格弹性系数', fontsize=PLT_CONFIG['font_size'])
ax.axvline(x=-1, color='red', linestyle='--', alpha=0.5, label='弹性阈值(-1)')
ax.axvline(x=-0.5, color='orange', linestyle='--', alpha=0.5, label='刚性阈值(-0.5)')
ax.legend()
for bar, val in zip(bars, valid_df['Elasticity']):
    ax.text(val + 0.02 if val >= 0 else val - 0.02, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', fontsize=10)
plt.tight_layout()
save_figure(fig, 'category_elasticity.png', output_dir, PLT_CONFIG['dpi'])
plt.close()

# 品类散点图集
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()
for i, cat in enumerate(CATEGORY_LIST):
    cat_df = df[df['Category'] == cat]
    axes[i].scatter(cat_df['Price_USD'], cat_df['Quantity_Sold'], alpha=0.6, s=25, c='steelblue')
    axes[i].set_title(cat, fontsize=11)
    axes[i].set_xlabel('价格')
    axes[i].set_ylabel('销量')
plt.suptitle('各品类价格-销量关系', fontsize=14, y=1.02)
plt.tight_layout()
save_figure(fig, 'category_price_quantity.png', output_dir, PLT_CONFIG['dpi'])
plt.close()
```

#### Step 5: 分析报告生成
- **本步骤要做什么**：生成四段框架 report.md
- **本步骤输出产物**：`report.md`
- **本步骤完成后的检查标准**：
  1. 弹性分析覆盖全部 6 个品类
  2. 每个品类有明确的弹性分类

### 三、产物总览与结构说明

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 价格弹性系数表 | `price_elasticity.csv` | `outputs/ch04_price_elasticity/` | ch05 输入 |
| 整体散点图 | `price_quantity_scatter.png` | `outputs/ch04_price_elasticity/` | 报告配图 |
| 品类弹性柱状图 | `category_elasticity.png` | `outputs/ch04_price_elasticity/` | 报告配图 |
| 品类散点图集 | `category_price_quantity.png` | `outputs/ch04_price_elasticity/` | 报告配图 |
| 章节执行报告 | `report.md` | `outputs/ch04_price_elasticity/` | 项目验收 |

### 四、产物后续优化方向

#### 4.1 当前方案的局限性
- 数据中同一产品在不同时间的价格变化有限，弹性估计可能不精确
- 未控制其他变量（如季节性、促销活动）的影响

#### 4.2 可进一步优化的方向
- 使用多元回归控制混杂变量
- 按产品级别（而非品类级别）计算弹性
- 增加价格分位数分析

### 五、异常处理与问题反馈机制

#### 5.1 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| 某品类样本量 < 10 | 跳过该品类，在报告中标注 |
| 对数转换出现 -inf | 过滤 Price_USD ≤ 0 或 Quantity_Sold ≤ 0 的记录 |
| 回归系数异常大 | 检查数据是否有极端值，考虑截断处理 |

---

## Prompt-05: 结论与业务建议

### 一、任务概述

#### 1.1 本次任务是什么
综合 ch02 描述性统计、ch03 销售预测、ch04 价格弹性分析的全部发现，输出结构化的业务建议报告，涵盖品类策略、区域策略、定价策略三个维度。

#### 1.2 从什么数据出发
- 清洗后数据：`outputs/ch01_data_cleaning/ch01_cleaned_data.csv`
- 品类汇总：`outputs/ch02_descriptive_analysis/category_summary.csv`
- 城市汇总：`outputs/ch02_descriptive_analysis/city_summary.csv`
- 产品排名：`outputs/ch02_descriptive_analysis/product_ranking.csv`
- 月度趋势：`outputs/ch02_descriptive_analysis/monthly_trend.csv`
- 预测结果：`outputs/ch03_sales_forecasting/forecast_results.csv`
- 弹性系数：`outputs/ch04_price_elasticity/price_elasticity.csv`

#### 1.3 可以采用什么方法
跨章节数据整合、关键指标提取、结构化归纳、优先级排序

### 二、执行步骤（六子结构）

#### Step 1: 全部章节产物加载与验证
- **本步骤要做什么**：读取 ch02/ch03/ch04 的核心产物，验证文件完整性
- **本步骤输出产物**：无独立产物
- **代码框架**：
```python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
import numpy as np
from utils.config import *
from utils.data_loader import load_preprocessed
from utils.output_manager import ensure_dir, save_dataframe, save_markdown

output_dir = os.path.join(OUTPUT_BASE, 'ch05_conclusions_and_recommendations')
ensure_dir(output_dir)

df = load_preprocessed('ch01')

# 加载前序章节产物
ch02_dir = os.path.join(OUTPUT_BASE, 'ch02_descriptive_analysis')
ch03_dir = os.path.join(OUTPUT_BASE, 'ch03_sales_forecasting')
ch04_dir = os.path.join(OUTPUT_BASE, 'ch04_price_elasticity')

cat_summary = pd.read_csv(os.path.join(ch02_dir, 'category_summary.csv'), index_col=0)
city_summary = pd.read_csv(os.path.join(ch02_dir, 'city_summary.csv'), index_col=0)
prod_rank = pd.read_csv(os.path.join(ch02_dir, 'product_ranking.csv'), index_col=0)
monthly = pd.read_csv(os.path.join(ch02_dir, 'monthly_trend.csv'))
forecast = pd.read_csv(os.path.join(ch03_dir, 'forecast_results.csv'))
elasticity = pd.read_csv(os.path.join(ch04_dir, 'price_elasticity.csv'))

print(f"品类汇总: {len(cat_summary)} 行")
print(f"城市汇总: {len(city_summary)} 行")
print(f"预测结果: {len(forecast)} 行")
print(f"弹性系数: {len(elasticity)} 行")
```

#### Step 2: 核心指标汇总
- **本步骤要做什么**：计算总销售额、总销量、平均客单价等核心指标
- **本步骤输出产物**：`key_metrics_summary.csv`
- **代码框架**：
```python
metrics = {
    '指标': ['总销售额(USD)', '总销量(件)', '平均客单价(USD)', '产品种类', '覆盖城市数', '数据月数'],
    '值': [
        df['Total_Sales_USD'].sum(),
        df['Quantity_Sold'].sum(),
        round(df['Total_Sales_USD'].mean(), 0),
        df['Product_Name'].nunique(),
        df['Customer_City'].nunique(),
        df['Order_Date'].dt.to_period('M').nunique()
    ]
}
metrics_df = pd.DataFrame(metrics)
save_dataframe(metrics_df, 'key_metrics_summary.csv', output_dir)
print(f"\n核心指标:\n{metrics_df.to_string(index=False)}")
```

#### Step 3: 品类策略提炼
- **本步骤要做什么**：基于品类表现和弹性分析，提出品类运营建议
- **本步骤输出产物**：`category_recommendations.csv`
- **代码框架**：
```python
cat_rec = []
for _, row in cat_summary.iterrows():
    cat = row.name
    sales = row['Total_Sales']
    qty = row['Total_Quantity']
    avg_price = row['Avg_Price']
    
    # 查找弹性系数
    elas_row = elasticity[elasticity['Category'] == cat]
    elas_type = elas_row['Type'].values[0] if len(elas_row) > 0 else '未知'
    elas_val = elas_row['Elasticity'].values[0] if len(elas_row) > 0 else None
    
    # 策略建议
    if sales >= cat_summary['Total_Sales'].median():
        strategy = '重点投入：增加营销资源和库存'
        priority = '高'
    else:
        strategy = '优化提升：分析低销原因，调整产品组合'
        priority = '中'
    
    cat_rec.append({
        'Category': cat,
        'Total_Sales': sales,
        'Total_Quantity': qty,
        'Avg_Price': avg_price,
        'Elasticity_Type': elas_type,
        'Strategy': strategy,
        'Priority': priority
    })

cat_rec_df = pd.DataFrame(cat_rec)
save_dataframe(cat_rec_df, 'category_recommendations.csv', output_dir)
```

#### Step 4: 区域策略提炼
- **本步骤要做什么**：基于城市表现，提出区域资源分配建议
- **本步骤输出产物**：`region_recommendations.csv`
- **代码框架**：
```python
region_rec = []
for _, row in city_summary.iterrows():
    city = row.name
    sales = row['Total_Sales']
    avg_price = row['Avg_Price']
    
    if sales >= city_summary['Total_Sales'].median():
        strategy = '核心市场：维持投入，深耕客户关系'
        priority = '高'
    else:
        strategy = '拓展市场：加大推广力度，提升品牌认知'
        priority = '中'
    
    region_rec.append({
        'City': city,
        'Total_Sales': sales,
        'Avg_Price': avg_price,
        'Strategy': strategy,
        'Priority': priority
    })

region_rec_df = pd.DataFrame(region_rec)
save_dataframe(region_rec_df, 'region_recommendations.csv', output_dir)
```

#### Step 5: 定价策略提炼
- **本步骤要做什么**：基于弹性分析结果，提出定价调整建议
- **本步骤输出产物**：`pricing_recommendations.csv`
- **代码框架**：
```python
pricing_rec = []
for _, row in elasticity.iterrows():
    cat = row['Category']
    elas = row['Elasticity']
    etype = row['Type']
    
    if etype == '弹性':
        strategy = '可考虑适度降价促销，以量换价'
    elif etype == '刚性':
        strategy = '维持当前价格，可尝试小幅提价测试'
    else:
        strategy = '价格与销量平衡，谨慎调整'
    
    pricing_rec.append({
        'Category': cat,
        'Elasticity': elas,
        'Type': etype,
        'Pricing_Strategy': strategy
    })

pricing_rec_df = pd.DataFrame(pricing_rec)
save_dataframe(pricing_rec_df, 'pricing_recommendations.csv', output_dir)
```

#### Step 6: 综合报告生成
- **本步骤要做什么**：汇总全部发现和建议，生成最终 report.md
- **本步骤输出产物**：`report.md`
- **本步骤完成后的检查标准**：
  1. report.md 包含品类/区域/定价三维度建议
  2. 每条建议有数据支撑
  3. 局限性分析完整

### 三、产物总览与结构说明

| 产物名称 | 文件名 | 路径 | 后续使用 |
|----------|--------|------|----------|
| 核心指标总览表 | `key_metrics_summary.csv` | `outputs/ch05_conclusions_and_recommendations/` | 快速查阅 |
| 品类策略建议表 | `category_recommendations.csv` | `outputs/ch05_conclusions_and_recommendations/` | 执行参考 |
| 区域策略建议表 | `region_recommendations.csv` | `outputs/ch05_conclusions_and_recommendations/` | 执行参考 |
| 定价策略建议表 | `pricing_recommendations.csv` | `outputs/ch05_conclusions_and_recommendations/` | 执行参考 |
| 章节执行报告 | `report.md` | `outputs/ch05_conclusions_and_recommendations/` | 最终交付 |

### 四、产物后续优化方向

#### 4.1 当前方案的局限性
- 数据量有限（1000 条），结论的统计显著性不足
- 无 Customer_ID，无法进行用户维度分析
- 无成本/利润数据，策略建议仅基于营收视角

#### 4.2 可进一步优化的方向
- 增加更多数据源（用户行为、竞品数据）
- 引入 A/B 测试验证定价策略效果
- 建立自动化仪表板实时监控关键指标

### 五、异常处理与问题反馈机制

#### 5.1 常见异常场景与处理策略
| 异常场景 | 处理策略 |
|---------|---------|
| 前序章节产物缺失 | 提示用户先运行对应章节 |
| CSV 列名不匹配 | 检查 index_col 参数，灵活处理 |
| 弹性系数表为空 | 提示 ch04 未执行或执行失败 |

---

## 附录：执行顺序与并行策略

```
Batch 1: ch01 数据清洗（串行，必须先完成）
    │
Batch 2: ch02 描述性统计与可视化（串行，依赖 ch01）
    │
Batch 3: ch03 销售趋势预测 + ch04 价格弹性分析（可并行）
    │           │
    │           └── 两者均依赖 ch01 + ch02，互不依赖
    │
Batch 4: ch05 结论与业务建议（串行，依赖 ch02 + ch03 + ch04）
```

**推荐执行命令**：
```bash
cd Product_Sales_Analysis
conda activate py310

# Batch 1
python src/ch01_data_cleaning/script.py

# Batch 2
python src/ch02_descriptive_analysis/script.py

# Batch 3（可并行）
python src/ch03_sales_forecasting/script.py &
python src/ch04_price_elasticity/script.py &
wait

# Batch 4
python src/ch05_conclusions_and_recommendations/script.py
```

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-05-08 | 初始版本，5 章节完整执行指令 |
