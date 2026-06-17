# AB_Test_Analysis 项目规范文档

> 项目描述：A/B测试点击率数据分析
> 生成时间：2026-05-08
> 数据格式：csv | Python版本：3.10 | 环境：system

---

## 1. 项目结构总览

```
AB_Test_Analysis/
├── data/                          # 数据目录（只读）
│   ├── raw/                       # 原始数据
│   │   └── ab_test_click_data.csv
│   └── processed/                 # 清洗后数据
│       └── cleaned_data.csv
├── src/                           # 源代码
│   ├── utils/                     # 公共工具模块（4个Skill模块）
│   │   ├── __init__.py
│   │   ├── config.py              # Skill-00: 全局配置
│   │   ├── data_loader.py         # Skill-01: 数据加载工具
│   │   ├── visualizer.py          # Skill-02: 可视化工具
│   │   ├── metrics.py             # Skill-03: 指标计算工具
│   │   ├── output_manager.py      # Skill-04: 产物输出管理
│   │   └── task_graph.py          # Skill-05: 任务依赖管理
│   ├── ch01_data_cleaning/        # 数据清洗
│   │   ├── run.py
│   │   └── notebook.ipynb
│   ├── ch02_metrics_visualization/  # 核心指标与可视化
│   │   ├── run.py
│   │   └── notebook.ipynb
│   ├── ch03_hypothesis_testing/     # 假设检验与效应量
│   │   ├── run.py
│   │   └── notebook.ipynb
│   ├── ch04_time_trend_analysis/    # 时间趋势分析
│   │   ├── run.py
│   │   └── notebook.ipynb
│   └── ch05_conclusion_recommendation/  # 结论与决策建议
│       ├── run.py
│       └── notebook.ipynb
├── outputs/                       # 产物输出（按章节归档）
│   ├── ch01_data_cleaning/
│   │   ├── report.md              # 章节执行报告（四段框架）
│   │   └── *.csv/*.json           # 章节产物
│   ├── ch02_metrics_visualization/
│   │   ├── report.md
│   │   └── *.csv/*.png
│   ├── ch03_hypothesis_testing/
│   │   ├── report.md
│   │   └── *.csv
│   ├── ch04_time_trend_analysis/
│   │   ├── report.md
│   │   └── *.csv/*.png
│   └── ch05_conclusion_recommendation/
│       ├── report.md
│       └── *.md
├── docs/                          # 文档
│   ├── project_convention.md      # 本文档
│   ├── analysis_goals.md          # 分析目标
│   ├── flow_design.md             # 研究设计
│   ├── execution_prompts.md       # 执行指令
│   └── task_dispatch_guide.md     # 任务分发指南
├── tests/                         # 测试
│   └── test_project_health.py
├── project_params.json            # 项目参数
├── requirements.txt               # 依赖清单
└── README.md
```

### 文件分类规则

| 类别 | 目录 | 说明 |
|------|------|------|
| 原始数据 | `data/raw/` | 只读，禁止修改 |
| 处理后数据 | `data/processed/` | 清洗/转换后的数据 |
| 工具代码 | `src/utils/` | 跨章节复用的公共模块（4个Skill） |
| 章节代码 | `src/chXX_*/` | 各章节专属脚本（.py + .ipynb） |
| 章节产物 | `outputs/chXX_*/` | 各章节输出文件（含report.md） |
| 文档 | `docs/` | 项目文档 |

---

## 2. 命名规范

### 目录命名
- 项目根目录：`snake_case`（如 `AB_Test_Analysis`）
- 章节目录：`chXX_<name_en>`（如 `ch01_data_cleaning`）
- 输出目录：`chXX_<dir_suffix>`（与章节目录一致）

### 脚本命名
- Python脚本：`run.py`（章节主脚本）
- Notebook：`notebook.ipynb`（交互版本）

### 产物命名
- 报告：`report.md`（章节执行报告，四段框架）
- 图表：`chXX_<描述>.png/pdf`
- 表格：`chXX_<描述>.csv/xlsx`
- 数据文件：`snake_case.csv`

### 变量命名
- 变量/函数：`snake_case`
- 常量：`UPPER_SNAKE_CASE`
- 类名：`PascalCase`

---

## 3. 脚本编写规范

### Python 脚本结构模板

```python
"""
章节：<章节名称>
描述：<章节描述>
"""

import pandas as pd
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import Config
from src.utils.data_loader import DataLoader
from src.utils.visualizer import Visualizer
from src.utils.metrics import Metrics
from src.utils.output_manager import OutputManager


def main():
    """主函数"""
    config = Config()
    loader = DataLoader(config)
    visualizer = Visualizer(config)
    metrics = Metrics()
    output = OutputManager(config)

    # 执行步骤
    df = loader.load_processed("cleaned_data.csv")
    # ...

    print("章节完成")


if __name__ == "__main__":
    main()
```

### 代码质量要求
- 遵循 PEP 8 规范
- 函数必须有 docstring
- 关键步骤添加中文注释
- 使用类型注解（Python 3.10+）

