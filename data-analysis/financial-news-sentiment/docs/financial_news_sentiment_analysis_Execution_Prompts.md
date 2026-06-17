# 金融新闻舆情分析与市场预测 — 执行Prompt文档

## 文档说明

本文档为**全流程标准化金融新闻舆情分析执行指南**，覆盖从描述性统计分析到可视化看板与综合报告的完整分析链条。每个章节的 Prompt 均设计为**自包含、可独立执行**的单元，可直接复制到 AI 助手中执行，也可由数据分析师参照手动操作。

### 适用环境
- **Python 版本**: 3.10（本地 conda 环境 `py310`）
- **执行方式**: 每个章节均提供 **.py + .ipynb** 双格式脚本，按章节编号命名，支持批量执行和交互式调试
- **环境管理**: 使用本地 conda 环境 `py310`，激活命令 `conda activate py310`，通过 `pip install -r requirements.txt` 安装全部依赖。**禁止创建 venv 目录**
- **依赖库清单**: 见 `requirements.txt`

### 文档关系
- **上位设计文档**: `docs/flow_design.md` — 定义"做什么、为什么、用什么方法"
- **本文档**: 定义"怎么做——精确到函数、参数、代码级别"
- **项目规范**: `docs/project_convention.md` — 目录结构、命名规范、脚本规范
- **任务分发**: `docs/task_dispatch_guide.md` — 依赖图、批次划分、派活模板

### 章节列表（ch01 已完成，本文档覆盖 ch02-ch06）

| Prompt | 章节 | 状态 | 原型 |
|--------|------|------|------|
| Prompt-02 | ch02 描述性统计分析 | 待执行 | B 分析探索型 |
| Prompt-03 | ch03 文本挖掘与情感分析 | 待执行 | B 分析探索型 |
| Prompt-04 | ch04 特征工程 | 待执行 | B 分析探索型 |
| Prompt-05 | ch05 事件驱动策略分析 | 待执行 | B 分析探索型 |
| Prompt-06 | ch06 可视化看板与总结报告 | 待执行 | C 总结报告型 |

---

## 全局路径配置

> 每个章节脚本的首个 Cell 必须包含以下配置。**禁止硬编码路径**，所有路径通过 `src/utils/config.py` 统一管理。

```python
import sys
import os
from pathlib import Path

# 路径设置（确保能导入 utils）
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入全局配置
from src.utils.config import (
    PROJECT_ROOT, DATA_DIR, OUTPUTS_DIR, DOCS_DIR,
    RAW_DATA_PATH, FIGURE_DPI, FIGURE_DPI_HIGH,
    FIGURE_SIZE_DEFAULT, FIGURE_SIZE_WIDE,
    MATPLOTLIB_RC_PARAMS, get_chapter_output_dir,
)

# 设置 matplotlib 全局样式
import matplotlib
matplotlib.rcParams.update(MATPLOTLIB_RC_PARAMS)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

# 章节输出目录（按需修改章节名）
CHAPTER_NAME = "ch02_descriptive_stats"
OUTPUT_DIR = get_chapter_output_dir(CHAPTER_NAME)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
```

---

## 全局 Skill 库

以下 4 个 Skill 贯穿全流程，每个章节均可调用。完整代码见 `src/utils/`。

### Skill-01: 标准数据加载器 (`src/utils/data_loader.py`)

| 函数 | 说明 |
|------|------|
| `load_raw_data(filepath)` | 加载原始数据 |
| `load_preprocessed(filepath)` | 加载预处理后的数据 |

### Skill-02: 标准可视化出图器 (`src/utils/visualizer.py`)

| 函数 | 说明 |
|------|------|
| `plot_time_series(df, time_col, value_col, title, save_path)` | 标准时序曲线图 |
| `plot_heatmap(pivot_data, title, save_path)` | 标准热力图 |
| `plot_grouped_bar(data, x_col, y_col, title, save_path)` | 分组柱状图 |

### Skill-03: 标准评估指标计算器 (`src/utils/metrics.py`)

| 函数 | 说明 |
|------|------|
| `calc_coherence(model, texts, dictionary)` | 主题 Coherence Score |
| `calc_vif(X)` | 方差膨胀因子 |

### Skill-04: 标准输出产物管理器 (`src/utils/output_manager.py`)

| 函数 | 说明 |
|------|------|
| `save_dataframe(df, filename, output_dir)` | 保存 DataFrame 为 CSV |
| `save_figure(fig, filename, output_dir, dpi)` | 保存图表 |
| `save_markdown(content, filename, output_dir)` | 保存 Markdown |
| `generate_quality_checklist(items, chapter_num)` | 生成质量验证清单 |

---

# Prompt-02: 描述性统计分析

## 一、任务概述

### 1.1 本次任务是什么

对 139,919 条清洗后的金融新闻完成**时间趋势、行业分布、影响等级、关键词热度、来源偏差、文本长度**的多维度可视化统计分析，输出 10+ 张高质量图表和 1 份描述性统计报告。

本章是全流程分析的**数据理解阶段**，目标是建立对数据集的全面认知，为后续文本挖掘（ch03）、特征工程（ch04）、事件分析（ch05）提供数据分布基线。对应 `docs/flow_design.md` 第三章，回答 RQ-Sub-1（新闻发布时间分布规律）和 RQ-Sub-2（行业分类热度分布）。

### 1.2 从什么数据出发

| 数据项 | 来源路径 | 说明 |
|--------|----------|------|
| 清洗后数据 | `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` | 139,919行 x 24列 |
| 分类统计表 | `outputs/ch01_data_preprocessing/ch01_category_statistics.csv` | 可直接使用 |
| 关键词统计表 | `outputs/ch01_data_preprocessing/ch01_keyword_statistics.csv` | 可直接使用 |

关键字段：`date`(datetime), `title`(str), `description`(str), `full_text`(str), `categories`(str, 竖线分隔), `categories_list`(list), `matched_keywords`(str), `keywords_list`(list), `impact_tier`(category: LOW/MEDIUM/HIGH), `relevance_score`(int: 1-11), `has_negation`(bool), `source_file`(str), `text_length`(int), `year`, `month`, `day_of_week`, `is_weekend`

### 1.3 可以采用什么方法

| 分析维度 | 方法 | 关键函数 |
|----------|------|----------|
| 时间分布 | 年度/月度/星期频次统计 + 折线图/柱状图 | `df.groupby('year').size()`, `df['day_of_week'].value_counts()` |
| 行业分布 | 频次统计 + 排名柱状图 + 堆叠面积图 | `categories_list.explode().value_counts()` |
| 影响等级 | 占比饼图 + 时间演变折线图 | `df['impact_tier'].value_counts(normalize=True)` |
| 关键词热度 | Top50 词频柱状图 + 词云图 | `keywords_list.explode().value_counts().head(50)` |
| 来源偏差 | 来源覆盖度统计 + 年度分布对比 | `df.groupby(['source_file','year']).size()` |
| 文本长度 | 直方图 + 箱线图 | `df['text_length'].describe()` |
| 交叉分析 | 行业×影响等级热力图 | `pd.crosstab()`, `sns.heatmap()` |

