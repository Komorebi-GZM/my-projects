# UCI 胆结石数据集分析 — 项目规范 (Project Convention)

> **本文档是项目唯一规范依据。** 所有执行者（人 / AI）在动手前必须先阅读本文档。
> 派活时只需一句话：**"参考 `docs/project_convention.md`，执行 Prompt-XX。"**

---

## 〇、十参数配置表

| # | 参数 | 值 |
|---|------|-----|
| 1 | 项目名称 | `gallstone_analysis` |
| 2 | 项目描述 | UCI 胆结石数据集分析 |
| 3 | 原始数据文件名 | `dataset-uci.xlsx` |
| 4 | 数据格式 | `xlsx` |
| 5 | 分析实体名称 | 患者 (Patient) |
| 6 | 实体配置 | `["Gallstone_Status=0 (无胆结石)", "Gallstone_Status=1 (有胆结石)"]` |
| 7 | 章节列表 | 见下方 §0.1 |
| 8 | 章节依赖关系 | 见下方 §0.2 |
| 9 | Python 版本 | `3.10` |
| 10 | 环境配置 | `py310` / `conda` |

### §0.1 章节列表

```json
[
  {"id": 1, "name_cn": "数据预处理",       "name_en": "preprocessing",      "dir_suffix": "preprocessing"},
  {"id": 2, "name_cn": "探索性数据分析",   "name_en": "eda",                "dir_suffix": "eda"},
  {"id": 3, "name_cn": "统计检验",         "name_en": "statistical_test",   "dir_suffix": "statistical_test"},
  {"id": 4, "name_cn": "特征筛选",         "name_en": "feature_selection",  "dir_suffix": "feature_selection"},
  {"id": 5, "name_cn": "建模预测",         "name_en": "modeling",           "dir_suffix": "modeling"},
  {"id": 6, "name_cn": "总结报告",         "name_en": "summary",            "dir_suffix": "summary"}
]
```

### §0.2 章节依赖关系

```json
{
  "ch01": [],
  "ch02": ["ch01"],
  "ch03": ["ch01", "ch02"],
  "ch04": ["ch01", "ch02", "ch03"],
  "ch05": ["ch01", "ch04"],
  "ch06": ["ch01", "ch02", "ch03", "ch04", "ch05"]
}
```

**依赖图**：

```
ch01 (数据预处理)
  ├── ch02 (探索性分析)
  │     ├── ch03 (统计检验)
  │     │     └── ch04 (特征筛选)
  │     │           └── ch05 (建模预测)
  │     │                 └── ch06 (总结报告)
  │     └─────────────────┘
  └───────────────────────────────────────┘
```

---

## 一、项目结构总览