---

## 4. 禁止事项清单

### 核心禁止（5条）
1. **禁止修改 `data/raw/` 目录** — 原始数据只读，所有变更写入 `data/processed/`
2. **禁止跨章节写入产物** — 每个章节只写入自己的 `outputs/chXX/` 目录
3. **禁止在项目根目录散落文件** — 所有文件归入对应目录
4. **禁止跳过依赖直接执行** — 按批次顺序执行
5. **禁止在代码中硬编码参数** — 使用 `src/utils/config.py` 统一管理

### 扩展禁止
- 禁止使用 `import *`（显式导入）
- 禁止提交含敏感信息的数据文件
- 禁止在 Notebook 中存放大量原始数据输出

---

## 5. 环境配置

### 环境信息
- Python：3.10
- 环境：system（系统默认）

### 运行脚本
```bash
# 运行章节脚本
python src/ch01_data_cleaning/run.py
python src/ch02_metrics_visualization/run.py
python src/ch03_hypothesis_testing/run.py
python src/ch04_time_trend_analysis/run.py
python src/ch05_conclusion_recommendation/run.py
```

### 核心依赖
- pandas >= 2.0.3
- numpy >= 1.24.3
- matplotlib >= 3.8.0
- scipy >= 1.11.4
- statsmodels >= 0.14.0

---

## 6. 章节输出三项规范

每个章节必须遵守以下输出规范：

| 规范 | 说明 |
|------|------|
| **report.md 必需** | 每个章节输出 `outputs/chXXX/report.md`（四段框架：背景、分析方法、分析发现、小结） |
| **notebook.ipynb 必需** | 每个章节提供 `.ipynb`（与 `.py` 执行逻辑一致） |
| **outputs/chXXX/** | 所有输出文件统一归档到此目录 |

### report.md 四段框架

1. **背景**：本章要解决什么问题，为什么重要
2. **分析方法**：采用了什么方法、工具、参数
3. **分析发现**：具体的数据结果、图表、统计量
4. **小结**：结论、产物清单、后续建议

---

## 7. 全局 Skill 模块引用

| Skill ID | 模块名 | 路径 | 核心函数 | 调用时机 |
|----------|--------|------|----------|----------|
| Skill-01 | 标准数据加载器 | `src/utils/data_loader.py` | `load_raw()`, `load_processed()` | 读取输入数据时 |
| Skill-02 | 标准可视化出图器 | `src/utils/visualizer.py` | `save_figure()`, `create_bar_plot()` | 生成图表时 |
| Skill-03 | 标准评估指标计算器 | `src/utils/metrics.py` | `null_summary()`, `duplicate_summary()` | 数据质量检查时 |
| Skill-04 | 标准输出产物管理器 | `src/utils/output_manager.py` | `save_table()`, `save_data()`, `save_json()` | 保存产物时 |
| Skill-05 | 任务依赖图管理 | `src/utils/task_graph.py` | `get_status()`, `run_parallel()` | 任务调度时 |

---

## 8. 章节依赖关系

```
ch01 数据清洗 ──┬──▶ ch02 核心指标与可视化 ──┐
                ├──▶ ch03 假设检验与效应量 ──┼──▶ ch05 结论与决策建议
                └──▶ ch04 时间趋势分析   ──┘
```

### 批次划分

| 批次 | 章节 | 依赖 | 并行性 |
|------|------|------|--------|
| Batch-0 | ch01 | 无 | 串行前置 |
| Batch-1 | ch02, ch03, ch04 | ch01 | 可并行 |
| Batch-2 | ch05 | ch02, ch03, ch04 | 串行收束 |

---

## 9. 产物完整性检查

### 通用检查项
- [ ] 每个章节的 `outputs/chXXX/report.md` 已生成
- [ ] 每个章节的 `src/chXXX/notebook.ipynb` 已存在
- [ ] 所有产物文件已归档到 `outputs/chXXX/` 目录
- [ ] 脚本可独立运行，无报错

### ch01 数据清洗检查项
- [ ] 缺失值检查报告
- [ ] 重复值检查报告
- [ ] 清洗后数据已保存至 `data/processed/`

### ch02 核心指标与可视化检查项
- [ ] 分组 CTR 计算结果表
- [ ] 95% CI 计算正确
- [ ] 可视化图表已保存

### ch03 假设检验与效应量检查项
- [ ] Z 统计量、p 值计算正确
- [ ] Cohen's h 效应量计算正确
- [ ] 统计功效分析完成

### ch04 时间趋势分析检查项
- [ ] 按天/按小时趋势表已生成
- [ ] 时间趋势图已保存
- [ ] 新奇效应检测已完成

### ch05 结论与决策建议检查项
- [ ] 决策框架应用正确
- [ ] 决策报告已生成

---

## 10. 版本历史

- v2.0 (2026-05-08): 符合最新技能规范，增加三项输出规范、Skill模块引用
- v1.0 (2026-05-07): 初始版本
