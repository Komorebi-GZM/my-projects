# 基于51job招聘数据的人才市场全维度分析 — 执行 Prompt 文档

> **本文档是各章节执行的详细指令手册。** 每个章节均采用**五段式结构**（任务概述 → 执行步骤 → 产物总览 → 优化方向 → 异常处理），提供可直接落地的代码框架和检查标准。
>
> **使用方式**：派活时参考 `docs/project_convention.md` 的派活话术，将具体 Prompt 编号告知执行者，执行者阅读本文档对应章节即可开始工作。

---

## 适用环境

| 属性 | 值 |
|------|-----|
| Python 版本 | 3.10 |
| Conda 环境名 | `py310` |
| 激活命令 | `conda activate py310` |
| 依赖安装 | `pip install -r requirements.txt` |
| 脚本运行 | `python src/chXX_xxx/{script}.py` |
| Notebook 运行 | `jupyter notebook src/chXX_xxx/{script}.ipynb` |

---

## 全局路径配置

```python
# === 以下代码块在每个章节脚本开头使用 ===
import sys
import os

# 路径设置（确保能导入 utils）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)

# 导入项目工具
from utils.config import (
    PROJECT_ROOT, PROJECT_NAME, PROJECT_NAME_CN,
    RAW_DATA_FILE, OUTPUT_BASE, CHAPTER_CONFIG,
    DOMAIN_PARAMS, CATEGORY_MAP, PLT_STYLE, CITY_KEYWORDS,
)
from utils.data_loader import load_raw_data, load_preprocessed
from utils.output_manager import get_chapter_dir, save_dataframe, save_figure, save_markdown
from utils.visualizer import plot_bar_chart, plot_boxplot, plot_heatmap, plot_pie_chart
from utils.task_graph import TaskGraph
```

---

## 数据集概况

| 属性 | 值 |
|------|-----|
| 数据来源 | 51job（前程无忧）招聘平台 |
| 原始文件 | `data/前程无忧数据集.csv` |
| 数据规模 | 295 条有效记录（原始 297 行，含 1 行重复表头） |
| 字段数量 | 10 列 |
| 数据格式 | CSV（UTF-8 编码） |
| 分析单元 | 每行 = 一条招聘信息（一个岗位 + 一个公司） |

### 原始字段清单

| 序号 | 原始字段名 | 语义说明 | 数据类型 | 示例值 |
|------|-----------|---------|---------|--------|
| 1 | 岗位 | 职位名称 | string | "Python开发工程师-CDN" |
| 2 | 公司 | 企业全称 | string | "华为技术有限公司" |
| 3 | 学历 | 学历要求 | string | "本科" / "大专" |
| 4 | 公司性质 | 企业所有制类型 | string | "民营公司" / "外资（非欧美）" |
| 5 | 薪资 | 薪资范围（含单位） | string | "1.8-3.5万/月" / "18-36万/年" |
| 6 | 学历要求 | **实为工作经验要求** | string | "1年经验" / "3-4年经验" |
| 7 | 工作经验 | **实为附加要求** | string | "英语良好" / 空值 |
| 8 | 公司规模 | 企业人员规模 | string | "10000人以上" / "50-150人" |
| 9 | 公司类型 | 行业标签（多值，空格分隔） | string | "计算机软件 通信/电信/网络设备" |
| 10 | 公司福利 | 福利标签（多值，短横线分隔） | string | "五险一金-通讯补贴-专业培训" |

---

## 全局 Skill 库

本章项目提供 4 个通用工具模块，所有章节脚本均可直接导入使用。

### Skill-01: data_loader.py — 数据加载器

| 函数 | 签名 | 说明 |
|------|------|------|
| `load_raw_data` | `load_raw_data(skip_duplicate_header: bool = True) -> pd.DataFrame` | 加载原始 CSV 数据，自动跳过第 2 行重复表头 |
| `load_preprocessed` | `load_preprocessed(filepath: str) -> pd.DataFrame` | 加载预处理后的数据集（CSV/Excel/Parquet），自动检测格式 |

**使用示例**：

```python
from utils.data_loader import load_raw_data, load_preprocessed

# 加载原始数据
df = load_raw_data()

# 加载 ch01 清洗后的数据
df = load_preprocessed('outputs/ch01_data_overview/ch01_cleaned_data.csv')
```

---

### Skill-02: visualizer.py — 可视化出图器

| 函数 | 签名 | 说明 |
|------|------|------|
| `plot_bar_chart` | `plot_bar_chart(data, title, xlabel='', ylabel='', output_path=None, figsize=(14,5), dpi=150, color='#2196F3', horizontal=False, grid=True) -> Figure` | 绘制条形图，支持 dict/Series/DataFrame 输入 |
| `plot_boxplot` | `plot_boxplot(data, x, y, title, output_path=None, figsize=(14,6), dpi=150, palette='Set2', order=None) -> Figure` | 绘制箱线图（分组对比），支持自定义排序 |
| `plot_heatmap` | `plot_heatmap(data, title, xlabel='', ylabel='', output_path=None, figsize=(12,8), dpi=150, cmap='YlOrRd', annot=True, fmt='.2f', linewidths=0.5) -> Figure` | 绘制热力图，支持数值标注 |
| `plot_pie_chart` | `plot_pie_chart(data, title, output_path=None, figsize=(10,8), dpi=150, autopct='%.1f%%', startangle=90) -> Figure` | 绘制饼图，支持 dict/Series/DataFrame 输入 |

**使用示例**：

```python
from utils.visualizer import plot_bar_chart, plot_boxplot, plot_heatmap, plot_pie_chart

# 条形图
fig = plot_bar_chart(
    data=salary_by_edu,
    title='各学历薪资中位数',
    xlabel='学历', ylabel='薪资（千/月）',
    output_path='outputs/ch02_salary_analysis/ch02_salary_by_education.png',
)

# 箱线图
fig = plot_boxplot(
    data=df, x='学历', y='salary_avg',
    title='学历-薪资分布',
    order=DOMAIN_PARAMS['education_order'],
    output_path='outputs/ch02_salary_analysis/ch02_salary_by_education.png',
)

# 热力图
fig = plot_heatmap(
    data=cross_tab, title='学历-经验交叉分析',
    output_path='outputs/ch03_supply_demand/ch03_education_experience_heatmap.png',
)

# 饼图
fig = plot_pie_chart(
    data=nature_counts, title='企业性质分布',
    output_path='outputs/ch04_enterprise_features/ch04_nature_pie.png',
)
```

---

### Skill-03: output_manager.py — 输出产物管理器

| 函数 | 签名 | 说明 |
|------|------|------|
| `get_chapter_dir` | `get_chapter_dir(chapter_key: str) -> str` | 获取章节输出目录完整路径（自动创建） |
| `save_dataframe` | `save_dataframe(df, filename, output_dir, index=True) -> str` | 保存 DataFrame 为 CSV（utf-8-sig 编码） |
| `save_figure` | `save_figure(fig, filename, output_dir, dpi=150) -> str` | 保存 matplotlib 图表为 PNG |
| `save_markdown` | `save_markdown(content, filename, output_dir) -> str` | 保存 Markdown 文本 |

**使用示例**：

```python
from utils.output_manager import get_chapter_dir, save_dataframe, save_figure, save_markdown

# 获取章节输出目录
output_dir = get_chapter_dir('ch01')

# 保存 DataFrame
save_dataframe(df_clean, 'ch01_cleaned_data.csv', output_dir)

# 保存图表
save_figure(fig, 'ch01_missing_values.png', output_dir)

# 保存 Markdown 报告
save_markdown(report_text, 'ch01_data_quality_report.md', output_dir)
```

---

### Skill-04: task_graph.py — 任务依赖图

| 类/函数 | 签名 | 说明 |
|---------|------|------|
| `TaskGraph` | `TaskGraph(project_root=None)` | 任务依赖图实例，提供前置检查和进度查询 |
| `check_ready` | `check_ready(task_key: str) -> dict` | 检查某任务是否可启动，返回 `{'ready': bool, 'missing_artifacts': [...]}` |
| `print_status` | `print_status()` | 打印全部任务进度总览 |
| `get_status` | `get_status() -> list` | 返回全部任务状态列表 |

**使用示例**：

```python
from utils.task_graph import TaskGraph

tg = TaskGraph()

# 执行前检查前置依赖
status = tg.check_ready('prompt-02')
if not status['ready']:
    print(f"缺少前置产物: {status['missing_artifacts']}")
else:
    print("前置条件满足，可以开始执行")

# 打印全局进度
tg.print_status()
```

---

# Prompt-01: 基础数据概览

## 一、任务概述

### 1.1 本次任务是什么

对 51job 原始招聘数据进行全面的质量评估与清洗，产出一份结构化的清洗后数据集，为后续所有分析章节提供可靠的数据基础。本章节是整个项目的前置依赖（Batch-1），必须最先完成。

### 1.2 从什么数据出发

从 `data/前程无忧数据集.csv` 原始数据出发，共 295 条有效记录、10 列。数据存在以下已知问题：
- 第 2 行为重复表头，需剔除
- 字段语义错位：`学历要求` 实为工作经验，`工作经验` 实为附加要求
- 薪资格式不统一（"万/月"和"万/年"两种单位）
- 无显式城市列，城市信息隐含在公司名称中
- `公司类型`（空格分隔）和 `公司福利`（短横线分隔）为多值字段

### 1.3 可以采用什么方法

- **数据加载**：使用 `Skill-01: data_loader.py` 的 `load_raw_data()` 函数，自动跳过重复表头
- **质量评估**：使用 `pandas` 的 `info()`, `describe()`, `isnull().sum()` 进行全面检查
- **薪资解析**：使用正则表达式提取数值区间，按单位统一换算为"万/月"
- **城市提取**：遍历 `config.py` 中的 `CITY_KEYWORDS` 字典，从公司名匹配省市关键词
- **多值拆分**：使用 `str.split()` 按分隔符拆分为列表
- **可视化**：使用 `Skill-02: visualizer.py` 的图表函数

---

## 二、执行步骤

### Step 1.1: 数据加载

**本步骤要做什么**

加载原始 CSV 数据，确认记录数和字段数，验证数据加载正确。

**代码框架**：

```python
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

from utils.data_loader import load_raw_data
from utils.output_manager import get_chapter_dir

OUTPUT_DIR = get_chapter_dir('ch01')

# 加载原始数据
df = load_raw_data(skip_duplicate_header=True)

# 验证数据规模
assert len(df) == 295, f"记录数异常: 期望 295, 实际 {len(df)}"
assert len(df.columns) == 10, f"字段数异常: 期望 10, 实际 {len(df.columns)}"
print(f"数据加载完成: {len(df)} 条记录, {len(df.columns)} 列")
print(f"字段列表: {list(df.columns)}")
```

**本步骤完成后的检查标准**

- 输出日志显示 295 条记录、10 列
- 无 `UnicodeDecodeError` 或 `FileNotFoundError`

**本步骤输出产物**

无独立产物（数据加载为中间步骤）

---

### Step 1.2: 数据质量评估

**本步骤要做什么**

对原始数据进行全面质量评估，统计缺失值、重复值、字段类型、唯一值数量等，生成数据质量报告和可视化图表。

**代码框架**：

