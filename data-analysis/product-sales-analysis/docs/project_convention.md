# Product_Sales_Analysis — 项目规范文档

> 项目名称：Product_Sales_Analysis  
> 项目描述：产品销售数据分析  
> Python 版本：3.10  
> 环境名称：py310  
> 生成日期：2026-05-08  
> 文档版本：v1.0

---

## 一、项目结构总览

### 1.1 目录树

```
Product_Sales_Analysis/
├── data/                                    # 原始数据目录（只读）
│   └── product_sales_dataset.csv
├── src/
│   ├── utils/                               # 通用工具模块
│   │   ├── __init__.py
│   │   ├── config.py                        # 全局配置
│   │   ├── data_loader.py                   # 数据加载器
│   │   ├── visualizer.py                    # 可视化出图器
│   │   ├── metrics.py                       # 评估指标计算器
│   │   ├── output_manager.py                # 输出产物管理器
│   │   └── task_graph.py                    # 任务依赖图
│   ├── ch01_data_cleaning/                  # 数据清洗
│   │   ├── script.py
│   │   └── notebook.ipynb
│   ├── ch02_descriptive_analysis/           # 描述性统计与可视化
│   │   ├── script.py
│   │   └── notebook.ipynb
│   ├── ch03_sales_forecasting/              # 销售趋势预测
│   │   ├── script.py
│   │   └── notebook.ipynb
│   ├── ch04_price_elasticity/               # 价格弹性分析
│   │   ├── script.py
│   │   └── notebook.ipynb
│   └── ch05_conclusions_and_recommendations/ # 结论与业务建议
│       ├── script.py
│       └── notebook.ipynb
├── outputs/                                 # 产物输出目录
│   ├── ch01_data_cleaning/
│   │   ├── ch01_cleaned_data.csv
│   │   └── report.md
│   ├── ch02_descriptive_analysis/
│   │   ├── descriptive_stats.csv
│   │   ├── category_summary.csv
│   │   ├── city_summary.csv
│   │   ├── product_ranking.csv
│   │   ├── monthly_trend.csv
│   │   ├── *.png（6 张可视化图表）
│   │   └── report.md
│   ├── ch03_sales_forecasting/
│   │   ├── monthly_sales.csv
│   │   ├── moving_average.csv
│   │   ├── forecast_results.csv
│   │   ├── error_metrics.csv
│   │   ├── *.png（3 张可视化图表）
│   │   └── report.md
│   ├── ch04_price_elasticity/
│   │   ├── price_elasticity.csv
│   │   ├── *.png（3 张可视化图表）
│   │   └── report.md
│   └── ch05_conclusions_and_recommendations/
│       ├── key_metrics_summary.csv
│       ├── *_recommendations.csv（3 张策略表）
│       └── report.md
├── docs/                                    # 文档目录
│   ├── analysis_goals.md                    # 分析目标文档
│   ├── flow_design.md                       # 研究设计文档
│   └── project_convention.md                # 本文档
├── templates/                               # 模板目录
│   └── flow_design_template.md              # 章节设计模板
├── .learnings/                              # 经验学习日志
│   ├── LEARNINGS.md
│   ├── ERRORS.md
│   └── FEATURE_REQUESTS.md
├── project_params.json                      # 项目参数配置
├── requirements.txt                         # Python 依赖清单
└── README.md                                # 项目说明（可选）
```

### 1.2 文件分类规则

| 目录 | 文件类型 | 读写权限 | 说明 |
|------|---------|---------|------|
| `data/` | 原始数据 | 只读 | 禁止修改，保持数据原始性 |
| `src/utils/` | 工具模块 | 可读写 | 通用工具，所有章节共享 |
| `src/chXX_*/` | 章节脚本 | 可读写 | 每章独立目录 |
| `outputs/chXX_*/` | 分析产物 | 只写 | 每章独立输出目录 |
| `docs/` | 文档 | 可读写 | 项目文档 |
| `templates/` | 模板 | 只读 | 可复用模板 |

---

## 二、命名规范

### 2.1 目录命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 章节目录 | `ch{NN}_{dir_suffix}` | `ch01_data_cleaning` |
| 输出目录 | 与章节目录同名 | `outputs/ch01_data_cleaning/` |
| 工具目录 | `utils` | `src/utils/` |

### 2.2 脚本命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 批量执行脚本 | `script.py` | `src/ch01_data_cleaning/script.py` |
| 交互式 Notebook | `notebook.ipynb` | `src/ch01_data_cleaning/notebook.ipynb` |
| 工具模块 | `snake_case.py` | `data_loader.py`, `visualizer.py` |

### 2.3 产物命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 数据文件 | `{描述}.csv` | `category_summary.csv` |
| 图表文件 | `{描述}.png` | `category_sales_bar.png` |
| 报告文件 | `report.md` | 每章固定为 `report.md` |
| 配置文件 | `{描述}.json` | `project_params.json` |

### 2.4 变量命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 常量 | `UPPER_SNAKE_CASE` | `CATEGORY_LIST`, `OUTPUT_BASE` |
| 变量 | `snake_case` | `cleaned_df`, `monthly_sales` |
| 函数 | `snake_case` | `load_raw_data()`, `plot_category_sales()` |
| 类 | `PascalCase` | `TaskGraph`, `OutputManager` |