```
gallstone_analysis/
├── data/                              # 原始数据（只读，不可修改）
│   └── dataset-uci.xlsx               #    唯一数据源
│
├── src/                               # 源代码
│   ├── utils/                         #    通用工具模块（全章节共享）
│   │   ├── config.py                  #      全局配置：路径、参数、常量
│   │   ├── data_loader.py             #      Skill-01: 数据加载器
│   │   ├── output_manager.py          #      Skill-04: 输出产物管理器
│   │   └── task_graph.py              #      任务依赖图 + 进度检查
│   ├── ch01_preprocessing/            #    ch01: 数据预处理
│   │   ├── preprocess.py
│   │   └── preprocess.ipynb
│   ├── ch02_eda/                      #    ch02: 探索性数据分析
│   │   ├── eda.py
│   │   └── eda.ipynb
│   ├── ch03_statistical_test/         #    ch03: 统计检验
│   │   ├── stat_test.py
│   │   └── stat_test.ipynb
│   ├── ch04_feature_selection/        #    ch04: 特征筛选
│   │   ├── feature_select.py
│   │   └── feature_select.ipynb
│   ├── ch05_modeling/                 #    ch05: 建模预测
│   │   ├── modeling.py
│   │   └── modeling.ipynb
│   └── ch06_summary/                  #    ch06: 总结报告
│       ├── summary.py
│       └── summary.ipynb
│
├── outputs/                           # 输出产物（每个章节独立子目录）
│   ├── ch01_preprocessing/            #    ch01 产物
│   │   ├── ch01_cleaned_dataset.csv
│   │   ├── ch01_cleaned_dataset.xlsx
│   │   ├── ch01_outlier_report.csv
│   │   ├── ch01_cleaned_data_statistics.csv
│   │   ├── ch01_boxplot_before_after.png
│   │   ├── ch01_histogram_cleaned.png
│   │   ├── ch01_correlation_heatmap.png
│   │   └── ch01_target_distribution.png
│   ├── ch02_eda/                      #    ch02 产物
│   ├── ch03_statistical_test/         #    ch03 产物
│   ├── ch04_feature_selection/        #    ch04 产物
│   ├── ch05_modeling/                 #    ch05 产物
│   └── ch06_summary/                  #    ch06 产物
│
├── docs/                              # 项目文档
│   ├── project_convention.md          #    项目规范（本文档）
│   ├── gallstone_analysis_流程设计.md  #    流程设计文档
│   ├── task_dispatch_guide.md         #    任务分发指南（依赖图 + 派活模板）
│   └── gallstone_analysis_Execution_Prompts.md  #    各 Prompt 执行细节
│
├── requirements.txt                   # Python 依赖清单
└── README.md                          # 项目说明（可选）
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
| **项目文档** | `docs/` | 规范文档、设计文档、执行 Prompt 等 |
| **依赖清单** | 项目根目录 | `requirements.txt` 唯一一份 |

### 2.2 禁止事项

- ❌ 禁止在 `data/` 中写入任何文件
- ❌ 禁止在 `outputs/` 下跨章节写入（ch02 的产物不能写到 ch01 目录）
- ❌ 禁止在项目根目录散落脚本、数据、临时文件
- ❌ 禁止在 `src/` 下直接放 `.py` 文件（必须在 `chXX_xxx/` 或 `utils/` 子目录内）
- ❌ 禁止创建 `venv/` 目录（使用 conda 环境 `py310`）
- ❌ **禁止在代码中硬编码项目特定参数**（如文件路径、实体名称、领域常量等），所有参数必须通过 `src/utils/config.py` 统一管理

---

## 三、命名规范

### 3.1 目录命名

| 层级 | 格式 | 示例 |
|------|------|------|
| 章节脚本目录 | `src/ch{NN}_{英文简称}/` | `src/ch02_eda/` |
| 章节输出目录 | `outputs/ch{NN}_{英文简称}/` | `outputs/ch02_eda/` |

### 3.2 脚本命名

| 类型 | 格式 | 说明 |
|------|------|------|
| Python 脚本 | `{动作}.py` | 如 `preprocess.py`, `eda.py`, `modeling.py` |
| Jupyter Notebook | `{动作}.ipynb` | 与 `.py` 同名，内容对应 |

### 3.3 产物命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch01_cleaned_dataset.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch02_distribution_plot.png` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch03_statistical_test_report.md` |
| 模型文件 | `ch{NN}_{模型名}.pkl` | `ch05_random_forest.pkl` |

**前缀 `ch{NN}_` 是强制的**，确保产物归属清晰。

### 3.4 变量命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 常量 | `UPPER_SNAKE_CASE` | `OUTPUT_BASE`, `FIGURE_DPI` |
| 函数 | `snake_case` | `load_cleaned_data()`, `save_figure()` |
| 类 | `PascalCase` | `DataLoader`, `OutputManager` |
| 私有方法 | `_leading_underscore` | `_validate_input()`, `_parse_config()` |

### 3.5 配置命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 环境变量 | `UPPER_SNAKE_CASE` | `PYTHON_VERSION`, `DATA_DIR` |
| 配置文件键 | `snake_case` | `output_base`, `figure_dpi` |
| 命令行参数 | `--kebab-case` | `--output-dir`, `--figure-dpi` |

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

### 4.2 Python 脚本结构模板

每个 `.py` 脚本必须遵循以下结构：

```python
"""
Prompt-XX: {章节名称}
{章节描述}

覆盖步骤:
  - Step X.1: ...
  - Step X.2: ...
  ...

产物输出到: outputs/chXX_xxx/
"""

import sys
import os

# 路径设置（确保能导入 utils）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

# 导入项目工具
from utils.config import OUTPUT_BASE, FIGURE_DPI, ...
from utils.data_loader import load_cleaned_data
from utils.output_manager import save_dataframe, save_figure, save_markdown


def main():
    """主函数：执行本章全部分析步骤。"""
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'chXX_xxx')
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step X.1: {步骤描述}
    # ...

    # Step X.2: {步骤描述}
    # ...

    print(f"章节 XX 完成。产物已输出到: {OUTPUT_DIR}")


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

**Cell 0 Markdown 模板**：

