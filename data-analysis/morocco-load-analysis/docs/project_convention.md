# 摩洛哥电力负荷分析 — 项目规范 (Project Convention)

> **本文档是项目唯一规范依据。** 所有执行者（人 / AI）在动手前必须先阅读本文档。
> 派活时只需一句话：**"参考 `docs/project_convention.md`，执行 Prompt-XX。"**

---

## 一、项目结构总览

```
Morocco_Load_Analysis/
├── data/                              # 📁 原始数据（只读，不可修改）
│   └── Data Morocco.xlsx              #    唯一数据源
│
├── src/                               # 📁 源代码
│   ├── utils/                         #    通用工具模块（全章节共享）
│   │   ├── config.py                  #      全局配置：路径、参数、常量
│   │   ├── data_loader.py             #      Skill-01: 数据加载器
│   │   ├── output_manager.py          #      Skill-04: 输出产物管理器
│   │   └── task_graph.py              #      任务依赖图 + 进度检查
│   ├── ch01_preprocessing/            #    Prompt-01: 数据预处理
│   ├── ch02_load_pattern/             #    Prompt-02: 用电规律挖掘
│   ├── ch03_peak_analysis/            #    Prompt-03: 峰值识别
│   ├── ch04_load_forecasting/         #    Prompt-04: 短期负荷预测
│   ├── ch05_midlong_term_trend/       #    Prompt-05: 中长期趋势分析
│   ├── ch06_cross_country/            #    Prompt-06: 跨国对比
│   ├── ch07_grid_optimization/        #    Prompt-07: 配电网优化
│   └── ch08_summary/                  #    Prompt-08: 总结展望
│
├── outputs/                           # 📁 输出产物（每个章节独立子目录）
│   ├── ch01_data_preprocessing/
│   ├── ch02_load_pattern_analysis/
│   ├── ch03_peak_analysis/
│   ├── ch04_load_forecasting/
│   ├── ch05_midlong_term_trend/
│   ├── ch06_cross_country_comparison/
│   ├── ch07_grid_optimization/
│   └── ch08_summary/
│
├── docs/                              # 📁 项目文档
│   ├── project_convention.md          #    ← 你正在看的这份文档
│   ├── task_dispatch_guide.md         #    任务分发指南（依赖图 + 派活模板）
│   ├── 摩洛哥多城市电力负荷全流程分析流程设计.md  #    分析流程设计规范
│   └── Morocco_Load_Analysis_Execution_Prompts.md  #    各Prompt执行细节
│
├── requirements.txt                   # Python 依赖清单
└── morocco_load_data_preprocessing.ipynb  # 旧版Notebook（归档，不再使用）
```

---

## 二、文件分类规则

### 2.1 什么放哪里

| 文件类型 | 存放位置 | 规则 |
|----------|----------|------|
| **原始数据** | `data/` | 只读，唯一数据源，任何脚本不得修改此目录 |
| **脚本代码** | `src/chXX_xxx/` | 每个章节一个子目录，内含 `.py` + `.ipynb` |
| **通用工具** | `src/utils/` | 跨章节复用的模块（config、loader、manager 等） |
| **输出产物** | `outputs/chXX_xxx/` | 每个章节的产物写入对应子目录，互不干扰 |
| **项目文档** | `docs/` | 规范文档、设计文档、执行Prompt等 |
| **依赖清单** | 项目根目录 | `requirements.txt` 唯一一份 |

### 2.2 禁止事项

- ❌ 禁止在 `data/` 中写入任何文件
- ❌ 禁止在 `outputs/` 下跨章节写入（ch02 的产物不能写到 ch01 目录）
- ❌ 禁止在项目根目录散落脚本、数据、临时文件
- ❌ 禁止在 `src/` 下直接放 `.py` 文件（必须在 `chXX_xxx/` 或 `utils/` 子目录内）
- ❌ 禁止创建 `venv/` 目录（使用本地 conda 环境 `py310`）

---

## 三、命名规范

### 3.1 目录命名

| 层级 | 格式 | 示例 |
|------|------|------|
| 章节脚本目录 | `src/ch{NN}_{英文简称}/` | `src/ch02_load_pattern/` |
| 章节输出目录 | `outputs/ch{NN}_{英文全称}/` | `outputs/ch02_load_pattern_analysis/` |

### 3.2 脚本命名

