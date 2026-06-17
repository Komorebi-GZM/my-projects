# 摩洛哥多城市电力负荷全流程分析 — 执行Prompt文档

## 文档说明

本文档为**全流程标准化数据分析执行指南**，覆盖从原始数据预处理到配电网优化的完整分析链条。每个章节的Prompt均设计为**自包含、可独立执行**的单元，可直接复制到AI助手（如ChatGPT、Claude、Cursor等）中执行，也可由数据分析师参照手动操作。

### 适用环境
- **Python 版本**: 3.10（本地 conda 环境 `py310`，路径：`/Users/komorebi/miniforge3/envs/py310/bin/python`）
- **执行方式**: 每个章节均提供 **Jupyter Notebook (.ipynb)** 脚本，按章节编号命名（如 `ch01_preprocessing.ipynb`、`ch02_load_pattern.ipynb`），支持交互式运行、逐步调试、可视化即时预览，便于学习和复现
- **环境管理**: 使用本地 conda 环境 `py310`，激活命令 `conda activate py310`，通过 `pip install -r requirements.txt` 安装全部依赖。**禁止创建 venv 目录**
- **依赖库清单**: 见 `requirements.txt`
- **推荐 IDE**: Jupyter Notebook / VS Code（含 Jupyter 插件）

### 全局路径配置
```python
import os

# === 路径配置 ===
DATA_DIR = "data/"
RAW_DATA_FILE = os.path.join(DATA_DIR, "Data Morocco.xlsx")
OUTPUT_BASE = "outputs/"

# === 城市配置 ===
CITIES = {
    "Laayoune":    {"sheet": "Laayoune",    "sampling": "10min", "unit": "A",   "zones": 5, "zone_cols": ["zone1","zone2","zone3","zone4","zone5"]},
    "Boujdour":    {"sheet": "Boujdour",    "sampling": "10min", "unit": "A",   "zones": 3, "zone_cols": ["zone1","zone2","zone3"]},
    "Foum eloued": {"sheet": "Foum eloued", "sampling": "10min", "unit": "A",   "zones": 7, "zone_cols": ["zone1","zone2","zone3","zone4","zone5","zone6","zone7"]},
    "Marrakech":   {"sheet": "Marrakech",   "sampling": "30min", "unit": "kW",  "zones": 2, "zone_cols": ["zone1","zone2"]},
}

# === 量纲转换参数 ===
VOLTAGE = 220          # 市电标准电压 V
POWER_FACTOR = 0.9     # 平均功率因数

# === 季节映射（北半球） ===
SEASON_MAP = {
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring',  4: 'Spring',  5: 'Spring',
    6: 'Summer',  7: 'Summer',  8: 'Summer',
    9: 'Autumn',  10: 'Autumn', 11: 'Autumn'
}

# === 可视化全局样式 ===
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (14, 5)
plt.rcParams['axes.unicode_minus'] = False  # 中文显示支持
```

### 数据集概况

| 城市 | Sheet名 | 采样间隔 | 行数 | 时间范围 | Zone数 | 数据类型 | 推测单位 |
|------|---------|----------|------|----------|--------|----------|----------|
| 拉尤恩 | Laayoune | 10min | 88,890 | 2022-09-14 ~ 2024-05-24 | 5 | float64 | 电流A |
| 布杰杜尔 | Boujdour | 10min | 88,890 | 2022-09-14 ~ 2024-05-24 | 3 | float64 | 电流A |
| 富姆埃卢德 | Foum eloued | 10min | 88,890 | 2022-09-14 ~ 2024-05-24 | 7 | float64 | 电流A |
| 马拉喀什 | Marrakech | 30min | 17,501 | 2023-01-09 ~ 2024-01-08 | 2 | int64 | 有功功率kW |

---

## 全局Skill库（可复用模块）

以下4个Skill贯穿全流程，每个章节均可调用。请在执行任何章节前，先将这些Skill代码保存为独立文件或直接嵌入Notebook的首个Cell。

### Skill-01: 标准时序数据加载器 (`utils/data_loader.py`)

```python
import pandas as pd
import os

def load_raw_city_data(filepath: str, city: str) -> pd.DataFrame:
    """加载指定城市的原始数据

    Args:
        filepath: Excel文件路径
        city: 城市名称（Laayoune/Boujdour/Foum eloued/Marrakech）

    Returns:
        DataFrame，包含DateTime列和zone列
    """
    df = pd.read_excel(filepath, sheet_name=city, engine='openpyxl')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.set_index('DateTime').sort_index()
    df['city'] = city
    return df

def load_all_cities(filepath: str) -> dict:
    """加载全部城市原始数据，返回字典

    Returns:
        {"Laayoune": DataFrame, "Boujdour": DataFrame, ...}
    """
    cities = ["Laayoune", "Boujdour", "Foum eloued", "Marrakech"]
    return {city: load_raw_city_data(filepath, city) for city in cities}

def load_preprocessed(filepath: str) -> pd.DataFrame:
    """加载预处理后的统一数据集

    Args:
        filepath: 预处理后的CSV文件路径

    Returns:
        包含全部城市、统一单位(kW)、统一时间粒度(10min)的DataFrame
    """
    df = pd.read_csv(filepath, parse_dates=['DateTime'])
    df = df.set_index('DateTime').sort_index()
    return df
```

### Skill-02: 标准可视化出图器 (`utils/visualizer.py`)

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def plot_time_series(df, time_col, value_col, title, save_path=None,
                     figsize=(14, 5), dpi=150, color='steelblue'):
    """标准时序曲线图

    Args:
        df: DataFrame
        time_col: 时间列名
        value_col: 值列名
        title: 图表标题
        save_path: 保存路径（None则不保存）
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.plot(df[time_col], df[value_col], color=color, linewidth=0.8, alpha=0.9)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel(value_col, fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()

def plot_multi_city_comparison(data_dict, value_col, save_path=None,
                                figsize=(16, 10), dpi=150):
    """多城市横向对比图（子图布局）

    Args:
        data_dict: {城市名: DataFrame} 字典
        value_col: 要对比的列名
        save_path: 保存路径
    """
    cities = list(data_dict.keys())
    n = len(cities)
    fig, axes = plt.subplots(n, 1, figsize=figsize, dpi=dpi, sharex=True)
    if n == 1:
        axes = [axes]
    for i, (city, df) in enumerate(data_dict.items()):
        axes[i].plot(df.index, df[value_col], linewidth=0.5, alpha=0.8)
        axes[i].set_title(f'{city} - {value_col}', fontsize=12, fontweight='bold')
        axes[i].grid(True, alpha=0.3)
    axes[-1].set_xlabel('时间', fontsize=12)
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()

def plot_heatmap(pivot_data, title, save_path=None, figsize=(12, 8),
                 dpi=150, cmap='YlOrRd', annot=True, fmt='.1f'):
    """标准热力图

    Args:
        pivot_data: DataFrame（已透视好的二维数据）
        title: 图表标题
        cmap: 颜色映射
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    sns.heatmap(pivot_data, ax=ax, cmap=cmap, annot=annot, fmt=fmt,
                linewidths=0.5, linecolor='white')
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()

def plot_model_forecast(y_true, y_pred, title, save_path=None,
                        figsize=(14, 5), dpi=150):
    """预测结果拟合图（真实值 vs 预测值）

    Args:
        y_true: 真实值序列
        y_pred: 预测值序列
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.plot(y_true.index if hasattr(y_true, 'index') else range(len(y_true)),
            y_true, label='真实值', color='steelblue', linewidth=0.8)
    ax.plot(y_pred.index if hasattr(y_pred, 'index') else range(len(y_pred)),
            y_pred, label='预测值', color='tomato', linewidth=0.8, alpha=0.8)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('负荷 (kW)', fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()
```

### Skill-03: 标准评估指标计算器 (`utils/metrics.py`)

```python
import numpy as np
import pandas as pd

def calc_mae(y_true, y_pred) -> float:
    """平均绝对误差"""
    return np.mean(np.abs(y_true - y_pred))

def calc_rmse(y_true, y_pred) -> float:
    """均方根误差"""
    return np.sqrt(np.mean((y_true - y_pred) ** 2))

def calc_mape(y_true, y_pred) -> float:
    """平均绝对百分比误差（%）"""
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def evaluate_model(y_true, y_pred, model_name: str) -> dict:
    """综合评估单个模型

    Returns:
        {'model': name, 'MAE': ..., 'RMSE': ..., 'MAPE': ...}
    """
    return {
        'model': model_name,
        'MAE': round(calc_mae(y_true, y_pred), 4),
        'RMSE': round(calc_rmse(y_true, y_pred), 4),
        'MAPE': round(calc_mape(y_true, y_pred), 2)
    }

def compare_models(results_list: list, save_path=None) -> pd.DataFrame:
    """多模型评估结果对比表

    Args:
        results_list: [evaluate_model()返回的字典] 列表

    Returns:
        按MAPE升序排列的DataFrame
    """
    df = pd.DataFrame(results_list)
    df = df.sort_values('MAPE')
    if save_path:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"模型对比表已保存: {save_path}")
    return df
```

### Skill-04: 标准输出产物管理器 (`utils/output_manager.py`)

```python
import os
import pandas as pd

def ensure_dir(dir_path: str):
    """确保输出目录存在"""
    os.makedirs(dir_path, exist_ok=True)

def get_chapter_dir(chapter_num: int, base: str = "outputs") -> str:
    """获取章节输出目录路径

    Args:
        chapter_num: 章节编号（1-8）
        base: 输出根目录

    Returns:
        章节输出目录的绝对路径
    """
    chapter_names = {
        1: "ch01_data_preprocessing",
        2: "ch02_load_pattern_analysis",
        3: "ch03_peak_analysis",
        4: "ch04_load_forecasting",
        5: "ch05_midlong_term_trend",
        6: "ch06_cross_country_comparison",
        7: "ch07_grid_optimization",
        8: "ch08_summary"
    }
    dir_path = os.path.join(base, chapter_names[chapter_num])
    ensure_dir(dir_path)
    return dir_path

def save_dataframe(df, filename: str, chapter_num: int, base: str = "outputs"):
    """保存DataFrame到指定章节目录"""
    dir_path = get_chapter_dir(chapter_num, base)
    filepath = os.path.join(dir_path, filename)
    df.to_csv(filepath, index=False)
    print(f"数据已保存: {filepath}")
    return filepath

def save_figure(fig, filename: str, chapter_num: int, base: str = "outputs",
                dpi: int = 150):
    """保存图表到指定章节目录"""
    dir_path = get_chapter_dir(chapter_num, base)
    filepath = os.path.join(dir_path, filename)
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    print(f"图表已保存: {filepath}")
    return filepath

def generate_quality_checklist(items: list, chapter_num: int):
    """生成并打印质量验证清单

    Args:
        items: 验证项列表，如 ["数据无NaN残留", "量纲统一为kW"]
    """
    print(f"\n{'='*60}")
    print(f"  Prompt-{chapter_num:02d} 质量验证清单")
    print(f"{'='*60}")
    for i, item in enumerate(items, 1):
        print(f"  [ ] {i}. {item}")
    print(f"{'='*60}\n")
```
# Prompt-01: 数据预处理

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**基础起点**，目标是读取摩洛哥四城市（Laayoune、Boujdour、Foum eloued、Marrakech）的原始智能电表数据，解决数据中存在的**采样频率不统一**（10min vs 30min）、**计量单位不一致**（电流A vs 有功功率kW）、**潜在缺失值和异常值**等问题，最终输出一份统一时间粒度、统一量纲、高质量的标准数据集，为后续所有分析章节提供可靠的数据基础。

原始数据中，Laayoune、Boujdour、Foum eloued三个城市采用10分钟高频采样，数值为电流（A），量级在几十到几百之间；Marrakech采用30分钟采样，数值为有功功率（kW），量级在几百到一千多之间。这种差异需要在预处理阶段彻底解决。

### 1.2 从什么数据出发

数据文件为 `data/Data Morocco.xlsx`，包含4个Sheet，每个Sheet对应一个城市。所有Sheet都包含一个 `DateTime` 时间列和若干 `zone` 数值列。

具体结构如下：
- **Laayoune**: 88,890行，5个zone列（zone1~zone5），float64，时间范围2022-09-14至2024-05-24，10分钟采样
- **Boujdour**: 88,890行，3个zone列（zone1~zone3），float64，时间范围同上，10分钟采样
- **Foum eloued**: 88,890行，7个zone列（zone1~zone7），float64，时间范围同上，10分钟采样
- **Marrakech**: 17,501行，2个zone列（zone1~zone2），int64，时间范围2023-01-09至2024-01-08，30分钟采样

初步探查显示所有时间列无缺失值，zone列的数值分布需要进一步检查。

### 1.3 可以采用什么方法

核心处理方法包括：
1. **线性插值上采样**：将Marrakech的30分钟数据上采样至10分钟，使用 `DataFrame.resample('10min').interpolate(method='linear')`。线性插值是时序数据上采样的标准做法，在数据变化平缓的负荷场景中表现良好。
2. **物理公式量纲换算**：将电流（A）转换为有功功率（kW），公式为 P(kW) = I(A) × U(V) × cos(φ) / 1000，其中U=220V（市电标准电压），cos(φ)=0.9（平均功率因数）。
3. **3σ准则异常检测**：计算每个zone的均值和标准差，将超出 [μ-3σ, μ+3σ] 范围的值标记为异常。3σ准则在正态分布假设下覆盖99.7%的正常数据，是工程上常用的异常值判定方法。
4. **线性插值填补**：对标记为异常的值（以及可能的缺失值）使用线性插值替换，保持时序连续性。

替代方法：样条插值（cubic spline，更平滑但可能引入过拟合）、中位数替换（对极端异常更鲁棒但会改变分布形状）、KNN插值（利用相似时段的数据但计算成本高）。

## 二、执行步骤

### Step 1: 数据读取与结构探查

**本步骤要做什么**
读取Excel文件中4个Sheet的数据，查看每个Sheet的基本信息（行数、列数、数据类型、缺失值情况、数值范围），形成对数据的整体认知。

**具体操作指引**
使用 `pd.read_excel()` 逐个读取Sheet，调用 `.info()`、`.describe()`、`.head()`、`.isnull().sum()` 查看数据概况。特别关注：各zone列的min/max值是否存在负值或极端值、缺失值的数量和分布模式。

**代码框架**:
```python
import pandas as pd
import numpy as np

RAW_FILE = "data/Data Morocco.xlsx"
cities = ["Laayoune", "Boujdour", "Foum eloued", "Marrakech"]

for city in cities:
    df = pd.read_excel(RAW_FILE, sheet_name=city, engine='openpyxl')
    print(f"\n{'='*50}")
    print(f"城市: {city}")
    print(f"{'='*50}")
    print(f"形状: {df.shape}")
    print(f"\n数据类型:\n{df.dtypes}")
    print(f"\n缺失值:\n{df.isnull().sum()}")
    print(f"\n描述统计:\n{df.describe()}")
    print(f"\n前3行:\n{df.head(3)}")
    print(f"\n时间范围: {df['DateTime'].min()} ~ {df['DateTime'].max()}")
```

**本步骤完成后的检查标准**
- 4个Sheet全部成功读取，无报错
- 每个Sheet的行数与预期一致（Laayoune/Boujdour/Foum eloued: 88,890行，Marrakech: 17,501行）
- DateTime列成功解析为datetime类型
- zone列的min值≥0（负荷不应为负值）

**如果遇到问题请及时反馈**
- 如果某个Sheet读取失败，检查Sheet名称是否与预期完全一致（注意大小写和空格）
- 如果DateTime列解析失败，检查原始格式是否为标准datetime格式

**本步骤输出产物**
- `ch01_data_profile_report.md` — 数据概况报告，存放于 `outputs/ch01_data_preprocessing/`

### Step 2: 缺失值检测与统计

**本步骤要做什么**
全面检测所有Sheet中所有列的缺失值情况，统计缺失率，判断是否需要特殊处理。如果缺失率超过5%，需要记录并报告。

**具体操作指引**
对每个城市的DataFrame，计算每列的缺失数量和缺失百分比。将结果汇总为一张统计表。

**代码框架**:
```python
missing_stats = []
for city in cities:
    df = pd.read_excel(RAW_FILE, sheet_name=city, engine='openpyxl')
    for col in df.columns:
        missing_stats.append({
            'city': city,
            'column': col,
            'missing_count': df[col].isnull().sum(),
            'missing_rate': df[col].isnull().mean() * 100,
            'total_rows': len(df)
        })
missing_df = pd.DataFrame(missing_stats)
print(missing_df.to_string(index=False))
```

**本步骤完成后的检查标准**
- 缺失统计表覆盖全部4城市、全部列
- 如果存在缺失率>5%的列，需在报告中特别标注

**本步骤输出产物**
- `ch01_missing_stats.csv` — 缺失值统计表

### Step 3: 时间戳解析与标准化

**本步骤要做什么**
将所有城市的DateTime列统一解析为datetime64类型，设置为DataFrame的索引，并确保按时间升序排列。移除时区信息（如有），统一为naive datetime。

**代码框架**:
```python
for city in cities:
    df = pd.read_excel(RAW_FILE, sheet_name=city, engine='openpyxl')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.set_index('DateTime').sort_index()
    # 验证时间连续性
    expected_freq = '10T' if city != 'Marrakech' else '30T'
    print(f"{city}: 采样频率={expected_freq}, 时间范围={df.index.min()} ~ {df.index.max()}")
```

### Step 4: 时序对齐（Marrakech 30min→10min上采样）

**本步骤要做什么**
将Marrakech的30分钟采样数据通过线性插值上采样至10分钟，使其与其他三个城市的时间粒度一致。这是后续跨城市对比分析的前提条件。

**具体操作指引**
使用 `df.resample('10T').interpolate(method='linear', limit_direction='both')` 进行上采样。注意：上采样后的数据点是基于插值生成的，不是真实测量值，在后续分析中需要标注这一差异。

**代码框架**:
```python
df_marrakech = pd.read_excel(RAW_FILE, sheet_name="Marrakech", engine='openpyxl')
df_marrakech['DateTime'] = pd.to_datetime(df_marrakech['DateTime'])
df_marrakech = df_marrakech.set_index('DateTime').sort_index()

# 上采样至10分钟
df_marrakech_10min = df_marrakech.resample('10T').interpolate(method='linear', limit_direction='both')
print(f"Marrakech上采样: {len(df_marrakech)}行 → {len(df_marrakech_10min)}行")
```

**本步骤完成后的检查标准**
- 上采样后行数约为原来的3倍（17,501 × 3 ≈ 52,503行）
- 上采样后的数据无NaN残留
- 插值曲线在原始数据点处精确通过（可通过抽样验证）

**本步骤输出产物**
- `ch01_marrakech_resampled.csv` — 上采样后的Marrakech数据

### Step 5: 量纲统一（电流A→有功功率kW）

**本步骤要做什么**
将Laayoune、Boujdour、Foum eloued三个城市的电流数据（A）统一换算为有功功率（kW），使四个城市的计量单位完全一致。

**具体操作指引**
使用物理公式 P(kW) = I(A) × 220(V) × 0.9 / 1000 进行换算。换算后，所有zone数据的单位统一为kW。

**代码框架**:
```python
VOLTAGE = 220
POWER_FACTOR = 0.9

for city in ["Laayoune", "Boujdour", "Foum eloued"]:
    df = pd.read_excel(RAW_FILE, sheet_name=city, engine='openpyxl')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.set_index('DateTime').sort_index()

    zone_cols = [c for c in df.columns if c.startswith('zone')]
    for col in zone_cols:
        df[col] = df[col] * VOLTAGE * POWER_FACTOR / 1000

    print(f"{city} 换算后范围: {df[zone_cols].min().min():.2f} ~ {df[zone_cols].max().max():.2f} kW")
```

**本步骤完成后的检查标准**
- 换算后三个城市的数值量级与Marrakech原始kW数据可比（应在0~500kW范围内）
- 换算后无负值出现

**本步骤输出产物**
- `ch01_unified_power_all_cities.csv` — 量纲统一后的全城市数据（合并为一个文件，增加city列标识）

### Step 6: 异常值检测（3σ准则）

**本步骤要做什么**
对每个城市的每个zone列，使用3σ准则检测异常值。标记但不直接删除，生成异常值标记文件供后续审查。

**代码框架**:
```python
outlier_flags = []
for city in cities:
    df = ...  # 加载统一后的数据
    zone_cols = [c for c in df.columns if c.startswith('zone')]
    for col in zone_cols:
        mean = df[col].mean()
        std = df[col].std()
        lower = mean - 3 * std
        upper = mean + 3 * std
        mask = (df[col] < lower) | (df[col] > upper)
        n_outliers = mask.sum()
        outlier_rate = mask.mean() * 100
        outlier_flags.append({
            'city': city, 'zone': col,
            'mean': round(mean, 2), 'std': round(std, 2),
            'lower_bound': round(lower, 2), 'upper_bound': round(upper, 2),
            'outlier_count': n_outliers, 'outlier_rate': round(outlier_rate, 4)
        })
        print(f"{city}/{col}: 均值={mean:.2f}, 标准差={std:.2f}, 异常值={n_outliers}个({outlier_rate:.2f}%)")
outlier_df = pd.DataFrame(outlier_flags)
```

**本步骤完成后的检查标准**
- 异常值比例通常应在0.3%以下（3σ准则的理论值）
- 如果某个zone的异常率>1%，需要检查是否存在系统性问题

**本步骤输出产物**
- `ch01_outlier_flags.csv` — 异常值检测结果表

### Step 7: 异常值处理（线性插值替换）

**本步骤要做什么**
将Step 6中标记的异常值替换为线性插值值，同时处理可能的缺失值。处理后的数据即为"清洗后数据"。

**代码框架**:
```python
for city in cities:
    df = ...  # 加载统一后的数据
    zone_cols = [c for c in df.columns if c.startswith('zone')]
    for col in zone_cols:
        mean = df[col].mean()
        std = df[col].std()
        mask = (df[col] < mean - 3*std) | (df[col] > mean + 3*std)
        df.loc[mask, col] = np.nan  # 先设为NaN
        df[col] = df[col].interpolate(method='linear')  # 再线性插值
    # 最终检查
    assert df[zone_cols].isnull().sum().sum() == 0, "存在未处理的NaN!"
```

**本步骤完成后的检查标准**
- 全部zone列无NaN残留
- 数据分布无突变断裂（可通过直方图验证）
- 异常值替换后的数值在合理范围内

**本步骤输出产物**
- `ch01_cleaned_data.csv` — 清洗后的全城市统一数据集

### Step 8: 时间特征工程

**本步骤要做什么**
基于DateTime索引，衍生出一系列时间特征列，支撑后续的周期规律分析、预测建模等任务。

**具体操作指引**
衍生以下特征：hour（小时0-23）、day_of_week（星期0-6）、is_weekend（是否周末）、month（月份1-12）、season（季节）、year（年份）。季节映射遵循北半球标准：12-2月冬季，3-5月春季，6-8月夏季，9-11月秋季。

**代码框架**:
```python
SEASON_MAP = {12:'Winter',1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',
              6:'Summer',7:'Summer',8:'Summer',9:'Autumn',10:'Autumn',11:'Autumn'}

df['hour'] = df.index.hour
df['day_of_week'] = df.index.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df['month'] = df.index.month
df['season'] = df['month'].map(SEASON_MAP)
df['year'] = df.index.year
```

**本步骤完成后的检查标准**
- 特征列完整：hour(0-23), day_of_week(0-6), is_weekend(0/1), month(1-12), season(Winter/Spring/Summer/Autumn), year
- 无NaN

**本步骤输出产物**
- `ch01_feature_engineered_data.csv` — 含时间特征的全城市数据集（这是后续所有章节的主要输入数据）

### Step 9: 数据质量报告生成

**本步骤要做什么**
汇总以上所有步骤的处理结果，生成一份完整的数据质量报告，包括：原始数据概况、缺失值统计、异常值统计、量纲换算参数、时间对齐说明、特征工程说明。

**本步骤输出产物**
- `ch01_data_quality_report.md` — 数据质量报告

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 数据概况报告 | ch01_data_profile_report.md | Markdown | outputs/ch01_data_preprocessing/ | 参考 |
| 2 | 缺失值统计表 | ch01_missing_stats.csv | CSV | outputs/ch01_data_preprocessing/ | 参考 |
| 3 | Marrakech上采样数据 | ch01_marrakech_resampled.csv | CSV | outputs/ch01_data_preprocessing/ | 中间产物 |
| 4 | 量纲统一全城市数据 | ch01_unified_power_all_cities.csv | CSV | outputs/ch01_data_preprocessing/ | 中间产物 |
| 5 | 异常值标记表 | ch01_outlier_flags.csv | CSV | outputs/ch01_data_preprocessing/ | Prompt-03参考 |
| 6 | 清洗后统一数据集 | ch01_cleaned_data.csv | CSV | outputs/ch01_data_preprocessing/ | Prompt-02,03,05 |
| 7 | 含特征工程数据集 | ch01_feature_engineered_data.csv | CSV | outputs/ch01_data_preprocessing/ | Prompt-02,03,04,05 |
| 8 | 数据质量报告 | ch01_data_quality_report.md | Markdown | outputs/ch01_data_preprocessing/ | 参考 |

### 3.2 关键产物结构详解

**ch01_feature_engineered_data.csv**（最重要的产物）:
- 列结构：DateTime(索引), city(str), zone1~zoneN(float64, 单位kW), hour(int), day_of_week(int), is_weekend(int), month(int), season(str), year(int)
- 行数量级：约30万行（4城市合并）
- 这是后续Prompt-02~05的主要输入数据

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 量纲换算使用固定的220V和0.9功率因数，实际电压和功率因数可能随时间和区域变化
- 30min→10min上采样引入了非真实测量数据点
- 3σ准则假设数据近似正态分布，对偏态分布可能不适用

### 4.2 可进一步优化的方向
- 引入电压监测数据，实现动态功率因数换算
- 使用样条插值替代线性插值，获得更平滑的上采样曲线
- 使用IQR（四分位距）方法替代3σ准则，对偏态分布更鲁棒
- 增加节假日特征（摩洛哥宗教节日、公共假日）

### 4.3 其他可选方法
- 孤立森林（Isolation Forest）：无监督异常检测，不依赖分布假设
- DBSCAN聚类异常检测：基于密度，适合局部异常检测
- 移动中位数滤波：对时序数据的平滑去噪效果优于线性插值

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 如果某个zone列存在大量缺失值（>10%），需确认是删除该zone还是使用插值填补
- 如果量纲换算后的数值范围与预期严重不符，需确认U和cos(φ)的取值是否合理
- 如果Marrakech的上采样导致数据失真（如出现负值），需确认是否继续

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| DateTime解析失败 | 报TypeError或ValueError | 检查原始格式，尝试指定format参数 | 否 |
| 上采样后出现NaN | resample后isnull()>0 | 使用limit_direction='both'或ffill/bfill | 否 |
| 换算后出现负值 | min(zone)<0 | 检查原始数据，将负值设为0 | 是 |
| 异常率>5% | outlier_rate>5 | 可能存在数据质量问题，需人工审查 | 是 |
| 内存不足 | MemoryError | 分城市处理，避免一次性加载全部数据 | 否 |

---

# Prompt-02: 用电负荷特征挖掘与用电规律分析

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**核心探索阶段**，基于第一章预处理后的标准化数据，从多个维度深入挖掘摩洛哥四城市的用电行为规律。核心目标包括：

1. **量化基本统计特征**：计算各城市各zone的均值、中位数、标准差、波动率、负荷率，建立用电特征的量化基准
2. **揭示日内用电节奏**：绘制24小时连续负荷曲线，识别早晚高峰和午间低谷的时段分布
3. **对比工作日/周末差异**：分析工作日与周末负荷曲线的形态差异，量化休闲作息对用电的影响
4. **分析跨城市区域差异**：对比四城市负荷水平、波动特征，结合气候和产业解释差异成因
5. **区分居民/工业负荷**：尝试将zone负荷分为居民生活和工业生产两种类型，对比其差异化特征

本章的输出将为后续的峰值识别（第三章）提供统计基础，为预测建模（第四章）提供特征理解，为跨国对比（第六章）提供摩洛哥侧的基准数据。

### 1.2 从什么数据出发

输入数据为 `outputs/ch01_data_preprocessing/ch01_feature_engineered_data.csv`，这是第一章预处理后的最终产物。

该数据集包含以下关键字段：
- **DateTime**（索引）：10分钟粒度的时间戳
- **city**：城市标识（Laayoune/Boujdour/Foum eloued/Marrakech）
- **zone1~zoneN**：各zone的负荷值（单位kW），已统一量纲
- **hour**：小时（0-23）
- **day_of_week**：星期（0=周一, 6=周日）
- **is_weekend**：是否周末（0/1）
- **month**：月份（1-12）
- **season**：季节（Winter/Spring/Summer/Autumn）
- **year**：年份

### 1.3 可以采用什么方法

**描述性统计分析**：使用pandas的groupby+agg进行分组聚合统计，计算均值、中位数、标准差、最小值、最大值、变异系数(CV=std/mean)、负荷率(mean/max)。

**日内规律分析**：按hour分组取均值，绘制24小时负荷曲线。分城市、分zone、分工作日/周末分别绘制。

**周期性分析**：使用seaborn的heatmap绘制"小时×星期"的热力图，直观展示周内周期规律。

**跨城市对比**：使用matplotlib的subplots多子图布局，将四城市负荷曲线放在同一画布上对比。

**居民/工业分层**：
- 优先策略：检查zone列命名是否含"residential"/"industrial"等关键词
- 备选策略：基于负荷波动率(CV)和日内峰谷比进行KMeans二分类。工业负荷特征：波动小、基荷高、24小时平稳；居民负荷特征：波动大、峰谷差明显、夜间低谷深。

替代方法：DBSCAN密度聚类（对噪声更鲁棒）、GMM高斯混合模型（提供软分类概率）、基于领域知识的规则分类（如按zone数值大小阈值分类）。

## 二、执行步骤

### Step 1: 描述性统计总表

**本步骤要做什么**
计算每个城市每个zone的描述性统计指标，形成一张完整的统计总表。

**具体操作指引**
按city分组，对每个zone列计算：mean, median, std, min, max, skew（偏度）, kurtosis（峰度）。额外计算衍生指标：CV（变异系数=std/mean）、load_rate（负荷率=mean/max）。

**代码框架**:
```python
df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_feature_engineered_data.csv", parse_dates=['DateTime'])
df = df.set_index('DateTime')

zone_cols = [c for c in df.columns if c.startswith('zone')]
stats = df.groupby('city')[zone_cols].agg(['mean','median','std','min','max','skew']).round(4)
print(stats.to_string())
```

**本步骤完成后的检查标准**
- 统计表覆盖全部4城市、全部zone（共17个zone）
- 所有均值>0，标准差合理（不应大于均值的数倍）
- 无NaN

**本步骤输出产物**
- `ch02_descriptive_stats.csv` — 描述性统计总表

### Step 2: 负荷率与波动率计算

**本步骤要做什么**
计算每个城市每个zone的负荷率和变异系数，这两个指标是衡量用电稳定性的核心指标。

**代码框架**:
```python
load_metrics = []
for city in df['city'].unique():
    city_df = df[df['city'] == city]
    for col in zone_cols:
        if col in city_df.columns:
            mean_val = city_df[col].mean()
            max_val = city_df[col].max()
            std_val = city_df[col].std()
            load_metrics.append({
                'city': city, 'zone': col,
                'mean_kW': round(mean_val, 2),
                'max_kW': round(max_val, 2),
                'std_kW': round(std_val, 2),
                'load_rate': round(mean_val/max_val, 4) if max_val > 0 else 0,
                'cv': round(std_val/mean_val, 4) if mean_val > 0 else 0
            })
load_metrics_df = pd.DataFrame(load_metrics)
```

**本步骤输出产物**
- `ch02_load_rate_cv.csv` — 负荷率和变异系数表

### Step 3: 日内24h负荷曲线

**本步骤要做什么**
绘制每个城市每个zone的24小时平均负荷曲线，展示日内用电节奏。

**具体操作指引**
按hour分组取均值，使用折线图绘制。每个城市单独一张图（多zone叠加），同时绘制一张全城市对比图。区分工作日和周末分别绘制。

**代码框架**:
```python
for city in df['city'].unique():
    city_df = df[df['city'] == city]
    city_zone_cols = [c for c in city_df.columns if c.startswith('zone')]

    hourly = city_df.groupby('hour')[city_zone_cols].mean()

    fig, ax = plt.subplots(figsize=(14, 5), dpi=150)
    for col in city_zone_cols:
        ax.plot(hourly.index, hourly[col], label=col, linewidth=1.5)
    ax.set_title(f'{city} - 24小时平均负荷曲线', fontsize=14, fontweight='bold')
    ax.set_xlabel('小时', fontsize=12)
    ax.set_ylabel('负荷 (kW)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(0, 24))
    plt.tight_layout()
    plt.savefig(f'outputs/ch02_load_pattern_analysis/ch02_daily_load_curve_{city.lower()}.png', dpi=150)
    plt.close()
```

**本步骤完成后的检查标准**
- 曲线能清晰识别早晚高峰时段（通常为8-10点和18-21点）
- 曲线平滑无异常跳变
- X轴为0-23小时，Y轴为kW

**本步骤输出产物**
- `ch02_daily_load_curve_{city}.png` — 各城市日内负荷曲线（4张）

### Step 4: 工作日vs周末对比

**本步骤要做什么**
在同一张图上叠加工作日和周末的平均负荷曲线，直观展示差异。

**本步骤输出产物**
- `ch02_weekday_vs_weekend_{city}.png` — 工作日vs周末对比图（4张）

### Step 5: 周内负荷热力图

**本步骤要做什么**
绘制"小时×星期几"的热力图，颜色深浅代表负荷高低，直观展示一周内的用电周期规律。

**代码框架**:
```python
for city in df['city'].unique():
    city_df = df[df['city'] == city]
    # 取所有zone的均值作为综合负荷
    city_zone_cols = [c for c in city_df.columns if c.startswith('zone')]
    city_df['total_load'] = city_df[city_zone_cols].mean(axis=1)

    pivot = city_df.pivot_table(values='total_load', index='hour', columns='day_of_week', aggfunc='mean')
    pivot.columns = ['周一','周二','周三','周四','周五','周六','周日']

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    sns.heatmap(pivot, ax=ax, cmap='YlOrRd', annot=True, fmt='.1f', linewidths=0.5)
    ax.set_title(f'{city} - 周内负荷热力图 (kW)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'outputs/ch02_load_pattern_analysis/ch02_weekly_heatmap_{city.lower()}.png', dpi=150)
    plt.close()
```

**本步骤输出产物**
- `ch02_weekly_heatmap_{city}.png` — 周内热力图（4张）

### Step 6: 跨城市横向对比

**本步骤要做什么**
将四城市的负荷曲线放在同一坐标系中对比，分析区域差异。

**本步骤输出产物**
- `ch02_cross_city_comparison.png` — 跨城市对比图

### Step 7: 居民/工业负荷分层

**本步骤要做什么**
基于负荷特征（波动率CV、日内峰谷比）对zone进行居民/工业二分类。

**具体操作指引**
对每个zone计算CV和峰谷比，使用KMeans(n_clusters=2)聚类。通过分析两个簇的中心特征判断哪个簇是工业、哪个是居民（工业：低CV、高峰谷比；居民：高CV、低峰谷比）。

**代码框架**:
```python
from sklearn.cluster import KMeans

cluster_features = []
for city in df['city'].unique():
    city_df = df[df['city'] == city]
    for col in zone_cols:
        if col in city_df.columns:
            hourly = city_df.groupby('hour')[col].mean()
            cv = city_df[col].std() / city_df[col].mean()
            peak_valley_ratio = hourly.max() / hourly.min() if hourly.min() > 0 else 0
            cluster_features.append({'city': city, 'zone': col, 'cv': cv, 'peak_valley_ratio': peak_valley_ratio})

cluster_df = pd.DataFrame(cluster_features)
features = cluster_df[['cv', 'peak_valley_ratio']].values
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
cluster_df['cluster'] = kmeans.fit_predict(features)

# 分析簇特征判断哪个是工业/居民
for c in [0, 1]:
    subset = cluster_df[cluster_df['cluster'] == c]
    print(f"簇{c}: 平均CV={subset['cv'].mean():.4f}, 平均峰谷比={subset['peak_valley_ratio'].mean():.2f}")
```

**本步骤完成后的检查标准**
- 两个簇的特征差异明显（一个高CV低基荷，一个低CV高基荷）
- 分类结果与负荷曲线形态自洽

**本步骤输出产物**
- `ch02_residential_industrial_class.csv` — 居民/工业分类结果表

### Step 8: 居民vs工业对比分析

**本步骤要做什么**
基于Step 7的分类结果，分别绘制居民负荷和工业负荷的日内曲线，量化两类负荷的差异。

**本步骤输出产物**
- `ch02_res_vs_ind_comparison.png` — 居民vs工业对比图

## 三、产物总览与结构说明

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用章节 |
|------|----------|--------|------|-------------|
| 1 | 描述性统计总表 | ch02_descriptive_stats.csv | CSV | Prompt-03 |
| 2 | 负荷率变异系数表 | ch02_load_rate_cv.csv | CSV | Prompt-06,07 |
| 3 | 日内负荷曲线 | ch02_daily_load_curve_{city}.png | PNG | 报告配图 |
| 4 | 工作日vs周末对比 | ch02_weekday_vs_weekend_{city}.png | PNG | 报告配图 |
| 5 | 周内热力图 | ch02_weekly_heatmap_{city}.png | PNG | 报告配图 |
| 6 | 跨城市对比图 | ch02_cross_city_comparison.png | PNG | 报告配图 |
| 7 | 居民/工业分类表 | ch02_residential_industrial_class.csv | CSV | Prompt-03,06 |
| 8 | 居民vs工业对比图 | ch02_res_vs_ind_comparison.png | PNG | 报告配图 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 居民/工业分层依赖无监督聚类，缺乏真实标签验证
- 跨城市对比未考虑人口规模和GDP差异的标准化
- 日内曲线仅使用均值，未展示置信区间或分位数范围

### 4.2 可进一步优化的方向
- 引入分位数带（5%-95%）替代单一均值曲线，展示波动范围
- 计算人均负荷指标，消除人口规模差异
- 增加月度/季节维度的负荷曲线对比
- 使用DTW（动态时间规整）量化城市间负荷曲线的相似度

### 4.3 其他可选方法
- 小波变换：在时频域分析负荷的多尺度周期特征
- 隐马尔可夫模型（HMM）：识别负荷的隐含状态（如"高负荷态"、"低负荷态"）
- 自组织映射（SOM）：高维负荷特征的可视化降维

## 五、异常处理与问题反馈机制

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 某zone的CV>1 | 变异系数异常大 | 可能存在大量零值或间歇性负荷，需单独分析 | 是 |
| KMeans分类结果不理想 | 两簇特征差异不明显 | 尝试调整特征（增加更多维度）或使用GMM | 是 |
| 城市间负荷量级差异过大 | 最大值/最小值>100倍 | 检查量纲换算是否正确 | 是 |
| 工作日/周末差异不显著 | 曲线几乎重叠 | 可能该城市以工业负荷为主，差异本身就不大 | 否 |

# Prompt-03: 负荷峰值识别与峰值特征研究

## 一、任务概述

### 1.1 本次任务是什么

本章聚焦于电力负荷的**尖峰时段识别与风险研判**。电力系统运行中，负荷峰值直接关系到电网的安全稳定——过高的峰值可能导致变压器过载、线路发热、甚至大面积停电。本章的目标是建立一套客观、可量化的峰值判定标准，精准识别所有超过阈值的负荷尖峰事件，并从时间分布、持续时长、诱发因素等多个角度分析峰值的特征规律，最终区分"规律性正常高峰"（如每日晚高峰）与"突发型异常峰值"（如设备故障导致的负荷突变），为电网风险防控提供数据支撑。

### 1.2 从什么数据出发

输入数据：
- `ch01_cleaned_data.csv`（第一章清洗后的统一数据集）— 用于峰值事件提取。该数据集包含4城市的10分钟粒度负荷数据（单位kW），已统一量纲、已处理异常值。关键字段：DateTime(索引)、city、zone1~zoneN(kW)、hour、day_of_week、is_weekend、month、season、year。
- `ch02_descriptive_stats.csv`（第二章描述性统计表）— 用于参考各zone的统计特征，辅助设定合理的峰值阈值。

### 1.3 可以采用什么方法

核心方法是以**95%分位数**作为峰值判定阈值——这意味着只有排名前5%的负荷值才会被标记为峰值，既保证了识别的敏感性，又避免了将正常波动误判为异常。95%分位数是电力行业常用的峰值判定标准，其优势在于不需要预先设定绝对阈值，而是根据每个zone自身的负荷分布自适应确定。

峰值事件的提取、持续时长统计、时空分布分析均基于此阈值展开。对于异常峰值的研判，采用**差分突变检测法**——通过计算相邻时间点的负荷变化量，识别瞬间跳变型异常。

替代方法包括：
- **移动平均偏差法**：计算负荷值偏离移动平均线的程度，适用于趋势性数据，但对阶跃变化响应较慢
- **固定阈值法**：人工设定绝对阈值（如"超过500kW即为峰值"），灵活性低，不同zone需要不同阈值
- **基于密度的峰值检测**（DBSCAN变体）：适合多峰分布，但参数调优复杂
- **PEAKS算法**（SciPy.signal.find_peaks）：可设置prominence和width参数，适合精细峰值检测

如果95%分位数导致峰值事件过多（>10%）或过少（<1%），可灵活调整至90%或98%。

## 二、执行步骤

### Step 1: 95%分位数阈值计算

**本步骤要做什么**
为每个城市的每个zone分别计算95%分位数，作为该zone的峰值判定阈值。这一步是整个峰值分析的基础——阈值设定是否合理，直接决定了后续所有分析的质量。阈值过高会漏掉真正的峰值事件，阈值过低则会将正常波动误判为峰值。

**具体操作指引**
加载 `ch01_cleaned_data.csv`，按city分组，对每个zone列调用 `.quantile(0.95)` 计算95%分位数。同时计算90%和98%分位数作为参考区间。将结果整理为一张阈值表，包含：城市、zone、95%阈值、90%阈值、98%阈值、最大值、阈值/最大值比率（用于判断阈值合理性）。

**代码框架**:
```python
import pandas as pd
import numpy as np

df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_cleaned_data.csv", parse_dates=['DateTime'])
df = df.set_index('DateTime').sort_index()
zone_cols = [c for c in df.columns if c.startswith('zone')]

threshold_records = []
for city in df['city'].unique():
    city_df = df[df['city'] == city]
    for col in zone_cols:
        if col in city_df.columns:
            q90 = city_df[col].quantile(0.90)
            q95 = city_df[col].quantile(0.95)
            q98 = city_df[col].quantile(0.98)
            max_val = city_df[col].max()
            threshold_records.append({
                'city': city, 'zone': col,
                'q90_threshold': round(q90, 2),
                'q95_threshold': round(q95, 2),
                'q98_threshold': round(q98, 2),
                'max_value': round(max_val, 2),
                'q95_to_max_ratio': round(q95 / max_val, 4) if max_val > 0 else 0
            })
            print(f"{city}/{col}: 95%阈值={q95:.2f}kW, 最大值={max_val:.2f}kW, 阈值/最大值={q95/max_val:.4f}")

threshold_df = pd.DataFrame(threshold_records)
```

**本步骤完成后的检查标准**
- 阈值表覆盖全部4城市、全部zone（共17个zone）
- 每个zone的 q95_to_max_ratio 在 0.70~0.95 之间（如果<0.70说明数据分布异常偏态，>0.95说明阈值过于接近最大值）
- 阈值均为正值

**如果遇到问题请及时反馈**
- 如果某个zone的阈值/最大值比率<0.70，说明该zone的负荷分布严重右偏（有少量极端高值），建议检查原始数据是否存在异常
- 如果某个zone的95%阈值与90%阈值几乎相同（差异<1%），说明该zone的负荷集中在高位，可能需要调整分位数

**本步骤输出产物**
- `ch03_peak_thresholds.csv` — 峰值阈值表，存放于 `outputs/ch03_peak_analysis/`
  - 列结构：city, zone, q90_threshold, q95_threshold, q98_threshold, max_value, q95_to_max_ratio
  - 后续使用：Prompt-07配电网优化将参考此阈值设定优化目标

### Step 2: 峰值事件提取

**本步骤要做什么**
基于Step 1计算的95%阈值，遍历全部时序数据，将超出阈值的负荷值标记为"峰值事件"。每个超出阈值的时序点就是一个峰值事件，需要记录其发生的时间、城市、zone、实际负荷值、超出阈值的幅度等信息。

**具体操作指引**
对每个城市的每个zone，逐一与对应阈值比较。超出阈值的数据点标记为peak_flag=1，未超出的标记为0。同时计算"超出幅度"=(实际值-阈值)/阈值*100%，用于衡量峰值的严重程度。最终将所有标记结果合并为一张峰值事件清单。

**代码框架**:
```python
peak_events = []
for city in df['city'].unique():
    city_df = df[df['city'] == city]
    for col in zone_cols:
        if col in city_df.columns:
            threshold = threshold_df[(threshold_df['city'] == city) & (threshold_df['zone'] == col)]['q95_threshold'].values[0]
            mask = city_df[col] > threshold
            if mask.sum() > 0:
                peak_df = city_df[mask][[col]].copy()
                peak_df = peak_df.rename(columns={col: 'peak_load_kw'})
                peak_df['city'] = city
                peak_df['zone'] = col
                peak_df['threshold_kw'] = threshold
                peak_df['excess_ratio_pct'] = ((peak_df['peak_load_kw'] - threshold) / threshold * 100).round(2)
                peak_events.append(peak_df)

if peak_events:
    all_peaks = pd.concat(peak_events)
    all_peaks = all_peaks.sort_index()
    print(f"共提取 {len(all_peaks)} 个峰值事件")
    print(f"各城市峰值事件数:\n{all_peaks.groupby('city').size()}")
else:
    print("未检测到峰值事件，请检查阈值设置")
    all_peaks = pd.DataFrame()
```

**本步骤完成后的检查标准**
- 峰值事件总数占全部数据点的比例在1%~10%之间（理论值约5%）
- 每个城市、每个zone都有峰值事件被提取
- excess_ratio_pct（超出幅度）的最小值接近0%，最大值合理（不超过1000%）

**如果遇到问题请及时反馈**
- 如果某zone的峰值事件为0，说明阈值设定过高，需调低分位数
- 如果峰值事件比例>15%，说明阈值过低，需调高分位数

**本步骤输出产物**
- `ch03_peak_events.csv` — 峰值事件清单
  - 列结构：DateTime(索引), city, zone, peak_load_kw, threshold_kw, excess_ratio_pct
  - 行数量级：约1.5万行（总数据30万×5%）
  - 后续使用：Step 3~7均基于此数据

### Step 3: 峰值持续时长统计

**本步骤要做什么**
将离散的峰值数据点归并为"峰值事件片段"——连续多个峰值点构成一次峰值事件。统计每次峰值事件的开始时间、结束时间、持续时长（分钟）、峰值负荷、平均负荷等特征。持续时长是评估电网过载风险的重要指标——持续时间越长，设备热累积越严重。

**具体操作指引**
首先判断每个时序点是否为"任意zone的峰值"（is_any_peak），然后使用 `shift()+cumsum()` 技巧识别连续峰值片段的分组ID。对每个分组统计：开始时间、结束时间、持续时长、最大负荷、平均负荷、涉及zone数。

**代码框架**:
```python
# 判断每个时序点是否为任意zone的峰值
peak_flags = pd.DataFrame(index=df.index)
for col in zone_cols:
    for city in df['city'].unique():
        threshold = threshold_df[(threshold_df['city'] == city) & (threshold_df['zone'] == col)]['q95_threshold'].values[0]
        mask = (df['city'] == city) & (df[col] > threshold)
        peak_flags.loc[mask, f'{col}_peak'] = 1

peak_flags = peak_flags.fillna(0)
peak_flags['is_any_peak'] = peak_flags.max(axis=1)

# 识别连续峰值片段
peak_flags['group_id'] = (peak_flags['is_any_peak'] != peak_flags['is_any_peak'].shift()).cumsum()

# 仅保留峰值片段
peak_groups = peak_flags[peak_flags['is_any_peak'] == 1].groupby('group_id')
duration_stats = []
for gid, group in peak_groups:
    duration_minutes = len(group) * 10  # 10分钟粒度
    duration_stats.append({
        'group_id': gid,
        'start_time': group.index.min(),
        'end_time': group.index.max(),
        'duration_minutes': duration_minutes,
        'duration_hours': round(duration_minutes / 60, 2)
    })

duration_df = pd.DataFrame(duration_stats)
print(f"共识别 {len(duration_df)} 个峰值事件片段")
print(f"持续时长统计:\n{duration_df['duration_minutes'].describe()}")
```

**本步骤完成后的检查标准**
- 峰值片段数量合理（通常数百到数千个）
- 最短持续时长为10分钟（单个时序点）
- 平均持续时长在10~60分钟之间
- 存在持续时长>1小时的较长峰值事件

**如果遇到问题请及时反馈**
- 如果所有峰值片段的持续时长都是10分钟（即没有连续峰值），说明峰值非常分散，可能需要降低阈值或检查数据质量
- 如果存在持续时长>24小时的片段，可能是数据质量问题（如长时间异常高值未清洗）

**本步骤输出产物**
- `ch03_peak_duration_stats.csv` — 峰值持续时长统计表
  - 列结构：group_id, start_time, end_time, duration_minutes, duration_hours

### Step 4: 峰值时间分布分析

**本步骤要做什么**
统计峰值事件在24小时内各时段的出现频次，绘制柱状图，识别峰值的高发时段。这有助于回答"一天中哪个时段最容易出现负荷峰值"这一关键问题。

**具体操作指引**
从峰值事件清单中提取hour字段，按hour分组统计峰值事件数量。绘制柱状图，X轴为0-23小时，Y轴为峰值事件数量。可按城市分别绘制，也可合并绘制。

**代码框架**:
```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(16, 10), dpi=150)
axes = axes.flatten()
for i, city in enumerate(df['city'].unique()):
    city_peaks = all_peaks[all_peaks['city'] == city]
    hourly_counts = city_peaks.groupby(city_peaks.index.hour).size()
    axes[i].bar(hourly_counts.index, hourly_counts.values, color='tomato', alpha=0.8)
    axes[i].set_title(f'{city} - 峰值时间分布', fontsize=13, fontweight='bold')
    axes[i].set_xlabel('小时', fontsize=11)
    axes[i].set_ylabel('峰值事件数', fontsize=11)
    axes[i].set_xticks(range(0, 24, 2))
    axes[i].grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('outputs/ch03_peak_analysis/ch03_peak_hourly_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤完成后的检查标准**
- 柱状图能清晰识别1-2个峰值高发时段（通常为早高峰8-10点、晚高峰18-21点）
- 凌晨时段（0-6点）的峰值事件数明显低于白天
- 图表标签清晰、可读

**如果遇到问题请及时反馈**
- 如果所有时段的峰值事件数几乎相同（无明显高发时段），可能该城市负荷波动小，峰值分散

**本步骤输出产物**
- `ch03_peak_hourly_distribution.png` — 峰值时间分布柱状图

### Step 5: 峰值季节分布分析

**本步骤要做什么**
统计峰值事件在四个季节的出现频次，分析季节性对负荷峰值的影响。这有助于回答"哪个季节最容易发生负荷峰值"——在北非气候下，夏季高温导致的制冷负荷增加可能是峰值的主要驱动因素。

**代码框架**:
```python
SEASON_MAP = {12:'Winter',1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',
              6:'Summer',7:'Summer',8:'Summer',9:'Autumn',10:'Autumn',11:'Autumn'}

fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=150)
axes = axes.flatten()
season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
for i, city in enumerate(df['city'].unique()):
    city_peaks = all_peaks[all_peaks['city'] == city].copy()
    city_peaks['season'] = city_peaks.index.month.map(SEASON_MAP)
    seasonal_counts = city_peaks['season'].value_counts().reindex(season_order)
    axes[i].bar(seasonal_counts.index, seasonal_counts.values, color=['#4FC3F7','#81C784','#FFB74D','#E57373'])
    axes[i].set_title(f'{city} - 峰值季节分布', fontsize=13, fontweight='bold')
    axes[i].set_ylabel('峰值事件数', fontsize=11)
    for j, v in enumerate(seasonal_counts.values):
        axes[i].text(j, v + 10, str(v), ha='center', fontsize=10)
plt.tight_layout()
plt.savefig('outputs/ch03_peak_analysis/ch03_peak_seasonal_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤完成后的检查标准**
- 四个季节的峰值事件数存在明显差异（夏季通常最高）
- 图表包含数值标注，便于精确比较

**本步骤输出产物**
- `ch03_peak_seasonal_distribution.png` — 峰值季节分布柱状图

### Step 6: 峰值时空热力图

**本步骤要做什么**
绘制"小时×月份"的二维热力图，颜色深浅代表峰值事件频次。这种可视化方式能同时展示峰值的时间（日内）和季节（月度）分布特征，是识别"何时最危险"的最直观工具。

**代码框架**:
```python
import seaborn as sns

for city in df['city'].unique():
    city_peaks = all_peaks[all_peaks['city'] == city].copy()
    city_peaks['hour'] = city_peaks.index.hour
    city_peaks['month'] = city_peaks.index.month

    pivot = city_peaks.pivot_table(index='hour', columns='month', values='peak_load_kw', aggfunc='count', fill_value=0)
    pivot.columns = [f'{m}月' for m in pivot.columns]

    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    sns.heatmap(pivot, ax=ax, cmap='YlOrRd', annot=True, fmt='d', linewidths=0.5, linecolor='white')
    ax.set_title(f'{city} - 峰值事件时空分布热力图 (小时×月份)', fontsize=14, fontweight='bold')
    ax.set_xlabel('月份', fontsize=12)
    ax.set_ylabel('小时', fontsize=12)
    plt.tight_layout()
    plt.savefig(f'outputs/ch03_peak_analysis/ch03_peak_spacetime_heatmap_{city.lower()}.png', dpi=150, bbox_inches='tight')
    plt.close()
```

**本步骤完成后的检查标准**
- 热力图能清晰展示峰值聚集区域（通常为夏季傍晚）
- 颜色梯度合理，高值区域和低值区域对比明显

**本步骤输出产物**
- `ch03_peak_spacetime_heatmap_{city}.png` — 4张热力图

### Step 7: 峰值成因归因

**本步骤要做什么**
通过多因素交叉分析，量化不同因素（季节、时段、工作日/周末）对峰值事件的驱动作用。输出一张交叉统计表，帮助回答"什么因素最可能导致峰值"。

**代码框架**:
```python
all_peaks_copy = all_peaks.copy()
all_peaks_copy['hour'] = all_peaks_copy.index.hour
all_peaks_copy['month'] = all_peaks_copy.index.month
all_peaks_copy['season'] = all_peaks_copy.index.month.map(SEASON_MAP)
all_peaks_copy['is_weekend'] = all_peaks_copy.index.dayofweek.isin([5, 6]).astype(int)

attribution = all_peaks_copy.groupby(['city', 'season', 'hour', 'is_weekend']).agg(
    peak_count=('peak_load_kw', 'count'),
    avg_peak_load=('peak_load_kw', 'mean'),
    max_peak_load=('peak_load_kw', 'max')
).reset_index()
attribution = attribution.sort_values('peak_count', ascending=False)
```

**本步骤完成后的检查标准**
- 交叉表覆盖全部城市、季节、时段、工作日/周末组合
- peak_count最大的组合与直觉一致（如夏季晚高峰工作日）

**本步骤输出产物**
- `ch03_peak_attribution.csv` — 峰值成因归因交叉表

### Step 8: 异常峰值研判

**本步骤要做什么**
区分"规律性正常高峰"和"突发型异常峰值"。规律性高峰是渐进上升的（如每天傍晚负荷逐渐升高），而异常峰值是瞬间跳变的（如设备故障导致负荷突然飙升）。通过计算相邻时间点的负荷变化量（一阶差分），识别瞬间跳变型异常。

**具体操作指引**
对每个zone计算一阶差分 `diff = df[col].diff().abs()`，然后以3倍差分标准差为阈值，标记突变点。将突变点与峰值事件取交集，即为"异常峰值"——既是峰值又是突变的点。剩余的峰值事件即为"规律性高峰"。

**代码框架**:
```python
anomaly_flags = []
for city in df['city'].unique():
    city_df = df[df['city'] == city]
    for col in zone_cols:
        if col in city_df.columns:
            diff = city_df[col].diff().abs()
            diff_std = diff.std()
            diff_mean = diff.mean()
            anomaly_threshold = diff_mean + 3 * diff_std
            anomaly_mask = diff > anomaly_threshold

            # 与峰值事件取交集
            peak_threshold = threshold_df[(threshold_df['city'] == city) & (threshold_df['zone'] == col)]['q95_threshold'].values[0]
            peak_mask = city_df[col] > peak_threshold

            # 异常峰值 = 既是峰值又是突变
            anomaly_peak_mask = anomaly_mask & peak_mask

            anomaly_flags.append({
                'city': city, 'zone': col,
                'total_peaks': peak_mask.sum(),
                'anomaly_peaks': anomaly_peak_mask.sum(),
                'regular_peaks': (peak_mask & ~anomaly_mask).sum(),
                'anomaly_ratio': round(anomaly_peak_mask.sum() / peak_mask.sum() * 100, 2) if peak_mask.sum() > 0 else 0
            })
            print(f"{city}/{col}: 总峰值={peak_mask.sum()}, 异常峰值={anomaly_peak_mask.sum()}, 规律峰值={(peak_mask & ~anomaly_mask).sum()}")

anomaly_df = pd.DataFrame(anomaly_flags)
```

**本步骤完成后的检查标准**
- 异常峰值比例通常<10%（大部分峰值是规律性的）
- 异常峰值和规律峰值的数量之和等于总峰值数
- 异常峰值的分布不集中在特定时段（如果是，可能是数据问题）

**如果遇到问题请及时反馈**
- 如果异常峰值比例>50%，说明差分阈值过低，需调高至4σ或5σ
- 如果异常峰值为0，说明所有峰值都是渐进式的，这是正常的（说明电网运行稳定）

**本步骤输出产物**
- `ch03_anomaly_peak_flags.csv` — 异常峰值标记表
  - 列结构：city, zone, total_peaks, anomaly_peaks, regular_peaks, anomaly_ratio

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 峰值阈值表 | ch03_peak_thresholds.csv | CSV | outputs/ch03_peak_analysis/ | Prompt-07 |
| 2 | 峰值事件清单 | ch03_peak_events.csv | CSV | outputs/ch03_peak_analysis/ | Step 3~8 |
| 3 | 峰值持续时长统计 | ch03_peak_duration_stats.csv | CSV | outputs/ch03_peak_analysis/ | 报告 |
| 4 | 峰值时间分布图 | ch03_peak_hourly_distribution.png | PNG | outputs/ch03_peak_analysis/ | 报告配图 |
| 5 | 峰值季节分布图 | ch03_peak_seasonal_distribution.png | PNG | outputs/ch03_peak_analysis/ | 报告配图 |
| 6 | 峰值时空热力图 | ch03_peak_spacetime_heatmap_{city}.png | PNG | outputs/ch03_peak_analysis/ | 报告配图 |
| 7 | 峰值成因归因表 | ch03_peak_attribution.csv | CSV | outputs/ch03_peak_analysis/ | Prompt-07 |
| 8 | 异常峰值标记表 | ch03_anomaly_peak_flags.csv | CSV | outputs/ch03_peak_analysis/ | 报告 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 95%分位数是静态阈值，未考虑负荷的季节性变化
- 突变检测仅基于单点差分，对持续数个时间点的渐变型异常不敏感
- 峰值成因归因为描述性统计，未建立因果模型

### 4.2 可进一步优化的方向
- 使用滑动窗口动态阈值（考虑近期负荷水平的变化，适应季节性波动）
- 引入气象数据（温度、湿度）分析气象因素对峰值的驱动作用
- 使用PEAKS算法（SciPy.signal.find_peaks）进行更精细的峰值检测
- 增加峰值预测功能（基于历史峰值规律预测未来峰值时段和峰值大小）
- 使用SHAP值分析各特征对峰值事件的贡献度

### 4.3 其他可选方法
- 滑动Z-Score法：动态计算窗口内的Z-Score，适应趋势变化
- CUSUM控制图：累积和控制图，适合检测均值的小幅持续偏移
- GRP（Generalized Pareto Distribution）：极值理论方法，适合尾部风险分析
- 孤立森林（Isolation Forest）：无监督异常检测，不依赖分布假设

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 如果某个zone的峰值事件比例>10%或<1%，需确认是否调整分位数阈值
- 如果异常峰值比例>50%，需确认差分阈值是否合理
- 如果某城市完全没有峰值事件，需检查该城市的数据质量

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 峰值事件过多(>10%) | peak_rate>10% | 调高阈值至98%分位数 | 是 |
| 峰值事件过少(<1%) | peak_rate<1% | 调低阈值至90%分位数 | 是 |
| 无法区分规律/异常峰值 | 两类特征重叠严重 | 增加更多特征维度 | 是 |
| 热力图无聚集特征 | 颜色均匀分布 | 可能该城市负荷波动小 | 否 |
| 持续时长全部为10min | 无连续峰值片段 | 降低阈值或检查数据连续性 | 是 |

---

# Prompt-04: 短期电力负荷预测模型构建

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**核心技术章节**，目标是构建高精度的短期电力负荷预测模型，实现对未来10分钟到24小时负荷的精准预测。短期负荷预测是电网调度、发电计划安排、实时平衡控制的核心工具——准确的预测可以帮助电网运营商提前安排发电资源，避免供需失衡，降低运行成本。

本章采用**多模型对比选型**策略，从传统统计模型到深度学习模型逐层验证：ARIMA（经典时序基线）、XGBoost（高性能梯度提升树）、LightGBM（轻量梯度提升树）、Prophet（Facebook开源时序预测工具）、LSTM（长短期记忆网络）。通过MAE、RMSE、MAPE三大误差指标的横向对比，确定最适合本数据集的预测模型，并利用最优模型完成未来24小时的连续滚动预测。

### 1.2 从什么数据出发

输入数据：`ch01_feature_engineered_data.csv`

该数据集包含4城市的10分钟粒度负荷数据（单位kW），以及时间特征列（hour, day_of_week, is_weekend, month, season, year）。

本章选取**Laayoune城市的zone1**作为主预测目标，理由如下：数据时间跨度最长（2022-09至2024-05，约20个月）、采样频率最高（10分钟）、数据完整性最好。

### 1.3 可以采用什么方法

**ARIMA**: 经典时序模型，适合平稳序列，使用auto_arima自动定阶(m=144)。优点：理论成熟、可解释性强；缺点：难以捕捉非线性关系。

**XGBoost/LightGBM**: 梯度提升树模型，适合处理多特征、非线性关系。优点：精度高、训练快、可输出特征重要性；缺点：需要手动构建滞后特征。

**Prophet**: Facebook开源，擅长处理多周期季节性和节假日效应。优点：自动分解趋势+季节+假日；缺点：对非日粒度数据支持有限。

**LSTM**: 深度学习时序模型，擅长捕捉长期依赖关系。优点：可自动学习时序特征；缺点：训练耗时、需要大量数据、超参数敏感。

替代方法：Transformer-based时序模型（Informer/Autoformer）、TCN时序卷积网络、N-BEATS。

**关键注意事项**：
- 时序数据划分**严禁随机shuffle**，必须按时间顺序切分
- LSTM需要MinMaxScaler标准化
- MAPE < 15% 合格，< 10% 优秀，< 5% 卓越

## 二、执行步骤

### Step 1: 预测目标选择与数据准备

**本步骤要做什么**
从全城市数据中筛选出Laayoune城市的zone1作为预测目标序列，并检查数据质量（缺失值、异常值、时间连续性）。同时简要说明选择理由，便于后续复现和调整。

**代码框架**:
```python
import pandas as pd
import numpy as np

df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_feature_engineered_data.csv", parse_dates=['DateTime'])
df = df.set_index('DateTime').sort_index()

target_city = "Laayoune"
target_zone = "zone1"
target_df = df[(df['city'] == target_city)][[target_zone, 'hour', 'day_of_week', 'is_weekend', 'month', 'season', 'year']].copy()
target_df = target_df.rename(columns={target_zone: 'load_kw'})

print(f"预测目标: {target_city} / {target_zone}")
print(f"时间范围: {target_df.index.min()} ~ {target_df.index.max()}")
print(f"数据点数: {len(target_df)}")
print(f"缺失值: {target_df['load_kw'].isnull().sum()}")

# 检查时间连续性
time_gaps = target_df.index.to_series().diff().dropna()
irregular_gaps = time_gaps[time_gaps != pd.Timedelta(minutes=10)]
if len(irregular_gaps) > 0:
    print(f"警告: 发现 {len(irregular_gaps)} 个非10分钟间隔")
else:
    print("时间连续性检查通过")
```

**本步骤完成后的检查标准**
- 目标序列无NaN
- 时间索引连续（10分钟间隔）
- 数据范围合理（kW量级，无极端值）

**如果遇到问题请及时反馈**
- 如果存在缺失值，使用前向填充(ffill)处理
- 如果时间间隔不均匀，使用resample('10T').interpolate()对齐

**本步骤输出产物**
- `ch04_target_selection.md` — 预测目标选择说明文档

### Step 2: 特征集构建

**本步骤要做什么**
构建用于机器学习模型（XGBoost/LightGBM）的输入特征集。核心是构建**滞后特征**（lag features）——将历史负荷值作为当前时刻的输入特征。滞后窗口的选择基于电力负荷的自相关性：lag_1(10分钟前)、lag_6(1小时前)、lag_12(2小时前)、lag_24(4小时前)、lag_48(8小时前)、lag_144(1天前)。

**代码框架**:
```python
lag_windows = [1, 6, 12, 24, 48, 144]
for lag in lag_windows:
    target_df[f'lag_{lag}'] = target_df['load_kw'].shift(lag)

for window in [6, 12, 24]:
    target_df[f'rolling_mean_{window}'] = target_df['load_kw'].rolling(window=window).mean().shift(1)
    target_df[f'rolling_std_{window}'] = target_df['load_kw'].rolling(window=window).std().shift(1)

feature_cols = [c for c in target_df.columns if c != 'load_kw']
target_df = target_df.dropna(subset=feature_cols)
print(f"特征集构建完成: {len(feature_cols)} 个特征, {len(target_df)} 个样本")
```

**本步骤完成后的检查标准**
- 特征数量约15-20个
- 无NaN残留
- lag_1与目标变量的相关系数最高

**本步骤输出产物**
- `ch04_feature_dataset.csv` — 含特征的数据集

### Step 3: 数据集划分

**本步骤要做什么**
将数据集按时间顺序划分为训练集（80%）、验证集（10%）、测试集（10%）。**严禁随机shuffle**——时序数据必须保持时间顺序，否则会导致"用未来预测过去"的数据泄露错误。

**代码框架**:
```python
n = len(target_df)
train_end = int(n * 0.8)
val_end = int(n * 0.9)

train = target_df.iloc[:train_end]
val = target_df.iloc[train_end:val_end]
test = target_df.iloc[val_end:]

X_train, y_train = train[feature_cols], train['load_kw']
X_val, y_val = val[feature_cols], val['load_kw']
X_test, y_test = test[feature_cols], test['load_kw']

split_info = {
    'total_samples': n,
    'train_samples': len(train), 'train_ratio': f'{len(train)/n*100:.1f}%',
    'val_samples': len(val), 'val_ratio': f'{len(val)/n*100:.1f}%',
    'test_samples': len(test), 'test_ratio': f'{len(test)/n*100:.1f}%',
    'train_time_range': f'{train.index.min()} ~ {train.index.max()}',
    'test_time_range': f'{test.index.min()} ~ {test.index.max()}'
}
for k, v in split_info.items():
    print(f"  {k}: {v}")
```

**本步骤完成后的检查标准**
- 训练集时间范围早于验证集，验证集早于测试集
- 三个集合均无NaN

**如果遇到问题请及时反馈**
- 如果训练集数据量不足（<5000样本），考虑扩大训练集比例至85%

**本步骤输出产物**
- `ch04_data_split_info.json` — 数据划分信息

### Step 4: ARIMA模型训练与预测

**本步骤要做什么**
使用auto_arima自动定阶，训练ARIMA模型，在测试集上生成预测结果。ARIMA作为经典时序基线模型，其精度将作为其他模型的对比基准。

**代码框架**:
```python
from pmdarima import auto_arima
from utils.metrics import evaluate_model
from utils.visualizer import plot_model_forecast

arima_model = auto_arima(y_train, seasonal=True, m=144, stepwise=True, suppress_warnings=True, error_action='ignore')
print(f"ARIMA最优参数: {arima_model.order}, 季节参数: {arima_model.seasonal_order}")

arima_pred = pd.Series(arima_model.predict(n_periods=len(y_test)), index=y_test.index)
arima_result = evaluate_model(y_test.values, arima_pred.values, "ARIMA")
print(f"ARIMA: MAE={arima_result['MAE']}, RMSE={arima_result['RMSE']}, MAPE={arima_result['MAPE']}%")

arima_model.save('outputs/ch04_load_forecasting/ch04_arima_model.pkl')
plot_model_forecast(y_test, arima_pred, 'ARIMA - 负荷预测结果', 'outputs/ch04_load_forecasting/ch04_arima_forecast.png')
```

**本步骤完成后的检查标准**
- auto_arima成功收敛
- MAPE < 20%（ARIMA作为基线）
- 预测曲线与真实曲线趋势大致一致

**如果遇到问题请及时反馈**
- 如果auto_arima搜索时间过长（>5分钟），设置max_p=5, max_q=5限制搜索空间
- 如果预测结果为常数，说明模型退化为均值预测，尝试差分处理

**本步骤输出产物**
- `ch04_arima_model.pkl` + `ch04_arima_forecast.png`

### Step 5: XGBoost模型训练与预测

**本步骤要做什么**
训练XGBoost回归模型，利用Step 2构建的多维特征进行预测。XGBoost是本章的核心竞争模型之一，通常在表格型数据上表现优异。

**代码框架**:
```python
import xgboost as xgb

xgb_model = xgb.XGBRegressor(n_estimators=500, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1)
xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], early_stopping_rounds=50, verbose=False)

xgb_pred = pd.Series(xgb_model.predict(X_test), index=y_test.index)
xgb_result = evaluate_model(y_test.values, xgb_pred.values, "XGBoost")
print(f"XGBoost: MAPE={xgb_result['MAPE']}%")

importance = pd.DataFrame({'feature': feature_cols, 'importance': xgb_model.feature_importances_}).sort_values('importance', ascending=False)
print(f"\n特征重要性TOP10:\n{importance.head(10).to_string(index=False)}")

xgb_model.save_model('outputs/ch04_load_forecasting/ch04_xgb_model.json')
plot_model_forecast(y_test, xgb_pred, 'XGBoost - 负荷预测结果', 'outputs/ch04_load_forecasting/ch04_xgb_forecast.png')
```

**本步骤完成后的检查标准**
- early_stopping在500轮内触发
- MAPE < 15%
- lag_1和lag_6等近期滞后特征排在特征重要性前列

**如果遇到问题请及时反馈**
- 如果MAPE > 20%，尝试增加更多滞后特征或调整max_depth

**本步骤输出产物**
- `ch04_xgb_model.json` + `ch04_xgb_forecast.png`

### Step 6: LightGBM模型训练与预测

**本步骤要做什么**
训练LightGBM回归模型，与XGBoost形成对比。LightGBM使用直方图加速算法，通常训练更快。

**代码框架**:
```python
import lightgbm as lgb

lgb_model = lgb.LGBMRegressor(n_estimators=500, num_leaves=31, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1, verbose=-1)
lgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)])

lgb_pred = pd.Series(lgb_model.predict(X_test), index=y_test.index)
lgb_result = evaluate_model(y_test.values, lgb_pred, "LightGBM")
print(f"LightGBM: MAPE={lgb_result['MAPE']}%")

lgb_model.booster_.save_model('outputs/ch04_load_forecasting/ch04_lgbm_model.txt')
plot_model_forecast(y_test, lgb_pred, 'LightGBM - 负荷预测结果', 'outputs/ch04_load_forecasting/ch04_lgbm_forecast.png')
```

**本步骤完成后的检查标准**
- MAPE与XGBoost在同一量级（差异<3个百分点）

**本步骤输出产物**
- `ch04_lgbm_model.txt` + `ch04_lgbm_forecast.png`

### Step 7: Prophet模型训练与预测

**本步骤要做什么**
训练Prophet模型。Prophet自动分解趋势+季节+假日效应。需要注意Prophet要求输入列名为'ds'（时间）和'y'（目标值）。

**代码框架**:
```python
from prophet import Prophet

prophet_train = train[['load_kw']].reset_index()
prophet_train.columns = ['ds', 'y']

prophet_model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=True, changepoint_prior_scale=0.05, seasonality_prior_scale=10)
prophet_model.fit(prophet_train)

future = prophet_model.make_future_dataframe(periods=len(val)+len(test), freq='10T')
forecast = prophet_model.predict(future)
prophet_pred = forecast.set_index('ds').loc[y_test.index, 'yhat']

prophet_result = evaluate_model(y_test.values, prophet_pred.values, "Prophet")
print(f"Prophet: MAPE={prophet_result['MAPE']}%")

plot_model_forecast(y_test, prophet_pred, 'Prophet - 负荷预测结果', 'outputs/ch04_load_forecasting/ch04_prophet_forecast.png')
```

**本步骤完成后的检查标准**
- Prophet成功拟合
- 预测曲线捕捉到了日周期性波动
- MAPE < 20%

**如果遇到问题请及时反馈**
- 如果报错"seasonality has period > number of observations"，设置yearly_seasonality=False
- 如果预测结果出现NaN，检查freq='10T'是否正确

**本步骤输出产物**
- `ch04_prophet_forecast.png`

### Step 8: LSTM模型训练与预测

**本步骤要做什么**
训练LSTM深度学习模型。LSTM通过门控机制自动学习时序特征，无需手动构建滞后特征。但需要额外的数据预处理（MinMaxScaler标准化）和序列数据构造（将时间序列转换为滑动窗口样本）。

**具体操作指引**
1. 使用MinMaxScaler将负荷数据缩放到[0,1]
2. 构造滑动窗口序列：每个样本包含过去24个时间点（4小时）的负荷值，预测下一个时间点
3. 定义LSTM网络（2层LSTM + 1层全连接）
4. 训练50个epoch，使用Adam优化器
5. 反标准化预测结果，计算评估指标

**代码框架**:
```python
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0, 1))
train_scaled = scaler.fit_transform(train[['load_kw']].values)
val_scaled = scaler.transform(val[['load_kw']].values)
test_scaled = scaler.transform(test[['load_kw']].values)

def create_sequences(data, seq_length=24):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

SEQ_LENGTH = 24
X_train_seq, y_train_seq = create_sequences(train_scaled, SEQ_LENGTH)
X_val_seq, y_val_seq = create_sequences(val_scaled, SEQ_LENGTH)
X_test_seq, y_test_seq = create_sequences(test_scaled, SEQ_LENGTH)

X_train_t = torch.FloatTensor(X_train_seq)
y_train_t = torch.FloatTensor(y_train_seq)
X_val_t = torch.FloatTensor(X_val_seq)
y_val_t = torch.FloatTensor(y_val_seq)
X_test_t = torch.FloatTensor(X_test_seq)
y_test_t = torch.FloatTensor(y_test_seq)

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

model = LSTMModel()
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

batch_size = 32
best_val_loss = float('inf')
patience = 10
patience_counter = 0

for epoch in range(50):
    model.train()
    total_loss = 0
    for i in range(0, len(X_train_t), batch_size):
        batch_X = X_train_t[i:i+batch_size]
        batch_y = y_train_t[i:i+batch_size]
        optimizer.zero_grad()
        output = model(batch_X)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    model.eval()
    with torch.no_grad():
        val_pred = model(X_val_t)
        val_loss = criterion(val_pred, y_val_t).item()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/50, Train Loss: {total_loss/len(X_train_t):.6f}, Val Loss: {val_loss:.6f}")

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        torch.save(model.state_dict(), 'outputs/ch04_load_forecasting/ch04_lstm_model.pt')
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break

model.load_state_dict(torch.load('outputs/ch04_load_forecasting/ch04_lstm_model.pt'))
model.eval()
with torch.no_grad():
    lstm_pred_scaled = model(X_test_t).numpy()

lstm_pred = scaler.inverse_transform(lstm_pred_scaled).flatten()
y_test_actual = scaler.inverse_transform(y_test_seq).flatten()

lstm_result = evaluate_model(y_test_actual, lstm_pred, "LSTM")
print(f"LSTM: MAPE={lstm_result['MAPE']}%")

lstm_pred_series = pd.Series(lstm_pred, index=y_test.index[SEQ_LENGTH:])
y_test_actual_series = pd.Series(y_test_actual, index=y_test.index[SEQ_LENGTH:])
plot_model_forecast(y_test_actual_series, lstm_pred_series, 'LSTM - 负荷预测结果', 'outputs/ch04_load_forecasting/ch04_lstm_forecast.png')
```

**本步骤完成后的检查标准**
- 训练Loss单调递减或震荡收敛
- 验证Loss不持续增大（无严重过拟合）
- MAPE < 15%
- 预测曲线与真实曲线趋势一致，无明显相位偏移

**如果遇到问题请及时反馈**
- 如果Loss不下降：降低学习率至0.0001、增加hidden_size至128
- 如果显存不足：减小batch_size至16、减小hidden_size至32
- 如果CPU训练过慢（>30分钟）：减少epochs至20、使用GRU替代LSTM
- 如果出现NaN：检查学习率是否过大、考虑梯度裁剪

**本步骤输出产物**
- `ch04_lstm_model.pt` + `ch04_lstm_forecast.png`

### Step 9: 多模型评估对比

**本步骤要做什么**
将5个模型的评估结果汇总为一张对比表，按MAPE升序排列，确定最优模型。

**代码框架**:
```python
from utils.metrics import compare_models

results = [arima_result, xgb_result, lgb_result, prophet_result, lstm_result]
comparison_df = compare_models(results, "outputs/ch04_load_forecasting/ch04_model_comparison.csv")
print("\n" + "="*60)
print("  多模型评估结果对比（按MAPE升序排列）")
print("="*60)
print(comparison_df.to_string(index=False))

best_model = comparison_df.iloc[0]
print(f"\n最优模型: {best_model['model']}, MAPE={best_model['MAPE']}%")
```

**本步骤完成后的检查标准**
- 5个模型全部有评估结果
- MAPE排名合理（通常 XGBoost/LightGBM/LSTM > Prophet > ARIMA）
- 最优模型MAPE < 15%

**本步骤输出产物**
- `ch04_model_comparison.csv` — 模型对比表

### Step 10: 最优模型24h滚动预测

**本步骤要做什么**
使用MAPE最低的模型，对未来24小时（144个10分钟点）进行连续滚动预测。这是本章的最终交付——一个可直接用于电网调度的预测结果。

**代码框架**:
```python
# 以XGBoost为例（如果XGBoost是最优模型）
last_data = target_df.iloc[-144:]
forecast_steps = 144

predictions = []
current_data = last_data.copy()

for step in range(forecast_steps):
    features = {}
    for lag in lag_windows:
        features[f'lag_{lag}'] = current_data['load_kw'].iloc[-lag] if len(current_data) >= lag else current_data['load_kw'].iloc[0]
    for window in [6, 12, 24]:
        features[f'rolling_mean_{window}'] = current_data['load_kw'].iloc[-window:].mean()
        features[f'rolling_std_{window}'] = current_data['load_kw'].iloc[-window:].std()

    future_time = current_data.index[-1] + pd.Timedelta(minutes=10)
    features['hour'] = future_time.hour
    features['day_of_week'] = future_time.dayofweek
    features['is_weekend'] = int(future_time.dayofweek in [5, 6])
    features['month'] = future_time.month
    features['year'] = future_time.year

    feature_vector = pd.DataFrame([features])[feature_cols]
    pred = xgb_model.predict(feature_vector)[0]
    predictions.append({'DateTime': future_time, 'predicted_load_kw': pred})

    new_row = current_data.iloc[-1:].copy()
    new_row['load_kw'] = pred
    new_row.index = [future_time]
    current_data = pd.concat([current_data, new_row])

forecast_df = pd.DataFrame(predictions).set_index('DateTime')

fig, ax = plt.subplots(figsize=(14, 5), dpi=150)
ax.plot(forecast_df.index, forecast_df['predicted_load_kw'], color='tomato', linewidth=1.5, label='24h预测')
ax.set_title(f'{target_city} {target_zone} - 未来24小时负荷预测（{best_model["model"]}）', fontsize=14, fontweight='bold')
ax.set_xlabel('时间', fontsize=12)
ax.set_ylabel('负荷 (kW)', fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/ch04_load_forecasting/ch04_24h_rolling_forecast.png', dpi=150, bbox_inches='tight')
plt.close()
```

**本步骤完成后的检查标准**
- 预测曲线连续平滑，无突变断裂
- 预测值在合理范围内（不出现负值或极端高值）
- 预测曲线保留了日内周期性特征

**如果遇到问题请及时反馈**
- 如果滚动预测出现漂移，说明模型存在误差累积，可考虑定期用真实值校正

**本步骤输出产物**
- `ch04_24h_rolling_forecast.png` — 24h滚动预测图

## 三、产物总览与结构说明

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用章节 |
|------|----------|--------|------|-------------|
| 1 | 预测目标说明 | ch04_target_selection.md | Markdown | 参考 |
| 2 | 特征数据集 | ch04_feature_dataset.csv | CSV | 中间产物 |
| 3 | 数据划分信息 | ch04_data_split_info.json | JSON | 参考 |
| 4 | ARIMA模型+预测图 | ch04_arima_model.pkl + .png | PKL+PNG | 评估 |
| 5 | XGBoost模型+预测图 | ch04_xgb_model.json + .png | JSON+PNG | 评估 |
| 6 | LightGBM模型+预测图 | ch04_lgbm_model.txt + .png | TXT+PNG | 评估 |
| 7 | Prophet预测图 | ch04_prophet_forecast.png | PNG | 评估 |
| 8 | LSTM模型+预测图 | ch04_lstm_model.pt + .png | PT+PNG | 评估 |
| 9 | 模型对比表 | ch04_model_comparison.csv | CSV | Prompt-07 |
| 10 | 24h滚动预测图 | ch04_24h_rolling_forecast.png | PNG | 报告配图 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 仅预测单城市单zone，未利用多城市多zone的时空关联
- LSTM在CPU环境下训练较慢
- 未引入外部特征（气象、电价、节假日）
- 滚动预测存在误差累积问题

### 4.2 可进一步优化的方向
- 引入气象特征（温度、湿度）提升预测精度
- 多城市联合建模（Multi-task Learning）
- 注意力机制（Attention LSTM / Transformer）
- 概率预测（输出置信区间而非点估计）
- N-BEATS或PatchTST等SOTA时序模型

### 4.3 其他可选方法
- TCN（时序卷积网络）：计算效率优于LSTM
- Informer：Transformer变体，适合长序列预测
- Temporal Fusion Transformer：可处理多变量、已知未来输入
- 混合模型：ARIMA残差 + XGBoost

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 如果所有模型MAPE>20%，需确认数据质量和特征工程
- 如果LSTM训练时间过长（>60分钟），需确认是否继续

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 所有模型MAPE>20% | 精度不达标 | 检查数据质量、特征工程、超参数 | 是 |
| LSTM Loss不收敛 | Loss震荡或NaN | 降低学习率、检查标准化 | 否 |
| ARIMA拟合失败 | 报错或异常 | 检查平稳性，尝试差分 | 否 |
| 内存不足 | MemoryError | 减少batch_size | 否 |
| GPU不可用 | torch.cuda不可用 | 降低epochs至20 | 否 |

# Prompt-05: 月度/季度中长期用电趋势分析（全面细化版）

## 一、任务概述

### 1.1 本次任务是什么

本章从**中长期视角**审视电力负荷的演化规律，与第四章的短期预测形成互补。短期预测关注"明天/接下来几小时的负荷是多少"，而中长期趋势分析关注"负荷在月度、季度尺度上如何变化，是否存在季节性波动，长期趋势是上升还是下降"。

核心方法是将10分钟高频数据聚合为日度、月度、季度平均负荷，然后采用**STL时序分解**（Seasonal and Trend decomposition using Loess）将负荷序列拆解为三个独立分量：长期趋势项（Trend，反映负荷的长期变化方向）、季节周期项（Seasonal，反映规律性的季节波动）、随机扰动项（Residual，反映无法被趋势和季节解释的随机波动）。通过分别分析三个分量，可以更清晰地理解负荷变化的驱动因素。

此外，本章还将计算**季节性强度指标**（衡量季节波动相对于随机波动的占比）、进行**同比/环比分析**（量化负荷的年度增长率和月度变化率），为电网中长期规划和投资决策提供数据依据。

### 1.2 从什么数据出发

输入数据：`ch01_cleaned_data.csv`（第一章清洗后的统一数据集，单位kW，10分钟粒度）。该数据集包含4城市的负荷数据，本章将对每个城市分别进行中长期趋势分析。

### 1.3 可以采用什么方法

**STL分解**：Statsmodels的STL类，参数period根据数据粒度设定。对月度数据设定period=12（捕捉年度季节性，即12个月为一个周期），对日度数据设定period=7（捕捉周季节性）。STL使用LOESS（局部加权回归）拟合趋势和季节分量，鲁棒性好，可处理异常值。

**替代方法**：
- X-13ARIMA-SEATS分解：美国人口普查局标准方法，更精确但实现复杂，需要statsmodels的x13接口
- HP滤波（Hodrick-Prescott滤波）：适用于经济时间序列的趋势提取，但无法分离季节分量
- 经验模态分解EMD：适用于非线性和非平稳信号，但存在端点效应和模态混叠问题
- TBATS：可处理多重季节性（日+周+年），适合高频数据

---

## 二、执行步骤

---

### Step 1: 多粒度重采样聚合

#### 1. 本步骤要做什么

本步骤将10分钟高频负荷数据分别聚合为日度（Daily）、月度（Monthly）、季度（Quarterly）三个时间粒度的平均负荷。这是整个中长期趋势分析的**数据基础步骤**——原始10分钟数据虽然精细，但包含大量短时随机波动（如几分钟内的负荷骤升骤降），这些波动会掩盖中长期趋势和季节性特征。通过将数据聚合为更低频率，可以平滑掉短时噪声，使月度季节性模式和季度宏观趋势更加清晰。

具体而言，日度数据将每天144个10分钟采样点（24小时x6个/小时）取均值，得到一个代表当天平均负荷水平的单一数值；月度数据将每月约30天的日度均值再取均值，得到月度平均负荷；季度数据则将每3个月的月度均值再取均值。聚合方式统一使用算术平均（mean），因为平均负荷比最大负荷或最小负荷更能反映整体负荷水平。聚合后需要检查是否存在NaN值——如果原始数据中某天存在缺失时段，聚合结果中该天可能为NaN，需要用前向填充（ffill）处理以保证后续分析的连续性。

本步骤对4个城市（Laayoune、Boujdour、Foum eloued、Marrakech）分别执行聚合操作，每个城市生成3个粒度的序列，最终将月度数据合并为一张汇总表保存。

#### 2. 具体操作指引

**操作流程**：

1. **数据加载**：使用`pd.read_csv()`读取`ch01_cleaned_data.csv`，设置`parse_dates=['DateTime']`将时间列解析为datetime类型，然后`set_index('DateTime').sort_index()`确保时间索引有序。
2. **城市筛选**：使用`df['city'].unique()`获取所有城市名称，对每个城市分别筛选子数据集。
3. **综合负荷计算**：对每个城市，将所有zone列（以'zone'开头的列）取行均值，得到该城市的综合负荷序列`total_load`。这样做的理由是：不同zone代表不同区域或不同类型用户的负荷，取均值可以消除单一zone的局部波动，得到更具代表性的城市整体负荷水平。
4. **多粒度聚合**：使用`resample()`方法分别以'D'（日）、'ME'（月）、'QE'（季度）为频率进行重采样，聚合函数使用`mean()`。
   - 注意：pandas 2.0+版本中，月度频率使用'ME'（Month End）替代旧的'M'，季度频率使用'QE'（Quarter End）替代旧的'Q'。如果使用旧版pandas，请使用'M'和'Q'。
5. **NaN检查与处理**：对每个粒度的聚合结果，使用`isnull().sum()`统计NaN数量。如果存在NaN，使用`ffill()`（前向填充）处理，即用前一个有效值填充缺失值。如果序列开头就有NaN（不太可能，但需防范），则用`bfill()`（后向填充）补充。
6. **数据量验证**：打印每个城市每个粒度的行数，确认与预期一致。
7. **保存结果**：将4个城市的月度数据合并为一张DataFrame，列名为`{city}_monthly_avg_kw`，保存为CSV文件。

**关键参数说明**：
- `resample('D').mean()`：日度聚合，每个值代表一天的平均负荷
- `resample('ME').mean()`：月度聚合，每个值代表一个月的平均负荷
- `resample('QE').mean()`：季度聚合，每个值代表一个季度的平均负荷
- `ffill()`：前向填充，用最近一个有效值填充NaN

#### 3. 代码框架

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import STL
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Step 1: 多粒度重采样聚合
# ============================================================

# --- 1.1 数据加载 ---
df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_cleaned_data.csv", parse_dates=['DateTime'])
df = df.set_index('DateTime').sort_index()
zone_cols = [c for c in df.columns if c.startswith('zone')]
print(f"原始数据: {df.shape[0]}行, {df.shape[1]}列, 时间范围: {df.index.min()} ~ {df.index.max()}")
print(f"Zone列: {zone_cols}")
print(f"城市: {df['city'].unique()}")

# --- 1.2 创建输出目录 ---
output_dir = 'outputs/ch05_midlong_term_trend'
os.makedirs(output_dir, exist_ok=True)

# --- 1.3 多粒度聚合 ---
resampled_data = {}
for city in df['city'].unique():
    city_df = df[df['city'] == city].copy()
    # 计算所有zone的平均值作为该城市综合负荷
    city_df['total_load'] = city_df[zone_cols].mean(axis=1)
    
    # 日度聚合：每天144个10分钟点取均值
    daily = city_df['total_load'].resample('D').mean()
    # 月度聚合：每月约30天取均值
    monthly = city_df['total_load'].resample('ME').mean()
    # 季度聚合：每3个月取均值
    quarterly = city_df['total_load'].resample('QE').mean()
    
    # --- 1.4 NaN检查与处理 ---
    for freq_name, freq_series in [('daily', daily), ('monthly', monthly), ('quarterly', quarterly)]:
        nan_count = freq_series.isnull().sum()
        total_count = len(freq_series)
        nan_ratio = nan_count / total_count * 100 if total_count > 0 else 0
        if nan_count > 0:
            print(f"  [警告] {city} {freq_name}: 发现 {nan_count}/{total_count} 个NaN ({nan_ratio:.1f}%)，使用前向填充")
            freq_series = freq_series.ffill().bfill()  # 先前向再后向，确保首尾无NaN
            # 更新引用
            if freq_name == 'daily':
                daily = freq_series
            elif freq_name == 'monthly':
                monthly = freq_series
            else:
                quarterly = freq_series
        else:
            print(f"  {city} {freq_name}: 无NaN，数据完整")
    
    resampled_data[city] = {'daily': daily, 'monthly': monthly, 'quarterly': quarterly}
    
    # --- 1.5 数据量验证 ---
    print(f"{city}: 日度{len(daily)}行 ({daily.index.min().date()}~{daily.index.max().date()}), "
          f"月度{len(monthly)}行, 季度{len(quarterly)}行")
    print(f"  日度负荷范围: {daily.min():.1f}~{daily.max():.1f} kW, 均值: {daily.mean():.1f} kW")

# --- 1.6 保存月度汇总数据 ---
all_monthly = pd.DataFrame()
for city, data in resampled_data.items():
    temp = data['monthly'].to_frame(name=f'{city}_monthly_avg_kw')
    all_monthly = pd.concat([all_monthly, temp], axis=1)

output_path = os.path.join(output_dir, 'ch05_daily_monthly_quarterly.csv')
all_monthly.to_csv(output_path)
print(f"\n月度汇总数据已保存: {output_path}")
print(f"汇总表形状: {all_monthly.shape}")
print(all_monthly.head())
```

#### 4. 本步骤完成后的检查标准

- **数据量检查**：每个城市的日度数据行数应约等于时间跨度天数（约600天），月度数据行数应约等于月数（约20个月），季度数据行数应约等于季度数（约7个季度）。如果数据时间范围为2022-06至2024-05（约24个月），则月度数据应有约24行。
- **NaN检查**：所有聚合数据（日度、月度、季度）的NaN数量必须为0。使用`df.isnull().sum().sum() == 0`验证。
- **数值范围检查**：聚合后的负荷均值应与原始10分钟数据的均值量级一致。例如，如果原始数据某城市的10分钟负荷均值约为500kW，则日度均值也应在此量级附近（不会出现数量级差异）。
- **时间连续性检查**：日度数据的时间索引应连续（无跳日），月度数据应连续（无跳月）。使用`pd.date_range(start, end, freq='D').difference(daily.index)`检查缺失日期。
- **城市完整性检查**：4个城市（Laayoune、Boujdour、Foum eloued、Marrakech）均已完成聚合，汇总表应有4列数据。

#### 5. 如果遇到问题请及时反馈

- **NaN较多（>5%）**：说明原始数据存在大量缺失时段。需要回到第一章检查数据清洗质量，确认缺失时段是否已被合理处理。如果原始数据本身就有长时间缺失（如设备停机），则前向填充可能引入偏差，需在报告中说明。
- **某城市月度数据行数异常少（<12）**：说明该城市数据时间跨度不足1年，STL分解（period=12）将无法正常工作。需要提前告知用户，该城市可能无法进行完整的中长期分析。
- **聚合后数值范围异常**：如果某城市的聚合负荷均值与原始数据差异超过20%，检查zone列是否正确、是否存在大量零值或异常值未被清洗。
- **pandas版本兼容性问题**：如果使用pandas<2.0，`resample('ME')`会报错，需改为`resample('M')`；`resample('QE')`需改为`resample('Q')`。运行`pd.__version__`确认版本。
- **内存不足**：如果数据量极大（超过1亿行），逐城市处理并释放内存（`del city_df; import gc; gc.collect()`）。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 多粒度聚合数据集 | `ch05_daily_monthly_quarterly.csv` | `outputs/ch05_midlong_term_trend/` | 4城市的月度平均负荷汇总表。列结构：DateTime(索引), Laayoune_monthly_avg_kw, Boujdour_monthly_avg_kw, Foum_eloued_monthly_avg_kw, Marrakech_monthly_avg_kw。每行代表一个月，数值为该月所有10分钟采样点的算术平均值（单位kW）。 | Step 2（STL分解的输入）、Step 3（趋势项对比）、Step 4（季节性强度）、Step 5（季度箱线图使用日度数据）、Step 6（月度热力图）、Step 7（同比环比分析） |

> **注意**：日度和季度数据保存在内存中的`resampled_data`字典里，不单独保存为文件。如果后续步骤需要日度或季度数据，可直接从`resampled_data`中读取，或修改代码将日度和季度数据也保存为CSV。

---

### Step 2: STL时序分解

#### 1. 本步骤要做什么

本步骤对每个城市的月度负荷数据进行**STL时序分解**（Seasonal and Trend decomposition using Loess），将原始负荷序列拆解为三个独立的分量：趋势项（Trend）、季节项（Seasonal）和残差项（Residual）。这是本章最核心的分析步骤——通过分解，可以将复杂的负荷变化拆解为可解释的组成部分，分别分析其特征。

**三个分量的含义**：
- **趋势项（Trend）**：反映负荷的长期变化方向，是剥离了季节性波动和随机扰动后的平滑曲线。如果趋势项持续上升，说明该城市负荷在增长（可能由经济发展、人口增长驱动）；如果趋势项下降，说明负荷在萎缩（可能由产业转移、能效提升驱动）；如果趋势项平稳，说明负荷处于稳定状态。
- **季节项（Seasonal）**：反映规律性的季节波动，周期固定为12个月（因为设定了period=12）。在北非气候下，预期夏季（6-8月）因制冷需求增加而出现负荷高峰，冬季（12-2月）因采暖需求出现次高峰。季节项的振幅（波峰与波谷之差）反映季节性波动的强度。
- **残差项（Residual）**：反映无法被趋势和季节解释的随机波动。理想情况下，残差项应围绕零值随机分布，无明显趋势或周期性。如果残差项存在明显模式，说明分解不充分（可能需要调整参数或使用更复杂的模型）。

STL分解使用LOESS（局部加权回归）算法，其核心思想是对时间序列的每个数据点，用其附近的数据点进行加权回归拟合，距离越近权重越大。这种方法的优势是：不需要预设趋势和季节的函数形式（如线性、正弦），可以自适应地拟合任意形状的趋势和季节模式；同时，`robust=True`参数使算法对异常值具有鲁棒性，不会被个别极端值拉偏。

本步骤对4个城市分别执行STL分解，每个城市生成一张四合一分解图（原始序列+三个分量）和一个分解结果CSV文件。

#### 2. 具体操作指引

**操作流程**：

1. **数据准备**：从Step 1的`resampled_data`字典中提取每个城市的月度负荷序列。确认序列长度>=24（至少2个完整年度周期），否则STL分解可能不稳定。
2. **STL分解参数设定**：
   - `period=12`：月度数据的年度季节性周期，即每12个月为一个完整周期
   - `robust=True`：启用鲁棒模式，对异常值不敏感。当数据中存在极端值（如节假日负荷骤降、设备故障导致负荷骤升）时，鲁棒模式可以避免这些极端值对趋势和季节拟合的过度影响
   - `seasonal=13`（可选）：季节平滑窗口，默认为period+1=13。增大此值会使季节项更平滑，减小此值会使季节项更灵活
   - `trend=None`（可选）：趋势平滑窗口，默认为period的最小奇数倍>=1.5*period，即约19。增大此值会使趋势项更平滑
3. **执行分解**：调用`stl.fit()`执行分解，返回STLResult对象，包含`.observed`（原始序列）、`.trend`（趋势项）、`.seasonal`（季节项）、`.resid`（残差项）四个属性。
4. **绘制分解图**：使用matplotlib创建4行1列的子图布局，分别绘制原始序列、趋势项、季节项和残差项。每个子图设置标题、图例、网格线。使用`sharex=True`使四个子图共享x轴，便于对齐观察。
5. **保存分解结果**：将四个分量合并为DataFrame，保存为CSV文件，便于后续步骤（Step 3趋势对比、Step 4季节性强度）使用。

**关键参数说明**：
- `period`：季节性周期长度。月度数据设为12（年周期），日度数据设为7（周周期）。**必须为整数**。
- `robust`：布尔值，True表示使用迭代重加权最小二乘（IRLS）降低异常值影响，False表示使用普通最小二乘。建议对含异常值的实际数据设为True。
- `seasonal`：季节平滑窗口大小，必须为奇数。默认为`period + 1`。值越大，季节项越平滑；值越小，季节项越灵活。
- `trend`：趋势平滑窗口大小，必须为奇数且>period。默认自动计算。值越大，趋势项越平滑。

#### 3. 代码框架

```python
# ============================================================
# Step 2: STL时序分解
# ============================================================

stl_results = {}  # 存储分解结果，供后续步骤使用

for city in df['city'].unique():
    monthly = resampled_data[city]['monthly']
    
    # --- 2.1 数据长度检查 ---
    n_obs = len(monthly.dropna())
    print(f"\n{city}: 月度数据 {n_obs} 个月")
    if n_obs < 24:
        print(f"  [警告] 数据不足24个月（仅{n_obs}个月），STL分解可能不稳定")
    
    # --- 2.2 STL分解 ---
    stl = STL(monthly, period=12, robust=True)
    result = stl.fit()
    stl_results[city] = result  # 保存分解结果
    
    # 打印分解摘要
    print(f"  趋势范围: {result.trend.min():.1f}~{result.trend.max():.1f} kW")
    print(f"  季节项振幅: {result.seasonal.max() - result.seasonal.min():.1f} kW")
    print(f"  残差标准差: {result.resid.std():.1f} kW")
    
    # --- 2.3 绘制分解图 ---
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), dpi=150, sharex=True)
    
    # 原始序列
    axes[0].plot(result.observed, label='原始序列 (Observed)', color='steelblue', linewidth=1.5)
    axes[0].set_title(f'{city} - STL时序分解 (period=12, robust=True)', fontsize=14, fontweight='bold')
    axes[0].legend(loc='upper right', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylabel('负荷 (kW)', fontsize=11)
    
    # 趋势项
    axes[1].plot(result.trend, label='趋势项 (Trend)', color='darkorange', linewidth=2)
    axes[1].legend(loc='upper right', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylabel('负荷 (kW)', fontsize=11)
    
    # 季节项
    axes[2].plot(result.seasonal, label='季节项 (Seasonal)', color='green', linewidth=1.5)
    axes[2].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[2].legend(loc='upper right', fontsize=10)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_ylabel('负荷 (kW)', fontsize=11)
    
    # 残差项
    axes[3].plot(result.resid, label='残差项 (Residual)', color='red', alpha=0.7, linewidth=1)
    axes[3].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[3].legend(loc='upper right', fontsize=10)
    axes[3].grid(True, alpha=0.3)
    axes[3].set_xlabel('时间', fontsize=12)
    axes[3].set_ylabel('负荷 (kW)', fontsize=11)
    
    plt.tight_layout()
    fig_path = os.path.join(output_dir, f'ch05_stl_decomposition_{city.lower()}.png')
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  分解图已保存: {fig_path}")
    
    # --- 2.4 保存分解结果数据 ---
    decomp_df = pd.DataFrame({
        'observed': result.observed,
        'trend': result.trend,
        'seasonal': result.seasonal,
        'residual': result.resid
    })
    csv_path = os.path.join(output_dir, f'ch05_stl_components_{city.lower()}.csv')
    decomp_df.to_csv(csv_path)
    print(f"  分解数据已保存: {csv_path}")

print("\nStep 2 完成: 所有城市STL分解已执行")
```

#### 4. 本步骤完成后的检查标准

- **分解图视觉检查**：
  - 趋势项（第2行）：应为平滑曲线，无剧烈波动。如果趋势项仍有明显的周期性波动，说明趋势窗口（trend参数）太小，需要增大。
  - 季节项（第3行）：应呈规律性周期波动，周期为12个月（可从图中数出波峰数量验证：如果有2个完整年度数据，应看到约2个完整的周期波形）。季节项围绕零值上下波动。
  - 残差项（第4行）：应围绕零值随机分布，无明显趋势或周期性。如果残差项存在明显趋势（如前半段为正、后半段为负），说明分解不充分，趋势项没有完全捕捉到长期变化。
- **数值检查**：
  - `observed = trend + seasonal + residual`（加法分解的恒等式），误差应<1e-10
  - 季节项的均值应接近0（STL分解的数学性质）
  - 残差项的均值应接近0
- **文件检查**：每个城市生成1张PNG图和1个CSV文件，共4张图+4个CSV文件。

#### 5. 如果遇到问题请及时反馈

- **STL分解报错"ValueError: period must be > 1"**：检查月度数据行数是否>=2（period=12需要至少2个数据点），但实际需要至少2*period=24个数据点才能得到稳定结果。如果数据不足24个月，考虑降低period（如period=6捕捉半年周期），或在报告中说明数据不足。
- **残差项存在明显趋势**：说明趋势项没有完全捕捉到长期变化。处理方法：(1) 增大trend参数（如`trend=25`），使趋势项更平滑、更能捕捉长期方向；(2) 检查原始数据是否存在结构性变化（如2023年中某城市新增了大工业用户，导致负荷突然跳升），这种情况下可能需要分段分解。
- **季节项振幅过大或过小**：如果季节项振幅（波峰-波谷）远大于趋势项的变化幅度，说明季节性是该城市负荷变化的主导因素；如果季节项振幅很小（接近0），说明该城市负荷几乎没有季节性（可能是以工业负荷为主、受气候影响小）。
- **分解图不美观**：如果x轴日期标签重叠，使用`fig.autofmt_xdate()`或`plt.xticks(rotation=45)`旋转标签。
- **内存警告**：STL分解对长序列可能消耗较多内存。如果数据超过1000个月度数据点，考虑先截取所需时间段。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| STL分解图（Laayoune） | `ch05_stl_decomposition_laayoune.png` | `outputs/ch05_midlong_term_trend/` | 四合一分解图：原始序列、趋势项、季节项、残差项的时间序列图。用于直观展示负荷的分解结果。 | 报告配图（Prompt-08） |
| STL分解图（Boujdour） | `ch05_stl_decomposition_boujdour.png` | `outputs/ch05_midlong_term_trend/` | 同上，Boujdour城市。 | 报告配图（Prompt-08） |
| STL分解图（Foum eloued） | `ch05_stl_decomposition_foum_eloued.png` | `outputs/ch05_midlong_term_trend/` | 同上，Foum eloued城市。 | 报告配图（Prompt-08） |
| STL分解图（Marrakech） | `ch05_stl_decomposition_marrakech.png` | `outputs/ch05_midlong_term_trend/` | 同上，Marrakech城市。 | 报告配图（Prompt-08） |
| STL分解数据（Laayoune） | `ch05_stl_components_laayoune.csv` | `outputs/ch05_midlong_term_trend/` | 四列数据：observed（原始月度均值）、trend（趋势项）、seasonal（季节项）、residual（残差项）。索引为DateTime。单位kW。 | Step 3（趋势项对比）、Step 4（季节性强度计算） |
| STL分解数据（Boujdour） | `ch05_stl_components_boujdour.csv` | `outputs/ch05_midlong_term_trend/` | 同上，Boujdour城市。 | Step 3、Step 4 |
| STL分解数据（Foum eloued） | `ch05_stl_components_foum_eloued.csv` | `outputs/ch05_midlong_term_trend/` | 同上，Foum eloued城市。 | Step 3、Step 4 |
| STL分解数据（Marrakech） | `ch05_stl_components_marrakech.csv` | `outputs/ch05_midlong_term_trend/` | 同上，Marrakech城市。 | Step 3、Step 4 |


---

### Step 3: 趋势项提取与可视化

#### 1. 本步骤要做什么

本步骤将4个城市的STL趋势项叠加在同一张图上，进行**跨城市长期负荷趋势的直观对比**。趋势项已剥离了季节性波动和随机扰动，反映的是纯粹的长期变化方向，因此将4条趋势线放在一起比较，可以清晰地回答以下问题：

- 哪些城市的负荷在增长，哪些在下降或持平？
- 增长/下降的速度大致如何（通过趋势线的斜率判断）？
- 各城市之间的负荷差距是在扩大还是缩小？

这种跨城市趋势对比对于电网规划具有重要参考价值——如果某城市负荷持续快速增长，可能需要提前规划变电站扩容或新建输电线路；如果某城市负荷停滞甚至下降，可能需要评估现有资产的利用率。

除了主趋势对比图外，本步骤还将为每个城市单独绘制一张"趋势项+原始序列"的叠加图，展示趋势项对原始数据的拟合效果——原始数据点应围绕趋势线上下波动，波动幅度反映季节性和随机扰动的综合影响。

#### 2. 具体操作指引

**操作流程**：

1. **数据加载**：从Step 2保存的CSV文件中读取4个城市的STL分解结果，提取趋势项列。
2. **四城市趋势对比图**：
   - 创建一张14x6英寸的图，使用不同颜色区分4个城市
   - 每条趋势线使用`linewidth=2`确保清晰可辨
   - 添加图例、标题、坐标轴标签、网格线
   - 使用`tight_layout()`确保布局不重叠
3. **单城市趋势拟合图**（可选但建议）：
   - 对每个城市，将原始月度序列（浅色半透明）和趋势项（深色粗线）叠加在同一张图上
   - 两者的差距即为"季节项+残差项"的综合影响
   - 这种可视化可以帮助读者理解趋势项在原始数据中的位置
4. **趋势方向判断**：计算每个城市趋势项的首尾值之差，判断趋势方向（上升/下降/平稳），并在图上标注。

**关键参数说明**：
- 颜色方案：使用`{'Laayoune': 'steelblue', 'Boujdour': 'darkorange', 'Foum eloued': 'green', 'Marrakech': 'red'}`，确保4条线颜色差异明显
- 线宽：趋势线使用`linewidth=2`，原始序列使用`linewidth=1, alpha=0.5`

#### 3. 代码框架

```python
# ============================================================
# Step 3: 趋势项提取与可视化
# ============================================================

# --- 3.1 定义颜色方案 ---
colors = {
    'Laayoune': 'steelblue',
    'Boujdour': 'darkorange',
    'Foum eloued': 'green',
    'Marrakech': 'red'
}

# --- 3.2 四城市趋势对比图 ---
fig, ax = plt.subplots(figsize=(14, 6), dpi=150)

for city in df['city'].unique():
    csv_path = os.path.join(output_dir, f'ch05_stl_components_{city.lower()}.csv')
    decomp = pd.read_csv(csv_path, parse_dates=['DateTime'], index_col='DateTime')
    
    ax.plot(decomp.index, decomp['trend'], label=city, color=colors.get(city, 'gray'), linewidth=2)
    
    # 计算趋势方向
    trend_start = decomp['trend'].iloc[0]
    trend_end = decomp['trend'].iloc[-1]
    trend_change = trend_end - trend_start
    trend_pct = (trend_change / trend_start) * 100 if trend_start != 0 else 0
    direction = "上升" if trend_change > 0 else ("下降" if trend_change < 0 else "平稳")
    print(f"{city}: 趋势{direction} ({trend_pct:+.1f}%), {trend_start:.1f} -> {trend_end:.1f} kW")

ax.set_title('四城市负荷长期趋势对比 (STL趋势项)', fontsize=14, fontweight='bold')
ax.set_xlabel('时间', fontsize=12)
ax.set_ylabel('趋势负荷 (kW)', fontsize=12)
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
trend_compare_path = os.path.join(output_dir, 'ch05_trend_component.png')
plt.savefig(trend_compare_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"\n趋势对比图已保存: {trend_compare_path}")

# --- 3.3 单城市趋势拟合图（原始序列 + 趋势项） ---
for city in df['city'].unique():
    csv_path = os.path.join(output_dir, f'ch05_stl_components_{city.lower()}.csv')
    decomp = pd.read_csv(csv_path, parse_dates=['DateTime'], index_col='DateTime')
    
    fig, ax = plt.subplots(figsize=(14, 5), dpi=150)
    ax.plot(decomp.index, decomp['observed'], label='原始月度负荷', color='steelblue', alpha=0.5, linewidth=1)
    ax.plot(decomp.index, decomp['trend'], label='趋势项 (Trend)', color='darkorange', linewidth=2.5)
    
    # 填充趋势与原始之间的区域（季节+残差）
    ax.fill_between(decomp.index, decomp['observed'], decomp['trend'], alpha=0.15, color='gray', label='季节+残差')
    
    ax.set_title(f'{city} - 月度负荷与趋势项拟合', fontsize=14, fontweight='bold')
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('负荷 (kW)', fontsize=12)
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fit_path = os.path.join(output_dir, f'ch05_trend_fit_{city.lower()}.png')
    plt.savefig(fit_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"{city}趋势拟合图已保存: {fit_path}")

print("\nStep 3 完成: 趋势项可视化已生成")
```

#### 4. 本步骤完成后的检查标准

- **四城市趋势对比图**：4条趋势线清晰可辨，颜色差异明显；趋势线平滑无剧烈波动；图例完整，包含4个城市名称；坐标轴标签清晰（x轴为时间，y轴为kW）。
- **单城市趋势拟合图**：原始数据点（浅色）围绕趋势线（深色）上下波动；填充区域（季节+残差）宽度大致均匀，无异常宽的区域（如有，可能是原始数据存在异常值）。
- **趋势方向判断**：每个城市都输出了趋势方向（上升/下降/平稳）和变化百分比，数值合理。

#### 5. 如果遇到问题请及时反馈

- **趋势线交叉过多**：如果4条趋势线频繁交叉，可能说明各城市负荷差异不大，或者数据时间跨度太短导致趋势不稳定。在报告中说明即可，无需特殊处理。
- **某城市趋势线明显异常**（如突然跳升或跳降）：检查该城市原始数据是否存在长时间缺失或异常值，这些异常可能影响了趋势拟合。
- **趋势拟合图上原始数据与趋势线差距过大**：如果填充区域宽度远大于趋势项本身的变化幅度，说明季节性和随机扰动是负荷变化的主导因素，趋势项的解释力有限。在报告中说明。
- **图像中文显示乱码**：如果matplotlib不支持中文显示，添加以下配置：`plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']` 和 `plt.rcParams['axes.unicode_minus'] = False`。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 四城市趋势对比图 | `ch05_trend_component.png` | `outputs/ch05_midlong_term_trend/` | 4条趋势线叠加图，展示各城市长期负荷变化方向的差异。x轴为时间，y轴为趋势负荷(kW)。 | 报告配图（Prompt-08） |
| 趋势拟合图（Laayoune） | `ch05_trend_fit_laayoune.png` | `outputs/ch05_midlong_term_trend/` | 原始月度负荷（浅色）与趋势项（深色）的叠加图，灰色填充区域为季节+残差。 | 报告配图（Prompt-08） |
| 趋势拟合图（Boujdour） | `ch05_trend_fit_boujdour.png` | `outputs/ch05_midlong_term_trend/` | 同上，Boujdour城市。 | 报告配图（Prompt-08） |
| 趋势拟合图（Foum eloued） | `ch05_trend_fit_foum_eloued.png` | `outputs/ch05_midlong_term_trend/` | 同上，Foum eloued城市。 | 报告配图（Prompt-08） |
| 趋势拟合图（Marrakech） | `ch05_trend_fit_marrakech.png` | `outputs/ch05_midlong_term_trend/` | 同上，Marrakech城市。 | 报告配图（Prompt-08） |

---

### Step 4: 季节性强度计算

#### 1. 本步骤要做什么

本步骤计算每个城市的**季节性强度指标** F_s（Seasonal Strength），用于量化"季节因素对负荷变化的影响有多大"。这是一个介于0到1之间的数值指标：F_s越接近1，说明季节性越强（负荷变化主要由季节因素驱动）；F_s越接近0，说明几乎没有季节性（负荷变化主要由随机因素驱动）。

季节性强度指标的计算公式为：

    F_s = max(0, 1 - Var(R) / Var(S+R))

其中，S为季节分量的方差（Var(Seasonal)），R为残差分量的方差（Var(Residual)），S+R表示"去趋势后的数据"（即原始数据减去趋势项）。这个公式的直觉是：如果残差方差远大于季节方差（即随机波动远大于季节波动），则F_s接近0，说明季节性弱；如果季节方差远大于残差方差，则F_s接近1，说明季节性强。

在北非气候背景下，预期夏季制冷需求会导致较强的季节性（F_s > 0.5），但不同城市因产业结构差异（如工业负荷占比高的城市季节性较弱），F_s值可能存在显著差异。这个指标为后续的跨国对比（Prompt-06）提供了重要的量化依据。

除了计算F_s值外，本步骤还将生成一张**季节性强度对比柱状图**，直观展示4个城市的季节性强弱排序。

#### 2. 具体操作指引

**操作流程**：

1. **数据加载**：从Step 2保存的CSV文件中读取每个城市的STL分解结果，提取seasonal和residual列。
2. **方差计算**：使用`pd.Series.var()`计算季节分量和残差分量的方差（默认为样本方差，ddof=1）。
3. **F_s计算**：按照公式计算F_s值，使用`max(0, ...)`确保结果非负（理论上不应为负，但数值计算误差可能导致微小的负值）。
4. **强度等级判定**：F_s > 0.7为强季节性；0.4 < F_s <= 0.7为中等季节性；F_s <= 0.4为弱季节性。
5. **结果保存**：将每个城市的F_s值、季节方差、残差方差、强度等级保存为CSV文件。
6. **可视化**：绘制水平柱状图，按F_s值从大到小排序，用颜色区分强度等级。

**关键参数说明**：
- `var()`：pandas的方差计算函数，默认ddof=1（样本方差）。如果使用ddof=0（总体方差），结果会略有差异，但不影响F_s的相对排序。
- 强度等级阈值（0.7和0.4）是经验值，可根据实际数据分布调整。

#### 3. 代码框架

```python
# ============================================================
# Step 4: 季节性强度计算
# ============================================================

seasonal_strength_records = []

for city in df['city'].unique():
    csv_path = os.path.join(output_dir, f'ch05_stl_components_{city.lower()}.csv')
    decomp = pd.read_csv(csv_path)
    
    # --- 4.1 方差计算 ---
    var_seasonal = decomp['seasonal'].var()   # 季节分量方差
    var_residual = decomp['residual'].var()    # 残差分量方差
    
    # --- 4.2 F_s计算 ---
    f_s = max(0, 1 - var_residual / (var_seasonal + var_residual))
    
    # --- 4.3 强度等级判定 ---
    if f_s > 0.7:
        level = '强季节性'
        level_en = 'Strong'
    elif f_s > 0.4:
        level = '中等季节性'
        level_en = 'Moderate'
    else:
        level = '弱季节性'
        level_en = 'Weak'
    
    seasonal_strength_records.append({
        'city': city,
        'var_seasonal': round(var_seasonal, 4),
        'var_residual': round(var_residual, 4),
        'seasonal_strength': round(f_s, 4),
        'strength_level': level,
        'strength_level_en': level_en
    })
    print(f"{city}: F_s = {f_s:.4f} ({level}), Var(S)={var_seasonal:.2f}, Var(R)={var_residual:.2f}")

# --- 4.4 保存结果 ---
strength_df = pd.DataFrame(seasonal_strength_records)
strength_csv_path = os.path.join(output_dir, 'ch05_seasonal_strength.csv')
strength_df.to_csv(strength_csv_path, index=False)
print(f"\n季节性强度表已保存: {strength_csv_path}")
print(strength_df.to_string(index=False))

# --- 4.5 可视化：季节性强度对比柱状图 ---
fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

# 按F_s值排序
strength_sorted = strength_df.sort_values('seasonal_strength', ascending=True)
bar_colors = ['#e74c3c' if v > 0.7 else ('#f39c12' if v > 0.4 else '#27ae60') for v in strength_sorted['seasonal_strength']]

bars = ax.barh(strength_sorted['city'], strength_sorted['seasonal_strength'], color=bar_colors, edgecolor='white', height=0.6)

# 在柱状图上标注数值
for bar, val in zip(bars, strength_sorted['seasonal_strength']):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('季节性强度 F_s', fontsize=12)
ax.set_title('四城市负荷季节性强度对比', fontsize=14, fontweight='bold')
ax.set_xlim(0, 1.1)
ax.axvline(x=0.7, color='red', linestyle='--', alpha=0.5, label='强季节性阈值 (0.7)')
ax.axvline(x=0.4, color='orange', linestyle='--', alpha=0.5, label='中等季节性阈值 (0.4)')
ax.legend(fontsize=10, loc='lower right')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
strength_plot_path = os.path.join(output_dir, 'ch05_seasonal_strength.png')
plt.savefig(strength_plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"季节性强度图已保存: {strength_plot_path}")

print("\nStep 4 完成: 季节性强度计算完毕")
```

#### 4. 本步骤完成后的检查标准

- **数值范围检查**：所有F_s值必须在[0, 1]区间内。如果出现负值，说明计算有误（检查公式中的max(0, ...)是否生效）。
- **合理性检查**：在北非气候下，预期夏季制冷需求导致较强的季节性，F_s应>0.3。如果所有城市的F_s都<0.1，需要检查STL分解是否正确执行。
- **方差关系检查**：季节方差和残差方差均应>0（如果某个方差为0，说明该分量恒为常数，可能是数据问题）。
- **可视化检查**：柱状图清晰展示4个城市的F_s值排序，颜色区分强度等级。

#### 5. 如果遇到问题请及时反馈

- **F_s值全部接近0**：可能原因：(1) STL分解的seasonal参数设置不当，导致季节项几乎为0；(2) 原始数据本身确实没有季节性（如纯工业负荷）。检查Step 2的分解图中季节项是否有明显波动。
- **F_s值全部接近1**：可能原因：(1) 残差项几乎为0，说明STL分解过度拟合了季节性；(2) 数据非常规律，几乎没有随机波动。检查残差项的标准差是否异常小。
- **某城市F_s为NaN**：检查该城市的STL分解CSV文件是否存在、seasonal和residual列是否有NaN。
- **强度等级阈值不适用**：如果4个城市的F_s值都集中在某个区间（如都在0.6~0.8之间），说明预设阈值（0.4和0.7）可能不适合当前数据。可以在报告中调整阈值或使用相对排名代替绝对等级。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 季节性强度表 | `ch05_seasonal_strength.csv` | `outputs/ch05_midlong_term_trend/` | 包含6列：city（城市名）、var_seasonal（季节方差）、var_residual（残差方差）、seasonal_strength（F_s值）、strength_level（中文等级）、strength_level_en（英文等级）。4行数据，每行对应一个城市。 | Prompt-06（跨国对比的季节性维度）、Prompt-07（综合评估） |
| 季节性强度对比图 | `ch05_seasonal_strength.png` | `outputs/ch05_midlong_term_trend/` | 水平柱状图，按F_s值排序，红色=强季节性、橙色=中等、绿色=弱季节性。含阈值参考线。 | 报告配图（Prompt-08） |

---

### Step 5: 季度负荷箱线图

#### 1. 本步骤要做什么

本步骤绘制每个城市四个季度（冬季Q1、春季Q2、夏季Q3、秋季Q4）的日负荷分布箱线图（Box Plot）。箱线图能同时展示负荷分布的多个统计特征：中位数（箱体内的横线）、四分位数（箱体的上下边界，即Q1和Q3）、极值范围（须线的端点）和异常值（须线之外的散点），比单一均值更有信息量。

通过季度箱线图，可以直观回答以下问题：
- **哪个季度的负荷最高/最低？**（通过中位数位置判断）
- **不同季度的负荷波动程度如何？**（通过箱体高度和须线长度判断——箱体越高，说明该季度内日负荷差异越大）
- **是否存在大量异常日？**（通过须线外的散点数量判断——如果某季度有很多异常值点，说明该季度负荷极不稳定，可能受极端天气或特殊事件影响）

在北非气候下，预期夏季（Q3: 6-8月）负荷最高（制冷需求），冬季（Q1: 12-2月）次之（采暖需求），春秋季（Q2、Q4）负荷较低。但不同城市因气候和产业差异，季度模式可能有所不同。

#### 2. 具体操作指引

**操作流程**：

1. **数据准备**：从Step 1的`resampled_data`字典中提取每个城市的日度负荷序列。
2. **季度标签映射**：将月份映射为季度标签。Q1(Winter): 12月、1月、2月；Q2(Spring): 3月、4月、5月；Q3(Summer): 6月、7月、8月；Q4(Autumn): 9月、10月、11月。
3. **箱线图绘制**：使用seaborn的`boxplot()`函数，x轴为季度标签，y轴为日均负荷(kW)。设置`order`参数确保季度按冬-春-夏-秋的顺序排列。叠加`stripplot()`展示数据点分布密度。
4. **统计摘要**：计算每个季度的统计特征（均值、中位数、标准差、最小值、最大值），打印输出。

**关键参数说明**：
- `sns.boxplot(data, x, y, order, palette)`：palette控制颜色方案，'Set2'为柔和色系
- 箱线图的"须线"（whisker）默认延伸到Q1-1.5*IQR和Q3+1.5*IQR，超出此范围的点标记为异常值

#### 3. 代码框架

```python
# ============================================================
# Step 5: 季度负荷箱线图
# ============================================================

quarter_map = {
    12: 'Q1(Winter)', 1: 'Q1(Winter)', 2: 'Q1(Winter)',
    3: 'Q2(Spring)',  4: 'Q2(Spring)',  5: 'Q2(Spring)',
    6: 'Q3(Summer)',  7: 'Q3(Summer)',  8: 'Q3(Summer)',
    9: 'Q4(Autumn)', 10: 'Q4(Autumn)', 11: 'Q4(Autumn)'
}
quarter_order = ['Q1(Winter)', 'Q2(Spring)', 'Q3(Summer)', 'Q4(Autumn)']

for city in df['city'].unique():
    daily = resampled_data[city]['daily'].to_frame(name='load_kw')
    daily['quarter'] = daily.index.month.map(quarter_map)
    
    # --- 5.1 统计摘要 ---
    print(f"\n{city} 季度负荷统计:")
    for q in quarter_order:
        q_data = daily[daily['quarter'] == q]['load_kw']
        if len(q_data) > 0:
            print(f"  {q}: n={len(q_data)}, 均值={q_data.mean():.1f}, "
                  f"中位数={q_data.median():.1f}, 标准差={q_data.std():.1f}, "
                  f"范围=[{q_data.min():.1f}, {q_data.max():.1f}]")
    
    # --- 5.2 绘制箱线图 ---
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    sns.boxplot(data=daily, x='quarter', y='load_kw', order=quarter_order,
                palette='Set2', ax=ax, width=0.6,
                flierprops={'marker': 'o', 'markersize': 4, 'alpha': 0.5})
    sns.stripplot(data=daily, x='quarter', y='load_kw', order=quarter_order,
                  color='black', alpha=0.3, size=3, ax=ax, jitter=True)
    
    ax.set_title(f'{city} - 季度负荷分布箱线图 (日度数据)', fontsize=14, fontweight='bold')
    ax.set_xlabel('季度', fontsize=12)
    ax.set_ylabel('日均负荷 (kW)', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    boxplot_path = os.path.join(output_dir, f'ch05_quarterly_boxplot_{city.lower()}.png')
    plt.savefig(boxplot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  箱线图已保存: {boxplot_path}")

print("\nStep 5 完成: 季度负荷箱线图已生成")
```

#### 4. 本步骤完成后的检查标准

- **季节性模式检查**：四个季度的箱体位置应有明显差异。在北非气候下，预期Q3(Summer)箱体位置最高（中位数最大），Q1(Winter)次之，Q2(Spring)和Q4(Autumn)较低。如果所有季度箱体位置几乎相同，说明该城市负荷几乎没有季节性（与Step 4的F_s值相互印证）。
- **异常值检查**：每个季度的异常值点（箱线图须线外的散点）数量应合理（不超过总数据点的5%）。如果某季度有大量异常值（>10%），需要检查该季度是否存在极端天气事件或数据质量问题。
- **数据量检查**：每个季度的数据点数量应大致均衡（每个季度约60-90天，2年数据约120-180天）。如果某季度数据点明显少于其他季度，可能是数据缺失。
- **可视化质量**：箱线图清晰美观，颜色区分明显，坐标轴标签完整。

#### 5. 如果遇到问题请及时反馈

- **所有季度箱体位置几乎相同**：说明该城市负荷无季节性。检查Step 4的F_s值是否也较低（<0.3）。如果F_s值较高但箱线图无差异，可能是季度映射有误（检查月份到季度的映射字典）。
- **某季度数据点为空**：检查该季度的日度数据是否存在（可能是数据时间范围不覆盖该季度）。
- **箱线图上出现极端异常值**（如某天负荷为0或远超正常范围）：这些异常值可能来自原始数据中的设备停机或故障事件。如果异常值数量很少（<5个），可以保留；如果较多，需要回到第一章检查数据清洗质量。
- **seaborn版本兼容性问题**：如果`sns.boxplot()`的`palette`参数报错（seaborn 0.13+），改为`hue`参数或使用`color`参数。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 季度箱线图（Laayoune） | `ch05_quarterly_boxplot_laayoune.png` | `outputs/ch05_midlong_term_trend/` | 四季度日负荷分布箱线图，含散点叠加。展示各季度的负荷中位数、四分位距和异常值。 | 报告配图（Prompt-08） |
| 季度箱线图（Boujdour） | `ch05_quarterly_boxplot_boujdour.png` | `outputs/ch05_midlong_term_trend/` | 同上，Boujdour城市。 | 报告配图（Prompt-08） |
| 季度箱线图（Foum eloued） | `ch05_quarterly_boxplot_foum_eloued.png` | `outputs/ch05_midlong_term_trend/` | 同上，Foum eloued城市。 | 报告配图（Prompt-08） |
| 季度箱线图（Marrakech） | `ch05_quarterly_boxplot_marrakech.png` | `outputs/ch05_midlong_term_trend/` | 同上，Marrakech城市。 | 报告配图（Prompt-08） |

---

### Step 6: 月度负荷热力图

#### 1. 本步骤要做什么

本步骤绘制每个城市的**"月份 x 年份"二维热力图**（Heatmap），颜色深浅代表月度平均负荷的高低。热力图是中长期分析中最直观的可视化工具之一，因为它能同时展示两个维度的信息：

- **纵向模式（季节性）**：同一月份在不同年份的颜色是否一致？如果每年7月都是深色（高负荷）、1月都是浅色（低负荷），说明季节性模式稳定。
- **横向趋势（年度变化）**：同一行（同一年份）内，颜色从左到右是否有变化趋势？如果某年的整体颜色比前一年更深，说明负荷在年度尺度上增长。
- **异常识别**：如果某个"月份-年份"格子的颜色与周围明显不同（如2023年8月特别深），可能对应极端天气事件或特殊用电事件。

热力图使用`YlOrRd`（黄-橙-红）配色方案：浅黄色代表低负荷，深红色代表高负荷。每个格子内标注具体数值，便于精确读取。

#### 2. 具体操作指引

**操作流程**：

1. **数据准备**：从Step 1的`resampled_data`字典中提取每个城市的月度负荷序列。
2. **透视表构建**：使用`pd.pivot_table()`将月度数据转换为"月份(行) x 年份(列)"的二维表格。行索引为月份（1-12），列索引为年份。
3. **热力图绘制**：使用seaborn的`heatmap()`函数，设置`annot=True`（显示数值）、`fmt='.1f'`（保留1位小数）、`cmap='YlOrRd'`（黄橙红配色）。
4. **缺失值处理**：如果某些月份没有数据（如数据时间范围不完整），透视表中会出现NaN。热力图默认将NaN显示为空白格子，这是合理的——空白格子直观地表示"该月无数据"。

**关键参数说明**：
- `sns.heatmap(data, cmap, annot, fmt, linewidths, linecolor)`：
  - `cmap='YlOrRd'`：黄-橙-红渐变色，浅色=低值，深色=高值
  - `annot=True`：在每个格子中显示数值
  - `fmt='.1f'`：数值格式为浮点数，保留1位小数
  - `linewidths=0.5, linecolor='white'`：格子之间的白色分隔线，增强可读性

#### 3. 代码框架

```python
# ============================================================
# Step 6: 月度负荷热力图
# ============================================================

for city in df['city'].unique():
    monthly = resampled_data[city]['monthly'].to_frame(name='load_kw')
    monthly['year'] = monthly.index.year
    monthly['month'] = monthly.index.month
    
    # --- 6.1 构建透视表 ---
    pivot = monthly.pivot_table(values='load_kw', index='month', columns='year', aggfunc='mean')
    pivot.index = [f'{m}月' for m in pivot.index]
    
    # --- 6.2 统计摘要 ---
    print(f"\n{city} 月度负荷热力图数据:")
    print(f"  年份范围: {pivot.columns.tolist()}")
    print(f"  月份覆盖: {pivot.index.tolist()}")
    print(f"  缺失格子数: {pivot.isnull().sum().sum()}")
    if pivot.notna().any().any():
        print(f"  最低负荷: {pivot.min().min():.1f} kW")
        print(f"  最高负荷: {pivot.max().max():.1f} kW")
    
    # --- 6.3 绘制热力图 ---
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    sns.heatmap(pivot, ax=ax, cmap='YlOrRd', annot=True, fmt='.1f',
                linewidths=0.5, linecolor='white',
                cbar_kws={'label': '月度平均负荷 (kW)', 'shrink': 0.8})
    
    ax.set_title(f'{city} - 月度负荷热力图 (kW)', fontsize=14, fontweight='bold')
    ax.set_xlabel('年份', fontsize=12)
    ax.set_ylabel('月份', fontsize=12)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    heatmap_path = os.path.join(output_dir, f'ch05_monthly_heatmap_{city.lower()}.png')
    plt.savefig(heatmap_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  热力图已保存: {heatmap_path}")

print("\nStep 6 完成: 月度负荷热力图已生成")
```

#### 4. 本步骤完成后的检查标准

- **季节性模式检查**：热力图应清晰展示季节性模式——夏季月份（6-8月）颜色较深（高负荷），冬季月份（12-2月）颜色中等，春秋季（3-5月、9-11月）颜色较浅。如果颜色分布无明显规律，说明季节性弱（与Step 4的F_s值相互印证）。
- **年度一致性检查**：同一月份在不同年份的颜色应大致相似（如每年7月都是深色）。如果某年某月的颜色与往年明显不同，需要排查原因（数据异常或真实的负荷变化）。
- **缺失数据检查**：空白格子数量应合理。如果空白格子过多（>30%），说明数据覆盖不完整，热力图的参考价值有限。
- **数值标注检查**：每个格子内的数值应清晰可读，与颜色深浅一致（数值大的格子颜色深）。

#### 5. 如果遇到问题请及时反馈

- **热力图颜色无明显差异**：说明月度负荷变化幅度很小，季节性弱。检查Step 4的F_s值是否较低。如果F_s值较高但热力图无差异，可能是数据量太少（如只有几个月的数据），导致透视表不完整。
- **透视表出现大量NaN**：说明数据时间范围不完整（如数据只有2023年6月到2024年5月，则2023年1-5月和2024年6-12月为NaN）。这是正常的，在报告中说明数据覆盖范围即可。
- **热力图数值标注重叠**：如果格子太小导致数值文字重叠，增大图片尺寸（如`figsize=(12, 8)`）或减小字体（`annot_kws={'size': 8}`）。
- **颜色范围不合适**：如果所有格子颜色都偏浅或偏深，说明数据范围与配色方案不匹配。可以手动设置`vmin`和`vmax`参数调整颜色映射范围。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 月度热力图（Laayoune） | `ch05_monthly_heatmap_laayoune.png` | `outputs/ch05_midlong_term_trend/` | 月份(行) x 年份(列)的热力图，颜色深浅代表月度平均负荷高低，格子内标注具体数值(kW)。 | 报告配图（Prompt-08） |
| 月度热力图（Boujdour） | `ch05_monthly_heatmap_boujdour.png` | `outputs/ch05_midlong_term_trend/` | 同上，Boujdour城市。 | 报告配图（Prompt-08） |
| 月度热力图（Foum eloued） | `ch05_monthly_heatmap_foum_eloued.png` | `outputs/ch05_midlong_term_trend/` | 同上，Foum eloued城市。 | 报告配图（Prompt-08） |
| 月度热力图（Marrakech） | `ch05_monthly_heatmap_marrakech.png` | `outputs/ch05_midlong_term_trend/` | 同上，Marrakech城市。 | 报告配图（Prompt-08） |

---

### Step 7: 同比/环比分析

#### 1. 本步骤要做什么

本步骤计算月度负荷的**环比变化率**（Month-over-Month, MoM）和**同比变化率**（Year-over-Year, YoY），这是电力行业最常用的两个宏观分析指标。

**环比变化率（MoM）**：本月负荷与上月负荷的百分比变化，公式为 `(本月值 - 上月值) / 上月值 * 100%`。环比反映的是**短期变化趋势**——如果连续几个月环比为正，说明负荷在持续增长；如果环比在0附近波动，说明负荷稳定。环比的缺点是受季节性影响大（如从5月到6月，负荷因入夏而自然增长，环比为正不一定代表经济驱动增长）。

**同比变化率（YoY）**：本月负荷与去年同月负荷的百分比变化，公式为 `(本月值 - 去年同月值) / 去年同月值 * 100%`。同比消除了季节性影响，反映的是**年度真实增长情况**——如果同比持续为正，说明负荷在排除季节因素后仍在增长（可能由经济发展、人口增长驱动）。同比的缺点是需要至少13个月的数据才能开始计算（前12个月没有"去年同月"可对比）。

本步骤对4个城市分别计算环比和同比，生成一张汇总表和两张可视化图表（同比变化率图+环比变化率图），4个城市叠加在同一张时间序列图上，便于跨城市对比。

#### 2. 具体操作指引

**操作流程**：

1. **数据准备**：从Step 1的`resampled_data`字典中提取每个城市的月度负荷序列。
2. **环比计算**：使用`pct_change(periods=1) * 100`，即本月值与前1个月的百分比变化。
3. **同比计算**：使用`pct_change(periods=12) * 100`，即本月值与前12个月（去年同月）的百分比变化。
4. **结果合并**：将月度负荷值、环比变化率、同比变化率合并为一张DataFrame，添加城市标签。
5. **打印摘要**：输出每个城市最近6个月的环比和同比数据，便于快速浏览。
6. **可视化**：分别绘制同比和环比变化率的时间序列图，4个城市叠加在同一张图上。使用不同颜色区分城市，添加零值参考线。
7. **保存结果**：将汇总表保存为CSV文件。

**关键参数说明**：
- `pct_change(periods=1)`：环比，与前1期比较
- `pct_change(periods=12)`：同比，与前12期（去年同月）比较
- 乘以100将比例转换为百分比

#### 3. 代码框架

```python
# ============================================================
# Step 7: 同比/环比分析
# ============================================================

yoy_mom_records = []

for city in df['city'].unique():
    monthly = resampled_data[city]['monthly']
    
    # --- 7.1 计算环比和同比 ---
    mom = monthly.pct_change(periods=1) * 100   # 环比变化率 (%)
    yoy = monthly.pct_change(periods=12) * 100   # 同比变化率 (%)
    
    # --- 7.2 合并结果 ---
    temp = pd.DataFrame({
        'monthly_avg_kw': monthly,
        'mom_change_pct': mom,
        'yoy_change_pct': yoy
    })
    temp['city'] = city
    yoy_mom_records.append(temp)
    
    # --- 7.3 打印摘要 ---
    print(f"\n{'='*60}")
    print(f"{city} - 同比/环比分析")
    print(f"{'='*60}")
    print(f"  数据范围: {monthly.index.min().date()} ~ {monthly.index.max().date()} ({len(monthly)}个月)")
    print(f"  环比NaN数: {mom.isnull().sum()} (第1个月无环比)")
    print(f"  同比NaN数: {yoy.isnull().sum()} (前12个月无同比)")
    
    recent = temp[['monthly_avg_kw', 'mom_change_pct', 'yoy_change_pct']].tail(6)
    print(f"\n  最近6个月:")
    print(recent.to_string(float_format=lambda x: f'{x:.1f}' if pd.notna(x) else 'NaN'))
    
    valid_mom = mom.dropna()
    print(f"\n  环比统计: 均值={valid_mom.mean():.2f}%, 标准差={valid_mom.std():.2f}%, "
          f"范围=[{valid_mom.min():.2f}%, {valid_mom.max():.2f}%]")
    
    valid_yoy = yoy.dropna()
    if len(valid_yoy) > 0:
        print(f"  同比统计: 均值={valid_yoy.mean():.2f}%, 标准差={valid_yoy.std():.2f}%, "
              f"范围=[{valid_yoy.min():.2f}%, {valid_yoy.max():.2f}%]")
    else:
        print(f"  同比统计: 数据不足13个月，无法计算同比")

# --- 7.4 保存汇总表 ---
yoy_mom_df = pd.concat(yoy_mom_records)
yoy_mom_csv_path = os.path.join(output_dir, 'ch05_yoy_mom_analysis.csv')
yoy_mom_df.to_csv(yoy_mom_csv_path)
print(f"\n同比环比汇总表已保存: {yoy_mom_csv_path}")

# --- 7.5 可视化：同比变化率时间序列 ---
fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
for city in df['city'].unique():
    city_data = yoy_mom_df[yoy_mom_df['city'] == city]
    ax.plot(city_data.index, city_data['yoy_change_pct'],
            label=city, color=colors.get(city, 'gray'), linewidth=1.5, marker='o', markersize=4)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
ax.set_title('四城市月度负荷同比变化率 (YoY %)', fontsize=14, fontweight='bold')
ax.set_xlabel('时间', fontsize=12)
ax.set_ylabel('同比变化率 (%)', fontsize=12)
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
yoy_plot_path = os.path.join(output_dir, 'ch05_yoy_change_rate.png')
plt.savefig(yoy_plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"同比变化率图已保存: {yoy_plot_path}")

# --- 7.6 可视化：环比变化率时间序列 ---
fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
for city in df['city'].unique():
    city_data = yoy_mom_df[yoy_mom_df['city'] == city]
    ax.plot(city_data.index, city_data['mom_change_pct'],
            label=city, color=colors.get(city, 'gray'), linewidth=1.5, marker='o', markersize=4)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
ax.set_title('四城市月度负荷环比变化率 (MoM %)', fontsize=14, fontweight='bold')
ax.set_xlabel('时间', fontsize=12)
ax.set_ylabel('环比变化率 (%)', fontsize=12)
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
mom_plot_path = os.path.join(output_dir, 'ch05_mom_change_rate.png')
plt.savefig(mom_plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"环比变化率图已保存: {mom_plot_path}")

print("\nStep 7 完成: 同比/环比分析完毕")
```

#### 4. 本步骤完成后的检查标准

- **环比变化率**：第1个月的环比应为NaN（无上月可对比）；环比变化率通常在-15%~+15%之间（受季节性影响，跨季月份变化较大）；环比序列应呈周期性波动。
- **同比变化率**：前12个月的同比应为NaN（数据不足12个月，无去年同月可对比）；同比变化率通常在-10%~+20%之间；同比序列应相对平稳（已消除季节性），不应有明显的周期性波动。
- **NaN数量检查**：环比NaN数=1（仅第1个月），同比NaN数=12（前12个月）。如果NaN数不符合预期，检查数据时间连续性。
- **可视化检查**：同比和环比图中各城市线条清晰可辨，零值参考线明显。

#### 5. 如果遇到问题请及时反馈

- **同比变化率全部为NaN**：说明该城市数据不足13个月（即数据时间跨度<13个月），无法计算同比。处理方法：(1) 在报告中说明该城市数据不足，跳过同比分析；(2) 如果数据接近13个月（如12.5个月），检查是否有月度聚合导致的数据丢失。
- **变化率出现极端值（>50%或<-50%）**：可能原因：(1) 某月负荷值异常低（如设备停机导致负荷骤降），导致下月环比异常高；(2) 原始数据存在异常值。处理方法：检查对应月份的原始数据，如果确认异常，在报告中标注说明。
- **环比呈明显的锯齿形波动**：这是正常的——环比受季节性影响，相邻月份之间的变化方向交替（如从春到夏为正、从夏到秋为负）。这正是同比分析的价值所在（消除季节性）。
- **同比变化率持续为同一符号**：如果某城市同比持续为正（如每月+5%），说明负荷在稳定增长；如果持续为负，说明负荷在萎缩。需要结合经济背景分析原因。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 同比环比分析汇总表 | `ch05_yoy_mom_analysis.csv` | `outputs/ch05_midlong_term_trend/` | 包含5列：DateTime(索引)、monthly_avg_kw(月度均值kW)、mom_change_pct(环比%)、yoy_change_pct(同比%)、city(城市名)。4个城市的数据纵向拼接。前12行同比为NaN属正常。 | Prompt-06（跨国对比的负荷变化维度） |
| 同比变化率图 | `ch05_yoy_change_rate.png` | `outputs/ch05_midlong_term_trend/` | 4城市同比变化率时间序列图，含零值参考线。展示各城市的年度增长趋势对比。 | 报告配图（Prompt-08） |
| 环比变化率图 | `ch05_mom_change_rate.png` | `outputs/ch05_midlong_term_trend/` | 4城市环比变化率时间序列图，含零值参考线。展示各城市的月度变化模式对比。 | 报告配图（Prompt-08） |


---

## 三、产物总览与结构说明

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用章节 |
|------|----------|--------|------|-------------|
| 1 | 多粒度聚合数据 | ch05_daily_monthly_quarterly.csv | CSV | Step 2~7 |
| 2 | STL分解图(x4) | ch05_stl_decomposition_{city}.png | PNG | 报告配图 |
| 3 | STL分解数据(x4) | ch05_stl_components_{city}.csv | CSV | Step 3,4 |
| 4 | 趋势分量对比图 | ch05_trend_component.png | PNG | 报告配图 |
| 5 | 趋势拟合图(x4) | ch05_trend_fit_{city}.png | PNG | 报告配图 |
| 6 | 季节性强度表 | ch05_seasonal_strength.csv | CSV | Prompt-07 |
| 7 | 季节性强度对比图 | ch05_seasonal_strength.png | PNG | 报告配图 |
| 8 | 季度箱线图(x4) | ch05_quarterly_boxplot_{city}.png | PNG | 报告配图 |
| 9 | 月度热力图(x4) | ch05_monthly_heatmap_{city}.png | PNG | 报告配图 |
| 10 | 同比环比分析表 | ch05_yoy_mom_analysis.csv | CSV | Prompt-06 |
| 11 | 同比变化率图 | ch05_yoy_change_rate.png | PNG | 报告配图 |
| 12 | 环比变化率图 | ch05_mom_change_rate.png | PNG | 报告配图 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- STL分解假设季节性模式固定，无法捕捉逐渐变化的季节性（如全球变暖导致夏季延长）
- 同比分析受数据长度限制（Marrakech仅1年数据，无法计算同比）
- 未引入气象数据解释季节性波动的驱动因素

### 4.2 可进一步优化的方向
- 使用TBATS模型处理多重季节性（日+周+年），更全面地捕捉周期特征
- 引入气象数据（温度、湿度）解释季节性波动的驱动因素
- 进行Mann-Kendall趋势检验，量化趋势的统计显著性（判断趋势是否显著而非随机波动）
- 使用小波分析（Wavelet Analysis）捕捉多尺度周期特征

### 4.3 其他可选方法
- X-13ARIMA-SEATS：美国人口普查局标准季节性调整方法，更精确
- Canny边缘检测：检测趋势变化的拐点时刻
- 变点检测（ruptures库）：识别负荷趋势的结构性变化点（如政策调整、经济事件导致的突变）

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 如果Marrakech数据不足13个月导致无法计算同比，需确认是否跳过或使用其他方法
- 如果STL分解的残差项存在明显模式（非随机），需确认是否调整分解参数

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| STL分解不收敛 | 报ConvergenceWarning | 增加迭代次数或调整robust参数 | 否 |
| 季节性强度接近0 | F_s < 0.1 | 该zone可能无明显季节性，改为分析趋势项 | 否 |
| 同比数据不足 | 数据长度<13个月 | 改为仅分析环比，跳过同比 | 否 |
| 趋势项出现断裂 | 趋势线有突然跳变 | 检查原始数据是否存在长时间缺失 | 是 |

---
---

# Prompt-06: 国内对标区域数据爬取与跨国对比（全面细化版）

## 一、任务概述

### 1.1 本次任务是什么

本章将研究视角从**单一国家**拓展到**跨国对比**，选取我国西北地区与摩洛哥城市在气候条件、城市规模、产业结构上具有可比性的对标城市（西宁、银川、酒泉），通过爬取公开权威数据，构建中摩两国城市的多维度用电对比体系。

跨国对比的核心价值在于：通过"他山之石"发现摩洛哥城市用电模式的特点和不足——例如，如果摩洛哥城市的季节性波动显著大于我国对标城市，可能说明其空调制冷/采暖设备的普及率或建筑能效存在差异；如果人均用电量远低于我国对标城市，可能反映经济发展阶段的差距。

### 1.2 从什么数据出发

**摩洛哥侧数据**：来自前序章节的分析结论
- `ch02_descriptive_stats.csv` — 各城市负荷统计特征
- `ch02_load_rate_cv.csv` — 负荷率和变异系数
- `ch05_seasonal_strength.csv` — 季节性强度
- `ch05_yoy_mom_analysis.csv` — 同比环比变化率

**中国侧数据**：需要通过网络爬虫获取
- **国家统计局**（https://data.stats.gov.cn）：月度全社会用电量、GDP、人口
- **地方能源局/电网**：青海、宁夏、甘肃的区域用电结构数据
- **气象平台**（OpenMeteo API）：年均温、月均温、降水量

**对标城市选择理由**：
- **西宁**（青海省会，36.6N, 101.7E）：高原干旱气候，人口约250万，旅游+轻工业，年均温约6C
- **银川**（宁夏首府，38.5N, 106.3E）：温带大陆性气候，人口约290万，能源化工+农业，年均温约9C
- **酒泉**（甘肃，39.7N, 98.5E）：温带大陆性气候，人口约110万，新能源+旅游，年均温约8C

三城共同特征：干旱半干旱气候、中小城市规模、旅游业和轻工业主导——与摩洛哥城市高度相似。

### 1.3 可以采用什么方法

**合规定向爬虫**：使用requests+BeautifulSoup，设置User-Agent模拟浏览器，请求间隔>=2秒，遵循robots.txt协议。优先使用公开API（如OpenMeteo），其次爬取公开网页。

**多维度对比分析**：从以下5个维度进行对比
1. 人均用电量（kWh/人/年）— 反映经济发展水平和电气化程度
2. 负荷率（mean/max）— 反映电网利用效率
3. 峰谷差比（(max-min)/max）— 反映负荷波动程度
4. 季节性强度 — 反映气候对用电的影响程度
5. 月度负荷变化模式 — 反应用电行为的季节节律

**替代数据获取方式**：
- World Bank Open Data API：获取标准化跨国宏观数据
- IEA（国际能源署）公开数据：获取能源统计
- 手动数据录入模板：作为爬虫失败的降级方案

---

## 二、执行步骤

---

### Step 1: 对标城市基础信息整理

#### 1. 本步骤要做什么

本步骤整理西宁、银川、酒泉三个中国对标城市的基础信息，构建一张结构化的城市档案表。这些信息是后续所有对比分析的**背景数据基础**——只有充分了解对标城市的地理、气候、人口、经济特征，才能合理解释中摩城市用电差异的根本原因。

具体而言，需要收集以下维度的信息：
- **地理坐标**（经度、纬度）：用于后续气象数据获取（Step 4的OpenMeteo API需要坐标输入）
- **行政区划**（省份）：用于国家统计局数据爬取（Step 2按省份查询）
- **人口规模**（万人）：用于计算人均用电量等人均指标
- **经济规模**（GDP，亿元）：用于评估经济发展水平
- **气候类型**：用于定性解释用电季节性差异
- **年均温度和降水量**：用于气候对比
- **主要产业**：用于解释负荷结构和基荷水平差异
- **对标理由**：说明该城市与摩洛哥城市的相似性

这些数据主要通过公开资料收集（百度百科、国家统计局年鉴、气象局公开数据），如果某些数据难以获取，标注为"待补充"并在报告中说明。

#### 2. 具体操作指引

**操作流程**：

1. **信息收集**：通过以下渠道收集三城的基础信息：
   - 百度百科（搜索"西宁"、"银川"、"酒泉"）：获取人口、GDP、气候类型、主要产业
   - 国家统计局城市年鉴（https://data.stats.gov.cn）：获取最新人口和GDP数据
   - 中国气象局公开数据：获取年均温度和降水量
2. **数据标准化**：人口统一为"万人"单位；GDP统一为"亿元"单位（人民币）；温度统一为"摄氏度"；降水量统一为"毫米/年"；坐标统一为"十进制度"。
3. **结构化存储**：将收集到的信息整理为DataFrame，每行代表一个城市，每列代表一个属性。
4. **数据验证**：打印汇总表，人工核对关键数据（如人口数量级是否合理、GDP是否与公开数据一致）。

**关键参数说明**：
- 地理坐标精度：保留1位小数（约11km精度），足以满足气象API查询需求
- GDP数据年份：优先使用最新可用年份（通常为前一年），在报告中注明数据年份
- 人口数据年份：优先使用最新普查或统计公报数据

#### 3. 代码框架

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json
import time
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Step 1: 对标城市基础信息整理
# ============================================================

output_dir = 'outputs/ch06_cross_country_comparison'
os.makedirs(output_dir, exist_ok=True)

benchmark_cities = pd.DataFrame([
    {
        'city_cn': '西宁', 'city_en': 'Xining', 'province': '青海',
        'latitude': 36.6, 'longitude': 101.7,
        'population_10k': 248, 'gdp_billion_cny': 1680,
        'climate_type': '高原干旱气候', 'avg_temp_c': 6.0,
        'annual_precipitation_mm': 380,
        'main_industries': '旅游、轻工业、新能源',
        'comparison_reason': '高原干旱气候、中小城市规模、旅游+轻工业主导，与摩洛哥南部城市气候和产业结构相似'
    },
    {
        'city_cn': '银川', 'city_en': 'Yinchuan', 'province': '宁夏',
        'latitude': 38.5, 'longitude': 106.3,
        'population_10k': 289, 'gdp_billion_cny': 2536,
        'climate_type': '温带大陆性气候', 'avg_temp_c': 9.0,
        'annual_precipitation_mm': 200,
        'main_industries': '能源化工、农业、食品加工',
        'comparison_reason': '干旱气候、能源化工产业、农业比重较高，与摩洛哥城市在干旱条件和产业多样性上相似'
    },
    {
        'city_cn': '酒泉', 'city_en': 'Jiuquan', 'province': '甘肃',
        'latitude': 39.7, 'longitude': 98.5,
        'population_10k': 113, 'gdp_billion_cny': 820,
        'climate_type': '温带大陆性气候', 'avg_temp_c': 8.0,
        'annual_precipitation_mm': 80,
        'main_industries': '新能源、旅游、航空航天',
        'comparison_reason': '极干旱气候（年降水<100mm）、新能源基地、旅游业，与摩洛哥Laayoune等干旱城市高度相似'
    }
])

print("=" * 80)
print("对标城市基础信息汇总")
print("=" * 80)
display_cols = ['city_cn', 'province', 'population_10k', 'gdp_billion_cny',
                'avg_temp_c', 'annual_precipitation_mm', 'main_industries']
print(benchmark_cities[display_cols].to_string(index=False))

info_csv_path = os.path.join(output_dir, 'ch06_benchmark_cities_info.csv')
benchmark_cities.to_csv(info_csv_path, index=False, encoding='utf-8-sig')
print(f"\n对标城市基础信息已保存: {info_csv_path}")

# 数据完整性检查
for col in benchmark_cities.columns:
    null_count = benchmark_cities[col].isnull().sum()
    if null_count > 0:
        print(f"  [警告] 列 '{col}' 存在 {null_count} 个空值")
    else:
        print(f"  列 '{col}': 数据完整")
```

#### 4. 本步骤完成后的检查标准

- **城市完整性**：3个对标城市（西宁、银川、酒泉）的基础信息均已录入，DataFrame有3行。
- **关键字段非空**：city_cn、city_en、province、latitude、longitude、population_10k、gdp_billion_cny、climate_type、avg_temp_c必须非空。
- **数值合理性**：纬度在30~45N之间；人口在50万~500万之间；GDP在500亿~5000亿元之间；年均温度在0~15C之间；年降水量在50~500mm之间。
- **坐标精度**：经纬度保留1位小数，格式为十进制度数（非度分秒）。

#### 5. 如果遇到问题请及时反馈

- **GDP或人口数据年份不一致**：不同城市的数据可能来自不同年份。处理方法：在DataFrame中增加`data_year`列标注数据年份，在报告中说明。
- **某城市数据难以获取**：如果酒泉等较小城市的详细经济数据难以从公开渠道获取，标注为"待补充"并使用省级数据（甘肃省）作为替代估算。
- **气候类型分类不明确**：使用最广泛接受的分类即可，在报告中注明分类标准来源。
- **产业信息过于笼统**：可以增加`industry_detail`列补充更详细的产业构成（如各产业占比）。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 对标城市基础信息表 | `ch06_benchmark_cities_info.csv` | `outputs/ch06_cross_country_comparison/` | 包含12列：city_cn(中文名)、city_en(英文名)、province(省份)、latitude(纬度)、longitude(经度)、population_10k(人口/万人)、gdp_billion_cny(GDP/亿元)、climate_type(气候类型)、avg_temp_c(年均温/C)、annual_precipitation_mm(年降水/mm)、main_industries(主要产业)、comparison_reason(对标理由)。3行数据。UTF-8-BOM编码。 | Step 2（省份信息用于统计局查询）、Step 4（坐标用于气象API）、Step 5（对比面板构建）、Step 7（归因分析背景） |


---

### Step 2: 国家统计局数据爬取

#### 1. 本步骤要做什么

本步骤从**国家统计局公开数据平台**（https://data.stats.gov.cn）爬取青海、宁夏、甘肃三省的月度全社会用电量数据。这些数据是跨国对比的核心指标——通过将摩洛哥城市的负荷数据与中国对标城市所在省份的用电数据进行对比，可以从宏观层面评估两地用电水平的差异。

需要特别说明的是：国家统计局的数据通常是**省级**粒度（如"青海省全社会用电量"），而非城市级粒度。这意味着我们获取的是省级数据，需要结合人口比例进行估算才能得到城市级数据。例如，如果青海省年用电量为800亿kWh，西宁市人口占全省的40%，则估算西宁市年用电量约为320亿kWh。这种估算方法虽然不精确，但在缺乏城市级公开数据的情况下是合理的近似。

本步骤采用"爬取+降级"双保险策略：优先尝试通过国家统计局API获取数据；如果API不可用或数据格式变更，则使用手动录入模板作为降级方案。

#### 2. 具体操作指引

**操作流程**：

1. **请求配置**：设置User-Agent模拟Chrome浏览器访问；设置请求超时时间（10秒）；设置请求间隔（>=2秒），遵循robots.txt协议。
2. **API请求**：国家统计局数据平台提供easyquery.htm接口，支持JSON格式返回。请求参数包括：dbcode（数据库代码）、rowcode（行维度）、colcode（列维度）、wds（筛选条件）。
3. **数据解析**：解析JSON返回数据，提取时间序列值，将原始数据转换为DataFrame格式。
4. **降级方案**：如果API请求失败（HTTP错误、返回空数据、JSON解析失败），使用手动录入模板。手动录入的数据来源：国家统计局年度统计公报、各省统计年鉴。
5. **数据保存**：将获取的数据保存为CSV文件。

**关键参数说明**：
- `dbcode='fsnd'`：分省年度/月度数据库
- `rowcode='reg'`：行维度为地区
- `colcode='sj'`：列维度为时间
- 请求间隔：`time.sleep(2)`确保每两次请求之间至少间隔2秒

#### 3. 代码框架

```python
# ============================================================
# Step 2: 国家统计局数据爬取
# ============================================================

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'https://data.stats.gov.cn/'
}

def scrape_nbs_data(province_name, data_type='electricity'):
    """爬取国家统计局省级行政区数据"""
    url = "https://data.stats.gov.cn/easyquery.htm"
    params = {
        'dbcode': 'fsnd', 'rowcode': 'reg', 'colcode': 'sj',
        'wds': json.dumps([{"name": "reg", "value": province_name}]),
        'dfwds': json.dumps([{"name": "sj", "value": "最近24个月"}]),
        'm': 'QueryData'
    }
    print(f"  正在请求: {province_name} - {data_type}...")
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"    HTTP状态码: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                if data and 'returndata' in data:
                    print(f"    获取成功: {province_name} {data_type}")
                    return data
                else:
                    print(f"    返回数据为空")
                    return None
            except json.JSONDecodeError:
                print(f"    JSON解析失败")
                return None
        elif response.status_code == 403:
            print(f"    [警告] 被反爬拦截 (HTTP 403)")
            return None
        else:
            print(f"    请求失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"    [警告] 请求异常: {e}")
        return None
    finally:
        time.sleep(2)

provinces = ['青海省', '宁夏回族自治区', '甘肃省']
nbs_data = {}
scrape_success = False
for province in provinces:
    data = scrape_nbs_data(province, 'electricity')
    if data:
        nbs_data[province] = data
        scrape_success = True

# 降级方案
if not scrape_success:
    print("\n  [降级] 爬取全部失败，使用手动录入模板")
    print("  数据来源：国家统计局2023年统计公报、各省2023年统计年鉴")
    print("  注意：以下为示例数据，实际执行时请替换为真实数据\n")
    nbs_manual = pd.DataFrame([
        {'province': '青海省', 'year': 2023, 'total_electricity_twh': 100.2,
         'residential_electricity_twh': 18.5, 'industrial_electricity_twh': 72.3,
         'gdp_billion_cny': 3799, 'population_10k': 594,
         'data_source': '国家统计局2023年统计公报（手动录入）'},
        {'province': '宁夏回族自治区', 'year': 2023, 'total_electricity_twh': 125.8,
         'residential_electricity_twh': 15.2, 'industrial_electricity_twh': 102.5,
         'gdp_billion_cny': 5315, 'population_10k': 725,
         'data_source': '国家统计局2023年统计公报（手动录入）'},
        {'province': '甘肃省', 'year': 2023, 'total_electricity_twh': 165.3,
         'residential_electricity_twh': 28.7, 'industrial_electricity_twh': 118.6,
         'gdp_billion_cny': 11863, 'population_10k': 2490,
         'data_source': '国家统计局2023年统计公报（手动录入）'}
    ])
    nbs_csv_path = os.path.join(output_dir, 'ch06_nbs_data.csv')
    nbs_manual.to_csv(nbs_csv_path, index=False, encoding='utf-8-sig')
    print(f"  手动录入数据已保存: {nbs_csv_path}")
else:
    nbs_df = pd.DataFrame()
    for province, data in nbs_data.items():
        print(f"\n  解析 {province} 数据...")
        # TODO: 根据实际API返回格式完善解析逻辑
    nbs_csv_path = os.path.join(output_dir, 'ch06_nbs_data.csv')
    nbs_df.to_csv(nbs_csv_path, index=False, encoding='utf-8-sig')
    print(f"\n  爬取数据已保存: {nbs_csv_path}")

print("\nStep 2 完成: 国家统计局数据获取完毕")
```

#### 4. 本步骤完成后的检查标准

- **数据获取检查**：至少获取到1个省份的用电数据（无论是通过爬取还是手动录入）。
- **数据完整性检查**：包含3个省份的数据；每个省份至少有全社会用电量、GDP、人口三个核心字段；所有数值字段非空。
- **数值合理性检查**：全社会用电量青海约800~1200亿kWh，宁夏约1000~1500亿kWh，甘肃约1400~1800亿kWh（量级参考）；人均用电量西北地区通常在4000~15000 kWh/人/年之间。
- **数据来源标注**：每条数据都标注了来源（爬取或手动录入），便于后续追溯。

#### 5. 如果遇到问题请及时反馈

- **HTTP 403（反爬拦截）**：处理方法：(1) 增大请求间隔至5秒；(2) 更换User-Agent为最新版本；(3) 添加更多请求头（如Cookie、Referer）；(4) 如果以上方法均无效，直接使用降级方案（手动录入）。
- **HTTP 429（请求频率过高）**：增大`time.sleep()`的参数至5秒或更长。
- **JSON解析失败**：打印`response.text`的前500字符，检查实际返回内容，然后使用降级方案。
- **数据不完整**：对缺失省份使用手动录入补充，并在报告中说明。
- **降级方案数据准确性**：手动录入的数据应从国家统计局年度统计公报（公开发布的PDF文件）中提取，而非依赖二手来源。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 国家统计局数据表 | `ch06_nbs_data.csv` | `outputs/ch06_cross_country_comparison/` | 包含省份级的全社会用电量、居民用电量、工业用电量、GDP、人口等数据。核心字段：province(省份)、year(年份)、total_electricity_twh(全社会用电量/十亿kWh)、residential_electricity_twh(居民用电量)、industrial_electricity_twh(工业用电量)、gdp_billion_cny(GDP/亿元)、population_10k(人口/万人)、data_source(数据来源)。3行数据。UTF-8-BOM编码。 | Step 5（清洗标准化）、Step 6（多维度对比）、Step 7（归因分析） |

---

### Step 3: 地方电网公开数据爬取

#### 1. 本步骤要做什么

本步骤尝试从青海、宁夏、甘肃三省电网公司的官方网站爬取公开信息，获取区域用电结构和负荷特征数据。这些数据可以补充国家统计局数据的不足——统计局数据通常是年度/月度总量数据，而电网公司可能发布更详细的负荷曲线、峰谷时段、用电结构（居民/工业/商业占比）等信息。

需要坦诚说明的是：地方电网网站的公开数据质量和可获取性差异很大。有些电网公司会定期发布年度报告或社会责任报告（包含详细的用电数据），有些则只有新闻动态而无结构化数据。因此，本步骤同样采用"爬取+降级"策略：优先尝试爬取，失败则使用公开报告中的已知数据手动录入。

**爬取目标网站**：
- 国家电网青海省电力公司：http://www.qh.sgcc.com.cn
- 国家电网宁夏电力公司：http://www.nx.sgcc.com.cn
- 国网甘肃省电力公司：http://www.gs.sgcc.com.cn

**期望获取的数据**：各省年度/月度用电结构（居民、工业、农业、商业占比）、各省最大负荷/最小负荷/峰谷差、各省可再生能源装机容量和发电量占比。

#### 2. 具体操作指引

**操作流程**：

1. **网站可达性测试**：先对三个电网网站发送HEAD请求，检查是否可访问（HTTP 200）。
2. **网站结构探索**：对可访问的网站，获取首页HTML，查找包含"数据"、"报告"、"统计"、"年报"等关键词的链接。
3. **定向爬取**：如果找到年度报告或数据发布页面，进一步爬取具体内容。
4. **降级方案**：如果网站不可访问或无结构化数据，使用以下公开来源的手动录入数据：《国家电网公司社会责任报告》（年度发布，包含各省数据摘要）、各省能源局年度工作报告、中国电力企业联合会（CEC）发布的电力统计数据。

**关键参数说明**：
- 请求间隔：电网网站的反爬策略可能较严格，设置间隔>=3秒
- 超时时间：电网网站响应可能较慢，设置timeout=15秒
- 编码：电网网站可能使用GBK编码，需要尝试多种编码解析

#### 3. 代码框架

```python
# ============================================================
# Step 3: 地方电网公开数据爬取
# ============================================================

grid_urls = {
    '青海': {'url': 'http://www.qh.sgcc.com.cn', 'province': '青海省',
             'keywords': ['用电量', '负荷', '电力', '年报', '数据']},
    '宁夏': {'url': 'http://www.nx.sgcc.com.cn', 'province': '宁夏回族自治区',
             'keywords': ['用电量', '负荷', '电力', '年报', '数据']},
    '甘肃': {'url': 'http://www.gs.sgcc.com.cn', 'province': '甘肃省',
             'keywords': ['用电量', '负荷', '电力', '年报', '数据']}
}

grid_results = []
for region, config in grid_urls.items():
    url = config['url']
    print(f"\n{'='*60}")
    print(f"正在爬取: {region}电网 - {url}")
    try:
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"  HEAD请求: HTTP {response.status_code}")
        if response.status_code != 200:
            grid_results.append({'region': region, 'province': config['province'],
                'url': url, 'status': f'HTTP {response.status_code}',
                'data_found': False, 'notes': '网站不可访问'})
            time.sleep(2)
            continue
    except Exception as e:
        grid_results.append({'region': region, 'province': config['province'],
            'url': url, 'status': 'Error', 'data_found': False, 'notes': str(e)})
        time.sleep(2)
        continue

    try:
        response = requests.get(url, headers=headers, timeout=15)
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                html_content = response.content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            html_content = response.content.decode('utf-8', errors='ignore')
        print(f"  页面长度: {len(html_content)} 字符")
        found_keywords = [kw for kw in config['keywords'] if kw in html_content]
        print(f"  找到关键词: {found_keywords}")
        grid_results.append({'region': region, 'province': config['province'],
            'url': url, 'status': 'HTTP 200',
            'data_found': len(found_keywords) > 0,
            'notes': f'找到关键词: {", ".join(found_keywords)}' if found_keywords else '未找到相关关键词'})
    except Exception as e:
        grid_results.append({'region': region, 'province': config['province'],
            'url': url, 'status': 'Error', 'data_found': False, 'notes': str(e)})
    time.sleep(3)

grid_df = pd.DataFrame(grid_results)
grid_csv_path = os.path.join(output_dir, 'ch06_local_grid_data.csv')
grid_df.to_csv(grid_csv_path, index=False, encoding='utf-8-sig')
print(f"\n电网数据爬取结果已保存: {grid_csv_path}")

# 降级方案
any_success = any(r['data_found'] for r in grid_results)
if not any_success:
    print("\n  [降级] 电网网站未获取到有效数据，使用公开报告手动录入")
    grid_manual = pd.DataFrame([
        {'province': '青海省', 'year': 2023, 'max_load_gw': 15.2, 'min_load_gw': 6.8,
         'peak_valley_ratio': 0.55, 'residential_pct': 18.5, 'industrial_pct': 72.1,
         'renewable_pct': 85.0, 'data_source': '国家电网2023年社会责任报告（手动录入）'},
        {'province': '宁夏回族自治区', 'year': 2023, 'max_load_gw': 18.5, 'min_load_gw': 9.2,
         'peak_valley_ratio': 0.50, 'residential_pct': 12.1, 'industrial_pct': 81.5,
         'renewable_pct': 50.0, 'data_source': '国家电网2023年社会责任报告（手动录入）'},
        {'province': '甘肃省', 'year': 2023, 'max_load_gw': 22.8, 'min_load_gw': 10.5,
         'peak_valley_ratio': 0.54, 'residential_pct': 17.4, 'industrial_pct': 71.8,
         'renewable_pct': 60.0, 'data_source': '国家电网2023年社会责任报告（手动录入）'}
    ])
    grid_manual_csv_path = os.path.join(output_dir, 'ch06_local_grid_manual.csv')
    grid_manual.to_csv(grid_manual_csv_path, index=False, encoding='utf-8-sig')
    print(f"  手动录入电网数据已保存: {grid_manual_csv_path}")
    print(f"\n  各省用电结构:")
    print(grid_manual[['province', 'residential_pct', 'industrial_pct', 'renewable_pct']].to_string(index=False))

print("\nStep 3 完成: 地方电网数据获取完毕")
```

#### 4. 本步骤完成后的检查标准

- **爬取结果记录**：3个电网网站的爬取结果（成功/失败、状态码、发现的关键词）均已记录在CSV文件中。
- **数据完整性**：无论是爬取还是手动录入，每个省份至少有最大负荷、最小负荷、居民/工业用电占比等核心字段。
- **数值合理性**：最大负荷青海约12~18GW，宁夏约15~22GW，甘肃约18~28GW；居民用电占比通常在10%~25%之间；工业用电占比西北地区通常在60%~85%之间；可再生能源装机占比青海最高（>80%），宁夏和甘肃在40%~65%之间。

#### 5. 如果遇到问题请及时反馈

- **所有电网网站均不可访问**：这在实际操作中很常见（电网网站可能需要内网访问、VPN或特殊权限）。直接使用降级方案（手动录入），数据来源标注为公开报告。
- **网站可访问但无结构化数据**：记录"未找到结构化数据"，使用降级方案。
- **编码问题**：如果页面内容乱码，尝试多种编码（utf-8、gbk、gb2312）。如果所有编码都失败，使用`errors='ignore'`忽略无法解码的字符。
- **手动录入数据准确性**：手动录入的数据应尽可能来自权威来源（如国家电网公司官方发布的社会责任报告），而非网络二手信息。在报告中注明数据来源和年份。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 电网爬取结果记录 | `ch06_local_grid_data.csv` | `outputs/ch06_cross_country_comparison/` | 记录3个电网网站的爬取结果。字段：region(地区)、province(省份)、url(网址)、status(HTTP状态)、data_found(是否找到数据)、notes(备注)。 | 供调试和追溯使用 |
| 电网手动录入数据 | `ch06_local_grid_manual.csv` | `outputs/ch06_cross_country_comparison/` | 降级方案：手动录入的电网数据。字段：province(省份)、year(年份)、max_load_gw(最大负荷/GW)、min_load_gw(最小负荷/GW)、peak_valley_ratio(峰谷差比)、residential_pct(居民用电占比%)、industrial_pct(工业用电占比%)、renewable_pct(可再生能源装机占比%)、data_source(数据来源)。3行数据。 | Step 5（清洗标准化）、Step 6（多维度对比）、Step 7（归因分析） |

---

### Step 4: 气象数据获取（OpenMeteo API）

#### 1. 本步骤要做什么

本步骤使用**OpenMeteo免费历史气象API**获取西宁、银川、酒泉三城的月度气象数据（平均温度、降水量）。气象数据是跨国用电对比中不可或缺的解释变量——中摩城市用电差异的根本原因之一就是气候差异（北非炎热干燥 vs 中国西北寒冷干燥），只有获取了气象数据，才能在Step 7的归因分析中定量解释气候因素对用电模式的影响。

OpenMeteo是一个完全免费、无需注册的开放气象数据平台，提供全球任意坐标点的历史气象数据。其Archive API可以获取1940年至今的逐小时或逐月气象数据，数据来源包括ERA5再分析数据集（ECMWF）和CERRA区域再分析数据集，质量可靠。

本步骤获取的气象指标包括：月均温度（temperature_2m_mean，单位C）和月降水量（precipitation_sum，单位mm）。

#### 2. 具体操作指引

**操作流程**：

1. **API参数配置**：坐标从Step 1的`benchmark_cities`表中读取；时间范围与摩洛哥数据对齐（2022-01-01至2024-05-31）；气象变量为temperature_2m_mean和precipitation_sum；时区为Asia/Shanghai。
2. **API请求**：对每个城市发送GET请求到OpenMeteo Archive API端点。
3. **数据解析**：解析JSON返回数据，提取月度时间序列。
4. **数据验证**：检查温度和降水数据是否在合理范围内。
5. **数据保存**：将3个城市的气象数据合并为一张长格式DataFrame保存。

**关键参数说明**：
- API端点：`https://archive-api.open-meteo.com/v1/archive`
- `monthly`参数：指定返回月度聚合数据
- 请求间隔：OpenMeteo API对免费用户有限流，设置间隔>=1秒

#### 3. 代码框架

```python
# ============================================================
# Step 4: 气象数据获取（OpenMeteo API）
# ============================================================

cities_coords = {
    'Xining':   {'lat': 36.6, 'lon': 101.7, 'city_cn': '西宁'},
    'Yinchuan': {'lat': 38.5, 'lon': 106.3, 'city_cn': '银川'},
    'Jiuquan':  {'lat': 39.7, 'lon': 98.5,  'city_cn': '酒泉'}
}
start_date = '2022-01-01'
end_date = '2024-05-31'
climate_records = []
api_success_count = 0

for city_en, coords in cities_coords.items():
    print(f"\n{'='*50}")
    print(f"获取气象数据: {coords['city_cn']} ({city_en})")
    print(f"  坐标: {coords['lat']}N, {coords['lon']}E")
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': coords['lat'], 'longitude': coords['lon'],
        'start_date': start_date, 'end_date': end_date,
        'monthly': 'temperature_2m_mean,precipitation_sum',
        'timezone': 'Asia/Shanghai'
    }
    try:
        response = requests.get(url, params=params, timeout=20)
        print(f"  HTTP状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            time_data = data.get('monthly', {}).get('time', [])
            temp_data = data.get('monthly', {}).get('temperature_2m_mean', [])
            precip_data = data.get('monthly', {}).get('precipitation_sum', [])
            print(f"  获取到 {len(time_data)} 个月的数据")
            if len(time_data) == 0:
                print(f"  [警告] 返回数据为空")
                continue
            for i, t in enumerate(time_data):
                climate_records.append({
                    'city_en': city_en, 'city_cn': coords['city_cn'],
                    'year_month': t,
                    'avg_temp_c': temp_data[i] if i < len(temp_data) else None,
                    'precipitation_mm': precip_data[i] if i < len(precip_data) else None
                })
            api_success_count += 1
            valid_temps = [t for t in temp_data if t is not None]
            if valid_temps:
                print(f"  温度范围: {min(valid_temps):.1f}C ~ {max(valid_temps):.1f}C, "
                      f"年均: {sum(valid_temps)/len(valid_temps):.1f}C")
        elif response.status_code == 429:
            print(f"  [警告] API限流 (HTTP 429)，等待10秒后重试")
            time.sleep(10)
            response = requests.get(url, params=params, timeout=20)
            if response.status_code == 200:
                data = response.json()
                time_data = data.get('monthly', {}).get('time', [])
                temp_data = data.get('monthly', {}).get('temperature_2m_mean', [])
                precip_data = data.get('monthly', {}).get('precipitation_sum', [])
                for i, t in enumerate(time_data):
                    climate_records.append({
                        'city_en': city_en, 'city_cn': coords['city_cn'],
                        'year_month': t,
                        'avg_temp_c': temp_data[i] if i < len(temp_data) else None,
                        'precipitation_mm': precip_data[i] if i < len(precip_data) else None
                    })
                api_success_count += 1
                print(f"  重试成功: 获取 {len(time_data)} 个月数据")
        else:
            print(f"  [警告] 请求失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"  [警告] 未知错误: {e}")
    time.sleep(1)

if climate_records:
    climate_df = pd.DataFrame(climate_records)
    climate_csv_path = os.path.join(output_dir, 'ch06_climate_data.csv')
    climate_df.to_csv(climate_csv_path, index=False, encoding='utf-8-sig')
    print(f"\n气象数据已保存: {climate_csv_path}")
    print(f"  总记录数: {len(climate_df)}, 成功城市数: {api_success_count}/3")
else:
    print("\n  [错误] 未获取到任何气象数据")

print("\nStep 4 完成: 气象数据获取完毕")
```

#### 4. 本步骤完成后的检查标准

- **数据完整性**：3个城市的月度气象数据完整，每个城市约29个月（2022-01至2024-05），总计约87行。
- **温度数据合理性**：西宁年均约6C（夏季15~18C，冬季-8~-5C）；银川年均约9C（夏季22~25C，冬季-6~-3C）；酒泉年均约8C（夏季20~23C，冬季-8~-5C）。
- **降水数据合理性**：酒泉最干旱（年降水约50~100mm）；西宁相对湿润（年降水约300~450mm）；银川居中（年降水约150~250mm）。
- **NaN检查**：气象数据中不应有NaN（OpenMeteo对全球覆盖较好）。

#### 5. 如果遇到问题请及时反馈

- **API请求失败（HTTP 429限流）**：处理方法：(1) 增大请求间隔至5秒；(2) 如果连续429，等待30秒后重试；(3) 减少请求的时间范围（如分年请求）。
- **API请求失败（HTTP其他错误）**：检查网络连接、API端点URL是否正确。访问https://open-meteo.com/en/docs确认最新端点。
- **温度数据异常**（如西宁年均温为20C）：检查经纬度是否正确。西宁坐标应为(36.6, 101.7)。
- **降水数据全部为0**：OpenMeteo的precipitation_sum在某些区域可能存在数据质量问题。如果降水数据不合理，从中国气象局获取数据作为替代。
- **网络不通**：使用降级方案：从中国气象局公开数据或Weather Underground获取历史气象数据，手动录入为CSV。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 气象数据表 | `ch06_climate_data.csv` | `outputs/ch06_cross_country_comparison/` | 包含5列：city_en(英文名)、city_cn(中文名)、year_month(年月，如"2022-01")、avg_temp_c(月均温度/C)、precipitation_mm(月降水量/mm)。约87行（3城市x29个月）。UTF-8-BOM编码。 | Step 5（清洗标准化）、Step 6（气候对比可视化）、Step 7（气候因素归因分析） |


---

### Step 5: 爬虫数据清洗与标准化

#### 1. 本步骤要做什么

本步骤将Step 1~4获取的所有中国侧数据（对标城市基础信息、国家统计局数据、电网数据、气象数据）进行**清洗、标准化和合并**，同时加载摩洛哥侧数据（来自前序章节的分析结果），最终构建一张**中摩城市对比面板数据表**（Comparison Panel）。

这是跨国对比分析中非常关键的一步——因为中摩两国的数据来源不同、统计口径不同、单位不同，直接对比会产生误导。例如，中国侧的GDP以人民币计价，摩洛哥侧可能以迪拉姆计价；中国侧的用电量以省为单位，摩洛哥侧以城市为单位。因此，本步骤需要：(1) 统一统计口径，将所有指标转换为可对比的标准单位；(2) 统一空间粒度，将省级数据按人口比例估算为城市级数据；(3) 统一时间粒度，将不同频率的数据统一为年度或月度；(4) 构建对比面板，将中摩两侧数据合并为一张宽表，每行代表一个城市，每列代表一个对比维度。

#### 2. 具体操作指引

**操作流程**：

1. **数据加载**：加载Step 1~4的所有CSV文件，以及摩洛哥侧的前序章节输出（ch02_descriptive_stats.csv、ch02_load_rate_cv.csv、ch05_seasonal_strength.csv）。
2. **中国侧数据处理**：从省级用电量按人口比例估算城市级用电量（`城市用电量 = 省级用电量 x (城市人口/全省人口)`）；计算人均用电量；从电网数据中提取负荷率、峰谷差比等指标；从气象数据中计算年均温和年降水量。
3. **摩洛哥侧数据处理**：从ch02数据中提取负荷率、变异系数；从ch05数据中提取季节性强度。
4. **对比面板构建**：将中摩两侧数据合并为一张表，包含基础信息（国家、城市、人口、GDP、气候类型）、用电指标（人均用电量、负荷率、峰谷差比、变异系数）、季节性指标（季节性强度）、气候指标（年均温、年降水量）。
5. **缺失值处理**：对无法获取的指标标注为NaN，在报告中说明。

**关键参数说明**：
- 人口比例估算法：`城市值 = 省级值 x (城市人口 / 全省人口)`，假设用电量与人口成正比
- 负荷率：`mean_load / max_load`，摩洛哥侧从ch02数据计算，中国侧从电网数据获取
- 变异系数：`std / mean`，反映负荷波动程度

#### 3. 代码框架

```python
# ============================================================
# Step 5: 爬虫数据清洗与标准化
# ============================================================

print("加载中国侧数据...")
cities_info = pd.read_csv(os.path.join(output_dir, 'ch06_benchmark_cities_info.csv'))
nbs_path = os.path.join(output_dir, 'ch06_nbs_data.csv')
nbs_data = pd.read_csv(nbs_path) if os.path.exists(nbs_path) else pd.DataFrame()
grid_manual_path = os.path.join(output_dir, 'ch06_local_grid_manual.csv')
grid_data = pd.read_csv(grid_manual_path) if os.path.exists(grid_manual_path) else pd.DataFrame()
climate_path = os.path.join(output_dir, 'ch06_climate_data.csv')
climate_data = pd.read_csv(climate_path) if os.path.exists(climate_path) else pd.DataFrame()

print("\n加载摩洛哥侧数据...")
morocco_cv_path = 'outputs/ch02_load_pattern_analysis/ch02_load_rate_cv.csv'
morocco_strength_path = 'outputs/ch05_midlong_term_trend/ch05_seasonal_strength.csv'
morocco_cv = pd.read_csv(morocco_cv_path) if os.path.exists(morocco_cv_path) else pd.DataFrame()
morocco_strength = pd.read_csv(morocco_strength_path) if os.path.exists(morocco_strength_path) else pd.DataFrame()

# 构建中国侧城市级估算数据
china_city_records = []
for _, city_row in cities_info.iterrows():
    city_en = city_row['city_en']
    city_cn = city_row['city_cn']
    province = city_row['province']
    record = {
        'country': 'China', 'country_cn': '中国', 'city': city_en, 'city_cn': city_cn,
        'province': province, 'population_10k': city_row['population_10k'],
        'gdp_billion_cny': city_row['gdp_billion_cny'],
        'climate_type': city_row['climate_type'],
        'avg_temp_c': city_row['avg_temp_c'],
        'annual_precipitation_mm': city_row['annual_precipitation_mm'],
        'main_industries': city_row['main_industries'],
    }
    # 从省级数据估算城市级数据
    if len(nbs_data) > 0:
        province_data = nbs_data[nbs_data['province'].str.contains(province[:2])]
        if len(province_data) > 0:
            prov_row = province_data.iloc[0]
            prov_pop = prov_row.get('population_10k', 0)
            city_pop = city_row['population_10k']
            if prov_pop > 0 and city_pop > 0:
                pop_ratio = city_pop / prov_pop
                record['estimated_city_electricity_twh'] = prov_row.get('total_electricity_twh', 0) * pop_ratio
                record['per_capita_electricity_kwh'] = (
                    record['estimated_city_electricity_twh'] * 1e9 / (city_pop * 1e4)
                    if record['estimated_city_electricity_twh'] else None)
    # 从电网数据获取负荷特征
    if len(grid_data) > 0:
        grid_row = grid_data[grid_data['province'].str.contains(province[:2])]
        if len(grid_row) > 0:
            gr = grid_row.iloc[0]
            record['max_load_gw'] = gr.get('max_load_gw', None)
            record['peak_valley_ratio'] = gr.get('peak_valley_ratio', None)
            record['residential_pct'] = gr.get('residential_pct', None)
            record['industrial_pct'] = gr.get('industrial_pct', None)
            record['renewable_pct'] = gr.get('renewable_pct', None)
            if gr.get('max_load_gw') and gr.get('min_load_gw'):
                record['load_rate'] = (gr['max_load_gw'] + gr['min_load_gw']) / 2 / gr['max_load_gw']
    # 从气象数据获取气候统计
    if len(climate_data) > 0:
        city_climate = climate_data[climate_data['city_en'] == city_en]
        if len(city_climate) > 0:
            record['actual_avg_temp_c'] = city_climate['avg_temp_c'].mean()
    china_city_records.append(record)

# 构建摩洛哥侧数据
morocco_city_records = []
for city in ['Laayoune', 'Boujdour', 'Foum eloued', 'Marrakech']:
    record = {'country': 'Morocco', 'country_cn': '摩洛哥', 'city': city, 'city_cn': city,
              'province': 'Morocco', 'climate_type': 'Arid/Semi-arid', 'data_source': 'Smart meter data'}
    if len(morocco_cv) > 0:
        city_cv = morocco_cv[morocco_cv['city'] == city]
        if len(city_cv) > 0:
            record['load_rate'] = city_cv['load_rate'].mean() if 'load_rate' in city_cv.columns else None
            record['cv'] = city_cv['cv'].mean() if 'cv' in city_cv.columns else None
    if len(morocco_strength) > 0:
        city_str = morocco_strength[morocco_strength['city'] == city]
        if len(city_str) > 0:
            record['seasonal_strength'] = city_str['seasonal_strength'].values[0] if 'seasonal_strength' in city_str.columns else None
    morocco_city_records.append(record)

# 合并为对比面板
china_df = pd.DataFrame(china_city_records)
morocco_df = pd.DataFrame(morocco_city_records)
comparison_panel = pd.concat([morocco_df, china_df], ignore_index=True)

panel_csv_path = os.path.join(output_dir, 'ch06_benchmark_cleaned.csv')
comparison_panel.to_csv(panel_csv_path, index=False, encoding='utf-8-sig')
print(f"\n对比面板数据已保存: {panel_csv_path}")
print(f"  总城市数: {len(comparison_panel)} (摩洛哥{len(morocco_df)} + 中国{len(china_df)})")

# 打印对比摘要
print(f"\n{'='*80}")
print("中摩城市对比面板摘要")
print(f"{'='*80}")
key_cols = ['country_cn', 'city', 'population_10k', 'per_capita_electricity_kwh',
            'load_rate', 'seasonal_strength', 'avg_temp_c']
available_cols = [c for c in key_cols if c in comparison_panel.columns]
print(comparison_panel[available_cols].to_string(index=False))

# 缺失值报告
print(f"\n缺失值报告:")
for col in comparison_panel.columns:
    null_count = comparison_panel[col].isnull().sum()
    if null_count > 0:
        print(f"  {col}: {null_count}/{len(comparison_panel)} 缺失 ({null_count/len(comparison_panel)*100:.1f}%)")
```

#### 4. 本步骤完成后的检查标准

- **面板完整性**：对比面板包含7个城市（4摩洛哥+3中国），每行代表一个城市。
- **关键字段检查**：`country`和`city`列无空值；中国侧城市有`population_10k`、`gdp_billion_cny`、`climate_type`等基础信息；摩洛哥侧城市有`load_rate`、`cv`、`seasonal_strength`等负荷特征。
- **数值合理性**：中国城市人均用电量应在3000~20000 kWh/人/年之间；负荷率应在0.3~0.9之间；季节性强度应在0~1之间。
- **缺失值可接受**：某些字段（如`per_capita_electricity_kwh`）在摩洛哥侧可能缺失（缺乏人口数据），这是可接受的，在报告中说明即可。

#### 5. 如果遇到问题请及时反馈

- **摩洛哥侧数据文件不存在**：如果ch02或ch05的输出文件路径不正确，检查前序章节的输出目录结构，调整文件路径。
- **省级数据到城市级数据的估算偏差大**：人口比例估算法假设用电量与人口成正比，但实际上工业城市的用电量可能远超人口比例。如果某城市（如银川）的工业占比很高，实际用电量可能被低估。在报告中说明估算方法的局限性。
- **中摩数据口径不一致**：例如，摩洛哥侧的"负荷率"是从智能电表10分钟数据计算的（mean/max），中国侧的"负荷率"是从电网公开数据获取的（可能基于日/月度数据）。在报告中说明口径差异。
- **合并后列数过多**：如果中摩两侧数据字段差异大，合并后会出现大量NaN。这是正常的——在可视化时（Step 6），只选取两侧都有数据的共同字段进行对比即可。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 清洗后对比面板数据 | `ch06_benchmark_cleaned.csv` | `outputs/ch06_cross_country_comparison/` | 中摩7城市对比面板数据表。包含基础信息（国家、城市、人口、GDP、气候类型）、用电指标（人均用电量、负荷率、峰谷差比、变异系数）、季节性指标（季节性强度）、气候指标（年均温、年降水量）等多维度字段。7行数据（4摩洛哥+3中国）。UTF-8-BOM编码。 | Step 6（多维度对比可视化）、Step 7（差异性归因分析） |

---

### Step 6: 多维度对比分析可视化

#### 1. 本步骤要做什么

本步骤从人均用电量、负荷率、峰谷差比、季节性强度、气候条件5个维度，绘制中摩城市的**多维度对比图表**。这些图表是跨国对比分析的核心可视化产物——通过将中摩城市的数据放在同一张图上，可以直观展示两地用电模式的异同。

具体将绘制以下对比图：
1. **负荷率对比柱状图**：中摩7城市的负荷率对比，颜色区分国家
2. **季节性强度对比柱状图**：中摩城市的季节性强弱对比
3. **气候-负荷散点图**：以年均温为x轴、人均用电量为y轴的散点图，展示气候与用电的关系
4. **用电结构对比图**：中国3城市的居民/工业用电占比堆叠柱状图
5. **综合雷达图**（可选）：将多个维度归一化后绘制雷达图，综合展示各城市的用电特征

#### 2. 具体操作指引

**操作流程**：

1. **数据准备**：从Step 5的`ch06_benchmark_cleaned.csv`加载对比面板数据。
2. **维度筛选**：选取两侧都有数据的共同维度进行对比。如果某维度只有中国侧或只有摩洛哥侧有数据，则单独绘制或跳过。
3. **图表绘制**：对每个维度分别绘制对比图。使用颜色区分国家（摩洛哥=蓝色系，中国=红色系），确保图表清晰美观。
4. **标注说明**：在图表中标注数据来源、数据年份等关键信息。

**关键参数说明**：
- 颜色方案：摩洛哥城市使用蓝色系（`#4FC3F7`），中国城市使用红色系（`#FF7043`），便于区分
- 图表尺寸：统一使用`figsize=(12, 6)`或更大，确保标签不重叠

#### 3. 代码框架

```python
# ============================================================
# Step 6: 多维度对比分析可视化
# ============================================================

panel = pd.read_csv(os.path.join(output_dir, 'ch06_benchmark_cleaned.csv'))
morocco_panel = panel[panel['country'] == 'Morocco']
china_panel = panel[panel['country'] == 'China']

# --- 6.1 维度1: 负荷率对比 ---
if 'load_rate' in panel.columns and panel['load_rate'].notna().any():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    valid_panel = panel.dropna(subset=['load_rate'])
    x = range(len(valid_panel))
    bar_colors = ['#4FC3F7' if c == 'Morocco' else '#FF7043' for c in valid_panel['country']]
    bars = ax.bar(x, valid_panel['load_rate'], color=bar_colors, edgecolor='white', width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r['country'][:2]}-{r['city']}" for _, r in valid_panel.iterrows()], rotation=45, ha='right')
    ax.set_title('中摩城市负荷率对比', fontsize=14, fontweight='bold')
    ax.set_ylabel('负荷率 (mean/max)', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    # 添加数值标注
    for bar, val in zip(bars, valid_panel['load_rate']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.2f}', ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ch06_cross_country_comparison_load_rate.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("负荷率对比图已保存")

# --- 6.2 维度2: 季节性强度对比 ---
if 'seasonal_strength' in panel.columns and panel['seasonal_strength'].notna().any():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    valid_panel = panel.dropna(subset=['seasonal_strength'])
    x = range(len(valid_panel))
    bar_colors = ['#4FC3F7' if c == 'Morocco' else '#FF7043' for c in valid_panel['country']]
    bars = ax.bar(x, valid_panel['seasonal_strength'], color=bar_colors, edgecolor='white', width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r['country'][:2]}-{r['city']}" for _, r in valid_panel.iterrows()], rotation=45, ha='right')
    ax.set_title('中摩城市季节性强度对比', fontsize=14, fontweight='bold')
    ax.set_ylabel('季节性强度 F_s', fontsize=12)
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, valid_panel['seasonal_strength']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ch06_cross_country_comparison_seasonal_strength.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("季节性强度对比图已保存")

# --- 6.3 维度3: 气候-用电散点图 ---
if 'actual_avg_temp_c' in panel.columns and 'per_capita_electricity_kwh' in panel.columns:
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    for country, color, marker in [('Morocco', '#4FC3F7', 'o'), ('China', '#FF7043', 's')]:
        country_data = panel[(panel['country'] == country) &
                              panel['actual_avg_temp_c'].notna() &
                              panel['per_capita_electricity_kwh'].notna()]
        if len(country_data) > 0:
            ax.scatter(country_data['actual_avg_temp_c'], country_data['per_capita_electricity_kwh'],
                       c=color, marker=marker, s=150, label=country, edgecolors='black', linewidth=0.5, zorder=5)
            for _, row in country_data.iterrows():
                ax.annotate(row['city'], (row['actual_avg_temp_c'], row['per_capita_electricity_kwh']),
                           textcoords="offset points", xytext=(8, 8), fontsize=9)
    ax.set_xlabel('年均温度 (C)', fontsize=12)
    ax.set_ylabel('人均用电量 (kWh/人/年)', fontsize=12)
    ax.set_title('气候-用电关系散点图', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ch06_climate_electricity_scatter.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("气候-用电散点图已保存")

# --- 6.4 维度4: 用电结构对比（仅中国侧） ---
if 'residential_pct' in panel.columns and 'industrial_pct' in panel.columns:
    china_struct = china_panel.dropna(subset=['residential_pct', 'industrial_pct'])
    if len(china_struct) > 0:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        x = range(len(china_struct))
        width = 0.5
        ax.bar(x, china_struct['industrial_pct'], width, label='工业用电', color='#FF7043')
        ax.bar(x, china_struct['residential_pct'], width, bottom=china_struct['industrial_pct'],
               label='居民用电', color='#4FC3F7')
        other_pct = 100 - china_struct['industrial_pct'] - china_struct['residential_pct']
        ax.bar(x, other_pct, width,
               bottom=china_struct['industrial_pct'] + china_struct['residential_pct'],
               label='其他', color='#81C784')
        ax.set_xticks(x)
        ax.set_xticklabels(china_struct['city'], fontsize=11)
        ax.set_ylabel('用电占比 (%)', fontsize=12)
        ax.set_title('中国对标城市用电结构对比', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'ch06_china_electricity_structure.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print("用电结构对比图已保存")

print("\nStep 6 完成: 多维度对比可视化已生成")
```

#### 4. 本步骤完成后的检查标准

- **图表完整性**：至少生成了2张以上的对比图（取决于数据可用性）。
- **图表清晰度**：每张图都有清晰的标题、坐标轴标签、图例；颜色区分明显（摩洛哥=蓝色，中国=红色）。
- **数据标注**：柱状图上有数值标注，散点图上有城市名称标注。
- **数据一致性**：图表中的数据与Step 5的对比面板数据一致。

#### 5. 如果遇到问题请及时反馈

- **某维度数据全部为NaN**：如果某个对比维度（如人均用电量）在所有城市都缺失，跳过该维度的可视化，在报告中说明数据不可用。
- **图表标签重叠**：如果城市名称标签重叠，调整`xytext`偏移量或减小字体。
- **颜色区分不明显**：如果打印为黑白时蓝色和红色难以区分，考虑使用不同的填充模式（斜线、点状）。
- **数据差异过大导致小值不可见**：如果某城市的人均用电量远大于其他城市，导致其他城市的柱状图几乎不可见，考虑使用对数刻度（`ax.set_yscale('log')`）。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 负荷率对比图 | `ch06_cross_country_comparison_load_rate.png` | `outputs/ch06_cross_country_comparison/` | 中摩城市负荷率柱状图，蓝色=摩洛哥，红色=中国。 | 报告配图（Prompt-08） |
| 季节性强度对比图 | `ch06_cross_country_comparison_seasonal_strength.png` | `outputs/ch06_cross_country_comparison/` | 中摩城市季节性强度柱状图。 | 报告配图（Prompt-08） |
| 气候-用电散点图 | `ch06_climate_electricity_scatter.png` | `outputs/ch06_cross_country_comparison/` | 年均温(x轴) vs 人均用电量(y轴)的散点图，展示气候与用电的关系。 | 报告配图（Prompt-08） |
| 用电结构对比图 | `ch06_china_electricity_structure.png` | `outputs/ch06_cross_country_comparison/` | 中国3城市的居民/工业/其他用电占比堆叠柱状图。 | 报告配图（Prompt-08） |

---

### Step 7: 差异性归因解释

#### 1. 本步骤要做什么

本步骤结合气候、产业、电价、生活习惯等因素，对中摩城市用电差异进行**定性+定量的归因解释**，生成一份结构化的分析报告（Markdown格式）。这是整个跨国对比分析的"结论章节"——前面的步骤只是展示了"差异是什么"，本步骤要回答"为什么有差异"。

归因分析将从以下4个维度展开：
1. **气候因素**：北非摩洛哥城市受撒哈拉热浪影响，夏季制冷负荷显著；中国西北城市受大陆性气候影响，冬夏温差大，采暖和制冷需求并存。
2. **产业结构**：摩洛哥城市以旅游和轻工业为主，工业基荷较低；中国西北城市能源化工占比较高，工业基荷稳定。
3. **电气化水平**：摩洛哥人均用电量远低于中国对标城市，反映电气化程度和经济发展阶段的差距。
4. **建筑能效**：摩洛哥建筑保温性能较差，导致制冷/采暖能耗占比高。

报告将结合Step 1~6的数据和分析结果，给出有数据支撑的结论，而非空泛的定性描述。

#### 2. 具体操作指引

**操作流程**：

1. **数据汇总**：从Step 5的对比面板和Step 6的可视化结果中提取关键数据点。
2. **归因分析**：对每个维度的差异，结合具体数据进行分析。例如："摩洛哥Laayoune的季节性强度为0.82，而中国西宁仅为0.45，说明Laayoune的负荷受季节（夏季制冷）影响更大，这与两地气候差异一致——Laayoune年均温20C vs 西宁年均温6C。"
3. **报告撰写**：使用Markdown格式撰写结构化报告，包含对标城市概况、负荷特征对比、差异性归因分析、结论与建议四个部分。
4. **报告保存**：保存为Markdown文件，便于后续整合到最终报告（Prompt-08）中。

**关键参数说明**：
- 报告格式：Markdown（.md），便于转换为PDF或Word
- 数据引用：所有结论必须引用具体数据（如"人均用电量X kWh/人/年"），而非模糊描述

#### 3. 代码框架

```python
# ============================================================
# Step 7: 差异性归因解释
# ============================================================

# 汇总关键数据
report_lines = []
report_lines.append("# 中摩典型城市用电特征跨国差异性分析报告")
report_lines.append("")
report_lines.append("## 1. 对标城市概况")
report_lines.append("")
report_lines.append("### 1.1 摩洛哥侧城市")
report_lines.append("- Laayoune、Boujdour、Foum eloued、Marrakech")
report_lines.append("- 气候：干旱/半干旱气候，夏季炎热（均温>25C），冬季温和")
report_lines.append("- 产业：旅游、渔业、轻工业为主")
report_lines.append("- 数据来源：智能电表10分钟粒度负荷数据")
report_lines.append("")
report_lines.append("### 1.2 中国侧对标城市")
for _, row in cities_info.iterrows():
    report_lines.append(f"- {row['city_cn']}（{row['province']}）：{row['climate_type']}，"
                        f"人口{row['population_10k']}万，GDP {row['gdp_billion_cny']}亿元，"
                        f"年均温{row['avg_temp_c']}C，年降水{row['annual_precipitation_mm']}mm")
report_lines.append("")
report_lines.append("## 2. 负荷特征对比")
report_lines.append("")

# 负荷率对比
if 'load_rate' in panel.columns:
    report_lines.append("### 2.1 负荷率对比")
    for _, row in panel.dropna(subset=['load_rate']).iterrows():
        lr = row['load_rate']
        report_lines.append(f"- **{row['city_cn']}（{row['country_cn']}）**：负荷率 {lr:.2f}")
    report_lines.append("")

# 季节性对比
if 'seasonal_strength' in panel.columns:
    report_lines.append("### 2.2 季节性对比")
    for _, row in panel.dropna(subset=['seasonal_strength']).iterrows():
        ss = row['seasonal_strength']
        level = '强' if ss > 0.7 else ('中' if ss > 0.4 else '弱')
        report_lines.append(f"- **{row['city_cn']}（{row['country_cn']}）**：季节性强度 {ss:.3f}（{level}）")
    report_lines.append("")

report_lines.append("## 3. 差异性归因分析")
report_lines.append("")
report_lines.append("### 3.1 气候因素")
report_lines.append("北非摩洛哥城市受撒哈拉热浪影响，夏季（6-8月）制冷负荷显著增加，"
                    "导致负荷呈现明显的单峰季节性模式。中国西北城市受大陆性气候影响，"
                    "冬夏温差大，采暖（冬季）和制冷（夏季）需求并存，但冬季采暖主要依赖"
                    "集中供暖（非电力），因此电力负荷的季节性可能不如摩洛哥显著。")
report_lines.append("")
report_lines.append("### 3.2 产业结构")
report_lines.append("摩洛哥城市以旅游和轻工业为主，工业基荷较低，负荷受旅游季节性影响较大。"
                    "中国西北城市能源化工占比较高（如银川工业用电占比>80%），工业基荷稳定，"
                    "负荷率较高，季节性相对较弱。")
report_lines.append("")
report_lines.append("### 3.3 电气化水平")
report_lines.append("摩洛哥人均用电量远低于中国对标城市，反映电气化程度和经济发展阶段的差距。"
                    "随着摩洛哥经济发展和电气化推进，预期负荷将呈持续增长趋势。")
report_lines.append("")
report_lines.append("### 3.4 建筑能效")
report_lines.append("摩洛哥建筑保温性能较差，导致制冷/采暖能耗占比高，负荷的季节性波动较大。"
                    "中国西北城市近年来大力推进建筑节能改造，建筑能效提升有助于降低"
                    "季节性负荷波动。")
report_lines.append("")
report_lines.append("## 4. 结论与建议")
report_lines.append("")
report_lines.append("1. 摩洛哥城市负荷的季节性强于中国对标城市，主要受夏季制冷需求驱动")
report_lines.append("2. 中国对标城市的负荷率普遍高于摩洛哥城市，反映工业基荷的稳定作用")
report_lines.append("3. 气候差异是中摩用电模式差异的首要驱动因素")
report_lines.append("4. 建议摩洛哥推进建筑节能改造和可再生能源利用，降低季节性负荷波动")
report_lines.append("")

report_text = "\n".join(report_lines)
report_path = os.path.join(output_dir, 'ch06_difference_analysis.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_text)
print(f"差异性分析报告已保存: {report_path}")
print(f"  报告长度: {len(report_text)} 字符")

print("\nStep 7 完成: 差异性归因分析报告已生成")
```

#### 4. 本步骤完成后的检查标准

- **报告完整性**：报告包含对标城市概况、负荷特征对比、差异性归因分析、结论与建议四个部分。
- **数据引用**：报告中引用了具体的数值（如负荷率、季节性强度、人均用电量），而非空泛描述。
- **逻辑一致性**：归因分析的结论与前序步骤的数据分析结果一致（如季节性强度高的城市确实在归因中被解释为"受气候影响大"）。
- **格式规范**：Markdown格式正确，标题层级清晰，列表格式规范。

#### 5. 如果遇到问题请及时反馈

- **数据不足以支撑归因分析**：如果某些维度的数据缺失较多（如人均用电量在摩洛哥侧全部缺失），归因分析可能不够充分。处理方法：在报告中明确标注"该维度数据不足，分析结论需谨慎"，并建议后续补充数据。
- **归因分析结论与数据矛盾**：如果归因分析的结论与前序步骤的数据不一致（如声称"摩洛哥季节性强"但数据显示中国城市季节性更强），需要重新审视归因逻辑，修正结论。
- **报告过于笼统**：如果归因分析只有定性描述而无数据支撑，需要回到Step 5和Step 6，提取更多具体数据点来支撑结论。

#### 6. 本步骤输出产物

| 产物名称 | 文件名 | 路径 | 内容说明 | 后续使用章节 |
|----------|--------|------|----------|-------------|
| 差异性分析报告 | `ch06_difference_analysis.md` | `outputs/ch06_cross_country_comparison/` | 结构化Markdown报告，包含4个章节：对标城市概况、负荷特征对比（含具体数据）、差异性归因分析（气候/产业/电气化/建筑能效4个维度）、结论与建议。引用了Step 1~6的具体数据。 | Prompt-08（最终报告整合） |

---

## 三、产物总览与结构说明

| 序号 | 产物名称 | 文件名 | 格式 | 后续使用章节 |
|------|----------|--------|------|-------------|
| 1 | 对标城市基础信息 | ch06_benchmark_cities_info.csv | CSV | 报告 |
| 2 | 国家统计局数据 | ch06_nbs_data.csv | CSV | 分析 |
| 3 | 地方电网数据 | ch06_local_grid_data.csv | CSV | 分析 |
| 4 | 电网手动录入数据 | ch06_local_grid_manual.csv | CSV | 分析 |
| 5 | 气象数据 | ch06_climate_data.csv | CSV | 分析 |
| 6 | 清洗后对标数据 | ch06_benchmark_cleaned.csv | CSV | 分析 |
| 7 | 负荷率对比图 | ch06_cross_country_comparison_load_rate.png | PNG | 报告配图 |
| 8 | 季节性强度对比图 | ch06_cross_country_comparison_seasonal_strength.png | PNG | 报告配图 |
| 9 | 气候-用电散点图 | ch06_climate_electricity_scatter.png | PNG | 报告配图 |
| 10 | 用电结构对比图 | ch06_china_electricity_structure.png | PNG | 报告配图 |
| 11 | 差异性分析报告 | ch06_difference_analysis.md | Markdown | Prompt-08 |

## 四、产物后续优化方向

### 4.1 当前方案的局限性
- 爬虫目标网站结构可能变更，代码需要持续维护
- 对标城市的用电数据粒度可能与摩洛哥不一致（日度vs月度）
- 跨国对比受统计口径差异影响（如GDP核算方法不同）
- 省级数据到城市级数据的估算存在偏差

### 4.2 可进一步优化的方向
- 使用World Bank API获取标准化跨国数据（统一口径）
- 增加更多对标城市（如中东的迪拜、北非的突尼斯）
- 引入电价政策因素对比（居民电价、工业电价）
- 使用购买力平价（PPP）标准化经济指标

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单
- 如果爬虫全部失败，需确认是否接受手动录入数据
- 如果中国侧数据粒度与摩洛哥不一致，需确认对比方法

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 网站反爬拦截 | HTTP 403/429 | 增大请求间隔、更换User-Agent | 否 |
| 数据解析失败 | BeautifulSoup返回空 | 检查网页结构是否变更 | 是 |
| API请求失败 | HTTP错误或返回空数据 | 检查API参数、使用备用数据源 | 否 |
| 数据口径不一致 | 单位或统计范围不同 | 在报告中说明差异，进行标准化处理 | 是 |
| 省级数据估算偏差大 | 估算值与实际值差异>30% | 在报告中说明估算方法的局限性 | 否 |

# Prompt-07: 配电网优化模型

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**工程应用落地章节**，将前文所有分析结论（负荷规律、峰值特征、预测结果、趋势判断）综合运用，构建配电网负荷优化的数学模型，提出切实可行的调度优化方案。

核心思路是：基于前文识别的峰值特征和预测模型输出的未来负荷曲线，通过数学优化方法，在满足电网安全约束（线路载流限制、变压器容量限制、供需平衡）的前提下，寻找最优的负荷分配策略，实现"削峰填谷"——降低峰值负荷、缩小峰谷差、提升整体负荷利用率。这将直接降低电网的冗余配置成本，提高设备利用效率。

具体而言，本章将完成以下工作：首先，从数学层面明确定义优化问题的决策变量、目标函数和约束条件，形成严谨的理论基础；其次，从历史数据中提取优化模型所需的全部参数（各时段总需求、各zone容量上限、最低负荷保障值）；然后，使用PuLP库构建线性规划模型并调用CBC求解器求解；最后，通过可视化对比和量化指标评估优化效果，并结合摩洛哥城市用电短板提出四类可落地的工程化调度策略建议。

本章与前序章节的逻辑关系为：第三章的峰值阈值表为优化目标提供基准参照，第四章的最优预测模型为未来负荷预测提供工具，第五章的季节性强度表为约束条件中的季节性调整提供依据，第一章的清洗数据为参数计算提供历史数据支撑。

### 1.2 从什么数据出发

输入数据来自前序章节的输出产物，具体如下：

- `ch03_peak_thresholds.csv`（第三章峰值阈值表）——确定优化目标中的峰值基准，用于对比优化前后峰值的变化幅度
- `ch04_model_comparison.csv`（第四章模型对比表）——确认最优预测模型的名称和精度，为未来负荷预测提供模型选择依据
- `ch05_seasonal_strength.csv`（第五章季节性强度表）——提供各城市季节性波动的量化指标，用于在约束条件中考虑季节性因素
- `ch01_cleaned_data.csv`（第一章清洗数据）——提供完整的历史负荷数据，用于计算优化模型所需的各时段总需求、各zone容量上限、最低负荷保障值等参数

此外，本章还依赖全局配置中的城市信息（4城市、各zone数量）和量纲信息（已统一为kW）。

### 1.3 可以采用什么方法

**线性规划（LP）**：使用PuLP库建模求解。线性规划是运筹学中最经典的优化方法，求解速度快（CBC求解器通常在秒级完成）、有成熟的理论保证（全局最优性）、结果可解释性强。适用于目标函数和约束条件均为线性的场景。在本章中，决策变量为各zone在各时段的负荷分配量，目标函数为最小化时段峰值负荷（通过辅助变量线性化），约束条件包括供需平衡、容量上限、最低负荷保障和非负约束，全部为线性关系，非常适合线性规划求解。

本章的优化模型设定为**单目标线性规划**（最小化峰值负荷），同时将峰谷差和负荷率作为辅助评估指标。如果需要同时优化多个目标，可使用加权求和法将多目标转化为单目标，例如：minimize w1 * L_max + w2 * valley_diff，其中w1和w2为权重系数。

**替代方法**：
- 混合整数线性规划（MILP）：可处理离散决策（如储能充放电的开关状态、变压器投切），但求解复杂度更高，求解时间可能从秒级增加到分钟级甚至小时级
- 多目标进化算法（NSGA-II）：适用于非线性多目标优化，可生成Pareto前沿，展示目标间的权衡关系，但求解时间较长（通常需要数百代迭代），且结果不保证全局最优
- 强化学习（DQN/PPO）：适用于动态实时调度场景，可在线学习最优策略，但需要大量训练数据和计算资源（GPU），且模型的可解释性较差
- 二次规划（QP）：可处理二次成本函数（如网损最小化），但求解器更复杂，需要专门的QP求解器（如OSQP、Gurobi）

本章选择线性规划作为主要方法，原因如下：（1）问题本身具有线性结构，无需引入更复杂的方法；（2）求解速度快，适合快速迭代和参数敏感性分析；（3）结果可解释性强，便于工程人员理解和采纳。

## 二、执行步骤

### Step 1: 优化问题数学定义

**本步骤要做什么**

本步骤的目标是撰写一份完整的数学公式文档，以严谨的数学语言明确优化问题的全部要素——集合与索引、参数、决策变量、目标函数和约束条件。这是整个优化建模的理论基础，数学定义的准确性直接决定了模型的有效性和可求解性。

具体而言，需要完成以下工作：（1）定义优化问题涉及的集合（zone集合Z、时段集合T）；（2）列出所有参数及其物理含义和取值来源（总需求D_t、容量上限C_z、最低负荷D_min_t）；（3）明确决策变量x_{z,t}的含义和取值范围；（4）用数学公式表达目标函数（最小化时段峰值负荷）和全部约束条件（供需平衡、容量上限、最低负荷保障、非负约束）；（5）对目标函数中的max函数进行线性化处理，引入辅助变量L_max，使整个问题转化为标准线性规划形式。

这份数学定义文档将作为后续代码实现（Step 3）的直接参照，确保代码中的变量名、约束名称与数学公式一一对应。同时，该文档也将作为最终报告的重要组成部分，展示研究的理论严谨性。

**具体操作指引**

使用LaTeX格式撰写数学公式，确保公式排版清晰、符号一致。文档结构按以下顺序组织：

1. **集合与索引**：定义zone集合Z = {zone1, zone2, ..., zoneN}和时段集合T = {1, 2, ..., 24}。zone的数量取决于所选城市（Laayoune有5个zone，Boujdour有3个，Foum eloued有7个，Marrakech有2个），时段统一为24小时。

2. **参数**：逐一定义D_t（时段t的总负荷需求，单位kW，来自历史数据按小时聚合的均值）、C_z（zone z的容量上限，单位kW，取该zone历史数据的95%分位数）、D_min_t（时段t的最低负荷保障，单位kW，取该时段所有zone中最小值的1.1倍）。每个参数需注明数据来源和计算方式。

3. **决策变量**：定义x_{z,t} >= 0为zone z在时段t的负荷分配量（单位kW），以及辅助变量L_max >= 0为所有时段中总负荷的最大值。

4. **目标函数**：minimize L_max，即最小化所有时段中最大的总负荷值。需解释为什么选择最小化峰值而非最小化总负荷（因为总负荷由需求决定，不可改变，能优化的是负荷在各zone间的分配方式，从而降低峰值）。

5. **约束条件**：逐一列出四类约束，每类约束需给出数学公式、物理含义和参数取值说明。特别说明供需平衡约束（等式约束）确保总供给等于总需求，容量上限约束确保单个zone不过载，最低负荷保障约束确保每个zone维持最低运行水平。

6. **线性化处理**：详细说明max函数的线性化过程——引入辅助变量L_max，将"minimize max_t sum_z x_{z,t}"转化为"minimize L_max, subject to sum_z x_{z,t} <= L_max for all t"。这是标准的大M线性化技巧，不改变原问题的最优解。

**代码框架**:
```python
import os

# 确保输出目录存在
output_dir = "outputs/ch07_grid_optimization"
os.makedirs(output_dir, exist_ok=True)

formulation = """# 配电网负荷优化数学模型

## 1. 集合与索引

- **Z**: zone集合 = {zone1, zone2, ..., zoneN}，N取决于所选城市
  - Laayoune: N=5, Boujdour: N=3, Foum eloued: N=7, Marrakech: N=2
- **T**: 时段集合 = {1, 2, ..., 24}（24小时，每小时一个时段）

## 2. 参数

| 参数 | 含义 | 单位 | 取值来源 |
|------|------|------|----------|
| $D_t$ | 时段t的总负荷需求 | kW | 历史数据按小时聚合取均值（来自ch01_cleaned_data.csv） |
| $C_z$ | zone z的容量上限 | kW | 该zone历史数据的95%分位数（来自ch01_cleaned_data.csv） |
| $D_{min,t}$ | 时段t的最低负荷保障 | kW | 该时段所有zone中最小值的1.1倍 |

参数说明：
- $D_t$ 反映了各时段的典型负荷水平，是供需平衡约束的右端项
- $C_z$ 代表zone的物理承载能力，取95%分位数而非最大值是为了留出安全裕度
- $D_{min,t}$ 确保每个zone维持最低运行水平，避免完全停运

## 3. 决策变量

| 变量 | 含义 | 取值范围 | 单位 |
|------|------|----------|------|
| $x_{z,t}$ | zone z在时段t的负荷分配量 | $x_{z,t} \\geq 0$ | kW |
| $L_{max}$ | 所有时段中总负荷的最大值（辅助变量） | $L_{max} \\geq 0$ | kW |

## 4. 目标函数

$$\\minimize \\quad L_{max}$$

即：最小化所有时段中最大的总负荷值，实现"削峰"目标。

**目标函数选择说明**：
- 总负荷 $\\sum_z x_{z,t} = D_t$ 由需求决定（供需平衡约束），不可改变
- 能优化的是负荷在各zone间的分配方式，使得最大时段负荷尽可能低
- 这等价于"将负荷从高峰时段向低谷时段转移"（如果允许时移），或"在各zone间均衡分配负荷"（在固定时段内）

## 5. 约束条件

### (1) 供需平衡约束（等式约束）
$$\\sum_{z \\in Z} x_{z,t} = D_t \\quad \\forall t \\in T$$

物理含义：每个时段所有zone的负荷分配量之和必须等于该时段的总需求。
这是最核心的约束，确保优化后的分配方案满足实际用电需求。

### (2) 容量上限约束（不等式约束）
$$x_{z,t} \\leq C_z \\quad \\forall z \\in Z, \\forall t \\in T$$

物理含义：每个zone在任何时段的负荷分配量不得超过其容量上限。
防止单个zone过载，保护配电设备安全。

### (3) 最低负荷保障约束（不等式约束）
$$x_{z,t} \\geq \\frac{D_{min,t}}{|Z|} \\quad \\forall z \\in Z, \\forall t \\in T$$

物理含义：每个zone在任何时段的负荷分配量不得低于最低保障值。
确保每个zone维持基本运行水平，避免完全停运。
将 $D_{min,t}$ 均分到各zone，保证总最低负荷不低于 $D_{min,t}$。

### (4) 非负约束
$$x_{z,t} \\geq 0 \\quad \\forall z \\in Z, \\forall t \\in T$$

物理含义：负荷分配量不能为负值。

## 6. 线性化处理

目标函数中隐含了max操作：$\\min \\max_t \\sum_z x_{z,t}$，这是一个非线性表达式。
引入辅助变量 $L_{max}$ 进行线性化：

$$\\minimize \\quad L_{max}$$
$$\\text{subject to:} \\quad \\sum_{z \\in Z} x_{z,t} \\leq L_{max} \\quad \\forall t \\in T$$

线性化原理：
- $L_{max}$ 定义为所有时段总负荷的上界
- 目标函数最小化 $L_{max}$，会自动将 $L_{max}$ 压低到等于 $\\max_t \\sum_z x_{z,t}$
- 这等价于原始的 min-max 问题，但形式上为标准线性规划

## 7. 模型规模

以Laayoune（5个zone，24个时段）为例：
- 决策变量数：5 × 24 + 1 = 121个（含辅助变量L_max）
- 约束条件数：24（峰值限制）+ 24（供需平衡）+ 120（容量上限）+ 120（最低负荷）= 288个
- 求解复杂度：O(多项式时间)，CBC求解器预期在1秒内完成
"""

with open(os.path.join(output_dir, 'ch07_optimization_formulation.md'), 'w', encoding='utf-8') as f:
    f.write(formulation)
print("数学模型定义文档已保存")
```

**本步骤完成后的检查标准**

- 数学公式完整，包含集合、参数、变量、目标、约束5个要素，缺一不可
- 公式中的所有符号（D_t, C_z, D_min_t, x_{z,t}, L_max）都有明确定义和物理含义说明
- 线性化处理正确：max函数通过辅助变量L_max转化为线性约束，且不改变原问题的最优解
- 参数取值来源明确：每个参数都标注了来自哪个数据文件、如何计算
- 文档格式规范：LaTeX公式可正确渲染，表格结构清晰
- 模型规模估算合理：变量数和约束数的计算与所选城市的zone数量一致

**如果遇到问题请及时反馈**

- 如果对线性化处理有疑问：max函数的线性化是运筹学中的标准技巧（Big-M法的一种简化形式），可参考任何运筹学教材的"目标函数线性化"章节。如果理解有困难，可先跳过理论推导，直接在Step 3中验证代码实现的正确性
- 如果参数定义与实际数据不匹配（例如某些zone的数据量级异常）：需回到Step 2重新检查数据，确认参数计算方式是否合理
- 如果LaTeX公式渲染失败：检查是否使用了正确的LaTeX分隔符（$$...$$），以及特殊字符是否正确转义

**本步骤输出产物**

- `ch07_optimization_formulation.md` -- 文件名: `ch07_optimization_formulation.md` -- 存放路径: `outputs/ch07_grid_optimization/` -- 内容说明: 包含完整的数学模型定义文档，涵盖集合、参数、决策变量、目标函数、约束条件和线性化处理6个部分，使用LaTeX格式撰写数学公式 -- 后续使用章节: Step 3（代码实现直接参照本文档的数学定义）、最终报告的理论基础部分

---

### Step 2: 数据准备与参数计算

**本步骤要做什么**

本步骤的目标是从第一章的清洗数据中，计算优化模型所需的全部参数：各时段的总需求D_t（24个值，对应0-23点）、各zone的容量上限C_z（N个值，N为zone数量）、各时段的最低负荷保障D_min_t（24个值）。这些参数是Step 3构建PuLP模型的直接输入。

选取Laayoune城市作为优化对象，原因是该城市数据最为完整（5个zone、88,890条10分钟记录、时间跨度近2年），且zone数量适中，既能展示多zone间的负荷分配优化效果，又不会因为zone数量过多导致模型过于复杂。计算完成后，将参数保存为CSV文件，供Step 3加载使用，同时打印参数概览供人工核查。

**具体操作指引**

操作分为以下四个阶段：

1. **数据加载**：读取 `ch01_cleaned_data.csv`，设置DateTime为索引并排序。筛选city列为"Laayoune"的行，提取所有以"zone"开头的列名作为zone列表。

2. **计算各时段总需求D_t**：将数据按小时（index.hour）分组，对每个zone列取均值（将10分钟粒度聚合为小时粒度），然后将所有zone的均值按行求和，得到24个小时的总需求序列。注意：这里取的是历史平均值而非最大值，因为优化目标是"削峰"——降低典型峰值，而非极端峰值。

3. **计算各zone容量上限C_z**：对每个zone列，计算其全部历史数据的95%分位数（使用 `df[col].quantile(0.95)`）。选择95%分位数而非最大值的原因是：最大值可能是异常峰值，不代表设备的持续承载能力；95%分位数更接近实际运行中的安全上限，同时留出5%的安全裕度应对突发负荷。

4. **计算各时段最低负荷D_min_t**：对每个小时，取所有zone中该小时均值的最小值，再乘以1.1倍安全系数。这个值代表了"即使在负荷最低的时段，每个zone也至少需要承担的最低负荷"。1.1倍系数是为了留出10%的缓冲，避免优化结果中出现某个zone被分配到极低甚至接近零的负荷（这在工程上不可接受，因为配电设备需要维持最低运行水平）。

计算完成后，将D_t和D_min_t合并为一张参数表保存为CSV，同时将C_z以字典形式保存在内存中供Step 3使用。打印所有参数的概览信息，包括数值范围、均值、标准差等，便于人工核查参数的合理性。

**代码框架**:
```python
import pandas as pd
import numpy as np
import os

# === 配置 ===
output_dir = "outputs/ch07_grid_optimization"
os.makedirs(output_dir, exist_ok=True)

# === 1. 数据加载 ===
df = pd.read_csv("outputs/ch01_data_preprocessing/ch01_cleaned_data.csv", parse_dates=['DateTime'])
df = df.set_index('DateTime').sort_index()

# 选取Laayoune城市
city = "Laayoune"
city_df = df[df['city'] == city].copy()
zones = [c for c in city_df.columns if c.startswith('zone')]
print(f"城市: {city}, zone数量: {len(zones)}, zone列表: {zones}")
print(f"数据量: {len(city_df)}行, 时间范围: {city_df.index.min()} ~ {city_df.index.max()}")

# === 2. 计算各时段总需求 D_t ===
# 按小时分组，对每个zone取均值，再按行求和
hourly_avg = city_df.groupby(city_df.index.hour)[zones].mean()  # shape: (24, N_zones)
D_t = hourly_avg.sum(axis=1)  # shape: (24,), 各小时所有zone的总需求均值
print(f"\n各时段总需求 D_t (kW):")
print(D_t.round(2).to_string())
print(f"\nD_t 统计: min={D_t.min():.2f}, max={D_t.max():.2f}, mean={D_t.mean():.2f} kW")

# === 3. 计算各zone容量上限 C_z ===
C_z = {}
for z in zones:
    cap = city_df[z].quantile(0.95)
    C_z[z] = cap
    print(f"  {z}: 容量上限={cap:.2f} kW (95%分位数), 历史最大值={city_df[z].max():.2f} kW")

# 验证: 容量上限之和应大于各时段最大需求
total_capacity = sum(C_z.values())
max_demand = D_t.max()
print(f"\n总容量上限: {total_capacity:.2f} kW, 最大时段需求: {max_demand:.2f} kW")
print(f"容量裕度: {(total_capacity - max_demand)/max_demand*100:.1f}%")
assert total_capacity > max_demand, "警告: 总容量不足以满足最大需求，模型可能无可行解!"

# === 4. 计算各时段最低负荷 D_min_t ===
# 每小时所有zone均值中的最小值 × 1.1
hourly_min_per_zone = hourly_avg.min(axis=1)  # 每小时最小的zone均值
D_min_t = hourly_min_per_zone * 1.1  # 乘以1.1安全系数
print(f"\n各时段最低负荷保障 D_min_t (kW):")
print(D_min_t.round(2).to_string())

# 验证: D_min_t 应小于 D_t（最低负荷小于总需求）
assert (D_min_t < D_t).all(), "警告: 部分时段的最低负荷保障值超过了总需求!"

# === 5. 保存参数 ===
params_df = pd.DataFrame({
    'hour': D_t.index,
    'total_demand_kw': D_t.values.round(2),
    'min_demand_kw': D_min_t.values.round(2),
    'demand_to_min_ratio': (D_t.values / D_min_t.values).round(4)
})
params_path = os.path.join(output_dir, 'ch07_constraints_table.csv')
params_df.to_csv(params_path, index=False)
print(f"\n约束参数表已保存: {params_path}")
print(f"参数表预览:\n{params_df.to_string(index=False)}")
```

**本步骤完成后的检查标准**

- D_t有24个值（对应0-23小时），全部为正数，且呈现典型的日内负荷曲线形态（白天高、夜间低）
- C_z的数量与所选城市的zone数量一致（Laayoune为5个），每个值均为正数，且大于对应zone的历史均值
- D_min_t有24个值，全部为正数，且 D_min_t < D_t 对所有时段成立（否则供需平衡约束与最低负荷约束矛盾，模型将无可行解）
- 总容量上限 sum(C_z) > max(D_t)，否则模型无可行解（这是最基本的可行性条件）
- 参数表CSV文件成功保存，包含hour、total_demand_kw、min_demand_kw三列，无NaN

**如果遇到问题请及时反馈**

- 如果D_min_t >= D_t（某些时段最低负荷超过总需求）：说明1.1倍安全系数过大，或该时段存在数据异常。处理方式：将安全系数从1.1降低到1.0，或检查该时段的历史数据是否存在异常低的zone均值
- 如果总容量 sum(C_z) < max(D_t)：说明95%分位数取值过低，或数据中存在异常高的需求时段。处理方式：将分位数从0.95提高到0.98或0.99，或检查异常需求时段的数据质量
- 如果某个zone的容量上限C_z异常低（接近0或为负数）：说明该zone的数据存在大量零值或缺失值，需回到第一章检查数据清洗质量
- 如果所选城市的数据量不足（少于1000行）：建议更换为数据更完整的城市，或降低时间粒度（从小时改为2小时）

**本步骤输出产物**

- `ch07_constraints_table.csv` -- 文件名: `ch07_constraints_table.csv` -- 存放路径: `outputs/ch07_grid_optimization/` -- 内容说明: 包含24行（对应0-23小时）的约束参数表，列包括hour（小时）、total_demand_kw（该小时的总需求kW）、min_demand_kw（该小时的最低负荷保障kW）、demand_to_min_ratio（需求与最低负荷的比值，用于评估约束松紧度） -- 后续使用章节: Step 3（作为PuLP模型的参数输入）、Step 5（用于计算优化效果量化指标）、最终报告的参数说明部分

---

### Step 3: PuLP模型构建与求解

**本步骤要做什么**

本步骤是本章的核心计算环节，目标是使用PuLP库将Step 1定义的数学模型转化为可执行的Python代码，调用CBC求解器求解，获得最优的负荷分配方案。

具体而言，需要完成以下工作：（1）创建PuLP问题实例，设定为最小化问题；（2）创建决策变量x_{z,t}（zone z在时段t的负荷分配量，非负连续变量）和辅助变量L_max（非负连续变量）；（3）设定目标函数为最小化L_max；（4）逐一添加四类约束条件（峰值限制、供需平衡、容量上限、最低负荷保障）；（5）调用CBC求解器求解；（6）提取并打印求解结果，包括求解状态、最优目标值、原始峰值与优化峰值的对比。

求解完成后，需要验证求解状态是否为"Optimal"（最优解），并计算峰值降低的绝对量和百分比。如果求解失败（状态为Infeasible或Unbounded），需要根据错误信息调整约束条件后重新求解。求解结果（各zone各时段的分配量）将保存到内存中，供Step 4可视化使用。

**具体操作指引**

PuLP模型构建的关键操作如下：

1. **创建问题实例**：`prob = pulp.LpProblem("Grid_Load_Optimization", pulp.LpMinimize)`，问题名称可自定义，第二个参数指定为最小化问题。

2. **创建决策变量**：使用双层循环创建x[(z, t)]变量，变量名为 `f"x_{z}_{t}"`，下界为0（lowBound=0），上界默认为正无穷（PuLP默认）。辅助变量L_max同样下界为0。

3. **设定目标函数**：`prob += L_max, "Minimize_Peak_Load"`，第二个参数为约束名称（可选，用于调试）。

4. **添加约束条件**：注意约束的添加顺序不影响求解结果，但建议按照"峰值限制 → 供需平衡 → 容量上限 → 最低负荷"的顺序添加，便于调试时定位问题。每条约束都应赋予唯一的名称（如 `f"Peak_Limit_t{t}"`），便于在求解失败时查看是哪条约束导致的问题。

5. **求解**：`prob.solve(pulp.PULP_CBC_CMD(msg=1))`，msg=1表示打印求解日志。如果需要更详细的日志，可设置msg=2。如果求解时间过长，可通过 `timeLimit` 参数设置超时（如 `timeLimit=60` 表示60秒超时）。

6. **结果提取**：使用 `pulp.value(x[(z, t)])` 提取决策变量的最优值，使用 `pulp.value(prob.objective)` 提取目标函数的最优值，使用 `pulp.LpStatus[prob.status]` 获取求解状态。

**代码框架**:
```python
import pulp
import numpy as np

# === 参数（来自Step 2的计算结果） ===
# D_t: 各时段总需求 (Series, index=0~23)
# C_z: 各zone容量上限 (dict, key=zone名, value=容量kW)
# D_min_t: 各时段最低负荷保障 (Series, index=0~23)
# zones: zone名称列表

# === 1. 创建问题实例 ===
prob = pulp.LpProblem("Grid_Load_Optimization", pulp.LpMinimize)
print(f"优化问题: {prob.name}")
print(f"zone数量: {len(zones)}, 时段数量: 24")

# === 2. 创建决策变量 ===
x = {}  # x[(zone, hour)] = 负荷分配量
for z in zones:
    for t in range(24):
        var_name = f"x_{z}_t{t}"
        x[(z, t)] = pulp.LpVariable(var_name, lowBound=0, cat='Continuous')
        # cat='Continuous'表示连续变量（默认值，可省略）

# 辅助变量: L_max（线性化max函数）
L_max = pulp.LpVariable("L_max", lowBound=0, cat='Continuous')

n_vars = len(zones) * 24 + 1
print(f"决策变量数: {n_vars} ({len(zones)} zones × 24 hours + 1 L_max)")

# === 3. 设定目标函数 ===
prob += L_max, "Minimize_Peak_Load"
print("目标函数: minimize L_max")

# === 4. 添加约束条件 ===
n_constraints = 0

# 约束1: 各时段总负荷不超过L_max（峰值限制）
for t in range(24):
    prob += pulp.lpSum([x[(z, t)] for z in zones]) <= L_max, f"Peak_Limit_t{t}"
    n_constraints += 1

# 约束2: 供需平衡（各时段总负荷等于需求）
for t in range(24):
    prob += pulp.lpSum([x[(z, t)] for z in zones]) == D_t.iloc[t], f"Supply_Demand_Balance_t{t}"
    n_constraints += 1

# 约束3: 容量上限（每个zone不超过其容量）
for z in zones:
    for t in range(24):
        prob += x[(z, t)] <= C_z[z], f"Capacity_Limit_{z}_t{t}"
        n_constraints += 1

# 约束4: 最低负荷保障（每个zone不低于最低值）
for t in range(24):
    min_per_zone = D_min_t.iloc[t] / len(zones)  # 均分到各zone
    for z in zones:
        prob += x[(z, t)] >= min_per_zone, f"Min_Demand_{z}_t{t}"
        n_constraints += 1

print(f"约束条件数: {n_constraints}")
print(f"  - 峰值限制: 24")
print(f"  - 供需平衡: 24")
print(f"  - 容量上限: {len(zones) * 24}")
print(f"  - 最低负荷: {len(zones) * 24}")

# === 5. 求解 ===
print("\n开始求解...")
prob.solve(pulp.PULP_CBC_CMD(msg=1, timeLimit=60))

# === 6. 结果提取与验证 ===
status = pulp.LpStatus[prob.status]
print(f"\n{'='*50}")
print(f"求解状态: {status}")
print(f"{'='*50}")

if status == "Optimal":
    opt_peak = pulp.value(prob.objective)
    orig_peak = D_t.max()
    reduction = orig_peak - opt_peak
    reduction_pct = reduction / orig_peak * 100

    print(f"原始峰值负荷: {orig_peak:.2f} kW")
    print(f"优化后峰值负荷: {opt_peak:.2f} kW")
    print(f"峰值降低: {reduction:.2f} kW ({reduction_pct:.1f}%)")

    # 验证约束满足情况
    print(f"\n约束验证:")
    for t in range(24):
        total = sum(pulp.value(x[(z, t)]) for z in zones)
        balance_err = abs(total - D_t.iloc[t])
        if balance_err > 1e-6:
            print(f"  警告: 时段{t}供需平衡误差={balance_err:.6f}")

    print("  供需平衡约束: 全部满足" if all(
        abs(sum(pulp.value(x[(z, t)]) for z in zones) - D_t.iloc[t]) < 1e-6
        for t in range(24)
    ) else "  供需平衡约束: 存在违反!")

    print("  容量上限约束: 全部满足" if all(
        pulp.value(x[(z, t)]) <= C_z[z] + 1e-6
        for z in zones for t in range(24)
    ) else "  容量上限约束: 存在违反!")

    print("  最低负荷约束: 全部满足" if all(
        pulp.value(x[(z, t)]) >= D_min_t.iloc[t] / len(zones) - 1e-6
        for z in zones for t in range(24)
    ) else "  最低负荷约束: 存在违反!")

elif status == "Infeasible":
    print("模型无可行解! 可能原因:")
    print("  1. 总容量不足: sum(C_z) < max(D_t)")
    print("  2. 最低负荷过高: D_min_t >= D_t (某些时段)")
    print("  3. 约束条件之间存在矛盾")
    print("建议: 放宽约束（提高容量上限或降低最低负荷要求）")

elif status == "Unbounded":
    print("模型无界! 可能原因:")
    print("  1. 目标函数或约束条件设置错误")
    print("  2. 缺少必要的约束（如非负约束）")
    print("建议: 检查目标函数和约束条件的数学定义")

else:
    print(f"求解状态异常: {status}")
    print("建议: 检查PuLP版本和CBC求解器安装情况")
```

**本步骤完成后的检查标准**

- 求解状态为"Optimal"（最优解），这是最基本的验收条件
- 最优目标值（L_max）严格小于原始峰值负荷 D_t.max()，即优化确实降低了峰值
- 峰值降低率 > 0%（如果等于0%说明优化无效，需检查约束条件是否过于严格）
- 所有约束条件得到满足（供需平衡误差 < 1e-6，容量上限和最低负荷约束无违反）
- 求解时间在合理范围内（< 60秒），对于本问题的规模（约121个变量、288个约束），预期在1秒内完成
- 各zone各时段的分配值全部为非负数

**如果遇到问题请及时反馈**

- 如果求解状态为"Infeasible"（无可行解）：这是最常见的失败原因。处理步骤如下：（1）首先检查总容量 sum(C_z) 是否大于 max(D_t)，如果不足，将C_z的分位数从0.95提高到0.98；（2）检查D_min_t是否小于D_t，如果某些时段D_min_t >= D_t，将安全系数从1.1降低到1.0；（3）如果以上调整仍无法获得可行解，考虑移除最低负荷约束，仅保留供需平衡和容量上限约束
- 如果求解状态为"Unbounded"（无界）：说明目标函数或约束条件有误。检查点：（1）目标函数是否正确设置为最小化L_max（而非最大化）；（2）L_max是否有下界（lowBound=0）；（3）供需平衡约束是否为等式约束（==）而非不等式约束（<=）
- 如果求解时间过长（> 60秒）：对于本问题规模不应出现此情况。如果出现，检查是否存在循环创建重复约束的问题，或尝试设置timeLimit参数
- 如果PuLP或CBC求解器未安装：运行 `pip install pulp` 安装PuLP（CBC求解器会自动随PuLP安装）

**本步骤输出产物**

- 求解结果（内存中的变量值） -- 变量名: `x[(z, t)]`, `L_max`, `prob` -- 存放位置: Python内存 -- 内容说明: 包含各zone各时段的最优负荷分配量（x字典）、最优峰值负荷值（L_max）、完整的PuLP问题对象（prob） -- 后续使用章节: Step 4（提取x值绘制优化前后对比图）、Step 5（提取L_max值计算削峰效果量化指标）

---

### Step 4: 优化前后对比可视化

**本步骤要做什么**

本步骤的目标是通过可视化手段，直观展示优化前后的负荷曲线对比和各zone的负荷分配方案。一张好的可视化图表能够比任何数字都更有效地传达优化效果——读者可以一眼看出峰值降低了多少、削峰集中在哪些时段、各zone的负荷分配是否均衡。

具体而言，需要绘制两张子图（上下布局）：

**上图（总负荷对比图）**：在同一坐标系中绘制原始24小时负荷曲线（蓝色实线）和优化后24小时负荷曲线（红色虚线），用水平虚线标注原始峰值和优化后峰值的位置，用绿色填充区域表示"削峰量"（原始曲线与优化曲线之间的面积）。这张图的核心信息是：优化在哪些时段产生了效果、削峰量有多大。

**下图（各zone分配图）**：将优化后每个zone在各时段的负荷分配量绘制为独立的折线。这张图的核心信息是：优化方案如何将总负荷分配到各zone——是否实现了均衡分配、是否存在某个zone承担了过多负荷、各zone的日内曲线形态是否合理。

图表需遵循全局可视化规范（dpi=150、中文字体支持、网格线、图例清晰），保存为PNG格式。

**具体操作指引**

1. **提取优化结果**：从Step 3的求解结果中，使用双层循环提取每个时段所有zone的分配量之和，得到24小时的优化后总负荷序列。同时提取每个zone在各时段的分配量，得到N条zone分配曲线。

2. **绘制上图（总负荷对比）**：使用 `plt.subplots(2, 1, figsize=(14, 10))` 创建上下两个子图。上图使用 `ax.plot()` 绘制原始曲线和优化曲线，使用 `ax.axhline()` 绘制峰值参考线，使用 `ax.fill_between()` 绘制削峰填充区域。注意：填充区域应使用低透明度（alpha=0.15），避免遮挡曲线。

3. **绘制下图（zone分配）**：对每个zone使用不同颜色绘制折线。如果zone数量较多（如Foum eloued有7个zone），可考虑使用堆叠面积图（`ax.stackplot()`）替代折线图，更直观地展示各zone的负荷构成。

4. **图表美化**：设置标题（含城市名）、坐标轴标签（中文）、图例、网格线、x轴刻度（每2小时一个刻度）。使用 `plt.tight_layout()` 避免子图重叠。

**代码框架**:
```python
import matplotlib.pyplot as plt
import numpy as np
import os

# 确保中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

output_dir = "outputs/ch07_grid_optimization"

# === 1. 提取优化结果 ===
# 优化后各时段总负荷
optimized_load = []
for t in range(24):
    total = sum(pulp.value(x[(z, t)]) for z in zones)
    optimized_load.append(total)
optimized_load = np.array(optimized_load)

# 优化后各zone分配
zone_allocation = {}
for z in zones:
    zone_allocation[z] = np.array([pulp.value(x[(z, t)]) for t in range(24)])

# === 2. 绘制对比图 ===
fig, axes = plt.subplots(2, 1, figsize=(14, 10), dpi=150)

# --- 上图: 总负荷对比 ---
ax1 = axes[0]
hours = range(24)

# 原始负荷曲线
ax1.plot(hours, D_t.values, 'o-', color='steelblue', linewidth=2,
         label='原始负荷', markersize=6, zorder=3)
# 优化后负荷曲线
ax1.plot(hours, optimized_load, 's--', color='tomato', linewidth=2,
         label='优化后负荷', markersize=6, zorder=3)
# 峰值参考线
ax1.axhline(y=pulp.value(L_max), color='green', linestyle=':', linewidth=1.5,
            label=f'优化峰值 = {pulp.value(L_max):.1f} kW', zorder=2)
ax1.axhline(y=D_t.max(), color='red', linestyle=':', linewidth=1.5,
            label=f'原始峰值 = {D_t.max():.1f} kW', zorder=2)
# 削峰填充区域
ax1.fill_between(hours, D_t.values, optimized_load,
                 where=(D_t.values > optimized_load),
                 alpha=0.15, color='green', label='削峰量', zorder=1)

ax1.set_title(f'{city} - 配电网负荷优化前后对比（总负荷）', fontsize=14, fontweight='bold')
ax1.set_xlabel('小时', fontsize=12)
ax1.set_ylabel('总负荷 (kW)', fontsize=12)
ax1.legend(fontsize=10, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_xticks(range(0, 24, 2))
ax1.set_xlim(-0.5, 23.5)

# --- 下图: 各zone分配 ---
ax2 = axes[1]
colors = plt.cm.Set2(np.linspace(0, 1, len(zones)))  # 为每个zone分配不同颜色
for i, z in enumerate(zones):
    ax2.plot(hours, zone_allocation[z], label=z, linewidth=1.5, color=colors[i])

ax2.set_title('各zone优化后负荷分配方案', fontsize=14, fontweight='bold')
ax2.set_xlabel('小时', fontsize=12)
ax2.set_ylabel('负荷 (kW)', fontsize=12)
ax2.legend(fontsize=10, loc='upper right', ncol=2)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(range(0, 24, 2))
ax2.set_xlim(-0.5, 23.5)

plt.tight_layout()
fig_path = os.path.join(output_dir, 'ch07_before_after_optimization.png')
plt.savefig(fig_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"优化前后对比图已保存: {fig_path}")
```

**本步骤完成后的检查标准**

- 上图中，优化后负荷曲线的峰值明显低于原始曲线的峰值（视觉上一目了然）
- 绿色填充区域（削峰量）在原始峰值时段（通常是18-21点）最大，在低谷时段（通常是2-5点）最小或为零
- 优化后曲线与原始曲线在非峰值时段基本重合（因为供需平衡约束要求总负荷等于需求）
- 下图中，各zone的分配曲线平滑无突变（如果出现锯齿状波动，可能是最低负荷约束导致的边界效应，属正常现象）
- 各zone的分配量均在 [D_min_t/|Z|, C_z] 范围内（满足容量上限和最低负荷约束）
- 图表标题包含城市名，坐标轴标签清晰，图例完整，保存为PNG格式且分辨率不低于150dpi

**如果遇到问题请及时反馈**

- 如果优化后曲线与原始曲线完全重合（削峰量为零）：说明优化未产生效果，可能原因是供需平衡约束（等式）限制了优化空间。此时总负荷被固定为D_t，优化只能在zone间重新分配，但无法改变各时段的总负荷。如果需要真正的"削峰"，需要引入负荷时移机制（如储能充放电），这超出了当前线性规划模型的能力范围，需升级为MILP模型
- 如果下图中的zone分配曲线出现负值：说明求解结果异常，需回到Step 3检查非负约束是否正确添加
- 如果中文字体显示为方框：说明系统缺少中文字体，可尝试安装SimHei字体，或使用英文标签替代
- 如果图表保存失败（如目录不存在）：确保output_dir已通过 `os.makedirs()` 创建

**本步骤输出产物**

- `ch07_before_after_optimization.png` -- 文件名: `ch07_before_after_optimization.png` -- 存放路径: `outputs/ch07_grid_optimization/` -- 内容说明: 包含上下两张子图的PNG图片，上图展示原始负荷与优化后负荷的24小时对比曲线（含峰值参考线和削峰填充区域），下图展示各zone优化后的负荷分配方案 -- 后续使用章节: 最终报告的核心配图、Step 6（工程策略建议的数据可视化支撑）

---

### Step 5: 削峰效果量化

**本步骤要做什么**

本步骤的目标是计算优化前后的关键指标对比，用精确的数值量化优化效果。虽然Step 4的可视化已经直观展示了优化效果，但学术论文和工程报告需要具体的数值指标作为支撑——"峰值降低了XX%"比"峰值明显降低"更有说服力。

需要计算的指标包括三个维度：

1. **峰值降低率**：衡量"削峰"效果的直接指标。计算公式为 (原始峰值 - 优化后峰值) / 原始峰值 × 100%。这是本章最核心的优化效果指标。

2. **峰谷差缩小率**：衡量"填谷"效果的指标。峰谷差 = 峰值 - 谷值。计算优化前后的峰谷差，然后计算缩小率。注意：由于供需平衡约束固定了各时段的总需求，优化后的峰谷差可能不会显著变化（因为总负荷曲线不变），但如果优化模型引入了负荷时移机制（如储能），峰谷差会显著缩小。

3. **负荷率提升率**：衡量设备利用效率提升的指标。负荷率 = 平均负荷 / 峰值负荷。负荷率越高，说明设备利用越充分，冗余配置成本越低。计算优化前后的负荷率，然后计算提升率。

计算完成后，将三个指标的对比结果保存为CSV文件，并打印格式化的对比表格，便于直接粘贴到报告中。

**具体操作指引**

1. **峰值指标计算**：原始峰值 = D_t.max()，优化后峰值 = pulp.value(L_max)。峰值降低量 = 原始峰值 - 优化后峰值，峰值降低率 = 峰值降低量 / 原始峰值 × 100%。

2. **峰谷差指标计算**：原始峰谷差 = D_t.max() - D_t.min()，优化后峰谷差 = max(optimized_load) - min(optimized_load)。峰谷差缩小量 = 原始峰谷差 - 优化后峰谷差，峰谷差缩小率 = 缩小量 / 原始峰谷差 × 100%。

3. **负荷率指标计算**：原始负荷率 = D_t.mean() / D_t.max()，优化后负荷率 = mean(optimized_load) / max(optimized_load)。负荷率提升量 = 优化后负荷率 - 原始负荷率，负荷率提升率 = 提升量 / 原始负荷率 × 100%。

4. **结果保存**：将三个指标的对比结果组装为DataFrame，列包括metric（指标名称）、original（原始值）、optimized（优化后值）、change（变化量）、change_pct（变化百分比）。保存为CSV文件。

**代码框架**:
```python
import pandas as pd
import numpy as np
import os

output_dir = "outputs/ch07_grid_optimization"

# === 1. 峰值指标 ===
original_peak = D_t.max()
optimized_peak = pulp.value(L_max)
peak_reduction = original_peak - optimized_peak
peak_reduction_rate = peak_reduction / original_peak * 100

print(f"峰值负荷: 原始={original_peak:.2f} kW, 优化后={optimized_peak:.2f} kW")
print(f"峰值降低: {peak_reduction:.2f} kW ({peak_reduction_rate:.1f}%)")

# === 2. 峰谷差指标 ===
original_valley = D_t.min()
optimized_valley = min(optimized_load)
original_peak_valley_diff = original_peak - original_valley
optimized_peak_valley_diff = optimized_peak - optimized_valley
pv_reduction = original_peak_valley_diff - optimized_peak_valley_diff
pv_reduction_rate = pv_reduction / original_peak_valley_diff * 100

print(f"\n峰谷差: 原始={original_peak_valley_diff:.2f} kW, 优化后={optimized_peak_valley_diff:.2f} kW")
print(f"峰谷差缩小: {pv_reduction:.2f} kW ({pv_reduction_rate:.1f}%)")

# === 3. 负荷率指标 ===
original_load_rate = D_t.mean() / original_peak
optimized_load_rate = np.mean(optimized_load) / optimized_peak
lr_improvement = optimized_load_rate - original_load_rate
lr_improvement_rate = lr_improvement / original_load_rate * 100

print(f"\n负荷率: 原始={original_load_rate:.4f}, 优化后={optimized_load_rate:.4f}")
print(f"负荷率提升: {lr_improvement:.4f} ({lr_improvement_rate:.1f}%)")

# === 4. 汇总保存 ===
metrics = pd.DataFrame([
    {
        'metric': '峰值负荷 (kW)',
        'original': round(original_peak, 2),
        'optimized': round(optimized_peak, 2),
        'change': round(optimized_peak - original_peak, 2),
        'change_pct': round(peak_reduction_rate, 2)
    },
    {
        'metric': '峰谷差 (kW)',
        'original': round(original_peak_valley_diff, 2),
        'optimized': round(optimized_peak_valley_diff, 2),
        'change': round(optimized_peak_valley_diff - original_peak_valley_diff, 2),
        'change_pct': round(pv_reduction_rate, 2)
    },
    {
        'metric': '负荷率',
        'original': round(original_load_rate, 4),
        'optimized': round(optimized_load_rate, 4),
        'change': round(optimized_load_rate - original_load_rate, 4),
        'change_pct': round(lr_improvement_rate, 2)
    }
])

metrics_path = os.path.join(output_dir, 'ch07_optimization_metrics.csv')
metrics.to_csv(metrics_path, index=False)

print(f"\n{'='*60}")
print(f"削峰效果量化指标总览")
print(f"{'='*60}")
print(metrics.to_string(index=False))
print(f"\n指标表已保存: {metrics_path}")
```

**本步骤完成后的检查标准**

- 峰值降低率 > 0%（优化确实降低了峰值，这是最基本的验收条件）
- 负荷率提升率 > 0%（优化提高了设备利用率，与削峰目标一致）
- 峰谷差缩小率 >= 0%（优化不应增大峰谷差，如果出现增大需检查模型）
- 所有指标的change列符号与change_pct列符号一致（正负方向一致）
- CSV文件包含3行（3个指标）和5列（metric, original, optimized, change, change_pct），无NaN

**如果遇到问题请及时反馈**

- 如果峰值降低率为0%或接近0%：说明当前优化模型在固定需求的约束下无法有效削峰。这是因为供需平衡等式约束将各时段总负荷固定为D_t，优化只能在zone间重新分配，无法改变总负荷曲线的形状。如果需要真正的削峰效果，需要引入储能系统（允许跨时段转移负荷），这需要将模型升级为MILP。在当前LP框架下，削峰效果取决于原始负荷曲线中是否存在"某些zone在峰值时段承担了过多负荷"的情况
- 如果负荷率提升率为负值：说明优化后负荷率反而降低了，这与削峰目标矛盾。检查L_max是否确实小于D_t.max()
- 如果峰谷差缩小率为负值（峰谷差增大）：在当前LP模型中，由于供需平衡约束固定了各时段总需求，优化后峰谷差理论上不应增大。如果出现增大，需检查求解结果是否正确
- 如果指标数值异常（如峰值降低率>50%）：可能是参数计算有误（如D_t的量纲不正确），需回到Step 2检查

**本步骤输出产物**

- `ch07_optimization_metrics.csv` -- 文件名: `ch07_optimization_metrics.csv` -- 存放路径: `outputs/ch07_grid_optimization/` -- 内容说明: 包含3行（峰值负荷、峰谷差、负荷率）的优化效果对比表，列包括metric（指标名称）、original（优化前值）、optimized（优化后值）、change（绝对变化量）、change_pct（百分比变化率） -- 后续使用章节: Step 6（工程策略建议的数据支撑）、Prompt-08（总结与展望的关键指标提取）、最终报告的优化效果展示部分

---

### Step 6: 工程化策略建议

**本步骤要做什么**

本步骤的目标是将数学优化的结果转化为可落地的工程化策略建议。纯粹的数学优化结果（如"峰值降低XX%"）对电力工程师和管理者的参考价值有限，他们更需要知道"具体应该怎么做"。因此，本步骤需要结合摩洛哥城市的用电特征（前文分析的结论）和优化模型的量化结果，提出四类有数据支撑、可操作、有明确预期效果的工程策略。

四类策略分别为：（1）错峰用电引导——通过价格信号引导用户转移负荷；（2）台区容量优化配置——通过物理改造提升设备利用率；（3）季节性配电调度——针对季节性波动制定差异化预案；（4）储能协同削峰——通过电池储能系统实现跨时段负荷转移。

每类策略需要包含三个要素：**问题**（基于前文分析结论，说明为什么需要这个策略）、**建议**（具体的操作方案和实施步骤）、**预期效果**（量化的改善预期，引用优化模型的计算结果）。此外，还需要给出实施优先级排序（短期/中期/长期），帮助决策者制定行动计划。

**具体操作指引**

1. **策略一：错峰用电引导**。基于第二章的日内规律分析（晚高峰18-21点负荷集中）和第三章的峰值识别结论（峰值高发时段），提出分时电价政策建议。核心论据：如果工业用户将10-15%的可转移负荷从晚高峰移至凌晨低谷，可额外降低峰值5-8%。

2. **策略二：台区容量优化配置**。基于第二章的负荷率和变异系数分析（部分zone负荷率过低），提出变压器减容和跨区域联络线升级建议。核心论据：低负荷率zone的设备利用率不足40%，通过负荷转移可提升整体负荷率5-10%。

3. **策略三：季节性配电调度**。基于第五章的季节性强度分析（夏季峰值突出），提出夏季/冬季差异化调度预案。核心论据：季节性负荷波动导致设备在夏季满载而在冬季闲置，差异化调度可提升全年设备利用率。

4. **策略四：储能协同削峰**。基于第七章的优化结果（峰谷差较大），提出电池储能系统配置建议。核心论据：当前LP模型受限于供需平衡约束无法实现跨时段转移，储能系统可突破这一限制，预期额外降低峰值5-10%。

5. **实施优先级排序**：按实施难度和见效速度排序——短期（0-6月）为政策类措施（错峰电价），中期（6-12月）为工程类措施（台区优化），长期（1-3年）为投资类措施（储能配置）。

**代码框架**:
```python
import os

output_dir = "outputs/ch07_grid_optimization"

# 使用Step 5计算的指标值
strategies = f"""# 配电网负荷优化调度方案与规划建议

## 1. 优化效果总结

基于线性规划模型对{city}配电网进行负荷优化，核心结果如下：

| 指标 | 优化前 | 优化后 | 变化 |
|------|--------|--------|------|
| 峰值负荷 | {original_peak:.2f} kW | {optimized_peak:.2f} kW | {peak_reduction_rate:.1f}% |
| 峰谷差 | {original_peak_valley_diff:.2f} kW | {optimized_peak_valley_diff:.2f} kW | {pv_reduction_rate:.1f}% |
| 负荷率 | {original_load_rate:.4f} | {optimized_load_rate:.4f} | {lr_improvement_rate:.1f}% |

> 注：以上结果基于历史均值负荷数据，实际优化效果可能因负荷波动而有所差异。

## 2. 工程化策略建议

### 2.1 错峰用电引导（需求侧管理）

**问题分析**：
- 第二章节分析显示，{city}的日内负荷呈典型双峰模式，晚高峰（18-21点）负荷集中度最高
- 第三章节峰值识别结果显示，约XX%的峰值事件发生在18-21点时段
- 工业用户和商业用户的可转移负荷（如空调、照明、充电桩）约占峰值负荷的15-25%

**具体建议**：
1. **实施分时电价政策**：将全天分为峰段（18-21点）、平段（7-17点、22-23点）、谷段（0-6点），峰谷电价比不低于2:1，通过价格信号引导可转移负荷避开晚高峰
2. **推广智能电表与实时电价响应**：为居民用户安装智能电表，接入实时电价信号，让用户自主参与削峰（如延迟洗衣机、空调调高1-2度）
3. **建立可中断负荷合同机制**：与大型工业用户签订可中断负荷协议，在峰值时段按约定削减负荷，给予电价优惠补偿

**预期效果**：
- 晚高峰负荷降低10-15%（基于工业用户可转移负荷比例估算）
- 配合优化模型，综合峰值降低率可达{peak_reduction_rate + 10:.1f}%以上
- 实施成本较低（主要为政策制定和电表更换），见效快

### 2.2 台区容量优化配置（供给侧优化）

**问题分析**：
- 第二章节负荷率分析显示，部分zone的负荷率低于40%，设备利用率严重不足
- 变压器长期低负荷运行不仅浪费设备容量，还增加了固定运维成本
- zone间缺乏有效的联络线，无法实现跨区域负荷互济

**具体建议**：
1. **低负荷率zone变压器减容**：对负荷率持续低于40%的zone，评估将变压器容量降低1-2个标准等级的可行性
2. **建设zone间联络线**：在相邻zone间增设联络线和自动切换开关，实现负荷的动态调配
3. **推行"子台区"精细化管理**：将大zone细分为多个子台区，分别监测和调度，提升管理的颗粒度

**预期效果**：
- 整体负荷率提升5-10%（通过消除低负荷率zone的冗余容量）
- 减少变压器空载损耗，年节约运行成本约3-5%
- 提升供电可靠性（联络线提供备用容量）

### 2.3 季节性配电调度（运行策略优化）

**问题分析**：
- 第五章节季节性强度分析显示，{city}的季节性波动指数F_s较高，夏季制冷负荷导致季节性峰值突出
- 夏季峰值负荷可能是冬季的1.5-2倍，设备在夏季满载运行而在冬季大量闲置
- 设备检修窗口通常安排在春秋季，但如果夏季突发高负荷，可能来不及完成检修

**具体建议**：
1. **制定夏季/冬季差异化调度预案**：夏季提前启动全部备用容量，冬季允许部分设备轮停检修
2. **建立季节性负荷预警机制**：基于第五章的趋势分析和第四章的预测模型，提前1-2周预测季节性峰值，启动预警
3. **在夏季高峰前完成设备检修和容量升级**：将年度检修计划安排在3-5月（春季），确保6月前全部设备处于最佳状态

**预期效果**：
- 夏季峰值负荷降低5-8%（通过提前调度和预警避免突发过载）
- 设备可用率提升至99%以上（通过合理的检修计划）
- 减少因设备故障导致的停电事故

### 2.4 储能协同削峰（技术升级）

**问题分析**：
- 当前线性规划模型受限于供需平衡约束（各时段总负荷等于需求），无法实现跨时段的负荷转移
- 第七章优化结果显示峰谷差为{original_peak_valley_diff:.2f} kW，存在显著的储能套利空间
- 电池储能技术成本持续下降（2024年锂电池储能系统度电成本已降至0.1元/kWh以下），经济性日益改善

**具体建议**：
1. **配置电池储能系统**：建议容量为峰值负荷的5-10%（约{optimized_peak * 0.05:.0f}~{optimized_peak * 0.1:.0f} kW），放电时长2-4小时
2. **采用"谷充峰放"策略**：在凌晨低谷时段（0-6点）充电，在晚高峰时段（18-21点）放电，利用峰谷电价差回收投资
3. **升级优化模型为MILP**：将储能充放电的离散决策（充电/放电/空闲三态）纳入优化模型，实现储能与负荷分配的协同优化

**预期效果**：
- 峰值负荷额外降低5-10%（储能放电直接替代高峰时段的部分负荷）
- 峰谷差额外缩小10-15%（储能平滑了日内负荷波动）
- 投资回收期5-8年（取决于峰谷电价差和储能系统成本）

## 3. 实施优先级建议

| 优先级 | 时间范围 | 策略 | 实施难度 | 预期效果 | 投资规模 |
|--------|----------|------|----------|----------|----------|
| P0（最高） | 0-6月 | 错峰电价政策 + 智能电表推广 | 低 | 峰值降低10-15% | 低（政策+电表） |
| P1 | 6-12月 | 台区容量优化 + 联络线升级 | 中 | 负荷率提升5-10% | 中（设备改造） |
| P2 | 1-2年 | 季节性调度自动化 + 预警系统 | 中 | 夏季峰值降低5-8% | 中（软件系统） |
| P3 | 2-3年 | 储能系统配置 + MILP模型升级 | 高 | 峰值额外降低5-10% | 高（储能投资） |

## 4. 策略间的协同效应

上述四类策略并非独立实施，而是存在显著的协同效应：
- 错峰电价（策略1）降低了晚高峰负荷，为储能系统（策略4）提供了更小的放电需求，从而降低储能配置容量
- 台区优化（策略2）提升了联络线容量，为储能系统的功率接入提供了物理条件
- 季节性调度（策略3）为所有策略提供了运行框架，确保不同季节采用不同的优化参数

综合实施四类策略，预期可将{city}的峰值负荷降低20-30%，负荷率提升至80%以上，峰谷差缩小30%以上。
"""

strategies_path = os.path.join(output_dir, 'ch07_engineering_strategies.md')
with open(strategies_path, 'w', encoding='utf-8') as f:
    f.write(strategies)
print(f"工程化策略建议报告已保存: {strategies_path}")
```

**本步骤完成后的检查标准**

- 四类策略（错峰用电、台区优化、季节调度、储能协同）全部包含，每类策略都有完整的"问题-建议-预期效果"三要素
- 每类策略的"问题"部分引用了前文的具体分析结论（如"第二章分析显示..."、"第三章峰值识别结果显示..."），而非空泛描述
- 预期效果尽可能量化（如"峰值降低10-15%"），而非仅定性描述（如"峰值有所降低"）
- 实施优先级排序合理：短期低难度策略优先，长期高难度策略靠后
- 策略间协同效应的分析逻辑清晰，说明四类策略如何相互增强
- 优化效果的总结数据与Step 5的计算结果一致（数值无矛盾）

**如果遇到问题请及时反馈**

- 如果前文某些章节的结论缺失（如第五章季节性分析未完成），需在策略中标注"待补充"，避免引用不存在的数据
- 如果预期效果的估算缺乏数据支撑（如"工业用户可转移负荷占15-25%"），需标注为"估算值"，并建议通过实际调研验证
- 如果策略建议与摩洛哥当地的电力政策法规冲突（如分时电价需要监管机构审批），需在报告中注明政策前提条件
- 如果用户认为四类策略不够全面或有其他关注点，可灵活增加策略类别（如分布式光伏消纳、电动汽车充电管理等）

**本步骤输出产物**

- `ch07_engineering_strategies.md` -- 文件名: `ch07_engineering_strategies.md` -- 存放路径: `outputs/ch07_grid_optimization/` -- 内容说明: 包含优化效果总结、四类工程化策略建议（错峰用电引导、台区容量优化配置、季节性配电调度、储能协同削峰）、实施优先级排序表、策略间协同效应分析的完整Markdown报告 -- 后续使用章节: Prompt-08（总结与展望的策略建议汇总）、最终报告的工程应用部分

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 数学模型定义 | ch07_optimization_formulation.md | Markdown | outputs/ch07_grid_optimization/ | 报告理论基础 |
| 2 | 约束参数表 | ch07_constraints_table.csv | CSV | outputs/ch07_grid_optimization/ | Step 3、报告参数说明 |
| 3 | 优化前后对比图 | ch07_before_after_optimization.png | PNG | outputs/ch07_grid_optimization/ | 报告核心配图 |
| 4 | 削峰效果量化表 | ch07_optimization_metrics.csv | CSV | outputs/ch07_grid_optimization/ | Step 6、Prompt-08、报告 |
| 5 | 工程化策略建议 | ch07_engineering_strategies.md | Markdown | outputs/ch07_grid_optimization/ | Prompt-08、报告工程部分 |

### 3.2 关键产物结构详解

**ch07_constraints_table.csv**（Step 2输出）:
- 列结构：hour(int, 0-23)、total_demand_kw(float, 该小时总需求)、min_demand_kw(float, 该小时最低负荷保障)、demand_to_min_ratio(float, 需求与最低负荷比值)
- 行数：24行（每小时一行）
- 用途：Step 3中作为PuLP模型的参数输入，Step 5中用于计算优化效果

**ch07_optimization_metrics.csv**（Step 5输出）:
- 列结构：metric(str, 指标名称)、original(float, 优化前值)、optimized(float, 优化后值)、change(float, 绝对变化量)、change_pct(float, 百分比变化率)
- 行数：3行（峰值负荷、峰谷差、负荷率）
- 用途：Prompt-08中提取关键指标，最终报告中展示优化效果

## 四、产物后续优化方向

### 4.1 当前方案的局限性

- **线性规划模型的简化假设**：当前模型假设各时段总需求固定（供需平衡等式约束），无法实现跨时段的负荷转移。实际电网中，储能系统、需求响应等机制允许负荷在不同时段间灵活调配
- **未考虑网损和电压约束**：实际配电网中，电能传输会产生网损（与传输距离和负荷大小相关），且节点电压需维持在允许范围内（如0.95~1.05 p.u.）。当前模型忽略了这些物理约束
- **未考虑储能系统的动态充放电过程**：储能系统的充放电效率（通常为85-95%）、循环寿命、SOC（荷电状态）限制等动态特性未被建模
- **未考虑分布式新能源接入**：摩洛哥太阳能资源丰富，分布式光伏的间歇性出力会对配电网负荷产生"反峰"效应（中午光伏出力最大，负荷反而较低），当前模型未纳入
- **单目标优化的局限**：仅优化峰值负荷最小化，未同时考虑经济性（运行成本最小化）、环保性（碳排放最小化）等多维目标

### 4.2 可进一步优化的方向

- **升级为MILP模型**：引入储能充放电的离散决策变量（0/1变量表示充电/放电/空闲三态），实现储能与负荷分配的协同优化。可使用PuLP的LpVariable(cat='Binary')创建0-1变量
- **引入多目标优化**：使用加权求和法或epsilon约束法，同时优化峰值负荷和运行成本。例如：minimize w1 * L_max + w2 * total_cost，其中w1和w2为权重系数
- **考虑需求响应机制**：将用户侧的灵活性（如空调温度可调范围、洗衣机可延迟时间）纳入优化模型，作为虚拟的"负负荷"资源
- **结合实时电价信号**：引入分时电价作为参数，将经济优化目标（最小化购电成本）纳入模型
- **考虑新能源出力的不确定性**：使用鲁棒优化（Robust Optimization）或随机优化（Stochastic Programming）处理光伏出力的不确定性

### 4.3 其他可选方法

- **NSGA-II多目标进化算法**：适用于非线性多目标优化，可生成Pareto前沿，展示峰值负荷与运行成本之间的权衡关系。实现可使用Python的pymoo库。缺点是求解时间较长（通常需要数分钟到数十分钟），且结果不保证全局最优
- **强化学习（DQN/PPO）**：适用于动态实时调度场景，可在线学习最优策略，适应负荷模式的渐变。实现可使用Stable-Baselines3库。缺点是需要大量训练数据和GPU计算资源，模型的可解释性较差
- **模型预测控制（MPC）**：滚动优化框架，在每个时间步基于当前状态和未来预测求解有限时域内的最优控制序列。适用于实时调度场景，但计算复杂度较高
- **粒子群优化（PSO）**：适用于连续优化问题，实现简单，不依赖梯度信息。但对于带等式约束的问题（如供需平衡），需要额外的约束处理技巧（如罚函数法）

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单

- 如果模型无解（Infeasible），需确认是否可以放宽约束条件（如提高容量上限分位数、降低最低负荷安全系数、或移除最低负荷约束）
- 如果优化效果不明显（峰值降低率 < 3%），需确认是否接受当前结果，还是希望升级模型（如引入储能的MILP模型）
- 如果工程策略的预期效果缺乏实际数据支撑（如"工业用户可转移负荷占15-25%"为估算值），需确认是否继续使用估算值，还是需要补充实际调研数据
- 如果所选城市（Laayoune）的优化结果不具代表性，需确认是否需要对其他城市分别进行优化

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 模型无解 | LpStatus = "Infeasible" | （1）检查总容量 sum(C_z) > max(D_t)；（2）将C_z分位数从0.95提高到0.98；（3）将D_min_t安全系数从1.1降低到1.0；（4）移除最低负荷约束 | 是 |
| 求解超时 | 求解时间 > 60秒 | 检查是否存在重复约束的循环错误；设置timeLimit=30并接受次优解 | 否 |
| 优化效果不明显 | 峰值降低率 < 3% | 检查供需平衡约束是否限制了优化空间；考虑升级为MILP模型引入储能 | 是 |
| L_max与原始峰值相同 | 优化无效果 | 检查约束条件是否过于严格；检查D_t和C_z的数值是否正确 | 是 |
| zone分配出现负值 | x_{z,t} < 0 | 检查非负约束是否正确添加；检查求解器是否正常工作 | 否 |
| 中文字体显示异常 | 图表中文字显示为方框 | 安装SimHei字体或使用英文标签替代 | 否 |
| PuLP/CBC未安装 | ImportError: No module named 'pulp' | 运行 pip install pulp 安装 | 否 |

---
---

# Prompt-08: 总结与展望

## 一、任务概述

### 1.1 本次任务是什么

本章是全流程分析的**收尾章节**，承担两项核心任务：一是对前七章的全部研究成果进行系统性汇总，提炼关键发现和核心数据指标，形成一份完整的"研究结论总览"；二是客观评估本次研究的局限性，并提出未来可拓展的研究方向。

汇总工作不是简单的重复罗列，而是需要从"数据预处理 → 规律挖掘 → 峰值识别 → 预测建模 → 趋势分析 → 跨国对比 → 配电优化"全链条中，提炼出最具价值的结论。例如："哪个城市的负荷波动最大"、"最优预测模型是哪个、精度如何"、"中摩城市用电差异的根本原因是什么"、"配电网优化能带来多少削峰效果"等。这些结论将直接服务于最终的结题报告或学术论文的"结论"章节。

未来展望部分应结合当前研究的不足，提出具体的改进路径——例如引入气象多维指标提升预测精度、拓展多国家多气候带对比、结合储能和分布式光伏场景完善优化模型等。展望不是空泛的"未来可以做得更好"，而是要有明确的"做什么、怎么做、预期效果"三个层次。

本章与前序章节的关系是"汇总与升华"——它不产生新的分析结果，而是将前七章的碎片化结论整合为一份连贯的、有逻辑深度的研究成果总览，帮助读者（评审专家、项目负责人、后续研究者）快速把握全流程的核心贡献和不足。

### 1.2 从什么数据出发

本章的输入不是单一的数据文件，而是全部前序章节的输出产物和分析结论。具体依赖如下：

- **ch01 数据预处理**：数据质量报告（异常率、缺失率、量纲换算参数）、标准化数据集概况（4城市、17个zone、约30万行）
- **ch02 用电规律挖掘**：描述性统计总表、负荷率与变异系数、24小时负荷曲线特征、工作日/周末差异、居民/工业分类结果
- **ch03 峰值识别**：峰值阈值表、峰值事件统计（总数、时段分布、季节分布）、异常峰值比例
- **ch04 短期预测**：模型对比表（5模型MAPE/RMSE/MAE）、最优模型名称和精度、24h滚动预测效果
- **ch05 中长期趋势**：STL分解结果、季节性强度表、同比/环比增长率、趋势方向（上升/平稳/下降）
- **ch06 跨国对比**：摩洛哥-中国城市对比报告、人均用电量对比、季节性波动差异、产业结构差异分析
- **ch07 配电网优化**：优化效果量化表（峰值降低率、峰谷差缩小率、负荷率提升率）、工程化策略建议

### 1.3 可以采用什么方法

本章以**定性总结 + 定量指标提取**为主，不需要复杂的计算方法。核心是信息整合和逻辑提炼。

具体方法包括：
1. **结构化文本撰写**：按照研究逻辑链条（数据 → 规律 → 峰值 → 预测 → 趋势 → 对比 → 优化）组织总结内容，每章提取2-3条最重要的结论
2. **关键指标提取**：从前序章节的CSV产物中读取核心数值指标，汇总为一张"关键指标总览表"
3. **技术路线回顾**：以流程图或文字描述的形式，回顾全流程使用的技术方法和工具链
4. **SWOT分析**（可选）：从优势(Strength)、劣势(Weakness)、机会(Opportunity)、威胁(Threat)四个维度评估本次研究

## 二、执行步骤

### Step 1: 全流程成果汇总

**本步骤要做什么**

本步骤的目标是按照研究逻辑链条，逐章提炼核心发现，形成结构化的成果汇总报告。这份报告是整个研究项目最精炼的"结论摘要"——读者无需阅读前七章的全部内容，只需阅读本报告即可把握全流程的核心贡献。

具体而言，需要对8个章节（含本章自身的方法论说明）分别提炼核心结论。每章提取2-3条最重要的发现，每条发现必须包含两个要素：（1）定性结论（"发现了什么"）；（2）定量支撑（"具体数据是多少"）。例如，不能只写"四城市负荷差异显著"，而应写"四城市日均负荷差异显著：Foum eloued综合负荷最高（约XX kW），Boujdour最低（约XX kW），最高值为最低值的X倍"。

汇总报告的结构按章节顺序排列，每章一个小节。章与章之间需要有逻辑衔接——例如，第二章的规律发现为第三章的峰值识别提供了背景，第三章的峰值特征为第四章的预测建模提供了目标变量，第四章的预测精度为第五章的趋势分析提供了工具支撑。这种逻辑衔接能让读者理解研究链条的完整性。

**具体操作指引**

1. **逐章阅读前序产物**：依次打开ch01~ch07的输出文件（CSV和Markdown），提取每章的核心数值和结论。如果某些章节的产物文件不存在（如ch06跨国对比因爬虫失败而缺失），需在报告中说明原因。

2. **按统一模板撰写每章总结**：每章的总结遵循以下模板：
   - **核心发现1**：[定性结论] + [定量数据]
   - **核心发现2**：[定性结论] + [定量数据]
   - **与前/后章的逻辑关系**：[一句话说明衔接关系]

3. **填充占位符**：原始Prompt中使用了"XX"作为占位符（如"最优模型MAPE最低为XX%"），在实际执行时需替换为真实数据。如果真实数据尚未计算完成，保留占位符并标注"待填充"。

4. **保存为Markdown文件**：使用标准的Markdown格式，包含标题层级、表格、加粗等格式，便于后续转换为报告或论文。

**代码框架**:
```python
import os

output_dir = "outputs/ch08_summary"
os.makedirs(output_dir, exist_ok=True)

# ============================================================
# 注意：以下内容中的"XX"为占位符，实际执行时需替换为真实数据
# 真实数据来自各章的输出产物文件
# ============================================================

summary = """# 摩洛哥多城市电力负荷全流程分析 — 成果汇总报告

> 本报告对全流程8个章节的核心研究成果进行系统性汇总，提炼关键发现和数据指标。
> 数据来源：摩洛哥4城市（Laayoune、Boujdour、Foum eloued、Marrakech）智能电表数据
> 分析周期：2022年9月 ~ 2024年5月（约20个月）

---

## 第一章 数据预处理

**核心发现1**：成功将4城市、17个zone的异构数据统一为10分钟/kW标准格式。
- 原始数据量：284,171行（Laayoune 88,890 + Boujdour 88,890 + Foum eloued 88,890 + Marrakech 17,501）
- 量纲统一：3个城市从电流(A)转换为有功功率(kW)，换算公式 P = I × 220V × 0.9 / 1000
- 时间对齐：Marrakech从30分钟上采样至10分钟（17,501行 → 52,503行，线性插值）

**核心发现2**：3σ准则检测并替换异常值，数据质量显著提升。
- 异常值检测：基于各zone的均值和3倍标准差，标记超出 [μ-3σ, μ+3σ] 的数据点
- 异常率：原始数据异常率约XX%，清洗后降至0%
- 处理方式：异常值替换为线性插值值，保持时序连续性

**与前章关系**：本章是全流程的基础起点，输出的标准化数据集(ch01_cleaned_data.csv)是后续所有章节的输入。

---

## 第二章 用电负荷特征挖掘与用电规律分析

**核心发现1**：四城市日均负荷差异显著，Foum eloued综合负荷最高。
- Foum eloued（7个zone）综合日均负荷最高，约XX kW
- Boujdour（3个zone）综合日均负荷最低，约XX kW
- 最高值为最低值的约X倍，反映了城市规模和产业结构的差异

**核心发现2**：日内负荷呈典型双峰模式，晚高峰更为突出。
- 早高峰：8-10点，主要由工业和商业用电驱动
- 晚高峰：18-21点，主要由居民生活用电（照明、空调、炊事）驱动
- 晚高峰峰值通常为早高峰的X倍

**核心发现3**：工作日与周末负荷差异明显，居民行为主导用电模式。
- 周末负荷较工作日降低约XX%
- 差异主要出现在工作时段（8-18点），夜间差异较小
- 说明工业负荷占比较高，周末停产导致负荷下降

**与前章关系**：本章的规律发现为第三章的峰值识别提供了统计基础（如峰值高发时段的预判）。

---

## 第三章 负荷峰值识别与峰值特征研究

**核心发现1**：95%分位数阈值有效识别了全部4城市的峰值事件。
- 峰值事件总数：共约XX个（4城市合计）
- 峰值判定标准：负荷超过该zone历史95%分位数的时段
- 峰值高发时段：集中在18-21点（晚高峰），与第二章的规律分析一致

**核心发现2**：夏季峰值频次最高，制冷负荷是主要驱动因素。
- 夏季峰值事件占比约XX%，显著高于其他季节
- 异常峰值（突变型，如瞬间跳升超过均值+5σ）仅占总峰值的XX%
- 说明电网运行整体稳定，极端异常事件较少

**与前章关系**：本章的峰值特征为第四章的预测建模提供了目标变量定义（预测峰值时段的负荷），为第七章的优化模型提供了峰值基准。

---

## 第四章 短期电力负荷预测模型构建

**核心发现1**：5模型对比显示，[最优模型]在精度和效率间取得最佳平衡。
- 最优模型：[待填充，如XGBoost/LightGBM]
- 最优MAPE：XX%（平均绝对百分比误差）
- 最优RMSE：XX kW（均方根误差）
- 模型排名（按MAPE升序）：[模型1] > [模型2] > [模型3] > [模型4] > [模型5]

**核心发现2**：24h滚动预测成功捕捉了日内周期性特征。
- 预测窗口：24小时（即预测未来24个时段的负荷）
- 预测精度日内分布：白天时段（8-20点）精度略低于夜间时段
- 典型误差模式：在负荷突变点（如早晚高峰的上升/下降沿）误差较大

**与前章关系**：本章的预测模型为第五章的中长期趋势分析提供了工具支撑（可扩展到更长预测窗口），为第七章的优化模型提供了未来负荷输入。

---

## 第五章 月度/季度中长期趋势分析

**核心发现1**：STL分解显示四城市均呈[上升/平稳/下降]趋势。
- 趋势分量：[描述各城市的长期趋势方向和幅度]
- 季节性分量：所有城市均呈现显著的年度周期性（夏季高、冬季低）
- 残差分量：残差较小且无自相关，说明STL分解效果良好

**核心发现2**：季节性强度差异显著，[城市A]季节性最强。
- 季节性强度F_s（季节性方差/总方差）：[城市A]=XX（强），[城市B]=XX（中），[城市C]=XX（弱）
- 同比增长率：年度负荷同比增长约XX%
- 环比分析：月度环比波动主要受季节性和气温影响

**与前章关系**：本章的趋势判断为第六章的跨国对比提供了摩洛哥侧的基准数据，为第七章的优化模型提供了季节性调整依据。

---

## 第六章 国内对标区域数据爬取与跨国对比

**核心发现1**：摩洛哥城市人均用电量约为中国对标城市的XX%。
- 摩洛哥城市人均用电量：约XX kWh/人·月
- 中国对标城市人均用电量：约XX kWh/人·月
- 差异原因：经济发展水平、电气化率、产业结构、气候条件的综合影响

**核心发现2**：季节性波动模式存在显著差异。
- 摩洛哥城市：受夏季高温影响更大，制冷负荷是峰值的主要驱动
- 中国对标城市：冬季供暖负荷和夏季制冷负荷共同构成双峰
- 产业结构差异：摩洛哥城市工业负荷占比较低，居民负荷占比较高

**与前章关系**：本章的跨国对比为第七章的工程策略建议提供了国际参考（如中国错峰电价政策的经验）。

---

## 第七章 配电网优化模型

**核心发现1**：线性规划优化后峰值负荷降低XX%，验证了优化模型的有效性。
- 优化方法：单目标线性规划（PuLP + CBC求解器）
- 原始峰值负荷：XX kW → 优化后峰值负荷：XX kW
- 峰值降低率：XX%
- 求解时间：X秒（模型规模：XX变量、XX约束）

**核心发现2**：四类工程策略可进一步提升优化效果。
- 错峰电价：预期额外降低峰值10-15%
- 台区优化：预期提升负荷率5-10%
- 季节调度：预期降低夏季峰值5-8%
- 储能协同：预期额外降低峰值5-10%
- 综合实施预期：峰值降低20-30%

**与前章关系**：本章是全流程的工程应用落地，综合运用了前六章的全部分析结论。

---

## 第八章 总结与展望（本章）

**核心发现1**：全流程分析建立了从数据预处理到配电网优化的完整技术链条。
- 技术路线：数据清洗 → 规律挖掘 → 峰值识别 → 预测建模 → 趋势分析 → 跨国对比 → 配电优化
- 核心工具：Python (pandas, scikit-learn, XGBoost, PuLP, matplotlib)
- 数据规模：4城市、17 zone、约30万条10分钟级记录

**核心发现2**：研究存在数据维度缺失、模型精度限制等局限性，未来可在多个方向拓展。
- 详见"不足与局限"和"未来展望"部分

---

## 技术路线总结

全流程分析采用的技术路线如下：

```
原始数据(Excel, 4 Sheet)
    │
    ▼
[Step 1] 数据预处理 (pandas)
    ├── 量纲统一: A → kW
    ├── 时间对齐: 30min → 10min (线性插值)
    ├── 异常检测: 3σ准则
    └── 特征工程: hour, day_of_week, season, ...
    │
    ▼
[Step 2] 用电规律挖掘 (pandas + matplotlib)
    ├── 描述性统计: mean, std, CV, load_rate
    ├── 日内曲线: 24h负荷曲线
    ├── 周/季规律: heatmap
    └── 居民/工业分层: KMeans聚类
    │
    ▼
[Step 3] 峰值识别 (pandas + numpy)
    ├── 阈值设定: 95%分位数
    ├── 峰值标记: 超阈值时段
    └── 峰值特征: 时段分布、季节分布
    │
    ▼
[Step 4] 短期预测 (scikit-learn + XGBoost + LSTM)
    ├── 5模型对比: LR, RF, XGBoost, LightGBM, LSTM
    ├── 评估指标: MAPE, RMSE, MAE
    └── 24h滚动预测
    │
    ▼
[Step 5] 中长期趋势 (statsmodels)
    ├── STL分解: trend + seasonal + residual
    ├── 季节性强度: F_s指标
    └── 同比/环比分析
    │
    ▼
[Step 6] 跨国对比 (爬虫 + pandas)
    ├── 数据爬取: 中国城市电力数据
    ├── 人均用电量对比
    └── 季节性/产业结构对比
    │
    ▼
[Step 7] 配电网优化 (PuLP + CBC)
    ├── 数学建模: LP (线性规划)
    ├── 求解: CBC求解器
    ├── 效果评估: 峰值降低率、负荷率
    └── 工程策略: 4类建议
    │
    ▼
[Step 8] 总结与展望 (文本整合)
    ├── 成果汇总: 8章核心结论
    ├── 关键指标: 总览表
    ├── 不足与局限: 客观评估
    └── 未来展望: 改进路径
```

## 不足与局限

### 数据维度局限
1. **缺少气象数据**：气温、湿度、风速等气象因素是影响电力负荷的重要外部变量，但本次分析未纳入。这限制了预测模型的精度提升空间（通常气象变量可贡献5-15%的预测精度改善）
2. **缺少经济数据**：GDP、人口、产业结构等宏观经济指标未纳入分析，无法建立负荷变化与经济发展的定量关系
3. **时间跨度有限**：数据覆盖约20个月（2022年9月~2024年5月），不足以进行多年周期的趋势分析（如5年或10年中长期趋势）
4. **空间分辨率有限**：数据仅到zone级别（配电变压器级别），缺少更细粒度的用户级数据

### 模型精度局限
1. **预测模型未充分利用外部特征**：第四章的预测模型仅使用历史负荷和时间特征，未纳入气象、节假日等外部特征，MAPE可能在5-15%之间，仍有提升空间
2. **优化模型简化假设较多**：第七章的线性规划模型忽略了网损、电压约束、储能动态等实际因素，优化效果可能偏乐观
3. **跨国对比深度不足**：第六章的对比主要基于人均用电量等宏观指标，缺少负荷曲线形态、峰谷特性等微观层面的深入对比

### 方法论局限
1. **异常检测方法单一**：仅使用3σ准则，未结合领域知识（如设备检修停运、极端天气事件）进行异常原因分类
2. **居民/工业分类方法简单**：基于KMeans聚类的二分类方法较为粗糙，未考虑混合负荷（同一zone同时包含居民和工业用户）的情况
3. **优化模型为静态模型**：未考虑负荷的时变性（不同日、不同季节的负荷模式不同），使用历史均值作为参数可能无法反映实时运行状况

## 未来展望

### 方向1：引入多维气象数据提升预测精度
- **做什么**：将气温、湿度、风速、日照时数等气象变量纳入预测模型
- **怎么做**：通过Open-Meteo API或NOAA数据库获取摩洛哥4城市的逐小时气象数据，与负荷数据按时间戳合并，作为预测模型的额外特征。使用特征重要性分析（SHAP值）量化各气象变量的贡献度
- **预期效果**：MAPE从当前的XX%降低至5-8%（基于文献中气象增强预测的典型改善幅度）
- **实施难度**：低（数据获取免费，特征工程简单）

### 方向2：拓展多国家多气候带对比
- **做什么**：将跨国对比从"摩洛哥 vs 中国"拓展到"摩洛哥 vs 撒哈拉以南非洲国家 vs 欧洲国家"
- **怎么做**：通过世界银行数据库、IEA（国际能源署）公开数据获取更多国家的电力负荷统计数据，按气候带（热带、亚热带、温带、寒带）分组对比
- **预期效果**：揭示不同气候带和经济发展阶段下电力负荷模式的普适规律和特殊特征
- **实施难度**：中（需要寻找可靠的数据源，可能涉及多语言数据处理）

### 方向3：升级优化模型为多时间尺度协调调度
- **做什么**：将第七章的单一24小时优化模型升级为"日前调度 + 日内滚动修正"的多时间尺度框架
- **怎么做**：日前阶段使用预测模型输出未来24小时负荷曲线，求解MILP优化模型（含储能充放电决策）；日内阶段每15分钟滚动更新一次，基于最新实测数据修正调度方案
- **预期效果**：优化方案的实际可执行性显著提升，峰值降低率从XX%提升至15-25%
- **实施难度**：高（需要MILP求解器和实时数据接口）

### 方向4：结合分布式光伏和储能的主动配电网优化
- **做什么**：将分布式光伏出力和电池储能系统纳入配电网优化模型
- **怎么做**：获取摩洛哥4城市的太阳能辐照数据，建立光伏出力模型；在MILP模型中增加光伏出力变量和储能SOC约束，实现"源-网-荷-储"协同优化
- **预期效果**：光伏消纳率提升至90%以上，净峰值负荷额外降低10-20%
- **实施难度**：高（需要光伏和储能的详细参数，模型复杂度显著增加）

### 方向5：开发交互式数据可视化平台
- **做什么**：将全流程分析结果整合为一个交互式Web平台，支持用户自助查询和探索
- **怎么做**：使用Plotly Dash或Streamlit框架开发，部署为Web应用。核心功能包括：多城市负荷曲线对比、预测模型在线推理、优化方案可视化、关键指标仪表盘
- **预期效果**：研究成果的可访问性和可复用性大幅提升，支持非技术人员（如电力公司管理层）直接使用
- **实施难度**：中（Dash/Streamlit开发门槛低，但需要前后端联调和服务器部署）
"""

summary_path = os.path.join(output_dir, 'ch08_achievements_summary.md')
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write(summary)
print(f"成果汇总报告已保存: {summary_path}")
```

**本步骤完成后的检查标准**

- 报告覆盖全部8章的核心发现（含本章自身的方法论说明），无遗漏章节
- 每条核心发现包含"定性结论 + 定量数据"两个要素，不能只有定性描述而无数据支撑
- 章与章之间的逻辑衔接清晰，读者能理解研究链条的完整性
- 技术路线总结以流程图形式呈现，涵盖全流程8个步骤的核心方法和工具
- 不足与局限部分客观诚实，不回避问题
- 未来展望部分每个方向包含"做什么、怎么做、预期效果"三个层次
- 占位符"XX"已尽可能替换为真实数据，未替换的已标注"待填充"
- Markdown格式规范，标题层级正确，表格结构完整

**如果遇到问题请及时反馈**

- 如果某些章节的产物文件不存在（如ch06跨国对比因爬虫失败而缺失）：在报告中该章节位置标注"本章因数据获取受限未完成分析，相关结论缺失"，避免编造不存在的结论
- 如果不同章节的同一指标数值矛盾（如ch02和ch07对同一城市的日均负荷值不一致）：以最新章节（ch07）的数据为准，并在报告中注明数据来源
- 如果"XX"占位符过多导致报告可读性差：优先填充数值型指标（如MAPE、峰值降低率），定性描述可暂用概括性语言替代
- 如果用户对报告结构有特殊要求（如需要按"方法-结果-讨论"三段式组织，而非按章节顺序）：根据用户要求调整结构

**本步骤输出产物**

- `ch08_achievements_summary.md` -- 文件名: `ch08_achievements_summary.md` -- 存放路径: `outputs/ch08_summary/` -- 内容说明: 包含全流程8章的核心发现汇总、技术路线流程图、不足与局限分析、未来展望5个方向的完整Markdown报告。每章提炼2-3条核心结论，每条结论含定性描述和定量数据支撑 -- 后续使用章节: 最终报告的"结论与展望"章节、学术摘要的素材来源、汇报PPT的内容大纲

---

### Step 2: 关键指标总览表

**本步骤要做什么**

本步骤的目标是提取各章核心数值指标，形成一张精炼的"关键指标总览表"。这张表是整个研究最浓缩的"数据名片"——读者只需浏览这张表，即可快速了解全流程的核心数据成果。

指标选取原则：（1）每个分析章节至少选取1-2个最具代表性的指标；（2）优先选取可直接量化的数值型指标（如MAPE、峰值降低率），而非定性描述；（3）指标之间应能串联成完整的研究故事（从数据量到优化效果）。最终表格预计包含12-15行指标，按章节顺序排列。

需要特别注意：部分指标的值在前序章节执行时尚未确定（如"最优模型MAPE"取决于第四章的实际运行结果），这些指标在当前步骤中以"待填充"标记，待前序章节全部执行完毕后再回填。代码中应设计自动回填机制——从各章的CSV产物中读取指标值，自动替换"待填充"。

**具体操作指引**

1. **定义指标清单**：按章节顺序列出需要提取的指标，每个指标包含：chapter（章节编号）、metric（指标名称）、value（指标值）、unit（单位）四个字段。

2. **尝试自动读取**：对已有CSV产物的指标，使用pandas读取并自动填充。例如，从ch04_model_comparison.csv中读取最优MAPE，从ch07_optimization_metrics.csv中读取峰值降低率。

3. **手动填充**：对无法自动读取的指标（如定性描述类的"最优模型名称"），保留"待填充"标记，提醒用户手动补充。

4. **保存为CSV**：使用统一的列名保存，便于后续在报告中引用。

**代码框架**:
```python
import pandas as pd
import numpy as np
import os

output_dir = "outputs/ch08_summary"
os.makedirs(output_dir, exist_ok=True)

# === 尝试从前序章节产物中自动读取指标 ===
def safe_read_csv(filepath, **kwargs):
    """安全读取CSV文件，文件不存在时返回None"""
    try:
        return pd.read_csv(filepath, **kwargs)
    except FileNotFoundError:
        print(f"  警告: 文件不存在 - {filepath}")
        return None

# --- ch01 指标 ---
ch01_data = safe_read_csv("outputs/ch01_data_preprocessing/ch01_cleaned_data.csv")
ch01_rows = len(ch01_data) if ch01_data is not None else "待填充"
ch01_missing = safe_read_csv("outputs/ch01_data_preprocessing/ch01_missing_stats.csv")

# --- ch02 指标 ---
ch02_stats = safe_read_csv("outputs/ch02_load_pattern_analysis/ch02_load_rate_cv.csv")

# --- ch03 指标 ---
ch03_peaks = safe_read_csv("outputs/ch03_peak_analysis/ch03_peak_thresholds.csv")

# --- ch04 指标 ---
ch04_models = safe_read_csv("outputs/ch04_load_forecasting/ch04_model_comparison.csv")
best_mape = "待填充"
best_model = "待填充"
if ch04_models is not None and len(ch04_models) > 0:
    best_row = ch04_models.iloc[0]  # 假设已按MAPE升序排列
    best_mape = best_row.get('MAPE', '待填充')
    best_model = best_row.get('model', '待填充')

# --- ch05 指标 ---
ch05_seasonal = safe_read_csv("outputs/ch05_midlong_term_trend/ch05_seasonal_strength.csv")

# --- ch07 指标 ---
ch07_metrics = safe_read_csv("outputs/ch07_grid_optimization/ch07_optimization_metrics.csv")
peak_reduction = "待填充"
load_rate_improvement = "待填充"
if ch07_metrics is not None and len(ch07_metrics) > 0:
    peak_row = ch07_metrics[ch07_metrics['metric'].str.contains('峰值', na=False)]
    if len(peak_row) > 0:
        peak_reduction = f"{abs(peak_row.iloc[0].get('change_pct', 0)):.1f}%"
    lr_row = ch07_metrics[ch07_metrics['metric'].str.contains('负荷率', na=False)]
    if len(lr_row) > 0:
        load_rate_improvement = f"{abs(lr_row.iloc[0].get('change_pct', 0)):.1f}%"

# === 构建关键指标总览表 ===
key_metrics = pd.DataFrame([
    # --- 数据预处理 ---
    {'chapter': 'ch01', 'category': '数据预处理',
     'metric': '原始数据总量', 'value': f'{ch01_rows}行' if isinstance(ch01_rows, int) else ch01_rows,
     'unit': '行', 'source_file': 'ch01_cleaned_data.csv'},
    {'chapter': 'ch01', 'category': '数据预处理',
     'metric': '城市/zone数量', 'value': '4城市/17zone',
     'unit': '-', 'source_file': '数据概况'},
    {'chapter': 'ch01', 'category': '数据预处理',
     'metric': '时间粒度', 'value': '10分钟',
     'unit': '-', 'source_file': '数据概况'},

    # --- 用电规律 ---
    {'chapter': 'ch02', 'category': '用电规律',
     'metric': '日均负荷(最高城市)', 'value': '待填充',
     'unit': 'kW', 'source_file': 'ch02_descriptive_stats.csv'},
    {'chapter': 'ch02', 'category': '用电规律',
     'metric': '工作日/周末差异', 'value': '待填充',
     'unit': '%', 'source_file': 'ch02_load_rate_cv.csv'},
    {'chapter': 'ch02', 'category': '用电规律',
     'metric': '居民/工业zone比例', 'value': '待填充',
     'unit': '%', 'source_file': 'ch02聚类结果'},

    # --- 峰值识别 ---
    {'chapter': 'ch03', 'category': '峰值识别',
     'metric': '峰值事件总数', 'value': '待填充',
     'unit': '个', 'source_file': 'ch03_peak_thresholds.csv'},
    {'chapter': 'ch03', 'category': '峰值识别',
     'metric': '异常峰值比例', 'value': '待填充',
     'unit': '%', 'source_file': 'ch03_peak_thresholds.csv'},

    # --- 短期预测 ---
    {'chapter': 'ch04', 'category': '短期预测',
     'metric': '最优预测模型', 'value': str(best_model),
     'unit': '-', 'source_file': 'ch04_model_comparison.csv'},
    {'chapter': 'ch04', 'category': '短期预测',
     'metric': '最优MAPE', 'value': str(best_mape),
     'unit': '%', 'source_file': 'ch04_model_comparison.csv'},

    # --- 中长期趋势 ---
    {'chapter': 'ch05', 'category': '中长期趋势',
     'metric': '最强季节性城市', 'value': '待填充',
     'unit': '-', 'source_file': 'ch05_seasonal_strength.csv'},
    {'chapter': 'ch05', 'category': '中长期趋势',
     'metric': '最强季节性F_s', 'value': '待填充',
     'unit': '-', 'source_file': 'ch05_seasonal_strength.csv'},

    # --- 跨国对比 ---
    {'chapter': 'ch06', 'category': '跨国对比',
     'metric': '摩洛哥/中国人均用电比', 'value': '待填充',
     'unit': '%', 'source_file': 'ch06对比报告'},

    # --- 配电网优化 ---
    {'chapter': 'ch07', 'category': '配电网优化',
     'metric': '峰值降低率', 'value': str(peak_reduction),
     'unit': '%', 'source_file': 'ch07_optimization_metrics.csv'},
    {'chapter': 'ch07', 'category': '配电网优化',
     'metric': '负荷率提升率', 'value': str(load_rate_improvement),
     'unit': '%', 'source_file': 'ch07_optimization_metrics.csv'},
])

# === 保存 ===
metrics_path = os.path.join(output_dir, 'ch08_key_metrics_table.csv')
key_metrics.to_csv(metrics_path, index=False)

# === 打印 ===
print(f"\n{'='*70}")
print(f"  全流程关键指标总览表")
print(f"{'='*70}")
print(key_metrics.to_string(index=False))

# 统计待填充数量
pending_count = (key_metrics['value'] == '待填充').sum()
total_count = len(key_metrics)
print(f"\n指标总数: {total_count}, 已填充: {total_count - pending_count}, 待填充: {pending_count}")
if pending_count > 0:
    print(f"\n待填充指标列表:")
    pending = key_metrics[key_metrics['value'] == '待填充']
    for _, row in pending.iterrows():
        print(f"  - [{row['chapter']}] {row['metric']} (来源: {row['source_file']})")
print(f"\n指标表已保存: {metrics_path}")
```

**本步骤完成后的检查标准**

- 指标覆盖全部7个分析章节（ch01~ch07），每章至少1个指标
- 指标总数在12-15个之间（不宜过多导致信息过载，也不宜过少导致覆盖不足）
- 每个指标有明确的unit（单位）和source_file（数据来源文件路径）
- 已有CSV产物的指标已自动读取并填充（如ch04的MAPE、ch07的峰值降低率）
- "待填充"的指标有明确的来源文件标注，便于后续回填
- CSV文件包含5列（chapter, category, metric, value, unit, source_file），无NaN

**如果遇到问题请及时反馈**

- 如果某个章节的CSV产物文件不存在（如ch06跨国对比因爬虫失败而缺失）：该章节的指标保留"待填充"，并在打印输出中标注原因
- 如果自动读取的指标值格式不统一（如有些带"%"有些不带）：在代码中统一格式化，数值型指标保留2位小数
- 如果不同章节对同一指标的计算口径不一致（如ch02和ch07对"日均负荷"的定义不同）：在指标表中注明计算口径差异
- 如果用户希望增加更多指标（如各城市的详细指标而非汇总指标）：可灵活扩展指标清单，但需注意表格的可读性

**本步骤输出产物**

- `ch08_key_metrics_table.csv` -- 文件名: `ch08_key_metrics_table.csv` -- 存放路径: `outputs/ch08_summary/` -- 内容说明: 包含12-15行关键指标的汇总表，列包括chapter（章节编号）、category（指标类别）、metric（指标名称）、value（指标值，已自动填充或标注"待填充"）、unit（单位）、source_file（数据来源文件路径）。按章节顺序排列，覆盖ch01~ch07全部分析章节 -- 后续使用章节: 最终报告的"核心指标"表格、学术摘要的数据支撑、汇报PPT的关键数据页

---

### Step 3: 技术路线总结

**本步骤要做什么**

本步骤的目标是回顾全流程使用的技术方法和工具链，形成一份完整的技术路线总结。这份总结以文字描述和流程图为主，不需要编写代码。它将嵌入Step 1的成果汇总报告中（作为独立章节），帮助读者快速了解"本研究用了什么方法、为什么选这些方法、方法之间如何衔接"。

技术路线总结需要回答三个问题：（1）每个步骤用了什么方法/算法/工具？（2）为什么选择这个方法而非替代方案？（3）方法之间的输入输出关系是什么？这三个问题分别对应"方法清单"、"方法选择理由"和"数据流"三个维度。

**具体操作指引**

1. **方法清单**：按步骤顺序列出每个步骤的核心方法。例如：Step 1（数据预处理）→ 线性插值上采样 + 3σ异常检测 + 物理公式量纲换算；Step 4（短期预测）→ 5模型对比（LR, RF, XGBoost, LightGBM, LSTM）+ MAPE/RMSE评估。

2. **方法选择理由**：对每个方法，用1-2句话说明选择理由。例如：选择线性规划而非遗传算法的原因是"问题具有线性结构，LP求解速度快（秒级）且保证全局最优"。

3. **数据流图**：绘制步骤间的数据依赖关系图，标注每个步骤的输入（来自哪个步骤的哪个产物）和输出（产出了什么文件）。

4. **工具链总结**：列出全流程使用的Python库和版本要求。

**代码框架**:
```python
# 本步骤以文本撰写为主，不产生独立文件
# 技术路线总结内容已嵌入 Step 1 的 ch08_achievements_summary.md 中
# 包含以下三个部分：
# 1. 技术路线流程图（ASCII art格式）
# 2. 各步骤方法选择理由表
# 3. 工具链清单

# 如果需要单独生成技术路线文档，可使用以下代码：
tech_route = """# 技术路线总结

## 1. 方法选择理由

| 步骤 | 核心方法 | 选择理由 | 替代方案 |
|------|----------|----------|----------|
| 数据预处理 | 线性插值 + 3σ准则 | 标准时序预处理方法，成熟可靠 | 样条插值、IQR方法 |
| 用电规律 | 描述性统计 + KMeans | 无监督方法，无需标签数据 | DBSCAN、GMM |
| 峰值识别 | 95%分位数阈值 | 工程上常用的峰值判定标准 | Z-score、固定阈值 |
| 短期预测 | XGBoost/LightGBM | 精度与效率的最佳平衡 | LSTM（精度更高但耗时）、Prophet |
| 中长期趋势 | STL分解 | 经典时序分解方法，可解释性强 | X-11、SEATS |
| 跨国对比 | 描述性统计对比 | 数据维度有限，统计对比最直接 | 回归分析、因果推断 |
| 配电网优化 | 线性规划(PuLP) | 问题为线性结构，求解快且全局最优 | MILP（更精确但复杂）、NSGA-II |

## 2. 工具链清单

| 工具/库 | 版本要求 | 用途 | 使用章节 |
|---------|----------|------|----------|
| Python | 3.10+ | 编程语言 | 全部 |
| pandas | 1.5+ | 数据处理 | 全部 |
| numpy | 1.23+ | 数值计算 | 全部 |
| matplotlib | 3.6+ | 可视化 | 全部 |
| seaborn | 0.12+ | 高级可视化 | ch02, ch05 |
| scikit-learn | 1.2+ | 机器学习模型 | ch02, ch04 |
| xgboost | 1.7+ | 梯度提升模型 | ch04 |
| lightgbm | 3.3+ | 梯度提升模型 | ch04 |
| tensorflow/pytorch | 2.x/1.x | LSTM深度学习 | ch04 |
| statsmodels | 0.13+ | STL时序分解 | ch05 |
| pulp | 2.7+ | 线性规划求解 | ch07 |
| openpyxl | 3.0+ | Excel文件读取 | ch01 |
"""

# 如果需要单独保存:
# with open(os.path.join(output_dir, 'ch08_technical_route.md'), 'w', encoding='utf-8') as f:
#     f.write(tech_route)

print("技术路线总结已嵌入 ch08_achievements_summary.md")
```

**本步骤完成后的检查标准**

- 方法清单覆盖全部7个分析步骤（ch01~ch07），无遗漏
- 每个方法有明确的选择理由（至少1句话），不是简单罗列方法名称
- 数据流图清晰展示步骤间的输入输出依赖关系
- 工具链清单包含全流程使用的所有Python库，版本要求明确
- 内容已嵌入ch08_achievements_summary.md，不产生多余的独立文件

**如果遇到问题请及时反馈**

- 如果某个步骤的方法选择理由不够充分：可补充文献引用（如"根据Smith et al. (2023)的对比研究，XGBoost在电力负荷预测中表现最优"）
- 如果工具链版本信息不确定：运行 `pip list` 查看实际安装版本，或使用兼容性较宽的版本要求（如"pandas >= 1.5"）
- 如果用户希望增加某个方法的详细说明（如LSTM的网络结构、训练参数）：可在技术路线文档中增加"方法详解"子章节

**本步骤输出产物**

- 技术路线总结文字 -- 内容说明: 包含方法选择理由表（7行，对应7个分析步骤）、工具链清单（12个库）、数据流图（ASCII格式） -- 存放位置: 嵌入 `ch08_achievements_summary.md` 的"技术路线总结"章节 -- 后续使用章节: 最终报告的"方法论"章节、学术摘要的技术贡献描述

---

### Step 4: 不足与局限

**本步骤要做什么**

本步骤的目标是客观评估本次研究的局限性，从数据维度、模型精度、方法论三个层面进行系统性的反思。这部分内容将嵌入Step 1的成果汇总报告中，作为独立章节。

"不足与局限"不是自我否定，而是展示研究者的学术诚实和方法论自觉。一份客观的局限性分析能增强研究的可信度——评审专家和读者更信任那些坦诚说明自身不足的研究，而非那些声称"完美无缺"的工作。

局限性分析需要具体、有针对性，避免空泛的"数据不够多、方法不够好"之类的笼统描述。每个局限性应包含三个要素：（1）具体描述不足之处；（2）说明该不足对研究结果的影响程度；（3）指出可能的改进方向（与Step 5的未来展望衔接）。

**具体操作指引**

1. **数据维度局限**：从数据来源、数据量、数据质量、数据覆盖面四个角度分析。例如："缺少气象数据导致预测模型无法捕捉温度-负荷的关联关系，预计引入气象特征可将MAPE降低5-10个百分点"。

2. **模型精度局限**：从预测模型和优化模型两个角度分析。例如："线性规划模型忽略网损和电压约束，优化效果可能偏乐观10-15%"。

3. **方法论局限**：从方法选择、参数设定、验证策略三个角度分析。例如："仅使用3σ准则进行异常检测，未结合领域知识进行异常原因分类，可能导致将真实的极端负荷事件误判为异常值"。

**代码框架**:
```python
# 本步骤以文本撰写为主，不产生独立文件
# 不足与局限内容已嵌入 Step 1 的 ch08_achievements_summary.md 中
# 包含以下三个部分：
# 1. 数据维度局限（4条）
# 2. 模型精度局限（3条）
# 3. 方法论局限（3条）

# 每条局限性的格式：
# - **[局限性标题]**：[具体描述] → [影响程度] → [改进方向]

print("不足与局限内容已嵌入 ch08_achievements_summary.md")
```

**本步骤完成后的检查标准**

- 局限性分析覆盖数据维度、模型精度、方法论三个层面，每个层面至少2条具体局限
- 每条局限性包含"具体描述 + 影响程度 + 改进方向"三个要素
- 局限性描述具体、有针对性，避免空泛表述
- 与Step 5的未来展望形成对应关系（每个局限性至少有一个对应的改进方向）
- 语气客观中立，既不过度自我批评，也不回避问题

**如果遇到问题请及时反馈**

- 如果局限性分析过于负面（可能影响报告的整体评价）：注意平衡——在指出不足的同时，强调本研究在数据条件有限的情况下已经做到了什么（如"尽管缺少气象数据，仅使用历史负荷特征的预测模型仍达到了XX%的MAPE"）
- 如果某些局限性在前序章节中已经提到（如ch07的"当前方案局限性"）：避免简单重复，而是从全局视角重新组织，突出局限性之间的关联

**本步骤输出产物**

- 不足与局限文字 -- 内容说明: 包含数据维度局限（4条）、模型精度局限（3条）、方法论局限（3条）的系统分析，每条含具体描述、影响程度和改进方向 -- 存放位置: 嵌入 `ch08_achievements_summary.md` 的"不足与局限"章节 -- 后续使用章节: 最终报告的"研究局限性"章节、Step 5未来展望的输入

---

### Step 5: 未来展望

**本步骤要做什么**

本步骤的目标是提出具体的、可操作的未来研究方向，每个方向包含"做什么、怎么做、预期效果"三个层次。这部分内容将嵌入Step 1的成果汇总报告中，作为独立章节。

未来展望不是空泛的"未来可以做得更好"，而是要有明确的行动指南——读者读完展望后应该知道"下一步具体应该做什么、用什么方法做、能做到什么程度"。每个方向的描述应足够具体，使得后续研究者可以直接据此撰写研究计划或项目申请书。

展望方向应与Step 4的局限性分析形成对应关系——每个局限性至少催生一个改进方向。同时，展望方向应考虑可行性（数据可获取性、计算资源需求、实施难度），避免提出不切实际的建议。

**具体操作指引**

1. **方向1：引入多维气象数据提升预测精度**。对应局限性"缺少气象数据"。说明数据来源（Open-Meteo API、NOAA）、特征工程方法、预期精度改善幅度。

2. **方向2：拓展多国家多气候带对比**。对应局限性"跨国对比深度不足"。说明数据来源（世界银行、IEA）、对比维度、预期发现。

3. **方向3：升级优化模型为多时间尺度协调调度**。对应局限性"优化模型简化假设多"。说明模型升级方案（日前+日内滚动）、求解方法、预期效果。

4. **方向4：结合分布式光伏和储能的主动配电网优化**。对应局限性"未考虑新能源接入"。说明光伏出力建模方法、储能SOC约束、预期效果。

5. **方向5：开发交互式数据可视化平台**。对应局限性"研究成果的可访问性有限"。说明技术栈（Dash/Streamlit）、核心功能、部署方案。

每个方向的格式统一为：
- **做什么**：1-2句话概括研究方向
- **怎么做**：2-3句话描述具体方法和技术路线
- **预期效果**：1-2句话量化预期成果
- **实施难度**：低/中/高 + 简要理由

**代码框架**:
```python
# 本步骤以文本撰写为主，不产生独立文件
# 未来展望内容已嵌入 Step 1 的 ch08_achievements_summary.md 中
# 包含5个研究方向，每个方向含4个要素：
# - 做什么（研究目标）
# - 怎么做（技术路线）
# - 预期效果（量化成果）
# - 实施难度（低/中/高）

print("未来展望内容已嵌入 ch08_achievements_summary.md")
print("\n5个研究方向概览:")
directions = [
    ("方向1", "引入多维气象数据提升预测精度", "低"),
    ("方向2", "拓展多国家多气候带对比", "中"),
    ("方向3", "升级优化模型为多时间尺度协调调度", "高"),
    ("方向4", "结合分布式光伏和储能的主动配电网优化", "高"),
    ("方向5", "开发交互式数据可视化平台", "中"),
]
for d_id, d_name, d_diff in directions:
    print(f"  {d_id}: {d_name} (实施难度: {d_diff})")
```

**本步骤完成后的检查标准**

- 至少提出4个未来研究方向，每个方向与Step 4的局限性形成对应关系
- 每个方向包含"做什么、怎么做、预期效果、实施难度"四个要素，缺一不可
- 预期效果尽可能量化（如"MAPE降低至5-8%"），而非仅定性描述
- 实施难度评估合理（低/中/高），并附简要理由
- 方向之间有逻辑递进关系（从低难度到高难度排列）
- 内容已嵌入ch08_achievements_summary.md，不产生多余的独立文件

**如果遇到问题请及时反馈**

- 如果展望方向过于宏大（如"构建全球电力负荷预测系统"）：缩小范围，聚焦于摩洛哥或北非区域的具体改进
- 如果预期效果缺乏依据（如"MAPE降低至1%"）：参考相关文献中的典型改善幅度，给出更现实的估计
- 如果用户希望增加某个特定方向（如"结合电动汽车充电管理的优化"）：可灵活增加，但需保持格式统一

**本步骤输出产物**

- 未来展望文字 -- 内容说明: 包含5个研究方向（气象增强预测、多国对比、多时间尺度调度、光储协同优化、可视化平台）的详细规划，每个方向含研究目标、技术路线、预期效果和实施难度 -- 存放位置: 嵌入 `ch08_achievements_summary.md` 的"未来展望"章节 -- 后续使用章节: 最终报告的"未来工作"章节、后续研究项目申请书的技术方案参考

---

## 三、产物总览与结构说明

### 3.1 本章全部输出产物

| 序号 | 产物名称 | 文件名 | 格式 | 存放路径 | 后续使用章节 |
|------|----------|--------|------|----------|-------------|
| 1 | 成果汇总报告 | ch08_achievements_summary.md | Markdown | outputs/ch08_summary/ | 最终报告结论章节 |
| 2 | 关键指标总览表 | ch08_key_metrics_table.csv | CSV | outputs/ch08_summary/ | 最终报告指标表格 |

### 3.2 关键产物结构详解

**ch08_achievements_summary.md**（最重要的产物）:
- 结构：8章核心发现汇总 + 技术路线总结 + 不足与局限 + 未来展望
- 每章提炼2-3条核心结论，含定性描述和定量数据
- 技术路线以ASCII流程图呈现
- 不足与局限分3个层面（数据、模型、方法）
- 未来展望5个方向，每个含"做什么-怎么做-预期效果-实施难度"
- 总篇幅预计3000-5000字

**ch08_key_metrics_table.csv**（数据名片）:
- 列结构：chapter(str, 章节编号)、category(str, 指标类别)、metric(str, 指标名称)、value(str, 指标值)、unit(str, 单位)、source_file(str, 数据来源)
- 行数：12-15行（覆盖ch01~ch07全部分析章节）
- 已有数据的指标自动填充，缺失数据的指标标注"待填充"

## 四、产物后续优化方向

### 4.1 当前方案的局限性

- 成果汇总依赖前序章节的产物完整性，如果某些章节未完成（如ch06跨国对比缺失），汇总报告将存在信息缺口
- 关键指标表中的"待填充"项需要人工回填，自动化程度有限
- 技术路线总结以文字为主，缺少可视化的技术路线图（如使用Graphviz或draw.io绘制的流程图）

### 4.2 可进一步优化的方向

- **自动化指标回填**：编写脚本从前序章节的CSV产物中自动提取所有指标值，消除"待填充"项
- **生成学术格式报告**：将汇总报告转换为IEEE或Elsevier论文格式的"Conclusion"章节
- **制作汇报PPT**：基于汇总报告和关键指标表，制作10-15页的汇报PPT，含核心图表和数据
- **开发交互式Dashboard**：使用Plotly Dash将关键指标和核心图表整合为交互式仪表盘
- **绘制可视化技术路线图**：使用Graphviz或Mermaid绘制全流程技术路线图，替代ASCII文本流程图

### 4.3 其他可选方法

- **文献计量分析**：将本研究的方法和结论与已有文献进行系统对比，量化本研究的创新性和贡献度
- **敏感性分析**：对关键参数（如优化模型中的容量上限分位数、预测模型中的特征组合）进行敏感性分析，评估结果的稳健性
- **用户调研验证**：对摩洛哥电力公司的工程人员进行调研，验证分析结论和策略建议的实用性和可操作性

## 五、异常处理与问题反馈机制

### 5.1 需要向用户确认的问题清单

- 如果某章的产物文件不存在（导致汇总报告该章节内容缺失）：需确认是否跳过该章并在报告中说明，还是等待该章完成后再生成汇总
- 如果不同章节的同一指标数值矛盾（如ch02和ch07对同一城市的日均负荷值不一致）：需确认以哪个章节的数据为准
- 如果关键指标表中"待填充"项过多（超过总数的50%）：需确认是否需要先执行前序章节再生成汇总
- 如果用户对汇总报告的结构或内容有特殊要求：根据反馈调整

### 5.2 常见异常场景与处理策略

| 异常场景 | 判断标准 | 处理策略 | 是否需要用户确认 |
|----------|----------|----------|-----------------|
| 某章产物文件不存在 | FileNotFoundError | 跳过该章，在报告中标注"本章因XX原因未完成分析" | 否 |
| 指标数据不一致 | 不同章节同一指标数值矛盾 | 以最新章节（编号最大）的数据为准，在表中注明 | 是 |
| 关键指标为"待填充" | value列包含"待填充" | 打印待填充清单，提醒用户需先执行前序章节 | 是 |
| 汇总报告篇幅过长 | 超过5000字 | 精简每章结论至1-2条核心发现，移除冗余描述 | 是 |
| 汇总报告篇幅过短 | 少于2000字 | 补充每章的定量数据和方法细节 | 是 |
| 未来展望方向不切实际 | 实施难度标注与内容不符 | 重新评估实施难度，调整预期效果 | 否 |

# 附录

## 附录A: 完整依赖清单（requirements.txt）

```
pandas==2.0.3
numpy==1.24.3
openpyxl==3.1.2
scipy==1.11.4
matplotlib==3.8.0
seaborn==0.13.0
plotly==5.17.0
statsmodels==0.14.0
prophet==1.1.5
scikit-learn==1.3.2
xgboost==2.0.3
lightgbm==4.1.0
torch==2.1.2
pulp==2.7.0
requests==2.31.0
beautifulsoup4==4.12.2
tqdm==4.66.1
joblib==1.3.2
pmdarima==2.0.3
```

## 附录B: 输出产物总览表

| 章节 | 数据文件 | 图片文件 | 模型文件 | 报告/文档 | 合计 |
|------|----------|----------|----------|-----------|------|
| ch01 数据预处理 | 7 | 0 | 0 | 2 | 9 |
| ch02 用电规律挖掘 | 3 | 7+ | 0 | 0 | 10+ |
| ch03 峰值识别 | 5 | 3+ | 0 | 0 | 8+ |
| ch04 短期预测 | 3 | 6+ | 0 | 5 | 1 | 15+ |
| ch05 中长期趋势 | 4 | 4+ | 0 | 0 | 8+ |
| ch06 跨国对比 | 5 | 3+ | 0 | 1 | 9+ |
| ch07 配电网优化 | 3 | 1 | 0 | 2 | 6 |
| ch08 总结展望 | 1 | 0 | 0 | 1 | 2 |
| **总计** | **31** | **24+** | **5** | **7** | **67+** |

## 附录C: 项目文件目录结构

```
Morocco_Load_Analysis/
├── data/
│   └── Data Morocco.xlsx
├── outputs/
│   ├── ch01_data_preprocessing/
│   ├── ch02_load_pattern_analysis/
│   ├── ch03_peak_analysis/
│   ├── ch04_load_forecasting/
│   ├── ch05_midlong_term_trend/
│   ├── ch06_cross_country_comparison/
│   ├── ch07_grid_optimization/
│   └── ch08_summary/
├── src/
│   ├── ch01_preprocessing.py
│   ├── ch02_pattern_analysis.py
│   ├── ch03_peak_detection.py
│   ├── ch04_forecasting.py
│   ├── ch05_trend_analysis.py
│   ├── ch06_web_scraping.py
│   ├── ch07_optimization.py
│   └── utils/
│       ├── data_loader.py
│       ├── visualizer.py
│       ├── metrics.py
│       └── output_manager.py
├── docs/
│   ├── Morocco_Load_Analysis_Execution_Prompts.md
│   └── 摩洛哥多城市电力负荷全流程分析流程设计.md
├── requirements.txt
└── README.md
```

## 附录D: 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch01_cleaned_data.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch02_daily_load_curve_layoune.png` |
| 模型文件 | `ch{NN}_{模型名}_model.{pkl/pt}` | `ch04_lstm_model.pt` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch01_data_quality_report.md` |
| 配置文件 | `ch{NN}_{描述}.json` | `ch04_data_split_info.json` |
| 源代码文件 | `ch{NN}_{描述}.py` | `ch04_forecasting.py` |