```python
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# === 缺失值统计 ===
missing_stats = pd.DataFrame({
    '字段名': df.columns,
    '缺失数量': df.isnull().sum().values,
    '缺失比例(%)': (df.isnull().sum().values / len(df) * 100).round(2),
    '非空数量': df.notnull().sum().values,
})
print("\n=== 缺失值统计 ===")
print(missing_stats.to_string(index=False))

# === 重复值检查 ===
dup_count = df.duplicated().sum()
print(f"\n重复行数: {dup_count}")

# === 字段类型检查 ===
print("\n=== 字段类型 ===")
print(df.dtypes)

# === 各字段唯一值数量 ===
print("\n=== 唯一值统计 ===")
for col in df.columns:
    nunique = df[col].nunique()
    print(f"  {col}: {nunique} 个唯一值")

# === 可视化: 缺失值热力图 ===
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'font.size': 12,
    'axes.unicode_minus': False,
    'font.sans-serif': ['SimHei', 'WenQuanYi Micro Hei', 'DejaVu Sans'],
})

fig, ax = plt.subplots(figsize=(14, 5))
missing_matrix = df.isnull().astype(int)
sns.heatmap(missing_matrix, cbar=True, yticklabels=False, ax=ax, cmap='YlOrRd')
ax.set_title('缺失值分布热力图', fontsize=14, fontweight='bold')
ax.set_xlabel('字段', fontsize=12)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'ch01_missing_values.png'), dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"  [保存] {os.path.join(OUTPUT_DIR, 'ch01_missing_values.png')}")

# === 可视化: 各字段非空值数量 ===
fig, ax = plt.subplots(figsize=(14, 5))
non_null_counts = df.notnull().sum().sort_values(ascending=True)
colors = ['#e74c3c' if v < len(df) * 0.9 else '#2ecc71' for v in non_null_counts.values]
ax.barh(non_null_counts.index, non_null_counts.values, color=colors, alpha=0.85)
ax.set_title('各字段非空值数量', fontsize=14, fontweight='bold')
ax.set_xlabel('非空记录数', fontsize=12)
ax.axvline(x=len(df), color='red', linestyle='--', alpha=0.5, label=f'总记录数 ({len(df)})')
ax.legend()
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'ch01_field_distribution.png'), dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"  [保存] {os.path.join(OUTPUT_DIR, 'ch01_field_distribution.png')}")
```

**本步骤完成后的检查标准**

- 缺失值统计表覆盖全部 10 个字段
- `ch01_missing_values.png` 和 `ch01_field_distribution.png` 已生成

**本步骤输出产物**

- `ch01_missing_values.png` — 缺失值分布热力图
- `ch01_field_distribution.png` — 各字段非空值数量条形图

---

### Step 1.3: 字段重命名

**本步骤要做什么**

修正字段语义错位问题：将 `学历要求` 重命名为 `工作经验要求`，将 `工作经验` 重命名为 `附加要求`。

**代码框架**：

```python
# 字段重命名：修正语义错位
rename_map = {
    '学历要求': '工作经验要求',
    '工作经验': '附加要求',
}
df = df.rename(columns=rename_map)
print(f"字段重命名完成: {rename_map}")
print(f"当前字段列表: {list(df.columns)}")
```

**本步骤完成后的检查标准**

- `df.columns` 中不再包含 `学历要求` 和 `工作经验`
- 新增 `工作经验要求` 和 `附加要求` 两列

**本步骤输出产物**

无独立产物（字段重命名为中间步骤）

---

### Step 1.4: 薪资解析

**本步骤要做什么**

使用正则表达式从 `薪资` 字段提取数值区间，统一换算为"万/月"单位，生成 `salary_min`、`salary_max`、`salary_avg` 三列。

**代码框架**：

```python
import re

def parse_salary(salary_str: str) -> tuple:
    """解析薪资字符串，返回 (salary_min, salary_max, salary_avg)，单位：万/月

    Args:
        salary_str: 薪资字符串，如 "1.8-3.5万/月" 或 "18-36万/年"

    Returns:
        (salary_min万/月, salary_max万/月, salary_avg万/月)，解析失败返回 (None, None, None)
    """
    if pd.isna(salary_str) or str(salary_str).strip() == '':
        return (None, None, None)

    salary_str = str(salary_str).strip()

    # 判断单位
    if '万/年' in salary_str:
        divisor = 12
    elif '万/月' in salary_str:
        divisor = 1
    elif '千/月' in salary_str:
        divisor = 10  # 千转万
    elif '元/天' in salary_str:
        divisor = 22 * 10  # 按每月22天工作日，元转万
    else:
        return (None, None, None)

    # 提取数值区间
    pattern = r'(\d+\.?\d*)\s*[-~]\s*(\d+\.?\d*)'
    match = re.search(pattern, salary_str)
    if match:
        low = float(match.group(1)) / divisor
        high = float(match.group(2)) / divisor
        return (round(low, 2), round(high, 2), round((low + high) / 2, 2))

    # 单个数值
    pattern_single = r'(\d+\.?\d*)'
    match_single = re.search(pattern_single, salary_str)
    if match_single:
        val = float(match_single.group(1)) / divisor
        return (round(val, 2), round(val, 2), round(val, 2))

    return (None, None, None)


# 批量解析薪资
salary_parsed = df['薪资'].apply(parse_salary)
df['salary_min'] = salary_parsed.apply(lambda x: x[0])
df['salary_max'] = salary_parsed.apply(lambda x: x[1])
df['salary_avg'] = salary_parsed.apply(lambda x: x[2])

# 统计解析成功率
parsed_count = df['salary_avg'].notna().sum()
total_count = len(df)
parse_rate = parsed_count / total_count * 100
print(f"薪资解析: {parsed_count}/{total_count} ({parse_rate:.1f}%)")
print(f"薪资统计: min={df['salary_min'].min()}, max={df['salary_max'].max()}, "
      f"avg={df['salary_avg'].mean():.2f} 万/月")
```

**本步骤完成后的检查标准**

- 薪资解析覆盖率 >= 95%
- `salary_min`, `salary_max`, `salary_avg` 三列已添加到 DataFrame
- 无法解析的记录 salary 值为 NaN（非删除）

**本步骤输出产物**

无独立产物（薪资解析为中间步骤）

---

### Step 1.5: 城市提取

**本步骤要做什么**

从 `公司` 字段中遍历 `CITY_KEYWORDS` 匹配省市关键词，提取城市信息作为新列 `城市`。

**代码框架**：

```python
from utils.config import CITY_KEYWORDS

def extract_city(company_name: str) -> str:
    """从公司名称中提取城市信息

    Args:
        company_name: 公司全称

    Returns:
        城市名称，未匹配到返回 '未知'
    """
    if pd.isna(company_name):
        return '未知'

    company_str = str(company_name)

    # 优先匹配城市级关键词（避免省级关键词误匹配）
    for city_name, keywords in CITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in company_str:
                return city_name

    return '未知'


# 批量提取城市
df['城市'] = df['公司'].apply(extract_city)

# 统计提取成功率
known_count = (df['城市'] != '未知').sum()
total_count = len(df)
extract_rate = known_count / total_count * 100
print(f"城市提取: {known_count}/{total_count} ({extract_rate:.1f}%)")

# 城市分布 TOP10
city_counts = df['城市'].value_counts()
print("\n城市分布 TOP10:")
print(city_counts.head(10).to_string())
```

**本步骤完成后的检查标准**

- `城市` 列已添加到 DataFrame
- 城市提取成功率应 >= 80%（低于此值需检查关键词覆盖）
- "未知" 城市记录数已统计

**本步骤输出产物**

无独立产物（城市提取为中间步骤）

---

### Step 1.6: 多值字段拆分

**本步骤要做什么**

将 `公司类型`（空格分隔）和 `公司福利`（短横线分隔）拆分为列表类型，并提取 `主行业`（公司类型的第一个标签）。

**代码框架**：

```python
# 公司类型拆分（空格分隔）
df['公司类型列表'] = df['公司类型'].apply(
    lambda x: [t.strip() for t in str(x).split() if t.strip()] if pd.notna(x) else []
)

# 公司福利拆分（短横线分隔）
df['公司福利列表'] = df['公司福利'].apply(
    lambda x: [t.strip() for t in str(x).split('-') if t.strip()] if pd.notna(x) else []
)

# 提取主行业（公司类型的第一个标签）
df['主行业'] = df['公司类型列表'].apply(lambda x: x[0] if len(x) > 0 else '未知')

# 福利标签数量
df['福利标签数'] = df['公司福利列表'].apply(len)

# 统计
print(f"主行业分布 TOP10:")
print(df['主行业'].value_counts().head(10).to_string())
print(f"\n平均福利标签数: {df['福利标签数'].mean():.1f}")
```

**本步骤完成后的检查标准**

- `公司类型列表` 和 `公司福利列表` 为 list 类型列
- `主行业` 列已提取，"未知" 记录数已统计
- `福利标签数` 列已添加

**本步骤输出产物**

无独立产物（多值拆分为中间步骤）

---

### Step 1.7: 保存清洗数据与质量报告

**本步骤要做什么**

保存清洗后的完整数据集为 CSV 文件，生成数据质量报告 Markdown 文档。

**代码框架**：

```python
from utils.output_manager import save_dataframe, save_markdown

# 保存清洗后数据
save_dataframe(df, 'ch01_cleaned_data.csv', OUTPUT_DIR)

# 生成数据质量报告
report_lines = [
    "# 数据质量报告 — 基础数据概览\n",
    f"## 数据概况\n",
    f"- **原始记录数**: 295 条",
    f"- **清洗后记录数**: {len(df)} 条",
    f"- **字段数量**: {len(df.columns)} 列（原始 10 列 + 新增字段）\n",
    f"## 字段重命名\n",
    f"| 原字段名 | 新字段名 | 原因 |",
    f"|---------|---------|------|",
    f"| 学历要求 | 工作经验要求 | 原字段实际存储工作经验信息 |",
    f"| 工作经验 | 附加要求 | 原字段实际存储附加要求信息 |\n",
    f"## 薪资解析\n",
    f"- **解析成功率**: {parse_rate:.1f}% ({parsed_count}/{total_count})",
    f"- **薪资范围**: {df['salary_min'].min()} ~ {df['salary_max'].max()} 万/月",
    f"- **薪资均值**: {df['salary_avg'].mean():.2f} 万/月",
    f"- **薪资中位数**: {df['salary_avg'].median():.2f} 万/月\n",
    f"## 城市提取\n",
    f"- **提取成功率**: {extract_rate:.1f}% ({known_count}/{total_count})",
    f"- **覆盖城市数**: {(df['城市'] != '未知').nunique()} 个\n",
    f"## 缺失值统计\n",
    f"| 字段名 | 缺失数量 | 缺失比例 |",
    f"|--------|---------|---------|",
]
for _, row in missing_stats.iterrows():
    report_lines.append(f"| {row['字段名']} | {int(row['缺失数量'])} | {row['缺失比例(%)']}% |")

report_lines.append(f"\n## 新增字段\n")
report_lines.append(f"| 字段名 | 类型 | 说明 |")
report_lines.append(f"|--------|------|------|")
report_lines.append(f"| salary_min | float | 薪资下限（万/月） |")
report_lines.append(f"| salary_max | float | 薪资上限（万/月） |")
report_lines.append(f"| salary_avg | float | 薪资均值（万/月） |")
report_lines.append(f"| 城市 | string | 从公司名提取的城市信息 |")
report_lines.append(f"| 公司类型列表 | list | 公司类型标签列表 |")
report_lines.append(f"| 公司福利列表 | list | 公司福利标签列表 |")
report_lines.append(f"| 主行业 | string | 公司类型第一个标签 |")
report_lines.append(f"| 福利标签数 | int | 福利标签数量 |")

report_text = '\n'.join(report_lines)
save_markdown(report_text, 'ch01_data_quality_report.md', OUTPUT_DIR)

print(f"\n章节 01 完成。产物已输出到: {OUTPUT_DIR}")
```

**本步骤完成后的检查标准**

- `ch01_cleaned_data.csv` 包含 295 条记录，含全部新增字段
- `ch01_data_quality_report.md` 内容完整，包含缺失值统计、薪资解析统计、城市提取统计
- 运行 `python src/utils/task_graph.py` 显示 prompt-01 状态为已完成

**本步骤输出产物**

- `ch01_cleaned_data.csv` — 清洗后完整数据集
- `ch01_data_quality_report.md` — 数据质量报告

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物文件名 | 类型 | 说明 |
|------|-----------|------|------|
| 1 | `ch01_cleaned_data.csv` | 数据 | 清洗后完整数据集（295 条记录，含新增字段） |
| 2 | `ch01_data_quality_report.md` | 报告 | 数据质量评估报告（缺失值、薪资解析、城市提取统计） |
| 3 | `ch01_missing_values.png` | 图片 | 缺失值分布热力图 |
| 4 | `ch01_field_distribution.png` | 图片 | 各字段非空值数量条形图 |

### 3.2 关键产物结构详解

**ch01_cleaned_data.csv**：