```markdown
# Prompt-XX: {章节名称}

> **环境**: py310 (Python 3.10)
> **规范**: 参考 `docs/project_convention.md`
> **数据**: dataset-uci.xlsx

## 本章目标
{章节目标描述}
```

### 4.4 Kernel 配置

```json
"kernelspec": {
    "display_name": "Python 3.10 (py310)",
    "language": "python",
    "name": "py310"
}
```

### 4.5 代码质量规则

#### PEP8 合规

- 行长度不超过 88 字符
- 缩进使用 4 个空格
- 类和函数定义之间空两行
- 导入顺序：标准库 → 第三方库 → 项目内部模块，每组之间空一行
- 避免使用通配符导入（`from xxx import *`）

#### 类型注解

- 所有公共函数必须有参数类型注解和返回值类型注解
- 复杂数据结构使用 `typing` 模块（`List`, `Dict`, `Optional`, `Tuple` 等）

#### Docstring 规范

- 所有公共模块、类、函数必须有 docstring
- 使用 Google 风格 docstring
- docstring 必须包含：简要描述、Args、Returns、Raises（如有）

### 4.6 文档更新规则

- **修改代码后必须同步更新文档**：如果修改了脚本逻辑、产物格式、依赖关系，必须同步更新以下文档：
  - `docs/project_convention.md`：如果影响了项目结构、命名规范、脚本规范
  - `docs/task_dispatch_guide.md`：如果影响了依赖关系、批次划分、产物清单
  - 脚本内的 docstring：如果修改了函数签名、行为、产物

---

## 五、禁止事项清单

### 5.1 核心禁止事项（5 条）

| # | 禁止事项 | 原因 | 正确做法 |
|---|----------|------|----------|
| 1 | 禁止修改 `data/` 目录 | 原始数据是唯一数据源，修改后无法恢复 | 所有数据处理结果写入 `outputs/` |
| 2 | 禁止跨章节写入产物 | 产物归属混乱，后续引用困难 | 每个章节只写入自己的 `outputs/chXX_xxx/` |
| 3 | 禁止在根目录散落文件 | 项目结构混乱，难以维护 | 文件必须归入对应目录（data/src/outputs/docs） |
| 4 | 禁止跳过依赖直接执行 | 数据不一致，产物不可靠 | 严格按批次顺序执行 |
| 5 | 禁止在代码中硬编码参数 | 参数分散难以维护，换项目需大量修改 | 所有参数通过 `src/utils/config.py` 管理 |

### 5.2 扩展禁止事项

| # | 禁止事项 | 原因 | 正确做法 |
|---|----------|------|----------|
| 6 | 禁止在业务逻辑脚本中使用 `print()` 输出调试信息 | 污染标准输出 | 使用 `logging` 模块 |
| 7 | 禁止提交包含敏感信息的代码 | 安全风险 | 使用环境变量或配置文件管理密钥 |
| 8 | 禁止在 Notebook 中保留大量调试输出 | 文件体积膨胀 | 清理 Cell 输出后再提交 |
| 9 | 禁止使用绝对路径引用项目文件 | 换环境后路径失效 | 使用 `os.path` 动态构建相对路径 |
| 10 | 禁止忽略 PEP8 和类型注解要求 | 代码质量下降 | 使用 linter（flake8/pylint）自动检查 |
| 11 | 禁止创建未经规范的临时文件 | 临时文件堆积 | 使用 `tempfile` 模块或写入系统临时目录 |
| 12 | 禁止在 `src/` 下直接放 `.py` 文件 | 破坏目录结构规范 | 必须放在 `chXX_xxx/` 或 `utils/` 子目录内 |

---

## 六、环境配置

### 6.1 环境初始化

```bash
# 创建环境（首次）
conda create -n py310 python=3.10

# 激活环境
conda activate py310

# 安装依赖（首次）
cd gallstone_analysis
pip install -r requirements.txt
```

### 6.2 运行脚本

```bash
# 激活环境
conda activate py310

# 运行 Python 脚本
python src/chXX_xxx/analysis.py

# 运行 Notebook
jupyter notebook src/chXX_xxx/analysis.ipynb
# → 选择 Kernel: "Python 3.10 (py310)"
```

### 6.3 依赖管理

```bash
# 添加新依赖
pip install {PACKAGE_NAME}
pip freeze | grep {PACKAGE_NAME} >> requirements.txt

# 更新依赖
pip install --upgrade {PACKAGE_NAME}
pip freeze > requirements.txt

# 检查依赖冲突
pip check
```