**替代方法**：词云可用 pyecharts（交互式但配置复杂）；热力图可用 plotly（交互式）。

## 二、执行步骤

### Step 1: 数据加载与验证

**本步骤要做什么**
加载 ch01 清洗后数据，验证行数（139,919）、列数（24）、缺失率（0%），确认数据完整性。

**代码框架**:
```python
df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_cleaned_data.csv", parse_dates=['date'])
print(f"数据形状: {df.shape}")
print(f"缺失值总数: {df.isnull().sum().sum()}")
print(f"时间范围: {df['date'].min()} ~ {df['date'].max()}")
assert len(df) == 139919, f"行数不符: {len(df)}"
assert df.isnull().sum().sum() == 0, "存在缺失值"
```

**本步骤输出产物**
- 无独立文件（内存中验证通过即可）

### Step 2: 新闻发布时间分布分析

**本步骤要做什么**
按年度、月度、星期、工作日vs周末统计新闻数量，绘制4子图时间分布图。

**代码框架**:
```python
fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=150)

# 年度趋势
yearly = df.groupby('year').size()
axes[0, 0].plot(yearly.index, yearly.values, marker='o', linewidth=2)
axes[0, 0].set_title('年度新闻数量趋势')
axes[0, 0].set_xlabel('年份')
axes[0, 0].set_ylabel('新闻数量')
for x, y in zip(yearly.index, yearly.values):
    axes[0, 0].annotate(f'{y:,}', (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)

# 月度分布
monthly = df.groupby('month').size()
axes[0, 1].bar(monthly.index, monthly.values, color='steelblue')
axes[0, 1].set_title('月度新闻数量分布')
axes[0, 1].set_xlabel('月份')
axes[0, 1].set_ylabel('新闻数量')
axes[0, 1].set_xticks(range(1, 13))

# 星期分布
weekday = df.groupby('day_of_week').size()
weekday_labels = ['周一','周二','周三','周四','周五','周六','周日']
axes[1, 0].bar(range(7), weekday.values, color='coral')
axes[1, 0].set_title('星期新闻数量分布')
axes[1, 0].set_xlabel('星期')
axes[1, 0].set_ylabel('新闻数量')
axes[1, 0].set_xticks(range(7))
axes[1, 0].set_xticklabels(weekday_labels)

# 工作日 vs 周末
wknd = df.groupby('is_weekend').size()
axes[1, 1].pie(wknd.values, labels=['工作日','周末'], autopct='%1.1f%%', startangle=90)
axes[1, 1].set_title('工作日 vs 周末新闻占比')

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch02_time_distribution.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch02_time_distribution.png` — 时间分布4子图

### Step 3: 17个行业分类热度排名与占比

**本步骤要做什么**
展开 categories_list 统计各分类新闻数量，绘制水平柱状图，标注占比百分比。

**代码框架**:
```python
# 展开 categories_list 统计
cat_counts = df['categories_list'].explode().value_counts()
cat_pct = (cat_counts / len(df) * 100).round(1)

fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
bars = ax.barh(range(len(cat_counts)), cat_counts.values, color='steelblue')
ax.set_yticks(range(len(cat_counts)))
ax.set_yticklabels(cat_counts.index)
ax.invert_yaxis()
ax.set_xlabel('新闻数量')
ax.set_title('17个行业/事件分类热度排名')

for bar, pct in zip(bars, cat_pct.values):
    ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2,
            f'{bar.get_width():,} ({pct}%)', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch02_category_ranking.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch02_category_ranking.png` — 行业分类排名图

### Step 4: 影响等级分布与时间演变

**本步骤要做什么**
统计 HIGH/MEDIUM/LOW 占比（饼图），绘制月度数量时序图（堆叠面积图）。

**代码框架**:
```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=150)

# 饼图
tier_counts = df['impact_tier'].value_counts()
ax1.pie(tier_counts.values, labels=tier_counts.index, autopct='%1.1f%%', startangle=90)
ax1.set_title('影响等级分布')

# 月度堆叠面积图
df_monthly_tier = df.set_index('date').groupby([pd.Grouper(freq='M'), 'impact_tier']).size().unstack(fill_value=0)
df_monthly_tier.plot.area(ax=ax2, alpha=0.7)
ax2.set_title('影响等级月度时序演变')
ax2.set_xlabel('日期')
ax2.set_ylabel('新闻数量')

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch02_impact_tier_analysis.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch02_impact_tier_analysis.png` — 影响等级分析图

### Step 5: Top 50 高频关键词词频统计 + 词云

**本步骤要做什么**
展开 keywords_list 统计词频，绘制 Top50 水平柱状图，生成词云图。

**代码框架**:
```python
from wordcloud import WordCloud

kw_counts = df['keywords_list'].explode().value_counts().head(50)

# 柱状图
fig, ax = plt.subplots(figsize=(12, 10), dpi=150)
ax.barh(range(len(kw_counts)), kw_counts.values, color='teal')
ax.set_yticks(range(len(kw_counts)))
ax.set_yticklabels(kw_counts.index)
ax.invert_yaxis()
ax.set_title('Top 50 高频关键词')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch02_top50_keywords.png", dpi=150, bbox_inches='tight')
plt.close()

# 词云
all_keywords = df['keywords_list'].explode().value_counts()
wc = WordCloud(width=1200, height=600, background_color='white', max_words=100)
wc.generate_from_frequencies(all_keywords)
wc.to_file(f"{OUTPUT_DIR}/ch02_keyword_wordcloud.png")
```

**本步骤输出产物**
- `ch02_top50_keywords.png` — Top50关键词柱状图
- `ch02_keyword_wordcloud.png` — 关键词词云图

### Step 6: 数据来源覆盖度与偏差分析

**本步骤要做什么**
统计各来源的新闻数量与占比，绘制来源×年度热力图。

**代码框架**:
```python
source_year = df.groupby(['source_file', 'year']).size().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
sns.heatmap(source_year, cmap='YlOrRd', annot=True, fmt='d', linewidths=0.5, ax=ax)
ax.set_title('数据来源 × 年度 新闻数量热力图')
ax.set_xlabel('年份')
ax.set_ylabel('数据来源')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch02_source_bias_analysis.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch02_source_bias_analysis.png` — 来源偏差分析热力图

### Step 7: 文本长度分布 + 交叉分析

**本步骤要做什么**
绘制 text_length 直方图+箱线图；绘制行业×影响等级交叉热力图。