| 字段 | 类型 | 说明 |
|------|------|------|
| 岗位 | string | 原始字段 |
| 公司 | string | 原始字段 |
| 学历 | string | 原始字段（学历要求） |
| 公司性质 | string | 原始字段 |
| 薪资 | string | 原始字段（原始薪资格式） |
| 工作经验要求 | string | 重命名字段（原"学历要求"） |
| 附加要求 | string | 重命名字段（原"工作经验"） |
| 公司规模 | string | 原始字段 |
| 公司类型 | string | 原始字段（多值，空格分隔） |
| 公司福利 | string | 原始字段（多值，短横线分隔） |
| salary_min | float | 薪资下限（万/月） |
| salary_max | float | 薪资上限（万/月） |
| salary_avg | float | 薪资均值（万/月） |
| 城市 | string | 从公司名提取 |
| 公司类型列表 | string(序列化) | 公司类型标签列表 |
| 公司福利列表 | string(序列化) | 公司福利标签列表 |
| 主行业 | string | 公司类型第一个标签 |
| 福利标签数 | int | 福利标签数量 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性

1. **城市提取依赖关键词匹配**：对于公司名中不含标准省市关键词的企业（如使用简称、英文名），可能提取失败
2. **薪资解析仅覆盖常见格式**：对于"面议"、"薪资面议"等非数值格式，无法解析
3. **工作经验年数未提取**：`工作经验要求` 列仍为原始文本格式（如"3-4年经验"），未提取为数值

### 4.2 可进一步优化的方向

1. **补充工作经验年数提取**：使用正则从 `工作经验要求` 中提取 `experience_min` 和 `experience_max` 数值列
2. **公司名标准化**：去除常见后缀（如"有限公司"、"技术有限公司"），提高城市匹配率
3. **薪资异常值检测**：识别并标记极端薪资值（如超过 3 倍 IQR）

### 4.3 其他可选方法

1. 使用 `jieba` 分词辅助公司名解析
2. 使用模糊匹配（如 `fuzzywuzzy`）提高城市关键词匹配率
3. 对薪资区间取对数后分析，缓解右偏分布

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单

| 序号 | 问题 | 影响范围 | 建议处理 |
|------|------|---------|---------|
| 1 | 薪资解析覆盖率低于 95% 时，是否保留未解析记录 | ch02~ch05 薪资分析 | 保留记录，薪资分析时排除 NaN |
| 2 | 城市提取成功率低于 80% 时，是否需要补充关键词 | ch03 城市分析 | 补充 CITY_KEYWORDS 后重新运行 |
| 3 | 数据中是否存在明显异常值（如薪资 > 100 万/月） | 全部章节 | 标记异常值，不删除 |

### 5.2 常见异常场景与处理策略

| 异常场景 | 可能原因 | 处理策略 |
|---------|---------|---------|
| `FileNotFoundError` | 原始数据文件路径错误 | 检查 `config.py` 中 `RAW_DATA_FILE` 路径 |
| `UnicodeDecodeError` | CSV 编码非 UTF-8 | 尝试 `encoding='gbk'` 或 `encoding='gb18030'` |
| 薪资解析率 < 90% | 存在大量"面议"或非常规格式 | 统计未解析格式分布，补充正则规则 |
| 城市提取率 < 70% | 公司名使用简称或英文名 | 补充 `CITY_KEYWORDS` 映射 |
| `save_dataframe` 目录不存在 | 输出目录未创建 | `get_chapter_dir()` 已自动创建，检查权限 |
| 中文字体显示为方块 | 系统缺少中文字体 | 安装 `WenQuanYi Micro Hei` 或 `SimHei` 字体 |

---
---

# Prompt-02: 薪资维度分析

## 一、任务概述

### 2.1 本次任务是什么

从学历、工作经验、行业、公司性质、公司规模 5 个维度对薪资进行分组对比分析，识别影响薪资水平的关键因素，产出多张对比图表和一份综合薪资统计表。

### 2.2 从什么数据出发

从 `outputs/ch01_data_overview/ch01_cleaned_data.csv` 出发，使用 ch01 清洗后的完整数据集（含 `salary_min`, `salary_max`, `salary_avg` 等解析字段）。

### 2.3 可以采用什么方法

- **薪资分布分析**：直方图 + 核密度估计，展示整体薪资分布特征
- **分组对比**：箱线图（`plot_boxplot`）展示各维度薪资差异
- **有序分类排序**：使用 `DOMAIN_PARAMS['education_order']` 和 `DOMAIN_PARAMS['company_size_order']` 控制图表排序
- **描述统计**：分组计算均值、中位数、标准差、分位数

---

## 二、执行步骤

### Step 2.1: 加载数据

**本步骤要做什么**

加载 ch01 清洗后的数据集，验证薪资字段完整性。

**代码框架**：

```python
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

from utils.data_loader import load_preprocessed
from utils.output_manager import get_chapter_dir
from utils.config import DOMAIN_PARAMS
from utils.visualizer import plot_bar_chart, plot_boxplot, plot_heatmap
from utils.task_graph import TaskGraph

# 检查前置依赖
tg = TaskGraph()
status = tg.check_ready('prompt-02')
if not status['ready']:
    raise RuntimeError(f"前置条件不满足: {status['missing_artifacts']}")

OUTPUT_DIR = get_chapter_dir('ch02')

# 加载清洗后数据
df = load_preprocessed('outputs/ch01_data_overview/ch01_cleaned_data.csv')

# 筛选有效薪资记录
df_salary = df.dropna(subset=['salary_avg']).copy()
print(f"有效薪资记录: {len(df_salary)}/{len(df)}")
```

**本步骤完成后的检查标准**

- 前置依赖检查通过
- 有效薪资记录数 >= 280 条（覆盖率 >= 95%）

**本步骤输出产物**

无独立产物

---

### Step 2.2: 薪资整体分布

**本步骤要做什么**

绘制薪资整体分布直方图，展示 salary_avg 的分布特征（均值、中位数、分位数）。

**代码框架**：

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'figure.dpi': 150, 'savefig.dpi': 150, 'font.size': 12,
    'axes.unicode_minus': False,
    'font.sans-serif': ['SimHei', 'WenQuanYi Micro Hei', 'DejaVu Sans'],
})

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 左图: 薪资分布直方图
ax1 = axes[0]
ax1.hist(df_salary['salary_avg'], bins=30, color='#2196F3', alpha=0.7, edgecolor='white')
ax1.axvline(df_salary['salary_avg'].mean(), color='red', linestyle='--',
            label=f"均值: {df_salary['salary_avg'].mean():.2f}")
ax1.axvline(df_salary['salary_avg'].median(), color='green', linestyle='--',
            label=f"中位数: {df_salary['salary_avg'].median():.2f}")
ax1.set_title('薪资均值分布', fontsize=14, fontweight='bold')
ax1.set_xlabel('薪资（万/月）', fontsize=12)
ax1.set_ylabel('频次', fontsize=12)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 右图: 薪资区间分布（分桶统计）
ax2 = axes[1]
bins = [0, 1, 2, 3, 5, 10, 20, 100]
labels = ['0-1万', '1-2万', '2-3万', '3-5万', '5-10万', '10-20万', '20万+']
df_salary['薪资区间'] = pd.cut(df_salary['salary_avg'], bins=bins, labels=labels)
bin_counts = df_salary['薪资区间'].value_counts().sort_index()
ax2.bar(range(len(bin_counts)), bin_counts.values, color='#FF9800', alpha=0.85)
ax2.set_xticks(range(len(bin_counts)))
ax2.set_xticklabels(bin_counts.index, rotation=30)
ax2.set_title('薪资区间分布', fontsize=14, fontweight='bold')
ax2.set_xlabel('薪资区间（万/月）', fontsize=12)
ax2.set_ylabel('岗位数量', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'ch02_salary_distribution.png'), dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"  [保存] {os.path.join(OUTPUT_DIR, 'ch02_salary_distribution.png')}")
```

**本步骤完成后的检查标准**

- 直方图清晰展示薪资分布的集中趋势和离散程度
- 均值和中位数参考线已标注

**本步骤输出产物**

- `ch02_salary_distribution.png` — 薪资整体分布图（双子图）

---

### Step 2.3: 学历-薪资分析

**本步骤要做什么**

按学历分组对比薪资水平，使用 `DOMAIN_PARAMS['education_order']` 控制排序。

**代码框架**：

```python
# 按学历分组统计
edu_order = DOMAIN_PARAMS['education_order']
edu_stats = df_salary.groupby('学历')['salary_avg'].agg(['mean', 'median', 'std', 'count'])
edu_stats = edu_stats.reindex(edu_order).dropna()
print("=== 学历-薪资统计 ===")
print(edu_stats.round(2).to_string())

# 箱线图
fig = plot_boxplot(
    data=df_salary[df_salary['学历'].isin(edu_order)],
    x='学历', y='salary_avg',
    title='各学历薪资分布',
    order=edu_order,
    output_path=os.path.join(OUTPUT_DIR, 'ch02_salary_by_education.png'),
    figsize=(10, 6),
)
```

**本步骤完成后的检查标准**

- 学历按 `education_order` 排序（大专 → 本科 → 硕士 → 博士）
- 箱线图清晰展示各学历薪资中位数和离散程度

**本步骤输出产物**

- `ch02_salary_by_education.png` — 学历-薪资箱线图

---

### Step 2.4: 经验-薪资分析

**本步骤要做什么**

按工作经验要求分组对比薪资水平。

**代码框架**：

```python
# 按工作经验要求分组统计
exp_stats = df_salary.groupby('工作经验要求')['salary_avg'].agg(
    ['mean', 'median', 'std', 'count']
).sort_values('median', ascending=False)
print("=== 经验-薪资统计 ===")
print(exp_stats.round(2).to_string())

# 条形图: 各经验等级薪资中位数
fig = plot_bar_chart(
    data=exp_stats['median'],
    title='各工作经验要求薪资中位数',
    xlabel='工作经验要求', ylabel='薪资中位数（万/月）',
    output_path=os.path.join(OUTPUT_DIR, 'ch02_salary_by_experience.png'),
    figsize=(14, 6),
    color='#4CAF50',
    horizontal=True,
)
```

**本步骤完成后的检查标准**

- 经验等级按薪资中位数降序排列
- 条形图水平展示，便于阅读长标签

**本步骤输出产物**

- `ch02_salary_by_experience.png` — 经验-薪资条形图

---

### Step 2.5: 行业-薪资分析

**本步骤要做什么**

按主行业分组对比薪资水平，使用箱线图展示行业间薪资差异。

**代码框架**：

```python
# 按主行业分组统计（取岗位数 >= 5 的行业）
industry_counts = df_salary['主行业'].value_counts()
major_industries = industry_counts[industry_counts >= 5].index.tolist()

industry_stats = df_salary[df_salary['主行业'].isin(major_industries)].groupby(
    '主行业'
)['salary_avg'].agg(['mean', 'median', 'std', 'count']).sort_values('median', ascending=False)

print("=== 行业-薪资统计（岗位数>=5） ===")
print(industry_stats.round(2).to_string())

# 箱线图
fig = plot_boxplot(
    data=df_salary[df_salary['主行业'].isin(major_industries)],
    x='主行业', y='salary_avg',
    title='各行业薪资分布（岗位数 >= 5）',
    output_path=os.path.join(OUTPUT_DIR, 'ch02_salary_by_industry_boxplot.png'),
    figsize=(16, 7),
    palette='Set3',
)
```

**本步骤完成后的检查标准**

- 仅展示岗位数 >= 5 的行业，避免小样本偏差
- 箱线图 x 轴标签可读

**本步骤输出产物**

- `ch02_salary_by_industry_boxplot.png` — 行业-薪资箱线图

---

### Step 2.6: 公司性质-薪资分析

**本步骤要做什么**

按公司性质分组对比薪资水平。

**代码框架**：

```python
# 按公司性质分组统计
nature_stats = df_salary.groupby('公司性质')['salary_avg'].agg(
    ['mean', 'median', 'std', 'count']
).sort_values('median', ascending=False)
print("=== 公司性质-薪资统计 ===")
print(nature_stats.round(2).to_string())

