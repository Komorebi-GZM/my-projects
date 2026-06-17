# 在线小游戏数据分析 — 项目规范 (Project Convention)

> **本文档是项目唯一规范依据。** 所有执行者（人 / AI）在动手前必须先阅读本文档。
> 派活时只需一句话：**"参考 `docs/project_convention.md`，执行 Prompt-XX。"**

---

## 一、项目结构总览

```
online_gaming_analysis/
├── data/                              # 原始数据（只读，不可修改）
│   └── online-gaming-14-04-26.csv      #    唯一数据源（TSV格式，Tab分隔）
│
├── src/                               # 源代码
│   ├── utils/                         #    通用工具模块（全章节共享）
│   │   ├── config.py                  #      全局配置：路径、参数、常量
│   │   ├── data_loader.py             #      Skill-01: 数据加载器
│   │   ├── output_manager.py          #      Skill-04: 输出产物管理器
│   │   └── task_graph.py              #      任务依赖图 + 进度检查
│   └── ch01_data_cleaning/            #    第一章：数据清洗
│       ├── clean.py                   #      可直接运行: python src/ch01_data_cleaning/clean.py
│       └── clean.ipynb                #      Jupyter 交互式
│
├── outputs/                           # 输出产物（每个章节独立子目录）
│   └── ch01_data_cleaning/            #    第一章产物
│
├── docs/                              # 项目文档
│   ├── project_convention.md          #    项目规范（本文档）
│   ├── flow_design.md                 #    流程设计文档
│   ├── task_dispatch_guide.md         #    任务分发指南（依赖图 + 派活模板）
│   └── online_gaming_analysis_Execution_Prompts.md  #    各 Prompt 执行细节
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
| **脚本代码** | `src/ch01_data_cleaning/` | 每个章节一个子目录，内含 `.py` + `.ipynb` |
| **通用工具** | `src/utils/` | 跨章节复用的模块（config、loader、manager 等） |
| **输出产物** | `outputs/ch01_data_cleaning/` | 每个章节的产物写入对应子目录，互不干扰 |
| **项目文档** | `docs/` | 规范文档、设计文档、执行 Prompt 等 |
| **依赖清单** | 项目根目录 | `requirements.txt` 唯一一份 |

### 2.2 禁止事项

- 禁止在 `data/` 中写入任何文件
- 禁止在 `outputs/` 下跨章节写入（不同章节的产物不能写到其他章节目录）
- 禁止在项目根目录散落脚本、数据、临时文件
- 禁止在 `src/` 下直接放 `.py` 文件（必须在 `ch01_data_cleaning/` 或 `utils/` 子目录内）
- 禁止创建 `venv/` 目录（使用 conda 环境 `py310`）
- 禁止在代码中硬编码项目特定参数（如文件路径、实体名称、领域常量等），所有参数必须通过 `src/utils/config.py` 统一管理

---

## 三、命名规范

### 3.1 目录命名

| 层级 | 格式 | 示例 |
|------|------|------|
| 章节脚本目录 | `src/ch{NN}_{英文简称}/` | `src/ch01_data_cleaning/` |
| 章节输出目录 | `outputs/ch{NN}_{英文全称}/` | `outputs/ch01_data_cleaning/` |

### 3.2 脚本命名

| 类型 | 格式 | 说明 |
|------|------|------|
| Python 脚本 | `{action}.py` | 如 `clean.py`, `analysis.py` |
| Jupyter Notebook | `{action}.ipynb` | 与 `.py` 同名，内容对应 |

### 3.3 产物命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch01_cleaned_data.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch01_tag_distribution.png` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch01_data_quality_report.md` |

**前缀 `ch{NN}_` 是强制的**，确保产物归属清晰。

### 3.4 变量命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 常量 | `UPPER_SNAKE_CASE` | `OUTPUT_BASE`, `MAX_ITERATIONS` |
| 函数 | `snake_case` | `load_preprocessed_data()`, `save_figure()` |
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
src/ch01_data_cleaning/
├── clean.py       # 可直接运行: python src/ch01_data_cleaning/clean.py
└── clean.ipynb    # Jupyter 交互式: jupyter notebook src/ch01_data_cleaning/clean.ipynb
```

- `.py` 和 `.ipynb` 逻辑完全一致，`.ipynb` 是 `.py` 的分步展开版
- `.py` 用于批量执行，`.ipynb` 用于逐步学习和调试

### 4.2 Python 脚本结构模板