---

## 七、派活标准话术

### 7.1 完整项目启动（从零开始）

```
【UCI 胆结石数据集分析 — 完整项目启动】

=== 第一步：了解项目 ===
阅读 docs/project_convention.md（目录结构、命名规则、禁止事项）
阅读 docs/gallstone_analysis_流程设计.md 第一章（研究概述、数据概况、整体逻辑）

=== 第二步：配置环境 ===
conda activate py310
pip install -r requirements.txt

=== 第三步：检查进度 ===
python src/utils/task_graph.py

=== 第四步：按批次执行 ===
参考 docs/task_dispatch_guide.md 的批次划分
从 Batch-0（数据预处理）开始，逐批执行
每个章节使用 §7.2 的精确派活话术

=== 第五步：产物检查 ===
每完成一个章节，运行 python src/utils/task_graph.py 确认状态更新
全部完成后，检查 outputs/ 下所有章节产物齐全
```

### 7.2 派单个章节（最常用）

```
【UCI 胆结石数据集分析 — Prompt-{NN}: {章节名称}】

你现在阅读 docs/gallstone_analysis_Execution_Prompts.md，概览任务状况，
你的任务是 Prompt-{NN}: {章节名称}；
执行标准看 docs/gallstone_analysis_流程设计.md 第{N}章；
产物要求看该文档第{N}章 {N}.5 节产物表；
项目规范（文件放哪、怎么命名、脚本结构）看 docs/project_convention.md；
执行前从 src/utils/task_graph.py 检查进度。

环境: conda activate py310
```

**变量说明**：

| 变量 | 含义 | 示例值 |
|------|------|--------|
| `{NN}` | 章节编号（两位数） | `01` / `02` / `03` |
| `{章节名称}` | 章节中文名称 | `数据预处理` / `探索性数据分析` |
| `{N}` | 流程设计文档中的章节编号 | `2` / `3` / `4`（注意：流程设计文档第一章是研究概述，Prompt-01 对应第二章） |

**首次执行 vs 重试执行**：

首次执行时，在话术末尾追加：
```
首次执行：先阅读 docs/project_convention.md 了解项目规范，再开始。
```

重试/继续执行时，在话术末尾追加：
```
继续执行：检查 outputs/ch{NN}_{章节目录}/ 已有哪些产物，从未完成的步骤继续。
```

### 7.3 检查进度

```
检查全部进度:
  python src/utils/task_graph.py

检查特定章节:
  python src/utils/task_graph.py --chapter ch{NN}

生成检查报告:
  python src/utils/task_graph.py --report outputs/quality_report.md
```

### 7.4 执行前必做清单（Pre-flight Checklist）

每次收到派活后、开始编码前，必须逐项确认：

- [ ] **1. 环境已激活**: `conda activate py310`，且 `python --version` 输出正确
- [ ] **2. 依赖已安装**: `pip list | grep pandas` 确认核心依赖可用
- [ ] **3. 前置章节产物已存在**: `python src/utils/task_graph.py --check prompt-{NN}`
- [ ] **4. 已阅读项目规范**: `docs/project_convention.md`（至少看完目录结构和命名规范）
- [ ] **5. 已阅读本 Prompt 任务概述**: `docs/gallstone_analysis_Execution_Prompts.md` 中搜索 `Prompt-{NN}`
- [ ] **6. 已阅读流程设计对应章节**: `docs/gallstone_analysis_流程设计.md` 第{N}章
- [ ] **7. 已确认产物输出目录**: `outputs/ch{NN}_{章节目录}/` 目录存在或将被自动创建

---

## 八、产物完整性检查

### 8.1 通用检查项（6 项）

每个章节完成后，必须确认以下检查项：

- [ ] `outputs/chXX_xxx/` 目录下产物齐全
- [ ] 所有数据文件以 `ch{NN}_` 开头
- [ ] 所有图片以 `ch{NN}_` 开头，DPI >= 150
- [ ] 脚本可在 `conda activate py310` 下无报错运行
- [ ] `.py` 和 `.ipynb` 逻辑一致
- [ ] 运行 `python src/utils/task_graph.py` 状态更新为完成

### 8.2 章节自定义检查项

#### ch01: 数据预处理
- [ ] 清洗后数据无 NaN 值
- [ ] 异常值已通过 IQR + Winsorize 处理
- [ ] 列名已标准化为代码友好格式
- [ ] 异常值检测报告已生成