**代码框架**:
```python
fig, axes = plt.subplots(1, 3, figsize=(20, 6), dpi=150)

# 文本长度直方图
axes[0].hist(df['text_length'], bins=50, color='steelblue', edgecolor='white', alpha=0.8)
axes[0].axvline(df['text_length'].mean(), color='red', linestyle='--', label=f"均值={df['text_length'].mean():.0f}")
axes[0].set_title('新闻文本长度分布')
axes[0].set_xlabel('字符数')
axes[0].legend()

# 文本长度箱线图
axes[1].boxplot(df['text_length'], vert=True)
axes[1].set_title('文本长度箱线图')
axes[1].set_ylabel('字符数')

# 行业×影响等级热力图
cat_tier = pd.crosstab(df['categories_list'].explode(), df['impact_tier'])
sns.heatmap(cat_tier, cmap='YlOrRd', annot=True, fmt='d', linewidths=0.5, ax=axes[2])
axes[2].set_title('行业 × 影响等级 交叉热力图')
axes[2].set_xlabel('影响等级')

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch02_text_length_and_cross.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch02_text_length_and_cross.png` — 文本长度分布 + 交叉分析图

### Step 8: 行业年度趋势堆叠面积图

**本步骤要做什么**
取 Top5 行业，绘制年度趋势堆叠面积图，展示各行业的时间演变。

**代码框架**:
```python
top5_cats = df['categories_list'].explode().value_counts().head(5).index.tolist()
df_top5 = df[df['categories_list'].apply(lambda x: any(c in x for c in top5_cats))].copy()
df_top5['primary_cat'] = df_top5['categories_list'].apply(lambda x: next((c for c in top5_cats if c in x), x[0]))

yearly_cat = df_top5.groupby(['year', 'primary_cat']).size().unstack(fill_value=0)
yearly_cat.plot.area(figsize=(14, 6), alpha=0.7)
plt.title('Top5 行业年度新闻数量趋势')
plt.xlabel('年份')
plt.ylabel('新闻数量')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch02_category_yearly_trend.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch02_category_yearly_trend.png` — Top5行业年度趋势图

### Step 9: 描述性统计报告撰写

**本步骤要做什么**
汇总全部统计结果，生成 `ch02_descriptive_stats_report.md`，包含数据概况、各维度分析结论、关键发现。

**本步骤输出产物**
- `ch02_descriptive_stats_report.md` — 描述性统计报告
- `ch02_descriptive_stats.csv` — 描述统计汇总表

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 时间分布图 | ch02_time_distribution.png | PNG | outputs/ch02_descriptive_stats/ | 报告配图 |
| 2 | 行业分类排名图 | ch02_category_ranking.png | PNG | outputs/ch02_descriptive_stats/ | 报告配图 |
| 3 | 影响等级分析图 | ch02_impact_tier_analysis.png | PNG | outputs/ch02_descriptive_stats/ | 报告配图 |
| 4 | Top50关键词图 | ch02_top50_keywords.png | PNG | outputs/ch02_descriptive_stats/ | 报告配图 |
| 5 | 关键词词云图 | ch02_keyword_wordcloud.png | PNG | outputs/ch02_descriptive_stats/ | 报告配图 |
| 6 | 来源偏差分析图 | ch02_source_bias_analysis.png | PNG | outputs/ch02_descriptive_stats/ | 报告配图 |
| 7 | 文本长度+交叉图 | ch02_text_length_and_cross.png | PNG | outputs/ch02_descriptive_stats/ | 报告配图 |
| 8 | 行业年度趋势图 | ch02_category_yearly_trend.png | PNG | outputs/ch02_descriptive_stats/ | 报告配图 |
| 9 | 描述统计汇总表 | ch02_descriptive_stats.csv | CSV | outputs/ch02_descriptive_stats/ | ch03 参考 |
| 10 | 描述性统计报告 | ch02_descriptive_stats_report.md | Markdown | outputs/ch02_descriptive_stats/ | ch03 参考、最终交付 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
1. 词云图基于简单词频，未考虑 TF-IDF 权重，高频通用词（如 market, stock）占比过大
2. 交叉分析仅覆盖行业×影响等级二维，未扩展到行业×时间×来源三维
3. 2021年数据稀疏区间（仅3,548条）仅做标注，未做插值或特殊处理

### 4.2 可进一步优化的方向
1. 使用 TF-IDF 加权词云，突出行业区分性关键词；或按行业分组生成独立词云
2. 新增"行业×来源×时间"三维交叉分析，识别来源的行业偏好和时间演变趋势
3. 对 2021 年稀疏区间做线性插值补全时序图，或将其标注为独立分析区间

### 4.3 工程落地建议
- 14万条数据的词频统计建议使用 `collections.Counter` 或 `pandas.Series.value_counts()`，避免逐行循环
- 词云图 DPI 建议 ≥ 200，确保大屏展示清晰度

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
1. 如果 wordcloud 库未安装，需确认是否安装或跳过词云图

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| categories_list 解析失败 | 列类型为 str 而非 list | 使用 `ast.literal_eval` 转换 | 否 |
| wordcloud 未安装 | ImportError | `pip install wordcloud`，或跳过词云图 | 否 |
| 2021年数据量异常少 | 年度统计中 2021 < 5000 | 在报告中标注，不做插值 | 否 |
| 图表中文显示异常 | 方块或问号 | 检查 matplotlib 字体配置 | 否 |

---

---

# Prompt-03: 文本挖掘与情感分析

## 一、任务概述

### 1.1 本次任务是什么

本章节包含两大核心模块：

**模块一：情感分析** — 基于 FinBERT（ProsusAI/finbert）对全量 139,919 条新闻的 `full_text` 进行情感判别（positive/negative/neutral），输出每条新闻的情感标签与置信度，并分析情感时序演变规律。

**模块二：主题建模** — 对新闻文本进行主题建模（BERTopic 主选 + LDA 对比），自动划分为 8-15 个金融主题簇，并与现有 17 个 categories 分类进行对比分析。

本章对应 `docs/flow_design.md` 第四章，回答 RQ-Sub-3（FinBERT 情感判别效果）和 RQ-Sub-4（新闻主题自动聚类）。

### 1.2 从什么数据出发

| 数据项 | 来源路径 | 说明 |
|--------|----------|------|
| 清洗后数据 | `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` | 139,919行 x 24列 |
| 描述统计报告 | `outputs/ch02_descriptive_stats/ch02_descriptive_stats_report.md` | 参考 |

### 1.3 可以采用什么方法

**情感分析**: FinBERT 预训练模型推理，GPU 优先（batch_size=32），CPU 备选（batch_size=8）。
**主题建模**: BERTopic（nr_topics='auto'）主选，LDA（gensim）对比，Coherence Score (c_v) 评估。
**替代方法**: VADER（规则方法，速度快但精度低）、TextBlob（金融领域效果差）、NMF（速度快但可解释性不如 LDA）。

## 二、执行步骤

### Step 1: FinBERT 模型加载与环境配置

**本步骤要做什么**
检测 GPU 可用性，加载 ProsusAI/finbert 模型，配置批量推理参数。

**代码框架**:
```python
import torch
from transformers import pipeline

device = 0 if torch.cuda.is_available() else -1
batch_size = 32 if device == 0 else 8
print(f"使用设备: {'GPU' if device == 0 else 'CPU'}, batch_size={batch_size}")

sentiment_pipeline = pipeline(
    'sentiment-analysis',
    model='ProsusAI/finbert',
    device=device,
    truncation=True,
    max_length=512
)
```

**本步骤输出产物**
- 无独立文件（模型加载到内存）

