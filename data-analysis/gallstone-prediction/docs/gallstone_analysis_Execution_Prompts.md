# gallstone_analysis — 执行 Prompt 文档

## 文档说明

本文档为**胆结石数据集全流程标准化分析执行指南**，覆盖从探索性数据分析到建模预测再到总结报告的完整分析链条。每个章节的 Prompt 均设计为**自包含、可独立执行**的单元，可直接复制到 AI 助手中执行，也可由数据分析师参照手动操作。

### 适用环境
- **Python 版本**: 3.10（conda 环境 `py310`）
- **执行方式**: 每个章节均提供 **.py + .ipynb 双格式**脚本，按章节编号命名，支持批量执行和交互式调试
- **环境管理**: 使用 conda 环境 `py310`，激活命令 `conda activate py310`，通过 `pip install -r requirements.txt` 安装全部依赖。**禁止创建 venv 目录**
- **依赖库清单**: 见 `requirements.txt`

### 全局路径配置

```python
import os
import sys

# === 路径配置 ===
DATA_DIR = "data/"
RAW_DATA_FILE = os.path.join(DATA_DIR, "dataset-uci.xlsx")
OUTPUT_BASE = "outputs/"

# === 章节目录映射 ===
CHAPTER_DIR_MAP = {
    "ch01": "ch01_preprocessing",
    "ch02": "ch02_eda",
    "ch03": "ch03_statistical_test",
    "ch04": "ch04_feature_selection",
    "ch05": "ch05_modeling",
    "ch06": "ch06_summary",
}

# === 可视化全局样式 ===
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 12
plt.rcParams['axes.unicode_minus'] = False
```

### 数据集概况

| 维度 | 值 |
|------|-----|
| 数据量 | 319 行 × 39 列 |
| 目标变量 | Gallstone_Status（0=无, 1=有） |
| 类别分布 | 0: 161 (50.5%), 1: 158 (49.5%) |
| 特征分组 | 人口统计(4) + 合并症(5) + 人体成分(16) + 血液生化(13) + 目标(1) |
| 缺失值 | 无 |
| 数据来源 | UCI Gallstone Dataset |

---

## 全局 Skill 库

### Skill-01: 标准数据加载器 (`src/utils/data_loader.py`)

| 函数 | 签名 | 说明 |
|------|------|------|
| `load_raw_data` | `load_raw_data(filepath) -> pd.DataFrame` | 加载原始数据 |
| `load_cleaned_data` | `load_cleaned_data(filepath) -> pd.DataFrame` | 加载清洗后数据 |
| `load_selected_features` | `load_selected_features(filepath) -> pd.DataFrame` | 加载特征筛选后数据 |

### Skill-02: 标准可视化出图器 (`src/utils/visualizer.py`)

| 函数 | 签名 | 说明 |
|------|------|------|
| `plot_grouped_boxplot` | `plot_grouped_boxplot(df, cols, group_col, save_path, **kwargs)` | 分组箱线图 |
| `plot_roc_curves` | `plot_roc_curves(models_results, save_path, **kwargs)` | ROC 曲线对比图 |
| `plot_forest` | `plot_forest(results_df, save_path, **kwargs)` | 森林图（效应量） |
| `plot_heatmap` | `plot_heatmap(corr_matrix, save_path, **kwargs)` | 相关性热力图 |

### Skill-03: 标准评估指标计算器 (`src/utils/metrics.py`)

| 函数 | 签名 | 说明 |
|------|------|------|
| `calc_cohens_d` | `calc_cohens_d(group1, group2) -> float` | Cohen's d 效应量 |
| `calc_vif` | `calc_vif(X_df) -> pd.DataFrame` | 方差膨胀因子 |
| `compare_models` | `compare_models(results_list, save_path) -> pd.DataFrame` | 多模型对比表 |

### Skill-04: 标准输出产物管理器 (`src/utils/output_manager.py`)

| 函数 | 签名 | 说明 |
|------|------|------|
| `get_chapter_dir` | `get_chapter_dir(chapter_key) -> str` | 获取章节输出目录 |
| `save_dataframe` | `save_dataframe(df, filename, output_dir) -> str` | 保存 DataFrame |
| `save_figure` | `save_figure(fig, filename, output_dir, dpi=150) -> str` | 保存图表 |
| `save_markdown` | `save_markdown(content, filename, output_dir) -> str` | 保存 Markdown |

---

# Prompt-01: 数据预处理

> **状态**: ✅ 已完成

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**基础起点**，目标是对原始胆结石数据集进行清洗和标准化处理，包括列名标准化、异常值检测与处理、数据质量验证，输出高质量的分析数据集。

### 1.2 从什么数据出发

- `data/dataset-uci.xlsx`：319 行 × 39 列，单 Sheet "dataset"

### 1.3 可以采用什么方法

- 列名标准化：手动映射为 snake_case
- 异常值检测：IQR 方法（1.5×IQR）
- 异常值处理：Winsorize 截断

## 二、执行步骤

> 已完成，详见 `outputs/ch01_preprocessing/` 下的 9 个产物。

## 三、产物总览

| 序号 | 产物名称 | 文件名 | 后续使用 |
|------|----------|--------|----------|
| 1 | 清洗后数据集 | `ch01_cleaned_dataset.csv` | ch02~ch06 |
| 2 | 异常值检测报告 | `ch01_outlier_report.csv` | 参考 |
| 3 | 清洗后统计摘要 | `ch01_cleaned_data_statistics.csv` | ch02 |
| 4 | 清洗前后箱线图 | `ch01_boxplot_before_after.png` | 报告配图 |
| 5 | 清洗后分布直方图 | `ch01_histogram_cleaned.png` | 报告配图 |
| 6 | 相关性热力图 | `ch01_correlation_heatmap.png` | ch02, ch04 |
| 7 | 目标变量分布图 | `ch01_target_distribution.png` | 报告配图 |

---

# Prompt-02: 探索性数据分析

> **状态**: ⬜ 待执行

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**核心探索阶段**，基于第一章预处理后的标准化数据，从**人口统计、合并症、人体成分、血液生化**四个维度全面描述数据分布特征，量化胆结石组与非胆结石组的差异化模式，识别潜在的关键风险因素。

核心目标包括：
1. **全局描述统计**：计算全部连续变量的集中趋势、离散程度、分布形态
2. **分组对比分析**：按胆结石状态分组，量化各特征的组间差异（均值差、效应量）
3. **可视化探索**：分布图、箱线图、分类变量频率图、性别分层对比图
4. **相关性细化**：按特征分组（人体成分 / 血液生化）分别绘制相关性热力图

本章的输出将为后续统计检验（ch03）和特征筛选（ch04）提供直观依据和定量基础。

### 1.2 从什么数据出发

- `outputs/ch01_preprocessing/ch01_cleaned_dataset.csv`：319 行 × 39 列，已完成异常值处理和列名标准化