---

## 三、脚本编写规范

### 3.1 Python 脚本结构（script.py）

每个章节的 `script.py` 遵循以下统一结构：

```python
"""
ch{NN} {章节中文名}
{一句话描述本章功能}
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 标准库导入
import pandas as pd
import numpy as np

# 第三方库导入
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt

# 项目工具导入
from utils.config import *
from utils.data_loader import load_preprocessed
from utils.output_manager import ensure_dir, save_dataframe, save_figure, save_markdown

def main():
    """主执行函数"""
    # Step 1: 初始化输出目录
    output_dir = os.path.join(OUTPUT_BASE, 'ch{NN}_{dir_suffix}')
    ensure_dir(output_dir)
    
    # Step 2: 数据加载
    df = load_preprocessed('ch01')
    
    # Step 3-N: 分析步骤
    
    # 最后一步: 生成报告
    report = """# ch{NN} {章节标题}\n\n## 背景\n...\n\n## 分析方法\n...\n\n## 分析发现\n...\n\n## 小结\n..."""
    save_markdown(report, 'report.md', output_dir)
    print(f"[ch{NN}] 分析完成，产物保存至 {output_dir}")

if __name__ == '__main__':
    main()
```

### 3.2 Notebook 结构（notebook.ipynb）

每个章节的 `notebook.ipynb` 遵循以下结构：

| Cell 序号 | 类型 | 内容 |
|-----------|------|------|
| 1 | Markdown | 章节标题 `# ch{NN} {章节中文名}` |
| 2 | Code | 导入库和初始化 |
| 3 | Markdown | 步骤说明 |
| 4 | Code | 步骤代码 |
| ... | ... | 交替 Markdown + Code |
| 最后 | Code | 生成 report.md |

**要求**：Notebook 与 script.py 的执行逻辑必须一致。

### 3.3 代码质量标准

| 标准 | 要求 |
|------|------|
| PEP 8 | 遵循 PEP 8 编码规范 |
| Docstring | 所有函数和类必须有 docstring |
| 类型注解 | 公共函数建议添加类型注解 |
| 中文注释 | 关键步骤添加中文注释 |
| matplotlib 后端 | 脚本中使用 `matplotlib.use('Agg')` |
| 路径处理 | 使用 `os.path.join()`，禁止硬编码路径 |
| 配置读取 | 使用 `utils/config.py`，禁止硬编码参数 |

### 3.4 可视化规范

| 标准 | 要求 |
|------|------|
| 中文字体 | 使用 `SimHei` 或 `Noto Sans CJK SC` |
| 图表尺寸 | 默认 `(10, 6)`，可通过 `PLT_CONFIG` 调整 |
| DPI | ≥ 150 |
| 标签 | 中文标签，包含单位和图例 |
| 配色 | 统一使用 seaborn 或 matplotlib 默认配色 |
| 保存格式 | PNG（统一） |

---

## 四、禁止事项清单

### 4.1 核心禁止事项（5 条）

| # | 禁止事项 | 原因 |
|---|---------|------|
| 1 | **禁止修改 `data/` 目录中的原始数据** | 保持数据原始性，确保可复现 |
| 2 | **禁止跨章节写入产物** | 产物归属清晰，避免冲突 |
| 3 | **禁止在项目根目录散落文件** | 保持目录整洁 |
| 4 | **禁止跳过依赖直接执行** | 确保数据依赖正确 |
| 5 | **禁止在代码中硬编码参数** | 统一使用 `utils/config.py` 管理 |

### 4.2 扩展禁止事项

| # | 禁止事项 | 原因 |
|---|---------|------|
| 6 | 禁止使用 `pd.read_csv()` 时省略 `encoding` 参数 | 避免编码问题 |
| 7 | 禁止在 Notebook 中使用 `!pip install` | 依赖统一在 `requirements.txt` 管理 |
| 8 | 禁止提交 `outputs/` 中的中间产物到版本控制 | 产物应通过脚本重新生成 |
| 9 | 禁止使用绝对路径引用数据文件 | 使用 `config.py` 中的相对路径 |
| 10 | 禁止覆盖 `utils/config.py` 中的配置项 | 配置变更需通过修改 config.py 统一进行 |

---

## 五、环境配置

### 5.1 环境初始化

```bash
# 创建 conda 环境
conda create -n py310 python=3.10 -y
conda activate py310

# 安装依赖
pip install -r requirements.txt --break-system-packages
```

### 5.2 运行脚本

```bash
# 激活环境
conda activate py310

# 运行单个章节
cd Product_Sales_Analysis
python src/ch01_data_cleaning/script.py

# 按依赖顺序运行全部章节
python src/ch01_data_cleaning/script.py
python src/ch02_descriptive_analysis/script.py
python src/ch03_sales_forecasting/script.py
python src/ch04_price_elasticity/script.py
python src/ch05_conclusions_and_recommendations/script.py
```

### 5.3 依赖管理