### Step 2: 全量新闻情感标签生成

**本步骤要做什么**
对 full_text 列逐批推理，输出 sentiment（positive/negative/neutral）和 confidence（置信度），添加 sentiment_score 数值列（positive=1, neutral=0, negative=-1）。

**代码框架**:
```python
from tqdm import tqdm

texts = df['full_text'].tolist()
results = []
for i in tqdm(range(0, len(texts), batch_size), desc="FinBERT 推理中"):
    batch = texts[i:i+batch_size]
    batch_results = sentiment_pipeline(batch)
    results.extend(batch_results)

df['sentiment'] = [r['label'].lower() for r in results]
df['confidence'] = [r['score'] for r in results]
df['sentiment_score'] = df['sentiment'].map({'positive': 1, 'neutral': 0, 'negative': -1})

# 保存
df[['sentiment', 'confidence', 'sentiment_score']].to_csv(
    f"{OUTPUT_DIR}/ch03_sentiment_labels.csv", index=False
)
print(f"情感标签覆盖率: {df['sentiment'].notna().mean()*100:.1f}%")
```

**本步骤完成后的检查标准**
- 情感标签覆盖率 = 100%
- 情感分布合理（任一类别占比 < 80%）

**本步骤输出产物**
- `ch03_sentiment_labels.csv` — 情感标签数据（含 sentiment, confidence, sentiment_score 列）

### Step 3: 情感分布统计 + 行业交叉分析

**本步骤要做什么**
统计三种情感占比（饼图），按主分类统计情感均值（箱线图）。

**代码框架**:
```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=150)

# 情感分布饼图
sent_counts = df['sentiment'].value_counts()
ax1.pie(sent_counts.values, labels=sent_counts.index, autopct='%1.1f%%', startangle=90)
ax1.set_title('FinBERT 情感分布')

# 行业情感箱线图
df['primary_category'] = df['categories_list'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else 'Unknown')
top10_cats = df['primary_category'].value_counts().head(10).index
df_top10 = df[df['primary_category'].isin(top10_cats)]
order = df_top10.groupby('primary_category')['sentiment_score'].mean().sort_values().index
sns.boxplot(data=df_top10, x='primary_category', y='sentiment_score', order=order, ax=ax2)
ax2.set_title('Top10 行业情感得分分布')
ax2.set_xlabel('行业分类')
ax2.set_ylabel('情感得分')
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch03_sentiment_by_category.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch03_sentiment_distribution.png` — 情感分布饼图
- `ch03_sentiment_by_category.png` — 行业情感对比箱线图

### Step 4: 情感时序演变 + 事件窗口分析

**本步骤要做什么**
计算月度情感均值折线图；定义 COVID-19（2020-03）、俄乌战争（2022-02）事件窗口，分析前后情感变化。

**代码框架**:
```python
df['date'] = pd.to_datetime(df['date'])
monthly_sentiment = df.set_index('date').resample('M')['sentiment_score'].agg(['mean','std','count'])

fig, axes = plt.subplots(2, 1, figsize=(14, 10), dpi=150)

# 月度情感趋势
axes[0].plot(monthly_sentiment.index, monthly_sentiment['mean'], linewidth=1.5, label='月度均值')
axes[0].fill_between(monthly_sentiment.index,
                     monthly_sentiment['mean'] - monthly_sentiment['std'],
                     monthly_sentiment['mean'] + monthly_sentiment['std'],
                     alpha=0.2, label='±1std')
axes[0].axhline(0, color='gray', linestyle='--')
axes[0].set_title('月度情感得分趋势')
axes[0].legend()

# 事件窗口分析
events = {'COVID-19': '2020-03-01', '俄乌战争': '2022-02-01'}
colors = ['red', 'blue']
for (name, date_str), color in zip(events.items(), colors):
    event_date = pd.Timestamp(date_str)
    axes[1].axvline(event_date, color=color, linestyle='--', label=name)
axes[1].plot(monthly_sentiment.index, monthly_sentiment['mean'], linewidth=1.5)
axes[1].set_title('重大事件窗口情感变化')
axes[1].legend()

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch03_sentiment_timeline.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch03_sentiment_timeline.png` — 情感时序趋势 + 事件窗口图
- `ch03_event_window_sentiment.png` — 事件窗口情感变化图

### Step 5: 文本预处理 + BERTopic 主题建模

**本步骤要做什么**
对 full_text 进行小写转换、去停用词、lemmatization；使用 BERTopic 自动确定主题数并训练。

**代码框架**:
```python
import spacy
from bertopic import BERTopic

# 文本预处理
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

def preprocess_text(text):
    doc = nlp(str(text).lower())
    return ' '.join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct and len(token) > 2])

docs = [preprocess_text(t) for t in tqdm(df['full_text'], desc="文本预处理")]

# BERTopic
topic_model = BERTopic(nr_topics='auto', verbose=True)
topics, probs = topic_model.fit_transform(docs)

# 保存
topic_df = pd.DataFrame({'topic_id': topics, 'topic_prob': probs})
topic_df.to_csv(f"{OUTPUT_DIR}/ch03_topic_model_results.csv", index=False)

# 主题信息
topic_info = topic_model.get_topic_info()
print(f"识别到 {len(topic_info)} 个主题")
print(topic_info.head(15))
```

**本步骤完成后的检查标准**
- 主题数量在 8-15 范围内
- 每个主题有明确的 Top10 关键词

**本步骤输出产物**
- `ch03_topic_model_results.csv` — 主题分类结果（含 topic_id, topic_prob）
- `ch03_topic_visualization.html` — BERTopic 交互式可视化

### Step 6: LDA 对比 + 主题时序分析 + 报告

**本步骤要做什么**
使用 gensim LDA 训练对比模型；计算 Coherence Score；绘制主题热度时序热力图；生成情感分析报告和主题分析报告。