每个 `.py` 脚本必须遵循以下结构：

```python
"""
Prompt-01: 数据清洗
在线小游戏数据清洗预处理

覆盖步骤:
  - Step 01.1: 数据读取与结构探查
  - Step 01.2: 缺失值检测与统计
  - Step 01.3: 重复行检测与处理
  - Step 01.4: description 与 tags 字段清洗
  - Step 01.5: 标签规范化
  - Step 01.6: 派生字段计算与最终验证
  - Step 01.7: 数据质量报告生成
  - Step 01.8: 数据保存与编码验证

产物输出到: outputs/ch01_data_cleaning/
"""

import sys
import os

# 路径设置（确保能导入 utils）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

# 导入项目工具
from utils.config import OUTPUT_BASE, FIGURE_DPI, ...
from utils.data_loader import load_preprocessed
from utils.output_manager import save_dataframe, save_figure, save_markdown


def main():
    """主函数：执行本章全部分析步骤。"""
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, 'ch01_data_cleaning')
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 01.1: 数据读取与结构探查
    # ...

    # Step 01.2: 缺失值检测与统计
    # ...

    print(f"章节 01 完成。产物已输出到: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
```

### 4.3 Notebook 结构模板

每个 `.ipynb` 必须遵循以下结构：

```
Cell 0 [Markdown]: 标题 + 环境说明 + 规范文档引用
Cell 1 [Code]:     导入 + 路径设置 + 配置加载
Cell 2 [Markdown]: Step 01.1 说明（目标 + 方法 + 产物）
Cell 3 [Code]:     Step 01.1 实现
Cell 4 [Markdown]: Step 01.2 说明
Cell 5 [Code]:     Step 01.2 实现
...
Cell N [Code]:     总结
```

**Cell 0 Markdown 模板**：

```markdown
# Prompt-01: 数据清洗

> **环境**: py310 (Python 3.10)
> **规范**: 参考 `docs/project_convention.md`
> **数据**: online-gaming-14-04-26.csv

## 本章目标
对 Poki + Newgrounds 双平台的在线小游戏原始数据进行清洗预处理，输出高质量标准化数据集。
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

所有 Python 代码必须遵守以下质量标准：

#### PEP8 合规

- 行长度不超过 88 字符（使用 Black 格式化器的默认值）
- 缩进使用 4 个空格
- 类和函数定义之间空两行
- 导入顺序：标准库 → 第三方库 → 项目内部模块，每组之间空一行
- 避免使用通配符导入（`from xxx import *`）

#### 类型注解

- 所有公共函数必须有参数类型注解和返回值类型注解
- 复杂数据结构使用 `typing` 模块（`List`, `Dict`, `Optional`, `Tuple` 等）
- 示例：

```python
from typing import List, Dict, Optional
import pandas as pd


def load_preprocessed(
    entity_name: str,
    data_dir: str = "data"
) -> pd.DataFrame:
    """加载预处理后的数据。

    Args:
        entity_name: 分析实体名称。
        data_dir: 数据目录路径。

    Returns:
        预处理后的 DataFrame。
    """
    ...
```

#### Docstring 规范

- 所有公共模块、类、函数必须有 docstring
- 使用 Google 风格 docstring
- docstring 必须包含：简要描述、Args（参数）、Returns（返回值）、Raises（异常，如有）
- 示例：

```python
def calculate_statistics(
    df: pd.DataFrame,
    group_col: str,
    value_col: str
) -> pd.DataFrame:
    """计算分组统计量。

    对 DataFrame 按指定列分组，计算均值、标准差、最大值、最小值等统计量。

    Args:
        df: 输入数据框。
        group_col: 分组列名。
        value_col: 数值列名。

    Returns:
        包含分组统计量的 DataFrame，列包括 mean, std, min, max, median。

    Raises:
        ValueError: 如果 group_col 或 value_col 不在 df 的列中。
    """
    ...