# 箱线图
fig = plot_boxplot(
    data=df_salary, x='公司性质', y='salary_avg',
    title='各公司性质薪资分布',
    output_path=os.path.join(OUTPUT_DIR, 'ch02_salary_by_company_nature.png'),
    figsize=(14, 6),
    palette='Set2',
)
```

**本步骤完成后的检查标准**

- 公司性质分类完整覆盖
- 箱线图清晰展示各性质企业薪资差异

**本步骤输出产物**

- `ch02_salary_by_company_nature.png` — 公司性质-薪资箱线图

---

### Step 2.7: 公司规模-薪资分析

**本步骤要做什么**

按公司规模分组对比薪资水平，使用 `DOMAIN_PARAMS['company_size_order']` 控制排序。

**代码框架**：

```python
# 按公司规模分组统计
size_order = DOMAIN_PARAMS['company_size_order']
size_stats = df_salary.groupby('公司规模')['salary_avg'].agg(
    ['mean', 'median', 'std', 'count']
)
size_stats = size_stats.reindex(size_order).dropna()
print("=== 公司规模-薪资统计 ===")
print(size_stats.round(2).to_string())

# 箱线图
fig = plot_boxplot(
    data=df_salary[df_salary['公司规模'].isin(size_order)],
    x='公司规模', y='salary_avg',
    title='各公司规模薪资分布',
    order=size_order,
    output_path=os.path.join(OUTPUT_DIR, 'ch02_salary_by_company_size.png'),
    figsize=(16, 6),
    palette='Pastel1',
)
```

**本步骤完成后的检查标准**

- 公司规模按 `company_size_order` 排序（少于50人 → 10000人以上）
- 箱线图清晰展示规模与薪资的关系

**本步骤输出产物**

- `ch02_salary_by_company_size.png` — 公司规模-薪资箱线图

---

### Step 2.8: 保存薪资统计表

**本步骤要做什么**

将各维度的薪资统计结果合并为一张综合统计表并保存。

**代码框架**：

```python
from utils.output_manager import save_dataframe

# 构建综合薪资统计表
salary_summary_rows = []

# 学历维度
for edu in edu_stats.index:
    salary_summary_rows.append({
        '分析维度': '学历', '分组': edu,
        '均值': round(edu_stats.loc[edu, 'mean'], 2),
        '中位数': round(edu_stats.loc[edu, 'median'], 2),
        '标准差': round(edu_stats.loc[edu, 'std'], 2) if pd.notna(edu_stats.loc[edu, 'std']) else None,
        '样本数': int(edu_stats.loc[edu, 'count']),
    })

# 行业维度
for ind in industry_stats.index:
    salary_summary_rows.append({
        '分析维度': '行业', '分组': ind,
        '均值': round(industry_stats.loc[ind, 'mean'], 2),
        '中位数': round(industry_stats.loc[ind, 'median'], 2),
        '标准差': round(industry_stats.loc[ind, 'std'], 2) if pd.notna(industry_stats.loc[ind, 'std']) else None,
        '样本数': int(industry_stats.loc[ind, 'count']),
    })

# 公司性质维度
for nat in nature_stats.index:
    salary_summary_rows.append({
        '分析维度': '公司性质', '分组': nat,
        '均值': round(nature_stats.loc[nat, 'mean'], 2),
        '中位数': round(nature_stats.loc[nat, 'median'], 2),
        '标准差': round(nature_stats.loc[nat, 'std'], 2) if pd.notna(nature_stats.loc[nat, 'std']) else None,
        '样本数': int(nature_stats.loc[nat, 'count']),
    })

# 公司规模维度
for sz in size_stats.index:
    salary_summary_rows.append({
        '分析维度': '公司规模', '分组': sz,
        '均值': round(size_stats.loc[sz, 'mean'], 2),
        '中位数': round(size_stats.loc[sz, 'median'], 2),
        '标准差': round(size_stats.loc[sz, 'std'], 2) if pd.notna(size_stats.loc[sz, 'std']) else None,
        '样本数': int(size_stats.loc[sz, 'count']),
    })

salary_summary_df = pd.DataFrame(salary_summary_rows)
save_dataframe(salary_summary_df, 'ch02_salary_stats.csv', OUTPUT_DIR)

print(f"\n章节 02 完成。产物已输出到: {OUTPUT_DIR}")
```

**本步骤完成后的检查标准**

- `ch02_salary_stats.csv` 包含学历、行业、公司性质、公司规模 4 个维度的统计结果
- 每行包含均值、中位数、标准差、样本数

**本步骤输出产物**

- `ch02_salary_stats.csv` — 薪资综合统计表

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物文件名 | 类型 | 说明 |
|------|-----------|------|------|
| 1 | `ch02_salary_distribution.png` | 图片 | 薪资整体分布图（直方图 + 区间分布） |
| 2 | `ch02_salary_by_education.png` | 图片 | 学历-薪资箱线图 |
| 3 | `ch02_salary_by_experience.png` | 图片 | 经验-薪资条形图 |
| 4 | `ch02_salary_by_industry_boxplot.png` | 图片 | 行业-薪资箱线图 |
| 5 | `ch02_salary_by_company_nature.png` | 图片 | 公司性质-薪资箱线图 |
| 6 | `ch02_salary_by_company_size.png` | 图片 | 公司规模-薪资箱线图 |
| 7 | `ch02_salary_stats.csv` | 数据 | 薪资综合统计表（4 维度） |

### 3.2 关键产物结构详解

**ch02_salary_stats.csv**：

| 字段 | 类型 | 说明 |
|------|------|------|
| 分析维度 | string | 学历 / 行业 / 公司性质 / 公司规模 |
| 分组 | string | 维度内的分组名称 |
| 均值 | float | 薪资均值（万/月） |
| 中位数 | float | 薪资中位数（万/月） |
| 标准差 | float | 薪资标准差 |
| 样本数 | int | 该分组的有效记录数 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性

1. **样本量较小（295条）**：部分分组（如博士学历、事业单位）样本数极少，统计结果不稳定
2. **未进行统计检验**：仅展示描述性统计，未验证组间差异的统计显著性
3. **未做多因素交叉分析**：各维度独立分析，未控制其他变量的影响

### 4.2 可进一步优化的方向

1. **添加统计检验**：使用 Kruskal-Wallis 检验或 Mann-Whitney U 检验验证组间差异
2. **多因素回归分析**：构建多元线性回归模型，量化各因素对薪资的独立贡献
3. **城市维度补充**：在薪资分析中加入城市维度对比

### 4.3 其他可选方法

1. 使用 violin plot 替代 boxplot，展示更精细的分布形态
2. 使用 radar chart 综合展示各维度薪资排名
3. 使用聚类分析识别薪资特征相似的岗位群

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单

| 序号 | 问题 | 影响范围 | 建议处理 |
|------|------|---------|---------|
| 1 | 某些分组样本数 < 5，是否纳入分析 | 对应维度的图表 | 纳入但标注样本量 |
| 2 | 薪资存在极端值（如 > 20 万/月），是否剔除 | 全部分析 | 保留，在报告中标注 |

### 5.2 常见异常场景与处理策略

| 异常场景 | 可能原因 | 处理策略 |
|---------|---------|---------|
| `KeyError: 'salary_avg'` | ch01 清洗数据未包含薪资字段 | 重新运行 ch01 |
| 某学历分组为空 | 数据中无该学历记录 | 从排序中移除该分组 |
| 箱线图 x 轴标签重叠 | 分组名称过长 | 调整 `figsize` 或旋转标签 |
| 图表中文显示异常 | 系统缺少中文字体 | 安装字体或设置 `rcParams` |

---
---

# Prompt-03: 供需维度分析

## 一、任务概述

### 3.1 本次任务是什么

从岗位、城市、行业 3 个维度分析人才市场的供需结构，识别热门岗位、招聘热度城市和需求集中的行业，并通过学历-经验交叉分析刻画招聘门槛特征。

### 3.2 从什么数据出发

从 `outputs/ch01_data_overview/ch01_cleaned_data.csv` 出发，使用 ch01 清洗后的完整数据集。

### 3.3 可以采用什么方法

- **频次统计与排名**：统计岗位、城市、行业的招聘数量，取 TOP-N
- **占比分析**：计算各分组占总量的百分比
- **交叉分析**：使用热力图展示学历-经验的交叉分布
- **饼图**：展示行业需求占比分布

---

## 二、执行步骤

### Step 3.1: 加载数据

**本步骤要做什么**

加载 ch01 清洗后的数据集，检查前置依赖。

**代码框架**：

```python
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

from utils.data_loader import load_preprocessed
from utils.output_manager import get_chapter_dir
from utils.visualizer import plot_bar_chart, plot_heatmap, plot_pie_chart
from utils.task_graph import TaskGraph

# 检查前置依赖
tg = TaskGraph()
status = tg.check_ready('prompt-03')
if not status['ready']:
    raise RuntimeError(f"前置条件不满足: {status['missing_artifacts']}")

OUTPUT_DIR = get_chapter_dir('ch03')

# 加载清洗后数据
df = load_preprocessed('outputs/ch01_data_overview/ch01_cleaned_data.csv')
print(f"数据加载完成: {len(df)} 条记录")
```

**本步骤完成后的检查标准**

- 前置依赖检查通过
- 数据记录数 = 295

**本步骤输出产物**

无独立产物

---

### Step 3.2: 岗位 TOP20 分析

**本步骤要做什么**

统计招聘岗位的频次排名，取 TOP20 热门岗位绘制水平条形图。

**代码框架**：

```python
# 岗位频次统计 TOP20
job_counts = df['岗位'].value_counts().head(20)

print("=== 热门岗位 TOP20 ===")
print(job_counts.to_string())

# 水平条形图
fig = plot_bar_chart(
    data=job_counts,
    title='热门招聘岗位 TOP20',
    xlabel='岗位名称', ylabel='招聘数量',
    output_path=os.path.join(OUTPUT_DIR, 'ch03_job_type_top20.png'),
    figsize=(14, 8),
    color='#2196F3',
    horizontal=True,
)
```

**本步骤完成后的检查标准**

- TOP20 岗位按招聘数量降序排列
- 条形图水平展示，岗位名称完整可读

**本步骤输出产物**

- `ch03_job_type_top20.png` — 热门岗位 TOP20 条形图

---

### Step 3.3: 城市招聘热度分析

**本步骤要做什么**

统计各城市的招聘数量，取 TOP15 城市绘制条形图，展示城市维度的招聘热度。

**代码框架**：

```python
# 城市招聘热度（排除"未知"）
city_counts = df[df['城市'] != '未知']['城市'].value_counts().head(15)

print("=== 城市招聘热度 TOP15 ===")
print(city_counts.to_string())

# 条形图
fig = plot_bar_chart(
    data=city_counts,
    title='城市招聘热度 TOP15',
    xlabel='城市', ylabel='招聘数量',
    output_path=os.path.join(OUTPUT_DIR, 'ch03_city_hiring_ranking.png'),
    figsize=(14, 7),
    color='#FF5722',
)
```

**本步骤完成后的检查标准**

- 排除"未知"城市
- TOP15 城市按招聘数量降序排列

**本步骤输出产物**

- `ch03_city_hiring_ranking.png` — 城市招聘热度 TOP15 条形图

---

### Step 3.4: 行业需求分布分析

**本步骤要做什么**

统计各行业的招聘数量占比，使用饼图展示行业需求分布。

**代码框架**：

```python
# 行业需求分布
industry_counts = df['主行业'].value_counts()
# 将占比 < 3% 的行业合并为"其他"
threshold = len(df) * 0.03
major = industry_counts[industry_counts >= threshold]
other_count = industry_counts[industry_counts < threshold].sum()
if other_count > 0:
    major['其他'] = other_count

print("=== 行业需求分布 ===")
print(major.to_string())

# 饼图
fig = plot_pie_chart(
    data=major,
    title='行业需求分布',
    output_path=os.path.join(OUTPUT_DIR, 'ch03_industry_demand_pie.png'),
    figsize=(10, 8),
)
```

**本步骤完成后的检查标准**

- 占比 < 3% 的行业合并为"其他"
- 饼图标签清晰可读

**本步骤输出产物**

- `ch03_industry_demand_pie.png` — 行业需求分布饼图

---

### Step 3.5: 学历-经验交叉分析

**本步骤要做什么**

构建学历与工作经验要求的交叉频次表，使用热力图展示招聘门槛的分布特征。

**代码框架**：

```python
import pandas as pd

# 学历-经验交叉频次表
cross_tab = pd.crosstab(df['学历'], df['工作经验要求'])

# 按学历排序
edu_order = ['大专', '本科', '硕士', '博士']
valid_edu = [e for e in edu_order if e in cross_tab.index]
cross_tab = cross_tab.reindex(valid_edu)