关键列说明：
- **Gallstone_Status**：目标变量（0/1）
- **Age, Gender, Height, Weight**：人口统计学特征
- **Comorbidity, CAD, Hypothyroidism, Hyperlipidemia, DM**：合并症（二分类/有序分类）
- **BMI, TBW, ECW, ICW, ECF_TBW_Ratio, TBFR_pct, LM_pct, Protein_pct, VFR, BM, MM, Obesity(%), TFC, VFA, VMA_kg, HFA**：人体成分指标（16 个连续变量）
- **Glucose, TC, LDL, HDL, Triglyceride, AST, ALT, ALP, Creatinine, GFR, CRP, HGB, Vitamin D**：血液生化指标（13 个连续变量）

### 1.3 可以采用什么方法

| 分析维度 | 方法 | 关键函数 |
|----------|------|----------|
| 描述统计 | 分组统计 | `df.groupby('Gallstone_Status').describe()` |
| 效应量 | Cohen's d | `(mean1 - mean2) / pooled_std` |
| 分布分析 | 直方图 + KDE | `sns.histplot(kde=True)` |
| 组间对比 | 箱线图 + 小提琴图 | `sns.boxplot()`, `sns.violinplot()` |
| 分类变量 | 频率表 + 堆叠柱状图 | `pd.crosstab()`, `sns.countplot()` |
| 相关性 | Pearson 相关系数 | `df.corr(method='pearson')` |
| 性别分层 | 分层描述统计 + 对比图 | `sns.catplot(hue='Gender')` |

替代方法：Parallel Coordinates Plot（高维可视化）、t-SNE/PCA 降维可视化

## 二、执行步骤

### Step 1: 全局描述统计

**本步骤要做什么**
计算全部 30 个连续变量的描述统计指标（均值、标准差、中位数、四分位数、偏度、峰度），形成全局统计表。

**代码框架**:
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.output_manager import get_chapter_dir, save_dataframe, save_figure

OUTPUT_DIR = get_chapter_dir("ch02")

df = pd.read_csv("outputs/ch01_preprocessing/ch01_cleaned_dataset.csv")

# 连续变量列表
binary_cols = ['Gallstone_Status', 'Gender', 'CAD', 'Hypothyroidism', 'Hyperlipidemia', 'DM']
ordinal_cols = ['Comorbidity', 'HFA', 'VFR']
continuous_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in binary_cols + ordinal_cols]

# 全局描述统计
stats_all = df[continuous_cols].agg(['count', 'mean', 'std', 'median', 'skew', 'kurtosis']).T
stats_all = stats_all.round(4)
save_dataframe(stats_all, "ch02_descriptive_stats_all.csv", OUTPUT_DIR)
```

**本步骤输出产物**
- `ch02_descriptive_stats_all.csv` — 全局描述统计表

### Step 2: 分组描述统计 + 效应量

**本步骤要做什么**
按 Gallstone_Status 分组计算描述统计量，并计算 Cohen's d 效应量，量化组间差异大小。

**代码框架**:
```python
from scipy import stats

group0 = df[df['Gallstone_Status'] == 0]
group1 = df[df['Gallstone_Status'] == 1]

effect_sizes = []
for col in continuous_cols:
    m0, m1 = group0[col].mean(), group1[col].mean()
    s0, s1 = group0[col].std(), group1[col].std()
    n0, n1 = len(group0), len(group1)
    pooled_std = np.sqrt(((n0-1)*s0**2 + (n1-1)*s1**2) / (n0+n1-2))
    cohens_d = (m1 - m0) / pooled_std if pooled_std > 0 else 0
    effect_sizes.append({
        'feature': col,
        'mean_group0': round(m0, 4),
        'mean_group1': round(m1, 4),
        'mean_diff': round(m1 - m0, 4),
        'cohens_d': round(cohens_d, 4),
        'abs_cohens_d': round(abs(cohens_d), 4)
    })

effect_df = pd.DataFrame(effect_sizes).sort_values('abs_cohens_d', ascending=False)
save_dataframe(effect_df, "ch02_effect_sizes.csv", OUTPUT_DIR)
print(effect_df.head(15).to_string(index=False))
```

**本步骤输出产物**
- `ch02_descriptive_stats_by_group.csv` — 分组描述统计表
- `ch02_effect_sizes.csv` — 组间效应量表

### Step 3: 连续变量分布图

**本步骤要做什么**
按胆结石状态分组，绘制全部 30 个连续变量的直方图 + KDE 叠加图，直观展示组间分布差异。

**代码框架**:
```python
n_cols = 4
n_rows = (len(continuous_cols) + n_cols - 1) // n_cols
fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 4))
axes = axes.flatten()

for i, col in enumerate(continuous_cols):
    ax = axes[i]
    for status, color, label in [(0, '#4CAF50', 'No Gallstone'), (1, '#F44336', 'Gallstone')]:
        subset = df[df['Gallstone_Status'] == status][col]
        ax.hist(subset, bins=25, alpha=0.5, color=color, label=label, density=True, edgecolor='white')
        subset.plot.kde(ax=ax, color=color, linewidth=1.5)
    ax.set_title(col, fontsize=9)
    ax.legend(fontsize=6)

for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)

plt.suptitle('Distribution by Gallstone Status', fontsize=14, fontweight='bold')
plt.tight_layout()
save_figure(fig, "ch02_distribution_plots.png", OUTPUT_DIR)
plt.close()
```

**本步骤输出产物**
- `ch02_distribution_plots.png` — 连续变量分布图

### Step 4: 分组箱线图

**本步骤要做什么**
绘制 Top 15 效应量最大的连续变量的分组箱线图，直观展示胆结石组与非胆结石组的数值差异。

**代码框架**:
```python
top15 = effect_df.head(15)['feature'].tolist()
n_cols = 5
n_rows = 3
fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 12))
axes = axes.flatten()

for i, col in enumerate(top15):
    ax = axes[i]
    sns.boxplot(x='Gallstone_Status', y=col, data=df, ax=ax, palette=['#4CAF50', '#F44336'])
    ax.set_title(f"{col}\n(d={effect_df[effect_df['feature']==col]['cohens_d'].values[0]:.2f})", fontsize=9)

plt.suptitle('Top 15 Features by Effect Size (Cohen\'s d)', fontsize=14, fontweight='bold')
plt.tight_layout()
save_figure(fig, "ch02_boxplots_by_group.png", OUTPUT_DIR)
plt.close()
```

**本步骤输出产物**
- `ch02_boxplots_by_group.png` — 分组箱线图

### Step 5: 分类变量分析

**本步骤要做什么**
对 Gender, Comorbidity, CAD, Hypothyroidism, Hyperlipidemia, DM 绘制频率分布和堆叠柱状图，分析分类变量与胆结石状态的关联。

**代码框架**:
```python
categorical_cols = ['Gender', 'Comorbidity', 'CAD', 'Hypothyroidism', 'Hyperlipidemia', 'DM']
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for i, col in enumerate(categorical_cols):
    ax = axes[i]
    ct = pd.crosstab(df[col], df['Gallstone_Status'], normalize='index')
    ct.plot(kind='bar', stacked=True, ax=ax, color=['#4CAF50', '#F44336'], edgecolor='white')
    ax.set_title(col, fontsize=11)
    ax.set_xlabel('')
    ax.set_ylabel('Proportion')
    ax.legend(['No Gallstone', 'Gallstone'], fontsize=8)
    ax.tick_params(axis='x', rotation=0)