| 类型 | 格式 | 说明 |
|------|------|------|
| Python 脚本 | `{动作}.py` | 如 `preprocess.py`, `analysis.py`, `forecast.py` |
| Jupyter Notebook | `{动作}.ipynb` | 与 `.py` 同名，内容对应 |

### 3.3 产物命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch02_descriptive_stats.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch02_daily_load_curve.png` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch02_load_pattern_report.md` |
| 模型文件 | `ch{NN}_{模型名}.pkl` | `ch04_lstm_model.pkl` |

**前缀 `ch{NN}_` 是强制的**，确保产物归属清晰。

---

## 四、脚本编写规范

### 4.1 每个章节必须提供两种格式

```
src/chXX_xxx/
├── analysis.py       # 可直接运行: python src/chXX_xxx/analysis.py
└── analysis.ipynb    # Jupyter 交互式: jupyter notebook src/chXX_xxx/analysis.ipynb
```

- `.py` 和 `.ipynb` 逻辑完全一致，`.ipynb` 是 `.py` 的分步展开版
- `.py` 用于批量执行，`.ipynb` 用于逐步学习和调试

### 4.2 脚本结构模板

每个 `.py` 脚本必须遵循以下结构：

```python
"""
Prompt-XX: {章节名称}
{一句话描述}

覆盖步骤:
  - Step X.1: ...
  - Step X.2: ...
  ...

产物输出到: outputs/chXX_xxx/
"""

import sys, os
# 路径设置（确保能导入 utils）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

# 导入项目工具
from utils.config import CITIES, OUTPUT_BASE, ...
from utils.data_loader import load_preprocessed
from utils.output_manager import save_dataframe, save_figure, save_markdown

def main():
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'chXX_xxx')
    # ... 业务逻辑 ...

if __name__ == '__main__':
    main()
```

### 4.3 Notebook 结构模板

每个 `.ipynb` 必须遵循以下结构：

```
Cell 0 [Markdown]: 标题 + 环境说明 + 规范文档引用
Cell 1 [Code]:     导入 + 路径设置 + 配置加载
Cell 2 [Markdown]: Step X.1 说明（目标 + 方法 + 产物）
Cell 3 [Code]:     Step X.1 实现
Cell 4 [Markdown]: Step X.2 说明
Cell 5 [Code]:     Step X.2 实现
...
Cell N [Code]:     总结
```

### 4.4 Kernel 配置

```json
"kernelspec": {
    "display_name": "Python 3.10 (py310)",
    "language": "python",
    "name": "py310"
}
```

---

## 五、环境配置

```bash
# 激活环境
conda activate py310

# 安装依赖（首次）
cd Morocco_Load_Analysis
pip install -r requirements.txt

# 运行脚本
python src/chXX_xxx/analysis.py

# 运行 Notebook
jupyter notebook src/chXX_xxx/analysis.ipynb
# → 选择 Kernel: "Python 3.10 (py310)"
```

---

## 六、派活标准话术

### 6.1 派单个章节（最常用）

```
【摩洛哥电力负荷分析 — Prompt-XX】

参考 docs/project_convention.md 和 docs/task_dispatch_guide.md
执行 Prompt-XX: {章节名称}

环境: conda activate py310
规范: docs/摩洛哥多城市电力负荷全流程分析流程设计.md
细节: docs/Morocco_Load_Analysis_Execution_Prompts.md
```

### 6.2 检查进度

```
检查摩洛哥电力负荷分析进度:
python src/utils/task_graph.py
```

### 6.3 从零启动整个项目

```
【摩洛哥电力负荷分析 — 完整项目】

参考 docs/project_convention.md（结构规范）
参考 docs/task_dispatch_guide.md（依赖图 + 批次划分）

环境: conda activate py310
Batch-0 → Batch-1(并行) → Batch-2 → Batch-3 → Batch-4 → Batch-5
```

---

## 七、产物完整性检查

每个章节完成后，必须确认以下检查项：

- [ ] `outputs/chXX_xxx/` 目录下产物齐全
- [ ] 所有数据文件以 `ch{NN}_` 开头
- [ ] 所有图片以 `ch{NN}_` 开头，DPI ≥ 150
- [ ] 脚本可在 `conda activate py310` 下无报错运行
- [ ] `.py` 和 `.ipynb` 逻辑一致
- [ ] 运行 `python src/utils/task_graph.py` 状态更新为 ✅