**代码框架**:
```python
import gensim
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel

# LDA
texts_split = [d.split() for d in docs]
dictionary = corpora.Dictionary(texts_split)
dictionary.filter_extremes(no_below=10, no_above=0.5)
corpus = [dictionary.doc2bow(t) for t in texts_split]

best_score, best_n = 0, 8
for n in range(8, 16):
    lda = LdaModel(corpus, num_topics=n, id2word=dictionary, random_state=42, passes=5)
    cm = CoherenceModel(model=lda, texts=texts_split, dictionary=dictionary, coherence='c_v')
    score = cm.get_coherence()
    print(f"Topics={n}, Coherence={score:.4f}")
    if score > best_score:
        best_score, best_n = score, n

print(f"\n最优主题数: {best_n}, Coherence: {best_score:.4f}")

# 主题时序热力图
df['topic_id'] = topics
topic_monthly = df.groupby([pd.Grouper(key='date', freq='M'), 'topic_id']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(16, 8), dpi=150)
sns.heatmap(topic_monthly.T, cmap='YlOrRd', ax=ax)
ax.set_title('主题热度月度时序热力图')
ax.set_xlabel('月份')
ax.set_ylabel('主题ID')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch03_topic_timeline_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch03_topic_timeline_heatmap.png` — 主题热度时序热力图
- `ch03_sentiment_analysis_report.md` — 情感分析报告
- `ch03_topic_analysis_report.md` — 主题分析报告

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 情感标签数据 | ch03_sentiment_labels.csv | CSV | outputs/ch03_text_mining_sentiment/ | ch04, ch05 |
| 2 | 主题分类结果 | ch03_topic_model_results.csv | CSV | outputs/ch03_text_mining_sentiment/ | ch04 |
| 3 | 情感分布饼图 | ch03_sentiment_distribution.png | PNG | outputs/ch03_text_mining_sentiment/ | 报告配图 |
| 4 | 行业情感对比图 | ch03_sentiment_by_category.png | PNG | outputs/ch03_text_mining_sentiment/ | 报告配图 |
| 5 | 情感时序趋势图 | ch03_sentiment_timeline.png | PNG | outputs/ch03_text_mining_sentiment/ | 报告配图 |
| 6 | 事件窗口情感图 | ch03_event_window_sentiment.png | PNG | outputs/ch03_text_mining_sentiment/ | 报告配图 |
| 7 | 主题可视化 | ch03_topic_visualization.html | HTML | outputs/ch03_text_mining_sentiment/ | 报告配图 |
| 8 | 主题时序热力图 | ch03_topic_timeline_heatmap.png | PNG | outputs/ch03_text_mining_sentiment/ | 报告配图 |
| 9 | 情感分析报告 | ch03_sentiment_analysis_report.md | Markdown | outputs/ch03_text_mining_sentiment/ | ch05, 最终交付 |
| 10 | 主题分析报告 | ch03_topic_analysis_report.md | Markdown | outputs/ch03_text_mining_sentiment/ | ch05, 最终交付 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
1. FinBERT 对否定句（not, no, never, despite）的处理可能不够精确，导致情感标签翻转
2. BERTopic 在 14 万条文本上训练时间较长（CPU 可能需要数小时，GPU 约 30 分钟）
3. LDA 对比模型的 Coherence Score 可能偏低（< 0.4）
4. 情感分析仅使用单一模型，缺乏交叉验证

### 4.2 可进一步优化的方向
1. **否定句修正**：加入后处理规则，检测否定词后翻转情感标签；或使用 FinBERT-large（否定句 F1 提升 ~5%）
2. **训练加速**：预计算 sentence-transformers Embedding 缓存至磁盘，BERTopic 直接加载；CPU 环境可降采样至 50% 数据
3. **模型升级**：替换为 FinGPT（清华金融大模型）或 ChatGLM-Finance，提升金融领域精度
4. **多维评估**：增加 Silhouette Score、主题多样性（Topic Diversity）指标，不仅依赖 Coherence Score

### 4.3 工程落地建议
- GPU 推理建议 batch_size=32，CPU 建议 batch_size=8；内存不足时分批加载（每批 2 万条）
- BERTopic embedding 缓存文件约 2-3GB，需确保磁盘空间充足
- spaCy 模型需单独安装：`python -m spacy download en_core_web_sm`

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
1. 如果 GPU 不可用且 CPU 推理时间过长（>2小时），需确认是否降采样执行

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| GPU 内存不足 | CUDA OOM | 降低 batch_size 至 8 或 4 | 否 |
| spaCy 模型未安装 | OSError | `python -m spacy download en_core_web_sm` | 否 |
| BERTopic 训练超时 | CPU > 3小时 | 降采样至 50% 数据 | 是 |
| LDA Coherence < 0.3 | score < 0.3 | 调整 no_below/no_above 参数 | 否 |

---

# Prompt-04: 特征工程

## 一、任务概述

### 1.1 本次任务是什么

基于情感标签、主题分类、关键词统计、时间特征等维度，构建标准化的新闻舆情特征集，输出按日期聚合的**日频特征表**（目标 ≥ 30 个特征），为后续事件驱动分析（ch05）和看板展示（ch06）提供可直接使用的特征输入。

本章对应 `docs/flow_design.md` 第五章，回答 RQ-Sub-5（如何构建标准化日频舆情特征集）。

### 1.2 从什么数据出发

| 数据项 | 来源路径 | 说明 |
|--------|----------|------|
| 清洗后数据 | `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` | 基础字段 |
| 情感标签 | `outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv` | sentiment, confidence, sentiment_score |
| 主题分类 | `outputs/ch03_text_mining_sentiment/ch03_topic_model_results.csv` | topic_id, topic_prob |

### 1.3 可以采用什么方法

7类特征构造：情感特征、主题特征、关键词特征、影响等级特征、文本统计特征、时间特征、交叉特征。共线性检测使用 VIF（方差膨胀因子）。
**替代方法**: 基于树模型的特征重要性（RandomForest feature_importances_）可与 VIF 互补。

## 二、执行步骤

### Step 1: 数据合并

**本步骤要做什么**
将 ch01 清洗数据、ch03 情感标签、ch03 主题分类按行索引合并为统一 DataFrame。

**代码框架**:
```python
df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_cleaned_data.csv", parse_dates=['date'])
sentiment = pd.read_csv("outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv")
topics = pd.read_csv("outputs/ch03_text_mining_sentiment/ch03_topic_model_results.csv")

df['sentiment'] = sentiment['sentiment'].values
df['confidence'] = sentiment['confidence'].values
df['sentiment_score'] = sentiment['sentiment_score'].values
df['topic_id'] = topics['topic_id'].values
df['topic_prob'] = topics['topic_prob'].values
```

**本步骤输出产物**
- 无独立文件（内存中合并）

### Step 2-7: 七类特征构造

**本步骤要做什么**
按日期聚合，分别构造情感特征、主题特征、关键词特征、影响等级特征、文本统计特征、时间特征、交叉特征。