```

### 4.6 文档更新规则

- **修改代码后必须同步更新文档**：如果修改了脚本逻辑、产物格式、依赖关系，必须同步更新以下文档：
  - `docs/project_convention.md`：如果影响了项目结构、命名规范、脚本规范
  - `docs/task_dispatch_guide.md`：如果影响了依赖关系、批次划分、产物清单
  - 脚本内的 docstring：如果修改了函数签名、行为、产物
- **文档更新检查**：每次提交代码时，检查是否有对应的文档更新。如果没有，需要在提交信息中说明原因

---

## 五、禁止事项清单

### 5.1 核心禁止事项（6 条）

| # | 禁止事项 | 原因 | 正确做法 |
|---|----------|------|----------|
| 1 | 禁止修改 `data/` 目录 | 原始数据是唯一数据源，修改后无法恢复 | 所有数据处理结果写入 `outputs/` |
| 2 | 禁止跨章节写入产物 | 产物归属混乱，后续引用困难 | 每个章节只写入自己的 `outputs/ch01_data_cleaning/` |
| 3 | 禁止在根目录散落文件 | 项目结构混乱，难以维护 | 文件必须归入对应目录（data/src/outputs/docs） |
| 4 | 禁止跳过依赖直接执行 | 数据不一致，产物不可靠 | 严格按批次顺序执行 |
| 5 | 禁止在代码中硬编码参数 | 参数分散难以维护，换项目需大量修改 | 所有参数通过 `src/utils/config.py` 管理 |
| 6 | 禁止在业务逻辑脚本中使用 `print()` 输出中间调试信息 | 污染标准输出，不利于日志管理 | 使用 `logging` 模块。工具模块（utils/）中的 `print()` 用于用户反馈是允许的。 |

### 5.2 扩展禁止事项

| # | 禁止事项 | 原因 | 正确做法 |
|---|----------|------|----------|
| 7 | 禁止提交包含敏感信息的代码 | 安全风险 | 使用环境变量或配置文件管理密钥 |
| 8 | 禁止在 Notebook 中保留大量调试输出 | 文件体积膨胀，影响版本控制 | 清理 Cell 输出后再提交 |
| 9 | 禁止使用绝对路径引用项目文件 | 换环境后路径失效 | 使用 `os.path` 动态构建相对路径 |
| 10 | 禁止忽略 PEP8 和类型注解要求 | 代码质量下降，维护困难 | 使用 linter（flake8/pylint）自动检查 |
| 11 | 禁止创建未经规范的临时文件 | 临时文件堆积，项目混乱 | 临时文件使用 `tempfile` 模块或写入系统临时目录 |
| 12 | 禁止在 `src/` 下直接放 `.py` 文件 | 破坏目录结构规范 | 必须放在 `ch01_data_cleaning/` 或 `utils/` 子目录内 |

---

## 六、环境配置

### 6.1 环境初始化

```bash
# 创建环境（首次）
conda create -n py310 python=3.10

# 激活环境
conda activate py310

# 安装依赖（首次）
cd online_gaming_analysis
pip install -r requirements.txt
```

### 6.2 运行脚本

```bash
# 激活环境
conda activate py310

# 运行 Python 脚本
python src/ch01_data_cleaning/clean.py

# 运行 Notebook
jupyter notebook src/ch01_data_cleaning/clean.ipynb
# → 选择 Kernel: "Python 3.10 (py310)"
```

### 6.3 依赖管理

```bash
# 添加新依赖
pip install {package_name}
pip freeze | grep {package_name} >> requirements.txt

# 更新依赖
pip install --upgrade {package_name}
pip freeze > requirements.txt

# 检查依赖冲突
pip check
```

---

## 七、派活标准话术

### 7.1 完整项目启动（从零开始）

```
【在线小游戏数据分析 — 完整项目启动】

=== 第一步：了解项目 ===
阅读 docs/project_convention.md（目录结构、命名规则、禁止事项）
阅读 docs/flow_design.md 第一章（研究概述、数据概况、整体逻辑）

=== 第二步：配置环境 ===
conda activate py310
pip install -r requirements.txt

=== 第三步：检查进度 ===
python src/utils/task_graph.py

=== 第四步：按批次执行 ===
参考 docs/task_dispatch_guide.md 的批次划分
从 Batch-0（数据清洗）开始，逐批执行
每个章节使用 §7.2 的精确派活话术

=== 第五步：产物检查 ===
每完成一个章节，运行 python src/utils/task_graph.py 确认状态更新
全部完成后，检查 outputs/ 下所有章节产物齐全
```

### 7.2 派单个章节（最常用）

```
【在线小游戏数据分析 — Prompt-01: 数据清洗】

你现在阅读 docs/online_gaming_analysis_Execution_Prompts.md，概览任务状况，
你的任务是 Prompt-01: 数据清洗；
执行标准看 docs/flow_design.md 第2章；
产物要求看该文档第2章 2.5 节产物表；
项目规范（文件放哪、怎么命名、脚本结构）看 docs/project_convention.md；
执行前从 src/utils/task_graph.py 检查进度。