plt.suptitle('Categorical Variables by Gallstone Status', fontsize=14, fontweight='bold')
plt.tight_layout()
save_figure(fig, "ch02_categorical_plots.png", OUTPUT_DIR)
plt.close()
```

**本步骤输出产物**
- `ch02_categorical_plots.png` — 分类变量频率图

### Step 6: 分组相关性热力图

**本步骤要做什么**
按特征分组（人体成分 / 血液生化）分别绘制与 Gallstone_Status 的相关性热力图。

**代码框架**:
```python
body_comp_cols = ['BMI', 'TBW', 'ECW', 'ICW', 'ECF_TBW_Ratio', 'TBFR_pct', 'LM_pct',
                  'Protein_pct', 'VFR', 'BM', 'MM', 'Obesity (%)', 'TFC', 'VFA', 'VMA_kg', 'HFA']
blood_cols = ['Glucose', 'TC', 'LDL', 'HDL', 'Triglyceride', 'AST', 'ALT', 'ALP',
              'Creatinine', 'GFR', 'CRP', 'HGB', 'Vitamin D']

fig, axes = plt.subplots(1, 2, figsize=(20, 12))

for ax, cols, title in [(axes[0], body_comp_cols, 'Body Composition'),
                         (axes[1], blood_cols, 'Blood Biomarkers')]:
    corr = df[cols + ['Gallstone_Status']].corr()['Gallstone_Status'].drop('Gallstone_Status').sort_values(key=abs, ascending=True)
    colors = ['#F44336' if v > 0 else '#2196F3' for v in corr.values]
    ax.barh(corr.index, corr.values, color=colors, edgecolor='white')
    ax.set_title(f'Correlation with Gallstone Status\n({title})', fontsize=12, fontweight='bold')
    ax.set_xlabel('Pearson r')
    ax.axvline(x=0, color='black', linewidth=0.5)

plt.tight_layout()
save_figure(fig, "ch02_correlation_by_group.png", OUTPUT_DIR)
plt.close()
```

**本步骤输出产物**
- `ch02_correlation_body_composition.png` — 人体成分相关性图
- `ch02_correlation_blood_biomarkers.png` — 血液生化相关性图

### Step 7: 性别分层分析

**本步骤要做什么**
按性别分层，分析各特征在胆结石组与非胆结石组间的差异，识别性别特异性风险因素。

**代码框架**:
```python
top10 = effect_df.head(10)['feature'].tolist()
fig, axes = plt.subplots(2, 5, figsize=(25, 10))
axes = axes.flatten()

for i, col in enumerate(top10):
    ax = axes[i]
    sns.boxplot(x='Gallstone_Status', y=col, hue='Gender', data=df, ax=ax,
                palette=['#FF69B4', '#4169E1'])
    ax.set_title(col, fontsize=9)
    ax.legend(fontsize=7)

plt.suptitle('Gender-Stratified Analysis (Top 10 Features)', fontsize=14, fontweight='bold')
plt.tight_layout()
save_figure(fig, "ch02_gender_stratified.png", OUTPUT_DIR)
plt.close()
```

**本步骤输出产物**
- `ch02_gender_stratified.png` — 性别分层对比图

### Step 8: Top 10 差异特征汇总

**本步骤要做什么**
提取效应量最大的 Top 10 特征，生成汇总表，为后续统计检验和特征筛选提供候选列表。

**代码框架**:
```python
top10_df = effect_df.head(10).copy()
top10_df['rank'] = range(1, 11)
save_dataframe(top10_df, "ch02_top10_differences.csv", OUTPUT_DIR)
print("Top 10 差异最大的特征:")
print(top10_df[['rank', 'feature', 'mean_group0', 'mean_group1', 'cohens_d']].to_string(index=False))
```

**本步骤输出产物**
- `ch02_top10_differences.csv` — Top 10 差异特征汇总

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用章节 |
|------|----------|--------|------|-------------|
| 1 | 全局描述统计表 | `ch02_descriptive_stats_all.csv` | CSV | ch03 |
| 2 | 分组描述统计表 | `ch02_descriptive_stats_by_group.csv` | CSV | ch03 |
| 3 | 组间效应量表 | `ch02_effect_sizes.csv` | CSV | ch03, ch04 |
| 4 | 连续变量分布图 | `ch02_distribution_plots.png` | PNG | 报告配图 |
| 5 | 分组箱线图 | `ch02_boxplots_by_group.png` | PNG | 报告配图 |
| 6 | 分类变量频率图 | `ch02_categorical_plots.png` | PNG | 报告配图 |
| 7 | 人体成分相关性图 | `ch02_correlation_body_composition.png` | PNG | 报告配图 |
| 8 | 血液生化相关性图 | `ch02_correlation_blood_biomarkers.png` | PNG | 报告配图 |
| 9 | 性别分层对比图 | `ch02_gender_stratified.png` | PNG | 报告配图 |
| 10 | Top 10 差异特征 | `ch02_top10_differences.csv` | CSV | ch04 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- Cohen's d 假设正态分布，对偏态分布特征可能不精确
- 分布图未展示置信区间
- 相关性仅使用 Pearson，未考虑非线性关系

### 4.2 可进一步优化的方向
- 使用 Spearman 秩相关替代 Pearson 相关
- 增加分位数带（5%-95%）展示分布不确定性
- 使用 pairplot 展示关键特征间的两两关系

## 五、异常处理与问题反馈机制

| 异常场景 | 判断标准 | 处理策略 | 需确认 |
|----------|----------|----------|--------|
| 某特征两组均值差异极小 | Cohen's d < 0.1 | 正常现象，记录即可 | 否 |
| 分布图显示极端偏态 | skew > 3 | 后续使用非参数检验 | 否 |
| 分类变量某类别样本过少 | 频数 < 5 | 合并相邻类别或使用 Fisher 检验 | 是 |

---

# Prompt-03: 统计检验

> **状态**: ⬜ 待执行

## 一、任务概述

### 1.1 本次任务是什么

本章通过严格的统计检验方法，量化胆结石组与非胆结石组在各特征上的差异是否具有**统计学意义**，控制多重比较带来的假阳性风险，为特征筛选提供统计显著性依据。

核心目标：
1. **正态性检验**：对 30 个连续变量做 Shapiro-Wilk 检验
2. **组间差异检验**：根据正态性选择 t-test / Mann-Whitney U
3. **分类变量关联检验**：Chi-squared 检验
4. **多重比较校正**：BH-FDR 校正
5. **效应量计算**：Cohen's d + Cramér's V
6. **森林图可视化**：展示各特征的效应量和置信区间

### 1.2 从什么数据出发

- `outputs/ch01_preprocessing/ch01_cleaned_dataset.csv`：清洗后数据
- `outputs/ch02_eda/ch02_effect_sizes.csv`：效应量参考

### 1.3 可以采用什么方法

| 检验类型 | 方法 | 适用条件 | 关键函数 |
|----------|------|----------|----------|
| 正态性检验 | Shapiro-Wilk | 连续变量 | `scipy.stats.shapiro()` |
| 方差齐性 | Levene's test | 正态分布变量 | `scipy.stats.levene()` |
| 均值比较 | t-test / Welch's t-test | 正态分布 | `scipy.stats.ttest_ind()` |
| 秩和检验 | Mann-Whitney U | 非正态分布 | `scipy.stats.mannwhitneyu()` |
| 分类关联 | Chi-squared | 分类变量 | `scipy.stats.chi2_contingency()` |
| 多重校正 | BH-FDR | 全部 p 值 | `statsmodels.stats.multitest.multipletests()` |

## 二、执行步骤

### Step 1: 正态性检验

**本步骤要做什么**
对 30 个连续变量分别做 Shapiro-Wilk 正态性检验，记录 p 值和正态性判定（α=0.05）。

**代码框架**:
```python
from scipy.stats import shapiro, levene, ttest_ind, mannwhitneyu, chi2_contingency
from statsmodels.stats.multitest import multipletests