**代码框架**:
```python
features = pd.DataFrame(index=pd.date_range(df['date'].min(), df['date'].max(), freq='D'))
features.index.name = 'date'

# --- 情感特征 ---
daily_sent = df.groupby('date')['sentiment_score'].agg(['mean','std'])
daily_sent.columns = ['sentiment_mean', 'sentiment_std']
daily_sent['positive_ratio'] = df[df['sentiment']=='positive'].groupby('date').size() / df.groupby('date').size()
daily_sent['negative_ratio'] = df[df['sentiment']=='negative'].groupby('date').size() / df.groupby('date').size()
daily_sent['polarization_idx'] = abs(daily_sent['positive_ratio'] - daily_sent['negative_ratio'])

# --- 主题特征 ---
topic_counts = df.groupby(['date','topic_id']).size().unstack(fill_value=0)
topic_counts.columns = [f'topic_{c}_count' for c in topic_counts.columns]
topic_diversity = df.groupby('date')['topic_id'].apply(lambda x: -np.sum(np.unique(x, return_counts=True)[1]/len(x) * np.log(np.unique(x, return_counts=True)[1]/len(x)))

# --- 影响等级特征 ---
tier_counts = df.groupby(['date','impact_tier']).size().unstack(fill_value=0)
tier_counts['impact_weighted'] = tier_counts.get('HIGH',0)*3 + tier_counts.get('MEDIUM',0)*2 + tier_counts.get('LOW',0)*1
tier_total = df.groupby('date').size()
tier_counts = tier_counts.div(tier_total, axis=0).add_suffix('_ratio')
tier_counts['impact_weighted'] = df.groupby('date').apply(lambda x: (x['impact_tier'].map({'HIGH':3,'MEDIUM':2,'LOW':1})*x['relevance_score']).mean())

# --- 文本统计特征 ---
text_stats = df.groupby('date').agg(
    avg_text_length=('text_length','mean'),
    news_count=('title','size'),
    negation_ratio=('has_negation','mean'),
    avg_category_count=('category_count','mean')
)

# --- 时间特征 ---
features['day_of_week'] = features.index.dayofweek
features['month'] = features.index.month
features['is_weekend'] = features['day_of_week'].isin([5,6]).astype(int)
features['is_month_end'] = features.index.is_month_end.astype(int)
features['is_quarter_end'] = features.index.is_quarter_end.astype(int)

# --- 合并所有特征 ---
features = features.join(daily_sent).join(topic_diversity.rename('topic_shannon_entropy'))
features = features.join(text_stats)
features = features.join(tier_counts)

# 前向填充缺失值
features = features.ffill().bfill()
```

**本步骤输出产物**
- 无独立文件（中间特征 DataFrame）

### Step 8: 特征合并 + 缺失处理 + VIF 检测

**本步骤要做什么**
合并全部特征，检查覆盖率，计算 VIF，绘制相关性热力图，生成特征字典。

**代码框架**:
```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

print(f"特征总数: {features.shape[1]}")
print(f"日期跨度: {features.shape[0]} 天")
print(f"缺失率:\n{features.isnull().mean().sort_values(ascending=False).head(10)}")

# 相关性热力图
corr = features.corr()
fig, ax = plt.subplots(figsize=(20, 16), dpi=150)
sns.heatmap(corr, cmap='RdBu_r', center=0, ax=ax, annot=False)
ax.set_title('特征相关性热力图')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch04_feature_correlation_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()

# VIF 检测
numeric_cols = features.select_dtypes(include=[np.number]).columns
vif_data = pd.DataFrame({'feature': numeric_cols})
vif_data['VIF'] = [variance_inflation_factor(features[numeric_cols].values, i) for i in range(len(numeric_cols))]
vif_data.to_csv(f"{OUTPUT_DIR}/ch04_vif_results.csv", index=False)
print(f"VIF > 10 的特征: {vif_data[vif_data['VIF']>10]['feature'].tolist()}")

# 保存日频特征表
features.to_csv(f"{OUTPUT_DIR}/ch04_daily_features.csv")

# 特征字典
catalog = f"# 特征字典\n\n| 特征名 | 定义 | 类型 | 计算方式 |\n|--------|------|------|----------|\n"
for col in features.columns:
    catalog += f"| {col} | {col} | {features[col].dtype} | 见代码 |\n"
with open(f"{OUTPUT_DIR}/ch04_feature_catalog.md", 'w') as f:
    f.write(catalog)
```

**本步骤输出产物**
- `ch04_daily_features.csv` — 日频舆情特征表
- `ch04_feature_catalog.md` — 特征字典
- `ch04_feature_correlation_heatmap.png` — 特征相关性热力图
- `ch04_vif_results.csv` — VIF 共线性检测结果

## 三、产物总览与结构说明

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 日频舆情特征表 | ch04_daily_features.csv | CSV | outputs/ch04_feature_engineering/ | ch05, ch06 |
| 2 | 特征字典 | ch04_feature_catalog.md | Markdown | outputs/ch04_feature_engineering/ | ch05, ch06 |
| 3 | 特征相关性热力图 | ch04_feature_correlation_heatmap.png | PNG | outputs/ch04_feature_engineering/ | 报告配图 |
| 4 | VIF 检测结果 | ch04_vif_results.csv | CSV | outputs/ch04_feature_engineering/ | 参考 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
1. 特征构造基于简单当日聚合，无时间滞后信息，无法捕捉趋势动量
2. 交叉特征仅覆盖 Top5 行业，可能遗漏重要交叉关系
3. 特征字典仅标注"见代码"，缺乏业务含义解释

### 4.2 可进一步优化的方向
1. **滞后特征**：补充 sentiment_mean_lag1/3/7、news_count_lag7、topic_entropy_lag3 等滞后特征
2. **滚动窗口**：补充 7/14 天滚动均值（sentiment_mean_7d）、滚动标准差（sentiment_std_7d，波动率）
3. **变化率特征**：补充情感变化率（sentiment_change = 今日 - 昨日）、新闻量环比增长率
4. **共线性处理**：对 VIF > 10 的特征执行 PCA 降维或删除冗余特征，保留解释力

### 4.3 特征字典业务定义补充

| 特征名 | 业务定义 | 计算方式 | 预期范围 |
|--------|----------|----------|----------|
| sentiment_mean | 日均情感得分 | 当日全部新闻 sentiment_score 均值 | [-1, 1] |
| sentiment_std | 情感波动率 | 当日 sentiment_score 标准差 | [0, 1] |
| positive_ratio | 正面新闻占比 | 当日 positive 新闻数 / 总数 | [0, 1] |
| negative_ratio | 负面新闻占比 | 当日 negative 新闻数 / 总数 | [0, 1] |
| polarization_idx | 舆情极化指数 | abs(positive_ratio - negative_ratio)，反映舆情分化程度 | [0, 1] |
| topic_shannon_entropy | 主题多样性 | 各主题占比的 Shannon 熵，越高表示话题越分散 | [0, ln(N)] |
| impact_weighted | 影响力加权得分 | HIGH×3 + MEDIUM×2 + LOW×1 的日均值 | [1, 3] |
| news_count | 日新闻总量 | 当日新闻条数 | [0, ~500] |
| negation_ratio | 否定表述占比 | 当日 has_negation=True 的比例 | [0, 1] |

## 五、异常处理与问题反馈机制

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 特征数 < 30 | len(features.columns) < 30 | 增加更多交叉特征或滚动特征 | 是 |
| 全缺失列 | 某列缺失率 = 100% | 删除该列 | 否 |
| VIF > 50 | 极高共线性 | 删除或合并高 VIF 特征 | 是 |

---

# Prompt-05: 事件驱动策略分析

## 一、任务概述

### 1.1 本次任务是什么

基于 impact_tier、relevance_score、情感标签等维度，构建新闻影响力评估体系，识别高影响力新闻事件，分析事件发布后的舆情扩散模式，输出事件日历与影响力评分。

**重要说明**: 因数据集不含股价数据，本章聚焦**舆情层面的事件影响力分析**，不涉及交易策略回测。

本章对应 `docs/flow_design.md` 第五章，回答 RQ-Sub-6（高影响力新闻事件共性特征与舆情扩散）。

### 1.2 从什么数据出发