环境: conda activate py310
```

**变量说明**：

| 变量 | 含义 | 本项目值 |
|------|------|----------|
| `PROJECT_DESCRIPTION` | 项目中文描述 | 在线小游戏数据分析 |
| `NN` | 章节编号（两位数） | `01` |
| `CHAPTER_NAME` | 章节中文名称 | 数据清洗 |
| `PROJECT_NAME`_Execution_Prompts.md | 执行Prompt文档文件名 | `online_gaming_analysis_Execution_Prompts.md` |
| `FLOW_DESIGN_FILENAME` | 流程设计文档文件名 | `flow_design.md` |
| `N` | 流程设计文档中的章节编号 | `2`（注意：流程设计文档第一章是研究概述，Prompt-01 对应第二章） |
| `ENV_TYPE` | 环境类型 | `conda` |
| `ENV_NAME` | 环境名称 | `py310` |

**首次执行 vs 重试执行**：

首次执行时，在话术末尾追加：
```
首次执行：先阅读 docs/project_convention.md 了解项目规范，再开始。
```

重试/继续执行时，在话术末尾追加：
```
继续执行：检查 outputs/ch01_data_cleaning/ 已有哪些产物，从未完成的步骤继续。
```

### 7.3 检查进度

```
检查在线小游戏数据分析全部进度:
  python src/utils/task_graph.py

检查特定章节:
  python src/utils/task_graph.py --chapter ch01

生成检查报告:
  python src/utils/task_graph.py --report outputs/quality_report.md
```

### 7.4 执行前必做清单（Pre-flight Checklist）

每次收到派活后、开始编码前，必须逐项确认：

- [ ] **1. 环境已激活**: `conda activate py310`，且 `python --version` 输出正确
- [ ] **2. 依赖已安装**: `pip list | grep pandas` 确认核心依赖可用
- [ ] **3. 前置章节产物已存在**: `python src/utils/task_graph.py --check prompt-01`
- [ ] **4. 已阅读项目规范**: `docs/project_convention.md`（至少看完目录结构和命名规范）
- [ ] **5. 已阅读本 Prompt 任务概述**: `docs/online_gaming_analysis_Execution_Prompts.md` 中搜索 `Prompt-01`
- [ ] **6. 已阅读流程设计对应章节**: `docs/flow_design.md` 第2章（了解研究目标和方法选择依据）
- [ ] **7. 已确认产物输出目录**: `outputs/ch01_data_cleaning/` 目录存在或将被自动创建

**如果第3项不通过**：说明前置章节未完成，需要先完成前置章节或与项目负责人确认。
**如果第5项或第6项不通过**：说明对任务理解不充分，可能导致返工，强烈建议先读完再动手。

---

## 八、产物完整性检查

### 8.1 通用检查项（6 项）

每个章节完成后，必须确认以下检查项：

- [ ] `outputs/ch01_data_cleaning/` 目录下产物齐全
- [ ] 所有数据文件以 `ch01_` 开头
- [ ] 所有图片以 `ch01_` 开头，DPI >= 150
- [ ] 脚本可在 `conda activate py310` 下无报错运行
- [ ] `.py` 和 `.ipynb` 逻辑一致
- [ ] 运行 `python src/utils/task_graph.py` 状态更新为完成

### 8.2 章节自定义检查项

#### ch01: 数据清洗
- [ ] 清洗后数据无重复行
- [ ] description 和 tags 列无 NaN
- [ ] 标签已规范化（特殊字符替换、同义词合并、统一小写）
- [ ] game_id 唯一且连续（从 0 或 1 开始递增）
- [ ] source 列仅包含 poki 和 newgrounds 两个值
- [ ] like_ratio 在 [0, 1] 范围内
- [ ] 清洗后数据文件为 UTF-8 BOM 编码

### 8.3 自动化检查脚本

项目提供 `src/utils/task_graph.py` 用于自动化检查：

```bash
# 检查全部章节进度
python src/utils/task_graph.py

# 检查指定章节
python src/utils/task_graph.py --chapter ch01

# 输出检查报告
python src/utils/task_graph.py --report outputs/quality_report.md
```

检查脚本会自动验证：
1. 各章节产物目录是否存在
2. 必需的产物文件是否齐全
3. 产物文件命名是否符合规范（`ch{NN}_` 前缀）
4. 图片文件 DPI 是否达标
5. 依赖关系是否满足（前置章节产物是否存在）