OUTPUT_DIR = get_chapter_dir("ch03")
df = pd.read_csv("outputs/ch01_preprocessing/ch01_cleaned_dataset.csv")

group0 = df[df['Gallstone_Status'] == 0]
group1 = df[df['Gallstone_Status'] == 1]

normality_results = []
for col in continuous_cols:
    stat, p = shapiro(df[col])
    is_normal = p > 0.05
    normality_results.append({'feature': col, 'shapiro_stat': round(stat, 4),
                              'p_value': round(p, 6), 'is_normal': is_normal})

normality_df = pd.DataFrame(normality_results)
save_dataframe(normality_df, "ch03_normality_test.csv", OUTPUT_DIR)
normal_count = normality_df['is_normal'].sum()
print(f"正态分布变量: {normal_count}/{len(continuous_cols)}, 非正态: {len(continuous_cols) - normal_count}")
```

**本步骤输出产物**
- `ch03_normality_test.csv` — 正态性检验结果

### Step 2: 连续变量组间检验

**本步骤要做什么**
根据正态性检验结果，选择合适的统计检验方法：正态分布用 t-test（先做 Levene 方差齐性检验），非正态用 Mann-Whitney U。

**代码框架**:
```python
test_results = []
for col in continuous_cols:
    is_normal = normality_df[normality_df['feature'] == col]['is_normal'].values[0]
    v0, v1 = group0[col].values, group1[col].values

    if is_normal:
        _, p_levene = levene(v0, v1)
        equal_var = p_levene > 0.05
        stat, p_val = ttest_ind(v0, v1, equal_var=equal_var)
        method = "Welch's t-test" if not equal_var else "t-test"
    else:
        stat, p_val = mannwhitneyu(v0, v1, alternative='two-sided')
        method = "Mann-Whitney U"

    test_results.append({'feature': col, 'method': method, 'statistic': round(stat, 4),
                         'p_value': round(p_val, 6), 'is_normal': is_normal})

test_df = pd.DataFrame(test_results)
save_dataframe(test_df, "ch03_statistical_tests.csv", OUTPUT_DIR)
```

**本步骤输出产物**
- `ch03_statistical_tests.csv` — 完整检验结果表

### Step 3: 多重比较校正 + 效应量

**本步骤要做什么**
对全部 p 值应用 BH-FDR 校正，计算 Cohen's d 效应量，生成最终汇总表。

**代码框架**:
```python
# FDR 校正
p_values = test_df['p_value'].values
reject, p_corrected, _, _ = multipletests(p_values, method='fdr_bh')
test_df['p_corrected'] = np.round(p_corrected, 6)
test_df['significant_fdr'] = reject

# Cohen's d
for i, row in test_df.iterrows():
    col = row['feature']
    m0, m1 = group0[col].mean(), group1[col].mean()
    s0, s1 = group0[col].std(), group1[col].std()
    n0, n1 = len(group0), len(group1)
    pooled = np.sqrt(((n0-1)*s0**2 + (n1-1)*s1**2) / (n0+n1-2))
    test_df.loc[i, 'cohens_d'] = round((m1 - m0) / pooled, 4) if pooled > 0 else 0

save_dataframe(test_df, "ch03_adjusted_p_values.csv", OUTPUT_DIR)
sig_df = test_df[test_df['significant_fdr'] == True].sort_values('cohens_d', key=abs, ascending=False)
save_dataframe(sig_df, "ch03_significant_features.csv", OUTPUT_DIR)
print(f"FDR 校正后显著特征: {len(sig_df)}/{len(test_df)}")
print(sig_df[['feature', 'method', 'p_corrected', 'cohens_d']].to_string(index=False))
```

**本步骤输出产物**
- `ch03_adjusted_p_values.csv` — 校正后检验结果
- `ch03_significant_features.csv` — 显著特征汇总

### Step 4: 分类变量 Chi-squared 检验

**本步骤要做什么**
对 6 个分类/二分类变量做 Chi-squared 检验，计算 Cramér's V 效应量。

**代码框架**:
```python
from scipy.stats import chi2_contingency

categorical_cols = ['Gender', 'Comorbidity', 'CAD', 'Hypothyroidism', 'Hyperlipidemia', 'DM']
chi2_results = []

for col in categorical_cols:
    ct = pd.crosstab(df[col], df['Gallstone_Status'])
    chi2, p, dof, expected = chi2_contingency(ct)
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    chi2_results.append({'feature': col, 'chi2_stat': round(chi2, 4),
                         'p_value': round(p, 6), 'dof': dof, 'cramers_v': round(cramers_v, 4)})

chi2_df = pd.DataFrame(chi2_results)
save_dataframe(chi2_df, "ch03_chi2_tests.csv", OUTPUT_DIR)
```

**本步骤输出产物**
- `ch03_chi2_tests.csv` — 分类变量检验结果

### Step 5: 森林图可视化

**本步骤要做什么**
绘制检验结果森林图，展示各连续变量的效应量（Cohen's d）和 95% 置信区间，按显著性着色。

**代码框架**:
```python
import matplotlib.patches as mpatches

forest_df = test_df.sort_values('cohens_d').copy()
# 计算 95% CI for Cohen's d
for i, row in forest_df.iterrows():
    col = row['feature']
    n0, n1 = len(group0), len(group1)
    d = row['cohens_d']
    se = np.sqrt((n0+n1)/(n0*n1) + d**2/(2*(n0+n1)))
    forest_df.loc[i, 'ci_lower'] = round(d - 1.96*se, 4)
    forest_df.loc[i, 'ci_upper'] = round(d + 1.96*se, 4)

fig, ax = plt.subplots(figsize=(12, max(10, len(forest_df) * 0.35)))
colors = ['#F44336' if sig else '#BBBBBB' for sig in forest_df['significant_fdr']]
y_pos = range(len(forest_df))
ax.errorbar(forest_df['cohens_d'], y_pos, xerr=[forest_df['cohens_d'] - forest_df['ci_lower'],
            forest_df['ci_upper'] - forest_df['cohens_d']], fmt='o', color='black',
            capsize=3, markersize=4, elinewidth=1)