#### ch02: 探索性数据分析
- [ ] 描述统计表覆盖所有连续变量
- [ ] 分布图覆盖所有关键特征
- [ ] 分组对比图（按 Gallstone_Status）已生成
- [ ] 相关性矩阵热力图已生成

#### ch03: 统计检验
- [ ] 连续变量组间差异检验（t-test / Mann-Whitney U）已完成
- [ ] 分类变量卡方检验已完成
- [ ] 多重比较校正（Bonferroni / FDR）已应用
- [ ] 检验结果汇总表已生成

#### ch04: 特征筛选
- [ ] 单变量筛选（统计显著性）已完成
- [ ] 多变量筛选（递归特征消除 / LASSO）已完成
- [ ] 共线性诊断（VIF）已完成
- [ ] 最终特征列表及筛选理由已记录

#### ch05: 建模预测
- [ ] 至少 2 种模型已训练（如 Logistic Regression, Random Forest）
- [ ] 交叉验证评估已完成（AUC, F1, Accuracy）
- [ ] 特征重要性分析已生成
- [ ] 最佳模型已保存（.pkl 文件）

#### ch06: 总结报告
- [ ] 全部分析结论已汇总
- [ ] 关键可视化图表已整理
- [ ] 最终报告文档已生成

### 8.3 自动化检查脚本

```bash
# 检查全部章节进度
python src/utils/task_graph.py

# 检查指定章节
python src/utils/task_graph.py --chapter ch02

# 输出检查报告
python src/utils/task_graph.py --report outputs/quality_report.md
```

---

## 九、领域背景知识

> 本节记录胆结石疾病领域的关键背景知识，供各章节分析时参考。

### 9.1 疾病概述

**胆结石（Gallstone / Cholelithiasis）** 是一种常见的消化系统疾病，指胆道系统（包括胆囊和胆管）内由于胆汁成分异常、胆汁淤滞等原因形成的固体结晶。全球成年人患病率约为 10%-15%，女性发病率约为男性的 2-3 倍。

**胆结石分类**：
- **胆固醇结石**（最常见，约 80%）：主要成分为胆固醇，与肥胖、高脂饮食、代谢综合征密切相关
- **胆色素结石**：主要成分为胆红素，与溶血性贫血、肝硬化、胆道感染相关
- **混合性结石**：同时含胆固醇和胆色素

**主要危险因素**（与数据集中特征对应）：

| 危险因素 | 对应特征 | 机制说明 |
|----------|----------|----------|
| **肥胖 / 超重** | BMI, Obesity(%), TBFR_pct, TFC, VFA | 肥胖增加肝脏胆固醇分泌，改变胆汁成分，降低胆囊排空效率 |
| **内脏脂肪堆积** | VFR, VFA, VMA_kg | 内脏脂肪与胰岛素抵抗、炎症反应相关，促进胆固醇结晶 |
| **代谢综合征** | Glucose, Triglyceride, HDL, DM, Hypertension | 胰岛素抵抗增加胆固醇饱和度，高甘油三酯降低胆汁流动性 |
| **血脂异常** | TC, LDL, HDL, Triglyceride | 高胆固醇直接增加胆汁胆固醇饱和度 |
| **肝功能异常** | AST, ALT, ALP, GFR, Creatinine | 肝脏是胆固醇代谢的核心器官，肝功能异常影响胆汁成分 |
| **炎症反应** | CRP | 全身性炎症与胆结石形成及胆囊壁炎症相关 |
| **维生素 D 缺乏** | Vitamin D | 维生素 D 缺乏与胆囊收缩功能下降、免疫调节异常相关 |
| **年龄** | Age | 胆汁中胆固醇分泌随年龄增加，胆囊排空功能逐渐下降 |
| **性别** | Gender | 女性受雌激素影响，增加胆汁胆固醇分泌、降低胆囊活动度 |

### 9.2 数据集特征与临床意义对照

