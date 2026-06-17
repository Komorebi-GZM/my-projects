# 基于51job招聘数据的人才市场全维度分析 — 项目规范 (Project Convention)

> **本文档是项目唯一规范依据。** 所有执行者（人 / AI）在动手前必须先阅读本文档。
> 派活时只需一句话：**"参考 `docs/project_convention.md`，执行 Prompt-XX。"**

---

## 一、项目结构总览

```
51job_recruitment_analysis/
├── AGENTS.md                          # AI Agent 协作规范
├── CLAUDE.md                          # Claude AI 项目上下文
├── .learnings/                        # 经验教训记录
│   └── LEARNINGS.md                   #    学习总结
│
├── data/                              # 原始数据（只读，不可修改）
│   └── 前程无忧数据集.csv              #    唯一数据源（295条有效记录，10列）
│
├── src/                               # 源代码
│   ├── utils/                         #    通用工具模块（全章节共享）
│   │   ├── __init__.py
│   │   ├── config.py                  #      全局配置：路径、参数、常量
│   │   ├── data_loader.py             #      Skill-01: 数据加载器
│   │   ├── output_manager.py          #      Skill-04: 输出产物管理器
│   │   ├── visualizer.py              #      Skill-02: 可视化工具
│   │   └── task_graph.py              #      任务依赖图 + 进度检查
│   ├── ch01_data_overview/            #    ch01: 基础数据概览
│   │   ├── __init__.py
│   │   ├── overview.py                #      .py 脚本
│   │   └── overview.ipynb             #      .ipynb 笔记本
│   ├── ch02_salary_analysis/          #    ch02: 薪资维度分析
│   │   ├── __init__.py
│   │   ├── salary.py
│   │   └── salary.ipynb
│   ├── ch03_supply_demand/            #    ch03: 供需维度分析
│   │   ├── __init__.py
│   │   ├── supply_demand.py
│   │   └── supply_demand.ipynb
│   ├── ch04_enterprise_features/      #    ch04: 企业特征分析
│   │   ├── __init__.py
│   │   ├── enterprise.py
│   │   └── enterprise.ipynb
│   └── ch05_summary_report/           #    ch05: 总结报告
│       ├── __init__.py
│       ├── summary.py
│       └── summary.ipynb
│
├── outputs/                           # 输出产物（每个章节独立子目录）
│   ├── ch01_data_overview/            #    ch01 产物
│   ├── ch02_salary_analysis/          #    ch02 产物
│   ├── ch03_supply_demand/            #    ch03 产物
│   ├── ch04_enterprise_features/      #    ch04 产物
│   └── ch05_summary_report/           #    ch05 产物
│
├── docs/                              # 项目文档
│   ├── project_convention.md          #    项目规范（本文档）
│   ├── analysis_goals.md              #    分析目标文档
│   ├── flow_design.md                 #    研究设计文档
│   ├── task_dispatch_guide.md         #    任务分发指南（依赖图 + 派活模板）
│   └── 51job_recruitment_analysis_Execution_Prompts.md  #    各 Prompt 执行细节
│
├── requirements.txt                   # Python 依赖清单
└── README.md                          # 项目说明（待创建）
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
| 章节脚本目录 | `src/ch{NN}_{英文简称}/` | `src/ch02_salary_analysis/` |
| 章节输出目录 | `outputs/ch{NN}_{英文简称}/` | `outputs/ch02_salary_analysis/` |

### 3.2 脚本命名

| 类型 | 格式 | 说明 |
|------|------|------|
| Python 脚本 | `{动作}.py` | 如 `overview.py`, `salary.py`, `supply_demand.py` |
| Jupyter Notebook | `{动作}.ipynb` | 与 `.py` 同名，内容对应 |

### 3.3 产物命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 数据文件 | `ch{NN}_{描述}.csv` | `ch01_cleaned_data.csv` |
| 图片文件 | `ch{NN}_{描述}.png` | `ch02_salary_boxplot.png` |
| 报告文件 | `ch{NN}_{描述}.md` | `ch05_final_report.md` |

**前缀 `ch{NN}_` 是强制的**，确保产物归属清晰。

### 3.4 变量命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 常量 | `UPPER_SNAKE_CASE` | `OUTPUT_BASE`, `RAW_DATA_FILE` |
| 函数 | `snake_case` | `load_raw_data()`, `save_figure()` |
| 类 | `PascalCase` | `DataLoader`, `OutputManager` |
| 私有方法 | `_leading_underscore` | `_parse_salary()`, `_extract_city()` |

---

## 四、脚本编写规范

### 4.1 每个章节必须提供两种格式

```
src/chXX_xxx/
├── {action}.py       # 可直接运行: python src/chXX_xxx/{action}.py
└── {action}.ipynb    # Jupyter 交互式: jupyter notebook src/chXX_xxx/{action}.ipynb
```

- `.py` 和 `.ipynb` 逻辑完全一致，`.ipynb` 是 `.py` 的分步展开版
- `.py` 用于批量执行，`.ipynb` 用于逐步学习和调试

### 4.2 Python 脚本结构模板

```python
"""
Prompt-{NN}: {章节名称}
基于51job招聘数据的人才市场全维度分析

覆盖步骤:
  - Step {N}.1: ...
  - Step {N}.2: ...

产物输出到: outputs/ch{NN}_xxx/
"""

import sys
import os

# 路径设置（确保能导入 utils）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SRC_DIR)