ax.scatter(forest_df['cohens_d'], y_pos, c=colors, zorder=5, s=30)
ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(forest_df['feature'], fontsize=8)
ax.set_xlabel("Cohen's d (95% CI)", fontsize=12)
ax.set_title('Forest Plot: Feature Effect Sizes', fontsize=14, fontweight='bold')
sig_patch = mpatches.Patch(color='#F44336', label='Significant (FDR p<0.05)')
ns_patch = mpatches.Patch(color='#BBBBBB', label='Not Significant')
ax.legend(handles=[sig_patch, ns_patch], loc='lower right')
plt.tight_layout()
save_figure(fig, "ch03_forest_plot.png", OUTPUT_DIR)
plt.close()
```

**本步骤输出产物**
- `ch03_forest_plot.png` — 检验结果森林图

## 三、产物总览

| 序号 | 产物名称 | 文件名 | 后续使用 |
|------|----------|--------|----------|
| 1 | 正态性检验结果 | `ch03_normality_test.csv` | 参考 |
| 2 | 完整检验结果表 | `ch03_statistical_tests.csv` | ch04 |
| 3 | 校正后检验结果 | `ch03_adjusted_p_values.csv` | ch04 |
| 4 | 分类变量检验 | `ch03_chi2_tests.csv` | ch04 |
| 5 | 森林图 | `ch03_forest_plot.png` | 报告配图 |
| 6 | 显著特征汇总 | `ch03_significant_features.csv` | ch04, ch05 |

## 四、产物后续优化方向

### 4.1 局限性
- Shapiro-Wilk 对大样本过于敏感（n>50 时几乎总是拒绝正态性）
- 横截面数据无法推断因果关系
- 未考虑混杂因素（如年龄、性别）的调整

### 4.2 优化方向
- 使用 Q-Q 图辅助正态性判断
- 增加多因素 Logistic 回归调整混杂因素
- 使用 Bootstrap 计算效应量的稳健置信区间

## 五、异常处理

| 异常场景 | 判断标准 | 处理策略 | 需确认 |
|----------|----------|----------|--------|
| 全部变量均不显著 | FDR 校正后无显著特征 | 降低 α 阈值至 0.10 或增加样本量 | 是 |
| 某变量方差为 0 | std == 0 | 跳过该变量（常量无分析价值） | 否 |
| Chi-squared 期望频数 < 5 | `expected.min() < 5` | 改用 Fisher's exact test | 否 |

---

# Prompt-04: 特征筛选

> **状态**: ⬜ 待执行

## 一、任务概述

### 1.1 本次任务是什么

综合统计显著性、效应量、模型特征重要性和共线性诊断，从 38 个候选特征中筛选出胆结石预测的**最优特征子集**，解决人体成分指标间高度共线性问题。

核心目标：
1. **统计筛选**：基于 ch03 的显著性检验结果，筛选 FDR p < 0.05 且 |Cohen's d| > 0.2 的特征
2. **VIF 共线性诊断**：识别并去除高度共线性特征
3. **LASSO 回归筛选**：自动特征选择
4. **RFE 递归特征消除**：基于模型性能排序
5. **Random Forest 特征重要性**：基于基尼不纯度排序
6. **综合评分**：多方法交叉验证，确定最终特征子集

### 1.2 从什么数据出发

- `outputs/ch01_preprocessing/ch01_cleaned_dataset.csv`：清洗后数据
- `outputs/ch03_statistical_test/ch03_significant_features.csv`：显著特征列表
- `outputs/ch03_statistical_test/ch03_adjusted_p_values.csv`：校正后检验结果

### 1.3 可以采用什么方法

| 方法 | 参数 | 选择理由 |
|------|------|----------|
| VIF 诊断 | 阈值 > 10 | 识别多重共线性 |
| LASSO | LassoCV | 自动特征选择，处理共线性 |
| RFE | LogisticRegression + 5-fold CV | 基于模型性能排序 |
| Random Forest | n_estimators=500 | 非线性特征重要性 |

## 二、执行步骤

### Step 1: 统计筛选

**本步骤要做什么**
筛选 FDR 校正后 p < 0.05 且 |Cohen's d| > 0.2 的特征。

**代码框架**:
```python
OUTPUT_DIR = get_chapter_dir("ch04")
df = pd.read_csv("outputs/ch01_preprocessing/ch01_cleaned_dataset.csv")
test_df = pd.read_csv("outputs/ch03_statistical_test/ch03_adjusted_p_values.csv")

# 统计筛选
stat_selected = test_df[(test_df['p_corrected'] < 0.05) & (test_df['cohens_d'].abs() > 0.2)]
stat_features = stat_selected['feature'].tolist()
print(f"统计筛选通过: {len(stat_features)} 个特征")
print(stat_features)
```

**本步骤输出产物**
- `ch04_statistical_selection.csv` — 统计筛选结果

### Step 2: VIF 共线性诊断

**本步骤要做什么**
对通过统计筛选的特征计算 VIF，逐步去除 VIF > 10 的特征。

**代码框架**:
```python
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

X = df[stat_features].copy()
X_scaled = pd.DataFrame(StandardScaler().fit_transform(X), columns=stat_features)

vif_data = pd.DataFrame()
vif_data['feature'] = stat_features
vif_data['VIF'] = [variance_inflation_factor(X_scaled.values, i) for i in range(len(stat_features))]
vif_data = vif_data.sort_values('VIF', ascending=False)

# 逐步去除高 VIF 特征
while vif_data['VIF'].max() > 10:
    drop_feat = vif_data.loc[vif_data['VIF'].idxmax(), 'feature']
    stat_features.remove(drop_feat)
    X_scaled = X_scaled.drop(columns=[drop_feat])
    vif_data = pd.DataFrame()
    vif_data['feature'] = stat_features
    vif_data['VIF'] = [variance_inflation_factor(X_scaled.values, i) for i in range(len(stat_features))]
    vif_data = vif_data.sort_values('VIF', ascending=False)

save_dataframe(vif_data, "ch04_vif_analysis.csv", OUTPUT_DIR)
print(f"VIF 筛选后: {len(stat_features)} 个特征")
```

**本步骤输出产物**
- `ch04_vif_analysis.csv` — VIF 诊断结果

### Step 3: LASSO 回归筛选

**本步骤要做什么**
使用 LassoCV 自动选择正则化强度，获取非零系数特征。

**代码框架**:
```python
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

y = df['Gallstone_Status']
X = df[stat_features]
X_scaled = StandardScaler().fit_transform(X)

lasso = LassoCV(cv=5, random_state=42, max_iter=10000)
lasso.fit(X_scaled, y)

lasso_results = pd.DataFrame({'feature': stat_features, 'coefficient': lasso.coef_})
lasso_selected = lasso_results[lasso_results['coefficient'] != 0]['feature'].tolist()
save_dataframe(lasso_results, "ch04_lasso_selection.csv", OUTPUT_DIR)
print(f"LASSO 筛选: {len(lasso_selected)} 个特征, alpha={lasso.alpha_:.4f}")
```

**本步骤输出产物**
- `ch04_lasso_selection.csv` — LASSO 筛选结果

### Step 4: RFE 递归特征消除

**本步骤要做什么**
使用 Logistic Regression + 5-fold CV 进行递归特征消除，获取特征排序。

**代码框架**:
```python
from sklearn.feature_selection import RFECV
from sklearn.linear_model import LogisticRegression

rfe = RFECV(estimator=LogisticRegression(max_iter=1000, random_state=42),
             cv=5, scoring='roc_auc', step=1)
rfe.fit(X_scaled, y)