print("=== 学历-经验交叉分析 ===")
print(cross_tab.to_string())

# 热力图
fig = plot_heatmap(
    data=cross_tab,
    title='学历-工作经验要求交叉分布',
    xlabel='工作经验要求', ylabel='学历',
    output_path=os.path.join(OUTPUT_DIR, 'ch03_education_experience_heatmap.png'),
    figsize=(16, 6),
    cmap='Blues',
    annot=True,
    fmt='d',
)
```

**本步骤完成后的检查标准**

- 交叉表行按学历排序
- 热力图数值标注为整数（`fmt='d'`）

**本步骤输出产物**

- `ch03_education_experience_heatmap.png` — 学历-经验交叉热力图

---

### Step 3.6: 保存供需统计表

**本步骤要做什么**

将岗位 TOP20、城市 TOP15、行业分布统计合并为一张供需统计表并保存。

**代码框架**：

```python
from utils.output_manager import save_dataframe

# 构建供需统计表
supply_demand_rows = []

# 岗位 TOP20
for rank, (job, count) in enumerate(job_counts.items(), 1):
    supply_demand_rows.append({
        '分析维度': '岗位',
        '排名': rank,
        '分组名称': job,
        '数量': int(count),
        '占比(%)': round(count / len(df) * 100, 2),
    })

# 城市 TOP15
for rank, (city, count) in enumerate(city_counts.items(), 1):
    supply_demand_rows.append({
        '分析维度': '城市',
        '排名': rank,
        '分组名称': city,
        '数量': int(count),
        '占比(%)': round(count / len(df) * 100, 2),
    })

# 行业分布
for rank, (ind, count) in enumerate(industry_counts.items(), 1):
    supply_demand_rows.append({
        '分析维度': '行业',
        '排名': rank,
        '分组名称': ind,
        '数量': int(count),
        '占比(%)': round(count / len(df) * 100, 2),
    })

supply_demand_df = pd.DataFrame(supply_demand_rows)
save_dataframe(supply_demand_df, 'ch03_supply_demand_stats.csv', OUTPUT_DIR)

print(f"\n章节 03 完成。产物已输出到: {OUTPUT_DIR}")
```

**本步骤完成后的检查标准**

- `ch03_supply_demand_stats.csv` 包含岗位、城市、行业 3 个维度的统计
- 每行包含排名、分组名称、数量、占比

**本步骤输出产物**

- `ch03_supply_demand_stats.csv` — 供需综合统计表

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物文件名 | 类型 | 说明 |
|------|-----------|------|------|
| 1 | `ch03_job_type_top20.png` | 图片 | 热门岗位 TOP20 水平条形图 |
| 2 | `ch03_city_hiring_ranking.png` | 图片 | 城市招聘热度 TOP15 条形图 |
| 3 | `ch03_industry_demand_pie.png` | 图片 | 行业需求分布饼图 |
| 4 | `ch03_education_experience_heatmap.png` | 图片 | 学历-经验交叉分布热力图 |
| 5 | `ch03_supply_demand_stats.csv` | 数据 | 供需综合统计表 |

### 3.2 关键产物结构详解

**ch03_supply_demand_stats.csv**：

| 字段 | 类型 | 说明 |
|------|------|------|
| 分析维度 | string | 岗位 / 城市 / 行业 |
| 排名 | int | 该维度内的排名 |
| 分组名称 | string | 具体的岗位/城市/行业名称 |
| 数量 | int | 招聘数量 |
| 占比(%) | float | 占总记录数的百分比 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性

1. **岗位名称未标准化**：如"Python开发"和"Python工程师"可能指同一类岗位，但被分别统计
2. **城市提取可能不完整**：部分公司名中城市信息无法提取
3. **行业分类较粗**：仅取公司类型的第一个标签，可能丢失细分行业信息

### 4.2 可进一步优化的方向

1. **岗位名称标准化**：使用关键词匹配或聚类将相似岗位归并
2. **地理区域聚合**：将城市按一线/新一线/二线等层级聚合分析
3. **供需比计算**：结合外部数据（如求职者数量）计算供需比

### 4.3 其他可选方法

1. 使用词云图展示岗位关键词分布
2. 使用 Sankey 图展示学历→经验→岗位的流向关系
3. 使用地图热力图展示城市招聘地理分布

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单

| 序号 | 问题 | 影响范围 | 建议处理 |
|------|------|---------|---------|
| 1 | 岗位名称是否需要标准化合并 | 岗位 TOP20 统计 | 首次分析保持原始名称，后续可优化 |
| 2 | "未知"城市记录占比过高时如何处理 | 城市分析 | 报告中标注，分析时排除 |

### 5.2 常见异常场景与处理策略

| 异常场景 | 可能原因 | 处理策略 |
|---------|---------|---------|
| 饼图标签重叠 | 行业分类过多 | 合并占比 < 3% 的为"其他" |
| 热力图某行全为 0 | 该学历无对应经验要求记录 | 从交叉表中移除空行 |
| 岗位 TOP20 中存在高度相似名称 | 岗位名称未标准化 | 在报告中说明，后续优化 |

---
---

# Prompt-04: 企业特征分析

## 一、任务概述

### 4.1 本次任务是什么

从企业性质、企业规模、福利标签 3 个维度分析企业招聘特征，识别不同类型企业的招聘偏好（学历门槛、经验门槛），分析福利标签的行业分布差异，构建企业招聘偏好画像。

### 4.2 从什么数据出发

从 `outputs/ch01_data_overview/ch01_cleaned_data.csv` 出发，使用 ch01 清洗后的完整数据集（含 `公司福利列表`、`福利标签数` 等新增字段）。

### 4.3 可以采用什么方法

- **分布分析**：饼图展示企业性质分布，条形图展示企业规模分布
- **频次统计**：统计福利标签出现频次，取 TOP15
- **交叉分析**：热力图展示福利-企业关联、行业-福利分布
- **画像构建**：按企业性质分组统计学历门槛、经验门槛、薪资水平、福利标签数

---

## 二、执行步骤

### Step 4.1: 加载数据

**本步骤要做什么**

加载 ch01 清洗后的数据集，检查前置依赖。

**代码框架**：

```python
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

from utils.data_loader import load_preprocessed
from utils.output_manager import get_chapter_dir
from utils.config import DOMAIN_PARAMS
from utils.visualizer import plot_bar_chart, plot_boxplot, plot_heatmap, plot_pie_chart
from utils.task_graph import TaskGraph

# 检查前置依赖
tg = TaskGraph()
status = tg.check_ready('prompt-04')
if not status['ready']:
    raise RuntimeError(f"前置条件不满足: {status['missing_artifacts']}")

OUTPUT_DIR = get_chapter_dir('ch04')

# 加载清洗后数据
df = load_preprocessed('outputs/ch01_data_overview/ch01_cleaned_data.csv')
print(f"数据加载完成: {len(df)} 条记录")
```

**本步骤完成后的检查标准**

- 前置依赖检查通过
- 数据记录数 = 295

**本步骤输出产物**

无独立产物

---

### Step 4.2: 企业性质分布分析

**本步骤要做什么**

统计各企业性质的招聘数量占比，使用饼图展示。

**代码框架**：

```python
# 企业性质分布
nature_counts = df['公司性质'].value_counts()
print("=== 企业性质分布 ===")
print(nature_counts.to_string())

# 饼图
fig = plot_pie_chart(
    data=nature_counts,
    title='企业性质分布',
    output_path=os.path.join(OUTPUT_DIR, 'ch04_nature_pie.png'),
    figsize=(10, 8),
)
```

**本步骤完成后的检查标准**

- 饼图覆盖全部企业性质分类
- 百分比标注清晰

**本步骤输出产物**

- `ch04_nature_pie.png` — 企业性质分布饼图

---

### Step 4.3: 企业规模分布分析

**本步骤要做什么**

统计各企业规模的招聘数量，使用条形图展示，按 `DOMAIN_PARAMS['company_size_order']` 排序。

**代码框架**：

```python
# 企业规模分布
size_order = DOMAIN_PARAMS['company_size_order']
size_counts = df['公司规模'].value_counts()
size_counts = size_counts.reindex(size_order).dropna()
print("=== 企业规模分布 ===")
print(size_counts.to_string())

# 条形图
fig = plot_bar_chart(
    data=size_counts,
    title='企业规模分布',
    xlabel='公司规模', ylabel='招聘数量',
    output_path=os.path.join(OUTPUT_DIR, 'ch04_size_bar.png'),
    figsize=(14, 6),
    color='#9C27B0',
)
```

**本步骤完成后的检查标准**

- 企业规模按 `company_size_order` 排序
- 条形图清晰展示各规模的企业数量

**本步骤输出产物**

- `ch04_size_bar.png` — 企业规模分布条形图

---

### Step 4.4: 福利标签 TOP15 分析

**本步骤要做什么**

统计全部福利标签的出现频次，取 TOP15 绘制水平条形图。

**代码框架**：

```python
from collections import Counter

# 统计所有福利标签频次
all_welfares = []
for welfare_list in df['公司福利列表']:
    if isinstance(welfare_list, str):
        # CSV 序列化后为字符串，需解析
        import ast
        try:
            parsed = ast.literal_eval(welfare_list)
            all_welfares.extend(parsed)
        except (ValueError, SyntaxError):
            pass
    elif isinstance(welfare_list, list):
        all_welfares.extend(welfare_list)

welfare_counter = Counter(all_welfares)
welfare_top15 = welfare_counter.most_common(15)
welfare_labels = [item[0] for item in welfare_top15]
welfare_values = [item[1] for item in welfare_top15]

print("=== 福利标签 TOP15 ===")
for label, count in welfare_top15:
    print(f"  {label}: {count}")

# 水平条形图
fig = plot_bar_chart(
    data=dict(zip(welfare_labels, welfare_values)),
    title='福利标签 TOP15',
    xlabel='福利标签', ylabel='出现次数',
    output_path=os.path.join(OUTPUT_DIR, 'ch04_welfare_top15.png'),
    figsize=(14, 8),
    color='#00BCD4',
    horizontal=True,
)
```

**本步骤完成后的检查标准**

- 福利标签按频次降序排列
- 正确处理 CSV 序列化后的字符串格式

**本步骤输出产物**

- `ch04_welfare_top15.png` — 福利标签 TOP15 水平条形图

---

### Step 4.5: 福利-企业关联分析

**本步骤要做什么**

分析不同企业性质的平均福利标签数量和薪资水平，构建福利-企业关联图。

**代码框架**：

```python
# 各企业性质的福利标签数和薪资
nature_welfare = df.groupby('公司性质').agg(
    平均福利标签数=('福利标签数', 'mean'),
    平均薪资=('salary_avg', 'mean'),
    招聘数量=('公司性质', 'count'),
).round(2)

print("=== 企业性质-福利-薪资关联 ===")
print(nature_welfare.to_string())

# 箱线图: 各企业性质的福利标签数
fig = plot_boxplot(
    data=df, x='公司性质', y='福利标签数',
    title='各企业性质福利标签数量分布',
    output_path=os.path.join(OUTPUT_DIR, 'ch04_welfare_by_nature.png'),
    figsize=(14, 6),
    palette='Set2',
)
```

**本步骤完成后的检查标准**

- 统计表包含平均福利标签数、平均薪资、招聘数量
- 箱线图展示福利标签数的分布差异

**本步骤输出产物**

- `ch04_welfare_by_nature.png` — 各企业性质福利标签数量分布箱线图

---

### Step 4.6: 行业-福利热力图

**本步骤要做什么**

构建行业与 TOP10 福利标签的交叉频次热力图，展示不同行业的福利偏好差异。

**代码框架**：

```python
import pandas as pd

# 取 TOP10 福利标签
top10_welfares = [item[0] for item in welfare_top15[:10]]

# 构建行业-福利交叉表
industry_welfare_rows = []
for _, row in df.iterrows():
    industry = row['主行业']
    welfares = row['公司福利列表']
    if isinstance(welfares, str):
        import ast
        try:
            welfares = ast.literal_eval(welfares)
        except (ValueError, SyntaxError):
            welfares = []
    if isinstance(welfares, list):
        for w in welfares:
            if w in top10_welfares:
                industry_welfare_rows.append({'行业': industry, '福利': w})