| 数据项 | 来源路径 | 说明 |
|--------|----------|------|
| 清洗后数据 | `outputs/ch01_data_preprocessing/ch01_cleaned_data.csv` | impact_tier, relevance_score, categories, date |
| 情感标签 | `outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv` | sentiment, sentiment_score |
| 日频特征 | `outputs/ch04_feature_engineering/ch04_daily_features.csv` | 日频舆情特征 |

### 1.3 可以采用什么方法

事件识别（impact_tier=HIGH + relevance_score≥7）、事件分类（基于 categories + keywords 规则）、窗口分析（前后7天）、影响力评分（多维度加权）。
**替代方法**: DBSCAN 密度聚类、AHP 层次分析法。

## 二、执行步骤

### Step 1: 高影响力事件筛选

**本步骤要做什么**
筛选 impact_tier=HIGH 且 relevance_score≥7 的新闻，统计事件数量和行业分布。

**代码框架**:
```python
df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_cleaned_data.csv", parse_dates=['date'])
sentiment = pd.read_csv("outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv")
df['sentiment_score'] = sentiment['sentiment_score'].values

events = df[(df['impact_tier']=='HIGH') & (df['relevance_score']>=7)].copy()
print(f"高影响力事件数量: {len(events)}")
print(f"行业分布:\n{events['categories_list'].explode().value_counts().head(10)}")
```

**本步骤输出产物**
- 无独立文件（内存中筛选）

### Step 2: 事件类型分类 + 窗口分析

**本步骤要做什么**
基于 categories 和 keywords 将事件分为政策类/财报类/地缘类/行业类/其他；定义前后7天窗口，计算情感变化。

**代码框架**:
```python
import ast

def classify_event(row):
    cats = row['categories_list'] if isinstance(row['categories_list'], list) else ast.literal_eval(row['categories_list'])
    cats_str = ' '.join(cats).lower()
    if any(k in cats_str for k in ['policy', 'regulation', 'government', 'rbi', 'tax']):
        return '政策类'
    elif any(k in cats_str for k in ['earning', 'result', 'revenue', 'profit', 'q1', 'q2', 'q3', 'q4']):
        return '财报类'
    elif any(k in cats_str for k in ['war', 'conflict', 'geopolitical', 'sanction', 'oil']):
        return '地缘类'
    elif any(k in cats_str for k in ['bank', 'fintech', 'it', 'pharma', 'auto']):
        return '行业类'
    else:
        return '其他'

events['event_type'] = events.apply(classify_event, axis=1)

# 窗口分析
WINDOW = 7
event_impacts = []
for _, event in events.iterrows():
    event_date = event['date']
    window_df = df[(df['date'] >= event_date - pd.Timedelta(days=WINDOW)) &
                   (df['date'] <= event_date + pd.Timedelta(days=WINDOW))]
    baseline = df[(df['date'] < event_date - pd.Timedelta(days=WINDOW)) &
                  (df['date'] >= event_date - pd.Timedelta(days=WINDOW*3))]
    event_impacts.append({
        'date': event_date,
        'title': event['title'],
        'event_type': event['event_type'],
        'relevance_score': event['relevance_score'],
        'window_sentiment_mean': window_df['sentiment_score'].mean(),
        'baseline_sentiment_mean': baseline['sentiment_score'].mean() if len(baseline) > 0 else 0,
        'sentiment_change': window_df['sentiment_score'].mean() - (baseline['sentiment_score'].mean() if len(baseline) > 0 else 0),
        'affected_categories': ', '.join(event['categories_list'][:3]) if isinstance(event['categories_list'], list) else str(event['categories_list'])[:50],
    })

impact_df = pd.DataFrame(event_impacts)
```

### Step 3: 影响力评分 + 事件日历 + 可视化

**本步骤要做什么**
构建综合影响力评分，生成事件日历 CSV，绘制事件分析图表。