rfe_results = pd.DataFrame({'feature': stat_features, 'ranking': rfe.ranking_, 'selected': rfe.support_})
rfe_results = rfe_results.sort_values('ranking')
save_dataframe(rfe_results, "ch04_rfe_ranking.csv", OUTPUT_DIR)
print(f"RFE 最优特征数: {rfe.n_features_}")
```

**本步骤输出产物**
- `ch04_rfe_ranking.csv` — RFE 特征排序

### Step 5: Random Forest 特征重要性

**本步骤要做什么**
训练随机森林，获取基于基尼不纯度的特征重要性排序。

**代码框架**:
```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=500, random_state=42, max_depth=10)
rf.fit(X_scaled, y)

rf_importance = pd.DataFrame({'feature': stat_features, 'importance': rf.feature_importances_})
rf_importance = rf_importance.sort_values('importance', ascending=False)
save_dataframe(rf_importance, "ch04_rf_importance.csv", OUTPUT_DIR)
print("Top 10 RF 特征重要性:")
print(rf_importance.head(10).to_string(index=False))
```

**本步骤输出产物**
- `ch04_rf_importance.csv` — RF 特征重要性

### Step 6: 综合评分与最终特征确定

**本步骤要做什么**
综合 4 种方法的结果，计算每个特征的综合得分，确定最终特征子集。

**代码框架**:
```python
# 综合评分：每种方法排名归一化后取平均
from sklearn.preprocessing import MinMaxScaler

all_features = list(set(stat_features + lasso_selected + rfe_results[rfe_results['selected']]['feature'].tolist()))

score_df = pd.DataFrame({'feature': all_features})

# 统计得分（是否通过统计筛选）
score_df['stat_score'] = score_df['feature'].isin(stat_features).astype(int)

# VIF 得分（VIF 越低越好，归一化到 0-1）
vif_map = dict(zip(vif_data['feature'], vif_data['VIF']))
score_df['vif'] = score_df['feature'].map(vif_map).fillna(20)
score_df['vif_score'] = 1 - MinMaxScaler().fit_transform(score_df[['vif']])

# LASSO 得分
lasso_map = dict(zip(lasso_results['feature'], np.abs(lasso_results['coefficient'])))
score_df['lasso_score'] = score_df['feature'].map(lasso_map).fillna(0)
score_df['lasso_score'] = MinMaxScaler().fit_transform(score_df[['lasso_score']])

# RFE 得分（排名越小越好）
rfe_map = dict(zip(rfe_results['feature'], -rfe_results['ranking']))
score_df['rfe_score'] = score_df['feature'].map(rfe_map).fillna(0)
score_df['rfe_score'] = MinMaxScaler().fit_transform(score_df[['rfe_score']])

# RF 得分
rf_map = dict(zip(rf_importance['feature'], rf_importance['importance']))
score_df['rf_score'] = score_df['feature'].map(rf_map).fillna(0)
score_df['rf_score'] = MinMaxScaler().fit_transform(score_df[['rf_score']])

# 综合得分
score_df['composite_score'] = (score_df['stat_score'] + score_df['vif_score'] +
                                score_df['lasso_score'] + score_df['rfe_score'] +
                                score_df['rf_score']) / 5
score_df = score_df.sort_values('composite_score', ascending=False)

# 最终特征：综合得分 > 0.3 且 VIF < 10
final_features = score_df[(score_df['composite_score'] > 0.3)]['feature'].tolist()
save_dataframe(score_df, "ch04_composite_score.csv", OUTPUT_DIR)

final_df = pd.DataFrame({'feature': final_features, 'rank': range(1, len(final_features)+1)})
save_dataframe(final_df, "ch04_final_features.csv", OUTPUT_DIR)

# 保存筛选后数据集
X_final = df[final_features + ['Gallstone_Status']]
save_dataframe(X_final, "ch04_selected_features_data.csv", OUTPUT_DIR)

print(f"最终特征子集: {len(final_features)} 个特征")
print(final_features)
```

**本步骤输出产物**
- `ch04_composite_score.csv` — 综合评分表
- `ch04_final_features.csv` — 最终特征列表
- `ch04_selected_features_data.csv` — 筛选后数据集

### Step 7: 可视化

**本步骤要做什么**
绘制特征重要性排序图和 VIF 柱状图。

**代码框架**:
```python
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# 特征重要性图
ax = axes[0]
top = score_df.head(15)
colors = plt.cm.RdYlGn(top['composite_score'].values / top['composite_score'].max())
ax.barh(range(len(top)), top['composite_score'].values, color=colors)
ax.set_yticks(range(len(top)))
ax.set_yticklabels(top['feature'], fontsize=9)
ax.set_xlabel('Composite Score')
ax.set_title('Feature Selection - Composite Score', fontsize=12, fontweight='bold')
ax.invert_yaxis()

# VIF 柱状图
ax = axes[1]
vif_sorted = vif_data.sort_values('VIF', ascending=True)
colors_vif = ['#F44336' if v > 10 else '#4CAF50' for v in vif_sorted['VIF']]
ax.barh(range(len(vif_sorted)), vif_sorted['VIF'].values, color=colors_vif)
ax.set_yticks(range(len(vif_sorted)))
ax.set_yticklabels(vif_sorted['feature'], fontsize=9)
ax.axvline(x=10, color='red', linestyle='--', linewidth=1, label='VIF=10')
ax.set_xlabel('VIF')
ax.set_title('VIF Analysis', fontsize=12, fontweight='bold')
ax.legend()