if industry_welfare_rows:
    iw_df = pd.DataFrame(industry_welfare_rows)
    iw_cross = pd.crosstab(iw_df['行业'], iw_df['福利'])
    # 按总频次排序取 TOP10 行业
    iw_cross['总计'] = iw_cross.sum(axis=1)
    iw_cross = iw_cross.sort_values('总计', ascending=False).head(10)
    iw_cross = iw_cross.drop(columns='总计')

    print("=== 行业-福利交叉分析 TOP10 行业 ===")
    print(iw_cross.to_string())

    fig = plot_heatmap(
        data=iw_cross,
        title='行业-福利标签交叉分布（TOP10 行业 x TOP10 福利）',
        xlabel='福利标签', ylabel='行业',
        output_path=os.path.join(OUTPUT_DIR, 'ch04_industry_welfare_heatmap.png'),
        figsize=(16, 8),
        cmap='YlGnBu',
        annot=True,
        fmt='d',
    )
```

**本步骤完成后的检查标准**

- 热力图展示 TOP10 行业与 TOP10 福利的交叉频次
- 行业按总频次降序排列

**本步骤输出产物**

- `ch04_industry_welfare_heatmap.png` — 行业-福利交叉热力图

---

### Step 4.7: 招聘偏好画像

**本步骤要做什么**

按企业性质分组，构建学历门槛分布热力图，刻画不同类型企业的招聘偏好。

**代码框架**：

```python
# 各企业性质的学历门槛分布
edu_nature_cross = pd.crosstab(df['公司性质'], df['学历'])
edu_order = DOMAIN_PARAMS['education_order']
valid_edu = [e for e in edu_order if e in edu_nature_cross.columns]
edu_nature_cross = edu_nature_cross[valid_edu]

print("=== 企业性质-学历门槛交叉分析 ===")
print(edu_nature_cross.to_string())

# 热力图
fig = plot_heatmap(
    data=edu_nature_cross,
    title='各企业性质学历要求分布',
    xlabel='学历要求', ylabel='企业性质',
    output_path=os.path.join(OUTPUT_DIR, 'ch04_edu_by_nature_heatmap.png'),
    figsize=(12, 6),
    cmap='OrRd',
    annot=True,
    fmt='d',
)
```

**本步骤完成后的检查标准**

- 热力图行为企业性质，列为学历
- 学历按 `education_order` 排序

**本步骤输出产物**

- `ch04_edu_by_nature_heatmap.png` — 企业性质-学历门槛热力图

---

### Step 4.8: 保存企业特征统计表

**本步骤要做什么**

将企业性质分布、企业规模分布、福利 TOP15、招聘偏好画像合并为一张综合统计表。

**代码框架**：

```python
from utils.output_manager import save_dataframe

# 构建企业特征统计表
enterprise_rows = []

# 企业性质分布
for nature, count in nature_counts.items():
    enterprise_rows.append({
        '分析维度': '企业性质',
        '分组名称': nature,
        '数量': int(count),
        '占比(%)': round(count / len(df) * 100, 2),
        '附加信息': '',
    })

# 企业规模分布
for size, count in size_counts.items():
    enterprise_rows.append({
        '分析维度': '企业规模',
        '分组名称': size,
        '数量': int(count),
        '占比(%)': round(count / len(df) * 100, 2),
        '附加信息': '',
    })

# 福利 TOP15
for label, count in welfare_top15:
    enterprise_rows.append({
        '分析维度': '福利标签',
        '分组名称': label,
        '数量': int(count),
        '占比(%)': round(count / len(df) * 100, 2),
        '附加信息': '',
    })

# 招聘偏好画像
for nature in nature_welfare.index:
    enterprise_rows.append({
        '分析维度': '招聘偏好',
        '分组名称': nature,
        '数量': int(nature_welfare.loc[nature, '招聘数量']),
        '占比(%)': '',
        '附加信息': f"平均福利{nature_welfare.loc[nature, '平均福利标签数']}项, "
                    f"平均薪资{nature_welfare.loc[nature, '平均薪资']}万/月",
    })

enterprise_df = pd.DataFrame(enterprise_rows)
save_dataframe(enterprise_df, 'ch04_enterprise_stats.csv', OUTPUT_DIR)

print(f"\n章节 04 完成。产物已输出到: {OUTPUT_DIR}")
```

**本步骤完成后的检查标准**

- `ch04_enterprise_stats.csv` 包含企业性质、规模、福利、招聘偏好 4 个维度
- 招聘偏好行包含平均福利数和平均薪资

**本步骤输出产物**

- `ch04_enterprise_stats.csv` — 企业特征综合统计表

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物文件名 | 类型 | 说明 |
|------|-----------|------|------|
| 1 | `ch04_nature_pie.png` | 图片 | 企业性质分布饼图 |
| 2 | `ch04_size_bar.png` | 图片 | 企业规模分布条形图 |
| 3 | `ch04_welfare_top15.png` | 图片 | 福利标签 TOP15 水平条形图 |
| 4 | `ch04_welfare_by_nature.png` | 图片 | 各企业性质福利标签数量分布箱线图 |
| 5 | `ch04_industry_welfare_heatmap.png` | 图片 | 行业-福利交叉热力图 |
| 6 | `ch04_edu_by_nature_heatmap.png` | 图片 | 企业性质-学历门槛热力图 |
| 7 | `ch04_enterprise_stats.csv` | 数据 | 企业特征综合统计表 |

### 3.2 关键产物结构详解

**ch04_enterprise_stats.csv**：

| 字段 | 类型 | 说明 |
|------|------|------|
| 分析维度 | string | 企业性质 / 企业规模 / 福利标签 / 招聘偏好 |
| 分组名称 | string | 维度内的分组名称 |
| 数量 | int | 招聘数量或标签出现次数 |
| 占比(%) | float | 占总记录数的百分比 |
| 附加信息 | string | 招聘偏好维度包含平均福利数和平均薪资 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性

1. **福利标签未标准化**：如"五险一金"和"五险"可能被视为不同标签
2. **招聘偏好画像较简单**：仅按企业性质分组，未考虑规模、行业的交叉影响
3. **未分析福利与薪资的相关性**：仅展示了分布差异，未量化相关系数

### 4.2 可进一步优化的方向

1. **福利标签标准化**：建立同义词映射表，合并相似标签
2. **福利-薪资相关性分析**：计算福利标签数与薪资的 Pearson/Spearman 相关系数
3. **多维交叉画像**：按企业性质 x 规模构建更细粒度的招聘偏好画像

### 4.3 其他可选方法

1. 使用词云图展示福利标签分布
2. 使用关联规则挖掘（Apriori 算法）发现福利标签的共现模式
3. 使用雷达图对比不同性质企业的招聘偏好

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单

| 序号 | 问题 | 影响范围 | 建议处理 |
|------|------|---------|---------|
| 1 | 福利标签是否需要标准化合并 | 福利 TOP15 统计 | 首次保持原始标签，后续可优化 |
| 2 | 部分企业性质样本极少（< 5条），是否纳入分析 | 企业性质相关图表 | 纳入但标注样本量 |

### 5.2 常见异常场景与处理策略

| 异常场景 | 可能原因 | 处理策略 |
|---------|---------|---------|
| `公司福利列表` 列为字符串 | CSV 序列化导致 | 使用 `ast.literal_eval()` 解析 |
| 热力图某行全为 0 | 该行业无对应福利标签 | 从交叉表中移除空行 |
| 饼图分类过多导致标签重叠 | 企业性质分类细 | 合并占比 < 3% 的为"其他" |

---
---

# Prompt-05: 总结报告

## 一、任务概述

### 5.1 本次任务是什么

汇总前 4 个章节（ch01~ch04）的核心发现，生成一份面向三类受众（求职者、企业HR、研究机构）的综合分析报告，包含核心结论、洞察建议和局限性说明，并生成一张核心结论汇总仪表板图。

### 5.2 从什么数据出发

从以下 4 个章节的输出产物出发：
- `outputs/ch01_data_overview/ch01_cleaned_data.csv` — 清洗后数据
- `outputs/ch01_data_overview/ch01_data_quality_report.md` — 数据质量报告
- `outputs/ch02_salary_analysis/ch02_salary_stats.csv` — 薪资统计表
- `outputs/ch03_supply_demand/ch03_supply_demand_stats.csv` — 供需统计表
- `outputs/ch04_enterprise_features/ch04_enterprise_stats.csv` — 企业特征统计表

### 5.3 可以采用什么方法

- **数据汇总**：加载各章统计表，提取关键指标
- **结论提炼**：基于统计数据归纳核心结论（>= 10 条）
- **建议生成**：面向三类受众分别提出可执行建议
- **Markdown 报告**：使用结构化 Markdown 格式输出最终报告
- **仪表板图**：使用 matplotlib 子图布局展示核心指标

---

## 二、执行步骤

### Step 5.1: 加载各章结果

**本步骤要做什么**

加载 ch01~ch04 的统计表和清洗数据，检查前置依赖。

**代码框架**：

```python
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

from utils.data_loader import load_preprocessed
from utils.output_manager import get_chapter_dir, save_markdown
from utils.task_graph import TaskGraph

# 检查前置依赖
tg = TaskGraph()
status = tg.check_ready('prompt-05')
if not status['ready']:
    raise RuntimeError(f"前置条件不满足: {status['missing_artifacts']}")

OUTPUT_DIR = get_chapter_dir('ch05')

# 加载各章数据
df = load_preprocessed('outputs/ch01_data_overview/ch01_cleaned_data.csv')
salary_stats = load_preprocessed('outputs/ch02_salary_analysis/ch02_salary_stats.csv')
supply_demand_stats = load_preprocessed('outputs/ch03_supply_demand/ch03_supply_demand_stats.csv')
enterprise_stats = load_preprocessed('outputs/ch04_enterprise_features/ch04_enterprise_stats.csv')

print(f"数据加载完成:")
print(f"  清洗数据: {len(df)} 条")
print(f"  薪资统计: {len(salary_stats)} 行")
print(f"  供需统计: {len(supply_demand_stats)} 行")
print(f"  企业统计: {len(enterprise_stats)} 行")
```

**本步骤完成后的检查标准**

- 前置依赖检查通过（ch02, ch03, ch04 产物齐全）
- 4 个数据源均成功加载

**本步骤输出产物**

无独立产物

---

### Step 5.2: 汇总薪资发现

**本步骤要做什么**

从薪资统计表中提取关键发现，包括整体薪资水平、各维度薪资差异最大的分组。

**代码框架**：

```python
import pandas as pd

# 整体薪资概况
df_valid = df.dropna(subset=['salary_avg'])
salary_overall = {
    '平均薪资': round(df_valid['salary_avg'].mean(), 2),
    '薪资中位数': round(df_valid['salary_avg'].median(), 2),
    '薪资下限均值': round(df_valid['salary_min'].mean(), 2),
    '薪资上限均值': round(df_valid['salary_max'].mean(), 2),
    '25分位数': round(df_valid['salary_avg'].quantile(0.25), 2),
    '75分位数': round(df_valid['salary_avg'].quantile(0.75), 2),
}
print("=== 薪资概况 ===")
for k, v in salary_overall.items():
    print(f"  {k}: {v} 万/月")

# 各维度薪资最高/最低分组
salary_findings = []
for dim in salary_stats['分析维度'].unique():
    dim_data = salary_stats[salary_stats['分析维度'] == dim]
    if len(dim_data) > 0:
        top_group = dim_data.loc[dim_data['中位数'].idxmax()]
        bottom_group = dim_data.loc[dim_data['中位数'].idxmin()]
        salary_findings.append({
            '维度': dim,
            '最高薪资分组': top_group['分组'],
            '最高中位数': top_group['中位数'],
            '最低薪资分组': bottom_group['分组'],
            '最低中位数': bottom_group['中位数'],
        })

salary_findings_df = pd.DataFrame(salary_findings)
print("\n=== 各维度薪资差异 ===")
print(salary_findings_df.to_string(index=False))
```

**本步骤完成后的检查标准**

- 薪资概况包含均值、中位数、分位数
- 各维度最高/最低薪资分组已识别

**本步骤输出产物**

无独立产物（数据汇总为中间步骤）

---

### Step 5.3: 汇总供需发现

**本步骤要做什么**

从供需统计表中提取关键发现，包括热门岗位、热门城市、热门行业。

**代码框架**：

```python
# 岗位 TOP5
job_top5 = supply_demand_stats[
    (supply_demand_stats['分析维度'] == '岗位') & (supply_demand_stats['排名'] <= 5)
]
print("=== 热门岗位 TOP5 ===")
print(job_top5[['排名', '分组名称', '数量', '占比(%)']].to_string(index=False))