| 文件 | 说明 |
|------|------|
| `requirements.txt` | Python 依赖清单（pip install -r requirements.txt） |
| `project_params.json` | 项目参数配置（10 个核心参数） |

**依赖安装原则**：
- 基础依赖（pandas, numpy, matplotlib, seaborn）必须安装
- 可选依赖根据章节需求安装
- 禁止在代码中隐式导入未声明的依赖

---

## 六、产物完整性检查

### 6.1 通用检查项（所有章节）

- [ ] `outputs/chXX_{dir_suffix}/report.md` 已生成（四段框架：背景/分析方法/分析发现/小结）
- [ ] `src/chXX_{dir_suffix}/notebook.ipynb` 与 `script.py` 逻辑一致
- [ ] 所有产物文件保存在对应的 `outputs/chXX_*/` 目录下
- [ ] 图表文件为 PNG 格式，DPI ≥ 150
- [ ] 数据文件为 CSV 格式，编码 UTF-8
- [ ] 无硬编码路径，所有路径通过 `config.py` 管理

### 6.2 章节自定义检查项

#### ch01 数据清洗

- [ ] `ch01_cleaned_data.csv` 已生成
- [ ] 缺失值统计为 0（或已处理）
- [ ] 重复值统计为 0（或已处理）
- [ ] `Order_Date` 已转换为 datetime 类型
- [ ] 数据行数正确（1000 行）

#### ch02 描述性统计与可视化

- [ ] `descriptive_stats.csv` 已生成（含全部数值字段）
- [ ] `category_summary.csv` 已生成（覆盖 6 个品类）
- [ ] `city_summary.csv` 已生成（覆盖 5 个城市）
- [ ] `product_ranking.csv` 已生成（含 Top/Bottom 排名）
- [ ] `monthly_trend.csv` 已生成（覆盖全部月份）
- [ ] 6 张可视化图表已生成（PNG）
- [ ] 所有图表含中文标签和图例

#### ch03 销售趋势预测

- [ ] `monthly_sales.csv` 已生成（17 个月数据）
- [ ] `moving_average.csv` 已生成（SMA-3 和 SMA-6）
- [ ] `forecast_results.csv` 已生成（3 个月预测值）
- [ ] `error_metrics.csv` 已生成（MAE, RMSE）
- [ ] 3 张可视化图表已生成（PNG）
- [ ] MAE ≤ 月均销售额的 20%

#### ch04 价格弹性分析

- [ ] `price_elasticity.csv` 已生成（覆盖 6 个品类）
- [ ] 弹性系数计算正确（对数回归斜率）
- [ ] 弹性分类完整（弹性/刚性/单位弹性）
- [ ] 3 张可视化图表已生成（PNG）

#### ch05 结论与业务建议

- [ ] `key_metrics_summary.csv` 已生成
- [ ] 3 张策略建议表已生成（品类/区域/定价）
- [ ] 全部前序章节发现已纳入总结
- [ ] 每条建议有数据支撑
- [ ] 局限性分析覆盖数据、方法、范围三个维度

### 6.3 产物数量汇总

| 章节 | CSV | PNG | Markdown | 合计 |
|------|-----|-----|----------|------|
| ch01 | 1 | 0 | 1 | 2 |
| ch02 | 6 | 6 | 1 | 13 |
| ch03 | 4 | 3 | 1 | 8 |
| ch04 | 1 | 3 | 1 | 5 |
| ch05 | 4 | 0 | 1 | 5 |
| **总计** | **16** | **12** | **5** | **33** |

---

## 七、章节依赖关系

```
ch01 数据清洗（无依赖）
    │
    ├──▶ ch02 描述性统计与可视化（依赖 ch01）
    │       │
    │       ├──▶ ch03 销售趋势预测（依赖 ch01, ch02）
    │       │
    │       └──▶ ch04 价格弹性分析（依赖 ch01, ch02）
    │               │
    │               └──▶ ch05 结论与业务建议（依赖 ch02, ch03, ch04）
```

### 执行批次

| 批次 | 章节 | 可并行 | 说明 |
|------|------|--------|------|
| Batch 1 | ch01 | 否 | 数据清洗，所有后续章节的基础 |
| Batch 2 | ch02 | 否 | 描述性分析，ch03/ch04 的输入 |
| Batch 3 | ch03, ch04 | 是 | 预测和弹性分析互不依赖，可并行 |
| Batch 4 | ch05 | 否 | 综合建议，依赖全部前序章节 |

---

## 八、report.md 四段框架

每个章节的 `report.md` 必须遵循以下固定四段框架：

```markdown
# ch{NN} {章节标题}

## 背景
{本章输入数据的来源、特征、规模；本章要解决的核心问题；前置章节的产物依赖}

## 分析方法
{采用的分析方法/模型/算法及选择理由；关键参数设置；数据预处理策略}

## 分析发现
{核心发现与关键数据支撑；可视化图表解读；异常值或特殊情况说明}

## 小结
{结论性摘要；产物清单；对下游章节的影响或建议}
```

> **原则**：四段框架是骨架，每段内部的小节和内容由执行者根据分析实际内容自由组织，不做硬性限制。

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-05-08 | 初始版本，5 章节规范 |