plt.tight_layout()
save_figure(fig, "ch04_feature_importance.png", OUTPUT_DIR)
plt.close()
```

**本步骤输出产物**
- `ch04_feature_importance.png` — 特征重要性图
- `ch04_vif_barplot.png` — VIF 柱状图

## 三、产物总览

| 序号 | 产物名称 | 文件名 | 后续使用 |
|------|----------|--------|----------|
| 1 | VIF 诊断结果 | `ch04_vif_analysis.csv` | 参考 |
| 2 | LASSO 筛选结果 | `ch04_lasso_selection.csv` | 参考 |
| 3 | RFE 特征排序 | `ch04_rfe_ranking.csv` | 参考 |
| 4 | RF 特征重要性 | `ch04_rf_importance.csv` | 参考 |
| 5 | 综合评分表 | `ch04_composite_score.csv` | ch05 |
| 6 | 最终特征列表 | `ch04_final_features.csv` | ch05 |
| 7 | 特征重要性图 | `ch04_feature_importance.png` | 报告配图 |
| 8 | VIF 柱状图 | `ch04_vif_barplot.png` | 报告配图 |
| 9 | 筛选后数据集 | `ch04_selected_features_data.csv` | ch05 |

## 四、产物后续优化方向

### 4.1 局限性
- 综合评分权重为等权，未考虑方法可靠性差异
- 样本量较小（319），LASSO 和 RFE 结果可能不稳定

### 4.2 优化方向
- 使用 Stacking 集成多种筛选方法
- 使用 Bootstrap 评估特征选择的稳定性
- 增加领域知识加权（如 CRP、Vitamin D 的临床证据更强）

## 五、异常处理

| 异常场景 | 判断标准 | 处理策略 | 需确认 |
|----------|----------|----------|--------|
| 最终特征数 < 5 | 综合得分 > 0.3 的特征过少 | 降低阈值至 0.2 | 是 |
| 最终特征数 > 20 | 特征过多可能导致过拟合 | 提高阈值至 0.5 | 是 |
| LASSO 全部系数为 0 | 正则化过强 | 检查数据标准化是否正确 | 否 |

---

# Prompt-05: 建模预测

> **状态**: ⬜ 待执行

## 一、任务概述

### 1.1 本次任务是什么

基于筛选后的特征子集，训练多种机器学习模型，通过严格的交叉验证评估预测性能，确定最优胆结石预测模型，并使用 SHAP 分析关键预测特征。

核心目标：
1. **多模型训练**：Logistic Regression, Random Forest, Gradient Boosting, XGBoost
2. **交叉验证评估**：5-fold Stratified CV，评估 AUC-ROC, F1, Accuracy
3. **模型比较**：确定最优模型
4. **可解释性分析**：SHAP 特征贡献分析

### 1.2 从什么数据出发

- `outputs/ch04_feature_selection/ch04_selected_features_data.csv`：筛选后数据集
- `outputs/ch04_feature_selection/ch04_final_features.csv`：最终特征列表

### 1.3 可以采用什么方法

| 模型 | 参数 | 选择理由 |
|------|------|----------|
| Logistic Regression | CV 正则化 | 可解释性强，临床标准 |
| Random Forest | n_estimators=500 | 对非线性鲁棒 |
| Gradient Boosting | learning_rate=0.1 | 通常性能最优 |
| XGBoost | max_depth=5 | 高性能梯度提升 |

## 二、执行步骤

### Step 1: 数据准备

**本步骤要做什么**
加载筛选后数据集，划分特征矩阵 X 和目标向量 y。

**代码框架**:
```python
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score, precision_score, recall_score, roc_curve
from sklearn.linear_model import LogisticRegressionCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb
import shap
import joblib

OUTPUT_DIR = get_chapter_dir("ch05")
df = pd.read_csv("outputs/ch04_feature_selection/ch04_selected_features_data.csv")
feature_cols = pd.read_csv("outputs/ch04_feature_selection/ch04_final_features.csv")['feature'].tolist()

X = df[feature_cols]
y = df['Gallstone_Status']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=feature_cols)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
```

**本步骤输出产物**
- 无独立文件（内存中传递）

### Step 2: 模型训练与交叉验证

**本步骤要做什么**
训练 4 种模型，使用 5-fold Stratified CV 评估 AUC-ROC, F1, Accuracy。

**代码框架**:
```python
models = {
    'Logistic Regression': LogisticRegressionCV(cv=5, max_iter=2000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=500, max_depth=10, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42),
    'XGBoost': xgb.XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42, eval_metric='logloss', use_label_encoder=False)
}

scoring = ['roc_auc', 'f1', 'accuracy', 'precision', 'recall']
results = []

for name, model in models.items():
    cv_results = cross_validate(model, X_scaled_df, y, cv=cv, scoring=scoring, return_estimator=True)
    results.append({
        'model': name,
        'AUC-ROC': f"{cv_results['test_roc_auc'].mean():.4f} ± {cv_results['test_roc_auc'].std():.4f}",
        'F1': f"{cv_results['test_f1'].mean():.4f} ± {cv_results['test_f1'].std():.4f}",
        'Accuracy': f"{cv_results['test_accuracy'].mean():.4f} ± {cv_results['test_accuracy'].std():.4f}",
        'Precision': f"{cv_results['test_precision'].mean():.4f} ± {cv_results['test_precision'].std():.4f}",
        'Recall': f"{cv_results['test_recall'].mean():.4f} ± {cv_results['test_recall'].std():.4f}",
        'best_estimator': cv_results['estimator'][np.argmax(cv_results['test_roc_auc'])]
    })
    print(f"{name}: AUC={cv_results['test_roc_auc'].mean():.4f}")

results_df = pd.DataFrame([{k: v for k, v in r.items() if k != 'best_estimator'} for r in results])
save_dataframe(results_df, "ch05_model_comparison.csv", OUTPUT_DIR)
```

**本步骤输出产物**
- `ch05_model_comparison.csv` — 模型性能对比表

### Step 3: ROC 曲线绘制

**本步骤要做什么**
绘制各模型的 ROC 曲线对比图。

**代码框架**:
```python
from sklearn.model_selection import cross_val_predict

fig, ax = plt.subplots(figsize=(10, 8))
colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']