# 导入项目工具
from utils.config import OUTPUT_BASE, PLT_STYLE
from utils.data_loader import load_raw_data, load_preprocessed
from utils.output_manager import get_chapter_dir, save_dataframe, save_figure, save_markdown
from utils.visualizer import plot_time_series, plot_multi_comparison, plot_heatmap


def main():
    """主函数：执行本章全部分析步骤。"""
    OUTPUT_DIR = get_chapter_dir('ch{NN}')
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step {N}.1: ...
    # Step {N}.2: ...

    print(f"章节 {NN} 完成。产物已输出到: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
```

### 4.3 代码质量规则

- 行长度不超过 88 字符
- 缩进使用 4 个空格
- 导入顺序：标准库 → 第三方库 → 项目内部模块
- 所有公共函数必须有 docstring（Google 风格）
- 所有公共函数必须有参数类型注解和返回值类型注解

---

## 五、禁止事项清单

| # | 禁止事项 | 原因 | 正确做法 |
|---|----------|------|----------|
| 1 | 禁止修改 `data/` 目录 | 原始数据是唯一数据源 | 所有数据处理结果写入 `outputs/` |
| 2 | 禁止跨章节写入产物 | 产物归属混乱 | 每个章节只写入自己的 `outputs/chXX_xxx/` |
| 3 | 禁止在根目录散落文件 | 项目结构混乱 | 文件必须归入对应目录 |
| 4 | 禁止跳过依赖直接执行 | 数据不一致 | 严格按批次顺序执行 |
| 5 | 禁止在代码中硬编码参数 | 参数分散难以维护 | 所有参数通过 `src/utils/config.py` 管理 |
| 6 | 禁止使用绝对路径引用项目文件 | 换环境后路径失效 | 使用 `os.path` 动态构建相对路径 |

---

## 六、环境配置

### 6.1 环境初始化

```bash
# 创建环境（首次）
conda create -n py310 python=3.10 -y

# 激活环境
conda activate py310

# 安装依赖（首次）
cd 51job_recruitment_analysis
pip install -r requirements.txt
```

### 6.2 运行脚本

```bash
# 激活环境
conda activate py310

# 运行 Python 脚本
python src/ch01_data_overview/overview.py

# 运行 Notebook
jupyter notebook src/ch01_data_overview/overview.ipynb
```

---

## 七、派活标准话术

### 7.1 完整项目启动（从零开始）

```
【基于51job招聘数据的人才市场全维度分析 — 完整项目启动】

=== 第一步：了解项目 ===
阅读 docs/project_convention.md（目录结构、命名规则、禁止事项）
阅读 docs/analysis_goals.md（分析目标与研究问题）

=== 第二步：配置环境 ===
conda activate py310
pip install -r requirements.txt

=== 第三步：检查进度 ===
python src/utils/task_graph.py

=== 第四步：按批次执行 ===
参考 docs/task_dispatch_guide.md 的批次划分
从 Batch-1（数据概览）开始，逐批执行
```

### 7.2 派单个章节（最常用）

```
【基于51job招聘数据的人才市场全维度分析 — Prompt-{NN}: {章节名称}】

你现在阅读 docs/51job_recruitment_analysis_Execution_Prompts.md，概览任务状况，
你的任务是 Prompt-{NN}: {章节名称}；
执行标准看 docs/flow_design.md 第{N}章；
产物要求看该文档第{N}章 {N}.5 节产物表；
项目规范（文件放哪、怎么命名、脚本结构）看 docs/project_convention.md；
执行前从 src/utils/task_graph.py 检查进度。

环境: conda activate py310
```

### 7.3 检查进度

```
检查全部进度: python src/utils/task_graph.py
```

---

## 八、产物完整性检查

### 8.1 通用检查项（6 项）

- [ ] `outputs/chXX_xxx/` 目录下产物齐全
- [ ] 所有数据文件以 `ch{NN}_` 开头
- [ ] 所有图片以 `ch{NN}_` 开头，DPI >= 150
- [ ] 脚本可在 `conda activate py310` 下无报错运行
- [ ] `.py` 和 `.ipynb` 逻辑一致
- [ ] 运行 `python src/utils/task_graph.py` 状态更新为完成

### 8.2 章节自定义检查项

#### ch01: 基础数据概览
- [ ] 清洗后数据无重复表头行
- [ ] 字段已正确重命名（学历要求→工作经验要求，工作经验→附加要求）
- [ ] 薪资已解析为 salary_min / salary_max / salary_avg 三列
- [ ] 城市信息已从公司名提取
- [ ] 缺失值已标记（非删除）

#### ch02: 薪资维度分析
- [ ] 薪资分布图覆盖整体分布和分位数
- [ ] 学历-薪资、经验-薪资、行业-薪资对比图齐全
- [ ] 箱线图和热力图正确展示分组差异

#### ch03: 供需维度分析
- [ ] 热门岗位 TOP20 图表已生成
- [ ] 城市/行业招聘热度排名图已生成
- [ ] 学历+经验供需交叉分析表已生成

#### ch04: 企业特征分析
- [ ] 企业性质/规模分布图已生成
- [ ] 福利标签频次统计图已生成
- [ ] 福利-薪资关联分析已生成

#### ch05: 总结报告
- [ ] 核心结论有数据支撑
- [ ] 洞察建议面向三类受众（求职者、企业、研究机构）
- [ ] 局限性已明确标注（样本量、时效性等）