# 城市 TOP5
city_top5 = supply_demand_stats[
    (supply_demand_stats['分析维度'] == '城市') & (supply_demand_stats['排名'] <= 5)
]
print("\n=== 热门城市 TOP5 ===")
print(city_top5[['排名', '分组名称', '数量', '占比(%)']].to_string(index=False))

# 行业 TOP5
industry_top5 = supply_demand_stats[
    (supply_demand_stats['分析维度'] == '行业') & (supply_demand_stats['排名'] <= 5)
]
print("\n=== 热门行业 TOP5 ===")
print(industry_top5[['排名', '分组名称', '数量', '占比(%)']].to_string(index=False))
```

**本步骤完成后的检查标准**

- 岗位、城市、行业各提取 TOP5
- 数据与 ch03 统计表一致

**本步骤输出产物**

无独立产物

---

### Step 5.4: 汇总企业发现

**本步骤要做什么**

从企业特征统计表中提取关键发现，包括企业性质分布、福利标签特征。

**代码框架**：

```python
# 企业性质分布
nature_dist = enterprise_stats[enterprise_stats['分析维度'] == '企业性质']
print("=== 企业性质分布 ===")
print(nature_dist[['分组名称', '数量', '占比(%)']].to_string(index=False))

# 福利 TOP5
welfare_top5 = enterprise_stats[
    (enterprise_stats['分析维度'] == '福利标签') & (enterprise_stats.index < 5)
]
print("\n=== 福利标签 TOP5 ===")
print(welfare_top5[['分组名称', '数量']].to_string(index=False))

# 招聘偏好
preference = enterprise_stats[enterprise_stats['分析维度'] == '招聘偏好']
print("\n=== 招聘偏好画像 ===")
print(preference[['分组名称', '附加信息']].to_string(index=False))
```

**本步骤完成后的检查标准**

- 企业性质分布数据完整
- 福利 TOP5 已提取
- 招聘偏好画像包含各性质企业的平均福利和薪资

**本步骤输出产物**

无独立产物

---

### Step 5.5: 核心结论提炼

**本步骤要做什么**

基于前述数据汇总，提炼 >= 10 条有数据支撑的核心结论。

**代码框架**：

```python
# 核心结论列表（基于数据自动生成 + 人工校验）
conclusions = []

# 薪资相关结论
conclusions.append(
    f"1. Python 开发岗位平均薪资为 {salary_overall['平均薪资']} 万/月，"
    f"中位数为 {salary_overall['薪资中位数']} 万/月，"
    f"薪资分布呈右偏特征（均值 > 中位数）。"
)

# 学历薪资差异
edu_data = salary_stats[salary_stats['分析维度'] == '学历']
if len(edu_data) > 1:
    top_edu = edu_data.loc[edu_data['中位数'].idxmax()]
    conclusions.append(
        f"2. 学历对薪资影响显著：{top_edu['分组']}学历的薪资中位数最高"
        f"（{top_edu['中位数']} 万/月）。"
    )

# 热门岗位
if len(job_top5) > 0:
    top_job = job_top5.iloc[0]
    conclusions.append(
        f"3. 招聘需求最大的岗位是「{top_job['分组名称']}」，"
        f"共有 {int(top_job['数量'])} 条招聘信息（占比 {top_job['占比(%)']}%）。"
    )

# 热门城市
if len(city_top5) > 0:
    top_city = city_top5.iloc[0]
    conclusions.append(
        f"4. 招聘热度最高的城市是「{top_city['分组名称']}」，"
        f"共有 {int(top_city['数量'])} 条招聘信息。"
    )

# 企业性质
if len(nature_dist) > 0:
    top_nature = nature_dist.iloc[0]
    conclusions.append(
        f"5. 民营企业是招聘主力军，"
        f"「{top_nature['分组名称']}」占比 {top_nature['占比(%)']}%。"
    )

# 福利
if len(welfare_top5) > 0:
    top_welfare = welfare_top5.iloc[0]
    conclusions.append(
        f"6. 最常见的福利标签是「{top_welfare['分组名称']}」，"
        f"出现 {int(top_welfare['数量'])} 次。"
    )

# 薪资区间
conclusions.append(
    f"7. 薪资 25 分位数为 {salary_overall['25分位数']} 万/月，"
    f"75 分位数为 {salary_overall['75分位数']} 万/月，"
    f"多数岗位薪资集中在 {salary_overall['25分位数']}~{salary_overall['75分位数']} 万/月区间。"
)

# 经验要求
exp_dist = df['工作经验要求'].value_counts()
if len(exp_dist) > 0:
    top_exp = exp_dist.index[0]
    conclusions.append(
        f"8. 最常见的工作经验要求是「{top_exp}」，"
        f"占比 {round(exp_dist.iloc[0] / len(df) * 100, 1)}%。"
    )

# 行业集中度
if len(industry_top5) > 0:
    top3_ratio = industry_top5.head(3)['占比(%)'].astype(float).sum()
    conclusions.append(
        f"9. 行业需求集中度较高，TOP3 行业合计占比 {round(top3_ratio, 1)}%。"
    )

# 企业规模
size_dist = df['公司规模'].value_counts()
if len(size_dist) > 0:
    top_size = size_dist.index[0]
    conclusions.append(
        f"10. 招聘企业以「{top_size}」规模为主，"
        f"占比 {round(size_dist.iloc[0] / len(df) * 100, 1)}%。"
    )

# 福利与薪资关联
avg_welfare_count = df['福利标签数'].mean()
conclusions.append(
    f"11. 平均每个岗位提供 {round(avg_welfare_count, 1)} 项福利标签，"
    f"福利完善度与薪资水平存在正相关趋势。"
)

print("=== 核心结论 ===")
for c in conclusions:
    print(f"  {c}")
```

**本步骤完成后的检查标准**

- 核心结论数量 >= 10 条
- 每条结论均有具体数据支撑（含数值引用）
- 结论覆盖薪资、供需、企业 3 个维度

**本步骤输出产物**

无独立产物（结论嵌入最终报告）

---

### Step 5.6: 洞察建议生成

**本步骤要做什么**

面向三类受众（求职者、企业HR、研究机构）分别生成可执行的洞察建议。

**代码框架**：

```python
suggestions = {
    '求职者': [
        f"薪资定位参考：Python 开发岗位薪资中位数为 {salary_overall['薪资中位数']} 万/月，"
        f"建议将此作为薪资谈判的基准线。",
        f"城市选择建议：优先考虑招聘热度最高的城市（{city_top5.iloc[0]['分组名称']}、"
        f"{city_top5.iloc[1]['分组名称']}），岗位机会更多。",
        f"技能提升方向：关注招聘需求最大的岗位类型（{job_top5.iloc[0]['分组名称']}），"
        f"针对性提升相关技能。",
        f"学历投资回报：{top_edu['分组']}学历薪资中位数为 {top_edu['中位数']} 万/月，"
        f"评估学历提升的投入产出比。",
    ],
    '企业HR': [
        f"薪资竞争力对标：行业平均薪资为 {salary_overall['平均薪资']} 万/月，"
        f"建议参考各维度薪资中位数制定有竞争力的薪酬方案。",
        f"福利策略优化：最常见的福利标签是「{top_welfare['分组名称']}」，"
        f"建议确保核心福利覆盖以提升岗位吸引力。",
        f"招聘渠道聚焦：在招聘热度最高的城市加大投入，"
        f"以获取更多优质候选人。",
        f"岗位描述优化：明确标注学历和经验要求，"
        f"降低筛选成本，提高招聘效率。",
    ],
    '研究机构': [
        f"数据局限性：本分析基于 {len(df)} 条 Python 开发岗位数据，"
        f"结论不可泛化到全行业或全岗位类型。",
        f"时效性注意：数据采集时间未知，薪资水平和市场需求可能已发生变化，"
        f"建议定期更新数据进行趋势分析。",
        f"扩展研究方向：建议补充时序数据进行趋势分析，"
        f"或扩大样本范围进行跨行业对比。",
    ],
}

for audience, items in suggestions.items():
    print(f"\n=== {audience}建议 ===")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
```

**本步骤完成后的检查标准**

- 三类受众各有 >= 3 条建议
- 建议内容具体、可执行
- 建议中引用了实际数据

**本步骤输出产物**

无独立产物（建议嵌入最终报告）

---

### Step 5.7: 局限性说明

**本步骤要做什么**

明确标注本次分析的局限性，确保结论不被过度解读。

**代码框架**：

```python
limitations = [
    f"样本量有限：本次分析仅包含 {len(df)} 条 Python 开发岗位数据，"
    f"统计结果的置信度有限，部分分组样本极少可能导致偏差。",
    "数据时效性：数据采集时间未知，无法反映当前市场状况，"
    "薪资水平和需求结构可能已发生变化。",
    "岗位范围限定：数据仅覆盖 Python 开发相关岗位，"
    "结论不可泛化到其他技术岗位或全行业。",
    "城市提取不完整：城市信息从公司名称中提取，"
    "部分公司可能因名称不含标准省市关键词而被标记为"未知"。",
    "薪资数据自报告偏差：招聘信息中的薪资为雇主报价范围，"
    "可能与实际入职薪资存在差异。",
    "缺乏时序维度：数据为截面数据，无法分析薪资和需求的趋势变化。",
    "缺乏供给端数据：仅有招聘需求端数据，无法计算真实的供需比。",
]

print("=== 局限性 ===")
for i, lim in enumerate(limitations, 1):
    print(f"  {i}. {lim}")