| 特征分组 | 特征 | 临床意义 |
|----------|------|----------|
| **人体水分** | TBW, ECW, ICW, ECF_TBW_Ratio | 细胞外液/总水分比值反映营养状态和水肿倾向，比值偏高可能提示蛋白质营养不良或炎症 |
| **体脂指标** | TBFR_pct, LM_pct, Protein_pct, Obesity(%), TFC | 体脂率与胆结石风险正相关；瘦体重和蛋白质含量反映肌肉量和营养储备 |
| **内脏脂肪** | VFR, VFA, VMA_kg | 内脏脂肪面积（VFA）≥ 100 cm² 为内脏肥胖标准，与胆结石风险显著正相关 |
| **肝脂肪** | HFA (Hepatic Fat Accumulation) | 肝脏脂肪堆积（脂肪肝）与胆固醇结石形成密切相关 |
| **血糖代谢** | Glucose, DM | 糖尿病患者胆结石风险增加 2-3 倍，高血糖通过多元醇途径增加胆汁胆固醇 |
| **脂质代谢** | TC, LDL, HDL, Triglyceride | 高 LDL + 低 HDL + 高 TG 构成致石性血脂谱（Lithogenic profile） |
| **肝功能** | AST, ALT, ALP | ALT/AST 升高提示肝细胞损伤；ALP 升高提示胆道梗阻 |
| **肾功能** | Creatinine, GFR | 肾功能异常可能伴随代谢紊乱，间接影响胆结石风险 |
| **炎症** | CRP, HGB | CRP 升高反映急性炎症；HGB 降低可能提示慢性疾病或营养不良 |
| **骨代谢** | BM (Bone Mass), Vitamin D | 维生素 D 缺乏与胆囊动力障碍相关，影响胆囊排空 |

### 9.3 分析时的领域注意事项

1. **因果关系 vs 相关关系**：数据集为横截面数据（cross-sectional），只能建立关联，不能推断因果
2. **共线性问题**：人体成分指标间高度相关（如 TBFR_pct 与 LM_pct r=-0.994），建模时需注意多重共线性
3. **性别差异**：胆结石发病率存在显著性别差异，分析时应考虑性别分层或交互效应
4. **合并症混杂**：糖尿病、高脂血症等合并症既是胆结石的危险因素，也可能与人体成分指标高度相关，需控制混杂因素
5. **炎症指标 CRP**：初步分析显示 CRP 与胆结石状态相关性最强（r=0.52），但需注意 CRP 可能受急性感染等混杂因素影响

---

## 十、数据概况备忘

> 本节记录数据集的关键信息，供各章节快速参考。

| 项目 | 值 |
|------|-----|
| 数据集名称 | UCI Gallstone Dataset（胆结石数据集） |
| 样本量 | 319 |
| 特征数 | 39（含目标变量） |
| 目标变量 | `Gallstone_Status`（0=无胆结石, 1=有胆结石） |
| 类别分布 | 0: 161 (50.5%), 1: 158 (49.5%) — **均衡** |
| 缺失值 | 无 |
| 特征分组 | 人口统计(4) + 合并症(5) + 人体成分(14) + 血液生化(13) + 目标(1) + 其他(2) |

### 特征分组详表

| 分组 | 特征 | 类型 | 数量 |
|------|------|------|------|
| **人口统计** | Age, Gender, Height, Weight | 连续/二分类 | 4 |
| **合并症** | Comorbidity, CAD, Hypothyroidism, Hyperlipidemia, DM | 分类/二分类 | 5 |
| **人体成分** | BMI, TBW, ECW, ICW, ECF_TBW_Ratio, TBFR_pct, LM_pct, Protein_pct, VFR, BM, MM, Obesity(%), TFC, VFA, VMA_kg, HFA | 连续/有序 | 16 |
| **血液生化** | Glucose, TC, LDL, HDL, Triglyceride, AST, ALT, ALP, Creatinine, GFR, CRP, HGB, Vitamin D | 连续 | 13 |
| **目标变量** | Gallstone_Status | 二分类 | 1 |

### ch01 清洗操作记录

| 操作 | 详情 |
|------|------|
| 列名标准化 | 27 个列名简化为 snake_case 格式 |
| 异常值检测 | IQR 方法（1.5×IQR），25 列共 223 个异常值 |
| 异常值处理 | Winsorize 截断至 IQR 边界值 |
| 数据完整性 | 清洗后 319 行 × 39 列，无缺失值，无重复行 |

### 初步相关性发现（ch01）

| 排名 | 特征 | 与 Gallstone_Status 相关系数 | 解读 |
|------|------|------------------------------|------|
| 1 | CRP | 0.517 | 炎症指标与胆结石状态强正相关 |
| 2 | Vitamin D | -0.357 | 维生素 D 缺乏与胆结石正相关 |
| 3 | AST | -0.274 | 肝酶异常与胆结石状态相关 |
| 4 | LM_pct | -0.226 | 瘦体重百分比偏低与胆结石正相关 |
| 5 | TBFR_pct | 0.225 | 体脂率偏高与胆结石正相关 |