**代码框架**:
```python
# 影响力评分
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
impact_df['breadth'] = impact_df['affected_categories'].apply(lambda x: len(x.split(', ')))
for col in ['relevance_score', 'sentiment_change', 'breadth']:
    impact_df[f'{col}_norm'] = scaler.fit_transform(impact_df[[col]])
impact_df['influence_score'] = (0.3 * impact_df['relevance_score_norm'] +
                                 0.3 * impact_df['sentiment_change_norm'].abs() +
                                 0.2 * impact_df['breadth_norm'] +
                                 0.2 * impact_df['window_sentiment_mean'].abs())

# 保存
impact_df.sort_values('date').to_csv(f"{OUTPUT_DIR}/ch05_event_calendar.csv", index=False)
impact_df.sort_values('influence_score', ascending=False).to_csv(f"{OUTPUT_DIR}/ch05_influence_score.csv", index=False)

# 可视化
fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=150)

# 事件类型分布
type_counts = impact_df['event_type'].value_counts()
axes[0,0].pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
axes[0,0].set_title('事件类型分布')

# 行业事件影响力
industry_impact = impact_df.groupby('affected_categories')['influence_score'].mean().sort_values(ascending=False).head(10)
axes[0,1].barh(range(len(industry_impact)), industry_impact.values)
axes[0,1].set_yticks(range(len(industry_impact)))
axes[0,1].set_yticklabels(industry_impact.index)
axes[0,1].invert_yaxis()
axes[0,1].set_title('Top10 行业平均影响力评分')

# 情感变化分布
axes[1,0].hist(impact_df['sentiment_change'], bins=30, color='steelblue', edgecolor='white')
axes[1,0].axvline(0, color='red', linestyle='--')
axes[1,0].set_title('事件窗口情感变化分布')

# 传染效应热力图
event_types = impact_df['event_type'].unique()
contagion = pd.DataFrame(index=event_types, columns=event_types, dtype=float)
for t1 in event_types:
    for t2 in event_types:
        t1_sent = impact_df[impact_df['event_type']==t1]['sentiment_change']
        t2_sent = impact_df[impact_df['event_type']==t2]['sentiment_change']
        contagion.loc[t1, t2] = t1_sent.corr(t2_sent) if len(t1_sent) > 2 and len(t2_sent) > 2 else 0
sns.heatmap(contagion.astype(float), cmap='RdBu_r', center=0, annot=True, ax=axes[1,1])
axes[1,1].set_title('事件类型间情感传染效应')

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/ch05_event_analysis.png", dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤输出产物**
- `ch05_event_calendar.csv` — 事件日历
- `ch05_influence_score.csv` — 影响力评分表
- `ch05_event_analysis.png` — 事件分析4子图
- `ch05_event_analysis_report.md` — 事件分析报告

## 三、产物总览与结构说明

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 事件日历 | ch05_event_calendar.csv | CSV | outputs/ch05_event_driven_strategy/ | ch06 |
| 2 | 影响力评分表 | ch05_influence_score.csv | CSV | outputs/ch05_event_driven_strategy/ | ch06 |
| 3 | 事件分析图 | ch05_event_analysis.png | PNG | outputs/ch05_event_driven_strategy/ | 报告配图 |
| 4 | 事件分析报告 | ch05_event_analysis_report.md | Markdown | outputs/ch05_event_driven_strategy/ | ch06, 最终交付 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
1. 无股价/指数数据，无法验证舆情特征与市场波动的相关性
2. 事件分类基于规则匹配，未利用文本语义信息
3. 影响力评分权重为人工设定，缺乏数据驱动校准

### 4.2 可进一步优化的方向
1. **市场关联验证**：接入 NIFTY 50 指数或个股 OHLCV 数据，计算舆情特征与收益率/波动率的 Granger 因果检验和 Pearson 相关系数
2. **事件语义聚类**：使用 DBSCAN 对事件文本 Embedding 做密度聚类，自动发现事件群（替代规则分类）
3. **传播网络图**：构建行业间舆情传染有向图（行业A → 行业B），分析传播路径和延迟
4. **评分校准**：使用回归模型（如 Ridge）拟合影响力评分与实际市场影响，校准权重

## 五、异常处理与问题反馈机制

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 高影响力事件 < 10 | len(events) < 10 | 降低 relevance_score 阈值至 5 | 是 |
| baseline 数据不足 | len(baseline) == 0 | 扩大 baseline 窗口 | 否 |

---

# Prompt-06: 可视化看板与总结报告

## 一、任务概述

### 1.1 本次任务是什么

构建交互式 Streamlit 看板，整合行业新闻热度、舆情情绪时序、主题演变、事件影响力等核心指标，并输出综合分析报告。

本章对应 `docs/flow_design.md` 第六章，是全流程的**收尾章节**。

### 1.2 从什么数据出发

全部前序章节产物：`outputs/ch01~ch04, ch05/*/`

### 1.3 可以采用什么方法

Streamlit 多页面布局 + Plotly 交互式图表 + Markdown 综合报告。

## 二、执行步骤

### Step 1: Streamlit 框架搭建 + 概览页

**本步骤要做什么**
创建 `src/ch06_dashboard_summary/dashboard.py`，配置多页面布局，实现概览页（KPI 卡片）。

**代码框架**:
```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="金融新闻舆情分析看板", layout="wide")

# 数据加载
@st.cache_data
def load_data():
    df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_cleaned_data.csv", parse_dates=['date'])
    sentiment = pd.read_csv("outputs/ch03_text_mining_sentiment/ch03_sentiment_labels.csv")
    features = pd.read_csv("outputs/ch04_feature_engineering/ch04_daily_features.csv", parse_dates=['date'])
    events = pd.read_csv("outputs/ch05_event_driven_strategy/ch05_event_calendar.csv", parse_dates=['date'])
    df['sentiment_score'] = sentiment['sentiment_score'].values
    return df, features, events

df, features, events = load_data()

# 侧边栏筛选
st.sidebar.title("筛选条件")
date_range = st.sidebar.date_input("日期范围", [df['date'].min(), df['date'].max()])

# KPI 卡片
col1, col2, col3, col4 = st.columns(4)
col1.metric("新闻总量", f"{len(df):,}")
col2.metric("分析时间跨度", f"{(df['date'].max() - df['date'].min()).days} 天")
sent_dist = df['sentiment_score'].describe()
col3.metric("平均情感得分", f"{sent_dist['mean']:.3f}")
col4.metric("高影响力事件", f"{len(events)}")
```

### Step 2-5: 趋势页 + 行业页 + 事件页 + 词云页

**本步骤要做什么**
使用 `st.tabs()` 创建多标签页：时间趋势、行业分析、事件分析、关键词云。

**代码框架**:
```python
tab1, tab2, tab3, tab4 = st.tabs(["📈 时间趋势", "🏭 行业分析", "⚡ 事件分析", "☁️ 关键词云"])

with tab1:
    st.subheader("新闻量与情感时序")
    fig = px.line(features, x='date', y=['sentiment_mean', 'news_count'],
                  title='日频情感得分与新闻量')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("行业热度排名")
    cat_counts = df['categories_list'].explode().value_counts().head(10)
    fig = px.bar(x=cat_counts.values, y=cat_counts.index, orientation='h')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("影响力 Top 20 事件")
    st.dataframe(events.sort_values('influence_score', ascending=False).head(20))

with tab4:
    st.subheader("关键词云")
    from wordcloud import WordCloud
    all_kw = df['keywords_list'].explode().value_counts()
    wc = WordCloud(width=800, height=400, background_color='white')
    wc.generate_from_frequencies(all_kw)
    st.image(wc.to_array())
```

### Step 6: 综合分析报告

**本步骤要做什么**
汇总各章节核心发现，生成 `ch06_comprehensive_report.md`。

**本步骤输出产物**
- `dashboard.py` — Streamlit 看板代码
- `ch06_comprehensive_report.md` — 综合分析报告
- `ch06_key_metrics_table.csv` — 关键指标总览表

## 三、产物总览与结构说明

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | Streamlit 看板 | dashboard.py | Python | src/ch06_dashboard_summary/ | 本地运行 |
| 2 | 综合分析报告 | ch06_comprehensive_report.md | Markdown | outputs/ch06_dashboard_summary/ | 最终交付 |
| 3 | 关键指标总览表 | ch06_key_metrics_table.csv | CSV | outputs/ch06_dashboard_summary/ | 最终交付 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
1. Streamlit 基础组件交互性有限，非技术人员操作门槛较高
2. 仅支持本地运行，无法在线分享
3. 数据为静态快照，无实时更新能力

### 4.2 可进一步优化的方向
1. **交互增强**：补充 Plotly 交互式图表（缩放、悬停、框选），增加联动筛选和下钻功能
2. **部署上线**：部署到 Streamlit Cloud（免费）或 AWS EC2，支持在线访问和分享
3. **实时监控**：接入新闻 API（如 NewsAPI、Google News RSS），实现实时舆情监控和阈值预警推送
4. **用户适配**：增加引导式操作说明、默认视图预设，降低非技术人员的使用门槛

## 五、异常处理与问题反馈机制

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 前序章节产物缺失 | FileNotFoundError | 跳过对应页面，显示提示 | 否 |
| Streamlit 未安装 | ImportError | `pip install streamlit plotly` | 否 |
| 看板启动失败 | 端口占用 | `streamlit run dashboard.py --server.port 8502` | 否 |

---

## 附录A: 完整依赖清单

```
pandas>=2.0
numpy
matplotlib
seaborn
scikit-learn
nltk
transformers
torch
tqdm
openpyxl
spacy
en_core_web_sm
bertopic
gensim
pyLDAvis
wordcloud
plotly
streamlit
statsmodels
```

## 附录B: 输出产物总览表

| 章节 | 数据文件 | 图片文件 | 报告/文档 | 合计 |
|------|----------|----------|-----------|------|
| ch01（已完成） | 4 | 0 | 1 | 5 |
| ch02 | 1 | 8 | 1 | 10 |
| ch03 | 2 | 6 | 2 | 10 |
| ch04 | 3 | 1 | 1 | 5 |
| ch05 | 2 | 1 | 1 | 4 |
| ch06 | 1 | 0 | 1 | 2 |
| **总计** | **13** | **16** | **7** | **36** |