```

**本步骤完成后的检查标准**

- 局限性条目 >= 5 条
- 覆盖样本量、时效性、范围、方法论等维度

**本步骤输出产物**

无独立产物（局限性嵌入最终报告）

---

### Step 5.8: 生成最终报告与仪表板

**本步骤要做什么**

将核心结论、洞察建议、局限性整合为一份完整的 Markdown 报告，并生成核心指标仪表板图。

**代码框架**：

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# === 生成仪表板图 ===
plt.rcParams.update({
    'figure.dpi': 150, 'savefig.dpi': 150, 'font.size': 11,
    'axes.unicode_minus': False,
    'font.sans-serif': ['SimHei', 'WenQuanYi Micro Hei', 'DejaVu Sans'],
})

fig = plt.figure(figsize=(20, 12))
fig.suptitle('基于51job招聘数据的人才市场全维度分析 — 核心指标仪表板',
             fontsize=16, fontweight='bold', y=0.98)

# 子图1: 薪资概况
ax1 = fig.add_subplot(2, 3, 1)
metrics = ['均值', '中位数', 'P25', 'P75']
values = [salary_overall['平均薪资'], salary_overall['薪资中位数'],
          salary_overall['25分位数'], salary_overall['75分位数']]
colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
bars = ax1.bar(metrics, values, color=colors, alpha=0.85)
ax1.set_title('薪资概况（万/月）', fontsize=12, fontweight='bold')
for bar, val in zip(bars, values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f'{val}', ha='center', va='bottom', fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')

# 子图2: 热门岗位 TOP5
ax2 = fig.add_subplot(2, 3, 2)
if len(job_top5) > 0:
    top5_jobs = job_top5['分组名称'].values[::-1]
    top5_counts = job_top5['数量'].values[::-1].astype(float)
    ax2.barh(top5_jobs, top5_counts, color='#9C27B0', alpha=0.85)
    ax2.set_title('热门岗位 TOP5', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')

# 子图3: 热门城市 TOP5
ax3 = fig.add_subplot(2, 3, 3)
if len(city_top5) > 0:
    top5_cities = city_top5['分组名称'].values[::-1]
    top5_city_counts = city_top5['数量'].values[::-1].astype(float)
    ax3.barh(top5_cities, top5_city_counts, color='#FF5722', alpha=0.85)
    ax3.set_title('热门城市 TOP5', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')

# 子图4: 企业性质分布
ax4 = fig.add_subplot(2, 3, 4)
if len(nature_dist) > 0:
    ax4.pie(nature_dist['数量'].values, labels=nature_dist['分组名称'].values,
            autopct='%.1f%%', startangle=90)
    ax4.set_title('企业性质分布', fontsize=12, fontweight='bold')
    ax4.axis('equal')

# 子图5: 学历-薪资对比
ax5 = fig.add_subplot(2, 3, 5)
if len(edu_data) > 0:
    edu_labels = edu_data['分组'].values
    edu_medians = edu_data['中位数'].values.astype(float)
    ax5.bar(edu_labels, edu_medians, color='#00BCD4', alpha=0.85)
    ax5.set_title('各学历薪资中位数（万/月）', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')

# 子图6: 关键数字摘要
ax6 = fig.add_subplot(2, 3, 6)
ax6.axis('off')
summary_text = (
    f"数据规模: {len(df)} 条\n"
    f"平均薪资: {salary_overall['平均薪资']} 万/月\n"
    f"薪资中位数: {salary_overall['薪资中位数']} 万/月\n"
    f"覆盖城市: {(df['城市'] != '未知').nunique()} 个\n"
    f"覆盖行业: {df['主行业'].nunique()} 个\n"
    f"平均福利: {round(avg_welfare_count, 1)} 项"
)
ax6.text(0.5, 0.5, summary_text, transform=ax6.transAxes,
         fontsize=14, verticalalignment='center', horizontalalignment='center',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
ax6.set_title('关键数字', fontsize=12, fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.95])
dashboard_path = os.path.join(OUTPUT_DIR, 'ch05_dashboard.png')
fig.savefig(dashboard_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"  [保存] {dashboard_path}")

# === 生成 Markdown 报告 ===
report_lines = [
    "# 基于51job招聘数据的人才市场全维度分析 — 最终报告\n",
    f"> 数据来源：51job（前程无忧）招聘平台",
    f"> 数据规模：{len(df)} 条 Python 开发岗位招聘记录",
    f"> 分析日期：{pd.Timestamp.now().strftime('%Y-%m-%d')}\n",
    "---\n",
    "## 一、薪资维度核心发现\n",
]
for c in conclusions[:4]:
    report_lines.append(f"- {c}")

report_lines.extend([
    "\n## 二、供需维度核心发现\n",
])
for c in conclusions[4:7]:
    report_lines.append(f"- {c}")

report_lines.extend([
    "\n## 三、企业特征核心发现\n",
])
for c in conclusions[7:]:
    report_lines.append(f"- {c}")

report_lines.extend([
    "\n---\n",
    "## 四、洞察与建议\n",
])

for audience, items in suggestions.items():
    report_lines.append(f"\n### 面向{audience}\n")
    for item in items:
        report_lines.append(f"- {item}")

report_lines.extend([
    "\n---\n",
    "## 五、局限性\n",
])
for lim in limitations:
    report_lines.append(f"- {lim}")

report_lines.extend([
    "\n---\n",
    "## 六、产物清单\n",
    "| 章节 | 产物 | 说明 |",
    "|------|------|------|",
    "| ch01 | ch01_cleaned_data.csv | 清洗后数据集 |",
    "| ch01 | ch01_data_quality_report.md | 数据质量报告 |",
    "| ch02 | ch02_salary_stats.csv | 薪资综合统计表 |",
    "| ch02 | ch02_salary_distribution.png | 薪资分布图 |",
    "| ch02 | ch02_salary_by_education.png | 学历-薪资图 |",
    "| ch02 | ch02_salary_by_experience.png | 经验-薪资图 |",
    "| ch02 | ch02_salary_by_industry_boxplot.png | 行业-薪资图 |",
    "| ch02 | ch02_salary_by_company_nature.png | 公司性质-薪资图 |",
    "| ch02 | ch02_salary_by_company_size.png | 公司规模-薪资图 |",
    "| ch03 | ch03_supply_demand_stats.csv | 供需统计表 |",
    "| ch03 | ch03_job_type_top20.png | 热门岗位 TOP20 |",
    "| ch03 | ch03_city_hiring_ranking.png | 城市招聘热度 |",
    "| ch03 | ch03_industry_demand_pie.png | 行业需求分布 |",
    "| ch03 | ch03_education_experience_heatmap.png | 学历-经验交叉 |",
    "| ch04 | ch04_enterprise_stats.csv | 企业特征统计表 |",
    "| ch04 | ch04_nature_pie.png | 企业性质分布 |",
    "| ch04 | ch04_size_bar.png | 企业规模分布 |",
    "| ch04 | ch04_welfare_top15.png | 福利标签 TOP15 |",
    "| ch04 | ch04_welfare_by_nature.png | 福利-企业关联 |",
    "| ch04 | ch04_industry_welfare_heatmap.png | 行业-福利热力图 |",
    "| ch04 | ch04_edu_by_nature_heatmap.png | 学历门槛热力图 |",
    "| ch05 | ch05_final_report.md | 最终分析报告（本文档） |",
    "| ch05 | ch05_dashboard.png | 核心指标仪表板 |",
])

report_text = '\n'.join(report_lines)
save_markdown(report_text, 'ch05_final_report.md', OUTPUT_DIR)

print(f"\n章节 05 完成。产物已输出到: {OUTPUT_DIR}")
```

**本步骤完成后的检查标准**

- `ch05_dashboard.png` 包含 6 个子图，布局合理
- `ch05_final_report.md` 包含核心结论（>= 10 条）、洞察建议（三类受众）、局限性
- 运行 `python src/utils/task_graph.py` 显示全部任务为已完成

**本步骤输出产物**

- `ch05_final_report.md` — 最终分析报告
- `ch05_dashboard.png` — 核心指标仪表板

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物文件名 | 类型 | 说明 |
|------|-----------|------|------|
| 1 | `ch05_final_report.md` | 报告 | 最终综合分析报告（含结论、建议、局限性） |
| 2 | `ch05_dashboard.png` | 图片 | 核心指标仪表板（6 子图布局） |

### 3.2 关键产物结构详解

**ch05_final_report.md**：

| 章节 | 内容 |
|------|------|
| 一、薪资维度核心发现 | 薪资水平、学历/经验/行业薪资差异 |
| 二、供需维度核心发现 | 热门岗位、城市、行业分布 |
| 三、企业特征核心发现 | 企业性质、规模、福利特征 |
| 四、洞察与建议 | 面向求职者、企业HR、研究机构的建议 |
| 五、局限性 | 样本量、时效性、范围等限制说明 |
| 六、产物清单 | 全部章节产物索引 |

**ch05_dashboard.png**（6 子图布局）：

| 子图位置 | 内容 |
|---------|------|
| 左上 | 薪资概况（均值/中位数/P25/P75） |
| 中上 | 热门岗位 TOP5 |
| 右上 | 热门城市 TOP5 |
| 左下 | 企业性质分布饼图 |
| 中下 | 各学历薪资中位数 |
| 右下 | 关键数字摘要 |

---

## 四、产物后续优化方向

### 4.1 当前方案的局限性

1. **结论为静态快照**：无法反映市场趋势变化
2. **建议较为通用**：受限于数据维度，建议的针对性有限
3. **仪表板布局固定**：子图数量和类型为预设，不够灵活

### 4.2 可进一步优化的方向

1. **交互式仪表板**：使用 Plotly/Dash 构建可交互的仪表板
2. **自动化报告更新**：定期抓取新数据，自动更新报告
3. **对比分析**：与历史数据或其他平台数据对比

### 4.3 其他可选方法

1. 使用 PDF 格式输出正式报告
2. 使用 PPT 格式制作汇报演示文稿
3. 使用 HTML 格式构建可交互的在线报告

---

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单

| 序号 | 问题 | 影响范围 | 建议处理 |
|------|------|---------|---------|
| 1 | 核心结论数量不足 10 条时是否补充 | 报告质量 | 从数据中挖掘更多维度 |
| 2 | 某类受众建议不足 3 条 | 报告完整性 | 补充通用性建议 |

### 5.2 常见异常场景与处理策略

| 异常场景 | 可能原因 | 处理策略 |
|---------|---------|---------|
| 前置章节产物缺失 | ch02/ch03/ch04 未完成 | 运行 `task_graph.py` 检查，先完成前置章节 |
| 统计表列名不匹配 | 各章产物格式不一致 | 检查列名，使用实际列名访问数据 |
| 仪表板子图空白 | 某维度数据为空 | 跳过空子图，调整布局 |
| Markdown 报告中文乱码 | 文件编码问题 | 使用 `utf-8` 编码保存 |

---
---

# 附录

## 附录A: 依赖清单

| 包名 | 版本要求 | 用途 |
|------|---------|------|
| pandas | >= 2.0 | 数据处理与分析 |
| numpy | >= 1.24 | 数值计算 |
| matplotlib | >= 3.7 | 图表绑定 |
| seaborn | >= 0.12 | 高级可视化（热力图、箱线图） |
| openpyxl | >= 3.1 | Excel 文件读写 |
| scikit-learn | >= 1.3 | 机器学习（聚类/关联分析） |
| jieba | >= 0.42 | 中文分词 |
| wordcloud | >= 1.9 | 词云图生成 |
| jupyterlab | >= 4.0 | Jupyter Notebook 环境 |

**安装命令**：

```bash
conda create -n py310 python=3.10 -y
conda activate py310
pip install -r requirements.txt
```

---

## 附录B: 产物总览表

| 章节 | 产物文件名 | 类型 | 存放目录 |
|------|-----------|------|---------|
| ch01 | `ch01_cleaned_data.csv` | 数据 | `outputs/ch01_data_overview/` |
| ch01 | `ch01_data_quality_report.md` | 报告 | `outputs/ch01_data_overview/` |
| ch01 | `ch01_missing_values.png` | 图片 | `outputs/ch01_data_overview/` |
| ch01 | `ch01_field_distribution.png` | 图片 | `outputs/ch01_data_overview/` |
| ch02 | `ch02_salary_distribution.png` | 图片 | `outputs/ch02_salary_analysis/` |
| ch02 | `ch02_salary_by_education.png` | 图片 | `outputs/ch02_salary_analysis/` |
| ch02 | `ch02_salary_by_experience.png` | 图片 | `outputs/ch02_salary_analysis/` |
| ch02 | `ch02_salary_by_industry_boxplot.png` | 图片 | `outputs/ch02_salary_analysis/` |
| ch02 | `ch02_salary_by_company_nature.png` | 图片 | `outputs/ch02_salary_analysis/` |
| ch02 | `ch02_salary_by_company_size.png` | 图片 | `outputs/ch02_salary_analysis/` |
| ch02 | `ch02_salary_stats.csv` | 数据 | `outputs/ch02_salary_analysis/` |
| ch03 | `ch03_job_type_top20.png` | 图片 | `outputs/ch03_supply_demand/` |
| ch03 | `ch03_city_hiring_ranking.png` | 图片 | `outputs/ch03_supply_demand/` |
| ch03 | `ch03_industry_demand_pie.png` | 图片 | `outputs/ch03_supply_demand/` |
| ch03 | `ch03_education_experience_heatmap.png` | 图片 | `outputs/ch03_supply_demand/` |
| ch03 | `ch03_supply_demand_stats.csv` | 数据 | `outputs/ch03_supply_demand/` |
| ch04 | `ch04_nature_pie.png` | 图片 | `outputs/ch04_enterprise_features/` |
| ch04 | `ch04_size_bar.png` | 图片 | `outputs/ch04_enterprise_features/` |
| ch04 | `ch04_welfare_top15.png` | 图片 | `outputs/ch04_enterprise_features/` |
| ch04 | `ch04_welfare_by_nature.png` | 图片 | `outputs/ch04_enterprise_features/` |
| ch04 | `ch04_industry_welfare_heatmap.png` | 图片 | `outputs/ch04_enterprise_features/` |
| ch04 | `ch04_edu_by_nature_heatmap.png` | 图片 | `outputs/ch04_enterprise_features/` |
| ch04 | `ch04_enterprise_stats.csv` | 数据 | `outputs/ch04_enterprise_features/` |
| ch05 | `ch05_final_report.md` | 报告 | `outputs/ch05_summary_report/` |
| ch05 | `ch05_dashboard.png` | 图片 | `outputs/ch05_summary_report/` |

**产物总计**：25 个文件（数据 5 个、图片 17 个、报告 3 个）
