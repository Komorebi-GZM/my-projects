# AB_Test_Analysis

A/B测试点击率数据分析项目

## 项目概述

本项目通过规范的统计分析流程，评估互联网产品A/B测试中新版本页面（实验组）相比旧版本页面（对照组）是否显著提升了用户点击率，并依据结论给出明确的业务建议。

- **数据规模**：20,000 名用户
- **实验周期**：2024-01-01 ~ 2024-01-07（7天）
- **核心指标**：点击率（CTR）

## 项目结构

```
AB_Test_Analysis/
├── data/                          # 数据目录
│   ├── raw/                       # 原始数据（只读）
│   └── processed/                 # 清洗后数据
├── src/                           # 源代码
│   ├── utils/                     # 公共工具模块
│   ├── ch01_data_cleaning/        # 数据清洗
│   ├── ch02_metrics_visualization/  # 核心指标与可视化
│   ├── ch03_hypothesis_testing/     # 假设检验与效应量
│   ├── ch04_time_trend_analysis/    # 时间趋势分析
│   └── ch05_conclusion_recommendation/  # 结论与决策建议
├── outputs/                       # 产物输出
│   ├── figures/                   # 图表
│   └── tables/                    # 表格
├── docs/                          # 文档
├── tests/                         # 测试
└── project_params.json            # 项目参数
```

## 快速开始

```bash
# 按批次执行
python src/ch01_data_cleaning/run.py
python src/ch02_metrics_visualization/run.py
python src/ch03_hypothesis_testing/run.py
python src/ch04_time_trend_analysis/run.py
python src/ch05_conclusion_recommendation/run.py
```

## 文档

| 文档 | 说明 |
|------|------|
| [project_convention.md](docs/project_convention.md) | 项目规范文档 |
| [analysis_goals.md](docs/analysis_goals.md) | 分析目标与研究问题 |
| [flow_design.md](docs/flow_design.md) | 研究设计文档 |
| [execution_prompts.md](docs/execution_prompts.md) | 执行指令文档 |
| [task_dispatch_guide.md](docs/task_dispatch_guide.md) | 任务分发指南 |

## 技术栈

- Python 3.10
- pandas, numpy
- matplotlib
- scipy, statsmodels