for i, (name, model) in enumerate(models.items()):
    y_pred_proba = cross_val_predict(model, X_scaled_df, y, cv=cv, method='predict_proba')[:, 1]
    fpr, tpr, _ = roc_curve(y, y_pred_proba)
    auc = roc_auc_score(y, y_pred_proba)
    ax.plot(fpr, tpr, color=colors[i], linewidth=2, label=f"{name} (AUC={auc:.3f})")

ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
ax.set_xlabel('False Positive Rate', fontsize=12)
ax.set_ylabel('True Positive Rate', fontsize=12)
ax.set_title('ROC Curves Comparison', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
save_figure(fig, "ch05_roc_curves.png", OUTPUT_DIR)
plt.close()
```

**本步骤输出产物**
- `ch05_roc_curves.png` — ROC 曲线对比图

### Step 4: SHAP 分析

**本步骤要做什么**
使用 SHAP 分析最优模型的特征贡献，生成 SHAP summary plot 和 dependence plot。

**代码框架**:
```python
# 找到最优模型
best_idx = np.argmax([float(r['AUC-ROC'].split(' ')[0]) for r in results])
best_model = results[best_idx]['best_estimator']
best_name = results[best_idx]['model']

# 训练最优模型（全量数据）
best_model.fit(X_scaled_df, y)

# SHAP 分析
if 'XGBoost' in best_name or 'Random' in best_name or 'Gradient' in best_name:
    explainer = shap.TreeExplainer(best_model)
else:
    explainer = shap.LinearExplainer(best_model, X_scaled_df)

shap_values = explainer.shap_values(X_scaled_df)

fig, ax = plt.subplots(figsize=(10, 8))
shap.summary_plot(shap_values, X_scaled_df, show=False, max_display=15)
plt.tight_layout()
save_figure(fig, "ch05_shap_summary.png", OUTPUT_DIR)
plt.close()

# 保存 SHAP 值
shap_df = pd.DataFrame(shap_values, columns=feature_cols)
shap_df['mean_abs_shap'] = shap_df.abs().mean(axis=1).values
save_dataframe(shap_df, "ch05_shap_values.csv", OUTPUT_DIR)
```

**本步骤输出产物**
- `ch05_shap_summary.png` — SHAP 特征重要性图
- `ch05_shap_values.csv` — SHAP 值数据

### Step 5: 保存最优模型

**本步骤要做什么**
将最优模型保存为 .pkl 文件。

**代码框架**:
```python
model_path = os.path.join(OUTPUT_DIR, "ch05_best_model.pkl")
joblib.dump({'model': best_model, 'scaler': scaler, 'features': feature_cols}, model_path)
print(f"最优模型已保存: {best_name}")
print(f"保存路径: {model_path}")
```

**本步骤输出产物**
- `ch05_best_model.pkl` — 最优模型文件

## 三、产物总览

| 序号 | 产物名称 | 文件名 | 后续使用 |
|------|----------|--------|----------|
| 1 | 模型性能对比表 | `ch05_model_comparison.csv` | ch06 |
| 2 | ROC 曲线图 | `ch05_roc_curves.png` | 报告配图 |
| 3 | SHAP 特征重要性图 | `ch05_shap_summary.png` | 报告配图 |
| 4 | SHAP 值数据 | `ch05_shap_values.csv` | ch06 |
| 5 | 最优模型文件 | `ch05_best_model.pkl` | 部署参考 |

## 四、产物后续优化方向

### 4.1 局限性
- 样本量较小（319），模型性能可能不稳定
- 未进行超参数深度调优
- 未做外部验证

### 4.2 优化方向
- 使用 Optuna 进行贝叶斯超参数优化
- 使用 Nested CV 减少评估偏差
- 增加混淆矩阵可视化

## 五、异常处理

| 异常场景 | 判断标准 | 处理策略 | 需确认 |
|----------|----------|----------|--------|
| 所有模型 AUC < 0.65 | 性能低于随机水平 | 检查特征筛选和数据质量 | 是 |
| XGBoost 安装失败 | ImportError | 退回使用 Gradient Boosting | 否 |
| SHAP 计算超时 | 运行时间 > 5 分钟 | 减少特征数或使用采样 | 否 |

---

# Prompt-06: 总结报告

> **状态**: ⬜ 待执行

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**收尾章节**，系统汇总前 5 章的核心研究成果，提炼关键发现和核心数据指标，评估研究局限性，提出未来研究方向。

### 1.2 从什么数据出发

全部前序章节产物：`outputs/ch01~ch05/*/`

### 1.3 可以采用什么方法

- 结构化文本撰写
- 关键指标提取
- SWOT 分析（可选）

## 二、执行步骤

### Step 1: 全流程成果梳理

**本步骤要做什么**
按章节顺序，逐章提炼 2-3 条核心发现（定性结论 + 定量数据）。

**代码框架**:
```python
OUTPUT_DIR = get_chapter_dir("ch06")

summary = """# UCI 胆结石数据集分析 — 成果汇总报告

## 一、数据预处理（ch01）
- 清洗后数据：319 行 × 39 列，无缺失值，无重复行
- 异常值处理：IQR + Winsorize，25 列共 223 个异常值被截断
- 列名标准化：27 个列名简化为 snake_case

## 二、探索性分析（ch02）
- [待填充：Top 5 差异特征及效应量]
- [待填充：关键分布特征发现]

## 三、统计检验（ch03）
- [待填充：显著特征数量及关键发现]
- [待填充：分类变量检验结果]

## 四、特征筛选（ch04）
- [待填充：最终特征数量及列表]
- [待填充：共线性处理结果]

## 五、建模预测（ch05）
- [待填充：最优模型及 AUC]
- [待填充：Top 5 SHAP 特征]

## 六、研究局限性
1. **样本量有限**：319 例样本可能不足以发现弱效应特征
2. **横截面设计**：无法推断因果关系
3. **外部验证缺失**：模型未在独立数据集上验证

## 七、未来展望
1. 扩大样本量，提升统计检验力和模型泛化能力
2. 收集纵向数据，支持因果推断
3. 外部验证：在独立队列中验证模型性能
4. 深度学习：探索神经网络模型的潜力
"""

save_markdown(summary, "ch06_achievements_summary.md", OUTPUT_DIR)
```

**本步骤输出产物**
- `ch06_achievements_summary.md` — 成果汇总报告

### Step 2: 关键指标总览表

**本步骤要做什么**
提取各章核心数值指标，形成关键指标总览表。

**代码框架**:
```python
metrics = pd.DataFrame([
    {'chapter': 'ch01', 'category': '数据质量', 'metric': '清洗后样本量', 'value': 319, 'unit': '行'},
    {'chapter': 'ch01', 'category': '数据质量', 'metric': '异常值处理数', 'value': 223, 'unit': '个'},
    {'chapter': 'ch02', 'category': 'EDA', 'metric': 'Top 1 效应量特征', 'value': '待填充', 'unit': '-'},
    {'chapter': 'ch03', 'category': '统计检验', 'metric': 'FDR 显著特征数', 'value': '待填充', 'unit': '个'},
    {'chapter': 'ch04', 'category': '特征筛选', 'metric': '最终特征数', 'value': '待填充', 'unit': '个'},
    {'chapter': 'ch05', 'category': '建模', 'metric': '最优模型 AUC', 'value': '待填充', 'unit': '-'},
    {'chapter': 'ch05', 'category': '建模', 'metric': '最优模型 F1', 'value': '待填充', 'unit': '-'},
])

save_dataframe(metrics, "ch06_key_metrics_table.csv", OUTPUT_DIR)
```

**本步骤输出产物**
- `ch06_key_metrics_table.csv` — 关键指标总览表

## 三、产物总览

| 序号 | 产物名称 | 文件名 | 后续使用 |
|------|----------|--------|----------|
| 1 | 成果汇总报告 | `ch06_achievements_summary.md` | 最终交付 |
| 2 | 关键指标总览表 | `ch06_key_metrics_table.csv` | 最终交付 |

## 四、产物后续优化方向

### 4.1 局限性
- 依赖前序章节产物完整性
- "待填充"项需手动回填

### 4.2 优化方向
- 自动化指标回填
- 生成学术格式报告

## 五、异常处理

| 异常场景 | 判断标准 | 处理策略 | 需确认 |
|----------|----------|----------|--------|
| 某章产物缺失 | FileNotFoundError | 跳过该章，标注原因 | 否 |
| 指标数据矛盾 | 不同章节数值不一致 | 以最新章节为准 | 是 |

---

## 附录 A: 全项目产物总览表

| 章节 | 数据文件 | 图片文件 | 模型文件 | 报告/文档 | 合计 |
|------|----------|----------|----------|-----------|------|
| ch01 预处理 | 5 | 4 | 0 | 1 | 10 |
| ch02 EDA | 4 | 6 | 0 | 0 | 10 |
| ch03 统计检验 | 4 | 1 | 0 | 0 | 5 |
| ch04 特征筛选 | 5 | 2 | 0 | 0 | 7 |
| ch05 建模 | 2 | 2 | 1 | 0 | 5 |
| ch06 总结 | 1 | 0 | 0 | 1 | 2 |
| **总计** | **21** | **15** | **1** | **2** | **39** |

## 附录 B: 完整依赖清单

```
pandas>=2.0.0              # 数据处理
numpy>=1.24.0              # 数值计算
openpyxl>=3.1.0            # Excel 读写
matplotlib>=3.7.0          # 基础可视化
seaborn>=0.12.0            # 统计可视化
scipy>=1.10.0              # 统计检验
statsmodels>=0.14.0        # 统计建模与多重比较校正
scikit-learn>=1.3.0        # 机器学习模型
xgboost>=2.0.0             # XGBoost 梯度提升
shap>=0.43.0               # 模型可解释性分析
joblib>=1.3.0              # 模型序列化
jupyter>=1.0.0             # Jupyter Notebook
ipykernel>=6.25.0          # IPython Kernel
tqdm>=4.65.0               # 进度条
```
